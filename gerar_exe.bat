@echo off
echo Gerando AspersorETo.exe ...
python -m pip install --upgrade pyinstaller pywebview --quiet
python -m PyInstaller --onefile --windowed --name "AspersorETo" --add-data "index.html;." aspersor_eto_app.py
echo.
echo Pronto. Executavel em: dist\AspersorETo.exe
pause
