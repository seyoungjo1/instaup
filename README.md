# instaup

@sy_3dprintgarage 인스타그램 게시용 **임시 공개 저장소**입니다.

- 게시할 영상·사진만 게시 직전에 잠깐 올립니다. Instagram API 가 공개 주소(raw.githubusercontent.com)에서 파일을 가져가야 해서입니다.
- 게시가 끝나면 파일을 지우고 이력도 이 README·`site/`·`.github/` 만 남게 되돌립니다(강제 푸시).
- 게시글 자료(본문·스크립트·원본·기록)는 비공개 저장소 3mf-maker 의 `instagram/` 에만 둡니다.

## site/ — josseng-garage.pages.dev (지우지 않음)
- 공유용 공개 페이지. `site/` 에 올리면 Actions(`.github/workflows/pages.yml`, wrangler)가 Cloudflare Pages 프로젝트 josseng-garage 로 배포합니다. 저장소 Secrets: `CLOUDFLARE_API_TOKEN`(Pages Edit)·`CLOUDFLARE_ACCOUNT_ID`.
- `site/tripo-figure-print/SKILL.md` — 사진으로 Tripo 피규어를 만들고 출력용으로 분할하는 Claude 스킬(코드 포함).
