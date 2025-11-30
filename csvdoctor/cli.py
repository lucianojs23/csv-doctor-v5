import argparse
from .inspector import build_diagnostic
from .reporter import generate_html_report
from .converter import convert_csv
from .repair import repair_csv
from . import config
from .utils import ensure_dirs, pretty_json, log

def cmd_inspect(args):
    ensure_dirs()
    diag = build_diagnostic(args.file)
    with open(config.REPORT_JSON_PATH, "w", encoding="utf-8") as f:
        f.write(pretty_json(diag))
    print("Diagnóstico salvo em:", config.REPORT_JSON_PATH)
    if args.html:
        report = generate_html_report(diag)
        print("Relatório HTML salvo em:", report)

def cmd_convert(args):
    ensure_dirs()
    out = convert_csv(args.file, args.to)
    print("Arquivo convertido salvo em:", out)

def cmd_repair(args):
    ensure_dirs()
    stats = repair_csv(args.file, args.output)
    print("Reparo concluído. Arquivo salvo em:", stats["repaired_file"])
    print("Resumo:")
    for k, v in stats.items():
        print(f"  - {k}: {v}")

def cmd_full(args):
    ensure_dirs()
    # Repara primeiro
    stats = repair_csv(args.file, None)
    repaired = stats["repaired_file"]
    log(f"Arquivo reparado usado no diagnóstico full: {repaired}")
    diag = build_diagnostic(repaired)
    diag["repair_info"] = stats
    with open(config.REPORT_JSON_PATH, "w", encoding="utf-8") as f:
        f.write(pretty_json(diag))
    report = generate_html_report(diag)
    out = convert_csv(repaired, args.to)
    print("Reparo automático salvo em:", repaired)
    print("Diagnóstico salvo em:", config.REPORT_JSON_PATH)
    print("Relatório HTML salvo em:", report)
    print("Arquivo convertido salvo em:", out)

def main():
    parser = argparse.ArgumentParser(
        prog="csvdoctor",
        description="CSV Doctor v5 - diagnóstico e reparo automático de CSV."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_inspect = sub.add_parser("inspect", help="Diagnosticar um CSV.")
    p_inspect.add_argument("file", help="Caminho para o arquivo CSV.")
    p_inspect.add_argument("--html", action="store_true", help="Gerar relatório HTML (React).")
    p_inspect.set_defaults(func=cmd_inspect)

    p_convert = sub.add_parser("convert", help="Converter CSV.")
    p_convert.add_argument("file", help="Caminho para o arquivo CSV.")
    p_convert.add_argument("--to", choices=["parquet", "feather", "csv-clean"], required=True)
    p_convert.set_defaults(func=cmd_convert)

    p_repair = sub.add_parser("repair", help="Reparar CSV automaticamente.")
    p_repair.add_argument("file", help="Caminho para o arquivo CSV.")
    p_repair.add_argument("--output", help="Caminho de saída para o CSV reparado.")
    p_repair.set_defaults(func=cmd_repair)

    p_full = sub.add_parser("full", help="Reparo + Diagnóstico + Relatório + Conversão.")
    p_full.add_argument("file", help="Caminho para o arquivo CSV.")
    p_full.add_argument("--to", choices=["parquet", "feather", "csv-clean"], default="parquet")
    p_full.set_defaults(func=cmd_full)

    args = parser.parse_args()
    args.func(args)
