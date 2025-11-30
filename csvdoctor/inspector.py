from pathlib import Path
from typing import Dict, Any
import csv
import chardet
import pandas as pd

from . import config
from .utils import ensure_dirs, log

def detect_encoding(path: Path) -> str:
    log(f"Detectando encoding para {path}")
    with open(path, "rb") as f:
        raw = f.read(8192)
    guess = chardet.detect(raw)
    enc = guess.get("encoding") or "utf-8"
    log(f"Encoding detectado: {enc} (confiança={guess.get('confidence')})")
    return enc

def detect_delimiter(path: Path, encoding: str) -> str:
    log(f"Detectando delimitador para {path}")
    lines = []
    with open(path, "r", encoding=encoding, errors="replace") as f:
        for _ in range(30):
            line = f.readline()
            if not line:
                break
            lines.append(line)
    sample = "".join(lines)
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters="".join(config.CANDIDATE_DELIMS))
        delim = dialect.delimiter
        log(f"Delimitador detectado pelo Sniffer: {repr(delim)}")
        return delim
    except Exception as e:
        log(f"Sniffer falhou: {e}", level="WARN")
        counts = {d: sample.count(d) for d in config.CANDIDATE_DELIMS}
        delim = max(counts, key=counts.get)
        log(f"Delimitador escolhido por heurística: {repr(delim)}")
        return delim

def build_diagnostic(path: str) -> Dict[str, Any]:
    ensure_dirs()
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {csv_path}")

    log(f"Iniciando diagnóstico v5 para {csv_path}")

    encoding = detect_encoding(csv_path)
    delimiter = detect_delimiter(csv_path, encoding)

    errors = []
    bad_rows = {}
    preview_lines = []

    # Preview bruto
    with open(csv_path, "r", encoding=encoding, errors="replace") as f:
        for i in range(50):
            line = f.readline()
            if not line:
                break
            preview_lines.append(line.rstrip("\n"))

    # Scan estrutural simples
    expected_cols = None
    with open(csv_path, "r", encoding=encoding, errors="replace") as f:
        for i, line in enumerate(f, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            cols = stripped.split(delimiter)
            n_cols = len(cols)
            if expected_cols is None:
                expected_cols = n_cols
                continue
            if n_cols != expected_cols:
                msg = f"Linha {i}: número de colunas {n_cols}, esperado {expected_cols}."
                errors.append(msg)
                bad_rows[i] = line[:200]
                log(msg, level="WARN")

    # Tentativa de carregar com pandas
    df = None
    try:
        df = pd.read_csv(
            csv_path,
            encoding=encoding,
            sep=delimiter,
            engine="python",
            on_bad_lines="skip",
        )
        log(f"Arquivo carregado, shape={df.shape}")
    except Exception as e:
        msg = f"Falha do pandas ao carregar CSV: {e}"
        errors.append(msg)
        log(msg, level="ERROR")

    column_summary = []
    if df is not None:
        for col in df.columns:
            s = df[col]
            non_null = s.dropna()
            total = len(s)
            null_frac = float(s.isna().mean())
            inferred_type = str(s.dtype)
            unique = int(non_null.nunique()) if total else 0
            suspicious = False
            reasons = []
            if inferred_type == "object" and unique > 0.9 * len(non_null) and len(non_null) > 50:
                suspicious = True
                reasons.append("Alta cardinalidade em coluna textual.")
            col_info = {
                "name": col,
                "dtype": inferred_type,
                "null_fraction": null_frac,
                "n_unique": unique,
                "suspicious": suspicious,
                "reasons": reasons,
            }
            column_summary.append(col_info)

    score = max(0, 100 - len(errors) * 2)

    suggestions = []
    if errors:
        suggestions.append("Rever as linhas listadas em 'bad_rows' e corrigir desalinhamentos de colunas.")
    if df is None:
        suggestions.append("Pandas não conseguiu carregar o arquivo. Verifique encoding e delimitador.")
    else:
        suggestions.append("Considere definir schema explícito (tipos) ao carregar o CSV em produção.")
    suggestions.append("Você pode tentar o reparo automático com: csvdoctor repair <arquivo>.csv")

    diag: Dict[str, Any] = {
        "file_path": str(csv_path),
        "encoding": encoding,
        "delimiter": delimiter,
        "preview_raw": preview_lines,
        "bad_rows": bad_rows,
        "errors_detected": errors,
        "quality_score": score,
        "column_summary": column_summary,
        "suggestions": suggestions,
    }

    log("Diagnóstico concluído.")
    return diag
