import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Monitoramento de Fertilidade do Solo",
    layout="wide"
)

st.title("🌱 Monitoramento de Fertilidade do Solo")
st.markdown("Comparativo temporal entre **Coleta 1 (Base/Grid)** e **Coleta 2 (Monitoramento)**.")

# --- GERADOR DE DADOS FAKE PARA TESTES ---
@st.cache_data
def gerar_dados_demo():
    np.random.seed(42)
    n_pontos = 25
    
    # Coordenadas aproximadas
    lats = -12.5 + np.random.uniform(-0.01, 0.01, n_pontos)
    lons = -55.7 + np.random.uniform(-0.01, 0.01, n_pontos)
    
    # Valore Coleta 1 (mg/dm³)
    p_coleta1 = np.random.uniform(5, 25, n_pontos)
    # Valores Coleta 2 com alguma variação
    p_coleta2 = p_coleta1 + np.random.uniform(-3, 8, n_pontos)
    p_coleta2 = np.maximum(p_coleta2, 1.0) # Evita valores negativos
    
    df = pd.DataFrame({
        'Ponto_ID': [f'P-{i+1:02d}' for i in range(n_pontos)],
        'Latitude': lats,
        'Longitude': lons,
        'P_Coleta1': np.round(p_coleta1, 2),
        'P_Coleta2': np.round(p_coleta2, 2)
    })
    
    # Cálculo da variação (Delta)
    df['Delta_P'] = np.round(df['P_Coleta2'] - df['P_Coleta1'], 2)
    df['Var_Percentual'] = np.round((df['Delta_P'] / df['P_Coleta1']) * 100, 1)
    return df

df = gerar_dados_demo()

# --- FILTROS LATERAIS ---
st.sidebar.header("Configurações")
nutriente_selecionado = st.sidebar.selectbox("Nutriente / Parâmetro", ["Fósforo (P)", "Potássio (K)", "V%"])
teor_critico = st.sidebar.number_input("Teor Crítico Ideal (Linha Guia)", value=15.0)

# --- CARDS DE MÉTRICAS RESUMO ---
col1, col2, col3, col4 = st.columns(4)
media_c1 = df['P_Coleta1'].mean()
media_c2 = df['P_Coleta2'].mean()
delta_media = media_c2 - media_c1

col1.metric("Média Coleta 1", f"{media_c1:.2f} mg/dm³")
col2.metric("Média Coleta 2", f"{media_c2:.2f} mg/dm³", delta=f"{delta_media:.2f} mg/dm³")
col3.metric("Maior Ganho", f"+{df['Delta_P'].max():.2f} mg/dm³")
col4.metric("Maior Perda", f"{df['Delta_P'].min():.2f} mg/dm³")

st.divider()

# --- GRÁFICOS ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("1. Variação Ponto a Ponto (Gráfico 1:1)")
    
    # Linha de tendência 1:1
    val_max = max(df['P_Coleta1'].max(), df['P_Coleta2'].max()) + 2
    
    fig_scatter = px.scatter(
        df,
        x='P_Coleta1',
        y='P_Coleta2',
        hover_name='Ponto_ID',
        hover_data=['Delta_P', 'Var_Percentual'],
        color='Delta_P',
        color_continuous_scale='RdYlGn',
        labels={'P_Coleta1': 'Coleta 1 (mg/dm³)', 'P_Coleta2': 'Coleta 2 (mg/dm³)'},
        title="Pontos acima da linha tracejada ganharam teor"
    )
    
    # Adiciona a linha 1:1 (Estabilidade)
    fig_scatter.add_shape(
        type="line", x0=0, y0=0, x1=val_max, y1=val_max,
        line=dict(color="Gray", dash="dash")
    )
    
    # Adiciona linha do Teor Crítico
    fig_scatter.add_hline(y=teor_critico, line_dash="dot", line_color="blue", annotation_text="Teor Crítico")
    
    st.plotly_chart(fig_scatter, use_container_width=True)

with col_graf2:
    st.subheader("2. Distribuição Espacial da Variação (Delta)")
    
    fig_map = px.scatter_mapbox(
        df,
        lat="Latitude",
        lon="Longitude",
        color="Delta_P",
        size=np.abs(df["Delta_P"]) + 5,
        hover_name="Ponto_ID",
        hover_data={"P_Coleta1": True, "P_Coleta2": True, "Delta_P": True, "Latitude": False, "Longitude": False},
        color_continuous_scale="RdYlGn",
        zoom=13,
        mapbox_style="carto-positron",
        title="Verde = Ganho | Vermelho = Perda de Teor"
    )
    st.plotly_chart(fig_map, use_container_width=True)

# --- TABELA DE DADOS DETALHADA ---
st.subheader("Dados Detalhados dos Pontos de Monitoramento")
st.dataframe(df, use_container_width=True)
