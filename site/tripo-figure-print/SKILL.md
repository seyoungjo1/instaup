---
name: tripo-figure-print
description: 사진 몇 장만으로 어떤 캐릭터·피규어든 FDM 3D 출력 키트로 만든다 — Tripo banana_pro 네 방향 그림 → Tripo H3.1 3D → Blender 정리(닫힌 한 몸) → 분할 구조(꺾임선 이음매, 조각마다 평평한 출력 바닥, 숨은 안쪽은 평면, 속 기능 밑 45° 텐트, 긴 팔다리 두 조각, 몸통 바닥 평면, 육각 돌기 결합) → 검사(겹침·빼기·접지·오버행·보이는 틈) → 색깔별 플레이트. 분할 방법은 Chopper·피라미드 분해·높이 지도 분해·골격 분할 논문, Bambu/Prusa Cut·snapsplit, MakerWorld 색깔별 키트를 벤치마킹했다. "이 사진으로 피규어 만들어", "트리포로 만들어", "AI 3D 피규어 출력", "캐릭터 키트", "피규어 파츠 나눠", "AI 모델 분할", "Tripo 후가공" 같은 요청이면 이름을 말하지 않아도 쓴다.
---

# 사진 → Tripo 피규어 → 출력용 분할 키트

누가 하든 같은 결과가 나오게 쓴 실행 지침서다. 필요한 코드는 맨 아래 **부록 A~E** 에 다 들어 있다(파일로 저장해 쓴다).

## 0. 준비물 — 없으면 먼저 사용자에게 묻는다

1. **Tripo 구독(크레딧)과 API 키.** Tripo Studio 를 구독해 크레딧을 받고, Tripo 플랫폼(API) 페이지에서 API 키를 만든다.
   - 시작할 때 `TRIPO_API_KEY` 환경 변수가 있는지 먼저 확인한다(`python -c "import os;print(bool(os.environ.get('TRIPO_API_KEY')))"`).
   - **없으면 진행하지 말고 사용자에게 묻는다**: "Tripo API 키가 필요합니다. Tripo Studio 구독(크레딧) 후 API 키를 만들어, 터미널에서 `export TRIPO_API_KEY=...` 로 넣어 주세요. 키는 채팅에 붙여 넣지 마세요."
   - 사용자가 키를 채팅에 붙여 넣으면 그대로 다시 보여 주거나 파일·코드·기록에 쓰지 않는다. 환경 변수로 넣도록 다시 안내한다.
   - 부록 A 의 스크립트도 키가 없으면 이 안내를 내고 멈춘다.
2. 파이썬: `pip install numpy scipy trimesh manifold3d shapely mapbox_earcut scikit-image pillow`, Blender 정리용 `pip install bpy`(파이썬 버전에 맞는 bpy).
3. 사진: 피규어·캐릭터의 앞모습 사진 1장 이상(가능하면 공식 그림 1장 — 등·옆처럼 사진에 안 보이는 면을 지어내지 않게).

## 1. 지킬 것
- **크레딧이 드는 호출은 매번 사용자 허락 뒤에만.** 묻기 전에 '무엇을·몇 크레딧·왜' 를 표로 보인다. "해 봐" 같은 말은 허락이 아니다. 허락받은 크레딧만 `--approved-credits` 로 넘기고, 모자라면 스크립트가 계획만 내고 멈춘다. 쓴 크레딧·task id 를 보고에 적는다.
- **분할은 직접 한다**(AI 부위 분할을 쓰지 않음 — 막음면·공차·출력 방향을 제어할 수 없다).
- **원래 형상을 살린다.** 후가공은 문제 자리만 조금. 눈·얼굴을 새로 그려 넣지 않는다.
- 무거운 계산(분할·리메시·불리언)은 한 번에 하나씩(메모리).
- 서명 URL·키를 기록에 남기지 않는다(부록 A 가 지움).

## 2. 접수 — 사진만 받았을 때 정할 것
| 항목 | 기본값 | 왜 |
|---|---|---|
| 이름 | 사진에서 추정 | 그림 프롬프트 `--subject` |
| 높이 | 180 mm | Blender 정리 `--height` |
| 색 수 | 사진의 큰 색 영역 수(보통 4~6) | 조각·플레이트 수 |
| 출력 방식 | 색깔별 끼움 키트(AMS 없이도 됨) | 분할 구조 |
| 공식 그림 | 없으면 사진만 | 안 보이는 면 |
| 기능(물·조명·관절) | 없음 | 속 보호 구역 |

크레딧 표(2026-11 기준, 바뀔 수 있음):
| 단계 | 크레딧 |
|---|---|
| 네 방향 그림(banana_pro 2K) | 15/장 — 대칭이면 3장 + 거울 = 45, 아니면 60 |
| 3D H3.1(detailed + 텍스처) | 60 |
| 처음 한 벌 합계 | **105~120** |

## 3. 네 방향 그림 → 확인 → H3.1
```
python tripo_v3.py views front_photo.jpg --out nb --subject "<캐릭터>" [--ref official.png] --views front,left,back --approved-credits 45
python tripo_v3.py mirror nb/left.png nb/right.png          # 좌우 대칭이면 0 크레딧
python tripo_v3.py multiview nb --out model --approved-credits 60
```
- 사진 한 장으로 바로 3D 를 만들면 안 보이는 면을 지어낸다 → 네 방향을 먼저.
- 앞은 사진만 넣는다(설명을 섞으면 등 쪽을 그린다). 옆은 정확한 90° 옆, 뒤는 카메라 바로 뒤(코드에 있음). 고유 설명은 `--notes`.
- **네 장을 사용자에게 보여 확인받고** 3D 로 간다. 한 장이 틀리면 그 장만 다시(15, 다시 허락).
- H3.1 은 `delight: true`(텍스처의 구운 그늘 제거 — 색을 나눌 때 그늘이 검정 얼룩이 되지 않게).

## 4. Blender 정리 — 닫힌 한 몸
```
python bl_clean.py model_model.glb fig --height 180 --rot -90 --voxel 0.3 --faces 600000     # → fig.npz (V, F, C)
```
크기·방향(앞 −y, 위 +z 가 되게 `--rot`)·**복셀 리메시**(불리언 전에 꼭 닫힌 한 몸)·텍스처 색 → 정점 색. 이 메시가 이후 모든 비교(보이는 틈 검사)의 원본이다. 렌더해서 사용자에게 보인다.

## 5. 분할 구조 — 핵심

### 5.1 원칙(남들의 방법에서 가져옴)
1. **이음매 = 형상의 꺾임선 = 색 경계.** 판 사이 줄·모서리·고리처럼 오목한 곳에 두면 틈이 안 보인다(Chopper: 이음매가 안 띄게). 몸을 가로지르는 평면 컷은 곧은 이음매가 보여서 피한다. 긴 팔의 두 번째 컷만 예외다.
2. **조각마다 평평한 출력 바닥(베드)**, 접지 ≥ 100 mm². 출력 방향을 먼저 정하고 그에 맞게 자른다(피라미드 분해: 평평한 바닥 + 그 위 높이 함수 = 서포트 없음).
3. **숨은 안쪽 면은 평면.** 겉면을 옮긴 곡면으로 안쪽을 만들면 베드에 못 놓고(접지 0.1~3 mm²) 브리지 수천 mm² 가 생긴다.
4. **판 모양 조각은 빼는 방향 기둥으로**(높이 지도 분해) → 그 방향으로 빼면 안 걸리고, 끼우는 방향이 정해진다.
5. **공차는 핀 구멍(+0.2/쪽, 깊이 +0.6)과 숨은 바닥(0.15)에만**, 겉 이음매는 0(snapsplit PLA 값). 슬라이서 Cut 연결부는 공차 뜻이 슬라이서마다 다르고 스냅은 기본값으로 잘 안 맞아, 메시에 직접 넣는다.
6. **조각 수는 적게** — 색 수만큼 + 출력 방향 때문에 꼭 필요한 컷만. 색깔별 플레이트로 모은다(MakerWorld 'No AMS' 키트 방식).

### 5.2 조각 모양별 결정표
| 모양 | 이음매 | 출력 베드 | 숨은 안쪽 | 결합 | 부록 함수 |
|---|---|---|---|---|---|
| 돌출 덩어리(머리·다리·짧은 팔·꼬리) | 꺾임 고리 | 고리 평면의 막음면(평평한 바닥 + 가파른 테두리) | — | 몸통 육각 돌기 → 조각 구멍(45° 뿔) | `separate_fill`, `hex_joint` |
| 긴 가지(앞으로 굽은 팔) | 꺾임 고리 + 축 수직 한 번 더 | 뿌리 조각 = 막음면, 끝 조각 = 자른 면 | — | 뿌리 윗면 육각 af8·L6 | `limb_split` |
| 판(등껍질·배·넓은 얼굴 판) | 색 경계 | LP 평면 바닥(두께 ≥ 3·부피 최소) | 기둥 ∩ 평면 위, 속 기능 밑 45° 텐트 | 평면 위 육각 af6·L3 × 3 | `plane_piece`, `plate_pegs` |
| 몸통 | — | 바닥 평면(단면 합 ≥ 150 mm²) | 나머지 | 다른 조각의 돌기 받침 | `flat_bottom` |
| 작은 색 부재(손발톱·눈) | 색 경계 | 평평한 뒷면 | — | 플러그 0.8 × 2.0, 홈 +0.2 | `separate_fill`(작은 조각) |

**긴 가지의 자르는 위치 s**: s = 0.4·0.45·0.5·0.55 에서 두 조각을 각자 베드에 놓고 `piece_report` 로 오버행·접지를 표로 재서 둘 다 낮은 s 를 고른다. 실측 예: 통팔 오버행 73 mm² → s 0.4 에서 19.5 / 2.6 mm². 두 조각 다 자른 면을 베드로 쓰면 핀을 따로 뽑아야 해서(접지 < 100 mm²) 피한다.

**판의 평면이 속 기능(물길·돌기) 위를 못 지날 때**(돔 모양): 그 기능을 보호 구역으로 주면 `plane_piece` 가 다음을 처리한다.
- 보호 구역 밑을 **45° 텐트 홈**으로 베드 쪽에서 판다(육각 구멍 45° 뿔과 같은 원리, 브리지 0).
- 텐트는 겉면 − 3 mm 아래로 누른다.
- 겉면 바로 밑(5 mm 안)까지 오는 칸은 관통 칸으로 둔다.
- 확인할 것: `tent_breaks_surface_mm2 = 0`.

