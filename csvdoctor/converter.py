from pathlib import Path
from typing import Literal
import pandas as pd

from . import config
from .utils import log
from .inspector import detect_encoding, detect_delimiter

def convert_csv(path: str, target: Literal["parquet", "feather", "csv-clean"]) -> Path:
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {csv_path}")

    enc = detect_encoding(csv_path)
    delim = detect_delimiter(csv_path, enc)

    log(f"Iniciando conversão {target} para {csv_path}")
    df = pd.read_csv(
        csv_path,
        encoding=enc,
        sep=delim,
        engine="python",
        on_bad_lines="skip",
    )

    out_dir = config.OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    if target == "parquet":
        out_path = out_dir / f"{csv_path.stem}.parquet"
        df.to_parquet(out_path, index=False)
    elif target == "feather":
        out_path = out_dir / f"{csv_path.stem}.feather"
        df.to_feather(out_path)
    else:
        out_path = out_dir / f"{csv_path.stem}_clean.csv"
        df.to_csv(out_path, index=False)

    log(f"Conversão concluída: {out_path}")
    return out_path
