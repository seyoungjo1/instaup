# 내장 폰트

전부 SIL Open Font License 1.1(OFL) — 개인·상업 출력물에 무료로 쓸 수 있고, 폰트 파일 자체를 팔 수만 없습니다. 라이선스 전문 `OFL.txt`.

| 파일 | 이름 | 출처 |
|---|---|---|
| NanumGothicBold / NanumGothic / NanumBarunGothicBold / NanumSquareB / NanumSquareRoundB / NanumMyeongjoBold / NanumGothicCodingBold | 나눔 글꼴 | 네이버(NAVER) · Ubuntu fonts-nanum |
| BlackHanSans-Regular | 검은고딕 | Zess Type · google/fonts |
| Jua-Regular | 주아 | 우아한형제들 · google/fonts |
| DoHyeon-Regular | 도현 | 우아한형제들 · google/fonts |
| Gaegu-Bold | 개구 | JIKJI SOFT · google/fonts |
| Dongle-Bold | 동글 | Yoon Design · google/fonts |
| Sunflower-Bold | 해바라기 | JIKJI SOFT · google/fonts |
| YeonSung-Regular | 연성 | Woowahan Brothers(Yeon Sung) · google/fonts |
| BagelFatOne-Regular | 베이글 팻 원 | JAMO · google/fonts |

## 다시 저장한 파일 (2026-11-06)
`NanumGothic.ttf`·`NanumGothicBold.ttf` — Ubuntu fonts-nanum 판에 글꼴 제작 도구(VTT) 작업용 표 TSI0/1/2/3/5 가 남아 있었고
그중 TSI3 이 길이 0 이라 브라우저의 OTS 검사가 파일을 통째로 거부했다(편집기가 대체 세리프로 보임, 1회차 E4).
fontTools 로 그 다섯 표만 빼고 다시 저장했다(`recalcBBoxes=False`, 글리프·힌팅·kern 그대로).
글자 모양이 같은지는 `test/model/fonts.test.ts`(고치기 전 면적 `test/model/fixtures/font-areas-before.json`)가,
나머지 13종도 빈 표·TSI 표가 없는지 같은 시험이 확인한다. 15종 모두 `ots-sanitize` 통과, 크롬 FontFace 'loaded'.
