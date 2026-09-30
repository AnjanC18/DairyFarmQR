@echo off
echo ==========================================================
echo  Starting Smart Dairy Farm Management System...
echo ==========================================================
cd /d "%~dp0DairyFarmQR-main"

echo [1/2] Installing/verifying dependencies...
pip install -r requirements.txt

echo [2/2] Launching application...
echo ----------------------------------------------------------
echo  App URL: http://localhost:5000
echo  Credentials: admin / admin123
echo ----------------------------------------------------------
python app.py
pause
