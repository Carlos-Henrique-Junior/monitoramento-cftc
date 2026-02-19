import pandas as pd
from sqlalchemy import create_engine
import urllib.parse # Importante para corrigir a senha

# --- CONFIGURAÇÕES ---
SERVER = '127.0.0.1'
PORT = '1433'
DATABASE = 'MercadoFinanceiro'
USER = 'sa'
PASSWORD_RAW = 'Dados@2026Strong' # Sua senha original com @
DRIVER = 'ODBC Driver 17 for SQL Server'

def salvar_no_sql_server():
    print(f"🔌 Conectando ao SQL Server (Docker)...")
    
    try:
        # 1. TRATAMENTO DA SENHA (O Pulo do Gato 🐱)
        # Transforma 'Dados@2026Strong' em 'Dados%402026Strong' para não quebrar a conexão
        password_encoded = urllib.parse.quote_plus(PASSWORD_RAW)
        
        # 2. Monta a string de conexão correta
        connection_string = (
            f"mssql+pyodbc://{USER}:{password_encoded}@{SERVER}:{PORT}/{DATABASE}"
            f"?driver={urllib.parse.quote_plus(DRIVER)}"
            f"&TrustServerCertificate=yes"
        )
        
        # Cria a engine
        engine = create_engine(connection_string)

        # 3. Lê e Salva
        print("📂 Lendo dados_dashboard.csv...")
        df = pd.read_csv('dados_dashboard.csv')
        
        df['data_referencia'] = pd.to_datetime(df['data_referencia'])
        
        print(f"💾 Salvando {len(df)} registros na tabela 'TB_COT_REPORT'...")
        df.to_sql(name='TB_COT_REPORT', con=engine, if_exists='replace', index=False)
        
        print("✅ Sucesso! Dados salvos no SQL Server local.")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("-" * 50)
        print("Dicas de Resolução:")
        print("1. O Docker está rodando? (comando: docker ps)")
        print("2. O banco 'MercadoFinanceiro' existe? (Crie no DBeaver)")

if __name__ == "__main__":
    salvar_no_sql_server()