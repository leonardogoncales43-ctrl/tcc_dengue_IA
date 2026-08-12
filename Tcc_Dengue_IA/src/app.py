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
pasta_src = os.path.dirname(os.path.abspath(__file__))
raiz_projeto = os.path.dirname(pasta_src)


# ---------------------------------------------------------
# Funções de Carregamento com Cache
# ---------------------------------------------------------
@st.cache_data
def carregar_dados(codigo_ibge):
    caminho = os.path.join(raiz_projeto, "data", "processed", f"dengue_clima_processado_{codigo_ibge}.csv")
    if os.path.exists(caminho):
        return pd.read_csv(caminho)
    return None


@st.cache_resource
def carregar_modelo(codigo_ibge):
    caminho = os.path.join(raiz_projeto, "models", f"modelo_dengue_{codigo_ibge}.pkl")
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
    # 1. Previsão da IA (Baseline)
    colunas_features = [
        'casos_lag1', 'casos_lag2',
        'tempmed', 'tempmed_lag2', 'tempmed_lag4',
        'umidmed', 'umidmed_lag2', 'umidmed_lag4'
    ]
    colunas_existentes = [c for c in colunas_features if c in df.columns]

    df['previsao_IA'] = modelo.predict(df[colunas_existentes])
    df['previsao_IA'] = df['previsao_IA'].apply(lambda x: max(0, round(x)))

    ultima_semana = df.iloc[-1]
    casos_atuais = int(ultima_semana['casos'])
    previsao_proxima = int(ultima_semana['previsao_IA'])
    variacao = previsao_proxima - casos_atuais

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
    c1.metric("Semana Epidemiológica", str(ultima_semana['SE']))
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
    fig.update_layout(xaxis_title="Semana Epidemiológica", yaxis_title="Número de Casos", template="plotly_white",
                      height=450)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # 4. Mapeamento de Risco por Bairros Reais de SJC
    st.subheader("🗺️ Mapeamento Espaço-Temporal de Risco por Bairro")

    df_bairros = pd.DataFrame([
        {"bairro": "Jardim Satélite (Zona Sul)", "lat": -23.2320, "lon": -45.8860, "ib_larvario": 4.2,
         "casos_previstos": 280, "risco": "EMERGÊNCIA", "cor": "red"},
        {"bairro": "Eugênio de Melo (Zona Leste)", "lat": -23.1550, "lon": -45.7820, "ib_larvario": 4.8,
         "casos_previstos": 320, "risco": "EMERGÊNCIA", "cor": "red"},
        {"bairro": "Bosque dos Eucaliptos (Zona Sul)", "lat": -23.2500, "lon": -45.8890, "ib_larvario": 3.5,
         "casos_previstos": 190, "risco": "ALERTA", "cor": "orange"},
        {"bairro": "Vista Verde (Zona Leste)", "lat": -23.1810, "lon": -45.8350, "ib_larvario": 3.1,
         "casos_previstos": 160, "risco": "ALERTA", "cor": "orange"},
        {"bairro": "Santana (Zona Norte)", "lat": -23.1600, "lon": -45.8920, "ib_larvario": 2.1, "casos_previstos": 110,
         "risco": "MÉDIO", "cor": "gold"},
        {"bairro": "Centro", "lat": -23.1950, "lon": -45.8860, "ib_larvario": 1.2, "casos_previstos": 65,
         "risco": "SATISFATÓRIO", "cor": "green"},
        {"bairro": "Urbanova (Zona Oeste)", "lat": -23.2080, "lon": -45.9320, "ib_larvario": 0.8, "casos_previstos": 35,
         "risco": "SATISFATÓRIO", "cor": "green"}
    ])

    col_map1, col_map2 = st.columns([3, 1])

    with col_map2:
        modo_mapa = st.radio(
            "Visualização do Mapa:",
            ["🔥 Mapa de Calor (HeatMap)", "🎯 Radar por Bairro"],
            index=0
        )
        st.markdown("---")
        st.caption("💡 **Dica:** Passe o mouse sobre os pontos para inspecionar os detalhes de cada bairro.")

    with col_map1:
        mapa = folium.Map(location=[-23.2000, -45.8700], zoom_start=12, tiles="cartodbpositron")

        if modo_mapa == "🔥 Mapa de Calor (HeatMap)":
            dados_calor = [[row['lat'], row['lon'], row['casos_previstos']] for _, row in df_bairros.iterrows()]
            HeatMap(dados_calor, radius=40, blur=25, min_opacity=0.4).add_to(mapa)

            for _, row in df_bairros.iterrows():
                folium.CircleMarker(
                    location=[row['lat'], row['lon']],
                    radius=6, color="black", weight=1, fill=True,
                    fill_color=row['cor'], fill_opacity=0.9,
                    tooltip=f"<b>{row['bairro']}</b><br>Casos Previstos: {row['casos_previstos']}<br>Risco: {row['risco']}"
                ).add_to(mapa)
        else:
            for _, row in df_bairros.iterrows():
                folium.Circle(
                    location=[row['lat'], row['lon']],
                    radius=row['casos_previstos'] * 4, color=row['cor'],
                    fill=True, fill_color=row['cor'], fill_opacity=0.35,
                    popup=folium.Popup(f"""
                        <div style='font-family: sans-serif; width: 170px;'>
                            <h4 style='margin-bottom:5px;'>{row['bairro']}</h4>
                            <b>Nível de Risco:</b> {row['risco']}<br>
                            <b>Índice Breteau:</b> {row['ib_larvario']}<br>
                            <b>Casos Previstos:</b> {row['casos_previstos']}
                        </div>
                    """, max_width=220)
                ).add_to(mapa)

        st_folium(mapa, width=900, height=480)

    st.markdown("---")

    # 5. Simulador de Cenários Climáticos (What-If Analysis)
    st.subheader("🧪 Simulador de Cenários Climáticos (Análise What-If)")
    st.markdown(
        "Ajuste as variáveis meteorológicas hipotéticas para observar a reação do modelo de Inteligência Artificial em tempo real:")

    col_sim1, col_sim2 = st.columns([1, 2])

    with col_sim1:
        st.markdown("##### 🎛️ Parâmetros de Entrada")
        delta_temp = st.slider("Variação de Temperatura (°C):", min_value=-3.0, max_value=5.0, value=0.0, step=0.5)
        delta_umid = st.slider("Variação de Umidade Relativa (%):", min_value=-20.0, max_value=20.0, value=0.0,
                               step=5.0)

    # Lógica do Simulador: duplica a última linha e aplica os deltas
    linha_simulada = df.iloc[[-1]].copy()

    cols_temp = [c for c in ['tempmed', 'tempmed_lag2', 'tempmed_lag4'] if c in linha_simulada.columns]
    cols_umid = [c for c in ['umidmed', 'umidmed_lag2', 'umidmed_lag4'] if c in linha_simulada.columns]

    linha_simulada[cols_temp] += delta_temp
    linha_simulada[cols_umid] += delta_umid

    pred_simulada = max(0, round(modelo.predict(linha_simulada[colunas_existentes])[0]))
    diferenca_casos = int(pred_simulada - previsao_proxima)

    if previsao_proxima > 0:
        perc_impacto = ((pred_simulada - previsao_proxima) / previsao_proxima) * 100
    else:
        perc_impacto = 0.0

    with col_sim2:
        st.markdown("##### 📊 Resultado da Projeção Simulada")
        m1, m2, m3 = st.columns(3)
        m1.metric("Previsão Atual (Baseline)", f"{previsao_proxima} casos")
        m2.metric("Previsão Simulada", f"{pred_simulada} casos", delta=f"{diferenca_casos:+d} casos")
        m3.metric("Impacto % Estimado", f"{perc_impacto:+.1f}%")

        if diferenca_casos > 0:
            st.warning(
                f"⚠️ **Alerta do Modelo:** As condições simuladas causam um aumento projetado de **{diferenca_casos} casos adicionais** (+{perc_impacto:.1f}%) na próxima semana.")
        elif diferenca_casos < 0:
            st.success(
                f"📉 **Redução Projetada:** A alteração climática simulada reduz a transmissão em **{abs(diferenca_casos)} casos** ({perc_impacto:.1f}%).")
        else:
            st.info(
                "ℹ️ **Cenário Neutro:** A variação selecionada não altera significativamente o patamar de casos previsto.")

    st.markdown("---")
    st.markdown("### 📋 Indicadores Larvários e Risco Epidemiológico por Bairro")
    st.dataframe(
        df_bairros[['bairro', 'ib_larvario', 'casos_previstos', 'risco']],
        use_container_width=True
    )