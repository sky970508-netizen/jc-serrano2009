# 논문 PDF → 저널클럽 HTML 만들기

새 논문을 같은 형태의 읽기용 HTML로 만들 때 따르는 규칙과 순서.
이 문서 하나만 보고 처음부터 끝까지 갈 수 있게 정리했다.

**결과물**: 그림·수식 폰트까지 전부 내장된 단일 HTML 한 개.
보기 모드 6가지(교차 / 2단 / 한글 / English / 논문 / 논문·한글), 형광펜·메모,
절별 공부 가이드, 원문 PNAS식 2단 조판.

---

## 0. 준비물

| | 확인 | 없을 때 |
|---|---|---|
| Python 3 | `python3 -V` | (표준 라이브러리만 씀. 외부 패키지 불필요) |
| ImageMagick | `magick -version` | `brew install imagemagick` — 그림 캡션 크롭에 필요 |
| cwebp | `cwebp -version` | `brew install webp` — 배포용 경량화에만 필요(선택) |
| Swift | `swift --version` | macOS 기본 제공. PDF 구조 추출에 필요 |
| KaTeX | `.assets/katex/` | 아래 4.0 참조 |

---

## 1. 폴더 구조

새 논문 폴더를 만들고 이 폴더에서 다음 파일을 복사해 온다.

```
Paper2024/
├── build.py                    ← 복사 후 §5의 여섯 군데만 고친다
├── guide.py                    ← 공부 가이드 원고 (새로 쓴다)
├── captions.py                 ← 원문 그림 캡션 (PDF에서 뽑는다)
├── tools/
│   ├── pdf_text.swift          ← 복사 (그대로 씀)
│   ├── pdf_lines.swift         ← 복사 (그대로 씀)
│   └── pdf_paras.py            ← 복사 (그대로 씀)
├── .assets/katex/              ← 복사 (그대로 씀)
├── figures/                    ← 논문에서 오려낸 그림 PNG
├── <논문제목>.md                ← 한영 대역 번역 (§3 규칙대로)
└── paper.pdf
```

빌드 산출물은 `Paper2024.html`(로컬 고화질)과 `index.html`(배포 경량).

### 1.0 KaTeX 내려받기 (새 환경에서 한 번만)

```bash
mkdir -p .assets/katex && cd /tmp
curl -sL -o katex.tgz https://registry.npmjs.org/katex/-/katex-0.16.11.tgz
tar xzf katex.tgz
cp package/dist/katex.min.{css,js} <프로젝트>/.assets/katex/
cp -r package/dist/fonts <프로젝트>/.assets/katex/
rm -f <프로젝트>/.assets/katex/fonts/*.ttf <프로젝트>/.assets/katex/fonts/*.woff
```

woff2만 남기면 약 300 KB. build.py가 CSS의 폰트 URL을 data URI로 바꿔 넣는다.

---

## 2. 그림 준비

논문 PDF에서 **그림과 표를 각각 하나의 PNG로** 오려 `figures/`에 넣는다.
캡션이 같이 들어가도 된다 — build.py가 자동으로 잘라낸다(§7).

지켜야 할 것:

- **본문에 나오는 순서대로** 파일명이 정렬되게 한다(스크린샷 시각 순서면 자연스럽게 맞는다).
  이 순서가 그대로 `FIGURE_ORDER`와 짝지어진다.
- 표도 이미지로 넣되, 숫자를 그대로 살릴 표는 §6처럼 실제 HTML 표로 바꾸는 편이 낫다.
- 해상도는 가로 1000~2000 px면 충분하다.

---

## 3. 번역 md 작성 규칙 ★ 가장 중요

빌드기가 이 규칙만 보고 구조를 판별한다. 어기면 조용히 어긋난다.

### 3.1 기본 형태

**빈 줄로 구분된 블록** 단위로 쓴다. 영어 한 문장 → 그 번역 한 문장을 번갈아 둔다.

