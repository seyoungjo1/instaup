#!/usr/bin/env python3
"""실제 Bambu Studio(명령줄)로 3MF 를 열고 슬라이스해서 '프로젝트로 열리는지' 검증한다. GitHub Actions(.github/workflows/bambu-verify.yml)에서 돈다.
  python tools/bambu_cli.py --download --files a_bambu.3mf b.3mf --out bambu_out [--summary $GITHUB_STEP_SUMMARY] [--expect-project a_bambu.3mf]
방법(Bambu Studio 위키 Command-Line-Usage): `bambu-studio --slice 0 --debug 2 --export-3mf out.3mf in.3mf` — 설정 파일을 주지 않으면 3MF 안의 설정으로 슬라이스한다.
판정: 종료 코드 0 + 결과 3MF 에 G-code + G-code 머리말 설정이 3MF 의 project_settings 와 일치(printer_model, elefant_foot_compensation, enable_support, filament_colour …).
Bambu Studio 실행 파일: 환경변수 BAMBU_STUDIO, 없으면 --download 로 GitHub 최신 릴리스의 리눅스 AppImage 를 받아 풀어 쓴다(GH_TOKEN 있으면 API 한도 여유)."""
import os, sys, json, re, glob, shutil, subprocess, zipfile, argparse, urllib.request, time
KEYS = ['printer_model', 'nozzle_diameter', 'layer_height', 'elefant_foot_compensation', 'enable_support', 'support_on_build_plate_only', 'support_type', 'filament_colour', 'filament_settings_id', 'curr_bed_type']
def _api(url):
    req = urllib.request.Request(url, headers={'Accept': 'application/vnd.github+json', **({'Authorization': f'Bearer {os.environ["GH_TOKEN"]}'} if os.environ.get('GH_TOKEN') else {})})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())
def download(dest='bambu_app'):
    run_ = os.path.abspath(os.path.join(dest, 'squashfs-root', 'AppRun'))
    if os.path.exists(run_): return run_, '(이미 받음)', os.path.basename(next(iter(glob.glob(os.path.join(dest, '*.AppImage'))), 'AppImage'))   # 같은 작업 안 두 번째 단계는 다시 받지 않는다
    rel = _api('https://api.github.com/repos/bambulab/BambuStudio/releases/latest'); assets = rel.get('assets', [])
    pick = None
    for pat in [r'ubuntu.*24\.04.*\.AppImage$', r'linux.*24\.04.*\.AppImage$', r'ubuntu.*\.AppImage$', r'linux.*\.AppImage$', r'\.AppImage$']:
        c = [a for a in assets if re.search(pat, a['name'], re.I)]
        if c: pick = c[0]; break
    if not pick: raise SystemExit(f'AppImage 없음: {[a["name"] for a in assets]}')
    os.makedirs(dest, exist_ok=True); app = os.path.join(dest, pick['name'])
    print(f'다운로드 {rel["tag_name"]} {pick["name"]} ({pick["size"] // 1_000_000} MB)', flush=True)
    urllib.request.urlretrieve(pick['browser_download_url'], app); os.chmod(app, 0o755)
    subprocess.run([os.path.abspath(app), '--appimage-extract'], cwd=dest, check=True, stdout=subprocess.DEVNULL)
    return os.path.abspath(os.path.join(dest, 'squashfs-root', 'AppRun')), rel['tag_name'], pick['name']
def gcode_settings(gc):
    out = {}
    for k in KEYS:
        m = re.search(rf'^; {re.escape(k)} = (.*)$', gc, re.M)
        if m: out[k] = m.group(1).strip()
    return out
def project_settings(path):
    try: ps = json.loads(zipfile.ZipFile(path).read('Metadata/project_settings.config'))
    except Exception: return None
    return {k: (';'.join(ps[k]) if isinstance(ps.get(k), list) else ps.get(k)) for k in KEYS if k in ps}
