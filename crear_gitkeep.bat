@echo off
echo Creando archivos .gitkeep...

cd /d "C:\Proyectos\inventory-system"

echo. > data\sap_descargas\.gitkeep
echo Creado: data\sap_descargas\.gitkeep

echo. > data\raw\.gitkeep
echo Creado: data\raw\.gitkeep

echo. > data\processed\.gitkeep
echo Creado: data\processed\.gitkeep

echo. > outputs\.gitkeep
echo Creado: outputs\.gitkeep

echo.
echo Listo! Todos los archivos .gitkeep creados
echo.
pause