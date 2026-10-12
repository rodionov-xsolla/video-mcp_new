import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))

import still_shot as ss  # noqa: E402

HAS_FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


class ExpressionTests(unittest.TestCase):
    def test_frame_count_rounds_duration_times_fps(self):
        self.assertEqual(ss.frame_count(5, 24), 120)
        self.assertEqual(ss.frame_count(5.033, 30), 151)
        with self.assertRaises(ss.StillShotError):
            ss.frame_count(0.01, 24)

    def test_flat_effects_use_full_twelve_percent_move(self):
        ease = "(0.5-0.5*cos(PI*on/119))"
        self.assertEqual(
            ss.zoompan_expressions("push-in", "flat", 120),
            (f"1+0.12*{ease}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
        )
        self.assertEqual(ss.zoompan_expressions("pull-out", "flat", 120)[0], f"1.12-0.12*{ease}")
        self.assertEqual(
            ss.zoompan_expressions("pan-right", "flat", 120),
            ("1.12", f"(iw-iw/zoom)*{ease}", "ih/2-(ih/zoom/2)"),
        )
        self.assertEqual(ss.zoompan_expressions("pan-left", "flat", 120)[1], f"(iw-iw/zoom)*(1-{ease})")
        self.assertEqual(ss.zoompan_expressions("tilt-up", "flat", 120)[2], f"(ih-ih/zoom)*(1-{ease})")
        self.assertEqual(ss.zoompan_expressions("tilt-down", "flat", 120)[2], f"(ih-ih/zoom)*{ease}")

    def test_depth_uses_gentle_zoom_and_forbids_pans(self):
        ease = "(0.5-0.5*cos(PI*on/119))"
        self.assertEqual(ss.zoompan_expressions("push-in", "some", 120)[0], f"1+0.07*{ease}")
        self.assertEqual(ss.zoompan_expressions("pull-out", "deep", 120)[0], f"1.07-0.07*{ease}")
        for effect in ("pan-right", "pan-left", "tilt-up", "tilt-down"):
            with self.assertRaises(ss.StillShotError):
                ss.zoompan_expressions(effect, "deep", 120)

    def test_unknown_effect_or_depth_is_rejected(self):
        with self.assertRaises(ss.StillShotError):
            ss.zoompan_expressions("spin", "flat", 120)
        with self.assertRaises(ss.StillShotError):
            ss.zoompan_expressions("push-in", "medium", 120)

    def test_filter_renders_on_four_times_canvas(self):
        vf = ss.video_filter("push-in", "flat", 120, 1080, 1920, 24)
        self.assertIn("scale=4320:7680:force_original_aspect_ratio=increase:flags=lanczos,crop=4320:7680", vf)
        self.assertIn("d=120:s=1080x1920:fps=24", vf)


@unittest.skipUnless(HAS_FFMPEG, "ffmpeg and ffprobe are required")
class RenderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.image = self.tmp / "scene.png"
        subprocess.run(
            [shutil.which("ffmpeg"), "-v", "error", "-f", "lavfi", "-i", "testsrc2=s=192x344",
             "-frames:v", "1", str(self.image)],
            check=True,
        )

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_render_matches_requested_shape_without_audio(self):
        out = self.tmp / "scene.mp4"
        summary = ss.render(self.image, out, "pan-right", duration=1, fps=12, width=96, height=172)
        self.assertTrue(summary["ok"])
        self.assertEqual((summary["frames"], summary["width"], summary["height"]), (12, 96, 172))
        self.assertEqual(summary["audio"], "none")
        self.assertEqual(summary["cost_usd"], 0)

    def test_silent_audio_track_for_audio_formats(self):
        out = self.tmp / "scene.mp4"
        summary = ss.render(self.image, out, "pull-out", depth="some", duration=1, fps=12,
                            width=96, height=172, audio="silent")
        self.assertEqual(summary["audio"], "silent")
        self.assertEqual(summary["zoom"], 0.07)

    def test_existing_output_is_never_overwritten_without_force(self):
        out = self.tmp / "scene.mp4"
        out.write_bytes(b"paid clip")
        with self.assertRaises(ss.StillShotError):
            ss.render(self.image, out, "push-in", duration=1, fps=12, width=96, height=172)
        self.assertEqual(out.read_bytes(), b"paid clip")
        ss.render(self.image, out, "push-in", duration=1, fps=12, width=96, height=172, force=True)
        self.assertNotEqual(out.read_bytes(), b"paid clip")

    def test_failed_render_leaves_no_file_at_the_real_path(self):
        broken = self.tmp / "broken.png"
        broken.write_bytes(b"not an image")
        out = self.tmp / "scene.mp4"
        with self.assertRaises(ss.StillShotError):
            ss.render(broken, out, "push-in", duration=1, fps=12, width=96, height=172)
        self.assertEqual(sorted(p.name for p in self.tmp.iterdir()), ["broken.png", "scene.png"])

    def test_summary_records_source_image_hash(self):
        import hashlib
        summary = ss.render(self.image, self.tmp / "scene.mp4", "push-in", duration=1, fps=12,
                            width=96, height=172)
        self.assertEqual(summary["image_sha256"], hashlib.sha256(self.image.read_bytes()).hexdigest())

    def test_cli_prints_json_and_fails_cleanly(self):
        out = self.tmp / "cli.mp4"
        ok = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "still_shot.py"), "--image", str(self.image), "--out", str(out),
             "--effect", "tilt-up", "--duration", "1", "--fps", "12", "--width", "96", "--height", "172"],
            capture_output=True, text=True,
        )
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertTrue(json.loads(ok.stdout)["ok"])
        bad = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "still_shot.py"), "--image", str(self.image), "--out",
             str(self.tmp / "bad.mp4"), "--effect", "pan-left", "--depth", "deep"],
            capture_output=True, text=True,
        )
        self.assertEqual(bad.returncode, 1)
        self.assertFalse(json.loads(bad.stderr)["ok"])


if __name__ == "__main__":
    unittest.main()
