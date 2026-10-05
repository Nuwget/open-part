import sys
import unittest
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core import pixelate  # noqa: E402


def make_gradient(size=(64, 64)) -> Image.Image:
    img = Image.new("RGB", size)
    for x in range(size[0]):
        for y in range(size[1]):
            img.putpixel((x, y), ((x * 4) % 256, (y * 4) % 256, (x + y) * 2 % 256))
    return img


class TestPixelate(unittest.TestCase):
    def test_output_size_and_mode(self):
        out = pixelate(make_gradient(), block_size=8)
        self.assertEqual(out.size, (64, 64))
        self.assertEqual(out.mode, "RGBA")

    def test_block_size_one_keeps_resolution(self):
        out = pixelate(make_gradient(), block_size=1)
        self.assertEqual(out.size, (64, 64))

    def test_colors_limits_palette(self):
        for colors in (8, 16, 64):
            out = pixelate(make_gradient(), block_size=8, colors=colors)
            distinct = len(out.getcolors(maxcolors=100_000) or [])
            self.assertLessEqual(distinct, colors)

    def test_dither_changes_result(self):
        src = make_gradient()
        no_dither = pixelate(src, 8, colors=16, dither=False).tobytes()
        dithered = pixelate(src, 8, colors=16, dither=True).tobytes()
        self.assertNotEqual(no_dither, dithered)

    def test_alpha_preserved(self):
        img = Image.new("RGBA", (32, 32), (255, 0, 0, 128))
        out = pixelate(img, 8)
        alpha = out.getchannel("A")
        self.assertTrue(all(v in (127, 128, 129) for v in alpha.getdata()))

    def test_invalid_args(self):
        with self.assertRaises(ValueError):
            pixelate(make_gradient(), block_size=0)
        with self.assertRaises(ValueError):
            pixelate(make_gradient(), block_size=8, colors=1)


if __name__ == "__main__":
    unittest.main()
