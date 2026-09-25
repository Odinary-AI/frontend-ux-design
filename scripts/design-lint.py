#!/usr/bin/env python3
"""
design-lint.py — frontend-ux-design 的只读 HTML/CSS 模式扫描器。

- AUTO：满足可确定的文本模式，不等于已确认设计缺陷；仍需核对语境。
- CHECK：待核对线索。两种信号均不能证明视觉、交互或可访问性通过。
- 保留历史规则 ID（含 P0/P1 前缀），这些 ID 不是最终问题严重程度。
- 人工映射和交付判定的唯一正文：references/review.md。
- 纯 Python 标准库，不运行页面、不请求 URL、不解析完整 CSS 级联。

用法：python3 design-lint.py <file.html|dir> [--tokens tokens.css]
目录扫描 .html/.htm/.css；tokens 是外部 CSS 变量声明文件。
两类输入均须为不含 NUL 的 UTF-8 文本（允许 UTF-8 BOM）；不自动猜测编码。
退出码兼容：有效扫描无 AUTO 为 0，有 AUTO 为 1；调用/读取/遍历失败
或零候选输入为 2。0 可能仍含 CHECK，任何退出码都不是设计验收结论。

token 声明仅过滤部分颜色/字体信号，不证明有授权或质量达标；不抑制
占位域名、焦点等其他检查。片段跳过整页响应式启发式；颜色解析和
氛围判断是近似，不证明跨颜色空间的精密视觉分类。
"""

import os
import re
import sys

# ---------- 颜色解析 ----------

def rgb_to_hue_lights(r, g, b):
    """r,g,b ∈ 0–1，返回 (hue 0–360, max, min)。"""
    mx, mn = max(r, g, b), min(r, g, b)
    d = mx - mn
    if d == 0:
        h = 0.0
    elif mx == r:
        h = (60 * ((g - b) / d) + 360) % 360
    elif mx == g:
        h = (60 * ((b - r) / d) + 120) % 360
    else:
        h = (60 * ((r - g) / d) + 240) % 360
    return h, mx, mn

def parse_hex(s):
    s = s.lstrip('#')
    if len(s) == 3:
        s = ''.join(c * 2 for c in s)
    if len(s) != 6:
        return None
    try:
        return tuple(int(s[i:i+2], 16) / 255 for i in (0, 2, 4))
    except ValueError:
        return None

def parse_rgb_func(body):
    parts = re.split(r'[\s,/]+', body.strip())
    vals = []
    for p in parts[:3]:
        if p.endswith('%'):
            vals.append(float(p[:-1]) / 100)
        else:
            vals.append(float(p) / 255)
    return tuple(vals) if len(vals) == 3 else None

def parse_hsl_func(body):
    parts = re.split(r'[\s,/]+', body.strip())
    if len(parts) < 3:
        return None
    h = float(parts[0].replace('deg', ''))
    l = float(parts[2].rstrip('%')) / 100
    return h % 360, l

def parse_oklch_func(body):
    parts = re.split(r'[\s,/]+', body.strip())
    if len(parts) < 3:
        return None
    try:
        l = float(parts[0].rstrip('%'))
        if '%' in parts[0]:
            l /= 100
        h = float(parts[2].replace('deg', ''))
        return h % 360, l
    except ValueError:
        return None

COLOR_RE = re.compile(
    r'#[0-9a-fA-F]{3,6}\b'
    r'|rgba?\(([^)]*)\)'
    r'|hsla?\(([^)]*)\)'
    r'|oklch\(([^)]*)\)'
)

