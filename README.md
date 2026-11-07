# instaup

@sy_3dprintgarage 인스타그램 게시용 **임시 공개 저장소**입니다.

- 게시할 영상·사진만 게시 직전에 잠깐 올립니다. Instagram API 가 공개 주소(raw.githubusercontent.com)에서 파일을 가져가야 해서입니다.
- 게시가 끝나면 파일을 지우고 이력도 이 README·`site/`·`.github/` 만 남게 되돌립니다(강제 푸시).
- 게시글 자료(본문·스크립트·원본·기록)는 비공개 저장소 3mf-maker 의 `instagram/` 에만 둡니다.

## site/ — josseng-garage.pages.dev (지우지 않음)
- 공유용 공개 페이지(Cloudflare Pages 프로젝트 josseng-garage). `site/` 는 원본 보관, 배포는 3mf-maker `share/tripo-figure-skill/deploy_cf.py`(Cloudflare API 로 `_worker.js` 배포). 열림 확인은 Actions `pages-check`(수동).
- `site/tripo-figure-print/SKILL.md` — 사진으로 Tripo 피규어를 만들고 출력용으로 분할하는 Claude 스킬(코드 포함).