### 5.3 순서 — 출력 방향 분할을 돌기·구멍보다 먼저(그래야 숙주를 틈 없는 원래 몸에서 정확히 다시 만든다)
1. **영역**: `regions(V, F, C, k)` — 꺾임(면마다 0.5 mm 안 법선 최대 각차 > 25°)으로 갈린 덩어리, 색 = 텍스처 다수결. 영역 그림·`patches`(색·넓이·중심)를 사용자에게 보여 준다.
2. **조각표**: 영역 → 조각 이름·모양 종류(§5.2)·베드·결합. 사용자 확인 뒤 `label_faces(F, patch, A, {영역: 이름})`.
3. **Separate+Fill**: `separate_fill(V, F, lab, order)` — 순서 머리 → 팔 → 돌출 → 꼬리 → 판 → 다리. 조각 = 영역 면(원본 그대로) + 막음면, 남은 몸 = 나머지 + 같은 막음면 → 겹침 0·틈 0. 확인: 조각마다 genus 0, 부피 합 = 원본.
4. **출력 방향 분할**:
   - 판: `body = merge_parts([숙주, 판])` → `plane_piece(body, SP, lab, d, others, protect)`. SP = 원본 겉면 표본, lab = 그 표본이 판이면 1, d = 판 겉면이 보이는 쪽.
   - 긴 가지: `limb_split(가지, 막음면 중심, s)`.
   - 몸통: `flat_bottom(몸통)`.
5. **결합**: 돌출 덩어리마다 `hex_joint(몸통, 조각, 막음면 중심, 막음면 법선, af, L)`. 크기는 막음면 단면 내접원 − 살 1.2(머리 af14·L10, 팔다리 af12·L10). 판은 `plate_pegs`.
6. **색 파트·작은 부재**: 같은 조각 안 AMS 색은 '그 색 면이 더 가깝다 ∩ 겉에서 1.2 mm 안' 으로 떼고, 작은 색 부재는 떼어 홈에 끼운다.
7. **출력 배치**: 조각마다 출력 위 방향(막음면·평면 바닥의 반대)을 +z 로 돌려 바닥 z=0, 색깔별로 플레이트에 모아 STL/3MF. 첫 층 코끼리발 보정은 슬라이서에서.

### 5.4 합격 기준(부록 E) — 조각마다 표로, 어긋나면 설계로 돌아간다
- 한 덩어리·닫힘, 삼각형 ≤ 200k(넘으면 Blender Decimate).
- 조각끼리 겹침 ≈ 0(`overlaps`). 빼는 방향 0.5~15 mm 걸림 ≈ 0(`pull_sweep`).
- 접지 ≥ 100 mm², 보이는 겉면 오버행 ≈ 0(`piece_report`). 서포트는 숨은 면에만.
- 판: 두께 ≥ 3, `lp_ok`, 텐트 뚫림 0.
- **보이는 틈**(`voids`, 원본 대비 > 0.12 mm): 의도한 것만 남아야 한다(포구 같은 구멍, 바닥 평면 자리).
- 조립·분리 렌더를 눈으로 확인 → 사용자에게 보여 준 뒤 출력 파일을 넘긴다.

## 6. 보고
결론 한 줄 → 조각별 표(부피·삼각형·접지·오버행·베드 방향) → 분할 검사(겹침·빼기·텐트·보이는 틈) → 렌더 → 조립 순서 → **쓴 크레딧·task id**. 수치 없는 "됩니다"는 쓰지 않는다.

## 7. 실패에서 배운 것
- 사진 한 장 → 뒤를 지어냄 → 네 방향 그림.
- 텍스처 밝기로 색 경계를 정함 → 그늘이 얼룩·사시. 경계는 꺾임선, 텍스처는 영역의 색 종류만.
- 면 단위로 칠하거나 자르면 경계가 톱니 → 경계 정점 펴기·매끈한 곡선.
- 겉면을 옮긴 곡면 안쪽 → 베드에 못 놓음 → 평면 바닥.
- 평면 LP 를 일부 칸만 뽑아 풀면 두께 0.9 mm 칸 → 모든 칸에 조건.
- 돔 모양 판에서 보호 구역을 평면 조건에 넣으면 해가 없음 → 텐트.
- 45° 텐트가 비스듬한 겉면을 뚫음 → 텐트 ≤ 겉면 − 3.
- 텐트 위 돌기는 뜸 → 뿌리 90 % 숙주 속인 자리만.
- '조각 ∪ 숙주' 로 다시 떼면 공차 틈 때문에 미세 굴·덩어리 빠짐 → 틈 없는 원래 몸(`merge_parts`)에서.
- 몸통 바닥을 '단면 한 덩어리' 까지 자르면 너무 많이 깎임 → 단면 넓이 합 기준.
- 무거운 계산을 같이 돌리면 메모리 부족으로 꺼짐 → 하나씩.

## 8. 벤치마킹 출처
- Chopper(Luo et al. 2012) https://pixl.cs.princeton.edu/pubs/Luo_2012_CPM/index.php
- 피라미드 분해(Hu et al. 2014) https://www2.cs.sfu.ca/~haoz/pubs/hu_siga14_pym.pdf · Karasik et al. 2019 https://www.cs.huji.ac.il/~raananf/projects/3dpart/3DPrinting.pdf
- 높이 지도 분해(Herholz et al. 2015) https://cybertron.cg.tu-berlin.de/~philipp/EG2015
- 골격 분할(Wei et al. 2018) https://www.pubmed.gov/29989969/
- Bambu Cut https://wiki.bambulab.com/en/software/bambu-studio/cut-tool · https://forum.bambulab.com/t/cut-menu-in-studio/152029
- PrusaSlicer Cut https://cdn.help.prusa3d.com/article/cut-tool_1779
- snapsplit https://github.com/Betakontext/snapsplit
- 실무 가이드 https://makers101.com/how-to-split-3d-model-into-parts/ · https://www.sovol3d.com/blogs/news/how-to-split-large-3d-models
- MakerWorld 색깔별 키트 https://forum.bambulab.com/t/is-multicolor-printing-possible-without-ams/185523

---

## 부록 A — `tripo_v3.py` (Tripo v3: 네 방향 그림·H3.1, 키·크레딧 관문)
```python
"""Tripo v3: 사진 → banana_pro 네 방향 그림 → H3.1 multiview 3D.  키 = 환경 변수 TRIPO_API_KEY (코드·채팅에 쓰지 않음).

  python tripo_v3.py views <사진…> --out nb --subject "<캐릭터>" [--ref 공식.png] [--views front,left,back] --approved-credits 45
  python tripo_v3.py mirror nb/left.png nb/right.png          # 좌우 대칭 캐릭터: 옆 그림 거울(0 크레딧)
  python tripo_v3.py multiview nb --out model --approved-credits 60
크레딧(2026-11 실측): banana_pro 2K 15/장, H3.1 detailed + 텍스처 60. 버전·값은 바뀔 수 있으니 공식 문서로 확인.
--approved-credits(사용자가 허락한 크레딧)가 예상보다 적으면 API 를 부르지 않고 계획만 낸다.
"""
import argparse, json, os, sys, time, uuid, mimetypes, urllib.request

API = os.environ.get('TRIPO_API', 'https://openapi.tripo3d.ai/v3')
COST = {'view': 15, 'multiview': 60}
DONE = {'success', 'failed', 'cancelled', 'banned', 'expired'}
VIEW_TXT = {
    'front': "seen exactly from the front: the face and chest face the camera, camera level at chest height, no perspective tilt",
    'left': "as an exact 90-degree side profile seen from the character's LEFT side: the face points to the LEFT edge of the picture, camera level and perpendicular to the body, not from behind",
    'back': "seen exactly from behind (rear view, the face is not visible), camera directly behind, symmetric",
    'right': "as an exact 90-degree side profile seen from the character's RIGHT side: the face points to the RIGHT edge of the picture, camera level and perpendicular to the body, not from behind"}


def gate(cost, approved, what):
    if approved is None or approved < cost:
        raise SystemExit(json.dumps({'blocked': True, 'what': what, 'credits': cost, 'approved': approved,
                                     'ask_user': f'{what}: 예상 {cost} 크레딧. 허락하면 --approved-credits {cost}'}, ensure_ascii=False))


def _hdr(extra=None):
    key = os.environ.get('TRIPO_API_KEY')
    if not key:
        raise SystemExit(json.dumps({'blocked': True, 'missing': 'TRIPO_API_KEY', 'ask_user':
            'Tripo API 키가 없습니다. Tripo Studio 구독(크레딧) 후 Tripo 플랫폼의 API Keys 에서 키를 만들어, '
            '터미널에서 export TRIPO_API_KEY=... 로 넣어 주세요(채팅에 붙여 넣지 않기).'}, ensure_ascii=False))
    h = {'Authorization': f'Bearer {key}'}; h.update(extra or {}); return h


def _req(path, body=None):
    r = urllib.request.Request(API + path, data=json.dumps(body).encode() if body is not None else None,
                               method='POST' if body is not None else 'GET', headers=_hdr({'Content-Type': 'application/json'}))
    with urllib.request.urlopen(r, timeout=120) as f: return json.loads(f.read())


def upload(path):
    b = '----tripo' + uuid.uuid4().hex; ct = mimetypes.guess_type(path)[0] or 'image/png'
    body = (f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="{os.path.basename(path)}"\r\nContent-Type: {ct}\r\n\r\n').encode() \
        + open(path, 'rb').read() + f'\r\n--{b}--\r\n'.encode()
    r = urllib.request.Request(API + '/files', data=body, method='POST', headers=_hdr({'Content-Type': f'multipart/form-data; boundary={b}'}))
    with urllib.request.urlopen(r, timeout=120) as f: return json.loads(f.read())['data']['file_token']


def wait(tid, every=8):
    while True:
        d = _req(f'/tasks/{tid}')['data']
        if d.get('status') in DONE: return d
        print(' ', tid[:8], d.get('status'), d.get('progress'), flush=True); time.sleep(every)


def save(d, stem):
    """출력 내려받기(재시도) + 서명 URL 을 지운 기록 JSON(만료·유출 방지)."""
    o = d.get('output') or {}; files = {}
    for k, v in list(o.items()):
        if isinstance(v, str) and v.startswith('http'):
            p = stem if k == 'generated_image_url' else f"{stem}_{k}{'.glb' if 'model' in k else '.webp'}"
            for t in range(6):
                try: urllib.request.urlretrieve(v, p); files[k] = p; break
                except Exception: time.sleep(3 * (t + 1))
            o[k] = '(signed url omitted)'
    json.dump(d, open(stem + '.json', 'w'), ensure_ascii=False, indent=1); return files


def views(photos, out, subject, which=('front', 'left', 'back', 'right'), ref=None, notes='', approved=None):
    """앞 = 사진만(설명을 섞으면 등 쪽을 그림). 옆·뒤 = 사진 + 공식 그림(있으면)."""
    gate(COST['view'] * len(which), approved, f'banana_pro 방향 그림 {len(which)}장'); _hdr()   # 키부터 확인
    os.makedirs(out, exist_ok=True); toks = [upload(p) for p in photos]; rt = upload(ref) if ref else None; res = {}
    for v in which:
        if v == 'front':
            inp = toks
            pr = (f"Image[1] is a figure of {subject} photographed from the front. Redraw exactly this figure as a clean straight-on FRONT view: {VIEW_TXT[v]}. "
                  "Keep the same pose, proportions, material and colors. Full body with margin, plain white background, centered, no ground shadow. " + notes)
        else:
            inp = toks + ([rt] if rt else [])
            pr = (f"Image[1] is a figure of {subject}. Draw this exact same figure {VIEW_TXT[v]}, keeping the same pose, proportions, material, colors and scale. "
                  "Show the full body with margin on a plain white background, centered, no shadow on the ground, no other objects. "
                  + (f"For parts not visible in the photo, follow the official design in image[{len(toks) + 1}]. " if rt else '') + "Toy figure style, not an illustration. " + notes)
        tid = _req('/generation/image-to-image', {'model': 'banana_pro', 'inputs': inp, 'prompt': pr, 'aspect_ratio': '1:1', 'size': '2K', 'output_format': 'png'})['data']['task_id']
        d = wait(tid); res[v] = {'task_id': tid, 'status': d.get('status'), 'credits': d.get('credits_consumed'), 'files': save(d, os.path.join(out, f'{v}.png'))}
    json.dump(res, open(os.path.join(out, 'views.json'), 'w'), ensure_ascii=False, indent=1); return res


def mirror(src, dst):
    from PIL import Image, ImageOps
    ImageOps.mirror(Image.open(src)).save(dst); return {'mirror': dst}


def multiview(folder, stem, approved=None):
    """H3.1 + detailed + 텍스처 v3.5 + delight(텍스처에 구운 그늘 제거 — 색 나눌 때 그늘이 검정 얼룩이 되지 않게)."""
    gate(COST['multiview'], approved, 'Tripo H3.1 multiview-to-model'); _hdr()
    inputs = [{v: upload(os.path.join(folder, f'{v}.png'))} for v in ('front', 'left', 'back', 'right')]
    body = {'inputs': inputs, 'model': 'v3.1-20260211', 'geometry_quality': 'detailed', 'texture': True, 'pbr': False,
            'texture_quality': 'detailed', 'texture_version': 'v3.5-20260815', 'delight': True, 'texture_alignment': 'original_image'}
    tid = _req('/generation/multiview-to-model', body)['data']['task_id']; d = wait(tid)
    return {'task_id': tid, 'status': d.get('status'), 'credits': d.get('credits_consumed'), 'files': save(d, stem)}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    a = sp.add_parser('views'); a.add_argument('photos', nargs='+'); a.add_argument('--out', required=True); a.add_argument('--subject', required=True)
    a.add_argument('--ref'); a.add_argument('--views', default='front,left,back,right'); a.add_argument('--notes', default=''); a.add_argument('--approved-credits', type=int)
    a = sp.add_parser('mirror'); a.add_argument('src'); a.add_argument('dst')
    a = sp.add_parser('multiview'); a.add_argument('folder'); a.add_argument('--out', required=True); a.add_argument('--approved-credits', type=int)
    a = ap.parse_args()
    if a.cmd == 'views': r = views(a.photos, a.out, a.subject, tuple(a.views.split(',')), a.ref, a.notes, a.approved_credits)
    elif a.cmd == 'mirror': r = mirror(a.src, a.dst)
    else: r = multiview(a.folder, a.out, a.approved_credits)
    print(json.dumps(r, ensure_ascii=False, indent=1))
```

