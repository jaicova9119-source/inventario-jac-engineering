@echo off
title Sistema de Inventario - JAC Engineering
color 0A

echo.
echo ========================================================
echo    SISTEMA DE CONTROL DE INVENTARIO
echo    JAC Engineering SAS
echo    Electrical Systems ^& Data Intelligence
echo ========================================================
echo.
echo [INFO] Iniciando aplicacion...
echo.
echo Abriendo navegador en 3 segundos...
echo.

cd /d "C:\Proyectos\inventory-system"

REM Abrir navegador automaticamente despues de 3 segundos
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:8501"

REM Iniciar Streamlit
streamlit run app/app.py

pause