def extract_colors(text):
    """提取 (kind, hue, light, raw, rgb)；rgb 可为 None，light 仅为启发式值。"""
    out = []
    for m in COLOR_RE.finditer(text):
        raw = m.group(0)
        try:
            if raw.startswith('#'):
                rgb = parse_hex(raw)
                if rgb is None:
                    continue
                h, mx, mn = rgb_to_hue_lights(*rgb)
                out.append(('hex', h, (mx + mn) / 2, raw, rgb))
            elif raw.lower().startswith(('rgb(', 'rgba(')):
                rgb = parse_rgb_func(m.group(1))
                if rgb is None:
                    continue
                h, mx, mn = rgb_to_hue_lights(*rgb)
                out.append(('rgb', h, (mx + mn) / 2, raw, rgb))
            elif raw.lower().startswith(('hsl(', 'hsla(')):
                r = parse_hsl_func(m.group(2))
                if r:
                    out.append(('hsl', r[0], r[1], raw, None))
            elif raw.lower().startswith('oklch('):
                r = parse_oklch_func(m.group(3))
                if r:
                    out.append(('oklch', r[0], r[1], raw, None))
        except (ValueError, IndexError):
            continue
    return out

def line_of(text, pos):
    return text.count('\n', 0, pos) + 1

# ---------- 检测器 ----------

PLACEHOLDER_RE = re.compile(
    r'(unsplash\.com|picsum\.photos|placehold\.|via\.placeholder|lorem\.space'
    r'|dummyimage\.com|placekitten\.com|loremflickr\.com)', re.I)

EMOJI_RANGES = [
    (0x1F300, 0x1FAFF),
    (0x2600, 0x26FF),
    (0x2700, 0x27BF),
    (0x2B00, 0x2BFF),
    (0x2300, 0x23FF),
    (0xFE00, 0xFE0F),
]

DEFAULT_FONTS_RE = re.compile(
    r"font-family[^;}]*\b(Inter|Roboto|Arial|Open Sans|Helvetica Neue)\b", re.I)

def color_alpha(raw):
    """从色值文本解析 alpha；无 alpha 通道（hex/rgb/hsl 无第四参）返回 1.0。"""
    m = re.match(r'(?:rgba?|hsla?)\(([^)]*)\)', raw, re.I)
    if not m:
        m = re.match(r'oklch\(([^)]*)\)', raw, re.I)
        if m and '/' in m.group(1):
            a = m.group(1).split('/')[-1].strip()
        else:
            return 1.0
    else:
        parts = re.split(r'[\s,/]+', m.group(1).strip())
        if len(parts) < 4:
            return 1.0
        a = parts[3]
    try:
        return float(a.rstrip('%')) / (100 if a.endswith('%') else 1)
    except ValueError:
        return 1.0

def gradient_is_ambient(text, start, grad_text, colors):
    """背景氛围启发式：background 声明中各色标 alpha<0.4 或 light>0.9。
    仅决定扫描信号级别，不证明视觉权重、对比度或设计适用性。"""
    # 向前定位当前声明起点（; { } 之一），而非固定窗口——多行 background-image
    # 声明中可能夹有超长 data-URI，固定窗口会误判
    seg_start = max(text.rfind(';', 0, start), text.rfind('{', 0, start),
                    text.rfind('}', 0, start)) + 1
    prefix = text[seg_start:start].lower()
    if 'background' not in prefix:
        return False
    return all(color_alpha(raw) < 0.4 or light > 0.9
               for kind, h, light, raw, rgb in colors)

def gradient_spans(text):
    """保留颜色函数中的嵌套括号，避免首个 rgb()/oklch() 截断后续色标。"""
    for m in re.finditer(r'(?:linear|radial|conic)-gradient\(', text, re.I):
        depth = 1
        for end in range(m.end(), len(text)):
            if text[end] == '(':
                depth += 1
            elif text[end] == ')':
                depth -= 1
                if depth == 0:
                    yield m.start(), text[m.start():end + 1]
                    break


def check_gradient_hue(text, findings, whitelist=frozenset()):
    for start, gradient in gradient_spans(text):
        colors = extract_colors(gradient)
        ambient = gradient_is_ambient(text, start, gradient, colors)
        for kind, h, light, raw, rgb in colors:
            if 240 <= h <= 290:
                if norm_color(raw) in whitelist:
                    continue  # 已声明色值过滤此信号；不代表用户授权或设计结论
                if ambient:
                    findings.append(('CHECK', 'P0-1*', line_of(text, start),
                                     f'背景氛围层紫渐变 {raw}（hue {h:.0f}°，低透明或极浅）——结合用途与实际呈现核对'))
                else:
                    findings.append(('AUTO', 'P0-1', line_of(text, start),
                                     f'紫/蓝紫渐变色标 {raw}（hue {h:.0f}°）'))