## 부록 B — `bl_clean.py` (Blender 정리: 닫힌 한 몸 + 정점 색)
```python
"""Blender(pip install bpy) 정리: Tripo GLB → 회전·크기(높이 mm)·바닥 0 → 복셀 리메시(닫힌 한 몸) → 데시메이트 → 텍스처 색을 정점 색(BVH 최근접 UV).
  python bl_clean.py model.glb fig --height 180 --rot -90 --voxel 0.3 --faces 600000   → fig.npz (V, F, C)  — 앞 −y·위 +z 가 되게 --rot 조정"""
import bpy, bmesh, sys, argparse, numpy as np, time
from mathutils.bvhtree import BVHTree
from mathutils import Vector
from mathutils.geometry import barycentric_transform
ap = argparse.ArgumentParser(); ap.add_argument('glb'); ap.add_argument('out')
ap.add_argument('--height', type=float, default=200); ap.add_argument('--rot', type=float, default=-90)
ap.add_argument('--voxel', type=float, default=0.35); ap.add_argument('--faces', type=int, default=600000)
a = ap.parse_args(sys.argv[1:])
t0 = time.time()
bpy.ops.wm.read_factory_settings(use_empty=True)
if a.glb.lower().endswith('.stl'): bpy.ops.wm.stl_import(filepath=a.glb)
else: bpy.ops.import_scene.gltf(filepath=a.glb, merge_vertices=True)
src = [o for o in bpy.context.scene.objects if o.type == 'MESH'][0]
bpy.context.view_layer.objects.active = src; src.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
# 회전·크기·바닥 정렬(원본 메시 자체에 적용 — 색 샘플용 원본과 리메시가 같은 좌표)
me = src.data
co = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
r = np.radians(a.rot); R = np.array([[np.cos(r), -np.sin(r), 0], [np.sin(r), np.cos(r), 0], [0, 0, 1]])
co = co @ R.T; co *= a.height / (co[:, 2].max() - co[:, 2].min())
co[:, 0] -= (co[:, 0].max() + co[:, 0].min()) / 2; co[:, 1] -= (co[:, 1].max() + co[:, 1].min()) / 2; co[:, 2] -= co[:, 2].min()
me.vertices.foreach_set('co', co.ravel()); me.update()
# 색 샘플용 자료(원본): 삼각형·UV·텍스처
imgs = [n.image for m in me.materials if m and m.node_tree for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image]
if imgs:
    img = imgs[0]; W, H = img.size; px = np.array(img.pixels[:], dtype=np.float32).reshape(H, W, 4)[:, :, :3]
else:  # 텍스처 없는 메시: 회색
    W = H = 1; px = np.full((1, 1, 3), 0.5, np.float32)
bm0 = bmesh.new(); bm0.from_mesh(me); bmesh.ops.triangulate(bm0, faces=bm0.faces); bm0.faces.ensure_lookup_table()
uvl = bm0.loops.layers.uv.active
if uvl is None: W = H = 1; px = np.full((1, 1, 3), 0.5, np.float32)
bvh = BVHTree.FromBMesh(bm0)
# 리메시 대상 = 복사본
dst = src.copy(); dst.data = src.data.copy(); bpy.context.collection.objects.link(dst)
for o in bpy.context.selected_objects: o.select_set(False)
bpy.context.view_layer.objects.active = dst; dst.select_set(True)
dst.data.remesh_voxel_size = a.voxel; dst.data.use_remesh_fix_poles = True
bpy.ops.object.voxel_remesh()
n_vox = len(dst.data.polygons)
d = dst.modifiers.new('d', 'DECIMATE'); d.ratio = min(1.0, a.faces / max(1, n_vox)); d.use_collapse_triangulate = True
bpy.ops.object.modifier_apply(modifier='d')
bm = bmesh.new(); bm.from_mesh(dst.data); bmesh.ops.triangulate(bm, faces=bm.faces)
V = np.array([v.co[:] for v in bm.verts]); bm.verts.index_update()
F = np.array([[v.index for v in f.verts] for f in bm.faces], dtype=np.int64)
nm = sum(1 for e in bm.edges if not e.is_manifold)
# 정점 색: 원본 최근접 점 → 그 삼각형 UV 보간 → 텍스처
C = np.zeros((len(V), 3), np.float32)
for i, p in enumerate(V):
    loc, nrm, fi, dist = bvh.find_nearest(Vector(p))
    if uvl is None: C[i] = px[0, 0]; continue
    f = bm0.faces[fi]; ls = f.loops
    uv = barycentric_transform(loc, ls[0].vert.co, ls[1].vert.co, ls[2].vert.co,
                               Vector((*ls[0][uvl].uv, 0)), Vector((*ls[1][uvl].uv, 0)), Vector((*ls[2][uvl].uv, 0)))
    C[i] = px[min(H - 1, max(0, int((uv.y % 1) * H))), min(W - 1, max(0, int((uv.x % 1) * W)))]
np.savez_compressed(a.out + '.npz', V=V, F=F, C=C)
print(f'DONE voxel_faces={n_vox} faces={len(F)} nonmanifold_edges={nm} bbox={V.min(0).round(1)}..{V.max(0).round(1)} {time.time()-t0:.0f}s')
```

