@echo off
echo --- ROBÔ CARLOS HENRIQUE ---
cd /d "D:\Projetos\Projeto_CFTC"

:: Roda o Python
".venv\Scripts\python.exe" "src\etl_pipeline.py"

:: Git Push
git add dados_dashboard.csv
git commit -m "Update Diario"
git push origin master
