@echo off
cd /d "C:\Users\nico\Desktop\Api XTB"

:: Abrir ngrok en nueva ventana
start cmd /k "ngrok http 5000"

:: Esperar 3 segundos para que ngrok levante la URL
timeout /t 3 /nobreak >nul

:: Abrir servidor Flask en otra ventana
start cmd /k "python servidor.py"

exit