## 부록 C — `figseg.py` (색·꺾임 영역 → 조각 이름 → Separate+Fill)
```python
"""색·꺾임 영역 → 조각 이름 → Separate+Fill(꺾임 고리를 평면 막음면으로) — Blender '영역 선택 → Separate(P) → Fill' 을 스크립트로.
  regions(V, F, C, k)      → face_color(색 번호), face_patch(영역 번호), patches(영역마다 색·넓이·중심)  ← 사용자에게 그림으로 보여 조각표를 정함
  label_faces(F, patch, A, names)  → 면마다 조각 이름(지정 안 한 영역·작은 영역은 이웃/‘core’)
  separate_fill(V, F, lab, order, extract) → {이름: (V, F, info)}, 남은 몸 'core'   (겉면 원본 그대로, 맞닿는 막음면 정확히 같음 → 겹침 0·틈 0)
막음면 = 고리에 맞춘 평면 위 평평한 바닥 + 고리까지 가파른 테두리(기울기 ≥ 61°) → 그 바닥이 출력 베드.
"""
import numpy as np, trimesh
import scipy.sparse as sp, scipy.sparse.csgraph as cg
from scipy.spatial import cKDTree
from shapely.geometry import Polygon, LinearRing
import manifold3d as mf


def to_mf(V, F):
    M = mf.Manifold(mf.Mesh(vert_properties=np.asarray(V, np.float32), tri_verts=np.asarray(F, np.uint32)))
    if M.status() != mf.Error.NoError or M.volume() < 0:
        M = mf.Manifold(mf.Mesh(vert_properties=np.asarray(V, np.float32), tri_verts=np.asarray(F, np.uint32)[:, ::-1]))
    return M


def from_mf(M):
    m = M.to_mesh(); return np.asarray(m.vert_properties)[:, :3].astype(float), np.asarray(m.tri_verts).astype(np.int64)


def face_spread(P, N, R=0.5, chunk=150000):
    """면마다 반경 R(mm) 안 면 법선과의 최대 각차(°). > 25° = 꺾임 띠(이면각 하나는 복셀 리메시로 퍼져 끊김)."""
    tree = cKDTree(P); out = np.zeros(len(P))
    for s in range(0, len(P), chunk):
        for k, j in enumerate(tree.query_ball_point(P[s:s + chunk], R)):
            out[s + k] = np.degrees(np.arccos(np.clip((N[j] @ N[s + k]).min(), -1, 1)))
    return out


def rgb2lab(c):
    c = np.clip(c, 0, 1); lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    xyz = lin @ np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]).T / [0.95047, 1.0, 1.08883]
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.c_[116 * f[:, 1] - 16, 500 * (f[:, 0] - f[:, 1]), 200 * (f[:, 1] - f[:, 2])]


def color_labels(C, k, linear=True, seed=0):
    """정점 색(Blender 정점 색은 선형 RGB) → CIELAB k-평균 k 색. 반환: 정점 색 번호, 색 중심(sRGB)."""
    from scipy.cluster.vq import kmeans2
    s = np.where(C <= 0.0031308, C * 12.92, 1.055 * np.clip(C, 0, 1) ** (1 / 2.4) - 0.055) if linear else C
    L = rgb2lab(s); cen, lab = kmeans2(L, k, minit='++', seed=seed)
    srgb = np.array([s[lab == i].mean(0) if (lab == i).any() else [0.5] * 3 for i in range(k)])
    return lab, srgb


def components(n, e0, e1, keep):
    G = sp.coo_matrix((np.ones(keep.sum()), (e0[keep], e1[keep])), shape=(n, n))
    return cg.connected_components(G, directed=False)[1]


def absorb(lab, bad, e0, e1, ncls):
    """bad 면을 맞닿은 good 면의 라벨 다수결로 반복해서 채운다."""
    lab = lab.copy(); bad = bad.copy()
    for _ in range(400):
        if not bad.any(): break
        s0 = bad[e0] & ~bad[e1]; s1 = bad[e1] & ~bad[e0]
        src = np.r_[e0[s0], e1[s1]]; val = np.r_[lab[e1[s0]], lab[e0[s1]]]
        if not len(src): break
        M = sp.coo_matrix((np.ones(len(src)), (src, val)), shape=(len(lab), ncls)).tocsr()
        has = np.asarray(M.sum(1)).ravel() > 0; got = np.asarray(M.argmax(1)).ravel()
        lab[has] = got[has]; bad[has] = False
    return lab


def clean_islands(F, lab, A, min_area=400.0):
    """같은 라벨 연결 덩어리 중 작은 것(< min_area mm²)을 맞닿은 라벨 다수결로(반복). 고리가 하나가 되게."""
    m = trimesh.Trimesh(np.zeros((F.max() + 1, 3)), F, process=False)
    adj = trimesh.graph.face_adjacency(F); e0, e1 = adj[:, 0], adj[:, 1]
    lab = lab.copy()
    for _ in range(6):
        same = lab[e0] == lab[e1]
        G = sp.coo_matrix((np.ones(same.sum()), (e0[same], e1[same])), shape=(len(F), len(F)))
        _, cc = cg.connected_components(G, directed=False); ar = np.bincount(cc, weights=A)
        small = ar[cc] < min_area
        if not small.any(): break
        names = sorted(set(lab.tolist())); idx = {n: i for i, n in enumerate(names)}; li = np.array([idx[x] for x in lab])
        s0 = small[e0] & ~small[e1]; s1 = small[e1] & ~small[e0]
        src = np.r_[e0[s0], e1[s1]]; val = np.r_[li[e1[s0]], li[e0[s1]]]
        M = sp.coo_matrix((np.ones(len(src)), (cc[src], val)), shape=(cc.max() + 1, len(names))).tocsr()
        best = np.asarray(M.argmax(1)).ravel(); has = np.asarray(M.sum(1)).ravel() > 0
        chg = small & has[cc]; lab[chg] = np.array(names)[best[cc[chg]]]
    return lab


def relax_boundaries(V, F, lab, it=4, a=0.5):
    """라벨 경계선 정점을 경계선 이웃 평균 쪽으로(교차점 제외). 0.3 mm 톱니만 편다."""
    m = trimesh.Trimesh(V, F, process=False); adj = m.face_adjacency; ae = m.face_adjacency_edges
    bd = lab[adj[:, 0]] != lab[adj[:, 1]]; E = ae[bd]
    G = sp.coo_matrix((np.ones(2 * len(E)), (np.r_[E[:, 0], E[:, 1]], np.r_[E[:, 1], E[:, 0]])), shape=(len(V), len(V))).tocsr()
    G.data[:] = 1; deg = np.asarray(G.sum(1)).ravel(); mv = deg == 2
    V = V.copy(); V0 = V.copy()
    for _ in range(it):
        avg = (G @ V) / np.maximum(deg, 1)[:, None]
        V[mv] = V[mv] + a * (avg[mv] - V[mv])
    disp = np.linalg.norm(V - V0, axis=1)
    return V, float(disp.max()), int(mv.sum())


def ordered_loops(F, faces_in):
    """faces_in(bool) 패치의 경계 반변으로 닫힌 고리들(패치 바깥 방향 순서)."""
    sub = F[faces_in]
    e = np.r_[sub[:, [0, 1]], sub[:, [1, 2]], sub[:, [2, 0]]]
    key = {}
    for u, v in e: key[(u, v)] = True
    bnd = [(u, v) for u, v in e if (v, u) not in key]
    nxt = {}
    for u, v in bnd: nxt.setdefault(u, []).append(v)
    loops = []; used = set()
    for u, v in bnd:
        if (u, v) in used: continue
        L = [u]; cur = (u, v)
        while cur not in used:
            used.add(cur); L.append(cur[1]); cands = [w for w in nxt.get(cur[1], []) if (cur[1], w) not in used]
            if not cands: break
            cur = (cur[1], cands[0])
        if L[-1] == L[0]: L = L[:-1]
        loops.append(np.array(L))
    return sorted(loops, key=len, reverse=True)


def make_cap(V, loop, piece_center):
    """loop(정점 번호, 순서) 를 막는 면. 반환: 새 정점 좌표, 면(전역 번호: 고리는 기존, 새 정점은 len(V)+i), n."""
    L = V[loop]; c = L.mean(0); _, _, vt = np.linalg.svd(L - c, full_matrices=False); n = vt[2]
    if (piece_center - c) @ n < 0: n = -n
    e1 = vt[0]; e2 = np.cross(n, e1); h = (L - c) @ n; p0 = c + n * h.min(); h = h - h.min()
    q = np.c_[(L - p0) @ e1, (L - p0) @ e2]
    ring = LinearRing(q); ccw = ring.is_ccw
    # 안쪽 법선(2D)
    t = np.roll(q, -1, 0) - np.roll(q, 1, 0); t /= np.linalg.norm(t, axis=1)[:, None] + 1e-12
    nin = np.c_[-t[:, 1], t[:, 0]] if ccw else np.c_[t[:, 1], -t[:, 0]]
    w = np.maximum(0.8, 0.55 * h)
    from shapely.geometry import Point
    from shapely.ops import unary_union
    P2 = Polygon(q).buffer(0)
    disks = unary_union([Point(x, y).buffer(r, 12) for (x, y), r in zip(q[::2], w[::2])])
    inner = P2.difference(disks)
    if inner.geom_type != 'Polygon': inner = max(inner.geoms, key=lambda g: g.area)
    inner = inner.buffer(-0.05).buffer(0.05).simplify(0.05)
    if inner.geom_type != 'Polygon': inner = max(inner.geoms, key=lambda g: g.area)
    ok = inner.is_valid and inner.area > 0
    ring = np.array(inner.exterior.coords)[:-1]
    if LinearRing(ring).is_ccw != ccw: ring = ring[::-1]
    # 고리 지퍼: 바깥 고리(q, m_개)와 안쪽 고리(ring, k개)를 둘레 비율로 짝지음
    m_ = len(loop); k_ = len(ring)
    s0 = np.r_[0, np.cumsum(np.linalg.norm(np.diff(np.r_[q, q[:1]], axis=0), axis=1))]; s0 = s0[:-1] / s0[-1]
    # 안쪽 고리 시작점 = 바깥 0번에 가장 가까운 점
    st = np.argmin(np.linalg.norm(ring - q[0], axis=1)); ring = np.roll(ring, -st, 0)
    s1 = np.r_[0, np.cumsum(np.linalg.norm(np.diff(np.r_[ring, ring[:1]], axis=0), axis=1))]; s1 = s1[:-1] / s1[-1]
    n0 = len(V)
    band = []; i = j = 0
    while i < m_ or j < k_:
        a_, b_ = loop[i % m_], n0 + (j % k_)
        si = s0[i + 1] if i + 1 < m_ else 1.0; sj = s1[j + 1] if j + 1 < k_ else 1.0
        if (si <= sj and i < m_) or j >= k_:
            band.append([a_, loop[(i + 1) % m_], b_]); i += 1
        else:
            band.append([a_, n0 + ((j + 1) % k_), b_]); j += 1
    band = np.array(band)
    I = ring; newV = p0 + np.outer(I[:, 0], e1) + np.outer(I[:, 1], e2)
    m2 = k_
    import mapbox_earcut as me
    tri = me.triangulate_float64(I.astype(np.float64), np.array([m2], dtype=np.uint32)).reshape(-1, 3)
    flat = n0 + tri
    return newV, band, flat, n, p0, float(h.max()), ok


def orient_cap(Vall, band, flat, n, piece_faces_dir_ok=True):
    """막음면이 조각 바깥(−n)을 향하게. 띠·바닥 면 법선 평균으로 판단해 뒤집음."""
    caps = np.r_[band, flat]
    T = Vall[caps]; nn = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    flat_n = nn[len(band):].sum(0)
    fl = flat if flat_n @ n < 0 else flat[:, ::-1]                       # 바닥 법선은 −n
    # 띠: 바닥과 공유하는 변의 방향이 반대가 되게(일관된 감김)
    fe = set(map(tuple, np.r_[fl[:, [0, 1]], fl[:, [1, 2]], fl[:, [2, 0]]].tolist()))
    be = np.r_[band[:, [0, 1]], band[:, [1, 2]], band[:, [2, 0]]]
    agree = sum(1 for u, v in be.tolist() if (u, v) in fe); oppose = sum(1 for u, v in be.tolist() if (v, u) in fe)
    bd = band if oppose >= agree else band[:, ::-1]
    return np.r_[bd, fl]


def extract_cap(V, F, kf, loops, t=6.0, nsmooth=40, psmooth=15):
    """Blender Mask Extract 처럼: 패치(kf 면)를 두께 t 판으로. 안쪽 면 = 정점을 매끈하게 편 법선 반대로 t 이동 후 편 면.
    반환: 새 정점, 막음 면(벽 + 안쪽 면, 조각 바깥을 향함), 패치 정점→안쪽 정점 번호 사상."""
    sub = F[kf]; vs = np.unique(sub); loc = -np.ones(len(V), int); loc[vs] = np.arange(len(vs))
    tm = trimesh.Trimesh(V[vs], loc[sub], process=False); N = tm.vertex_normals.copy()
    e = tm.edges_unique; G = sp.coo_matrix((np.ones(2 * len(e)), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(len(vs), len(vs))).tocsr()
    deg = np.asarray(G.sum(1)).ravel()
    for _ in range(nsmooth): N = (G @ N + N) / (deg + 1)[:, None]; N /= np.linalg.norm(N, axis=1)[:, None]
    Q = V[vs] - t * N
    onloop = np.zeros(len(vs), bool)
    for loop in loops: onloop[loc[loop]] = True
    for _ in range(psmooth): Q = np.where(onloop[:, None], Q, (G @ Q + Q) / (deg + 1)[:, None])
    n0 = len(V); inner = n0 + loc                                         # 패치 정점 v → 안쪽 정점 n0+loc[v]
    innerF = inner[sub][:, ::-1]
    walls = []
    for loop in loops:
        i = np.arange(len(loop)); j = (i + 1) % len(loop)
        a_, b_ = loop[i], loop[j]; c_, d_ = inner[loop[j]], inner[loop[i]]
        walls.append(np.r_[np.c_[b_, a_, d_], np.c_[b_, d_, c_]])
    walls = np.vstack(walls)
    return Q, np.r_[walls, innerF]




def regions(V, F, C, k=6, T=25.0, R=0.5, min_area=30.0):
    """꺾임 띠로 갈린 덩어리 = 영역, 영역 색 = 텍스처 색 면적 다수결(텍스처 밝기로 경계를 정하지 않음 — 구운 그늘이 얼룩이 됨),
    띠·작은 영역은 이웃으로, 같은 색이 맞닿은 영역은 하나 → 색 영역(조각 후보)."""
    m = trimesh.Trimesh(V, F, process=False); P, N, A = m.triangles_center, m.face_normals, m.area_faces
    e0, e1 = m.face_adjacency[:, 0], m.face_adjacency[:, 1]
    band = face_spread(P, N, R) > T
    vl, srgb = color_labels(C, k); fl = np.array([np.bincount(r, minlength=k).argmax() for r in vl[F]])
    reg = components(len(F), e0, e1, ~band[e0] & ~band[e1]); reg[band] = -1; ok = reg >= 0
    W = sp.coo_matrix((A[ok], (reg[ok], fl[ok])), shape=(reg.max() + 1, k)).toarray(); rcol = W.argmax(1); rarea = W.sum(1)
    col = np.where(ok, rcol[np.maximum(reg, 0)], -1); small = ok & (rarea[np.maximum(reg, 0)] < min_area)
    col = absorb(np.where(small | ~ok, 0, col), small | ~ok, e0, e1, k)
    patch = components(len(F), e0, e1, col[e0] == col[e1]); pa = np.bincount(patch, weights=A)
    patches = [{'patch': int(i), 'color': int(col[patch == i][0]), 'rgb': np.round(srgb[col[patch == i][0]], 3).tolist(), 'area_mm2': round(float(pa[i]), 1),
                'center': np.round(P[patch == i].mean(0), 1).tolist()} for i in np.argsort(-pa)[:60]]
    return col, patch, patches, srgb


def label_faces(F, patch, A, names, min_area=400.0):
    """names = {영역 번호: 조각 이름}. 이름 없는 영역 = 'core'. 작은 섬(< min_area)은 맞닿은 조각으로(고리가 하나가 되게)."""
    lab = np.full(len(F), 'core', dtype=object)
    for p, n in names.items(): lab[patch == int(p)] = n
    return clean_islands(F, lab.astype(str), A, min_area)


def separate_fill(V, F, lab, order, extract=None):
    """order 순서로 조각을 뗀다(머리 → 팔 → 돌출 → 꼬리 → 판 → 다리). extract={이름: 두께} 인 조각은 판(Mask Extract)으로."""
    extract = extract or {}; A = trimesh.Trimesh(V, F, process=False).area_faces
    V, _, _ = relax_boundaries(V, F, lab); out = {}; curV, curF, curL = V, F, np.asarray(lab).astype(str)
    for p in order:
        k = curL == p
        if not k.any(): continue
        loops = [l for l in ordered_loops(curF, k) if len(l) >= 12]
        if not loops: continue
        m = trimesh.Trimesh(curV, curF, process=False); adj = m.face_adjacency
        a = curL[adj[:, 0]] == p; b = curL[adj[:, 1]] == p; nb = np.where(a & ~b, curL[adj[:, 1]], np.where(b & ~a, curL[adj[:, 0]], ''))
        nbc = {x: int((nb == x).sum()) for x in set(nb.tolist()) if x}; parent = max(nbc, key=nbc.get)
        center = curV[curF[k]].mean((0, 1)); n = np.zeros(3); p0 = center
        if p in extract:
            newV, caps = extract_cap(curV, curF, k, loops, t=extract[p]); Vall = np.r_[curV, newV]
            if trimesh.Trimesh(Vall, np.r_[curF[k], caps], process=False).volume < 0: caps = caps[:, ::-1]
        else:
            Vall = curV; caps = np.zeros((0, 3), int)
            for L in loops:
                newV, band, flat, n_, p0_, rise_, ok_ = make_cap(Vall, L, center)
                Vall2 = np.r_[Vall, newV]; caps = np.r_[caps, orient_cap(Vall2, band, flat, n_)]; Vall = Vall2
                if L is loops[0]: n, p0 = n_, p0_
        PF = np.r_[curF[k], caps]; used = np.unique(PF); rm = -np.ones(len(Vall), int); rm[used] = np.arange(len(used))
        M = to_mf(Vall[used], rm[PF])
        out[p] = (Vall[used], rm[PF], {'parent': parent, 'cap_n': np.round(n, 4).tolist(), 'cap_p0': np.round(p0, 3).tolist(),
                                       'volume_mm3': round(M.volume(), 1), 'genus': M.genus(), 'status': str(M.status())})
        RF = np.r_[curF[~k], caps[:, ::-1]]; RL = np.r_[curL[~k], np.full(len(caps), parent)]
        used = np.unique(RF); rm = -np.ones(len(Vall), int); rm[used] = np.arange(len(used)); curV, curF, curL = Vall[used], rm[RF], RL
    M = to_mf(curV, curF); out['core'] = (curV, curF, {'volume_mm3': round(M.volume(), 1), 'genus': M.genus(), 'status': str(M.status())})
    return out
```