```markdown
In recent years, a huge amount of data on large-scale social networks has become available.

최근 몇 년간 대규모 사회 네트워크에 관한 방대한 데이터가 활용 가능해졌다.

Examples can be found in all domains; from technological to social systems (1–3).

그 예는 모든 영역에서 찾아볼 수 있는데, 기술적 시스템에서 사회적 시스템까지 다양하다 (1–3).
```

| 규칙 | 이유 |
|---|---|
| **한 문장 = 한 블록** | 교차 모드에서 문장 단위로 대조된다 |
| **영어 먼저, 한국어 다음** | 한글 음절이 있으면 한국어로 판별한다. 순서가 바뀌면 짝이 깨진다 |
| 영어 블록에 한글을 섞지 말 것 | 위와 같은 이유 |
| 짝 없는 블록도 괜찮다 | 표제지·참고문헌 등은 그대로 단독 출력된다 |

### 3.2 제목

```markdown
# 논문 제목 한국어 번역
## 초록 (Abstract)
### 격차 필터 (The Disparity Filter)
#### 최소 신장 트리 (minimum spanning tree, MST)
```

- 형식은 반드시 **`한국어 (English)`** — 괄호 안이 논문 모드에서 원문 제목으로 쓰인다.
- `#`(h1)은 무시된다. 표제지는 build.py의 masthead에 직접 쓴다(§5).
- h2가 절, h3/h4가 소절. 목차와 공부 가이드가 이 단위로 붙는다.

### 3.3 수식

```markdown
인라인은 $p_{ij} = \omega_{ij}/s_i$ 처럼.

$$\alpha_{ij} = 1 - (k-1)\int_0^{p_{ij}} (1-x)^{k-2}\,dx < \alpha \quad [2]$$
```

- 블록 수식 끝의 **`\quad [n]`** 이 식 번호가 된다. 이 번호로 `guide.py`의 해설이 붙는다.
- 한국어 쪽에만 `$…$`를 붙여도 된다. **영어 쪽 평문 수식은 build.py가 자동 변환**한다(§5-③).

### 3.4 그림

```markdown
![[Pasted image 20260802141019.png]]
```

Obsidian 위키링크 형식. `figures/` 안의 파일명과 정확히 같아야 한다.
본문에서 **등장하는 순서**가 `FIGURE_ORDER`의 순서다.

### 3.5 캡션 절 (문서 맨 아래)

번역 캡션은 본문에 흩어 두지 말고 문서 끝에 모아 둔다.

```markdown
## 표 및 그림 캡션 (Tables and Figure Captions)

> **표 1(Table 1).** 서로 다른 유의수준 α 값에 대한 … 백본의 크기.

**U.S. airport network (미국 공항 네트워크)**

|α|%W_T|%N_T|%E_T|
|---|---|---|---|
|0.2|94|77|24|

> **그림 1(Fig. 1).** 필터가 유지한 가중치의 비율(왼쪽)과 …
```

- 이 절 제목에 **"표 및 그림 캡션"** 이라는 말이 반드시 들어가야 한다. 빌드기가 이걸로 절을 찾는다.
- `> **표 N(Table N).**` / `> **그림 N(Fig. N).**` 형식이어야 각 그림 아래로 옮겨진다.
- 이 절의 마크다운 표는 실제 HTML 표(§6)의 원자료로 쓰인다.
- 이 절 자체는 출력물에서 사라진다(내용이 전부 본문으로 흡수되므로).

### 3.6 그 밖

| 요소 | 형식 | 결과 |
|---|---|---|
| 각주 | `> _각주: …_` | 본문 흐름에 회색 상자로. 논문 모드에서는 숨김 |
| 참고문헌 | `1. Newman MEJ (2003) …` 를 빈 줄 없이 연속 | 번호 앵커가 생겨 본문 인용에서 점프 |
| 본문 인용 | `(5)`, `(17, 18)`, `(1–3)` | 자동으로 참고문헌 링크 |
| 상호참조 | `그림 2`, `표 1`, `Fig. 3`, `Table 1` | 자동으로 해당 그림·표로 링크 |
| 구분선 | `---` | 무시(절 구분은 제목이 한다) |

