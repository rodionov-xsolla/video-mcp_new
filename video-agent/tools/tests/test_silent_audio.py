import base64
import contextlib
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))

import silent_audio as sa  # noqa: E402

HAS_FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))
PREFIX = "data:audio/mpeg;base64,"


def run_main(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = sa.main(argv)
    return code, out.getvalue(), err.getvalue()


class DurationTests(unittest.TestCase):
    def assert_rejected(self, value):
        code, out, err = run_main(["--duration", value])
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        error = json.loads(err)
        self.assertFalse(error["ok"])
        self.assertIn("duration", error["error"])

    def test_rejects_shorter_than_two_seconds(self):
        self.assert_rejected("1")

    def test_rejects_longer_than_fifteen_seconds(self):
        self.assert_rejected("20")

    def test_rejects_non_numbers(self):
        for value in ("", "five", "nan", "inf"):
            with self.subTest(value=value):
                self.assert_rejected(value)

    def test_command_renders_mono_16k_mp3_silence(self):
        command = sa.build_command("ffmpeg", "out.mp3", 4.8)
        self.assertIn("anullsrc=r=16000:cl=mono", command)
        self.assertEqual(command[command.index("-t") + 1], "4.800")
        self.assertEqual(command[command.index("-c:a") + 1], "libmp3lame")
        self.assertEqual(command[command.index("-b:a") + 1], "16k")


@unittest.skipUnless(HAS_FFMPEG, "ffmpeg and ffprobe are required")
class RenderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def decode(self, uri, name):
        self.assertTrue(uri.startswith(PREFIX))
        mp3 = self.tmp / name
        mp3.write_bytes(base64.b64decode(uri[len(PREFIX):], validate=True))
        return mp3

    def assert_silent_mp3(self, mp3, duration):
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_name",
             "-of", "json", str(mp3)],
            capture_output=True, text=True, check=True,
        )
        meta = json.loads(probe.stdout)
        self.assertEqual([s["codec_name"] for s in meta["streams"]], ["mp3"])
        self.assertAlmostEqual(float(meta["format"]["duration"]), duration, delta=0.1)
        volume = subprocess.run(
            ["ffmpeg", "-hide_banner", "-nostats", "-i", str(mp3), "-af", "volumedetect",
             "-f", "null", "-"],
            capture_output=True, text=True, check=True,
        )
        match = re.search(r"max_volume: (-?[0-9.]+|-inf) dB", volume.stderr)
        self.assertIsNotNone(match, volume.stderr)
        self.assertLess(float(match.group(1)), -80)

    def test_prints_data_uri_of_silent_mp3_with_requested_duration(self):
        for duration in (2, 4.8, 15):
            with self.subTest(duration=duration):
                code, out, err = run_main(["--duration", str(duration)])
                self.assertEqual(code, 0, err)
                summary = json.loads(out)
                self.assertTrue(summary["ok"])
                self.assertEqual(summary["duration"], duration)
                self.assertNotIn("out", summary)
                mp3 = self.decode(summary["data_uri"], f"silence-{duration}.mp3")
                self.assertEqual(mp3.stat().st_size, summary["bytes"])
                self.assert_silent_mp3(mp3, duration)

    def test_out_writes_only_the_data_uri(self):
        target = self.tmp / "build" / "video" / "silence" / "scene-3.txt"
        code, out, err = run_main(["--duration", "5", "--out", str(target)])
        self.assertEqual(code, 0, err)
        summary = json.loads(out)
        self.assertEqual(summary["out"], str(target))
        self.assertNotIn("data_uri", summary)
        uri = target.read_text(encoding="ascii")
        self.assertEqual(uri, uri.strip())
        mp3 = self.decode(uri, "silence-out.mp3")
        self.assertEqual(mp3.stat().st_size, summary["bytes"])
        self.assert_silent_mp3(mp3, 5)


if __name__ == "__main__":
    unittest.main()
