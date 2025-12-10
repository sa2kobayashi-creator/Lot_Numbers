# Streamlitサーバー停止スクリプト (PowerShell版)

Write-Host "Streamlitサーバーを停止しています..." -ForegroundColor Yellow

# Streamlitプロセスを検索
$streamlitProcesses = Get-Process -Name "streamlit" -ErrorAction SilentlyContinue

if ($streamlitProcesses) {
    foreach ($proc in $streamlitProcesses) {
        Write-Host "プロセスID $($proc.Id) を終了しています..." -ForegroundColor Green
        Stop-Process -Id $proc.Id -Force
    }
    Write-Host "Streamlitサーバーを停止しました。" -ForegroundColor Green
} else {
    Write-Host "Streamlitプロセスが見つかりませんでした。" -ForegroundColor Yellow
}

# ポート8501を使用しているプロセスも終了
$port8501 = Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue
if ($port8501) {
    $pid = $port8501.OwningProcess
    if ($pid) {
        Write-Host "ポート8501を使用しているプロセス (PID: $pid) を終了しています..." -ForegroundColor Green
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        Write-Host "ポート8501のプロセスを終了しました。" -ForegroundColor Green
    }
}

Write-Host "`n完了しました。" -ForegroundColor Cyan
Read-Host "Enterキーを押して終了"