def check_placeholder_urls(text, findings):
    for m in PLACEHOLDER_RE.finditer(text):
        findings.append(('AUTO', '占位', line_of(text, m.start()),
                         f'图片服务/占位域名：{m.group(0)}（需确认实际用途）'))

def check_bare_outline(text, findings):
    m = re.search(r'outline\s*:\s*(none|0)\b', text, re.I)
    if m and ':focus-visible' not in text and 'focus-visible' not in text:
        findings.append(('AUTO', '焦点', line_of(text, m.start()),
                         'outline:none/0 且该文件无 focus-visible 字样；需核对其他焦点样式'))

def check_emoji(text, findings):
    in_tag = False
    for i, c in enumerate(text):
        if c == '<':
            in_tag = True
        elif c == '>':
            in_tag = False
        elif not in_tag:
            o = ord(c)
            if any(a <= o <= b for a, b in EMOJI_RANGES):
                findings.append(('CHECK', 'P0-2', line_of(text, i),
                                 f'emoji {c}（U+{o:04X}）——核对内容/图标用途和可访问名称'))

def check_responsive(text, findings, fname):
    if not fname.endswith(('.html', '.htm')):
        return
    head = text[:2048].lower()
    if '<!doctype' not in head and '<html' not in head:
        return  # HTML 片段（被嵌入的组件/figure），不做整页响应式判定
    if 'viewport' not in text:
        findings.append(('CHECK', 'P0-6', 1, '无 viewport meta'))
    if '@media' not in text and 'clamp(' not in text and 'auto-fit' not in text:
        findings.append(('CHECK', 'P0-6', 1,
                         '全文无 @media/clamp/auto-fit，疑似无响应式'))

def check_external_assets(text, findings):
    for m in re.finditer(r'(?:src|href)\s*=\s*["\'](https?://[^"\']+\.(?:png|jpe?g|gif|webp|svg|woff2?|ttf))[^"\']*["\']', text, re.I):
        findings.append(('CHECK', 'P0-7', line_of(text, m.start()),
                         f'外部资源需验证可达：{m.group(1)[:80]}'))

def check_default_fonts(text, findings, family_tokens=frozenset()):
    seen = set()
    for m in DEFAULT_FONTS_RE.finditer(text):
        name = m.group(1)
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        if any(name.lower() in ft for ft in family_tokens):
            continue  # waiver：字体已被项目 font token 声明
        findings.append(('CHECK', 'P1-12', line_of(text, m.start()),
                         f'默认字体 {name}——结合字体角色、页面用途和项目规范核对'))

def check_palette_pairs(text, findings, whitelist=frozenset()):
    """奶油底+赤陶橙 / 近黑底+酸性绿：基于全文颜色共现的弱信号，CHECK 级。
    参与判定的色值全部已声明时过滤此信号，不据此作审美或质量判断。"""
    colors = extract_colors(text)
    warm_vals, terracotta_vals, dark_vals, acid_vals = [], [], [], []
    for kind, h, light, raw, rgb in colors:
        if rgb is not None:
            r, g, b = rgb
            if r > 0.93 and g > 0.90 and b > 0.85 and r >= g > b and 0.02 <= r - b <= 0.12:
                warm_vals.append(norm_color(raw))
            if r < 0.15 and g < 0.15 and b < 0.15:
                dark_vals.append(norm_color(raw))
        if 40 <= h <= 55 and light < 0.75:
            terracotta_vals.append(norm_color(raw))
        if (100 <= h <= 140 or 15 <= h <= 35) and light > 0.35:
            acid_vals.append(norm_color(raw))
    if warm_vals and terracotta_vals:
        if not all(v in whitelist for v in warm_vals + terracotta_vals):
            findings.append(('CHECK', 'P1-8', 1,
                             '疑似奶油底+赤陶橙配色对（Claude 默认审美）——人工确认背景与强调色'))
    if dark_vals and acid_vals:
        if not all(v in whitelist for v in dark_vals + acid_vals):
            findings.append(('CHECK', 'P1-9', 1,
                             '疑似近黑底+酸性绿/朱红配色对——人工确认是否为唯一强调色'))

