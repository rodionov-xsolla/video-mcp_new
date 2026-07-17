import json
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest import mock


TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))

import fal_runner as fr  # noqa: E402


def png_chunk(kind: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + kind
        + data
        + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


def valid_portrait_png(width: int = 768, height: int = 1376) -> bytes:
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    row = b"\x00" + (b"\x25\x50\x75" * width)
    raw_pixels = row * height
    padding = b"runner-test\x00" + (b"x" * 1200)
    return (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"tEXt", padding)
        + png_chunk(b"IDAT", zlib.compress(raw_pixels))
        + png_chunk(b"IEND", b"")
    )


def truncated_pixel_png(width: int = 768, height: int = 1376) -> bytes:
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    one_row_only = b"\x00" + (b"\x25\x50\x75" * width)
    padding = b"runner-test\x00" + (b"x" * 1200)
    return (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"tEXt", padding)
        + png_chunk(b"IDAT", zlib.compress(one_row_only))
        + png_chunk(b"IEND", b"")
    )


VALID_PNG = valid_portrait_png()


class FakeTransport:
    curl = "/usr/bin/curl"

    def __init__(
        self,
        *,
        submits=None,
        statuses=None,
        results=None,
        downloads=None,
        ref_outcomes=None,
        uploads=None,
    ):
        self.submits = list(submits or [])
        self.statuses = list(statuses or [])
        self.results = list(results or [])
        self.downloads = list(downloads if downloads is not None else [VALID_PNG])
        self.ref_outcomes = list(ref_outcomes or [])
        self.uploads = list(uploads or [])
        self.submit_calls = []
        self.status_calls = []
        self.result_calls = []
        self.download_calls = []
        self.ref_checks = []
        self.upload_calls = []

    @staticmethod
    def _next(items, label):
        if not items:
            raise AssertionError(f"unexpected {label} call")
        outcome = items.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    def submit(self, url, payload_path):
        payload = Path(payload_path).read_bytes()
        self.submit_calls.append((url, payload))
        return self._next(self.submits, "submit")

    def get_json(self, url):
        if url.endswith("/status"):
            self.status_calls.append(url)
            return self._next(self.statuses, "status")
        self.result_calls.append(url)
        return self._next(self.results, "result")

    def download(self, url, destination):
        self.download_calls.append(url)
        outcome = self._next(self.downloads, "download")
        Path(destination).write_bytes(outcome)

    def check_url(self, url):
        self.ref_checks.append(url)
        if self.ref_outcomes:
            self._next(self.ref_outcomes, "reference check")

    def upload_asset(self, args, file_path):
        self.upload_calls.append((tuple(args), file_path))
        return self._next(self.uploads, "upload")

def submit_response(request_id="req-1"):
    base = f"https://queue.test/requests/{request_id}"
    return {
        "request_id": request_id,
        "status": "IN_QUEUE",
        "status_url": f"{base}/status",
        "response_url": f"{base}/response",
        "cancel_url": f"{base}/cancel",
    }


class FalRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write_job(
        self,
        *,
        route="nb2.edit",
        prompt="A valid portrait prompt",
        refs=True,
        artifact_kind="scene_start",
        supabase=None,
        schema_version=1,
    ):
        job_input = {"prompt": prompt}
        if refs:
            job_input["image_urls"] = ["https://assets.example.test/character.png"]
        job = {
            "schema_version": schema_version,
            "job_id": "scene-1-start",
            "route": route,
            "artifact_kind": artifact_kind,
            "output_dir": str(self.root),
            "output_path": "scenes/scene-1/scene-1.png",
            "input": job_input,
        }
        if supabase is not None:
            job["supabase"] = supabase
        path = self.root / "job.json"
        path.write_text(json.dumps(job), encoding="utf-8")
        return path

    def prepare(self, job_path):
        return fr.validate_and_prepare_job(job_path)

    def runner(self, job_path, transport, *, allow_paid_retry=False):
        return fr.FalRunner(
            self.prepare(job_path),
            transport,
            poll_interval_seconds=0,
            poll_timeout_seconds=30,
            sleeper=lambda _seconds: None,
            allow_paid_retry=allow_paid_retry,
        )

    def successful_transport(self):
        return FakeTransport(
            submits=[submit_response()],
            statuses=[{"status": "IN_QUEUE"}, {"status": "COMPLETED"}],
            results=[{"images": [{"url": "https://media.example.test/result.png"}]}],
        )

    def test_preflight_is_read_only(self):
        path = self.write_job()
        prepared = self.prepare(path)
        summary = fr.preflight_summary(prepared)

        self.assertTrue(summary["ok"])
        self.assertEqual(summary["route"], "nb2.edit")
        self.assertFalse(prepared["state_dir"].exists())

    def test_contract_hash_binds_supabase_destination(self):
        path = self.write_job(
            supabase={
                "game": "star-trek-timelines",
                "episode": "2026-07-16-wild-documentary-run-a",
                "name": "scene-1.png",
            },
        )
        original = fr.validate_and_prepare_job(path)
        job = json.loads(path.read_text())
        job["supabase"]["episode"] = "2026-07-16-wild-documentary-run-b"
        path.write_text(json.dumps(job), encoding="utf-8")
        changed = fr.validate_and_prepare_job(path)

        self.assertEqual(original["payload_sha256"], changed["payload_sha256"])
        self.assertNotEqual(original["contract_sha256"], changed["contract_sha256"])

    def test_claim_rejects_changed_supabase_destination(self):
        path = self.write_job(
            supabase={
                "game": "star-trek-timelines",
                "episode": "2026-07-16-wild-documentary-run-a",
                "name": "scene-1.png",
            },
        )
        interrupted = FakeTransport(
            submits=[submit_response()],
            statuses=[fr.TransportError("lost"), fr.TransportError("still lost")],
        )
        with self.assertRaises(fr.RemoteGenerationError):
            self.runner(path, interrupted).run()

        job = json.loads(path.read_text())
        job["supabase"]["name"] = "other.png"
        path.write_text(json.dumps(job), encoding="utf-8")
        untouched = FakeTransport()
        with self.assertRaisesRegex(fr.StateError, "claimed"):
            self.runner(path, untouched).run()
        self.assertEqual(len(untouched.submit_calls), 0)

    def test_text_route_rejects_image_urls(self):
        path = self.write_job(route="nb2.text", refs=True)
        with self.assertRaisesRegex(fr.JobValidationError, "must omit image_urls"):
            fr.validate_and_prepare_job(path)

    def test_edit_route_requires_refs(self):
        path = self.write_job(route="nb2.edit", refs=False)
        with self.assertRaisesRegex(fr.JobValidationError, "requires 1..4"):
            fr.validate_and_prepare_job(path)

    def test_edit_route_accepts_four_refs_but_not_five(self):
        path = self.write_job()
        job = json.loads(path.read_text())
        job["input"]["image_urls"] = [f"https://assets.example.test/{n}.png" for n in range(4)]
        path.write_text(json.dumps(job))
        self.assertEqual(len(self.prepare(path)["payload"]["image_urls"]), 4)

        job["input"]["image_urls"].append("https://assets.example.test/4.png")
        path.write_text(json.dumps(job))
        with self.assertRaisesRegex(fr.JobValidationError, "requires 1..4"):
            self.prepare(path)

    def test_duplicate_refs_are_rejected(self):
        path = self.write_job()
        job = json.loads(path.read_text())
        job["input"]["image_urls"] *= 2
        path.write_text(json.dumps(job))
        with self.assertRaisesRegex(fr.JobValidationError, "duplicates"):
            self.prepare(path)

    def test_unknown_top_level_field_is_rejected(self):
        path = self.write_job()
        job = json.loads(path.read_text())
        job["fallback_route"] = "gpt-image"
        path.write_text(json.dumps(job))
        with self.assertRaisesRegex(fr.JobValidationError, "unsupported job fields"):
            self.prepare(path)

    def test_end_frame_artifact_kind_is_rejected(self):
        path = self.write_job()
        job = json.loads(path.read_text())
        job["artifact_kind"] = "end_frame"
        path.write_text(json.dumps(job))
        with self.assertRaisesRegex(fr.JobValidationError, "artifact_kind"):
            self.prepare(path)

    def test_happy_path_writes_validated_output(self):
        path = self.write_job()
        transport = self.successful_transport()

        result = self.runner(path, transport).run()

        self.assertEqual(result["phase"], "DONE")
        self.assertEqual(result["generation_attempts"], 1)
        self.assertEqual(len(transport.submit_calls), 1)
        self.assertEqual(len(transport.download_calls), 1)
        self.assertTrue(Path(result["output_path"]).exists())
        state = json.loads(Path(result["state_path"]).read_text())
        self.assertEqual(state["phase"], "DONE")
        self.assertEqual(state["validation"]["width"], 768)
        self.assertFalse(Path(result["output_path"] + ".part").exists())

    def test_resume_polls_request_id_without_second_submit(self):
        path = self.write_job()
        interrupted = FakeTransport(
            submits=[submit_response()],
            statuses=[
                fr.TransportError("temporary status failure"),
                fr.TransportError("temporary status failure"),
            ],
        )
        with self.assertRaisesRegex(fr.RemoteGenerationError, "resume"):
            self.runner(path, interrupted).run()

        resumed = FakeTransport(
            statuses=[{"status": "COMPLETED"}],
            results=[{"images": [{"url": "https://media.example.test/result.png"}]}],
        )
        result = self.runner(path, resumed).run()

        self.assertEqual(result["phase"], "DONE")
        self.assertEqual(len(interrupted.submit_calls), 1)
        self.assertEqual(len(resumed.submit_calls), 0)

    def test_provider_tracking_urls_cannot_override_pinned_route(self):
        path = self.write_job()
        response = submit_response()
        response["status_url"] = "https://evil.example/status"
        response["response_url"] = "https://evil.example/result"
        transport = FakeTransport(
            submits=[response],
            statuses=[{"status": "COMPLETED", "response_url": "https://evil.example/result-2"}],
            results=[{"images": [{"url": "https://media.example.test/result.png"}]}],
        )

        self.runner(path, transport).run()

        pinned = "https://queue.fal.run/fal-ai/nano-banana-2/requests/req-1"
        self.assertEqual(transport.status_calls, [pinned + "/status"])
        self.assertEqual(transport.result_calls, [pinned])

    def test_remote_failure_requires_explicit_paid_retry(self):
        path = self.write_job()
        transport = FakeTransport(
            submits=[submit_response("req-1"), submit_response("must-not-run")],
            statuses=[{"status": "FAILED", "error": "provider failure"}],
        )

        with self.assertRaisesRegex(fr.RemoteGenerationError, "allow-paid-retry"):
            self.runner(path, transport).run()

        self.assertEqual(len(transport.submit_calls), 1)
        state = json.loads((self.root / "build/fal/scene-1-start/state.json").read_text())
        self.assertEqual(state["phase"], "PAID_RETRY_REQUIRED")

    def test_explicit_paid_retry_reuses_identical_payload_once(self):
        path = self.write_job()
        transport = FakeTransport(
            submits=[submit_response("req-1"), submit_response("req-2")],
            statuses=[
                {"status": "FAILED", "error": "provider failure"},
                {"status": "COMPLETED"},
            ],
            results=[{"images": [{"url": "https://media.example.test/result.png"}]}],
        )

        result = self.runner(path, transport, allow_paid_retry=True).run()

        self.assertEqual(result["generation_attempts"], 2)
        self.assertEqual(len(transport.submit_calls), 2)
        self.assertEqual(transport.submit_calls[0][0], transport.submit_calls[1][0])
        self.assertEqual(transport.submit_calls[0][1], transport.submit_calls[1][1])

    def test_second_remote_failure_is_terminal(self):
        path = self.write_job()
        transport = FakeTransport(
            submits=[submit_response("req-1"), submit_response("req-2")],
            statuses=[{"status": "FAILED"}, {"status": "FAILED"}],
        )

        with self.assertRaisesRegex(fr.RemoteGenerationError, "failed twice"):
            self.runner(path, transport, allow_paid_retry=True).run()

        self.assertEqual(len(transport.submit_calls), 2)
        state_path = self.root / "build/fal/scene-1-start/state.json"
        state = json.loads(state_path.read_text())
        self.assertEqual(state["phase"], "FAILED")

    def test_download_retries_without_regenerating(self):
        path = self.write_job()
        transport = FakeTransport(
            submits=[submit_response()],
            statuses=[{"status": "COMPLETED"}],
            results=[{"images": [{"url": "https://media.example.test/result.png"}]}],
            downloads=[fr.DownloadError("temporary download failure"), valid_portrait_png()],
        )

        result = self.runner(path, transport).run()

        self.assertEqual(result["phase"], "DONE")
        self.assertEqual(len(transport.submit_calls), 1)
        self.assertEqual(len(transport.download_calls), 2)

    def test_unsupported_portrait_ratio_fails_without_regeneration(self):
        path = self.write_job()
        bad_png = valid_portrait_png(width=800, height=1280)
        transport = FakeTransport(
            submits=[submit_response()],
            statuses=[{"status": "COMPLETED"}],
            results=[{"images": [{"url": "https://media.example.test/result.png"}]}],
            downloads=[bad_png, bad_png],
        )

        with self.assertRaisesRegex(fr.DownloadError, "failed twice"):
            self.runner(path, transport).run()
        self.assertEqual(len(transport.submit_calls), 1)
        self.assertEqual(len(transport.download_calls), 2)

    def test_png_with_incomplete_pixels_fails_without_regeneration(self):
        path = self.write_job()
        bad_png = truncated_pixel_png()
        transport = FakeTransport(
            submits=[submit_response()],
            statuses=[{"status": "COMPLETED"}],
            results=[{"images": [{"url": "https://media.example.test/result.png"}]}],
            downloads=[bad_png, bad_png],
        )

        with self.assertRaisesRegex(fr.DownloadError, "failed twice"):
            self.runner(path, transport).run()
        self.assertEqual(len(transport.submit_calls), 1)

    def test_documented_two_by_three_fallback_is_accepted(self):
        path = self.root / "fallback.png"
        path.write_bytes(valid_portrait_png(width=1024, height=1536))
        self.assertEqual(fr.validate_png(path)["height"], 1536)

    def test_dead_reference_stops_before_paid_submit(self):
        path = self.write_job()
        transport = FakeTransport(
            ref_outcomes=[fr.HttpResponseError(404, "missing")],
            submits=[submit_response("must-not-run")],
        )

        with self.assertRaisesRegex(fr.RemoteGenerationError, "reference URL"):
            self.runner(path, transport).run()
        self.assertEqual(len(transport.submit_calls), 0)
        state = json.loads((self.root / "build/fal/scene-1-start/state.json").read_text())
        self.assertEqual(state["phase"], "INPUT_REJECTED")

    def test_poll_404_is_terminal_and_never_resubmits(self):
        path = self.write_job()
        transport = FakeTransport(
            submits=[submit_response()],
            statuses=[fr.HttpResponseError(404, "lost request")],
        )
        with self.assertRaisesRegex(fr.RemoteGenerationError, "terminal HTTP 404"):
            self.runner(path, transport).run()

        no_network = FakeTransport(submits=[submit_response("must-not-run")])
        with self.assertRaisesRegex(fr.RemoteGenerationError, "terminal"):
            self.runner(path, no_network).run()
        self.assertEqual(len(no_network.submit_calls), 0)

    def test_retryable_submit_http_error_retries_once(self):
        path = self.write_job()
        transport = FakeTransport(
            submits=[fr.HttpResponseError(429, "rate limited"), submit_response("req-2")],
            statuses=[{"status": "COMPLETED"}],
            results=[{"images": [{"url": "https://media.example.test/result.png"}]}],
        )

        result = self.runner(path, transport).run()

        self.assertEqual(result["generation_attempts"], 2)
        self.assertEqual(len(transport.submit_calls), 2)

    def test_server_error_after_submit_is_ambiguous_and_never_retried(self):
        path = self.write_job()
        first = FakeTransport(
            submits=[fr.HttpResponseError(503, "gateway lost the response")]
        )
        with self.assertRaises(fr.AmbiguousSubmitError):
            self.runner(path, first).run()
        self.assertEqual(len(first.submit_calls), 1)

        second = FakeTransport(submits=[submit_response("must-not-run")])
        with self.assertRaises(fr.AmbiguousSubmitError):
            self.runner(path, second).run()
        self.assertEqual(len(second.submit_calls), 0)

    def test_payload_change_is_rejected_before_network(self):
        path = self.write_job(prompt="Original prompt")
        interrupted = FakeTransport(
            submits=[submit_response()],
            statuses=[
                fr.TransportError("temporary status failure"),
                fr.TransportError("temporary status failure"),
            ],
        )
        with self.assertRaises(fr.RemoteGenerationError):
            self.runner(path, interrupted).run()

        job = json.loads(path.read_text())
        job["input"]["prompt"] = "Changed prompt"
        path.write_text(json.dumps(job), encoding="utf-8")
        untouched = FakeTransport()

        with self.assertRaisesRegex(fr.StateError, "claimed"):
            self.runner(path, untouched).run()
        self.assertEqual(len(untouched.submit_calls), 0)

    def test_ambiguous_submit_never_resubmits_on_resume(self):
        path = self.write_job()
        ambiguous = FakeTransport(submits=[fr.TransportError("connection lost after POST")])
        with self.assertRaises(fr.AmbiguousSubmitError):
            self.runner(path, ambiguous).run()

        second_transport = FakeTransport(submits=[submit_response("must-not-run")])
        with self.assertRaises(fr.AmbiguousSubmitError):
            self.runner(path, second_transport).run()
        self.assertEqual(len(second_transport.submit_calls), 0)

    def test_output_path_claim_blocks_a_second_job_id_before_submit(self):
        path = self.write_job()
        first = FakeTransport(
            submits=[submit_response()],
            statuses=[fr.TransportError("lost"), fr.TransportError("still lost")],
        )
        with self.assertRaises(fr.RemoteGenerationError):
            self.runner(path, first).run()

        job = json.loads(path.read_text())
        job["job_id"] = "different-job"
        path.write_text(json.dumps(job))
        second = FakeTransport(submits=[submit_response("must-not-run")])
        with self.assertRaisesRegex(fr.StateError, "already claimed"):
            self.runner(path, second).run()
        self.assertEqual(len(second.submit_calls), 0)

    def test_missing_result_url_can_be_refetched_without_resubmit(self):
        path = self.write_job()
        first = FakeTransport(
            submits=[submit_response()],
            statuses=[{"status": "COMPLETED"}],
            results=[{"images": []}],
        )
        with self.assertRaisesRegex(fr.RemoteGenerationError, "no valid image URL"):
            self.runner(path, first).run()

        resumed = FakeTransport(
            results=[{"images": [{"url": "https://media.example.test/result.png"}]}]
        )
        result = self.runner(path, resumed).run()
        self.assertEqual(result["phase"], "DONE")
        self.assertEqual(len(resumed.submit_calls), 0)

    def test_expired_link_refetches_result_without_resubmit(self):
        path = self.write_job()
        transport = FakeTransport(
            submits=[submit_response()],
            statuses=[{"status": "COMPLETED"}],
            results=[
                {"images": [{"url": "https://media.example.test/expired.png"}]},
                {"images": [{"url": "https://media.example.test/fresh.png"}]},
            ],
            downloads=[fr.DownloadHttpError(404, "link expired"), valid_portrait_png()],
        )

        result = self.runner(path, transport).run()

        self.assertEqual(result["phase"], "DONE")
        self.assertEqual(len(transport.submit_calls), 1)
        self.assertEqual(len(transport.result_calls), 2)
        self.assertEqual(
            transport.download_calls,
            [
                "https://media.example.test/expired.png",
                "https://media.example.test/fresh.png",
            ],
        )

    def test_expired_link_retries_are_still_capped(self):
        path = self.write_job()
        transport = FakeTransport(
            submits=[submit_response()],
            statuses=[{"status": "COMPLETED"}],
            results=[
                {"images": [{"url": "https://media.example.test/expired-1.png"}]},
                {"images": [{"url": "https://media.example.test/expired-2.png"}]},
            ],
            downloads=[fr.DownloadHttpError(404, "gone"), fr.DownloadHttpError(404, "gone again")],
        )

        with self.assertRaisesRegex(fr.DownloadError, "failed twice"):
            self.runner(path, transport).run()

        self.assertEqual(len(transport.submit_calls), 1)
        self.assertEqual(len(transport.download_calls), 2)

    def test_download_failure_preserves_real_error_message(self):
        path = self.write_job()
        transport = FakeTransport(
            submits=[submit_response()],
            statuses=[{"status": "COMPLETED"}],
            results=[{"images": [{"url": "https://media.example.test/result.png"}]}],
            downloads=[
                fr.DownloadError("connection reset by peer"),
                fr.DownloadError("connection reset by peer"),
            ],
        )

        with self.assertRaisesRegex(fr.DownloadError, "connection reset by peer"):
            self.runner(path, transport).run()

        state = json.loads((self.root / "build/fal/scene-1-start/state.json").read_text())
        self.assertEqual(state["error"]["last_error"], "connection reset by peer")

    def test_interrupted_download_attempt_is_not_counted_against_the_cap(self):
        path = self.write_job()
        transport = FakeTransport(
            submits=[submit_response()],
            statuses=[{"status": "COMPLETED"}],
            results=[{"images": [{"url": "https://media.example.test/result.png"}]}],
            downloads=[fr.TransportError("process killed mid-download"), valid_portrait_png()],
        )

        with self.assertRaises(fr.RunnerError):
            self.runner(path, transport).run()

        state_path = self.root / "build/fal/scene-1-start/state.json"
        state = json.loads(state_path.read_text())
        self.assertEqual(state["phase"], "DOWNLOADING")
        self.assertEqual(state["downloads"], 0)

        resumed = FakeTransport(downloads=[valid_portrait_png()])
        resumed.results = []
        result = self.runner(path, resumed).run()

        self.assertEqual(result["phase"], "DONE")
        self.assertEqual(len(resumed.submit_calls), 0)
        self.assertEqual(len(resumed.download_calls), 1)

    def test_scene_start_missing_supabase_fields_is_rejected(self):
        path = self.write_job(supabase={"game": "star-trek-timelines"})
        with self.assertRaisesRegex(fr.JobValidationError, "supabase.episode"):
            fr.validate_and_prepare_job(path)

    def test_character_reference_requires_slug_not_episode(self):
        path = self.write_job(
            artifact_kind="character_reference",
            supabase={"game": "star-trek-timelines", "episode": "should-not-be-here"},
        )
        with self.assertRaisesRegex(fr.JobValidationError, "supabase.slug"):
            fr.validate_and_prepare_job(path)

    def test_supabase_upload_args_are_derived_from_artifact_kind(self):
        path = self.write_job(
            artifact_kind="character_reference",
            supabase={"game": "star-trek-timelines", "slug": "mirror-kirk", "tags": "serial-drama"},
        )
        prepared = self.prepare(path)
        self.assertEqual(
            prepared["upload_args"],
            ["--kind", "character", "--game", "star-trek-timelines", "--slug", "mirror-kirk", "--tags", "serial-drama"],
        )

    def test_upload_runs_after_validation_and_url_is_saved(self):
        path = self.write_job(
            supabase={
                "game": "star-trek-timelines",
                "episode": "2026-07-14-serial-drama",
                "name": "scene-1.png",
            }
        )
        transport = self.successful_transport()
        transport.uploads = ["https://supabase.example.test/episodes/scene-1.png"]

        result = self.runner(path, transport).run()

        self.assertEqual(result["phase"], "DONE")
        self.assertEqual(result["supabase_url"], "https://supabase.example.test/episodes/scene-1.png")
        self.assertEqual(len(transport.upload_calls), 1)
        expected_args = (
            "--kind", "episode-scene", "--game", "star-trek-timelines",
            "--episode", "2026-07-14-serial-drama", "--name", "scene-1.png",
        )
        self.assertEqual(transport.upload_calls[0][0], expected_args)

    def test_completed_upload_is_not_repeated_on_resume(self):
        path = self.write_job(
            supabase={
                "game": "star-trek-timelines",
                "episode": "2026-07-14-serial-drama",
                "name": "scene-1.png",
            }
        )
        first = self.successful_transport()
        first.uploads = ["https://supabase.example.test/episodes/scene-1.png"]
        self.runner(path, first).run()

        no_network = FakeTransport()
        result = self.runner(path, no_network).run()

        self.assertTrue(result["skipped"])
        self.assertEqual(len(no_network.upload_calls), 0)

    def test_upload_failure_is_resumable_without_redownload(self):
        path = self.write_job(
            supabase={
                "game": "star-trek-timelines",
                "episode": "2026-07-14-serial-drama",
                "name": "scene-1.png",
            }
        )
        failing = self.successful_transport()
        failing.uploads = [fr.UploadError("supabase 503")]

        with self.assertRaisesRegex(fr.UploadError, "supabase 503"):
            self.runner(path, failing).run()

        state = json.loads((self.root / "build/fal/scene-1-start/state.json").read_text())
        self.assertEqual(state["phase"], "VALIDATED")
        self.assertTrue(Path(state["output_path"]).exists())

        retried = FakeTransport(uploads=["https://supabase.example.test/episodes/scene-1.png"])
        result = self.runner(path, retried).run()

        self.assertEqual(result["phase"], "DONE")
        self.assertEqual(len(retried.submit_calls), 0)
        self.assertEqual(len(retried.download_calls), 0)
        self.assertEqual(len(retried.upload_calls), 1)

    def test_upload_helper_warning_is_a_runner_failure(self):
        transport = fr.CurlTransport("test-key")
        completed = subprocess_result = mock.Mock(
            returncode=0,
            stdout="https://supabase.example.test/assets/ref.png\n",
            stderr="WARN: insert returned 500",
        )
        local = self.root / "local.png"
        local.write_bytes(VALID_PNG)
        with mock.patch.object(fr.subprocess, "run", return_value=completed):
            with self.assertRaisesRegex(fr.UploadError, "reported a warning"):
                transport.upload_asset(["--kind", "character"], local)
        self.assertEqual(subprocess_result.returncode, 0)

    def test_upload_verifies_public_file_after_helper_success(self):
        transport = fr.CurlTransport("test-key")
        completed = mock.Mock(
            returncode=0,
            stdout="https://supabase.example.test/assets/ref.png\n",
            stderr="",
        )
        local = self.root / "local.png"
        local.write_bytes(VALID_PNG)
        with mock.patch.object(fr.subprocess, "run", return_value=completed), mock.patch.object(
            transport, "verify_public_asset"
        ) as verify:
            url = transport.upload_asset(["--kind", "character"], local)
        self.assertEqual(url, "https://supabase.example.test/assets/ref.png")
        verify.assert_called_once_with(url, local)

    def test_completed_job_is_idempotent(self):
        path = self.write_job()
        first = self.successful_transport()
        self.runner(path, first).run()
        no_network = FakeTransport()

        result = self.runner(path, no_network).run()

        self.assertTrue(result["skipped"])
        self.assertEqual(len(no_network.submit_calls), 0)
        self.assertEqual(len(no_network.status_calls), 0)
        self.assertEqual(len(no_network.download_calls), 0)


if __name__ == "__main__":
    unittest.main()