---

## 4. PDF에서 구조 뽑기

번역 md는 한 문장씩 쪼개져 있어서 **논문 모드에서 원래 문단으로 되돌리려면** PDF의 조판 정보가 필요하다.

### 4.1 본문 텍스트

```bash
swift tools/pdf_text.swift paper.pdf > pdf.txt
```

여기서 **원문 그림 캡션**을 찾아 `captions.py`에 옮긴다.

```bash
grep -o 'Fig\. 1\..\{0,300\}' pdf.txt
```

캡션은 본문과 섞여 나오므로 끝나는 지점을 눈으로 잘라야 한다.
`(Left)` `(Top)` 같은 방향 표시는 `<i>`로, 첨자는 `<sub>`로 감싼다.

### 4.2 문단 시작 지점

```bash
swift tools/pdf_lines.swift paper.pdf > lines.tsv
python3 tools/pdf_paras.py lines.tsv
```

들여쓰기된 줄이 문단의 첫 줄이다. 출력에서 **본문에 해당하는 것만** 골라
각 문단의 첫 문장을 `build.py`의 `PDF_PARA_STARTS`에 넣는다.

> 주의 — 추출된 줄 텍스트는 앞줄 꼬리가 10자쯤 섞여 나온다.
> `…as it is clearly seen in the first and second` 라고 찍혔다면,
> 실제 문단 시작은 **그다음 문장**이다. 참고문헌의 내어쓰기도 걸린다(무시).

**수식·그림 뒤에 이어지는 문장은 문단 시작이 아니다.** 빌드기가 자동으로
`.para.cont`(들여쓰기 없음)로 처리하므로 목록에 넣지 않는다.

### 4.3 그림이 한 단인가 두 단인가

```bash
grep -E 'Fig\. [0-9]\.|Table 1\.' lines.tsv | awk -F'\t' '{print $1, $3, $4, substr($5,1,50)}'
```

캡션 줄의 x 범위를 본다. 한쪽 컬럼 폭(예: 52~298)이면 **한 단**,
양쪽에 걸치면(52~560) **두 단**이다. 두 단짜리만 `build.py`에 따로 적어 준다.

---

## 5. build.py에서 논문마다 고치는 곳 — 여섯 군데

### ① `FIGURE_ORDER` (33행 근처)

본문에 이미지가 나오는 순서대로 무엇인지 적는다.

```python
FIGURE_ORDER = [("tbl", 1), ("fig", 1), ("fig", 2), ("fig", 3), ("fig", 4), ("fig", 5)]
```

`("tbl", 1)`은 실제 HTML 표로 대체되고, `("fig", n)`은 이미지+텍스트 캡션이 된다.

### ② `PDF_PARA_STARTS` (39행 근처)

§4.2에서 고른 문단 첫 문장들. **앞부분 40자 정도**면 충분하다.

```python
PDF_PARA_STARTS = [
    "A large number of complex systems find",
    "In recent years, a huge amount of data on",
    ...
]
```

### ③ `EN_MATH_RULES` (149행 근처)

영어 본문의 평문 수식을 LaTeX로 바꾸는 치환표. **구체적인 것부터** 위에 둔다.

```python
(r"pij\s*=\s*ωij/si", r"p_{ij} = \\omega_{ij}/s_i"),
(r"\bωc\b",           r"\\omega_c"),
(r"P\(ω\)",           r"P(\\omega)"),
# 낱글자 변수는 앞말로 확인하고 그 글자만 (뒤돌아보기 폭 고정)
(r"(?<=degree )k\b",  r"k"),
```

