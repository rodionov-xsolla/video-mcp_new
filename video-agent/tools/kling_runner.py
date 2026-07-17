#!/usr/bin/env python3
"""Durable executor for orchestrator-authored fal.ai video jobs."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import fal_runner as fr


SCHEMA_VERSION = 3
ROUTES_PATH = Path(__file__).resolve().with_name("video_routes.json")
ARTIFACT_KIND = "scene_video"
MAX_GENERATION_ATTEMPTS = 2
MAX_DOWNLOAD_ATTEMPTS = 2
PENDING = {"IN_QUEUE", "IN_PROGRESS"}
REMOTE_FAILURE = {"FAILED", "ERROR"}
RETRYABLE_HTTP = {429}
AMBIGUOUS_SUBMIT_HTTP = {500, 502, 503, 504}
EXPIRED_LINK_HTTP = {403, 404, 410}
JOB_FIELDS = {
    "schema_version",
    "job_id",
    "route",
    "artifact_kind",
    "output_dir",
    "output_path",
    "payload",
    "expect",
    "supabase",
}
EXPECT_FIELDS = {
    "kind",
    "duration_seconds",
    "duration_tolerance_seconds",
    "audio",
    "min_bytes",
    "min_width",
    "min_height",
    "orientation",
}
ROUTE_FIELDS = {
    "protocol",
    "submit_url",
    "poll_base",
    "result_url_path",
}
SUPABASE_FIELDS = {"game", "episode", "name"}


def permanent_https_url(value, field):
    if not fr.https_url(value):
        raise fr.JobValidationError(f"{field} must be an HTTPS URL")
    host = urlparse(value).netloc.lower()
    if "fal.media" in host or host == "queue.fal.run":
        raise fr.JobValidationError(f"temporary fal URLs are forbidden for {field}")
    return value


def load_route(route_id, path=ROUTES_PATH):
    if not isinstance(route_id, str) or not re.fullmatch(
        r"[a-z0-9][a-z0-9._-]{1,127}", route_id
    ):
        raise fr.JobValidationError("route must be a stable lowercase route id")
    document = fr.read_object(path, fr.JobValidationError)
    if set(document) != {"schema_version", "routes"} or document.get("schema_version") != 1:
        raise fr.JobValidationError("invalid video route registry header")
    routes = document.get("routes")
    if not isinstance(routes, dict) or not isinstance(routes.get(route_id), dict):
        raise fr.JobValidationError(
            f"unknown route {route_id!r}; add a fal_queue descriptor to {path}, not to runner Python"
        )
    route = routes[route_id]
    if set(route) != ROUTE_FIELDS or route.get("protocol") != "fal_queue":
        raise fr.JobValidationError(f"invalid fal_queue descriptor for route {route_id!r}")
    submit_url = route.get("submit_url")
    poll_base = route.get("poll_base")
    result_url_path = route.get("result_url_path")
    if not fr.https_url(submit_url) or not fr.https_url(poll_base):
        raise fr.JobValidationError(f"route {route_id!r} has invalid HTTPS endpoints")
    if (
        not isinstance(result_url_path, list)
        or not result_url_path
        or any(not isinstance(item, str) or not item for item in result_url_path)
    ):
        raise fr.JobValidationError(f"route {route_id!r} has invalid result_url_path")
    return route, hashlib.sha256(fr.canonical_bytes(route)).hexdigest()


def validate_mp4(path, expect):
    path = Path(path)
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise fr.DownloadError(f"cannot read MP4: {exc}") from exc
    if size < expect["min_bytes"]:
        raise fr.DownloadError(
            f"MP4 is missing or undersized: {size} < {expect['min_bytes']} bytes"
        )
    ffprobe = shutil.which("ffprobe")
    ffmpeg = shutil.which("ffmpeg")
    if not ffprobe or not ffmpeg:
        raise fr.DownloadError("ffprobe and ffmpeg are required for MP4 validation")
    probe = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    if probe.returncode:
        raise fr.DownloadError(probe.stderr.strip() or "ffprobe could not read MP4")
    try:
        metadata = json.loads(probe.stdout)
        duration = float(metadata["format"]["duration"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise fr.DownloadError("MP4 has invalid ffprobe metadata") from exc
    streams = metadata.get("streams") or []
    video = next((item for item in streams if item.get("codec_type") == "video"), None)
    audio = next((item for item in streams if item.get("codec_type") == "audio"), None)
    if not video or not video.get("codec_name"):
        raise fr.DownloadError("MP4 has no video stream")
    width, height = video.get("width"), video.get("height")
    if (
        not isinstance(width, int)
        or not isinstance(height, int)
        or width < expect["min_width"]
        or height < expect["min_height"]
    ):
        raise fr.DownloadError(f"MP4 dimensions do not meet expectation: {width}x{height}")
    orientation = expect["orientation"]
    if orientation == "portrait" and height <= width:
        raise fr.DownloadError(f"MP4 is not portrait: {width}x{height}")
    if orientation == "landscape" and width <= height:
        raise fr.DownloadError(f"MP4 is not landscape: {width}x{height}")
    if abs(duration - expect["duration_seconds"]) > expect["duration_tolerance_seconds"]:
        raise fr.DownloadError(
            f"MP4 duration {duration:.6f}s differs from expected {expect['duration_seconds']}s"
        )
    has_audio = bool(audio and audio.get("codec_name"))
    if expect["audio"] == "required" and not has_audio:
        raise fr.DownloadError("MP4 is missing the required native audio stream")
    if expect["audio"] == "forbidden" and has_audio:
        raise fr.DownloadError("MP4 contains an audio stream but expect.audio is forbidden")
    decode_command = [
            ffmpeg,
            "-v",
            "error",
            "-xerror",
            "-i",
            str(path),
            "-map",
            "0:v:0",
    ]
    if has_audio:
        decode_command.extend(["-map", "0:a:0"])
    decode_command.extend(
        [
            "-f",
            "null",
            "-",
        ]
    )
    decode = subprocess.run(
        decode_command,
        capture_output=True,
        text=True,
    )
    if decode.returncode:
        detail = decode.stderr.strip().splitlines()
        raise fr.DownloadError(
            f"MP4 cannot be fully decoded: {detail[-1] if detail else 'ffmpeg error'}"
        )
    return {
        "bytes": size,
        "duration": duration,
        "width": width,
        "height": height,
        "video_codec": video["codec_name"],
        "audio_codec": audio.get("codec_name") if audio else None,
        "sha256": fr.file_hash(path),
    }


def validate_payload(payload):
    if not isinstance(payload, dict) or not payload:
        raise fr.JobValidationError("payload must be a non-empty object")
    try:
        payload_bytes = fr.canonical_bytes(payload)
    except (TypeError, ValueError) as exc:
        raise fr.JobValidationError(f"payload must be canonical JSON: {exc}") from exc

    input_urls = []

    def inspect(value, path):
        if isinstance(value, dict):
            for key, child in value.items():
                if not isinstance(key, str) or not key:
                    raise fr.JobValidationError(f"{path} contains a non-string or empty key")
                inspect(child, f"{path}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                inspect(child, f"{path}[{index}]")
        elif isinstance(value, str) and re.match(r"^https?://", value, re.IGNORECASE):
            input_urls.append(permanent_https_url(value, path))

    inspect(payload, "payload")
    return payload_bytes, list(dict.fromkeys(input_urls))


def validate_expect(expect):
    if not isinstance(expect, dict) or set(expect) != EXPECT_FIELDS:
        raise fr.JobValidationError(
            f"expect must contain exactly: {', '.join(sorted(EXPECT_FIELDS))}"
        )
    if expect.get("kind") != "video":
        raise fr.JobValidationError("expect.kind must be video")
    duration = expect.get("duration_seconds")
    tolerance = expect.get("duration_tolerance_seconds")
    if (
        not isinstance(duration, (int, float))
        or isinstance(duration, bool)
        or duration <= 0
        or not isinstance(tolerance, (int, float))
        or isinstance(tolerance, bool)
        or tolerance < 0
    ):
        raise fr.JobValidationError("expect duration and tolerance must be non-negative numbers")
    if expect.get("audio") not in {"required", "optional", "forbidden"}:
        raise fr.JobValidationError("expect.audio must be required, optional, or forbidden")
    for field in ("min_bytes", "min_width", "min_height"):
        value = expect.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise fr.JobValidationError(f"expect.{field} must be a non-negative integer")
    if expect.get("orientation") not in {"portrait", "landscape", "any"}:
        raise fr.JobValidationError("expect.orientation must be portrait, landscape, or any")
    return dict(expect)

def validate_and_prepare_job(job_path, routes_path=ROUTES_PATH):
    job = fr.read_object(job_path)
    unknown = set(job) - JOB_FIELDS
    missing = JOB_FIELDS - set(job)
    if unknown:
        raise fr.JobValidationError(
            f"unsupported job fields: {', '.join(sorted(unknown))}"
        )
    if missing:
        raise fr.JobValidationError(f"missing job fields: {', '.join(sorted(missing))}")
    if job.get("schema_version") != SCHEMA_VERSION:
        raise fr.JobValidationError(
            f"schema_version must be {SCHEMA_VERSION} (generic video execution contract)"
        )
    job_id = job.get("job_id")
    if not isinstance(job_id, str) or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", job_id
    ):
        raise fr.JobValidationError("invalid job_id")
    route_id = job.get("route")
    route, route_sha256 = load_route(route_id, routes_path)
    if job.get("artifact_kind") != ARTIFACT_KIND:
        raise fr.JobValidationError(f"artifact_kind must be {ARTIFACT_KIND}")

    payload = job.get("payload")
    payload_bytes, input_urls = validate_payload(payload)
    payload_sha256 = hashlib.sha256(payload_bytes).hexdigest()
    expect = validate_expect(job.get("expect"))
    expect_sha256 = hashlib.sha256(fr.canonical_bytes(expect)).hexdigest()

    output_dir_value, output_path_value = job.get("output_dir"), job.get("output_path")
    if not isinstance(output_dir_value, str) or not isinstance(output_path_value, str):
        raise fr.JobValidationError("output_dir and output_path must be strings")
    output_dir = Path(output_dir_value).expanduser()
    relative = Path(output_path_value)
    if not output_dir.is_absolute() or not str(relative) or relative.is_absolute():
        raise fr.JobValidationError("output_dir must be absolute and output_path relative")
    output_dir, output = output_dir.resolve(), (output_dir / relative).resolve()
    if not output.is_relative_to(output_dir) or output.suffix.lower() != ".mp4":
        raise fr.JobValidationError("output_path must be an MP4 inside output_dir")

    supabase = job.get("supabase")
    if not isinstance(supabase, dict):
        raise fr.JobValidationError("supabase must be an object")
    unknown_supabase = set(supabase) - SUPABASE_FIELDS
    missing_supabase = SUPABASE_FIELDS - set(supabase)
    if unknown_supabase or missing_supabase:
        raise fr.JobValidationError("supabase must contain exactly game, episode, and name")
    for field in sorted(SUPABASE_FIELDS):
        value = supabase.get(field)
        if not isinstance(value, str) or not value.strip():
            raise fr.JobValidationError(f"supabase.{field} must be a non-empty string")
    if not supabase["name"].lower().endswith(".mp4"):
        raise fr.JobValidationError("supabase.name must end with .mp4")
    upload_args = [
        "--kind",
        "episode-scene",
        "--game",
        supabase["game"],
        "--episode",
        supabase["episode"],
        "--name",
        supabase["name"],
    ]

    state_dir = output_dir / "build" / "video" / job_id
    claim_key = hashlib.sha256(str(output).encode()).hexdigest()[:24]
    claim_dir = output_dir / "build" / "video" / "_claims"
    contract = {
        "schema_version": SCHEMA_VERSION,
        "job_id": job_id,
        "route": route_id,
        "route_sha256": route_sha256,
        "artifact_kind": ARTIFACT_KIND,
        "payload_sha256": payload_sha256,
        "input_urls": input_urls,
        "expect_sha256": expect_sha256,
        "output_path": str(output),
        "upload_args": upload_args,
    }
    contract_sha256 = hashlib.sha256(fr.canonical_bytes(contract)).hexdigest()
    return {
        "job_id": job_id,
        "route_id": route_id,
        "route_sha256": route_sha256,
        "artifact_kind": ARTIFACT_KIND,
        "submit_url": route["submit_url"],
        "poll_base": route["poll_base"],
        "result_url_path": route["result_url_path"],
        "payload": payload,
        "payload_bytes": payload_bytes,
        "payload_sha256": payload_sha256,
        "input_urls": input_urls,
        "expect": expect,
        "expect_sha256": expect_sha256,
        "contract_sha256": contract_sha256,
        "output_path": output,
        "upload_args": upload_args,
        "state_dir": state_dir,
        "state_path": state_dir / "state.json",
        "request_path": state_dir / "request.json",
        "claim_path": claim_dir / f"{claim_key}.json",
        "lock_path": claim_dir / f"{claim_key}.lock",
    }



def expected_claim(job):
    return {
        "schema_version": SCHEMA_VERSION,
        "job_id": job["job_id"],
        "route": job["route_id"],
        "route_sha256": job["route_sha256"],
        "artifact_kind": job["artifact_kind"],
        "payload_sha256": job["payload_sha256"],
        "expect_sha256": job["expect_sha256"],
        "contract_sha256": job["contract_sha256"],
        "output_path": str(job["output_path"]),
        "state_path": str(job["state_path"]),
        "submit_url": job["submit_url"],
        "poll_base": job["poll_base"],
    }


def verify_claim(job):
    claim = fr.read_object(job["claim_path"], fr.StateError)
    for key, expected in expected_claim(job).items():
        if claim.get(key) != expected:
            raise fr.StateError("output_path is already claimed by another job contract")
    return claim


def expected_state_fields(job):
    return {
        "schema_version": SCHEMA_VERSION,
        "job_id": job["job_id"],
        "route": job["route_id"],
        "route_sha256": job["route_sha256"],
        "artifact_kind": job["artifact_kind"],
        "submit_url": job["submit_url"],
        "poll_base": job["poll_base"],
        "payload_sha256": job["payload_sha256"],
        "expect_sha256": job["expect_sha256"],
        "contract_sha256": job["contract_sha256"],
        "output_path": str(job["output_path"]),
    }


def verify_existing_state(job):
    state = fr.read_object(job["state_path"], fr.StateError)
    for key, expected in expected_state_fields(job).items():
        if state.get(key) != expected:
            raise fr.StateError(f"state mismatch for {key}")
    if not job["request_path"].exists() or fr.file_hash(job["request_path"]) != job["payload_sha256"]:
        raise fr.StateError("request.json does not match payload_sha256")
    return state


class KlingRunner:
    def __init__(
        self,
        job,
        transport,
        poll_interval_seconds=15,
        poll_timeout_seconds=140,
        sleeper=time.sleep,
        monotonic=time.monotonic,
        allow_paid_retry=False,
    ):
        self.job, self.transport = dict(job), transport
        self.interval, self.timeout = poll_interval_seconds, poll_timeout_seconds
        self.sleep, self.clock = sleeper, monotonic
        self.allow_paid_retry = allow_paid_retry

    def save(self, state):
        state["updated_at"] = fr.now()
        fr.atomic_json(self.job["state_path"], state)

    def claim_output(self):
        expected = expected_claim(self.job)
        if fr.exclusive_json(self.job["claim_path"], expected):
            return
        verify_claim(self.job)

    def state(self):
        path, request = self.job["state_path"], self.job["request_path"]
        if not path.exists():
            if self.job["output_path"].exists():
                raise fr.StateError("output exists without matching state; preserve it and stop")
            fr.atomic_bytes(request, self.job["payload_bytes"])
            state = {
                **expected_state_fields(self.job),
                "phase": "PREPARED",
                "attempts": [],
                "downloads": 0,
                "result_url": None,
                "checked_input_urls": [],
                "validation": None,
                "supabase_url": None,
                "error": None,
                "created_at": fr.now(),
            }
            self.save(state)
            return state
        return verify_existing_state(self.job)

    def fail(self, state, phase, error):
        state.update(phase=phase, error=error)
        self.save(state)

    def check_inputs(self, state):
        checked = set(state.get("checked_input_urls") or [])
        for url in self.job["input_urls"]:
            if url in checked:
                continue
            try:
                self.transport.check_url(url)
            except fr.HttpResponseError as exc:
                self.fail(state, "INPUT_REJECTED", {"input_url": url, "http_status": exc.status_code})
                raise fr.RemoteGenerationError(
                    f"input URL rejected with HTTP {exc.status_code}: {url}"
                ) from exc
            except fr.TransportError as exc:
                self.fail(state, "PENDING", f"input URL check interrupted: {exc}")
                raise fr.RemoteGenerationError("input URL check failed; rerun before submit") from exc
            checked.add(url)
            state["checked_input_urls"] = sorted(checked)
            self.save(state)

    def interrupted_request(self, state, stage, exc):
        if isinstance(exc, fr.HttpResponseError) and exc.status_code in {400, 404, 422}:
            self.fail(state, "FAILED", {"stage": stage, "http_status": exc.status_code})
            raise fr.RemoteGenerationError(
                f"{stage} failed with terminal HTTP {exc.status_code}"
            ) from exc
        phase = (
            "AUTH_ERROR"
            if isinstance(exc, fr.HttpResponseError) and exc.status_code in {401, 403}
            else "PENDING"
        )
        self.fail(state, phase, f"{stage} interrupted: {exc}")
        raise fr.RemoteGenerationError(f"{stage} failed; rerun to resume request_id") from exc

    def get_json(self, state, stage, url):
        for retry in range(2):
            try:
                return self.transport.get_json(url)
            except (fr.TransportError, fr.HttpResponseError) as exc:
                transient = isinstance(exc, fr.TransportError) or exc.status_code in (
                    RETRYABLE_HTTP | AMBIGUOUS_SUBMIT_HTTP
                )
                if transient and retry == 0:
                    self.sleep(5)
                    continue
                self.interrupted_request(state, stage, exc)

    def submit(self, state):
        if len(state["attempts"]) >= MAX_GENERATION_ATTEMPTS:
            self.fail(state, "FAILED", "generation failed twice")
            raise fr.RemoteGenerationError("generation failed twice")
        attempt = {
            "number": len(state["attempts"]) + 1,
            "phase": "SUBMITTING",
            "request_id": None,
        }
        state["attempts"].append(attempt)
        state["phase"] = "SUBMITTING"
        self.save(state)
        try:
            response = self.transport.submit(self.job["submit_url"], self.job["request_path"])
        except fr.HttpResponseError as exc:
            if exc.status_code in AMBIGUOUS_SUBMIT_HTTP:
                attempt.update(phase="UNKNOWN", http_status=exc.status_code, error=exc.body)
                self.fail(state, "UNKNOWN", {"http_status": exc.status_code, "detail": exc.body})
                raise fr.AmbiguousSubmitError(
                    "submit may have succeeded behind a server error; refusing a duplicate paid POST"
                ) from exc
            attempt.update(phase="SUBMIT_FAILED", http_status=exc.status_code, error=exc.body)
            self.save(state)
            if exc.status_code in RETRYABLE_HTTP and len(state["attempts"]) < 2:
                self.sleep(15)
                return None
            phase = "INPUT_REJECTED" if exc.status_code in {400, 422} else "FAILED"
            self.fail(state, phase, {"http_status": exc.status_code, "detail": exc.body})
            raise fr.RemoteGenerationError(f"submit HTTP {exc.status_code}") from exc
        except fr.TransportError as exc:
            attempt.update(phase="UNKNOWN", error=str(exc))
            self.fail(state, "UNKNOWN", str(exc))
            raise fr.AmbiguousSubmitError("submit response lost; refusing a duplicate paid POST") from exc
        request_id = response.get("request_id")
        if not isinstance(request_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,200}", request_id):
            attempt.update(phase="UNKNOWN", response=response)
            self.fail(state, "UNKNOWN", "submit returned no usable request_id")
            raise fr.AmbiguousSubmitError("submit returned no usable request_id")
        base = self.job["poll_base"]
        attempt.update(
            phase="SUBMITTED",
            request_id=request_id,
            status_url=f"{base}/requests/{request_id}/status",
            response_url=f"{base}/requests/{request_id}",
            remote_status=response.get("status", "IN_QUEUE"),
        )
        state["phase"] = "SUBMITTED"
        self.save(state)
        return attempt

    def poll(self, state, attempt):
        deadline = self.clock() + self.timeout
        while self.clock() < deadline:
            response = self.get_json(state, "poll", attempt["status_url"])
            remote_status = response.get("status")
            attempt["remote_status"] = remote_status
            if remote_status in PENDING:
                state["phase"] = "RUNNING"
                self.save(state)
                self.sleep(self.interval)
                continue
            if remote_status in REMOTE_FAILURE or (
                remote_status == "COMPLETED" and (response.get("error") or response.get("error_type"))
            ):
                attempt.update(phase="REMOTE_FAILED", error=response.get("error") or response)
                self.save(state)
                return False
            if remote_status == "COMPLETED":
                attempt["phase"] = "COMPLETED"
                state["phase"] = "RESULT_READY"
                self.save(state)
                return True
            self.fail(state, "PENDING", f"unknown remote status: {remote_status!r}")
            raise fr.RemoteGenerationError("unknown remote status; no replacement submitted")
        self.fail(state, "PENDING", "local polling window elapsed")
        raise fr.RemoteGenerationError("polling window elapsed; rerun to resume request_id")

    def result_url(self, state, attempt, force=False):
        if not force and state.get("result_url"):
            return state["result_url"]
        result = self.get_json(state, "result fetch", attempt["response_url"])
        value = result
        for key in self.job["result_url_path"]:
            value = value.get(key) if isinstance(value, dict) else None
        url = value
        if not fr.https_url(url):
            self.fail(
                state,
                "RESULT_READY",
                {
                    "detail": "result has no URL at configured result_url_path",
                    "result_url_path": self.job["result_url_path"],
                    "response": result,
                },
            )
            raise fr.RemoteGenerationError("provider result has no valid configured video URL")
        state["result_url"] = url
        self.save(state)
        return url

    def download(self, state, attempt):
        output = self.job["output_path"]
        part = output.with_name(output.name + ".part")
        output.parent.mkdir(parents=True, exist_ok=True)
        for candidate in (output, part):
            if candidate.exists():
                try:
                    metadata = validate_mp4(candidate, self.job["expect"])
                except fr.DownloadError:
                    if candidate == part:
                        part.unlink(missing_ok=True)
                else:
                    if candidate == part:
                        fr.durable_replace(part, output)
                    state.update(phase="VALIDATED", validation=metadata, error=None)
                    self.save(state)
                    return
        refresh = False
        while state["downloads"] < MAX_DOWNLOAD_ATTEMPTS:
            url = self.result_url(state, attempt, force=refresh)
            refresh = False
            state["phase"] = "DOWNLOADING"
            self.save(state)
            try:
                self.transport.download(url, part)
                metadata = validate_mp4(part, self.job["expect"])
                fr.durable_replace(part, output)
                state.update(phase="VALIDATED", validation=metadata, error=None)
                self.save(state)
                return
            except (fr.DownloadError, OSError) as exc:
                part.unlink(missing_ok=True)
                state["downloads"] += 1
                state["error"] = str(exc)
                self.save(state)
                if isinstance(exc, fr.DownloadHttpError) and exc.status_code in EXPIRED_LINK_HTTP:
                    refresh = True
                if state["downloads"] < MAX_DOWNLOAD_ATTEMPTS:
                    self.sleep(10)
        last_error = state.get("error") or "no error recorded"
        self.fail(
            state,
            "FAILED",
            {"detail": "download failed twice", "last_error": last_error},
        )
        raise fr.DownloadError(f"download failed twice: {last_error}")

    def finalize_upload(self, state):
        if state["phase"] == "DONE":
            return
        if not state.get("supabase_url"):
            try:
                state["supabase_url"] = self.transport.upload_asset(
                    self.job["upload_args"], self.job["output_path"]
                )
            except fr.UploadError as exc:
                state["error"] = f"upload failed: {exc}"
                self.save(state)
                raise
        state.update(phase="DONE", error=None)
        self.save(state)

    def run(self):
        with fr.job_lock(self.job["lock_path"]):
            self.claim_output()
            state = self.state()
            if state["phase"] == "DONE":
                metadata = validate_mp4(self.job["output_path"], self.job["expect"])
                if state["validation"]["sha256"] != metadata["sha256"]:
                    raise fr.StateError("validated output changed")
                return self.summary(state, True)
            if state["phase"] in {"FAILED", "INPUT_REJECTED"}:
                raise fr.RemoteGenerationError("job is terminal; automatic resubmission is forbidden")
            if state["phase"] == "VALIDATED":
                self.finalize_upload(state)
                return self.summary(state)
            attempts = state["attempts"]
            if (
                attempts
                and attempts[-1]["phase"] in {"SUBMITTING", "UNKNOWN"}
                and not attempts[-1]["request_id"]
            ):
                self.fail(state, "UNKNOWN", "submit may have succeeded without saved request_id")
                raise fr.AmbiguousSubmitError("ambiguous previous submit; refusing duplicate POST")
            self.check_inputs(state)
            while True:
                attempt = state["attempts"][-1] if state["attempts"] else None
                if attempt and attempt.get("request_id") and attempt["phase"] != "REMOTE_FAILED":
                    if attempt["phase"] != "COMPLETED" and not self.poll(state, attempt):
                        continue
                    self.download(state, attempt)
                    self.finalize_upload(state)
                    return self.summary(state)
                if attempt and attempt["phase"] == "REMOTE_FAILED" and len(state["attempts"]) >= 2:
                    self.fail(state, "FAILED", "remote generation failed twice")
                    raise fr.RemoteGenerationError("remote generation failed twice")
                if attempt and attempt["phase"] == "REMOTE_FAILED" and not self.allow_paid_retry:
                    self.fail(
                        state,
                        "PAID_RETRY_REQUIRED",
                        "remote generation failed; a second paid POST requires --allow-paid-retry",
                    )
                    raise fr.RemoteGenerationError(
                        "remote generation failed; rerun the same job with --allow-paid-retry to authorize one replacement POST"
                    )
                if self.submit(state) is None and len(state["attempts"]) >= 2:
                    self.fail(state, "FAILED", "submit failed twice")
                    raise fr.RemoteGenerationError("submit failed twice")

    def summary(self, state, skipped=False):
        return {
            "ok": True,
            "job_id": self.job["job_id"],
            "route": self.job["route_id"],
            "route_sha256": self.job["route_sha256"],
            "payload_sha256": self.job["payload_sha256"],
            "expect": self.job["expect"],
            "phase": state["phase"],
            "output_path": str(self.job["output_path"]),
            "state_path": str(self.job["state_path"]),
            "generation_attempts": len(state["attempts"]),
            "download_attempts": state["downloads"],
            "skipped": skipped,
            "validation": state["validation"],
            "supabase_url": state.get("supabase_url"),
        }


def preflight_summary(job):
    return {
        "ok": True,
        "preflight": True,
        "job_id": job["job_id"],
        "route": job["route_id"],
        "route_sha256": job["route_sha256"],
        "artifact_kind": job["artifact_kind"],
        "payload_sha256": job["payload_sha256"],
        "expect": job["expect"],
        "contract_sha256": job["contract_sha256"],
        "output_path": str(job["output_path"]),
        "state_path": str(job["state_path"]),
        "upload_args": job["upload_args"],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Durable fal.ai video execution runner")
    parser.add_argument("job", type=Path)
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument(
        "--allow-paid-retry",
        action="store_true",
        help="authorize one replacement POST after a definitive remote generation failure",
    )
    parser.add_argument("--poll-interval", type=float, default=15)
    # 140s per-invocation poll window: the runner self-exits gracefully into a
    # resumable PENDING state at 140s instead of being SIGKILLed by an external
    # ~120s tool timeout mid-download. Invoke this runner with a Bash timeout of
    # ~150s so the 140s window runs uninterrupted. On resume the fal result URL
    # is re-fetched fresh (see result_url force + EXPIRED_LINK_HTTP handling),
    # so the link never goes stale across a resume.
    parser.add_argument("--poll-timeout", type=float, default=140)
    parser.add_argument(
        "--env-file",
        type=Path,
        default=Path(__file__).resolve().parents[1] / ".env",
    )
    args = parser.parse_args(argv)
    job_id = None
    try:
        if args.allow_paid_retry and args.preflight:
            raise fr.JobValidationError(
                "--allow-paid-retry is valid only for a real runner invocation"
            )
        job = validate_and_prepare_job(args.job.resolve())
        job_id = job["job_id"]
        if args.preflight:
            result = preflight_summary(job)
        else:
            if args.poll_interval < 1 or args.poll_timeout <= 0:
                raise fr.JobValidationError("invalid polling values")
            fr.load_env(args.env_file.expanduser())
            key = os.environ.get("FAL_KEY", "").strip()
            if not key:
                raise fr.JobValidationError("FAL_KEY is missing")
            result = KlingRunner(
                job,
                fr.CurlTransport(key),
                args.poll_interval,
                args.poll_timeout,
                allow_paid_retry=args.allow_paid_retry,
            ).run()
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
        return 0
    except fr.RunnerError as exc:
        print(
            json.dumps(
                {
                    "ok": False,
                    "job_id": job_id,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                },
                ensure_ascii=False,
                separators=(",", ":"),
            ),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
