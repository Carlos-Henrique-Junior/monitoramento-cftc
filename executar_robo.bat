@echo off
cd /d "D:\Projetos\Projeto_CFTC"
call .venv\Scripts\activate

echo 1. Baixando e Tratando Dados (ETL)...
python src/etl_pipeline.py

echo 2. Atualizando Banco de Dados Local (SQL Server)...
python src/banco_dados.py

echo 3. Enviando atualizacao para o Dashboard Online...
git add .
git commit -m "Auto: Atualizacao semanal dos dados"
git push origin master

echo ? Tudo pronto! Pode fechar.
pause