# ---------- token 漂移检测 ----------

VAR_DEF_RE = re.compile(r'(--[\w-]+)\s*:\s*([^;}]+)')
FONT_SIZE_RE = re.compile(r'font-size\s*:\s*([0-9.]+(?:px|rem|em))', re.I)
FONT_VALUE_RE = re.compile(r'[0-9.]+(?:px|rem|em)')

def norm_color(raw):
    raw = raw.strip().lower()
    if raw.startswith('#'):
        rgb = parse_hex(raw)
        if rgb:
            return '#%02x%02x%02x' % tuple(round(c * 255) for c in rgb)
        return raw
    return re.sub(r'\s+', '', raw)

DATA_URI_RE = re.compile(r'url\(["\']?data:[^)]*\)?', re.I)
DECOR_DECL_RE = re.compile(r'(?:background(?:-image)?|box-shadow)\s*:[^;}]*', re.I)

def collect_exempt_spans(text):
    """豁免区间：data-URI 内容（图标 SVG 的内部色值）与装饰性声明（渐变/阴影）。"""
    spans = [m.span() for m in DATA_URI_RE.finditer(text)]
    spans.extend(m.span() for m in DECOR_DECL_RE.finditer(text))
    return spans

def harvest_tokens(text, color_tokens, font_tokens, family_tokens=None):
    """从非注释文本收集 token；等长去注释保留主文本定义区 span。"""
    text = strip_comments(text)
    spans = []
    for m in VAR_DEF_RE.finditer(text):
        spans.append((m.start(), m.end()))
        name, val = m.group(1), m.group(2).strip()
        if COLOR_RE.fullmatch(val):
            color_tokens.setdefault(norm_color(val), name)
        elif FONT_VALUE_RE.fullmatch(val) and re.search(r'text|font|size', name, re.I):
            try:
                num = float(re.match(r'[0-9.]+', val).group(0))
            except (ValueError, AttributeError):
                continue
            if val.endswith('px') and not (8 <= num <= 96):
                continue  # 布局尺寸（如 150px 宽）不属字号梯度
            font_tokens.setdefault(val, name)
        elif family_tokens is not None and re.search(r'font|family', name, re.I):
            family_tokens.add(val.lower())
    return spans

def check_token_drift(text, findings, extra_tokens=None):
    color_tokens, font_tokens = {}, {}
    if extra_tokens:
        harvest_tokens(extra_tokens, color_tokens, font_tokens)
    def_spans = harvest_tokens(text, color_tokens, font_tokens)
    color_active = len(color_tokens) >= 3 or (extra_tokens and color_tokens)
    font_active = len(font_tokens) >= 2 or (extra_tokens and font_tokens)
    if not (color_active or font_active):
        return

    exempt_spans = collect_exempt_spans(text)

    def in_def(pos):
        return any(s <= pos < e for s, e in def_spans)

    def exempt(pos):
        return any(s <= pos < e for s, e in exempt_spans)

    if color_active:
        for m in COLOR_RE.finditer(text):
            if in_def(m.start()) or exempt(m.start()):
                continue
            v, ln = norm_color(m.group(0)), line_of(text, m.start())
            if v in color_tokens:
                findings.append(('CHECK', 'D3-漂移', ln,
                                 f'硬编码颜色 {m.group(0)} 有对应 token {color_tokens[v]}，建议 var() 引用'))
            else:
                findings.append(('CHECK', 'D3-漂移', ln,
                                 f'硬编码颜色 {m.group(0)} 不在 token 白名单（共 {len(color_tokens)} 个颜色 token）'))
    if font_active:
        for m in FONT_SIZE_RE.finditer(text):
            if in_def(m.start()):
                continue
            v, ln = m.group(1), line_of(text, m.start())
            if v in font_tokens:
                findings.append(('CHECK', 'D3-漂移', ln,
                                 f'font-size {v} 有对应 token {font_tokens[v]}，建议 var() 引用'))
            else:
                findings.append(('CHECK', 'D3-漂移', ln,
                                 f'font-size {v} 不在 token 字号梯度（{", ".join(sorted(font_tokens))}）'))

