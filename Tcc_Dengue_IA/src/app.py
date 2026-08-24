import os
import joblib
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap

# ---------------------------------------------------------
# Configuração da Página Web
# ---------------------------------------------------------
st.set_page_config(
    page_title="Portal Preditivo de Dengue - TCC",
    page_icon="🦟",
    layout="wide"
)

# ---------------------------------------------------------
# Localização dos Caminhos do Projeto
# ---------------------------------------------------------
diretorio_atual = os.path.dirname(os.path.abspath(__file__))

def obter_caminho_existente(rel_path):
    caminho1 = os.path.join(diretorio_atual, rel_path)
    caminho2 = os.path.join(os.path.dirname(diretorio_atual), rel_path)
    if os.path.exists(caminho1):
        return caminho1
    return caminho2

# ---------------------------------------------------------
# Funções de Carregamento com Cache
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def carregar_dados(codigo_ibge):
    caminho = obter_caminho_existente(os.path.join("data", "processed", f"dengue_clima_processado_{codigo_ibge}.csv"))
    if os.path.exists(caminho):
        return pd.read_csv(caminho)
    return None

@st.cache_resource(ttl=3600)
def carregar_modelo(codigo_ibge):
    caminho = obter_caminho_existente(os.path.join("models", f"modelo_dengue_{codigo_ibge}.pkl"))
    if os.path.exists(caminho):
        return joblib.load(caminho)
    return None

# ---------------------------------------------------------
# Barra Lateral (Menu)
# ---------------------------------------------------------
st.sidebar.title("🛡️ Vigilância Epidemiológica")
st.sidebar.markdown("---")

municipios = {
    "São José dos Campos (3549904)": 3549904,
}

cidade_selecionada = st.sidebar.selectbox("Selecione o Município:", list(municipios.keys()))
codigo_ibge = municipios[cidade_selecionada]

df = carregar_dados(codigo_ibge)
modelo = carregar_modelo(codigo_ibge)

# ---------------------------------------------------------
# Corpo do Portal
# ---------------------------------------------------------
st.title("🌐 Portal Preditivo de Tendência da Dengue")
st.markdown(f"**Sistema de Suporte à Decisão em Saúde Pública — Código IBGE: {codigo_ibge}**")
st.markdown("---")

if df is None or modelo is None:
    st.error("❌ Dados ou modelo preditivo não encontrados.")
