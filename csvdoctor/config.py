from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"
LOGS_DIR = OUTPUT_DIR / "logs"
REPORT_HTML_PATH = OUTPUT_DIR / "report.html"
REPORT_JSON_PATH = OUTPUT_DIR / "diagnostic.json"

SAMPLE_LINES = 500

CANDIDATE_ENCODINGS = [
    "utf-8",
    "latin-1",
    "cp1252",
    "utf-16",
    "ascii",
]

CANDIDATE_DELIMS = [",", ";", "\t", "|", " "]
