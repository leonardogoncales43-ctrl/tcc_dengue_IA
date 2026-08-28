import json
import os
import folium
import joblib
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Monitoramento Preditivo de Dengue - SJC",
    page_icon="🦟",
    layout="wide",
)

pasta_src = os.path.dirname(os.path.abspath(__file__))
raiz_projeto = os.path.dirname(pasta_src)

caminho_processed = os.path.join(
    raiz_projeto,
    "data",
    "processed",
    "dengue_clima_processado_3549904.csv",
)
caminho_modelo = os.path.join(
    raiz_projeto, "models", "modelo_dengue_3549904.pkl"
)
caminho_adl = os.path.join(raiz_projeto, "data", "raw", "adl_sjc.json")


@st.cache_data
def carregar_dados():
    if os.path.exists(caminho_processed):
        return pd.read_csv(caminho_processed)
    return None


@st.cache_data
def carregar_adl():
    if os.path.exists(caminho_adl):
        with open(caminho_adl, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


df_dados = carregar_dados()
dados_adl = carregar_adl()

st.title(
    "🦟 Sistema Preditivo e de Monitoramento de Dengue - São José dos Campos"
)
st.markdown(
    "Painel epidemiológico integrado com inteligência artificial para apoio à tomada de decisão em saúde pública."
)

st.subheader("🔮 Previsão Epidemiológica Próxima Semana")

if os.path.exists(caminho_modelo) and df_dados is not None:
    modelo = joblib.load(caminho_modelo)
    ultima_linha = df_dados.iloc[-1:]

    colunas_features = [
        "casos_lag1",
        "casos_lag2",
        "tempmed",
        "tempmed_lag2",
        "tempmed_lag4",
        "umidmed",
        "umidmed_lag2",
        "umidmed_lag4",
        "ib_larvario_municipal",
    ]
    features_disponiveis = [
        col for col in colunas_features if col in ultima_linha.columns
    ]

    previsao_casos = int(modelo.predict(ultima_linha[features_disponiveis])[0])
    casos_atuais = int(ultima_linha["casos"].values[0])
    ib_atual = dados_adl["ib_geral_municipio"] if dados_adl else 0.8[cite: 2]

    col1, col2, col3 = st.columns(3)
    col1.metric("Casos Registrados (Última Semana)", casos_atuais)
    col2.metric(
        "Previsão da IA (Próxima Semana)",
        f"~{previsao_casos} casos",
        delta=f"{previsao_casos - casos_atuais} casos",
    )
    col3.metric("Índice Breteau Geral (ADL SJC)", f"{ib_atual} (Satisfatório)")[cite: 2]
else:
    st.warning(
        "Modelo ou dados processados não encontrados. Execute o pipeline primeiro."
    )

st.divider()

st.subheader("🗺️ Mapeamento Espaço-Temporal de Risco por Distrito Sanitário")

if dados_adl:
    df_regioes = pd.DataFrame(dados_adl["regioes"])

    # Classificação conforme escala oficial da Prefeitura de SJC (ADL)[cite: 2]
    def classificar_risco(ib):
        if ib > 3.9:
            return "RISCO", "#d62728"
        elif ib >= 1.0:
            return "ALERTA", "#ff7f0e"
        else:
            return "SATISFATÓRIO", "#2ca02c"

    df_regioes[["risco", "cor"]] = df_regioes.apply(
        lambda row: pd.Series(classificar_risco(row["ib_larvario"])), axis=1
    )

    m = folium.Map(
        location=[-23.2237, -45.9009], zoom_start=11, tiles="cartodbpositron"
    )

    for _, row in df_regioes.iterrows():
        popup_content = f"""
        <b>Região:</b> {row['regiao']}<br>
        <b>Índice Breteau (IB):</b> {row['ib_larvario']}<br>
        <b>Classificação:</b> {row['risco']}<br>
        <b>Bairros:</b> {row['bairros_chave']}
        """
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=row["ib_larvario"] * 8 + 6,
            color=row["cor"],
            fill=True,
            fill_color=row["cor"],
            fill_opacity=0.6,
            popup=folium.Popup(popup_content, max_width=250),
        ).add_to(m)

    st_folium(m, width=1000, height=450)
    st.dataframe(
        df_regioes[["regiao", "ib_larvario", "risco", "bairros_chave"]],
        use_container_width=True,
    )
else:
    st.info("Arquivo 'adl_sjc.json' não encontrado na pasta data/raw/.")

st.divider()

if df_dados is not None and "SE" in df_dados.columns:
    st.subheader("📈 Tendência Temporal: Casos x Temperatura Média")
    fig = px.line(
        df_dados,
        x="SE",
        y=["casos", "tempmed"],
        labels={
            "value": "Quantidade / Temp (°C)",
            "SE": "Semana Epidemiológica",
        },
        title="Histórico de Notificações x Temperatura Média",
    )
    st.plotly_chart(fig, use_container_width=True)
