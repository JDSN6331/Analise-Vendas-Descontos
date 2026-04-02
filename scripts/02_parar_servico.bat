@echo off
:: Para o servico do Dashboard Analytics

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Execute como ADMINISTRADOR!
    pause
    exit /b 1
)

set NSSM_PATH=%~dp0nssm.exe
"%NSSM_PATH%" stop DashboardAnalytics

echo.
echo Servico parado.
pause