무엇을 넣을지는 이렇게 뽑는다:

```bash
python3 - <<'EOF'
import re
md=open("논문.md").read()
en=[b for b in md.split("\n\n") if b and not re.search(r'[가-힣]',b)
    and not b.startswith(('#','>','|','![[','$$'))]
from collections import Counter
c=Counter(m.group(0) for b in en
          for m in re.finditer(r'[^\s,.;:()\[\]]*[ωαβγμσϒΥΘ⟨⟩≈≃≥≤∝Σ−·²]+[^\s,.;:]*', b))
for t,n in sorted(c.items(), key=lambda x:-x[1]): print(n, repr(t))
EOF
```

마지막의 그리스 문자 규칙은 그대로 두면 된다(홑글자 α, ω 등을 자동 처리).

### ④ 두 단에 걸치는 그림 (CSS, 1003행 근처)

```css
body[data-view^="paper"] #fig-4{column-span:all;margin:18px 0 20px}
```

§4.3에서 확인한 번호로 바꾼다. 나머지 그림은 자동으로 한 단이다.

### ⑤ 표제지와 제목 (785행 `<title>`, 1258행 masthead)

```html
<title>격차 필터 — Serrano, Boguñá &amp; Vespignani (2009) | 저널클럽</title>
...
<h1>복잡 가중 네트워크의 다중스케일 백본 추출</h1>
<p class="orig">Extracting the multiscale backbone of complex weighted networks</p>
<div class="meta">저자 … <i>저널</i>, 연도 · <a href="https://doi.org/…">DOI</a></div>
```

상단 바의 `.brand`(1230행 근처)도 함께 고친다.

### ⑥ `SUMMARY_CARD` (704행 근처)

맨 위 요약 카드. 논문마다 새로 쓴다. 뼈대는 그대로 두고 내용만 바꾼다:

문제 / 기존 방법의 한계 / 아이디어 / 핵심 장치 / 결과(숫자) / 파이프라인 도식 / 발표 논점.

> 표가 없는 논문이면 `render_table1` 호출을 지우고 `FIGURE_ORDER`에서 `("tbl",1)`을 빼면 된다.

---

## 6. 표를 진짜 표로

수치 표는 이미지로 두지 말고 HTML 표로 만든다. 복사·확대·다크모드에 다 강하다.

1. §3.5처럼 마크다운 표를 캡션 절에 적어 둔다.
2. `render_table1()`을 논문의 표 구조에 맞게 손본다(현재는 두 블록을 좌우로 놓는 형태).
3. 표 캡션 영어 원문은 `captions.py`의 `("tbl", 1)`에.

---

## 7. 그림 캡션 분리 — 자동

논문에서 오려낸 그림에는 보통 캡션이 같이 들어 있다. build.py가

1. 이미지의 **행별 밝기 프로파일**을 만들고,
2. 아래쪽 55% 안에서 **가장 긴 흰 띠**를 찾아,
3. 그 띠의 끝에서 잘라낸다(캡션만 제거, 눈금선은 보존).

잘라낸 결과는 `.assets/crop/`에 캐시된다. **처음 빌드한 뒤 반드시 눈으로 확인**한다:

```bash
python3 - <<'EOF'
import subprocess, pathlib
parts=[]
for f in sorted(pathlib.Path("figures").glob("*.png")):
    c=pathlib.Path(".assets/crop")/f.name
    if c.exists():
        parts += ["(", str(f), "-resize", "480x", "-bordercolor", "gray", "-border", "2",
                  str(c), "-resize", "480x", "-bordercolor", "red", "-border", "2", "+append", ")"]
subprocess.run(["magick"]+parts+["-append","/tmp/crop_check.png"])
EOF
open /tmp/crop_check.png
```

왼쪽이 원본, 오른쪽이 크롭 결과다. 플롯이 잘렸으면 그 그림만 캡션 없이 다시 오려 넣는다.

