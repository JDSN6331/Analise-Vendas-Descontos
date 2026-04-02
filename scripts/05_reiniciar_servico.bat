@echo off
:: Reinicia o servico do Dashboard Analytics

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Execute como ADMINISTRADOR!
    pause
    exit /b 1
)

set NSSM_PATH=%~dp0nssm.exe

echo [INFO] Reiniciando servico...
"%NSSM_PATH%" restart DashboardAnalytics

echo.
echo Servico reiniciado.
echo Acesse: http://172.16.253.34:5050
pause
