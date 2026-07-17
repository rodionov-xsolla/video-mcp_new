#!/usr/bin/env python3
"""Small, resumable fal.ai runner for allowlisted Nano Banana 2 requests."""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import zlib
from pathlib import Path
from urllib.parse import urlparse


ROUTES = {
    "nb2.text": (
        "https://queue.fal.run/fal-ai/nano-banana-2",
        "https://queue.fal.run/fal-ai/nano-banana-2",
        False,
    ),
    "nb2.edit": (
        "https://queue.fal.run/fal-ai/nano-banana-2/edit",
        "https://queue.fal.run/fal-ai/nano-banana-2",
        True,
    ),
}
CONSTANTS = {
    "aspect_ratio": "9:16",
    "num_images": 1,
    "output_format": "png",
    "resolution": "1K",
    "safety_tolerance": "5",
}
MAX_GENERATION_ATTEMPTS = 2
MAX_DOWNLOAD_ATTEMPTS = 2
PENDING = {"IN_QUEUE", "IN_PROGRESS"}
REMOTE_FAILURE = {"FAILED", "ERROR"}
RETRYABLE_HTTP = {429}
AMBIGUOUS_SUBMIT_HTTP = {500, 502, 503, 504}
EXPIRED_LINK_HTTP = {403, 404, 410}
SUPABASE_FIELDS = {"game", "episode", "name", "slug", "variant", "tags"}
UPLOAD_KIND_BY_ARTIFACT = {
    "scene_start": "episode-scene",
    "character_reference": "character",
    "location_reference": "location",
}
JOB_FIELDS = {
    "schema_version",
    "job_id",
    "route",
    "artifact_kind",
    "output_dir",
    "output_path",
    "input",
    "supabase",
}
ARTIFACT_KINDS = {"scene_start", "character_reference", "location_reference"}


class RunnerError(RuntimeError):
    pass


class JobValidationError(RunnerError):
    pass


class StateError(RunnerError):
    pass


class AmbiguousSubmitError(RunnerError):
    pass


class RemoteGenerationError(RunnerError):
    pass


class TransportError(RunnerError):
    pass


class DownloadError(RunnerError):
    pass


class DownloadHttpError(DownloadError):
    def __init__(self, status_code, body):
        self.status_code = status_code
        super().__init__(body)


class UploadError(RunnerError):
    pass


