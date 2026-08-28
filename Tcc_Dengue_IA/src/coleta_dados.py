import os
import pandas as pd


def buscar_dados_infodengue(codigo_ibge=3549904):
    # Força a busca dos dados até o ano atual (2026)
    url = f"https://infodengue.mat.br/api/alertcity?geocode={codigo_ibge}&disease=dengue&format=csv&ew_start=1&ew_end=53&ey_start=2023&ey_end=2026"

    pasta_src = os.path.dirname(os.path.abspath(__file__))
    raiz_projeto = os.path.dirname(pasta_src)
    caminho_destino = os.path.join(
        raiz_projeto, "data", "raw", f"infodengue_{codigo_ibge}.csv"
    )

    os.makedirs(os.path.dirname(caminho_destino), exist_ok=True)

    df = pd.read_csv(url)
    df.to_csv(caminho_destino, index=False)
    print(
        f"✅ Dados baixados da API InfoDengue. Última SE encontrada na API:"
        f" {df['SE'].max()}"
    )


if __name__ == "__main__":
    buscar_dados_infodengue()
