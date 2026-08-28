import os
import requests
import pandas as pd

def coletar_dados_infodengue(codigo_ibge=3549904):
    url = f"https://info.dengue.mat.br/api/alertcity?geocode={codigo_ibge}&disease=dengue&format=json&ew_start=1&ew_end=53&ey_start=2023&ey_end=2026"
    
    print("🌐 Baixando dados atualizados do InfoDengue...")
    response = requests.get(url)
    
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
        pasta_raw = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
        os.makedirs(pasta_raw, exist_ok=True)
        
        caminho_saida = os.path.join(pasta_raw, f"infodengue_{codigo_ibge}.csv")
        df.to_csv(caminho_saida, index=False)
        print(f"✅ Dados da API salvos em: {caminho_saida}")
    else:
        print(f"❌ Erro ao acessar API InfoDengue: {response.status_code}")

if __name__ == "__main__":
    coletar_dados_infodengue()
