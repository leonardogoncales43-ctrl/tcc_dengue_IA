import os
import time
from io import StringIO
import pandas as pd
import requests


def buscar_dados_infodengue(codigo_ibge=3549904, max_tentativas=3):
    url = f"https://infodengue.mat.br/api/alertcity?geocode={codigo_ibge}&disease=dengue&format=csv&ew_start=1&ew_end=53&ey_start=2023&ey_end=2026"

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
        f"📡 Conectando à API do InfoDengue para o município {codigo_ibge}..."
    )

    for tentativa in range(1, max_tentativas + 1):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            df = pd.read_csv(StringIO(response.text))
            df.to_csv(caminho_destino, index=False)

            print(
                f"✅ Dados atualizados com sucesso! Última SE baixada:"
                f" {df['SE'].max()}"
            )
            return

        except Exception as e:
            print(
                f"⚠️ Tentativa {tentativa}/{max_tentativas} falhou (Erro de"
                f" conexão/DNS: {e})"
            )
            if tentativa < max_tentativas:
                time.sleep(5)

    if os.path.exists(caminho_destino):
        print(
            "⚠️ Servidor InfoDengue inacessível no momento. Mantendo a base"
            " local pré-existente para prosseguir o pipeline."
        )
    else:
        raise ConnectionError(
            "❌ Falha de conexão com a API do InfoDengue e nenhum arquivo"
            " local foi encontrado."
        )


if __name__ == "__main__":
    buscar_dados_infodengue()
