import os
from io import StringIO
import pandas as pd
import requests


def buscar_dados_infodengue(codigo_ibge=3549904):
    url = f"https://infodengue.mat.br/api/alertcity?geocode={codigo_ibge}&disease=dengue&format=csv&ew_start=1&ew_end=53&ey_start=2023&ey_end=2026"

    # Cabeçalho simulando navegador para evitar bloqueio do GitHub Actions
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    pasta_src = os.path.dirname(os.path.abspath(__file__))
    raiz_projeto = os.path.dirname(pasta_src)
    caminho_destino = os.path.join(
        raiz_projeto, "data", "raw", f"infodengue_{codigo_ibge}.csv"
    )

    os.makedirs(os.path.dirname(caminho_destino), exist_ok=True)

    print(
        f"📡 Baixando dados da API InfoDengue para o município"
        f" {codigo_ibge}..."
    )

    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()

    # Converte o texto retornado pela API em DataFrame
    df = pd.read_csv(StringIO(response.text))
    df.to_csv(caminho_destino, index=False)

    print(
        f"✅ Dados baixados com sucesso! Última SE encontrada: {df['SE'].max()}"
    )


if __name__ == "__main__":
    buscar_dados_infodengue()