# ---------- 主流程 ----------

CHECKS_WITH_TEXT = [
    check_placeholder_urls, check_bare_outline, check_emoji,
]

def strip_comments(text):
    """剥离 CSS /* */ 与 HTML <!-- --> 注释，等长替换（保换行）以维持行号。"""
    def repl(m):
        return ''.join('\n' if c == '\n' else ' ' for c in m.group(0))
    text = re.sub(r'/\*.*?\*/', repl, text, flags=re.DOTALL)
    return re.sub(r'<!--.*?-->', repl, text, flags=re.DOTALL)

def read_scan_text(path):
    """目标与外部 tokens 共用的读取边界；失败交由调用者报告。"""
    with open(path, encoding='utf-8-sig') as f:
        text = f.read()
    if '\x00' in text:
        raise UnicodeError('包含 NUL；仅支持不含 NUL 的 UTF-8 文本')
    return text

def lint_file(path, extra_tokens=None):
    try:
        text = read_scan_text(path)
    except (OSError, UnicodeError) as e:
        return [('CHECK', 'IO', 0, f'无法读取 UTF-8 文本 {path}：{e}')]
    text = strip_comments(text)
    # waiver 白名单：被审文件自身 token + --tokens 外部声明
    color_tokens, font_tokens, family_tokens = {}, {}, set()
    if extra_tokens:
        harvest_tokens(extra_tokens, color_tokens, font_tokens, family_tokens)
    harvest_tokens(text, color_tokens, font_tokens, family_tokens)
    whitelist = set(color_tokens)

    findings = []
    for fn in CHECKS_WITH_TEXT:
        fn(text, findings)
    check_gradient_hue(text, findings, whitelist)
    check_default_fonts(text, findings, family_tokens)
    check_palette_pairs(text, findings, whitelist)
    check_responsive(text, findings, path)
    check_external_assets(text, findings)
    check_token_drift(text, findings, extra_tokens)
    return findings

def main(argv):
    args = list(argv[1:])
    tokens_file = None
    if '--tokens' in args:
        i = args.index('--tokens')
        if i + 1 >= len(args):
            print(__doc__)
            return 2
        tokens_file = args[i + 1]
        del args[i:i + 2]
    if len(args) != 1:
        print(__doc__)
        return 2
    extra_tokens = None
    if tokens_file:
        try:
            extra_tokens = read_scan_text(tokens_file)
        except (OSError, UnicodeError) as e:
            print(f'无法读取 UTF-8 tokens 文件 {tokens_file}：{e}')
            return 2
    target = args[0]
    files = []
    read_errors = []
    if os.path.isdir(target):
        for root, _, names in os.walk(target, onerror=read_errors.append):
            for n in sorted(names):
                if n.endswith(('.html', '.htm', '.css')):
                    files.append(os.path.join(root, n))
    else:
        files.append(target)

    for error in read_errors:
        print(f'无法遍历目录：{error}')
    if not files:
        print('未找到可检查的 .html/.htm/.css 文件；扫描未完成')
        return 2

    auto_n = check_n = io_n = 0
    for path in files:
        findings = lint_file(path, extra_tokens)
        if not findings:
            continue
        print(f'\n{path}')
        for level, rule, line, msg in sorted(findings, key=lambda x: (x[0] != 'AUTO', x[2])):
            if rule == 'IO':
                io_n += 1
            tag = '[AUTO] ' if level == 'AUTO' else '[CHECK]'
            print(f'  {tag} {rule:>5}  L{line:<5} {msg}')
            if level == 'AUTO':
                auto_n += 1
            else:
                check_n += 1
    print(f'\n---\n[AUTO] 文本模式命中 {auto_n} 项（需结合语境核对）')
    print(f'[CHECK] 待人工判断 {check_n} 项（定位辅助）')
    print('扫描信号不代表设计通过或失败；历史规则 ID 不等于问题严重程度')
    if io_n or read_errors:
        print('读取失败，扫描未完成；不能将其余结果视为完整检查通过')
        return 2
    return 1 if auto_n else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
