import base64
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import convert


class EmbeddedFigureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def data_uri(data=b"embedded chart"):
        payload = base64.b64encode(data).decode("ascii")
        return f"data:image/png;base64,{payload}"

    def test_extracts_only_embedded_images_inside_knitr_figure(self):
        uri = self.data_uri()
        html = (
            f'<article><p><img src="{uri}" alt="ordinary"></p>'
            '<pre>plot(1)</pre>'
            f'<div class="figure"><img src="{uri}" '
            'aria-label="Generated chart"></div></article>'
        )
        (self.root / "post.html").write_text(html, encoding="utf-8")

        figures = convert.extract_generated_figures(self.root, "post")

        self.assertEqual(figures, [("plot(1)", uri, "Generated chart")])

    def test_decodes_and_injects_embedded_figure_after_matching_code(self):
        image = b"embedded chart bytes"
        uri = self.data_uri(image)
        asset_dir = self.root / "assets"
        body = "Before\n\n```r\nplot(1)\n```\n\nAfter"

        result = convert.inject_figures(
            body,
            [("plot(1)", uri, "Generated chart")],
            self.root,
            asset_dir,
            "post",
            [],
        )

        expected = "![Generated chart](./post/generated-figure-01.png)"
        self.assertIn("```r\nplot(1)\n```\n\n" + expected, result)
        self.assertEqual(
            (asset_dir / "generated-figure-01.png").read_bytes(), image)

    def test_embedded_figure_marker_targets_affected_html(self):
        uri = self.data_uri()
        generated = (
            f'<div class="figure"><img src="{uri}" alt="chart"></div>'
        ).encode()
        ordinary = f'<p><img src="{uri}" alt="ordinary"></p>'.encode()

        self.assertIsNotNone(convert.EMBEDDED_FIGURE_RE.search(generated))
        self.assertIsNone(convert.EMBEDDED_FIGURE_RE.search(ordinary))

    def test_refreshes_changed_external_figure_asset(self):
        source_dir = self.root / "post_files" / "figure-html"
        source_dir.mkdir(parents=True)
        source = source_dir / "chart.png"
        source.write_bytes(b"new chart")
        asset_dir = self.root / "assets"
        asset_dir.mkdir()
        (asset_dir / "chart.png").write_bytes(b"old chart")

        convert.inject_figures(
            "```r\nplot(1)\n```",
            [("plot(1)", "post_files/figure-html/chart.png", "Chart")],
            self.root,
            asset_dir,
            "post",
            [],
        )

        self.assertEqual((asset_dir / "chart.png").read_bytes(), b"new chart")


if __name__ == "__main__":
    unittest.main()