def _hms(t):
    """'1h 2m 3s' · '25m 4s' · '1d 2h 3m' → 초"""
    u = {'d': 86400, 'h': 3600, 'm': 60, 's': 1}; return sum(int(n) * u[k] for n, k in re.findall(r'(\d+)\s*([dhms])', t))
def print_stats(gc, sliced=None):
    """슬라이스 결과의 예상 출력 시간(초)·필라멘트(g, mm). G-code 머리말 '; model printing time: … ; total estimated time: …', '; total filament weight [g] : …'
    없으면 sliced 3MF 의 Metadata/slice_info.config(prediction·weight)."""
    r = {}
    m = re.search(r'model printing time:\s*([^;\n]+)', gc)
    if m: r['model_s'] = _hms(m.group(1))
    m = re.search(r'total estimated time:\s*([^;\n]+)', gc)
    if m: r['total_s'] = _hms(m.group(1))
    m = re.search(r'total filament weight \[g\]\s*:\s*([\d.,]+)', gc) or re.search(r'filament used \[g\]\s*=\s*([\d.,]+)', gc)
    if m: r['filament_g'] = round(sum(float(x) for x in m.group(1).split(',') if x), 2)
    m = re.search(r'filament used \[mm\]\s*=\s*([\d.,]+)', gc) or re.search(r'total filament length \[mm\]\s*:\s*([\d.,]+)', gc)
    if m: r['filament_mm'] = round(sum(float(x) for x in m.group(1).split(',') if x), 1)
    if sliced and ('total_s' not in r or 'filament_g' not in r):
        try:
            si = zipfile.ZipFile(sliced).read('Metadata/slice_info.config').decode('utf-8', 'ignore')
            m = re.search(r'key="prediction" value="(\d+)"', si); r.setdefault('total_s', int(m.group(1))) if m else None
            m = re.search(r'key="weight" value="([\d.]+)"', si); r.setdefault('filament_g', float(m.group(1))) if m else None
        except Exception: pass
    return r
def feature_stats(gc, zr=None):
    """G-code 를 ;TYPE: 종류별로 나눠 압출 이동 길이(mm)·이동 수·명목 시간(길이/F, 가감속 무시) 합산. 이동(travel)은 'travel'. zr=(z0, z1) 이면 그 높이만.
    출력 시간 차이가 어느 종류에서 났는지 보려는 것(예: 좁은 덩어리의 틈 메움)."""
    st = {}; t = 'start'; x = y = z = 0.0; e_abs = False; f = 3000.0
    for ln in gc.splitlines():
        if ln.startswith(';TYPE:'): t = ln[6:].strip(); continue
        if ln.startswith('M82'): e_abs = True
        if ln.startswith('M83'): e_abs = False
        if not (ln.startswith('G1 ') or ln.startswith('G0 ') or ln.startswith('G2 ') or ln.startswith('G3 ')): continue
        w = dict((tok[0], tok[1:]) for tok in ln.split(';')[0].split()[1:] if tok and tok[0] in 'XYZEF')
        try:
            nx, ny, nz = float(w.get('X', x)), float(w.get('Y', y)), float(w.get('Z', z))
            if 'F' in w: f = float(w['F'])
            ext = 'E' in w and float(w['E']) > 0 and not e_abs
        except ValueError: continue
        d = ((nx - x) ** 2 + (ny - y) ** 2) ** 0.5; x, y, z = nx, ny, nz
        if d <= 0 or (zr and not (zr[0] <= z <= zr[1])): continue
        k = t if ext else 'travel'; a = st.setdefault(k, [0.0, 0, 0.0]); a[0] += d; a[1] += 1; a[2] += d / (f / 60.0)
    return {k: {'mm': round(v[0]), 'moves': v[1], 's': round(v[2])} for k, v in sorted(st.items(), key=lambda kv: -kv[1][2])}