else:
    # 1. Previsão da IA (Forecasting para a Próxima Semana)
    colunas_features = [
        'casos_lag1', 'casos_lag2',
        'tempmed', 'tempmed_lag2', 'tempmed_lag4',
        'umidmed', 'umidmed_lag2', 'umidmed_lag4'
    ]
    colunas_existentes = [c for c in colunas_features if c in df.columns]

    # Ajusta o histórico passado no gráfico
    df['previsao_IA'] = modelo.predict(df[colunas_existentes])
    df['previsao_IA'] = df['previsao_IA'].apply(lambda x: max(0, round(x)))

    # Extrai a última semana real para projetar a seguinte
    ultima_semana = df.iloc[-1]
    se_atual = int(ultima_semana['SE'])
    proxima_se = se_atual + 1 if (se_atual % 100) < 52 else ((se_atual // 100) + 1) * 100 + 1

    # Monta as variáveis (features) deslocadas para a próxima semana
    dados_futuro = {
        'casos_lag1': ultima_semana['casos'],
        'casos_lag2': df.iloc[-2]['casos'] if len(df) > 1 else ultima_semana['casos'],
        'tempmed': ultima_semana['tempmed'],
        'tempmed_lag2': df.iloc[-2]['tempmed'] if len(df) > 1 else ultima_semana['tempmed'],
        'tempmed_lag4': df.iloc[-4]['tempmed'] if len(df) > 3 else ultima_semana['tempmed'],
        'umidmed': ultima_semana['umidmed'],
        'umidmed_lag2': df.iloc[-2]['umidmed'] if len(df) > 1 else ultima_semana['umidmed'],
        'umidmed_lag4': df.iloc[-4]['umidmed'] if len(df) > 3 else ultima_semana['umidmed']
    }

    # Previsão exclusiva para a semana seguinte
    df_futuro = pd.DataFrame([dados_futuro])
    previsao_futura_raw = modelo.predict(df_futuro[colunas_existentes])[0]
    previsao_proxima = max(0, int(round(previsao_futura_raw)))
    
    casos_atuais = int(ultima_semana['casos'])
    variacao = previsao_proxima - casos_atuais

    # Adiciona o ponto futuro no gráfico sem alterar os casos reais
    linha_grafico_futuro = pd.DataFrame({
        'SE': [proxima_se],
        'casos': [None],
        'previsao_IA': [previsao_proxima]
    })
    df = pd.concat([df, linha_grafico_futuro], ignore_index=True)

    if previsao_proxima > 500:
        status_alerta = "🚨 ALERTA DE SURTO"
        cor_alerta = "red"
    elif previsao_proxima > 200:
        status_alerta = "⚠️ ATENÇÃO"
        cor_alerta = "orange"
    else:
        status_alerta = "✅ SATISFATÓRIO"
        cor_alerta = "green"

    # 2. Painel de Métricas Rápidas
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Semana Epidemiológica", str(se_atual))
    c2.metric("Casos Reais Notificados", f"{casos_atuais} casos")
    c3.metric("Previsão IA (Próx. Semana)", f"{previsao_proxima} casos", delta=f"{variacao} casos")
    c4.markdown(f"**Status Operacional:**\n### :{cor_alerta}[{status_alerta}]")

    st.markdown("---")

    # 3. Gráfico Interativo Temporal
    st.subheader("📈 Tendência Temporal: Casos Reais vs. Previsão da IA")
    semanas_exibidas = st.slider("Exibir histórico das últimas semanas:", min_value=12, max_value=len(df), value=52)
    df_grafico = df.tail(semanas_exibidas)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_grafico['SE'].astype(str), y=df_grafico['casos'],
        mode='lines+markers', name='Casos Reais', line=dict(color='#1f77b4', width=3)
    ))
    fig.add_trace(go.Scatter(
        x=df_grafico['SE'].astype(str), y=df_grafico['previsao_IA'],
        mode='lines+markers', name='Previsão da IA', line=dict(color='#d62728', width=3, dash='dash')
    ))
    fig.update_layout(xaxis_title="Semana Epidemiológica", yaxis_title="Número de Casos", template="plotly_white", height=450)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # 4. Mapeamento de Risco por Regiões Epidemiológicas de SJC
    st.subheader("🗺️ Mapeamento Espaço-Temporal de Risco por Região Epidemiológica")
    st.markdown("Distribuição da previsão municipal entre os **Distritos Sanitários** de São José dos Campos com base no Índice Breteau (IB) Regional.")

    df_regioes = pd.DataFrame([
        {"regiao": "Zona Sul", "lat": -23.2450, "lon": -45.8920, "ib_larvario": 4.1, "bairros_chave": "Jd. Satélite, Bosque dos Eucaliptos, Campo dos Alemães"},
        {"regiao": "Zona Leste", "lat": -23.1720, "lon": -45.8150, "ib_larvario": 4.5, "bairros_chave": "Eugênio de Melo, Vista Verde, Novo Horizonte"},
        {"regiao": "Zona Sudeste", "lat": -23.2520, "lon": -45.8580, "ib_larvario": 3.6, "bairros_chave": "Putim, São Judas Tadeu"},
        {"regiao": "Zona Norte", "lat": -23.1580, "lon": -45.8920, "ib_larvario": 2.2, "bairros_chave": "Santana, Alto da Ponte, Vila Paiva"},
        {"regiao": "Centro", "lat": -23.1980, "lon": -45.8870, "ib_larvario": 1.1, "bairros_chave": "Centro, Jd. São Dimas, Vila Ema"},
        {"regiao": "Zona Oeste", "lat": -23.2150, "lon": -45.9220, "ib_larvario": 0.9, "bairros_chave": "Urbanova, Jd. Aquárius, Jd. das Indústrias"}
    ])

    def classificar_risco(ib):
        if ib >= 4.0: return "CRÍTICO / EMERGÊNCIA", "#d62728"
        elif ib >= 2.0: return "MÉDIO / ALERTA", "#ff7f0e"
        elif ib >= 1.0: return "MODERADO", "#bcbd22"
        else: return "SATISFATÓRIO", "#2ca02c"

    df_regioes[['risco', 'cor']] = df_regioes.apply(
        lambda row: pd.Series(classificar_risco(row['ib_larvario'])), axis=1
    )

    soma_ib = df_regioes['ib_larvario'].sum()
    df_regioes['casos_estimados'] = ((df_regioes['ib_larvario'] / soma_ib) * previsao_proxima).apply(lambda x: int(round(x)))

    col_map1, col_map2 = st.columns([3, 1])

    with col_map2:
        modo_mapa = st.radio(
            "Visualização do Mapa:",
            ["🔥 Densidade de Risco (HeatMap)", "🎯 Raio de Impacto Regional"],
            index=0
        )
        st.markdown("---")
        st.caption("💡 **Nota Científica:** A severidade é ponderada pela densidade vetorial (Índice Breteau) agregada por distrito sanitário.")

    with col_map1:
        mapa = folium.Map(location=[-23.2100, -45.8750], zoom_start=11.5, tiles="cartodbpositron")

        if modo_mapa == "🔥 Densidade de Risco (HeatMap)":
            dados_calor = [[row['lat'], row['lon'], row['casos_estimados']] for _, row in df_regioes.iterrows()]
            HeatMap(dados_calor, radius=50, blur=30, min_opacity=0.4).add_to(mapa)

            for _, row in df_regioes.iterrows():
                folium.CircleMarker(
                    location=[row['lat'], row['lon']],
                    radius=8, color="black", weight=1, fill=True,
                    fill_color=row['cor'], fill_opacity=0.9,
                    tooltip=f"<b>{row['regiao']}</b><br>Risco: {row['risco']}<br>Casos Estimados: {row['casos_estimados']}"
                ).add_to(mapa)
        else:
            for _, row in df_regioes.iterrows():
                folium.Circle(
                    location=[row['lat'], row['lon']],
                    radius=max(300, row['casos_estimados'] * 5), color=row['cor'],
                    fill=True, fill_color=row['cor'], fill_opacity=0.35,
                    popup=folium.Popup(f"""
                        <div style='font-family: sans-serif; width: 200px;'>
                            <h4 style='margin-bottom:5px;'>{row['regiao']}</h4>
                            <b>Status:</b> {row['risco']}<br>
                            <b>Índice Breteau Regional:</b> {row['ib_larvario']}<br>
                            <b>Casos Projetados:</b> {row['casos_estimados']}<br><br>
                            <small><b>Principais Bairros:</b> {row['bairros_chave']}</small>
                        </div>
                    """, max_width=240)
                ).add_to(mapa)

        st_folium(mapa, width=900, height=480)

    st.markdown("---")
    st.markdown("### 📋 Matriz Epidemiológica por Distrito Sanitário (Regiões de SJC)")
    st.dataframe(
        df_regioes[['regiao', 'ib_larvario', 'casos_estimados', 'risco', 'bairros_chave']].rename(
            columns={
                'regiao': 'Região / Zona',
                'ib_larvario': 'Índice Breteau (IB)',
                'casos_estimados': 'Casos Projetados',
                'risco': 'Classificação de Risco',
                'bairros_chave': 'Bairros Abrangidos'
            }
        ),
        use_container_width=True
    )
