import pandas as pd
import requests
import io
import zipfile
import urllib3

# Desabilita o aviso chato de SSL (certificado)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# URL do histórico de 2026 (Traders in Financial Futures)
URL_HISTORICO_2026 = "https://www.cftc.gov/files/dea/history/fut_fin_txt_2026.zip"

def run_etl():
    print(f"⏳ Baixando histórico CFTC 2026...")
    
    try:
        # 1. Baixa o arquivo ZIP (com verify=False para pular erro de SSL)
        response = requests.get(URL_HISTORICO_2026, verify=False)
        response.raise_for_status()
        
        # 2. Abre o ZIP na memória
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            nome_arquivo_txt = z.namelist()[0]
            print(f"📦 Processando arquivo: {nome_arquivo_txt}")
            
            with z.open(nome_arquivo_txt) as f:
                # 3. Lê o CSV com os índices CORRETOS para Financial Futures (TFF)
                # Índice 1: Data (YYMMDD)
                # Índice 9: Leveraged Funds Long (Comprados)
                # Índice 10: Leveraged Funds Short (Vendidos)
                df = pd.read_csv(
                    f, 
                    header=None,
                    encoding='utf-8',
                    usecols=[0, 1, 9, 10], 
                    names=['nome_ativo', 'data_raw', 'Comprados', 'Vendidos']
                )

        # 4. Tratamento de Dados
        # Converte Data (YYMMDD -> DateTime)
        df['data_referencia'] = pd.to_datetime(df['data_raw'], format='%y%m%d', errors='coerce')
        
        # Remove linhas que falharam na conversão de data
        df = df.dropna(subset=['data_referencia'])
        
        # Garante que números são inteiros
        df['Comprados'] = pd.to_numeric(df['Comprados'], errors='coerce').fillna(0).astype(int)
        df['Vendidos'] = pd.to_numeric(df['Vendidos'], errors='coerce').fillna(0).astype(int)
        
        # Limpa espaços em branco no nome
        df['nome_ativo'] = df['nome_ativo'].str.strip()

        # 5. Filtra e Ordena (Garante só 2026 em diante)
        df_final = df[['data_referencia', 'nome_ativo', 'Comprados', 'Vendidos']].copy()
        df_final = df_final.sort_values(by='data_referencia')

        # Salva o arquivo final
        df_final.to_csv("dados_dashboard.csv", index=False)
        
        print("✅ Sucesso Absoluto!")
        print(f"📊 Total de Registros: {len(df_final)}")
        print(f"📅 Período dos Dados: {df_final['data_referencia'].min().strftime('%d/%m/%Y')} até {df_final['data_referencia'].max().strftime('%d/%m/%Y')}")

    except Exception as e:
        print(f"❌ Erro no ETL: {e}")

if __name__ == "__main__":
    run_etl()