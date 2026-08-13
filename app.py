import streamlit as st
import pandas as pd
import numpy as np
import re
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(
    page_title="Sistema Fertigrama & Monitoramento de Solo",
    page_icon="🌱",
    layout="wide"
)

# -----------------------------------------------------------------------------
# FUNÇÃO DE NORMALIZAÇÃO AUTOMÁTICA DE NOMENCLATURA DE TALHÕES
# -----------------------------------------------------------------------------
def normalizar_nome_talhao(texto):
    """
    Padroniza automaticamente qualquer nome de talhão/pivô para garantir 
    compatibilidade entre diferentes planilhas e clientes, sem perder a identidade.
    Exemplos:
    - 'T09_2 - Escavelhi' -> 'T09 2 Escavelhi'
    - 'T09_Escavelhi'     -> 'T09 Escavelhi'
    - 'P01c - Pivô 1'     -> 'P01c Pivo 1'
    - 'Pivo_1'            -> 'Pivo 1'
    """
    if pd.isna(texto):
        return "Geral"
    
    s = str(texto).strip()
    
    # Remove acentos comuns para evitar divergências por caracteres especiais
    import unicodedata
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    
    # Substitui hífens com espaços e underscores por espaços simples
    s = s.replace('-', ' ').replace('_', ' ')
    
    # Remove espaços duplos e padroniza maiúsculas/minúsculas para comparação consistente
    s = re.sub(r'\s+', ' ', s).strip()
    
    return s

# -----------------------------------------------------------------------------
# CARREGAMENTO E CLASSIFICAÇÃO AUTOMÁTICA DE DADOS
# -----------------------------------------------------------------------------
@st.cache_data
def carregar_e_processar_dados(caminho_ou_arquivo, tipo_coleta_padrao="Coleta 2 (Monitoramento)"):
    try:
        df = pd.read_excel(caminho_ou_arquivo)
    except Exception as e:
        return pd.DataFrame()
        
    # Identifica colunas de referência de talhão de forma flexível
    col_talhao = None
    for col in df.columns:
        if 'talhão' in col.lower() or 'talhao' in col.lower() or 'gleba' in col.lower() or 'identificacao' in col.lower() or 'descricao' in col.lower():
            col_talhao = col
            break
            
    if col_talhao:
        df["Talhao_Original"] = df[col_talhao]
        df["Talhao_Normalizado"] = df[col_talhao].apply(normalizar_nome_talhao)
    else:
        df["Talhao_Original"] = "Geral"
        df["Talhao_Normalizado"] = "Geral"
        
    # Garante colunas essenciais
    if "Fazenda" not in df.columns:
        df["Fazenda"] = "Fazenda Principal"
    if "Profundidade" not in df.columns:
        df["Profundidade"] = "0 - 10 cm"
    if "Tipo_Coleta" not in df.columns:
        df["Tipo_Coleta"] = tipo_coleta_padrao
        
    return df

# -----------------------------------------------------------------------------
# INTERFACE DO APLICATIVO
# -----------------------------------------------------------------------------
st.title("🌱 Sistema Fertigrama & Monitoramento de Fertilidade")

# Sidebar - Upload Múltiplo para Automatizar por Cliente
st.sidebar.header("📁 Importação de Dados do Cliente")
arquivo_base_up = st.sidebar.file_uploader("1. Planilha de Coleta Base (Laudos)", type=["xlsx", "xls"], key="base")
arquivo_monit_up = st.sidebar.file_uploader("2. Planilha de Monitoramento (Safra Atual)", type=["xlsx", "xls"], key="monit")

# Processamento dos arquivos enviados ou fallbacks locais para teste
df_base = carregar_e_processar_dados(arquivo_base_up, "Coleta 1 (Base)") if arquivo_base_up else pd.DataFrame()
df_monit = carregar_e_processar_dados(arquivo_monit_up, "Coleta 2 (Monitoramento)") if arquivo_monit_up else pd.DataFrame()

# Se não houver upload, tenta carregar arquivos padrão locais se disponíveis
if df_base.empty and os.path.exists("Laudos-cesar_possamai_suia_safra_2025_2026_Fertilidade.xlsx"):
    df_base = carregar_e_processar_dados("Laudos-cesar_possamai_suia_safra_2025_2026_Fertilidade.xlsx", "Coleta 1 (Base)")
if df_monit.empty and os.path.exists("Monitoramentos Cesar Milho 26.xlsx"):
    df_monit = carregar_e_processar_dados("Monitoramentos Cesar Milho 26.xlsx", "Coleta 2 (Monitoramento)")

# Unificação automatizada se ambas as bases existirem
if not df_base.empty and not df_monit.empty:
    df_geral = pd.concat([df_base, df_monit], ignore_index=True)
else:
    df_geral = df_base if not df_base.empty else df_monit

# Navegação entre Abas
aba_selecionada = st.radio(
    "Navegação:",
    ["📈 Comparativo de Monitoramento", "📊 Diagnóstico Fertigrama", "📥 Entrar/Importar Laudo", "👤 Gerenciar Clientes & Laudos"],
    horizontal=True
)

st.markdown("---")