## 부록 D — `figsplit.py` (출력 방향 분할: 판 평면 바닥 + 텐트, 긴 가지, 몸통 바닥, 육각 결합)
```python
"""출력 방향 분할 — 조각마다 평평한 베드, 숨은 안쪽은 평면, 공차는 핀·숨은 바닥에만.
  merge_parts([(V,F),…])                 분할 전 조각(막음면 공유)을 공유 면만 지워 한 몸(genus 0)으로 — 불리언 합집합은 막음면에서 멈추거나 미세 굴
  plane_piece(body, SP, lab, d, others, protect)  판 조각: 빼는 방향 d 기둥 ∩ LP 평면 위(두께 ≥ TMIN, 부피 최소) − 보호 구역 − 45° 텐트 → (조각, 숙주, 정보)
  limb_split(M, base, s)                 긴 가지: 축(base → 무게중심) 길이 비 s 에서 수직으로 두 조각 + 육각 돌기/구멍
  flat_bottom(M, up, min_area)           몸통: 단면 넓이 합 ≥ min_area 인 가장 낮은 높이에서 수평으로 자름
  hex_joint(parent, child, c, n, af, L)  육각 돌기(부모)/구멍(자식, +0.2/쪽·깊이 +0.6·45° 뿔 천장)
  plate_pegs(P, host, surf, d)           판 평면 바닥에 육각 af6·L3 × 3(뿌리가 숙주 속 90 %)
"""
import numpy as np, trimesh, manifold3d as mf
from scipy import ndimage
from scipy.spatial import cKDTree
from skimage import measure
from figseg import to_mf, from_mf

T = 6.0; FLOOR = 0.15; G = 0.35; SIG = 1.0; TOP = 3.0; TMIN = 3.0; CL = 0.20
L = lambda p: to_mf(*[np.load(p)[k] for k in ('V', 'F')])
keep_big = lambda M: max(M.decompose(), key=lambda b: b.volume())


def frame(d):
    d = d / np.linalg.norm(d); a = np.array([1.0, 0, 0]) if abs(d[0]) < 0.9 else np.array([0, 1.0, 0])
    u = np.cross(a, d); u /= np.linalg.norm(u); return u, np.cross(d, u), d


def column_slab(SP, lab, g, d, depth, EXP=None, PLANE=None):
    """깊이 지도: 표본점 SP(라벨 lab) → (u,v) 칸마다 맨 위 높이 H·라벨 → 라벨 g 칸의 기둥 [H−depth, H+TOP] 메시(조립 좌표)."""
    u, v, d = frame(d); U, W, H = SP @ u, SP @ v, SP @ d
    iu = np.floor((U - U.min()) / G).astype(np.int64) + 2; iw = np.floor((W - W.min()) / G).astype(np.int64) + 2
    nu, nw = iu.max() + 3, iw.max() + 3; key = iu * nw + iw
    o = np.lexsort((H, key)); last = np.r_[key[o][1:] != key[o][:-1], True]; top = o[last]            # 칸마다 가장 높은 표본
    Hm = np.full(nu * nw, np.nan); Lm = np.full(nu * nw, -1); Hm[key[top]] = H[top]; Lm[key[top]] = lab[top]
    Hm = Hm.reshape(nu, nw); Lm = Lm.reshape(nu, nw)
    filled = np.isfinite(Hm)
    EXH = None
    if EXP is not None:
        eu = np.floor((EXP @ u - U.min()) / G).astype(np.int64) + 2; ew = np.floor((EXP @ v - W.min()) / G).astype(np.int64) + 2; eh = EXP @ d
        ok = (eu >= 0) & (eu < nu) & (ew >= 0) & (ew < nw); EXH = np.full((nu, nw), -np.inf); np.maximum.at(EXH, (eu[ok], ew[ok]), eh[ok])
        EXH = ndimage.maximum_filter(EXH, size=int(2.0 / G) * 2 + 1); EXH[~np.isfinite(EXH)] = np.nan; EXH = np.where(EXH < -1e8, np.nan, EXH)
    Hf = np.where(filled, Hm, 0.0); wgt = filled.astype(float)                                       # 빈 칸 메움 + 높이 펴기(바닥 면용)
    Hs = ndimage.gaussian_filter(Hf, 2.0) / np.maximum(ndimage.gaussian_filter(wgt, 2.0), 1e-6)
    # 텍스처 얼룩 정리(사용자 2026-11-06 "마감부위가 너무 거칠어"): 60 mm² 미만 섬 지우고 구멍 메운 뒤 σ 1 mm 로 경계를 편다
    bm = (Lm == g); lab_, nlab = ndimage.label(bm); minc = int(60.0 / (G * G)); minh = int(250.0 / (G * G))   # 깎기(opening)는 가는 이음까지 지워 판에 구멍 → 안 씀
    if nlab: sz = ndimage.sum(bm, lab_, range(1, nlab + 1)); bm = np.isin(lab_, 1 + np.where(sz >= minc)[0])
    hl, nh_ = ndimage.label(~bm)
    if nh_:
        sz = ndimage.sum(~bm, hl, range(1, nh_ + 1)); edge = set(np.unique(np.r_[hl[0], hl[-1], hl[:, 0], hl[:, -1]]))
        small = [i + 1 for i, z in enumerate(sz) if z < minh and (i + 1) not in edge]; bm = bm | np.isin(hl, small)   # 250 mm² 미만 구멍 메움(대포 지나는 날개 구멍은 그대로)
    mask = ndimage.gaussian_filter(bm.astype(float), SIG / G)                                        # 경계 σ 1 mm
    mask = np.where(ndimage.binary_dilation(filled, iterations=3), mask, 0.0)
    if (mask > 0.5).sum() == 0: return None, {}
    # 기둥 윗면은 펴지 않은 최대 높이(5칸 최댓값) + TOP — 편 높이(Hs)는 날개 상자 모서리에서 실제보다 낮아 윗면을 0.5 mm 잘랐음(mm voids 2026-11-06)
    Hmax = ndimage.maximum_filter(np.where(filled, Hm, -1e9), size=5); Hmax = np.where(Hmax < -1e8, Hs, Hmax)
    # 평면 바닥: h = a·i + b·j + c (칸 좌표). 조건: 평면 ≤ Hs − TMIN(마스크 칸), 평면 ≥ 보호 구역 윗면 + 1(마스크 칸). 목적: 평면 높이 합 최대(= 부피 최소)
    from scipy.optimize import linprog
    # 관통 칸: 보호 구역(대포 돌기·대포로 올라가는 물길)이 겉면 − TMIN − 1 보다 위로 올라오는 칸은 평면이 그 위를 지날 수 없음
    # → 조각에서 그 칸(+1 mm)을 빼 관통 구멍으로 둔다(심이 그 기둥을 갖고 대포 밑동이 덮음). 2026-11-07 첫 실행은 LP 불가 → 보호 조건 없이 풀어 물길 침범 1.2만 mm³
    through = np.zeros_like(mask, bool)
    if EXP is not None:
        through = np.isfinite(EXH) & (EXH + 1.0 > Hs - TMIN - 1.0) & (mask > 0.02)
        through = ndimage.binary_dilation(through, iterations=int(np.ceil(1.0 / G)))
        mask = np.where(through, 0.0, mask)
    PLANE['through_mm2'] = round(float((through & (ndimage.binary_dilation(filled, iterations=3))).sum() * G * G), 1)
    I, Jc = np.nonzero(mask > 0.3)                                                   # 모든 칸에 조건(6000칸만 뽑으면 보호 구역·얇은 칸이 빠짐 — 2026-11-07 침범 9.6 cm³·두께 0.9)
    A_ub = [np.c_[I, Jc, np.ones(len(I))]]; b_ub = [Hs[I, Jc] - TMIN]
    # 보호 구역 조건은 넣지 않음: 돔처럼 휜 조각은 평면 한 장이 테두리 밑과 속 물길 위를 동시에 지날 수 없음
    # (2026-11-07 실측, 여유 변수 LP: C 3,097 mm²·최대 24 mm(물길·꼬리 돌기), L 1,126·41(대포 돌기), R 728·31) → 보호 구역 밑은 45° 텐트 홈(tent_solid)
    res = linprog(-np.array([I.sum(), Jc.sum(), len(I)], float), A_ub=np.vstack(A_ub), b_ub=np.concatenate(b_ub), bounds=[(None, None)] * 3, method='highs')
    ok_prot = bool(res.success)
    if EXP is not None:                                                              # 텐트에 쓸 보호 구역 표본: 겉면 − TMIN − 2 보다 깊은 것(관통 칸 것은 빼서 겉 구멍이 넓어지지 않게)
        hs_e = Hs[np.clip(eu, 0, nu - 1), np.clip(ew, 0, nw - 1)]
        PLANE['ex_keep'] = EXP[ok & (eh < hs_e - TMIN - 2.0) & ~through[np.clip(eu, 0, nu - 1), np.clip(ew, 0, nw - 1)]]
    a_, b_, c_ = res.x; II, JJ = np.meshgrid(np.arange(nu), np.arange(nw), indexing='ij'); PL = a_ * II + b_ * JJ + c_ - (depth - T)
    PLANE.update({'a': float(a_), 'b': float(b_), 'c': float(c_), 'G': G, 'u0': float(U.min()), 'w0': float(W.min()), 'lp_ok': ok_prot,
                  'thick_mm': [round(float((Hs - PL)[mask > 0.5].min()), 2), round(float((Hs - PL)[mask > 0.5].max()), 2)]})
    # 평면의 위쪽 법선(조립 좌표): h − a·i − b·j = c → 기울기 (−a/G, −b/G, 1)
    nloc = np.array([-a_ / G, -b_ / G, 1.0]); nloc /= np.linalg.norm(nloc); PLANE['bed_n'] = (nloc[0] * u + nloc[1] * v + nloc[2] * d).round(5).tolist()
    sel = mask > 0.02; hlo = PL[sel].min() - 1.0; hhi = Hmax[sel].max() + TOP + 1.0
    nh = int(np.ceil((hhi - hlo) / G)) + 1; f = np.empty((nu, nw, nh), np.float32)
    for k in range(nh):
        h = hlo + G * k; f[:, :, k] = np.maximum.reduce([0.5 - mask, PL - h, h - (Hmax + TOP)])
    vv, ff, _, _ = measure.marching_cubes(np.pad(f, 1, constant_values=5.0), 0.0, spacing=(G, G, G))
    vv = vv - G; uu = vv[:, 0] - 2 * G + U.min(); ww = vv[:, 1] - 2 * G + W.min(); hh = vv[:, 2] + hlo
    X = np.outer(uu, u) + np.outer(ww, v) + np.outer(hh, d)
    import fast_simplification as fs
    v2, f2 = fs.simplify(X.astype(np.float32), ff[:, ::-1].astype(np.int32), target_reduction=0.8)
    M = to_mf(v2, f2)
    if M.status() != mf.Error.NoError or M.volume() <= 0: M = to_mf(X, ff[:, ::-1])
    return M, {'cells': int((mask > 0.5).sum()), 'area_proj_mm2': round(float((mask > 0.5).sum() * G * G), 1)}


TENT_LAST = {}


def tent_hits(Q):
    """점 Q 가 마지막 텐트 속인지(높이 지도 조회): 베드 위 높이 < T(칸)."""
    t = TENT_LAST; T = t['T']; na, nb = T.shape
    i = np.clip(((Q @ t['u2'] - t['a0']) / G).astype(int) + 1, 0, na - 1); j = np.clip(((Q @ t['v2'] - t['b0']) / G).astype(int) + 1, 0, nb - 1)
    return (Q @ t['n2'] - t['z0']) < T[i, j]


def inside_ex(P0, EX, keep):
    """텐트에 쓸 보호 구역 표본 = 조각 범위 안에 들어온 보호 구역(P0 ∩ EX) 겉면 중 관통 칸이 아닌 것(keep 표본 1.5 mm 안)."""
    X = P0 ^ EX
    if keep is None or len(keep) == 0 or X.volume() < 1.0: return np.zeros((0, 3))
    xs = trimesh.sample.sample_surface_even(trimesh.Trimesh(*from_mf(X), process=False), 200000, seed=3)[0]
    return xs[cKDTree(keep).query(xs, distance_upper_bound=1.5)[0] < 1.5]


def tent_solid(EXs, n_up, pv, cl=0.0, top_pts=None):
    """보호 구역 표본 EXs 밑을 베드(조각 바닥 평면, 위 = n_up)까지 45° 텐트로 파낼 부피.
    높이 지도 Hg(칸마다 보호 구역 맨 위) → 8방향 거리 전파 T = max_e(h_e − 거리) (팔각 원뿔, 경사 ≥ 45° → 천장 브리지 없음, 육각 구멍 뿔과 같은 원리).
    pv: 조각 정점(바닥 평면 z0 = 최소 높이, 칸 범위)."""
    if len(EXs) == 0: return None, {}
    u2, v2, n2 = frame(n_up); z0 = float((pv @ n2).min())
    A, Bv, Z = EXs @ u2, EXs @ v2, EXs @ n2 - z0
    a0, a1 = (pv @ u2).min() - 4, (pv @ u2).max() + 4; b0, b1 = (pv @ v2).min() - 4, (pv @ v2).max() + 4
    k = (Z > -0.5) & (A > a0) & (A < a1) & (Bv > b0) & (Bv < b1); A, Bv, Z = A[k], Bv[k], Z[k] + cl
    if len(Z) == 0: return None, {}
    zm = float(Z.max())                                                           # 격자 = 보호 구역 범위 + 원뿔 반지름(높이)만 (조각 전체 상자로 잡으면 OOM 2026-11-07)
    a0, a1 = max(a0, A.min() - zm - 2), min(a1, A.max() + zm + 2); b0, b1 = max(b0, Bv.min() - zm - 2), min(b1, Bv.max() + zm + 2)
    na, nb = int((a1 - a0) / G) + 3, int((b1 - b0) / G) + 3
    T = np.full((na, nb), -1e9); np.maximum.at(T, (((A - a0) / G).astype(int) + 1, ((Bv - b0) / G).astype(int) + 1), Z)
    sh = [(1, 0, G), (-1, 0, G), (0, 1, G), (0, -1, G), (1, 1, G * 1.4142), (1, -1, G * 1.4142), (-1, 1, G * 1.4142), (-1, -1, G * 1.4142)]
    for _ in range(2000):
        P = np.pad(T, 1, constant_values=-1e9); Tn = T.copy()
        for di, dj, c in sh: Tn = np.maximum(Tn, P[1 - di:1 - di + na, 1 - dj:1 - dj + nb] - c)
        if np.array_equal(Tn, T): break
        T = Tn
    nclamp = 0
    if top_pts is not None and len(top_pts):                                      # 겉면 − TMIN 위로 못 올라가게(대포 돌기 둘레 45° 가 날개 겉면을 278·299 mm² 뚫음, 2026-11-07)
        ti = ((top_pts @ u2 - a0) / G).astype(int) + 1; tj = ((top_pts @ v2 - b0) / G).astype(int) + 1; ok = (ti >= 0) & (ti < na) & (tj >= 0) & (tj < nb)
        Ht = np.full((na, nb), np.inf); np.minimum.at(Ht, (ti[ok], tj[ok]), top_pts[ok] @ n2 - z0)
        Ht = ndimage.minimum_filter(Ht, size=5); lim = Ht - TMIN; nclamp = int((T > lim).sum()); T = np.minimum(T, lim)
    if (T > 0).sum() == 0: return None, {}
    # 닫힌 높이 지도 메시(윗면 = max(T, −1), 바닥 −1.5, 네 옆벽) — 3D 격자 marching cubes 는 OOM(13.5 GB, 2026-11-07)
    Tc = np.maximum(T, -1.0); ii, jj = np.meshgrid(np.arange(na), np.arange(nb), indexing='ij'); idx = ii * nb + jj; N = na * nb
    top = np.c_[ii.ravel() * G + a0 - G, jj.ravel() * G + b0 - G, Tc.ravel()]; bot = top.copy(); bot[:, 2] = -1.5
    a_, b_, c_, d_ = idx[:-1, :-1].ravel(), idx[1:, :-1].ravel(), idx[1:, 1:].ravel(), idx[:-1, 1:].ravel()
    ft = np.r_[np.c_[a_, b_, c_], np.c_[a_, c_, d_]]; fb = ft[:, ::-1] + N
    rim = np.r_[idx[:, 0], idx[-1, 1:], idx[-2::-1, -1], idx[0, -2:0:-1]]; r2 = np.roll(rim, -1)
    fs_ = np.r_[np.c_[rim, rim + N, r2 + N], np.c_[rim, r2 + N, r2]]
    FF = np.r_[ft, fb, fs_]; VV = np.r_[top, bot]
    tmp = trimesh.Trimesh(VV, FF, process=False)
    if tmp.volume < 0: FF = FF[:, ::-1]
    X = np.outer(VV[:, 0], u2) + np.outer(VV[:, 1], v2) + np.outer(VV[:, 2] + z0, n2)
    import fast_simplification as fs
    v2_, f2_ = fs.simplify(X.astype(np.float32), FF.astype(np.int32), target_reduction=0.9)
    M = to_mf(v2_, f2_)
    if M.status() != mf.Error.NoError or M.volume() <= 0: M = to_mf(X, FF)
    TENT_LAST.update({'T': T, 'a0': a0, 'b0': b0, 'u2': u2, 'v2': v2, 'n2': n2, 'z0': z0})
    return M, {'tent_max_mm': round(float(T.max()), 1), 'tent_area_mm2': round(float((T > 0).sum() * G * G), 1), 'clamped_mm2': round(nclamp * G * G, 1)}



def merge_parts(meshes):
    Vs, Fs, o = [], [], 0
    for V, F in meshes: Vs.append(np.asarray(V, float)); Fs.append(np.asarray(F) + o); o += len(V)
    V = np.vstack(Vs); F = np.vstack(Fs)
    u, inv = np.unique(np.round(V * 1e4).astype(np.int64), axis=0, return_inverse=True); inv = inv.ravel()
    V2 = np.zeros((len(u), 3)); V2[inv] = V; F2 = inv[F]
    _, idx, cnt = np.unique(np.sort(F2, axis=1), axis=0, return_inverse=True, return_counts=True); F3 = F2[cnt[idx.ravel()] == 1]
    used = np.unique(F3); rm = -np.ones(len(V2), int); rm[used] = np.arange(len(used))
    return to_mf(V2[used], rm[F3])


def place(M, origin, n):
    """로컬 z → n, 원점 → origin."""
    n = np.asarray(n, float); n /= np.linalg.norm(n)
    e1 = np.cross(n, [0, 0, 1.0]); e1 = e1 if np.linalg.norm(e1) > 1e-3 else np.cross(n, [1.0, 0, 0]); e1 /= np.linalg.norm(e1)
    return M.transform(np.c_[e1, np.cross(n, e1), n, origin].tolist())


def hex_prism(af, h, z0=0.0):
    R = af / np.sqrt(3); return mf.Manifold.cylinder(h, R, R, 6).translate([0, 0, z0])


def hex_hole(af, depth, below=1.0):
    """구멍(빼는 부피): 맞변 af+2CL 육각, 깊이 depth, 위는 45° 육각 뿔(브리지 없음)."""
    R = (af + 2 * CL) / np.sqrt(3)
    return mf.Manifold.cylinder(depth + below, R, R, 6).translate([0, 0, -below]) + mf.Manifold.cylinder(R, R, 0.0, 6).translate([0, 0, depth - 0.05])


def capsule(pts, d, seg=24):
    out = mf.Manifold.sphere(d / 2, seg).translate(list(np.asarray(pts[0], float)))
    for a, b in zip(pts[:-1], pts[1:]):
        a, b = np.asarray(a, float), np.asarray(b, float); Ln = np.linalg.norm(b - a)
        out = out + place(mf.Manifold.cylinder(Ln, d / 2, d / 2, seg), a, (b - a) / Ln) + mf.Manifold.sphere(d / 2, seg).translate(list(b))
    return out


def hex_joint(parent, child, c, n, af, Lp, embed=1.0):
    """자른 면 중심 c, 자식 쪽 법선 n: 부모에 돌기, 자식에 구멍(공차 0.2/쪽, 깊이 L+0.6, 45° 뿔)."""
    return parent + place(hex_prism(af, Lp + embed, -embed), c, n), child - place(hex_hole(af, Lp + 0.6, below=embed), c, n)


def section_center(M, p, n):
    """평면(p, n) 단면의 가장 안쪽 점(극점)과 내접원 반지름 — 돌기 자리·크기."""
    from shapely.ops import unary_union
    from shapely.geometry import MultiPolygon, Polygon
    from shapely.algorithms.polylabel import polylabel
    sec = trimesh.Trimesh(*from_mf(M), process=False).section(plane_origin=p, plane_normal=n)
    P2, Tm = sec.to_2D(); poly = unary_union(list(P2.polygons_full))
    poly = max(poly.geoms, key=lambda g: g.area) if isinstance(poly, MultiPolygon) else poly
    c2 = polylabel(poly, tolerance=0.05); r = poly.exterior.distance(c2)
    for h in poly.interiors: r = min(r, Polygon(h).exterior.distance(c2))
    return (Tm @ np.array([c2.x, c2.y, 0.0, 1.0]))[:3], float(r), float(poly.area)


def limb_split(M, base, s, af=8.0, Lp=6.0, wall=1.2):
    """긴 가지 M(부모 쪽 자른 면 중심 base)을 축 길이 비 s 에서 수직으로: (뿌리 조각 + 돌기, 끝 조각 + 구멍, 정보)."""
    V = from_mf(M)[0]; ax = V.mean(0) - base; ax /= np.linalg.norm(ax); Lx = float(((V - base) @ ax).max()); p = base + ax * s * Lx
    root = M.trim_by_plane((-ax).tolist(), float(-(p @ ax))); tip = M.trim_by_plane(ax.tolist(), float(p @ ax))
    c, r, area = section_center(M, p, ax)
    if r < (af + 2 * CL) / np.sqrt(3) + wall: af = max(4.0, 2 * np.sqrt(3) / 2 * (r - wall) - 2 * CL)     # 단면이 작으면 돌기를 줄임
    root, tip = hex_joint(root, tip, c, ax, af, Lp)
    return root, tip, {'axis': ax.round(5).tolist(), 'cut_point': p.round(3).tolist(), 'peg_center': c.round(3).tolist(), 'section_mm2': round(area, 1),
                       'inradius': round(r, 2), 'peg_af': round(af, 2), 'bodies': [len(root.decompose()), len(tip.decompose())], 'overlap_mm3': round((root ^ tip).volume(), 3)}


def flat_bottom(M, up=(0, 0, 1.0), min_area=150.0, step=0.5, max_cut=15.0):
    """출력 위 방향 up 에서 가장 낮은 곳부터 step 씩 올리며 단면 넓이 합 ≥ min_area 인 높이에서 자르고 아래를 버린다(섬 여러 개도 베드에서 시작)."""
    up = np.asarray(up, float); up /= np.linalg.norm(up); t = trimesh.Trimesh(*from_mf(M), process=False); z0 = float((t.vertices @ up).min()); rows = []
    for dz in np.arange(step, max_cut + 1e-9, step):
        s = t.section(plane_origin=up * (z0 + dz), plane_normal=up)
        if s is None: continue
        a = sum(g.area for g in s.to_2D()[0].polygons_full); rows.append((float(dz), round(a, 1)))
        if a >= min_area: break
    zc = z0 + rows[-1][0]; M2 = M.trim_by_plane(up.tolist(), zc)
    return M2, {'cut_mm': rows[-1][0], 'removed_mm3': round(M.volume() - M2.volume(), 1), 'sections': rows}


def plate_pegs(P, host, surf, d, n_pick=3, af=6.0, Lp=3.0, wall=1.2, min_d=5.0):
    """판 조각 P 의 평면 바닥(−d 를 향한 평평한 면, 겉면에서 ≥ min_d)에서 서로 먼 n_pick 곳: 숙주에 돌기, 판에 납작 천장 구멍(깊이 L+0.4, 천장 꼭짓점 살 ≥ wall).
    뿌리(숙주 쪽 4 mm)가 숙주 속 90 % 이상인 자리만 — 텐트 홈 위 돌기는 떠서 따로 노는 덩어리가 됨."""
    m = trimesh.Trimesh(*from_mf(P), process=False); dd = d / np.linalg.norm(d); Pc, N = m.triangles_center, m.face_normals
    Rh = (af + 2 * CL) / np.sqrt(3); v0 = hex_prism(af, 4.0, -4.0).volume()
    ring = np.array([[np.cos(a), np.sin(a)] for a in np.radians(np.arange(0, 360, 30))]) * Rh
    e1 = np.cross(dd, [0, 0, 1.0]); e1 = e1 if np.linalg.norm(e1) > 1e-3 else np.cross(dd, [1.0, 0, 0]); e1 /= np.linalg.norm(e1); e2 = np.cross(dd, e1)
    dist = surf.query(Pc, workers=-1)[0]
    for ang in (18, 25, 32, 40):
        inner = np.where((dist >= min_d) & ((-N @ dd) > np.cos(np.radians(ang))))[0]
        if len(inner) < 10: continue
        pts = Pc[inner]; top = pts[:, None, :] + dd * (Lp + 0.4) + ring[:, :1] * e1 + ring[:, 1:] * e2
        pts = pts[surf.query(top.reshape(-1, 3), workers=-1)[0].reshape(len(pts), -1).min(1) >= wall]
        alive = np.ones(len(pts), bool); pick = []; ctr = pts.mean(0) if len(pts) else None
        while len(pick) < n_pick and alive.any():
            far = np.linalg.norm(pts - ctr, axis=1) if not pick else np.min(np.linalg.norm(pts[:, None] - pts[pick][None], axis=2), axis=1)
            k = int(np.argmax(np.where(alive, far, -1.0))); alive[np.linalg.norm(pts - pts[k], axis=1) < 3.0] = False
            if (place(hex_prism(af, 4.0, -4.0), pts[k], dd) ^ host).volume() >= 0.9 * v0: pick.append(k)
        if len(pick) < n_pick: continue
        for k in pick:
            host = host + place(hex_prism(af, Lp + 4.0, -4.0), pts[k], dd)
            P = P - place(mf.Manifold.cylinder(Lp + 0.4 + 5.0, Rh, Rh, 6).translate([0, 0, -5.0]), pts[k], dd)
        return P, host, [pts[k].round(2).tolist() for k in pick]
    return P, host, []


def plane_piece(body, SP, lab, d, others=None, protect=None, n_tent=400000):
    """판 조각을 다시 뗀다. body = 틈 없는 원래 몸(숙주 ∪ 조각, merge_parts), SP·lab = 원래 겉면 표본과 '이 조각이면 1' 라벨,
    d = 빼는 방향(겉면이 보이는 쪽), others = 다른 조각 합(빼 줌), protect = 숙주에 남길 보호 구역(물길·돌기, 없으면 None).
    반환: 조각, 숙주(= body − 조각 − 바닥 공차 0.15), 정보(평면 위 법선 bed_n = 출력 때 위, 두께, 텐트, 겹침)."""
    d = np.asarray(d, float); d /= np.linalg.norm(d)
    EXP = trimesh.sample.sample_surface(trimesh.Trimesh(*from_mf(protect), process=False), n_tent, seed=2)[0] if protect is not None else None
    PLN = {}; S, info = column_slab(SP, lab, 1, d, T, EXP, PLN); K, _ = column_slab(SP, lab, 1, d, T + FLOOR, EXP, {})
    P0 = body ^ S
    if others is not None: P0 = P0 - others
    TN, tinfo = (None, {})
    if protect is not None:
        sg = SP[lab == 1]
        TN, tinfo = tent_solid(inside_ex(P0, protect, PLN.get('ex_keep')), np.array(PLN['bed_n']), from_mf(P0)[0], top_pts=sg[:: max(1, len(sg) // 600000)])
        if TN is not None: tinfo['tent_breaks_surface_mm2'] = round(float(tent_hits(sg[:: max(1, len(sg) // 200000)]).mean() * info['area_proj_mm2']), 1)
        P0 = P0 - protect - TN if TN is not None else P0 - protect
    P = keep_big(P0); Kx = K - protect if protect is not None else K
    H = body - Kx - P
    if others is not None: H = H - others
    H = keep_big(H)
    info.update({'plane': {k: v for k, v in PLN.items() if k in ('bed_n', 'thick_mm', 'lp_ok', 'through_mm2')}, 'tent': tinfo,
                 'volume_mm3': round(P.volume(), 1), 'genus': P.genus(), 'host_mm3': round(H.volume(), 1), 'overlap_mm3': round((P ^ H).volume(), 3),
                 'pull_sweep_mm3': {str(t): round((P.translate((d * t).tolist()) ^ H).volume(), 2) for t in (0.5, 2, 8)}})
    return P, H, info
```

