#!/usr/bin/env python3
"""element_constants/isotopes.py を NIST の公開データから作り直す。

出典: NIST "Atomic Weights and Isotopic Compositions for All Elements"
https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl (米国政府の著作物、パブリックドメイン)

使い方:
    python scripts/generate_isotopes.py                 # NIST から取得して書き出す
    python scripts/generate_isotopes.py --source x.html # 保存済みのページから書き出す
"""
import argparse
import os
import re
import sys
import urllib.request

NIST_URL = ("https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl"
            "?ele=&ascii=ascii2&isotype=some")
OUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "element_constants", "isotopes.py")

_RECORD = re.compile(
    r"Atomic Number = (\d+)\s*\n"
    r"Atomic Symbol = (\w+)\s*\n"
    r"Mass Number = (\d+)\s*\n"
    r"Relative Atomic Mass = ([^\n]*?)\s*\n"
    r"Isotopic Composition = ([^\n]*?)\s*\n")


def parse(text):
    """(原子番号, 質量数, 相対原子質量, 存在比 or None) の一覧。値は NIST の表記(括弧内が不確かさ)のまま。"""
    rows = []
    for z, _symbol, a, mass, composition in _RECORD.findall(text):
        composition = composition.replace("&nbsp;", "").strip()
        rows.append((int(z), int(a), mass.strip(), composition or None))
    return rows


def select(rows):
    """天然に存在する核種がある元素はそれだけ、無い元素は NIST が挙げる代表的な長寿命核種を残す。"""
    natural = {z for z, _a, _m, c in rows if c is not None}
    return [r for r in rows if r[3] is not None or r[0] not in natural]


def render(rows):
    lines = [
        '"""安定同位体・長寿命核種の相対原子質量と天然存在比。',
        "",
        "scripts/generate_isotopes.py が NIST の公開データから生成する。手で編集しない。",
        f"出典: {NIST_URL}",
        '"""',
        "",
        "# (原子番号, 質量数, 相対原子質量, 天然存在比)。値は NIST の表記のまま(括弧内は末尾桁の不確かさ、",
        "# # は実測でない推定値)。天然に存在しない核種の存在比は None。",
        "ISOTOPE_ROWS = [",
    ]
    for z, a, mass, composition in rows:
        lines.append(f"    ({z}, {a}, {mass!r}, {composition!r}),")
    lines.append("]")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", help="保存済みの NIST のページ(省略時は取得する)")
    args = parser.parse_args(argv)

    if args.source:
        with open(args.source, encoding="utf-8") as f:
            text = f.read()
    else:
        with urllib.request.urlopen(NIST_URL, timeout=60) as response:
            text = response.read().decode("utf-8")

    rows = select(parse(text))
    if len({r[0] for r in rows}) != 118:
        print(f"118 元素がそろっていません({len({r[0] for r in rows})} 元素)", file=sys.stderr)
        return 1
    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(render(rows))
    print(f"{OUT_PATH}  ({len(rows)} 核種)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
