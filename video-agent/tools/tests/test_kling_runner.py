import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))

import fal_runner as fr  # noqa: E402
import kling_runner as kr  # noqa: E402


class FakeTransport:
    def __init__(
        self,
        *,
        video_bytes,
        submits=None,
        statuses=None,
        results=None,
        downloads=None,
        ref_outcomes=None,
        uploads=None,
    ):
        self.video_bytes = video_bytes
        self.submits = list(submits or [])
        self.statuses = list(statuses or [])
        self.results = list(results or [])
        self.downloads = list(downloads if downloads is not None else [video_bytes])
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
        if isinstance(outcome, bytes):
            Path(destination).write_bytes(outcome)

    def check_url(self, url):
        self.ref_checks.append(url)
        if self.ref_outcomes:
            self._next(self.ref_outcomes, "reference check")

    def upload_asset(self, args, file_path):
        self.upload_calls.append((tuple(args), Path(file_path)))
        return self._next(self.uploads, "upload")


def submit_response(request_id="req-1"):
    return {"request_id": request_id, "status": "IN_QUEUE"}


class KlingRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            raise unittest.SkipTest("ffmpeg and ffprobe are required")
        cls.fixture_temp = tempfile.TemporaryDirectory()
        fixture = Path(cls.fixture_temp.name) / "valid.mp4"
        process = subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-f",
                "lavfi",
                "-i",
                "testsrc2=size=600x1066:rate=8",
                "-f",
                "lavfi",
                "-i",
                "sine=frequency=440:sample_rate=44100",
                "-t",
                "5",
                "-c:v",
                "libx264",
                "-preset",
                "ultrafast",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-shortest",
                str(fixture),
            ],
            capture_output=True,
            text=True,
        )
        if process.returncode:
            raise RuntimeError(process.stderr)
        cls.valid_video = fixture.read_bytes()
        no_audio = Path(cls.fixture_temp.name) / "no-audio.mp4"
        subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(fixture), "-c", "copy", "-an", str(no_audio)],
            check=True,
        )
        cls.no_audio_video = no_audio.read_bytes()

    @classmethod
    def tearDownClass(cls):
        cls.fixture_temp.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    @staticmethod
    def default_expect(audio="required"):
        return {
            "kind": "video",
            "duration_seconds": 5,
            "duration_tolerance_seconds": 0.1,
            "audio": audio,
            "min_bytes": 100_000,
            "min_width": 600,
            "min_height": 1000,
            "orientation": "portrait",
        }

    def write_job(self, *, payload=None, expect=None, route="kling.v3.standard.i2v"):
        job = {
            "schema_version": kr.SCHEMA_VERSION,
            "job_id": "scene-1-video",
            "route": route,
            "artifact_kind": kr.ARTIFACT_KIND,
            "output_dir": str(self.root),
            "output_path": "scenes/scene-1/scene-1.mp4",
            "payload": payload
            or {
                "prompt": "A concise wildlife motion prompt",
                "start_image_url": "https://assets.example.test/scene-1.png",
                "duration": "5",
                "generate_audio": True,
                "negative_prompt": "blur, distortion, morphing",
            },
            "expect": expect or self.default_expect(),
            "supabase": {
                "game": "star-trek-timelines",
                "episode": "2026-07-16-video-runner-test",
                "name": "scene-1.mp4",
            },
        }
        path = self.root / "job.json"
        path.write_text(json.dumps(job), encoding="utf-8")
        return path

    def runner(self, job_path, transport, *, routes_path=kr.ROUTES_PATH, allow_paid_retry=False):
        return kr.KlingRunner(
            kr.validate_and_prepare_job(job_path, routes_path=routes_path),
            transport,
            poll_interval_seconds=0,
            poll_timeout_seconds=30,
            sleeper=lambda _seconds: None,
            allow_paid_retry=allow_paid_retry,
        )

    def transport(self, **kwargs):
        return FakeTransport(video_bytes=self.valid_video, **kwargs)

    def successful_transport(self, result=None):
        return self.transport(
            submits=[submit_response()],
            statuses=[{"status": "IN_QUEUE"}, {"status": "COMPLETED"}],
            results=[result or {"video": {"url": "https://media.example.test/result.mp4"}}],
            uploads=["https://supabase.example.test/episodes/scene-1.mp4"],
        )

    def write_routes(self, mutate=None):
        routes = json.loads(kr.ROUTES_PATH.read_text())
        if mutate:
            mutate(routes)
        path = self.root / "routes.json"
        path.write_text(json.dumps(routes), encoding="utf-8")
        return path

    def test_preflight_is_read_only(self):
        prepared = kr.validate_and_prepare_job(self.write_job())
        summary = kr.preflight_summary(prepared)

        self.assertTrue(summary["ok"])
        self.assertEqual(summary["route"], "kling.v3.standard.i2v")
        self.assertEqual(summary["expect"]["audio"], "required")
        self.assertFalse(prepared["state_dir"].exists())

    def test_runner_preserves_orchestrator_payload_without_format_semantics(self):
        payload = {
            "multi_prompt": [
                {"prompt": "Officer speaks. <<<voice_1>>> First line.", "duration": "3"},
                {"prompt": "Second officer answers. <<<voice_2>>> Second line.", "duration": "3"},
            ],
            "voice_ids": [
                "https://assets.example.test/voice-a.mp3",
                "https://assets.example.test/voice-b.mp3",
            ],
            "elements": [{"future_provider_shape": {"nested": [1, 2, 3]}}],
            "shot_type": "customize",
            "start_image_url": "https://assets.example.test/scene.png",
            "duration": "6",
            "generate_audio": True,
            "future_provider_option": {"mode": "new", "strength": 0.73},
        }
        prepared = kr.validate_and_prepare_job(
            self.write_job(payload=payload, expect={**self.default_expect(), "duration_seconds": 6})
        )
        self.assertEqual(prepared["payload"], payload)
        self.assertEqual(prepared["payload_bytes"], fr.canonical_bytes(payload))

    def test_format_fields_are_not_part_of_execution_contract(self):
        path = self.write_job()
        job = json.loads(path.read_text())
        job["format"] = "wild-documentary"
        job["format_mode"] = "single-prompt"
        path.write_text(json.dumps(job), encoding="utf-8")
        with self.assertRaisesRegex(fr.JobValidationError, "unsupported job fields"):
            kr.validate_and_prepare_job(path)

    def test_nested_temporary_input_url_is_rejected(self):
        payload = {
            "arbitrary": {
                "refs": [
                    {"url": "https://v3b.fal.media/files/temporary.png"},
                ]
            }
        }
        with self.assertRaisesRegex(fr.JobValidationError, "temporary fal URLs"):
            kr.validate_and_prepare_job(self.write_job(payload=payload))

    def test_all_payload_urls_are_checked_before_submit(self):
        payload = {
            "start_image_url": "https://assets.example.test/start.png",
            "voice_ids": ["https://assets.example.test/voice.mp3"],
            "elements": [
                {
                    "frontal_image_url": "https://assets.example.test/front.png",
                    "reference_image_urls": ["https://assets.example.test/side.png"],
                }
            ],
        }
        transport = self.successful_transport()
        self.runner(self.write_job(payload=payload), transport).run()
        self.assertEqual(
            transport.ref_checks,
            [
                "https://assets.example.test/start.png",
                "https://assets.example.test/voice.mp3",
                "https://assets.example.test/front.png",
                "https://assets.example.test/side.png",
            ],
        )

    def test_dead_input_stops_before_paid_submit(self):
        transport = self.transport(ref_outcomes=[fr.HttpResponseError(404, "missing")])
        with self.assertRaisesRegex(fr.RemoteGenerationError, "input URL rejected"):
            self.runner(self.write_job(), transport).run()
        self.assertEqual(len(transport.submit_calls), 0)

    def test_new_fal_queue_route_is_registry_only(self):
        def add_route(routes):
            routes["routes"]["future.video.route"] = {
                "protocol": "fal_queue",
                "submit_url": "https://queue.fal.run/future/video/generate",
                "poll_base": "https://queue.fal.run/future/video",
                "result_url_path": ["output", "file", "url"],
            }

        routes_path = self.write_routes(add_route)
        prepared = kr.validate_and_prepare_job(
            self.write_job(route="future.video.route"), routes_path=routes_path
        )
        self.assertEqual(prepared["submit_url"], "https://queue.fal.run/future/video/generate")
        self.assertEqual(prepared["result_url_path"], ["output", "file", "url"])

    def test_configured_result_path_is_used_without_runner_change(self):
        def add_route(routes):
            routes["routes"]["future.video.route"] = {
                "protocol": "fal_queue",
                "submit_url": "https://queue.fal.run/future/video/generate",
                "poll_base": "https://queue.fal.run/future/video",
                "result_url_path": ["output", "file", "url"],
            }

        routes_path = self.write_routes(add_route)
        transport = self.successful_transport(
            {"output": {"file": {"url": "https://media.example.test/future.mp4"}}}
        )
        result = self.runner(
            self.write_job(route="future.video.route"), transport, routes_path=routes_path
        ).run()
        self.assertEqual(result["phase"], "DONE")
        self.assertEqual(transport.download_calls, ["https://media.example.test/future.mp4"])

    def test_route_descriptor_is_bound_to_contract(self):
        routes_path = self.write_routes()
        path = self.write_job()
        original = kr.validate_and_prepare_job(path, routes_path=routes_path)
        routes = json.loads(routes_path.read_text())
        routes["routes"]["kling.v3.standard.i2v"]["poll_base"] = (
            "https://queue.fal.run/changed/base"
        )
        routes_path.write_text(json.dumps(routes), encoding="utf-8")
        changed = kr.validate_and_prepare_job(path, routes_path=routes_path)
        self.assertEqual(original["payload_sha256"], changed["payload_sha256"])
        self.assertNotEqual(original["route_sha256"], changed["route_sha256"])
        self.assertNotEqual(original["contract_sha256"], changed["contract_sha256"])

    def test_legacy_format_aware_schema_is_rejected(self):
        path = self.write_job()
        job = json.loads(path.read_text())
        job["schema_version"] = 2
        path.write_text(json.dumps(job), encoding="utf-8")
        with self.assertRaisesRegex(fr.JobValidationError, "generic video execution contract"):
            kr.validate_and_prepare_job(path)

    def test_audio_expectation_is_owned_by_job(self):
        silent = self.root / "silent.mp4"
        silent.write_bytes(self.no_audio_video)
        required = self.default_expect("required")
        forbidden = self.default_expect("forbidden")
        optional = self.default_expect("optional")

        with self.assertRaisesRegex(fr.DownloadError, "required native audio"):
            kr.validate_mp4(silent, required)
        self.assertIsNone(kr.validate_mp4(silent, forbidden)["audio_codec"])
        self.assertIsNone(kr.validate_mp4(silent, optional)["audio_codec"])

        with_audio = self.root / "audio.mp4"
        with_audio.write_bytes(self.valid_video)
        with self.assertRaisesRegex(fr.DownloadError, "audio stream.*forbidden"):
            kr.validate_mp4(with_audio, forbidden)
        self.assertEqual(kr.validate_mp4(with_audio, required)["audio_codec"], "aac")

    def test_happy_path_validates_and_uploads(self):
        path = self.write_job()
        transport = self.successful_transport()
        result = self.runner(path, transport).run()

        self.assertEqual(result["phase"], "DONE")
        self.assertEqual(result["generation_attempts"], 1)
        self.assertEqual(result["validation"]["video_codec"], "h264")
        self.assertEqual(result["validation"]["audio_codec"], "aac")
        self.assertEqual(transport.submit_calls[0][1], fr.canonical_bytes(json.loads(path.read_text())["payload"]))
        self.assertEqual(len(transport.upload_calls), 1)

    def test_resume_polls_saved_request_without_second_submit(self):
        path = self.write_job()
        interrupted = self.transport(
            submits=[submit_response()],
            statuses=[fr.TransportError("lost"), fr.TransportError("still lost")],
        )
        with self.assertRaisesRegex(fr.RemoteGenerationError, "resume"):
            self.runner(path, interrupted).run()

        resumed = self.transport(
            statuses=[{"status": "COMPLETED"}],
            results=[{"video": {"url": "https://media.example.test/result.mp4"}}],
            uploads=["https://supabase.example.test/episodes/scene-1.mp4"],
        )
        result = self.runner(path, resumed).run()
        self.assertEqual(result["phase"], "DONE")
        self.assertEqual(len(interrupted.submit_calls), 1)
        self.assertEqual(len(resumed.submit_calls), 0)

    def test_remote_failure_requires_explicit_same_payload_retry(self):
        path = self.write_job()
        first = self.transport(
            submits=[submit_response("req-1")],
            statuses=[{"status": "FAILED", "error": "provider failure"}],
        )
        with self.assertRaisesRegex(fr.RemoteGenerationError, "allow-paid-retry"):
            self.runner(path, first).run()

        second = self.transport(
            submits=[submit_response("req-2")],
            statuses=[{"status": "COMPLETED"}],
            results=[{"video": {"url": "https://media.example.test/result.mp4"}}],
            uploads=["https://supabase.example.test/episodes/scene-1.mp4"],
        )
        result = self.runner(path, second, allow_paid_retry=True).run()
        self.assertEqual(result["generation_attempts"], 2)
        self.assertEqual(second.submit_calls[0][1], first.submit_calls[0][1])

    def test_ambiguous_submit_never_resubmits(self):
        path = self.write_job()
        first = self.transport(submits=[fr.TransportError("connection lost after POST")])
        with self.assertRaises(fr.AmbiguousSubmitError):
            self.runner(path, first).run()

        second = self.transport(submits=[submit_response("must-not-run")])
        with self.assertRaises(fr.AmbiguousSubmitError):
            self.runner(path, second).run()
        self.assertEqual(len(second.submit_calls), 0)

    def test_expired_download_url_is_refetched_without_resubmit(self):
        path = self.write_job()
        transport = self.transport(
            submits=[submit_response()],
            statuses=[{"status": "COMPLETED"}],
            results=[
                {"video": {"url": "https://media.example.test/expired.mp4"}},
                {"video": {"url": "https://media.example.test/fresh.mp4"}},
            ],
            downloads=[fr.DownloadHttpError(404, "expired"), self.valid_video],
            uploads=["https://supabase.example.test/episodes/scene-1.mp4"],
        )
        result = self.runner(path, transport).run()
        self.assertEqual(result["phase"], "DONE")
        self.assertEqual(len(transport.submit_calls), 1)
        self.assertEqual(len(transport.result_calls), 2)

    def test_upload_failure_resumes_without_generation_or_download(self):
        path = self.write_job()
        failing = self.successful_transport()
        failing.uploads = [fr.UploadError("supabase 503")]
        with self.assertRaisesRegex(fr.UploadError, "supabase 503"):
            self.runner(path, failing).run()

        resumed = self.transport(
            uploads=["https://supabase.example.test/episodes/scene-1.mp4"]
        )
        result = self.runner(path, resumed).run()
        self.assertEqual(result["phase"], "DONE")
        self.assertEqual(len(resumed.submit_calls), 0)
        self.assertEqual(len(resumed.download_calls), 0)

    def test_payload_change_after_claim_is_rejected_before_network(self):
        path = self.write_job()
        interrupted = self.transport(
            submits=[submit_response()],
            statuses=[fr.TransportError("lost"), fr.TransportError("still lost")],
        )
        with self.assertRaises(fr.RemoteGenerationError):
            self.runner(path, interrupted).run()

        job = json.loads(path.read_text())
        job["payload"]["generate_audio"] = False
        path.write_text(json.dumps(job), encoding="utf-8")
        untouched = self.transport()
        with self.assertRaisesRegex(fr.StateError, "claimed"):
            self.runner(path, untouched).run()
        self.assertEqual(len(untouched.submit_calls), 0)

    def test_changed_destination_after_claim_is_rejected_before_network(self):
        path = self.write_job()
        interrupted = self.transport(
            submits=[submit_response()],
            statuses=[fr.TransportError("lost"), fr.TransportError("still lost")],
        )
        with self.assertRaises(fr.RemoteGenerationError):
            self.runner(path, interrupted).run()

        job = json.loads(path.read_text())
        job["supabase"]["name"] = "other.mp4"
        path.write_text(json.dumps(job), encoding="utf-8")
        untouched = self.transport()
        with self.assertRaisesRegex(fr.StateError, "claimed"):
            self.runner(path, untouched).run()
        self.assertEqual(len(untouched.submit_calls), 0)

    def test_completed_job_is_idempotent(self):
        path = self.write_job()
        self.runner(path, self.successful_transport()).run()
        no_network = self.transport()
        result = self.runner(path, no_network).run()
        self.assertTrue(result["skipped"])
        self.assertEqual(len(no_network.submit_calls), 0)
        self.assertEqual(len(no_network.status_calls), 0)
        self.assertEqual(len(no_network.download_calls), 0)

    def test_tracked_examples_pass_preflight(self):
        for path in sorted((TOOLS_DIR / "examples").glob("kling-v3-*.job.json")):
            with self.subTest(example=path.name):
                prepared = kr.validate_and_prepare_job(path)
                self.assertEqual(prepared["artifact_kind"], kr.ARTIFACT_KIND)


if __name__ == "__main__":
    unittest.main()