---

## 8. 공부 가이드 쓰기 (`guide.py`)

네 종류를 채운다. 논문을 다 읽은 뒤에 쓰는 것이 순서다.

| 키 | 내용 | 분량 |
|---|---|---|
| `SECTION[절제목일부]` | `before`(이 절에서 붙잡을 것) / `after`(여기까지 정리) / `check`(질문, 답) | 절마다 2~3줄 + 불릿 3~5 + 질문 1~2 |
| `EQ[번호]` | `title`(이 식이 하는 말) / `lines`(기호, 뜻) / `note`(덧붙임) | 식마다 |
| `FIG[("fig", n)]` | 이 그림에서 볼 것 한두 문장 | 그림마다 |
| `GLOSSARY[용어]` | 한 줄 정의. 본문에 처음 나올 때만 밑줄+툴팁 | 15~20개 |

키는 **제목의 일부 문자열**로 찾는다. `"격차 필터"`처럼 짧고 고유하게 잡는다.

`before`/`after` 안에서는 HTML과 `<span class='m' data-tex='…'></span>`(수식)을 쓸 수 있다.

**답을 아는 척하지 말 것.** 논문에 없는 내용은 넣지 않는다. 논점(`check`)은
저자가 실제로 인정한 한계나 본문에서 근거를 댈 수 있는 것만 쓴다.

---

## 9. 빌드와 배포

```bash
python3 build.py                                   # 로컬 고화질 (PNG)
python3 build.py --webp                            # 무손실 WebP, 화질 동일
python3 build.py --webp=90 --out=index.html        # 배포용 경량
```

GitHub Pages:

```bash
printf '*.pdf\n.assets/\nfigures/\n*.md\n!README.md\nbuild.py\nguide.py\ncaptions.py\ntools/\n__pycache__/\n.DS_Store\n' > .gitignore
printf 'User-agent: *\nDisallow: /\n' > robots.txt     # 검색 노출을 막는다
git init && git add -A && git commit -m "저널클럽 자료"
git branch -M main
gh repo create <저장소이름> --public --source=. --push
gh api -X POST repos/<계정>/<저장소>/pages -f 'source[branch]=main' -f 'source[path]=/'
```

1~2분 뒤 `https://<계정>.github.io/<저장소>/`.

> 무료 Pages는 **public 저장소만** 된다. 논문 전문 번역이 공개 웹에 올라간다는 뜻이므로
> 판단하고 진행한다. `robots.txt`로 검색 노출은 막을 수 있다.

---

## 10. 빌드 후 검증 체크리스트

```bash
python3 - <<'EOF'
import re, pathlib
h = pathlib.Path("index.html").read_text()
print("문단 쌍      ", h.count('class="pair'))
print("원문 문단    ", h.count('class="para'), "(cont:", h.count('class="para cont"'), ")")
print("그림 / 캡션  ", h.count('class="figure"'), "/", h.count("<figcaption>"))
print("식 / 해설    ", h.count('data-display="1"'), "/", h.count("eq-guide"))
print("가이드       ", h.count("guide before"), h.count("guide after"), h.count("guide look"))
print("용어 / 인용  ", len(re.findall(r'class="gl"', h)), "/", h.count('class="cite"'))
print("남은 마크다운", re.findall(r'!\[\[|\*\*|^\|', h, re.M)[:3])
EOF
```

그리고 눈으로:

- [ ] `논문` 모드에서 문단이 원문과 같이 묶였나 (수식 뒤 문장은 들여쓰기 없음)
- [ ] `논문` 모드에서 그림이 원문과 같은 단 폭인가
- [ ] 영어 본문의 수식이 이탤릭으로 조판됐나 (`pij` 같은 평문이 남아 있지 않은가)
- [ ] 그림 캡션이 이미지에서 잘리고 텍스트로 나오는가
- [ ] 참고문헌 인용 `(5)`가 해당 항목으로 점프하는가
- [ ] 문장을 드래그하면 형광펜이 뜨는가
- [ ] 320·360·390·414·768 px × 보기 모드 6가지에서 `documentElement.scrollWidth`와
      `main.scrollWidth`가 모두 뷰포트와 같은가 (넘치면 원인 요소를 찾아 고칠 것.
      `overflow-x:hidden`은 마지막 안전장치이지 원인 수정이 아니다)
