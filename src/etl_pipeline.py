import pandas as pd
import requests
import io
import os
from sqlalchemy import create_engine

URL_CFTC = 'https://www.cftc.gov/dea/newcot/FinFutWk.txt'
CONNECTION_STRING = 'mssql+pyodbc://sa:Dados%402026Strong@127.0.0.1:1433/MercadoFinanceiro?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes'

def run_pipeline():
    print('\n🚀 [ETL] Iniciando...')
    try:
        response = requests.get(URL_CFTC)
        data_io = io.StringIO(response.text)
        df = pd.read_csv(data_io, header=None, low_memory=False)
        
        df_final = df[[0, 2, 8, 9]].copy()
        df_final.columns = ['nome_ativo', 'data_referencia', 'Comprados', 'Vendidos']
        for col in ['Comprados', 'Vendidos']:
            df_final[col] = pd.to_numeric(df_final[col], errors='coerce').fillna(0)

        # Salva CSV na RAIZ
        csv_path = 'dados_dashboard.csv'
        df_final.to_csv(csv_path, index=False)
        print(f'✅ CSV Atualizado: {csv_path}')

        try:
            engine = create_engine(CONNECTION_STRING)
            df.to_sql('raw_cftc', con=engine, if_exists='replace', index=False)
            print('💾 SQL Local atualizado.')
        except:
            pass

    except Exception as e:
        print(f'❌ Erro: {e}')

if __name__ == '__main__':
    run_pipeline()
