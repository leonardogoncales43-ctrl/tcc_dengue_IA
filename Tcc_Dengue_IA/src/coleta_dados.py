import os
import requests
import pandas as pd


def baixar_dados_dengue(codigo_ibge=3549904, ano_inicio=2020, ano_fim=2026):
    print(f"📡 Conectando à API do InfoDengue para o município {codigo_ibge}...")

    url = "https://info.dengue.mat.br/api/alertcity"

    parametros = {
        "geocode": codigo_ibge,
        "disease": "dengue",
        "format": "json",
        "ew_start": 1,
        "ew_end": 53,
        "ey_start": ano_inicio,
        "ey_end": ano_fim
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    resposta = requests.get(url, params=parametros, headers=headers)

    if resposta.status_code == 200:
        dados_json = resposta.json()

        if not dados_json:
            print(" A API retornou uma resposta vazia. Verifique os parâmetros.")
            return None

        df = pd.DataFrame(dados_json)

        colunas_relevantes = [
            'SE', 'casos_est', 'casos', 'p_rt1', 'p_inc100k',
            'tempmin', 'tempmed', 'tempmax', 'umidmin', 'umidmed', 'umidmax'
        ]

        colunas_existentes = [col for col in colunas_relevantes if col in df.columns]
        df_filtrado = df[colunas_existentes]

        # Salvando informações (recuado dentro da função)
        pasta_destino = os.path.join("data", "raw")
        os.makedirs(pasta_destino, exist_ok=True)

        caminho_arquivo = os.path.join(pasta_destino, f"dengue_clima_{codigo_ibge}.csv")
        df_filtrado.to_csv(caminho_arquivo, index=False, encoding="utf-8")

        print(f" Dados baixados com sucesso! Registros salvos: {len(df_filtrado)}")
        print(f" Arquivo salvo em: {caminho_arquivo}")

        return df_filtrado
    else:
        print(f" Erro na requisição: Código HTTP {resposta.status_code}")
        return None


if __name__ == "__main__":
    df = baixar_dados_dengue(codigo_ibge=3549904, ano_inicio=2021, ano_fim=2026)

    if df is not None:
        print("\n Primeiras 5 linhas do dataset do TCC:")
        print(df.head())