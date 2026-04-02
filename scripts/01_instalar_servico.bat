@echo off
:: ============================================
:: Instalador do Servico - Dashboard Analytics
:: Cooxupe Sales Analytics
:: ============================================
:: Este script instala o servidor Flask como
:: um servico do Windows que inicia automaticamente.
:: ============================================

echo.
echo ============================================
echo   INSTALADOR DO SERVICO - DASHBOARD ANALYTICS
echo ============================================
echo.

:: Verificar se esta rodando como administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Este script precisa ser executado como ADMINISTRADOR!
    echo.
    echo Clique com o botao direito no arquivo e selecione
    echo "Executar como administrador"
    echo.
    pause
    exit /b 1
)

:: Definir variaveis - caminhos absolutos para garantir funcionamento do servico
set SCRIPT_DIR=%~dp0
for %%I in ("%~dp0..") do set "ROOT_DIR=%%~sfI\"
set SERVICE_NAME=DashboardAnalytics
set DISPLAY_NAME=Cooxupe Dashboard Analytics
set "PYTHON_PATH=C:\Users\joseduque\AppData\Local\Programs\Python\Python313\python.exe"
set "SERVER_SCRIPT=%ROOT_DIR%analytics\server.py"

:: Verificar se NSSM existe, senao baixar
set NSSM_PATH=%SCRIPT_DIR%nssm.exe

if not exist "%NSSM_PATH%" (
    echo [INFO] NSSM nao encontrado. Baixando...
    echo.
    
    :: Tentar baixar do GitHub (mirror mais confiavel)
    echo [INFO] Tentando fonte 1: GitHub...
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { Invoke-WebRequest -Uri 'https://github.com/kirillkovalenko/nssm/releases/download/v2.24-101-g897c7ad/nssm-2.24-101-g897c7ad.zip' -OutFile '%SCRIPT_DIR%nssm.zip' -TimeoutSec 30 } catch { exit 1 }}"
    
    if not exist "%SCRIPT_DIR%nssm.zip" (
        echo [INFO] Fonte 1 falhou. Tentando fonte 2: nssm.cc...
        powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.24.zip' -OutFile '%SCRIPT_DIR%nssm.zip' -TimeoutSec 30 } catch { exit 1 }}"
    )
    
    if not exist "%SCRIPT_DIR%nssm.zip" (
        echo.
        echo [ERRO] Falha ao baixar NSSM automaticamente.
        echo.
        echo Por favor, baixe manualmente:
        echo   1. Acesse: https://github.com/kirillkovalenko/nssm/releases
        echo   2. Baixe o arquivo .zip
        echo   3. Extraia o nssm.exe para: %SCRIPT_DIR%
        echo.
        pause
        exit /b 1
    )
    
    :: Extrair NSSM
    echo [INFO] Extraindo NSSM...
    powershell -Command "& {Expand-Archive -Path '%SCRIPT_DIR%nssm.zip' -DestinationPath '%SCRIPT_DIR%nssm_temp' -Force}"
    
    :: Procurar e copiar executavel (64-bit)
    for /r "%SCRIPT_DIR%nssm_temp" %%f in (nssm.exe) do (
        echo %%f | findstr /i "win64" >nul
        if not errorlevel 1 (
            copy "%%f" "%NSSM_PATH%" >nul
            goto :nssm_found
        )
    )
    :: Se nao encontrou win64, pegar qualquer nssm.exe
    for /r "%SCRIPT_DIR%nssm_temp" %%f in (nssm.exe) do (
        copy "%%f" "%NSSM_PATH%" >nul
        goto :nssm_found
    )
    
    :nssm_found
    :: Limpar arquivos temporarios
    rmdir /s /q "%SCRIPT_DIR%nssm_temp" 2>nul
    del "%SCRIPT_DIR%nssm.zip" 2>nul
    
    if not exist "%NSSM_PATH%" (
        echo [ERRO] Falha ao extrair NSSM.
        pause
        exit /b 1
    )
    
    echo [OK] NSSM baixado com sucesso!
    echo.
)

:: Verificar se o servico ja existe e remover
echo [INFO] Verificando servico existente...
"%NSSM_PATH%" status %SERVICE_NAME% >nul 2>&1
if %errorLevel% equ 0 (
    echo [INFO] Removendo servico anterior...
    "%NSSM_PATH%" stop %SERVICE_NAME% >nul 2>&1
    "%NSSM_PATH%" remove %SERVICE_NAME% confirm >nul 2>&1
    timeout /t 2 >nul
)

:: Instalar o servico
echo [INFO] Instalando servico...
"%NSSM_PATH%" install %SERVICE_NAME% "%PYTHON_PATH%" "%SERVER_SCRIPT%"

:: Configurar o servico
echo [INFO] Configurando servico...
"%NSSM_PATH%" set %SERVICE_NAME% DisplayName "%DISPLAY_NAME%"
"%NSSM_PATH%" set %SERVICE_NAME% Description "Servidor web do Dashboard de Analytics da Cooxupe"
"%NSSM_PATH%" set %SERVICE_NAME% AppDirectory "%ROOT_DIR:~0,-1%"
"%NSSM_PATH%" set %SERVICE_NAME% Start SERVICE_AUTO_START
"%NSSM_PATH%" set %SERVICE_NAME% AppStdout "%ROOT_DIR%logs\service.log"
"%NSSM_PATH%" set %SERVICE_NAME% AppStderr "%ROOT_DIR%logs\service_error.log"
"%NSSM_PATH%" set %SERVICE_NAME% AppRotateFiles 1
"%NSSM_PATH%" set %SERVICE_NAME% AppRotateBytes 1048576

:: Criar pasta de logs se nao existir
if not exist "%ROOT_DIR%logs" mkdir "%ROOT_DIR%logs"

:: Iniciar o servico
echo [INFO] Iniciando servico...
"%NSSM_PATH%" start %SERVICE_NAME%

:: Verificar status
timeout /t 2 >nul
"%NSSM_PATH%" status %SERVICE_NAME% | findstr /i "running" >nul
if %errorLevel% equ 0 (
    echo.
    echo ============================================
    echo   SERVICO INSTALADO COM SUCESSO!
    echo ============================================
    echo.
    echo O Dashboard Analytics agora inicia automaticamente
    echo com o Windows e roda em segundo plano.
    echo.
    echo Acesse: http://172.16.253.34:5050
    echo.
    echo Para gerenciar o servico:
    echo   - Parar:      02_parar_servico.bat
    echo   - Iniciar:    03_iniciar_servico.bat
    echo   - Remover:    04_remover_servico.bat
    echo   - Reiniciar:  05_reiniciar_servico.bat
    echo   - Status:     06_status_servico.bat
    echo.
) else (
    echo.
    echo [AVISO] O servico foi instalado, mas pode nao ter iniciado.
    echo Verifique os logs em: %ROOT_DIR%logs\
    echo.
)

pause
