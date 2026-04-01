from pathlib import Path

APP_TITLE = "BreakLines"
APP_SUBTITLE = "Structural Pass Analysis in Football"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "dashboard"
ASSETS_DIR = BASE_DIR / "assets"

PASS_TYPE_ORDER = [
    "circulatory",
    "destabilising",
    "line_breaking",
    "space_expanding",
]

PASS_TYPE_LABELS = {
    "circulatory": "Circulatory",
    "destabilising": "Destabilising",
    "line_breaking": "Line-breaking",
    "space_expanding": "Space-expanding",
}

PASS_TYPE_COLORS = {
    "circulatory": "#7A7A7A",
    "destabilising": "#F39C12",
    "line_breaking": "#C0392B",
    "space_expanding": "#2980B9",
}