# -----------------------------------------------------------------------------
# ABA 1: COMPARATIVO DE MONITORAMENTO AUTOMATIZADO
# -----------------------------------------------------------------------------
if aba_selecionada == "📈 Comparativo de Monitoramento":
    st.header("📈 Comparação Automatizada (Base vs Monitoramento)")
    
    if df_geral.empty:
        st.info("Por favor, envie as planilhas de Coleta Base e Monitoramento na barra lateral.")
    else:
        # Filtros dinâmicos baseados no DataFrame unificado e normalizado
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            fazendas = sorted(list(df_geral["Fazenda"].dropna().unique()))
            fazenda_sel = st.selectbox("Fazenda / Gleba:", fazendas if fazendas else ["Geral"])
            
        df_sub_faz = df_geral[df_geral["Fazenda"] == fazenda_sel]
        
        with col2:
            profs = sorted(list(df_sub_faz["Profundidade"].dropna().unique()))
            prof_sel = st.selectbox("Profundidade:", profs if profs else ["0 - 10 cm"])
            
        with col3:
            talhoes_disp = sorted(list(df_sub_faz["Talhao_Normalizado"].dropna().unique()))
            opcoes_talhao = ["Todos os Talhões / Pivôs"] + talhoes_disp
            talhao_sel = st.selectbox("Talhão / Pivô Normalizado:", opcoes_talhao)
            
        with col4:
            cols_excluir = ["Talhao_Original", "Talhao_Normalizado", "Fazenda", "Profundidade", "Tipo_Coleta", "Produtor", "Descricao", "Identificacao", "Talhão"]
            nutrientes = [c for c in df_sub_faz.columns if c not in cols_excluir and pd.api.types.is_numeric_dtype(df_sub_faz[c])]
            nutriente_sel = st.selectbox("Parâmetro / Nutriente:", nutrientes if nutrientes else [])

        # Filtragem cruzada automatizada
        df_filtrado = df_sub_faz[df_sub_faz["Profundidade"] == prof_sel] if "Profundidade" in df_sub_faz.columns else df_sub_faz

        if talhao_sel == "Todos os Talhões / Pivôs":
            df_c1 = df_filtrado[df_filtrado["Tipo_Coleta"].str.contains("Base", case=False, na=False)].dropna(subset=[nutriente_sel]) if nutriente_sel else pd.DataFrame()
            df_c2 = df_filtrado[df_filtrado["Tipo_Coleta"].str.contains("Monitoramento", case=False, na=False)].dropna(subset=[nutriente_sel]) if nutriente_sel else pd.DataFrame()
        else:
            df_sub_t = df_filtrado[df_filtrado["Talhao_Normalizado"] == talhao_sel]
            df_c1 = df_sub_t[df_sub_t["Tipo_Coleta"].str.contains("Base", case=False, na=False)].dropna(subset=[nutriente_sel]) if nutriente_sel else pd.DataFrame()
            df_c2 = df_sub_t[df_sub_t["Tipo_Coleta"].str.contains("Monitoramento", case=False, na=False)].dropna(subset=[nutriente_sel]) if nutriente_sel else pd.DataFrame()

        if df_c1.empty or df_c2.empty:
            st.warning(f"⚠️ Dados insuficientes para o cruzamento automático no talhão **{talhao_sel}**.")
            st.info("Certifique-se de que o mesmo talhão está presente tanto na planilha base quanto no monitoramento.")
        else:
            st.success(f"Cruzamento realizado com sucesso para **{talhao_sel}** ({nutriente_sel})")
            
            m1 = df_c1[nutriente_sel].mean()
            m2 = df_c2[nutriente_sel].mean()
            diff = m2 - m1
            pct = (diff / m1) * 100 if m1 != 0 else 0
            
            c_m1, c_m2, c_m3 = st.columns(3)
            c_m1.metric("Média Coleta 1 (Base)", f"{m1:.2f}")
            c_m2.metric("Média Coleta 2 (Monitoramento)", f"{m2:.2f}")
            c_m3.metric("Variação da Safra", f"{diff:+.2f}", f"{pct:+.1f}%")
            
            # Gráfico comparativo interativo
            fig = go.Figure()
            fig.add_trace(go.Box(y=df_c1[nutriente_sel], name="Coleta 1 (Base)", boxpoints='all', jitter=0.3))
            fig.add_trace(go.Box(y=df_c2[nutriente_sel], name="Coleta 2 (Monitoramento)", boxpoints='all', jitter=0.3))
            fig.update_layout(
                title=f"Evolução de {nutriente_sel} - {talhao_sel}",
                yaxis_title=nutriente_sel,
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)

# Demais abas padrão
elif aba_selecionada == "📊 Diagnóstico Fertigrama":
    st.header("📊 Diagnóstico Fertigrama")
    st.info("Módulo de recomendações e calagem/agem baseado nos laudos carregados.")
elif aba_selecionada == "📥 Entrar/Importar Laudo":
    st.header("📥 Importação Individual de Laudos")
    st.info("Cadastre dados avulsos diretamente pelo painel.")
elif aba_selecionada == "👤 Gerenciar Clientes & Laudos":
    st.header("👤 Gerenciamento Geral de Clientes")
    st.info("Painel de controle para auditoria e histórico dos clientes cadastrados.")
