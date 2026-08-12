import os
import pandas as pd


def processar_dados_dengue(codigo_ibge=3549904):
    pasta_src = os.path.dirname(os.path.abspath(__file__))
    raiz_projeto = os.path.dirname(pasta_src)

    caminho_raw = os.path.join(raiz_projeto, "data", "raw", f"dengue_clima_{codigo_ibge}.csv")

    if not os.path.exists(caminho_raw):
        caminho_raw = os.path.join(pasta_src, "data", "raw", f"dengue_clima_{codigo_ibge}.csv")

    if not os.path.exists(caminho_raw):
        print(f"❌ Arquivo bruto não encontrado em: {caminho_raw}")
        return None

    print(f"⚙️ Processando e preparando dados para o modelo de IA...")
    df = pd.read_csv(caminho_raw)

    # 1. Ordena cronologicamente por Semana Epidemiológica (SE)
    df = df.sort_values(by="SE").reset_index(drop=True)

    # 2. Preenche eventuais valores nulos
    df = df.ffill().bfill()

    # 3. Engenharia de Recursos: Lags Climáticos
    df['tempmed_lag2'] = df['tempmed'].shift(2)
    df['tempmed_lag4'] = df['tempmed'].shift(4)
    df['umidmed_lag2'] = df['umidmed'].shift(2)
    df['umidmed_lag4'] = df['umidmed'].shift(4)

    # 4. Engenharia de Recursos: Lags Epidemiológicos (Autorregressão)
    df['casos_lag1'] = df['casos'].shift(1)
    df['casos_lag2'] = df['casos'].shift(2)

    # 5. Remove as primeiras linhas sem histórico de lag
    df_limpo = df.dropna().reset_index(drop=True)

    # 6. Salva o dataset final na pasta data/processed
    pasta_processed = os.path.join(raiz_projeto, "data", "processed")
    os.makedirs(pasta_processed, exist_ok=True)

    caminho_salvamento = os.path.join(pasta_processed, f"dengue_clima_processado_{codigo_ibge}.csv")
    df_limpo.to_csv(caminho_salvamento, index=False, encoding="utf-8")

    print(f"✅ Tratamento concluído! Registros prontos para IA: {len(df_limpo)}")
    print(f"💾 Arquivo processado salvo em: {caminho_salvamento}")

    return df_limpo


if __name__ == "__main__":
    processar_dados_dengue(codigo_ibge=3549904)