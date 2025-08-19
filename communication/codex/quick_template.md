git -c diff.mnemonicprefix=false -c core.quotepath=false --no-optional-locks push -v --tags origin main:main
POST git-receive-pack (768 bytes)
Pushing to https://github.com/etloveaui/100xFenok
To https://github.com/etloveaui/100xFenok
 ! [remote rejected] main -> main (refusing to allow an OAuth App to create or update workflow `.github/workflows/telegram-notify.yml` without `workflow` scope)
error: failed to push some refs to 'https://github.com/etloveaui/100xFenok'


Completed with errors, see above.
## 100xFenok Push Quick Fix (Short)

핵심: 100xFenok이 모노레포 하위폴더인지, 독립 저장소인지 먼저 확인.

- 모노레포(현재 워크스페이스 루트가 Git 루트):
  - `git add projects/100xFenok/*`
  - `git commit -m "update 100xFenok"`
  - `git push origin main`

- 독립 저장소(100xFenok 자체가 Git 루트):
  - `cd projects/100xFenok`
  - `git remote -v` (없으면)
    - `git init && git branch -M main`
    - `git remote add origin <repo-url>`
  - `git add . && git commit -m "update"`
  - `git push -u origin main`

자주 막히는 원인→대응
- upstream 미설정: `git push -u origin main`
- pull 필요(rejected): `git pull --rebase origin main` 후 재푸시
- 훅/필터 차단: `secrets/*`, `.agents/locks/*` 제외하고 커밋
- LFS 필요 대용량: `git lfs track <pattern>` 후 재시도

Actions 연동 확인(텔레그램)
- 워크플로 위치: 해당 저장소 루트 `.github/workflows/telegram-notify.yml`
- 시크릿: `TELEGRAM_BOT_TOKEN` 존재
- 트리거: 대상 HTML 변경 후 push 또는 Actions → Run workflow



git -c diff.mnemonicprefix=false -c core.quotepath=false --no-optional-locks push -v --tags origin main:main
POST git-receive-pack (768 bytes)
Pushing to https://github.com/etloveaui/100xFenok
To https://github.com/etloveaui/100xFenok
 ! [remote rejected] main -> main (refusing to allow an OAuth App to create or update workflow `.github/workflows/telegram-notify.yml` without `workflow` scope)
error: failed to push some refs to 'https://github.com/etloveaui/100xFenok'


Completed with errors, see above.
