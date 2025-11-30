from pathlib import Path
from string import Template
import json

from . import config
from .utils import ensure_dirs, log

def generate_html_report(diag: dict) -> Path:
    ensure_dirs()
    tpl_path = config.BASE_DIR / "templates" / "report_react.html"
    if not tpl_path.exists():
        raise FileNotFoundError(f"Template não encontrado em {tpl_path}")

    with open(tpl_path, "r", encoding="utf-8") as f:
        tpl = Template(f.read())

    json_data = json.dumps(diag, ensure_ascii=False)

    html = tpl.safe_substitute(
        json_data=json_data
    )

    out_path = config.REPORT_HTML_PATH
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    log(f"Relatório gerado em {out_path}")
    return out_path
