import json
import os
import pandas as pd


def processar_dados(codigo_ibge=3549904):
    pasta_src = os.path.dirname(os.path.abspath(__file__))
    raiz_projeto = os.path.dirname(pasta_src)

    pasta_raw = os.path.join(raiz_projeto, "data", "raw")
    pasta_processed = os.path.join(raiz_projeto, "data", "processed")
    os.makedirs(pasta_processed, exist_ok=True)

    caminho_csv_raw = os.path.join(pasta_raw, f"infodengue_{codigo_ibge}.csv")
    caminho_json_adl = os.path.join(pasta_raw, "adl_sjc.json")

    if not os.path.exists(caminho_csv_raw):
        print(
            f"❌ Arquivo bruto não encontrado em: {caminho_csv_raw}. Executando coleta primeiro..."
        )
        return

    if not os.path.exists(caminho_json_adl):
        print(
            f"❌ Arquivo ADL não encontrado em: {caminho_json_adl}. Crie o arquivo adl_sjc.json em data/raw/."
        )
        return

    print("⚙️ Processando dados e mesclando com o Índice Larvário...")
    df = pd.read_csv(caminho_csv_raw)

    with open(caminho_json_adl, "r", encoding="utf-8") as f:
        dados_adl = json.load(f)

    # Incorpora o índice larvário geral como variável preditiva
    df["ib_larvario_municipal"] = dados_adl.get("ib_geral_municipio", 0.8)

    if "SE" in df.columns:
        df = df.sort_values(by="SE")

    # Lags temporais de contágio e clima
    df["casos_lag1"] = df["casos"].shift(1)
    df["casos_lag2"] = df["casos"].shift(2)
    df["tempmed_lag2"] = df["tempmed"].shift(2)
    df["tempmed_lag4"] = df["tempmed"].shift(4)
    df["umidmed_lag2"] = df["umidmed"].shift(2)
    df["umidmed_lag4"] = df["umidmed"].shift(4)

    df_processado = df.dropna().copy()

    caminho_saida = os.path.join(
        pasta_processed, f"dengue_clima_processado_{codigo_ibge}.csv"
    )
    df_processado.to_csv(caminho_saida, index=False)
    print(f"✅ Dados processados e salvos em: {caminho_saida}")


if __name__ == "__main__":
    processar_dados(codigo_ibge=3549904)