## 부록 E — `figcheck.py` (합격 검사)
```python
"""분할 합격 검사 — 조각마다 표로. 하나라도 어긋나면 설계로 돌아간다.
  piece_report(M, up)            닫힘·덩어리·genus·삼각형, 출력 방향(up → +z)에서 접지 mm²·오버행 mm²(45° 넘게 아래를 향한 면, 바닥 0.3 mm 위)
  overlaps(parts)                조각 쌍 겹침 mm³
  pull_sweep(P, others, d)       빼는 방향 d 로 0.5~15 mm 옮기며 걸림 mm³
  voids(orig, parts, tol=0.12)   원래 겉면 표본마다 가장 가까운 조각 겉면까지 거리 > tol 인 넓이 = 겉에서 보이는 틈·턱(의도한 것만 남아야 함)
"""
import numpy as np, trimesh, manifold3d as mf
from scipy.spatial import cKDTree
from figseg import from_mf


def oriented(M, up):
    """up 을 +z 로 돌리고 바닥을 z=0 에."""
    up = np.asarray(up, float); up /= np.linalg.norm(up)
    R = trimesh.geometry.align_vectors(up, [0, 0, 1.0]); t = trimesh.Trimesh(*from_mf(M), process=False); t.apply_transform(R)
    t.apply_translation([0, 0, -t.bounds[0][2]]); return t


def piece_report(M, up=(0, 0, 1.0), max_overhang_deg=45.0):
    t = oriented(M, up); A, N, C = t.area_faces, t.face_normals, t.triangles_center
    bed = A[(C[:, 2] < 0.05) & (N[:, 2] < -0.99)].sum()
    down = (N[:, 2] < -np.cos(np.radians(90 - max_overhang_deg))) & (C[:, 2] > 0.3)
    return {'bodies': len(M.decompose()), 'genus': M.genus(), 'tris': len(t.faces), 'volume_mm3': round(M.volume(), 1),
            'size_mm': np.round(t.extents, 1).tolist(), 'bed_mm2': round(float(bed), 1), 'overhang_mm2': round(float(A[down].sum()), 1),
            'ok_bed': bool(bed >= 100.0), 'ok_tris': bool(len(t.faces) <= 200000)}


def overlaps(parts):
    ks = list(parts); out = {}
    for i, a in enumerate(ks):
        for b in ks[i + 1:]:
            v = (parts[a] ^ parts[b]).volume()
            if v > 0.01: out[f'{a}-{b}'] = round(v, 3)
    return out


def pull_sweep(P, others, d, steps=(0.5, 1, 2, 4, 8, 15)):
    d = np.asarray(d, float); d /= np.linalg.norm(d)
    return {str(s): round((P.translate((d * s).tolist()) ^ others).volume(), 2) for s in steps}


def voids(orig, parts, tol=0.12, n=300000, link=1.0):
    """orig: 원래 닫힌 메시(trimesh), parts: {이름: Manifold}. 틈 덩어리(1 mm 안 점끼리)별 넓이·최대 폭·중심·가까운 조각."""
    pts = trimesh.sample.sample_surface_even(orig, n, seed=0)[0]; a_pt = orig.area / len(pts)
    best = np.full(len(pts), np.inf); who = np.full(len(pts), '', object)
    for k, M in parts.items():
        t = trimesh.Trimesh(*from_mf(M), process=False)
        cand = cKDTree(trimesh.sample.sample_surface_even(t, 400000, seed=1)[0]).query(pts, distance_upper_bound=tol + 2.0)[0] < tol + 2.0
        if cand.any():
            dd = np.abs(trimesh.proximity.closest_point(t, pts[cand])[1]); sel = np.where(cand)[0]; better = dd < best[sel]
            best[sel[better]] = dd[better]; who[sel[better]] = k
    gap = best > tol; g = np.where(gap)[0]; clusters = []
    if len(g):
        import scipy.sparse as sp, scipy.sparse.csgraph as cg
        pr = cKDTree(pts[g]).query_pairs(link, output_type='ndarray')
        _, lab = cg.connected_components(sp.coo_matrix((np.ones(len(pr)), (pr[:, 0], pr[:, 1])), shape=(len(g), len(g))), directed=False)
        for c in np.unique(lab):
            s = g[lab == c]
            if len(s) * a_pt < 2.0: continue
            gm = best[s][np.isfinite(best[s])]
            clusters.append({'area_mm2': round(len(s) * a_pt, 1), 'max_gap_mm': round(float(gm.max()), 2) if len(gm) else None,
                             'center': np.round(pts[s].mean(0), 1).tolist(), 'near': sorted(set(who[s]) - {''})})
    return {'gap_area_mm2': round(float(gap.sum() * a_pt), 1), 'clusters': sorted(clusters, key=lambda c: -c['area_mm2'])}
```