def tool_changes(gc):
    """G-code 의 필라멘트 교체 [(층 z, 필라멘트 번호 1부터)]: '; Z_HEIGHT: z'(Bambu 층 머리말)로 높이를 따라가며 'T<n>' 줄(n < 255)이 바뀌는 곳."""
    z = 0.0; cur = None; out = []
    for ln in gc.splitlines():
        if ln.startswith('; Z_HEIGHT:'):
            try: z = float(ln.split(':', 1)[1])
            except ValueError: pass
        m = re.match(r'^T(\d+)\s*(;.*)?$', ln)
        if m and int(m.group(1)) < 255:
            t = int(m.group(1)) + 1
            if cur is not None and t != cur: out.append((round(z, 3), t))
            cur = t
    return out
def swap_check(path, changes):
    """fpaint 3MF 옆 *.swaps.json(예상 교체: top_z, extruder)과 G-code 교체를 대조. 없으면 None."""
    sw = os.path.splitext(path)[0] + '.swaps.json'
    if not os.path.exists(sw): return None
    want = [(round(c['top_z'], 3), int(c['extruder'])) for c in json.load(open(sw, encoding='utf-8'))['changes']]
    got = [(z, t) for z, t in changes]
    ok = len(want) == len(got) and all(abs(a[0] - b[0]) < 0.011 and a[1] == b[1] for a, b in zip(want, got))
    return {'want': want, 'got': got, 'ok': ok}
