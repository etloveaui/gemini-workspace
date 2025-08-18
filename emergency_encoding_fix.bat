@echo off
chcp 65001 > nul
echo "=== 긴급 인코딩 수정 배치 스크립트 ==="

REM 환경변수 설정
setx PYTHONIOENCODING "utf-8" > nul
setx PYTHONLEGACYWINDOWSFSENCODING "utf-8" > nul

REM Git 설정
git config --global core.quotepath false
git config --global i18n.filesEncoding utf-8
git config --global i18n.commitEncoding utf-8
git config --global i18n.logOutputEncoding utf-8
git config --global core.autocrlf false
git config --global core.safecrlf false

REM Git 저장소 새로고침
git add .gitattributes
git rm --cached -r .
git reset --hard HEAD

echo "긴급 인코딩 수정 완료 - 새 터미널에서 확인하세요"
pause