- [ ] 상단 바 버튼들의 좌우 좌표가 서로 겹치지 않는가

---

## 11. 자주 밟는 함정

| 증상 | 원인 | 해결 |
|---|---|---|
| 한영 짝이 어긋난다 | 영어 블록에 한글이 섞였거나 순서가 뒤집힘 | 한글 음절 유무로 판별한다. 영어 블록을 순수 영어로 |
| 문단이 전부 따로 논다 | `PDF_PARA_STARTS` 문자열이 md와 다름 | 공백·따옴표·대시까지 md에서 그대로 복사 |
| 알파벳 단축키가 안 먹는다 | 한글 입력 상태 (`p` → `ㅔ`) | 이미 `e.code` 기준으로 처리됨. 새로 추가할 때도 `e.key`를 쓰지 말 것 |
| 바꾼 게 반영이 안 된다 | 브라우저 캐시 (Pages는 `max-age=600`) | `⌘⇧R` 또는 `?v=2` |
| 가이드 상자의 굵은 글씨가 줄바꿈된다 | CSS 후손 선택자가 안쪽 `<b>`까지 잡음 | `.guide.before>b` 처럼 **자식 선택자**로 |
| 용어를 바꿨더니 문장이 깨진다 | 받침 유무로 조사가 달라짐 | 치환 후 `엣지을→엣지를`류를 일괄 교정하고 문장을 확인 |
| 형광펜이 다 풀렸다 | 문단 키가 바뀜 | 키는 **영어 원문** 해시. 영어를 건드리지 않으면 유지된다 |
| 수식이 `,dx`로 깨져 보인다 | 번역 과정에서 `\,`가 `,`로 | build.py가 자동 보정. 다른 패턴이면 `fix_tex()`에 추가 |
| 캡션 크롭이 플롯을 먹었다 | 그림 안 여백이 캡션 앞 여백보다 큼 | 그 그림만 캡션 없이 다시 오려 넣는다 |
| 모바일에서 화면이 좌우로 끌린다 | `visibility:hidden`인 **가상 요소**(툴팁 등)도 레이아웃 공간을 차지해 문서를 넓힌다. 요소 스캔(`querySelectorAll`)에는 안 잡힌다 | `display:none`으로 숨기고, `main.scrollWidth`를 재서 원인을 좁힌다 |
| 상단 바 버튼이 서로 겹친다 | flex 항목이 min-content 아래로 줄어들면서 자식이 컨테이너 밖으로 나감 | `.seg`와 `.iconbtn`에 `flex:0 0 auto`. 좁은 화면에서는 버튼 수 자체를 줄인다 |

---

## 12. 한 눈에 보는 순서

```
1. 폴더 만들고 build.py / tools / .assets/katex 복사
2. PDF에서 그림·표를 figures/ 로 오려낸다        (순서 주의)
3. 번역 md 작성                                   §3 규칙
4. swift tools/pdf_text.swift  → captions.py      §4.1
5. swift tools/pdf_lines.swift → PDF_PARA_STARTS  §4.2
   그림 단 폭 확인                                §4.3
6. build.py 여섯 군데 수정                        §5
7. guide.py 작성                                  §8
8. python3 build.py → 크롭 결과 확인              §7
9. 체크리스트                                     §10
10. 배포                                          §9
```

번역 md(3)와 가이드(7)가 시간의 대부분을 차지한다. 나머지는 30분 안쪽이다.
