@echo off
:: Verifica o status do servico do Dashboard Analytics

set NSSM_PATH=%~dp0nssm.exe

echo.
echo ============================================
echo   STATUS DO SERVICO - DASHBOARD ANALYTICS
echo ============================================
echo.

"%NSSM_PATH%" status DashboardAnalytics

echo.
echo ============================================
echo.
echo Se o status for "SERVICE_RUNNING", o servico esta ativo.
echo Acesse: http://172.16.253.34:5050
echo.
pause
