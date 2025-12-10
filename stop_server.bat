@echo off
echo Streamlitサーバーを停止しています...

REM Streamlitプロセスを検索して終了
taskkill /F /IM streamlit.exe 2>nul
if %errorlevel% == 0 (
    echo Streamlitサーバーを停止しました。
) else (
    echo Streamlitプロセスが見つかりませんでした。
)

REM Pythonプロセスでstreamlitを実行している場合も終了
for /f "tokens=2" %%a in ('netstat -ano ^| findstr :8501') do (
    taskkill /F /PID %%a 2>nul
    echo ポート8501を使用しているプロセスを終了しました。
)

pause