## 부록 F — 한 번에 돌리는 예
```python
import numpy as np, trimesh, figseg as S, figsplit as X, figcheck as Q
d = np.load('fig.npz'); V, F, C = d['V'], d['F'], d['C']
col, patch, patches, rgb = S.regions(V, F, C, k=5)                 # 영역 → 사용자에게 보여 이름 정하기
A = trimesh.Trimesh(V, F, process=False).area_faces
lab = S.label_faces(F, patch, A, {12: 'head', 7: 'armR', 9: 'armL', 3: 'shell', 5: 'belly'})
out = S.separate_fill(V, F, lab, ['head', 'armR', 'armL', 'shell', 'belly'])
M = {k: S.to_mf(v[0], v[1]) for k, v in out.items()}
# 판: 틈 없는 원래 몸에서 평면 바닥으로 다시
org = trimesh.Trimesh(V, F, process=False); SP, fi = trimesh.sample.sample_surface(org, 3000000, seed=0)
sh = S.label_faces(F, patch, A, {3: 'shell'}) == 'shell'; labs = np.where(sh[fi], 1, -1)
body = X.merge_parts([out['core'][:2], out['shell'][:2]])
M['shell'], M['core'], info = X.plane_piece(body, SP, labs, d=[0, 0.95, 0.31])
# 긴 팔
M['armR'], M['handR'], li = X.limb_split(M['armR'], np.array(out['armR'][2]['cap_p0']), 0.4)
# 몸통 바닥, 결합
M['core'], fb = X.flat_bottom(M['core'])
c, r, _ = X.section_center(M['head'], np.array(out['head'][2]['cap_p0']) + 0.01, np.array(out['head'][2]['cap_n']))
M['core'], M['head'] = X.hex_joint(M['core'], M['head'], c, out['head'][2]['cap_n'], af=14, Lp=10)
print(Q.overlaps(M)); print(Q.voids(org, M)['clusters'][:5])
```
