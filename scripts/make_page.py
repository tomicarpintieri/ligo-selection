"""Build the standalone Spanish project page from results and generated figures."""
import base64
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _data_uri(path):
    mime = "image/gif" if path.suffix == ".gif" else "image/png"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def main():
    text = (ROOT / "page" / "template.html").read_text(encoding="utf8")
    values = json.loads((ROOT / "results.json").read_text(encoding="utf8"))
    for key, value in values.items():
        text = text.replace(f"__{key}__", f"{value:.5g}" if isinstance(value, float) else str(value))
    figures = {"[FIGURE_F01]": "f01_snr_timeseries.png", "[FIGURE_F02]": "f02_waveform_vs_lal.png", "[FIGURE_F03]": "f03_horizon_vs_mchirp.png", "[FIGURE_F04]": "f04_antenna_pattern.png", "[FIGURE_F05]": "f05_network_skymap.png", "[FIGURE_F06_GIF]": "f06_rotation.gif", "[FIGURE_F06_PANELS]": "f06_rotation_panels.png"}
    for marker, name in figures.items():
        text = text.replace(marker, _data_uri(ROOT / "figures" / name))
    assert not re.search(r"__[A-Za-z0-9_]+__|\[FIGURE_[A-Z0-9_]+\]", text)
    (ROOT / "page" / "index.html").write_text(text, encoding="utf8")


if __name__ == "__main__":
    main()
