@echo off
:: Inicia o servico do Dashboard Analytics

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Execute como ADMINISTRADOR!
    pause
    exit /b 1
)

set NSSM_PATH=%~dp0nssm.exe
"%NSSM_PATH%" start DashboardAnalytics

echo.
echo Servico iniciado.
echo Acesse: http://172.16.253.34:5050
pause