class HttpResponseError(RunnerError):
    def __init__(self, status_code, body):
        self.status_code, self.body = status_code, body
        super().__init__(f"fal HTTP {status_code}")


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def canonical_bytes(value):
    try:
        return json.dumps(
            value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")
        ).encode()
    except (TypeError, ValueError) as exc:
        raise JobValidationError(f"non-JSON job data: {exc}") from exc


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_bytes(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp = Path(temp)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
        fsync_directory(path.parent)
    finally:
        temp.unlink(missing_ok=True)


def atomic_json(path, value):
    atomic_bytes(path, (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode())


def fsync_directory(path):
    directory_fd = os.open(Path(path), os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def durable_replace(source, destination):
    os.replace(source, destination)
    fsync_directory(Path(destination).parent)


def exclusive_json(path, value):
    """Create a durable file once; never overwrite an existing ownership claim."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return False
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        fsync_directory(path.parent)
    except Exception:
        path.unlink(missing_ok=True)
        raise
    return True


def read_object(path, error_type=JobValidationError):
    try:
        value = json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise error_type(f"invalid JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise error_type(f"JSON root must be an object: {path}")
    return value


def https_url(value):
    parsed = urlparse(value) if isinstance(value, str) else None
    return bool(parsed and parsed.scheme == "https" and parsed.netloc)


def validate_and_prepare_job(job_path):
    job = read_object(job_path)
    unknown_job_fields = set(job) - JOB_FIELDS
    if unknown_job_fields:
        raise JobValidationError(
            f"unsupported job fields: {', '.join(sorted(unknown_job_fields))}"
        )
    if job.get("schema_version") != 1:
        raise JobValidationError("schema_version must be 1")
    job_id = job.get("job_id")
    if not isinstance(job_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", job_id):
        raise JobValidationError("invalid job_id")
    route_id = job.get("route")
    if route_id not in ROUTES:
        raise JobValidationError("route must be nb2.text or nb2.edit")
    submit_url, poll_base, needs_refs = ROUTES[route_id]
    artifact_kind = job.get("artifact_kind")
    if artifact_kind not in ARTIFACT_KINDS:
        raise JobValidationError(
            f"artifact_kind must be one of: {', '.join(sorted(ARTIFACT_KINDS))}"
        )

    inputs = job.get("input")
    if not isinstance(inputs, dict):
        raise JobValidationError("input must be an object")
    unknown = set(inputs) - {"prompt", "image_urls", "seed"}
    if unknown:
        raise JobValidationError(f"unsupported input fields: {', '.join(sorted(unknown))}")
    prompt = inputs.get("prompt")
    if not isinstance(prompt, str) or not 3 <= len(prompt.strip()) <= 50_000:
        raise JobValidationError("input.prompt must contain 3..50000 characters")
    refs = inputs.get("image_urls")
    if needs_refs:
        if not isinstance(refs, list) or not 1 <= len(refs) <= 4:
            raise JobValidationError("nb2.edit requires 1..4 image_urls")
        if any(not https_url(url) for url in refs):
            raise JobValidationError("image_urls must contain HTTPS URLs")
        if len(set(refs)) != len(refs):
            raise JobValidationError("image_urls must not contain duplicates")
        if any("fal.media" in urlparse(url).netloc.lower() for url in refs):
            raise JobValidationError("temporary fal.media refs are forbidden")
    elif "image_urls" in inputs:
        raise JobValidationError("nb2.text must omit image_urls entirely")
    if "seed" in inputs and (not isinstance(inputs["seed"], int) or isinstance(inputs["seed"], bool)):
        raise JobValidationError("input.seed must be an integer")

    output_dir_value, output_path_value = job.get("output_dir"), job.get("output_path")
    if not isinstance(output_dir_value, str) or not isinstance(output_path_value, str):
        raise JobValidationError("output_dir and output_path must be strings")
    output_dir = Path(output_dir_value).expanduser()
    relative = Path(output_path_value)
    if not output_dir.is_absolute() or not str(relative) or relative.is_absolute():
        raise JobValidationError("output_dir must be absolute and output_path relative")
    output_dir, output = output_dir.resolve(), (output_dir / relative).resolve()
    if not output.is_relative_to(output_dir) or output.suffix.lower() != ".png":
        raise JobValidationError("output_path must be a PNG inside output_dir")
    if re.search(r"(?:^|[-_])(end|endframe|end-frame)(?:[-_.]|$)", output.name.lower()):
        raise JobValidationError("end-frame outputs are forbidden")

    supabase_cfg = job.get("supabase")
    upload_args = None
    if supabase_cfg is not None:
        if not isinstance(supabase_cfg, dict):
            raise JobValidationError("supabase must be an object")
        unknown_supabase = set(supabase_cfg) - SUPABASE_FIELDS
        if unknown_supabase:
            raise JobValidationError(
                f"unsupported supabase fields: {', '.join(sorted(unknown_supabase))}"
            )
        game = supabase_cfg.get("game")
        if not isinstance(game, str) or not game.strip():
            raise JobValidationError("supabase.game must be a non-empty string")
        upload_kind = UPLOAD_KIND_BY_ARTIFACT[artifact_kind]
        upload_args = ["--kind", upload_kind, "--game", game]
        if upload_kind == "episode-scene":
            episode, name = supabase_cfg.get("episode"), supabase_cfg.get("name")
            if not isinstance(episode, str) or not episode.strip():
                raise JobValidationError("supabase.episode is required for scene_start uploads")
            if not isinstance(name, str) or not name.strip():
                raise JobValidationError("supabase.name is required for scene_start uploads")
            upload_args += ["--episode", episode, "--name", name]
        else:
            slug = supabase_cfg.get("slug")
            if not isinstance(slug, str) or not slug.strip():
                raise JobValidationError(
                    "supabase.slug is required for character/location uploads"
                )
            upload_args += ["--slug", slug]
            variant = supabase_cfg.get("variant")
            if variant is not None:
                if not isinstance(variant, str) or not variant.strip():
                    raise JobValidationError("supabase.variant must be a non-empty string")
                upload_args += ["--variant", variant]
        tags = supabase_cfg.get("tags")
        if tags is not None:
            if not isinstance(tags, str) or not tags.strip():
                raise JobValidationError("supabase.tags must be a non-empty string")
            upload_args += ["--tags", tags]

    payload = dict(CONSTANTS, prompt=prompt)
    if refs is not None:
        payload["image_urls"] = refs
    if "seed" in inputs:
        payload["seed"] = inputs["seed"]
    payload_bytes = canonical_bytes(payload)
    payload_sha256 = hashlib.sha256(payload_bytes).hexdigest()
    state_dir = output_dir / "build" / "fal" / job_id
    claim_key = hashlib.sha256(str(output).encode()).hexdigest()[:24]
    claim_dir = output_dir / "build" / "fal" / "_claims"
    contract = {
        "schema_version": 1,
        "job_id": job_id,
        "route": route_id,
        "artifact_kind": artifact_kind,
        "submit_url": submit_url,
        "poll_base": poll_base,
        "payload_sha256": payload_sha256,
        "output_path": str(output),
        "upload_args": upload_args,
    }
    contract_sha256 = hashlib.sha256(canonical_bytes(contract)).hexdigest()
    return {
        "job_id": job_id,
        "route_id": route_id,
        "artifact_kind": artifact_kind,
        "submit_url": submit_url,
        "poll_base": poll_base,
        "payload": payload,
        "payload_bytes": payload_bytes,
        "payload_sha256": payload_sha256,
        "contract_sha256": contract_sha256,
        "output_path": output,
        "upload_args": upload_args,
        "state_dir": state_dir,
        "state_path": state_dir / "state.json",
        "request_path": state_dir / "request.json",
        "claim_path": claim_dir / f"{claim_key}.json",
        "lock_path": claim_dir / f"{claim_key}.lock",
    }


def validate_png(path):
    try:
        data = Path(path).read_bytes()
    except OSError as exc:
        raise DownloadError(f"cannot read PNG: {exc}") from exc
    if len(data) <= 1000 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise DownloadError("PNG is missing, undersized, or has a bad signature")
    offset, width, height, idat, iend = 8, 0, 0, [], False
    while offset + 12 <= len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        end = offset + 12 + length
        if end > len(data):
            raise DownloadError("PNG has a truncated chunk")
        kind, body = data[offset + 4 : offset + 8], data[offset + 8 : offset + 8 + length]
        expected = struct.unpack(">I", data[offset + 8 + length : end])[0]
        if expected != zlib.crc32(kind + body) & 0xFFFFFFFF:
            raise DownloadError("PNG chunk CRC is invalid")
        if kind == b"IHDR":
            if length != 13:
                raise DownloadError("PNG IHDR is invalid")
            width, height = struct.unpack(">II", body[:8])
        elif kind == b"IDAT":
            idat.append(body)
        elif kind == b"IEND":
            iend = True
            break
        offset = end
    try:
        decoded = zlib.decompress(b"".join(idat))
    except zlib.error as exc:
        raise DownloadError(f"PNG image data is invalid: {exc}") from exc
    ratio = width / height if height else 0
    allowed_ratio = abs(ratio - 9 / 16) <= 0.03 or abs(ratio - 2 / 3) <= 0.03
    if not (
        width >= 600
        and height >= 1000
        and decoded
        and iend
        and height > width
        and allowed_ratio
    ):
        raise DownloadError(f"PNG has an unsupported portrait ratio: {width}x{height}")
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise DownloadError("ffmpeg is required for full PNG decoding")
    decoded_image = subprocess.run(
        [
            ffmpeg,
            "-v",
            "error",
            "-xerror",
            "-i",
            str(path),
            "-frames:v",
            "1",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
    )
    if decoded_image.returncode:
        detail = decoded_image.stderr.strip().splitlines()
        message = detail[-1] if detail else "ffmpeg error"
        raise DownloadError(f"PNG cannot be fully decoded: {message}")
    return {"bytes": len(data), "width": width, "height": height, "sha256": file_hash(path)}


def expected_claim(job):
    claim = {
        "schema_version": 1,
        "job_id": job["job_id"],
        "route": job["route_id"],
        "artifact_kind": job["artifact_kind"],
        "payload_sha256": job["payload_sha256"],
        "output_path": str(job["output_path"]),
        "state_path": str(job["state_path"]),
        "submit_url": job["submit_url"],
        "poll_base": job["poll_base"],
        "contract_sha256": job["contract_sha256"],
    }
    return claim


def verify_claim(job):
    claim = read_object(job["claim_path"], StateError)
    for key, value in expected_claim(job).items():
        if key == "contract_sha256" and key not in claim:
            continue
        if claim.get(key) != value:
            raise StateError("output_path is already claimed by another job contract")
    return claim


def expected_state_fields(job):
    fields = {
        "schema_version": 1,
        "job_id": job["job_id"],
        "route": job["route_id"],
        "artifact_kind": job["artifact_kind"],
        "submit_url": job["submit_url"],
        "poll_base": job["poll_base"],
        "payload_sha256": job["payload_sha256"],
        "output_path": str(job["output_path"]),
        "contract_sha256": job["contract_sha256"],
    }
    return fields


def verify_existing_state(job):
    state = read_object(job["state_path"], StateError)
    for key, expected in expected_state_fields(job).items():
        if key == "contract_sha256" and key not in state:
            continue
        if state.get(key) != expected:
            raise StateError(f"state mismatch for {key}")
    request = job["request_path"]
    if not request.exists() or file_hash(request) != job["payload_sha256"]:
        raise StateError("request.json does not match payload_sha256")
    return state


def load_env(path):
    if not Path(path).exists():
        return
    for raw in Path(path).read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = (part.strip() for part in line.split("=", 1))
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ.setdefault(key, value)


class CurlTransport:
    def __init__(self, key, timeout=120):
        self.key, self.timeout = key, timeout
        self.curl = "/usr/bin/curl" if Path("/usr/bin/curl").exists() else "curl"

    def request(self, method, url, payload=None):
        fd, name = tempfile.mkstemp(prefix="fal-response-")
        os.close(fd)
        response = Path(name)
        command = [
            self.curl, "-sS", "-L", "--connect-timeout", "20", "--max-time", str(self.timeout),
            "-X", method, "-H", f"Authorization: Key {self.key}", "-o", str(response),
            "-w", "%{http_code}",
        ]
        if payload:
            command += ["-H", "Content-Type: application/json", "--data-binary", f"@{payload}"]
        try:
            process = subprocess.run(command + [url], capture_output=True, text=True)
            body_text = response.read_text(errors="replace")
        finally:
            response.unlink(missing_ok=True)
        status = process.stdout.strip()
        if process.returncode or not status.isdigit() or status == "000":
            raise TransportError(process.stderr.strip() or "no definitive HTTP response")
        try:
            body = json.loads(body_text)
        except json.JSONDecodeError:
            body = body_text[:50_000]
        if not 200 <= int(status) < 300:
            raise HttpResponseError(int(status), body)
        if not isinstance(body, dict):
            raise TransportError("fal response is not a JSON object")
        return body

    def submit(self, url, payload):
        return self.request("POST", url, payload)

    def get_json(self, url):
        return self.request("GET", url)

    def download(self, url, destination):
        process = subprocess.run(
            [
                self.curl, "-sS", "-L", "--connect-timeout", "20", "--max-time", str(self.timeout),
                "-o", str(destination), "-w", "%{http_code}", url,
            ],
            capture_output=True,
            text=True,
        )
        status = process.stdout.strip()
        if process.returncode or not status.isdigit() or not 200 <= int(status) < 300:
            Path(destination).unlink(missing_ok=True)
            detail = process.stderr.strip() or f"download HTTP {status}"
            if status.isdigit():
                raise DownloadHttpError(int(status), detail)
            raise DownloadError(detail)

    def check_url(self, url):
        process = subprocess.run(
            [
                self.curl,
                "-sS",
                "-L",
                "--connect-timeout",
                "10",
                "--max-time",
                "30",
                "-o",
                "/dev/null",
                "-w",
                "%{http_code}",
                url,
            ],
            capture_output=True,
            text=True,
        )
        status = process.stdout.strip()
        if process.returncode or not status.isdigit() or status == "000":
            raise TransportError(process.stderr.strip() or "reference check had no HTTP response")
        if not 200 <= int(status) < 300:
            raise HttpResponseError(int(status), "reference URL is not reachable")

    def verify_public_asset(self, url, file_path):
        fd, name = tempfile.mkstemp(prefix="supabase-verify-", suffix=Path(file_path).suffix)
        os.close(fd)
        remote_copy = Path(name)
        try:
            try:
                self.download(url, remote_copy)
            except DownloadError as exc:
                raise UploadError(f"uploaded public URL is not readable: {exc}") from exc
            if file_hash(remote_copy) != file_hash(file_path):
                raise UploadError("uploaded public file does not match the validated local PNG")
        finally:
            remote_copy.unlink(missing_ok=True)

    def upload_asset(self, args, file_path):
        script = Path(__file__).resolve().parents[1] / "queue" / "upload-asset.sh"
        command = ["/bin/bash", str(script), *args, "--", str(file_path)]
        try:
            process = subprocess.run(command, capture_output=True, text=True, timeout=self.timeout)
        except subprocess.TimeoutExpired as exc:
            raise UploadError(f"upload-asset.sh timed out: {exc}") from exc
        if process.returncode != 0:
            raise UploadError(process.stderr.strip() or f"upload-asset.sh exited {process.returncode}")
        if process.stderr.strip():
            raise UploadError(f"upload-asset.sh reported a warning: {process.stderr.strip()}")
        lines = [line.strip() for line in process.stdout.splitlines() if line.strip()]
        url = lines[-1] if lines else ""
        if not https_url(url):
            raise UploadError(f"upload-asset.sh returned no usable URL: {process.stdout[-500:]}")
        self.verify_public_asset(url, file_path)
        return url


@contextlib.contextmanager
def job_lock(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("a+") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise StateError("another runner already owns this job") from exc
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


class FalRunner:
    def __init__(self, job, transport, poll_interval_seconds=15, poll_timeout_seconds=600,
                 sleeper=time.sleep, monotonic=time.monotonic, verbose=False,
                 allow_paid_retry=False):
        self.job, self.transport = dict(job), transport
        self.interval, self.timeout = poll_interval_seconds, poll_timeout_seconds
        self.sleep, self.clock, self.verbose = sleeper, monotonic, verbose
        self.allow_paid_retry = allow_paid_retry

    def save(self, state):
        state["updated_at"] = now()
        atomic_json(self.job["state_path"], state)

    def claim_output(self):
        """Bind one canonical output path to one exact paid request contract."""
        expected = expected_claim(self.job)
        if exclusive_json(self.job["claim_path"], expected):
            return
        verify_claim(self.job)

    def state(self):
        path, request = self.job["state_path"], self.job["request_path"]
        if not path.exists():
            if self.job["output_path"].exists():
                raise StateError("output exists without matching state; archive it first")
            atomic_bytes(request, self.job["payload_bytes"])
            state = {
                "schema_version": 1,
                "job_id": self.job["job_id"], "route": self.job["route_id"],
                "artifact_kind": self.job["artifact_kind"],
                "submit_url": self.job["submit_url"], "poll_base": self.job["poll_base"],
                "payload_sha256": self.job["payload_sha256"], "output_path": str(self.job["output_path"]),
                "phase": "PREPARED", "attempts": [], "downloads": 0, "result_url": None,
                "refs_checked": False, "validation": None, "error": None, "created_at": now(),
                "supabase_url": None,
                "contract_sha256": self.job["contract_sha256"],
            }
            self.save(state)
            return state
        return verify_existing_state(self.job)

    def fail(self, state, phase, error):
        state.update(phase=phase, error=error)
        self.save(state)

    def check_refs(self, state):
        if state.get("refs_checked"):
            return
        for url in self.job["payload"].get("image_urls", []):
            try:
                self.transport.check_url(url)
            except HttpResponseError as exc:
                self.fail(
                    state,
                    "INPUT_REJECTED",
                    {"reference_url": url, "http_status": exc.status_code},
                )
                raise RemoteGenerationError(
                    f"reference URL rejected with HTTP {exc.status_code}"
                ) from exc
            except TransportError as exc:
                self.fail(state, "PENDING", f"reference check interrupted: {exc}")
                raise RemoteGenerationError("reference check failed; rerun before submit") from exc
        state["refs_checked"] = True
        self.save(state)

    def interrupted_request(self, state, stage, exc):
        if isinstance(exc, HttpResponseError) and exc.status_code in {400, 404, 422}:
            self.fail(state, "FAILED", {"stage": stage, "http_status": exc.status_code})
            raise RemoteGenerationError(f"{stage} failed with terminal HTTP {exc.status_code}") from exc
        phase = "AUTH_ERROR" if isinstance(exc, HttpResponseError) and exc.status_code in {401, 403} else "PENDING"
        self.fail(state, phase, f"{stage} interrupted: {exc}")
        raise RemoteGenerationError(f"{stage} failed; rerun to resume request_id") from exc

    def get_json(self, state, stage, url):
        for retry in range(2):
            try:
                return self.transport.get_json(url)
            except (TransportError, HttpResponseError) as exc:
                transient = isinstance(exc, TransportError) or exc.status_code in (
                    RETRYABLE_HTTP | AMBIGUOUS_SUBMIT_HTTP
                )
                if transient and retry == 0:
                    self.sleep(5)
                    continue
                self.interrupted_request(state, stage, exc)

    def submit(self, state):
        if len(state["attempts"]) >= MAX_GENERATION_ATTEMPTS:
            self.fail(state, "FAILED", "generation failed twice")
            raise RemoteGenerationError("generation failed twice")
        attempt = {"number": len(state["attempts"]) + 1, "phase": "SUBMITTING", "request_id": None}
        state["attempts"].append(attempt)
        state["phase"] = "SUBMITTING"
        self.save(state)
        try:
            response = self.transport.submit(self.job["submit_url"], self.job["request_path"])
        except HttpResponseError as exc:
            if exc.status_code in AMBIGUOUS_SUBMIT_HTTP:
                attempt.update(phase="UNKNOWN", http_status=exc.status_code, error=exc.body)
                self.fail(state, "UNKNOWN", {"http_status": exc.status_code, "detail": exc.body})
                raise AmbiguousSubmitError(
                    "submit may have succeeded behind a server error; refusing a duplicate paid POST"
                ) from exc
            attempt.update(phase="SUBMIT_FAILED", http_status=exc.status_code, error=exc.body)
            self.save(state)
            if exc.status_code in RETRYABLE_HTTP and len(state["attempts"]) < 2:
                self.sleep(15)
                return None
            phase = "INPUT_REJECTED" if exc.status_code in {400, 422} else "FAILED"
            self.fail(state, phase, {"http_status": exc.status_code, "detail": exc.body})
            raise RemoteGenerationError(f"submit HTTP {exc.status_code}") from exc
        except TransportError as exc:
            attempt.update(phase="UNKNOWN", error=str(exc))
            self.fail(state, "UNKNOWN", str(exc))
            raise AmbiguousSubmitError("submit response lost; refusing a duplicate paid POST") from exc
        request_id = response.get("request_id")
        if not isinstance(request_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,200}", request_id):
            attempt.update(phase="UNKNOWN", response=response)
            self.fail(state, "UNKNOWN", "submit returned no usable request_id")
            raise AmbiguousSubmitError("submit returned no usable request_id")
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
            status = response.get("status")
            attempt["remote_status"] = status
            if status in PENDING:
                state["phase"] = "RUNNING"
                self.save(state)
                self.sleep(self.interval)
                continue
            if status in REMOTE_FAILURE or (
                status == "COMPLETED" and (response.get("error") or response.get("error_type"))
            ):
                attempt.update(phase="REMOTE_FAILED", error=response.get("error") or response)
                self.save(state)
                return False
            if status == "COMPLETED":
                attempt["phase"] = "COMPLETED"
                state["phase"] = "RESULT_READY"
                self.save(state)
                return True
            self.fail(state, "PENDING", f"unknown remote status: {status!r}")
            raise RemoteGenerationError("unknown remote status; no replacement submitted")
        self.fail(state, "PENDING", "local polling window elapsed")
        raise RemoteGenerationError("polling window elapsed; rerun to resume request_id")

    def result_url(self, state, attempt, force=False):
        if not force and state.get("result_url"):
            return state["result_url"]
        result = self.get_json(state, "result fetch", attempt["response_url"])
        images = result.get("images")
        url = images[0].get("url") if isinstance(images, list) and images and isinstance(images[0], dict) else None
        if not https_url(url):
            self.fail(state, "RESULT_READY", {"detail": "result has no images[0].url", "response": result})
            raise RemoteGenerationError("NB2 result has no valid image URL")
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
                    metadata = validate_png(candidate)
                except DownloadError:
                    if candidate == part:
                        part.unlink(missing_ok=True)
                else:
                    if candidate == part:
                        durable_replace(part, output)
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
                metadata = validate_png(part)
                durable_replace(part, output)
                state.update(phase="VALIDATED", validation=metadata, error=None)
                self.save(state)
                return
            except (DownloadError, OSError) as exc:
                part.unlink(missing_ok=True)
                state["downloads"] += 1
                state["error"] = str(exc)
                self.save(state)
                if isinstance(exc, DownloadHttpError) and exc.status_code in EXPIRED_LINK_HTTP:
                    refresh = True
                if state["downloads"] < MAX_DOWNLOAD_ATTEMPTS:
                    self.sleep(10)
        last_error = state.get("error") or "no error recorded"
        self.fail(state, "FAILED", {"detail": "download failed twice", "last_error": last_error})
        raise DownloadError(f"download failed twice: {last_error}")

    def finalize_upload(self, state):
        """Upload the validated local PNG to Supabase; safe to retry without re-downloading."""
        if state["phase"] == "DONE":
            return
        upload_args = self.job.get("upload_args")
        if upload_args and not state.get("supabase_url"):
            try:
                state["supabase_url"] = self.transport.upload_asset(
                    upload_args, self.job["output_path"]
                )
            except UploadError as exc:
                state["error"] = f"upload failed: {exc}"
                self.save(state)
                raise
        state.update(phase="DONE", error=None)
        self.save(state)

    def run(self):
        with job_lock(self.job["lock_path"]):
            self.claim_output()
            state = self.state()
            if state["phase"] == "DONE":
                metadata = validate_png(self.job["output_path"])
                if state["validation"]["sha256"] != metadata["sha256"]:
                    raise StateError("validated output changed")
                return self.summary(state, True)
            if state["phase"] in {"FAILED", "INPUT_REJECTED"}:
                raise RemoteGenerationError("job is terminal; automatic resubmission is forbidden")
            if state["phase"] == "VALIDATED":
                self.finalize_upload(state)
                return self.summary(state)
            attempts = state["attempts"]
            if attempts and attempts[-1]["phase"] in {"SUBMITTING", "UNKNOWN"} and not attempts[-1]["request_id"]:
                self.fail(state, "UNKNOWN", "submit may have succeeded without saved request_id")
                raise AmbiguousSubmitError("ambiguous previous submit; refusing duplicate POST")
            self.check_refs(state)
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
                    raise RemoteGenerationError("remote generation failed twice")
                if attempt and attempt["phase"] == "REMOTE_FAILED" and not self.allow_paid_retry:
                    self.fail(
                        state,
                        "PAID_RETRY_REQUIRED",
                        "remote generation failed; a second paid POST requires --allow-paid-retry",
                    )
                    raise RemoteGenerationError(
                        "remote generation failed; rerun the same job with --allow-paid-retry to authorize one replacement POST"
                    )
                if self.submit(state) is None and len(state["attempts"]) >= 2:
                    self.fail(state, "FAILED", "submit failed twice")
                    raise RemoteGenerationError("submit failed twice")

    def summary(self, state, skipped=False):
        return {
            "ok": True, "job_id": self.job["job_id"], "route": self.job["route_id"],
            "phase": state["phase"], "output_path": str(self.job["output_path"]),
            "state_path": str(self.job["state_path"]), "generation_attempts": len(state["attempts"]),
            "download_attempts": state["downloads"], "skipped": skipped, "validation": state["validation"],
            "supabase_url": state.get("supabase_url"),
        }


def preflight_summary(job):
    return {
        "ok": True, "preflight": True, "job_id": job["job_id"], "route": job["route_id"],
        "artifact_kind": job["artifact_kind"],
        "payload_sha256": job["payload_sha256"], "output_path": str(job["output_path"]),
        "contract_sha256": job["contract_sha256"],
        "state_path": str(job["state_path"]), "refs": len(job["payload"].get("image_urls", [])),
        "request_constants": CONSTANTS, "upload_args": job["upload_args"],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Durable fal.ai NB2 request runner")
    parser.add_argument("job", type=Path)
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument(
        "--allow-paid-retry",
        action="store_true",
        help="authorize one replacement POST after a definitive remote generation failure",
    )
    parser.add_argument("--poll-interval", type=float, default=15)
    parser.add_argument("--poll-timeout", type=float, default=600)
    parser.add_argument("--env-file", type=Path, default=Path(__file__).resolve().parents[1] / ".env")
    args = parser.parse_args(argv)
    job_id = None
    try:
        if args.allow_paid_retry and args.preflight:
            raise JobValidationError(
                "--allow-paid-retry is valid only for a real runner invocation"
            )
        job = validate_and_prepare_job(args.job.resolve())
        job_id = job["job_id"]
        if args.preflight:
            result = preflight_summary(job)
        else:
            if args.poll_interval < 1 or args.poll_timeout <= 0:
                raise JobValidationError("invalid polling values")
            load_env(args.env_file.expanduser())
            key = os.environ.get("FAL_KEY", "").strip()
            if not key:
                raise JobValidationError("FAL_KEY is missing")
            transport = CurlTransport(key)
            result = FalRunner(
                job,
                transport,
                args.poll_interval,
                args.poll_timeout,
                allow_paid_retry=args.allow_paid_retry,
            ).run()
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
        return 0
    except RunnerError as exc:
        print(json.dumps({"ok": False, "job_id": job_id, "error_type": type(exc).__name__,
                          "error": str(exc)}, ensure_ascii=False, separators=(",", ":")), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