fmt_s = lambda s: f"{s // 3600}h {s % 3600 // 60}m {s % 60}s" if s else '-'
def slice_one(exe, path, outdir, timeout=1200):
    os.makedirs(outdir, exist_ok=True); name = os.path.splitext(os.path.basename(path))[0]; out3 = os.path.join(os.path.abspath(outdir), f'{name}_sliced.3mf')
    cmd = ([shutil.which('xvfb-run'), '-a'] if shutil.which('xvfb-run') else []) + [exe, '--slice', '0', '--debug', '2', '--export-3mf', out3, os.path.abspath(path)]
    t = time.time()
    try: p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as e:                                            # 한 파일이 멈춰도 나머지는 검증한다(CI 134: 램프 슬라이스 1200 s 초과로 전체 중단)
        return {'file': path, 'exit': 'timeout', 'seconds': timeout, 'sliced_3mf': False, 'gcode_settings': {}, 'stats': {}, 'features': {}, 'project_settings': None,
                'tool_changes': [], 'swap_check': None, 'warn_lines': [f'시간 초과 {timeout} s'], 'ok': False}
    log = p.stdout + '\n' + p.stderr; open(os.path.join(outdir, f'{name}.log'), 'w').write(log)
    r = {'file': path, 'exit': p.returncode, 'seconds': round(time.time() - t), 'sliced_3mf': os.path.exists(out3)}
    gc = ''
    if r['sliced_3mf']:
        z = zipfile.ZipFile(out3); gn = [n for n in z.namelist() if n.endswith('.gcode')]; r['gcode_files'] = gn
        if gn: gc = z.read(gn[0]).decode('utf-8', 'ignore'); open(os.path.join(outdir, f'{name}.gcode'), 'w').write(gc)
    r['gcode_settings'] = gcode_settings(gc) if gc else {}
    r['stats'] = print_stats(gc, out3 if r['sliced_3mf'] else None)
    r['features'] = feature_stats(gc) if gc else {}
    want = project_settings(path); r['project_settings'] = want
    if want and r['gcode_settings']:
        norm = lambda v: re.sub(r'[\s,;]+', ';', str(v).replace('"', '')).strip(';').lower()   # G-code 머리말은 문자열 항목에 따옴표를 붙인다
        r['settings_match'] = {k: norm(want[k]) == norm(r['gcode_settings'].get(k, '')) for k in want if k in r['gcode_settings']}
    r['tool_changes'] = tool_changes(gc) if gc else []; r['swap_check'] = swap_check(path, r['tool_changes'])
    r['warn_lines'] = [l for l in log.splitlines() if re.search(r'not from bambu|load geometry|error|failed', l, re.I)][:12]
    r['ok'] = p.returncode == 0 and bool(gc) and (not want or all(r.get('settings_match', {}).values()))
    if r['swap_check'] is not None: r['ok'] = r['ok'] and r['swap_check']['ok']        # 필라멘트 페인팅: 교체 높이·번호가 계획대로
    return r
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--files', nargs='+', required=True); ap.add_argument('--out', default='bambu_out'); ap.add_argument('--download', action='store_true')
    ap.add_argument('--summary'); ap.add_argument('--expect-project', nargs='*', default=None, help='프로젝트로 열려야 하는 파일(기본: 이름에 _bambu 가 들어간 것)')
    a = ap.parse_args(); files = [f for pat in a.files for f in sorted(glob.glob(pat))] or a.files
    exe = os.environ.get('BAMBU_STUDIO'); tag = asset = '(환경변수)'
    if not exe:
        if not a.download: raise SystemExit('BAMBU_STUDIO 환경변수 또는 --download 필요')
        exe, tag, asset = download()
    must = set(a.expect_project) if a.expect_project is not None else {f for f in files if '_bambu' in os.path.basename(f)}
    res = [slice_one(exe, f, a.out) for f in files]
    L = [f'## Bambu Studio 실제 열기·슬라이스 검증 ({tag}, {asset})', '', '| 파일 | 프로젝트여야 함 | 종료 코드 | G-code | 설정 일치(3MF→G-code) | 예상 출력 시간 | 필라멘트 g | 판정 |', '|---|---|---|---|---|---|---|---|']
    bad = []
    for r in res:
        m = r.get('settings_match', {}); mm = f"{sum(m.values())}/{len(m)}" if m else '-'
        need = r['file'] in must; verdict = '✓ 프로젝트로 슬라이스' if r['ok'] else ('⚠ 실패' if need else 'ℹ (비교용) ' + ('슬라이스됨' if r.get('gcode_files') else '실패'))
        if need and not r['ok']: bad.append(r['file'])
        st = r.get('stats', {})
        L.append(f"| {os.path.basename(r['file'])} | {'예' if need else '아니오'} | {r['exit']} | {'있음' if r.get('gcode_files') else '없음'} | {mm} | {fmt_s(st.get('total_s'))} | {st.get('filament_g', '-')} | {verdict} |")
    for r in res:
        if r.get('swap_check') is not None:
            sc = r['swap_check']; L += ['', f"### 필라멘트 교체(계획 ↔ G-code) — {os.path.basename(r['file'])}: {'✓ 일치' if sc['ok'] else '⚠ 불일치'}", '', '| 계획 z | 계획 번호 | G-code z | G-code 번호 |', '|---|---|---|---|']
            for i in range(max(len(sc['want']), len(sc['got']))):
                a = sc['want'][i] if i < len(sc['want']) else ('-', '-'); b = sc['got'][i] if i < len(sc['got']) else ('-', '-'); L.append(f'| {a[0]} | {a[1]} | {b[0]} | {b[1]} |')
    L += [''] + [f"- {os.path.basename(r['file'])}: 불일치 키 {[k for k, v in r.get('settings_match', {}).items() if not v]} · G-code 설정 {r['gcode_settings']} / 경고 줄 {r['warn_lines'][:4]}" for r in res]
    for r in res:
        if r.get('features'):
            L += ['', f"### 종류별 이동(명목 시간 = 길이/F, 가감속 무시) — {os.path.basename(r['file'])}", '', '| 종류 | 길이 mm | 이동 수 | 명목 시간 |', '|---|---|---|---|']
            L += [f"| {k} | {v['mm']} | {v['moves']} | {fmt_s(v['s'])} |" for k, v in list(r['features'].items())[:12]]
    txt = '\n'.join(L); print(txt); json.dump(res, open(os.path.join(a.out, 'result.json'), 'w'), ensure_ascii=False, indent=1)
    if a.summary: open(a.summary, 'a').write(txt + '\n')
    sys.exit(1 if bad else 0)
if __name__ == '__main__': main()
