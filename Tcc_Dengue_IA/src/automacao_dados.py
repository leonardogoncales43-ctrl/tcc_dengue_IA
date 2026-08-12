import requests
import pandas as pd
from datetime import datetime

def coletar_clima_sjc():
    print("Conectando aos dados climaticos...")

    #Coordenadas exatas de São José dos Campos
    lat = -23.1791
    lon = -45.8872

    #Endereço da API, pedindo dados dos ultimos 28 dias
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_mean,relative_humidity_2m_mean&past_days=28&timezone=America%2FSao_Paulo"

    #Disparando a requisição
    resposta = requests.get(url)

    #Código 200 significa "Sucesso"
    if resposta.status_code == 200:
        dados = resposta.json() #Transforma a resposta em um formato legivel

        #Montando a tabela com os dados vindos do json
        df_clima = pd.DataFrame({
            'Data': dados['daily']['time'],
            'Temp_media_C': dados['daily']['temperature_2m_mean'],
            'Umid_media_%': dados['daily']['relative_humidity_2m_mean']
        })

        #Garante ao pandas que data é realmente do dipo data
        df_clima['data'] = pd.to_datetime(df_clima['Data'])
        print("Dados climaticos atualizados obtidos com sucesso!")
        return df_clima

    else:
        print(f"Erro ao conectar API . Código do erro {resposta.status_code}")
        return None

if __name__ == "__main__":
    tabela_clima = coletar_clima_sjc()

    if tabela_clima is not None:
        print("\nÚltimos 5 dias e Previsão de SJC:")
        print(tabela_clima.tail(7).to_string(index=False))