#!/usr/bin/env python3
"""
PDF의 '문단 시작' 지점을 찾아 build.py의 PDF_PARA_STARTS 후보를 뽑는다.

    swift tools/pdf_lines.swift paper.pdf > lines.tsv
    python3 tools/pdf_paras.py lines.tsv

원리: 2단 조판에서 새 문단의 첫 줄은 들여쓰기가 되어 있다.
각 줄의 왼쪽 x좌표를 모아 컬럼의 기준선을 찾고, 그보다 5~16pt 오른쪽에서
시작하는 줄을 문단 시작으로 본다. (참고문헌의 내어쓰기는 걸러야 하므로
출력 결과를 눈으로 확인한 뒤 본문에 해당하는 것만 골라 쓴다.)
"""
import collections
import re
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "lines.tsv"
geo = collections.defaultdict(list)
for line in open(path, encoding="utf-8"):
    p, y, x0, x1, s = line.rstrip("\n").split("\t", 4)
    geo[int(p)].append((float(y), float(x0), float(x1), s))

for page in sorted(geo):
    xs = [g[1] for g in geo[page]]
    cnt = collections.Counter(round(x) for x in xs)
    cols = sorted([x for x, c in cnt.items() if c >= 8])       # 본문 컬럼의 왼쪽 기준선
    for y, x0, x1, s in geo[page]:
        for c in cols:
            if 5 < x0 - c < 16:
                # 추출된 줄 텍스트는 앞줄 꼬리가 조금 섞여 나온다.
                # 그 꼬리 다음에 오는 문장이 실제 문단 시작이다.
                print(f"p{page:>2} y{round(y):>4} x{round(x0)}(col{c}) | {s[:96]}")
                break
