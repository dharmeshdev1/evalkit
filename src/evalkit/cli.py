from __future__ import annotations

import argparse
import json
from pathlib import Path

from evalkit.results import grade_rows, load_samples, per_task_pass_at_k, summarize
from evalkit.stats import paired_bootstrap_diff, sign_test


def cmd_report(args: argparse.Namespace) -> None:
    samples = load_samples(args.file)
    n_tasks = len(samples)
    sizes = sorted({len(v) for v in samples.values()})
    print(f"{args.file}: {n_tasks} tasks, samples per task {sizes}")
    for k, (mean, (lo, hi)) in summarize(samples, args.k).items():
        print(f"  pass@{k:<3} {mean:.3f}  95% CI [{lo:.3f}, {hi:.3f}]")


def cmd_compare(args: argparse.Namespace) -> None:
    a, b = load_samples(args.a), load_samples(args.b)
    shared = sorted(set(a) & set(b))
    if not shared:
        raise SystemExit("the two files share no task ids")
    if len(shared) < max(len(a), len(b)):
        print(f"note: comparing {len(shared)} shared tasks only")
    a = {t: a[t] for t in shared}
    b = {t: b[t] for t in shared}
    pa = per_task_pass_at_k(a, args.k)
    pb = per_task_pass_at_k(b, args.k)
    va, vb = [pa[t] for t in shared], [pb[t] for t in shared]
    diff, (lo, hi) = paired_bootstrap_diff(va, vb)
    wins_a = sum(x > y for x, y in zip(va, vb, strict=True))
    wins_b = sum(y > x for x, y in zip(va, vb, strict=True))
    p = sign_test(wins_a, wins_b)
    na, nb = Path(args.a).stem, Path(args.b).stem
    print(f"pass@{args.k} over {len(shared)} shared tasks")
    print(f"  {na} {sum(va) / len(va):.3f}   {nb} {sum(vb) / len(vb):.3f}")
    print(f"  {na} - {nb} = {diff:+.3f}  95% paired CI [{lo:+.3f}, {hi:+.3f}]")
    tied = len(shared) - wins_a - wins_b
    print(f"  tasks won: {na} {wins_a}, {nb} {wins_b}, tied {tied}")
    print(f"  sign test p = {p:.4f}")


def cmd_grade(args: argparse.Namespace) -> None:
    rows = [json.loads(line) for line in Path(args.file).read_text().splitlines() if line.strip()]
    for row in grade_rows(rows, args.grader):
        print(json.dumps(row))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="evalkit", description="Evaluation statistics toolkit")
    sub = parser.add_subparsers(dest="command", required=True)

    rep = sub.add_parser("report", help="pass@k with bootstrap confidence intervals")
    rep.add_argument("file")
    rep.add_argument("-k", type=int, nargs="+", default=[1])
    rep.set_defaults(func=cmd_report)

    cmp_ = sub.add_parser("compare", help="paired comparison of two systems")
    cmp_.add_argument("a")
    cmp_.add_argument("b")
    cmp_.add_argument("-k", type=int, default=1)
    cmp_.set_defaults(func=cmd_compare)

    grade = sub.add_parser("grade", help="grade outputs against expected answers")
    grade.add_argument("file")
    grade.add_argument("--grader", choices=["exact", "contains", "regex", "numeric"], required=True)
    grade.set_defaults(func=cmd_grade)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
