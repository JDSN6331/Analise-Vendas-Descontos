@echo off
:: Remove o servico do Dashboard Analytics

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Execute como ADMINISTRADOR!
    pause
    exit /b 1
)

set NSSM_PATH=%~dp0nssm.exe
"%NSSM_PATH%" stop DashboardAnalytics >nul 2>&1
"%NSSM_PATH%" remove DashboardAnalytics confirm

echo.
echo Servico removido.
echo O Dashboard nao iniciara mais automaticamente.
pause
