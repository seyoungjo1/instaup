# route3d-kr — 동선 3D 출력기 '우리동네 출력' 행정경계

- 시도 → 시군구 → (일반구) → 읍면동 경계. `index.json`(목록) + `<시도코드>.json`(경계, 좌표 1e-5° 정수 차분 [x0,y0,dx,dy,…], 경도·위도 순).
- 원자료: 행정동 경계 [vuski/admdongkor](https://github.com/vuski/admdongkor) ver20261001(통계청 행정동 경계 가공). 동을 합쳐 상위 경계를 만들고 단순화(5~30 m).
- 만드는 도구: 3mf-maker `tools/kr_admin.py`. 앱: https://josseng-garage.pages.dev/3d-tracker
