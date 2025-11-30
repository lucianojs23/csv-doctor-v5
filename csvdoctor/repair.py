from pathlib import Path
from typing import Dict, Any, List
import csv
import pandas as pd
import collections

from .inspector import detect_encoding, detect_delimiter
from .utils import ensure_dirs, log
from . import config

def _read_logical_lines(path: Path, encoding: str) -> List[str]:
    """Lê o arquivo agrupando linhas quebradas por aspas desbalanceadas."""
    logical_lines: List[str] = []
    buffer = ""
    with open(path, "r", encoding=encoding, errors="replace") as f:
        for raw in f:
            buffer += raw
            if buffer.count('"') % 2 == 0:
                logical_lines.append(buffer.rstrip("\n"))
                buffer = ""
    if buffer:
        logical_lines.append(buffer.rstrip("\n"))
    return logical_lines

def _parse_row(line: str, delimiter: str) -> List[str]:
    try:
        reader = csv.reader([line], delimiter=delimiter, quotechar='"')
        for row in reader:
            return list(row)
    except Exception:
        return line.split(delimiter)
    return []

def _determine_expected_cols(rows: List[List[str]]) -> int:
    counts = [len(r) for r in rows if len(r) > 0]
    if not counts:
        return 0
    counter = collections.Counter(counts)
    return counter.most_common(1)[0][0]

def _fix_columns(rows: List[List[str]], expected: int) -> Dict[str, Any]:
    fixed_rows: List[List[str]] = []
    stats = {
        "rows_total": len(rows),
        "rows_padded": 0,
        "rows_shrunk": 0,
        "rows_ok": 0,
    }
    for r in rows:
        if expected == 0:
            fixed_rows.append(r)
            continue
        if len(r) == expected:
            fixed_rows.append(r)
            stats["rows_ok"] += 1
        elif len(r) < expected:
            r2 = r + ["" for _ in range(expected - len(r))]
            fixed_rows.append(r2)
            stats["rows_padded"] += 1
        else:
            head = r[: expected - 1]
            tail = " ".join(r[expected - 1 :])
            fixed_rows.append(head + [tail])
            stats["rows_shrunk"] += 1
    return {"rows": fixed_rows, "stats": stats}

def _detect_column_types(df: pd.DataFrame) -> Dict[str, str]:
    types: Dict[str, str] = {}
    for col in df.columns:
        s = df[col].astype(str).str.strip()
        non_empty = s[(s != "") & (s.str.lower() != "na") & (s.str.lower() != "null")]
        if non_empty.empty:
            types[col] = "string"
            continue
        # tenta numérico
        num_coerced = pd.to_numeric(non_empty.str.replace(" ", "").str.replace(".", "").str.replace(",", "."), errors="coerce")
        frac_num = float(num_coerced.notna().mean())
        # tenta data
        date_coerced = pd.to_datetime(non_empty, errors="coerce", dayfirst=True)
        frac_date = float(date_coerced.notna().mean())
        if frac_num > 0.7 and frac_num > frac_date:
            types[col] = "number"
        elif frac_date > 0.7 and frac_date > frac_num:
            types[col] = "date"
        else:
            types[col] = "string"
    return types

def _normalize_column(s: pd.Series, col_type: str) -> pd.Series:
    s2 = s.astype(str).str.strip()
    if col_type == "number":
        cleaned = (
            s2.str.replace(" ", "", regex=False)
              .str.replace(".", "", regex=False)
              .str.replace(",", ".", regex=False)
        )
        num = pd.to_numeric(cleaned, errors="coerce")
        return num.map(lambda x: f"{x:.6g}" if pd.notna(x) else "")
    elif col_type == "date":
        dt = pd.to_datetime(s2, errors="coerce", dayfirst=True)
        return dt.dt.strftime("%Y-%m-%d").fillna("")
    else:
        return s2.replace({"NA": "", "NaN": "", "null": ""}, regex=False)

def repair_csv(path: str, output_path: str | None = None) -> Dict[str, Any]:
    ensure_dirs()
    src = Path(path)
    if not src.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {src}")

    log(f"Iniciando reparo automático para {src}")

    enc = detect_encoding(src)
    delim = detect_delimiter(src, enc)

    logical_lines = _read_logical_lines(src, enc)
    parsed_rows = [_parse_row(line, delim) for line in logical_lines if line.strip()]

    if not parsed_rows:
        raise ValueError("Nenhuma linha válida encontrada para reparo.")

    header = parsed_rows[0]
    data_rows = parsed_rows[1:]

    expected = _determine_expected_cols(data_rows)
    fix_result = _fix_columns(data_rows, expected)
    fixed_data = fix_result["rows"]
    col_stats = fix_result["stats"]

    df = pd.DataFrame(fixed_data, columns=header)

    col_types = _detect_column_types(df)
    norm_df = df.copy()
    for col, t in col_types.items():
        norm_df[col] = _normalize_column(df[col], t)

    out_dir = config.OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    if output_path is None:
        out_path = out_dir / f"{src.stem}_repaired.csv"
    else:
        out_path = Path(output_path)

    norm_df.to_csv(out_path, index=False, encoding="utf-8")

    stats = {
        "source_file": str(src),
        "repaired_file": str(out_path),
        "encoding_used": enc,
        "delimiter_used": delim,
        "expected_columns": expected,
        "column_types": col_types,
    }
    stats.update(col_stats)

    log(f"Reparo concluído. Arquivo salvo em {out_path}")
    return stats
