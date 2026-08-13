import re
import sqlite3
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from io import StringIO

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Terra Nativa - Monitoramento de Solo & Fertigrama",
    layout="wide",
    page_icon="🌾",
    initial_sidebar_state="expanded"
)

# --- BANCO DE DADOS (SQLITE) ---
def init_db():
    conn = sqlite3.connect("terranativa.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS analises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            fazenda TEXT,
            profundidade TEXT,
            tipo_coleta TEXT DEFAULT 'Coleta 1 (Base)',
            area_ha REAL DEFAULT 0.0,
            grid_amostral REAL DEFAULT 0.0,
            dados_json TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

init_db()

def get_clientes():
    conn = sqlite3.connect("terranativa.db")
    df = pd.read_sql_query("SELECT id, nome FROM clientes ORDER BY nome", conn)
    conn.close()
    return df

def add_cliente(nome):
    conn = sqlite3.connect("terranativa.db")
    c = conn.cursor()
    c.execute("INSERT INTO clientes (nome) VALUES (?)", (nome,))
    conn.commit()
    conn.close()

def excluir_analise(analise_id):
    conn = sqlite3.connect("terranativa.db")
    c = conn.cursor()
    c.execute("DELETE FROM analises WHERE id = ?", (analise_id,))
    conn.commit()
    conn.close()

def limpar_e_extrair_talhao(texto):
    if pd.isna(texto):
        return "Geral"
    s = str(texto).strip()
    # Remove prefixo de números do ponto de coleta (ex: "1 - ", "2 - ")
    s = re.sub(r'^\d+\s*-\s*', '', s)
    # Remove o sufixo da profundidade (ex: "- 0 - 10cm", "0-10cm")
    s = re.sub(r'\s*-\s*\d+.*$', '', s)
    # Remove o nome da fazenda se estiver no texto para focar no talhão/pivô
    s = re.sub(r'Fazenda_[A-Za-z0-9_]+?_', '', s, flags=re.IGNORECASE)
    s = re.sub(r'Fazenda\s+[A-Za-z0-9_]+\s*', '', s, flags=re.IGNORECASE)
    # Substitui underlines por espaços e padroniza
    s = s.replace('_', ' ').strip()
    s = re.sub(r'\s+', ' ', s)
    return s if s else "Geral"

def normalizar_profundidade(texto):
    if pd.isna(texto):
        return "0 - 10 cm"
    s = str(texto).strip().lower()
    if "0" in s and "10" in s:
        return "0 - 10 cm"
    elif "10" in s and "20" in s:
        return "10 - 20 cm"
    elif "20" in s and "40" in s:
        return "20 - 40 cm"
    return str(texto).strip()

def salvar_analise(cliente_id, fazenda, profundidade, tipo_coleta, area_ha, grid_amostral, df_dados):
    conn = sqlite3.connect("terranativa.db")
    c = conn.cursor()
    prof_norm = normalizar_profundidade(profundidade)
    json_data = df_dados.to_json(orient="records")
    c.execute("""
        INSERT INTO analises (cliente_id, fazenda, profundidade, tipo_coleta, area_ha, grid_amostral, dados_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (cliente_id, fazenda, prof_norm, tipo_coleta, area_ha, grid_amostral, json_data))
    conn.commit()
    conn.close()

def get_analises_cliente(cliente_id):
    conn = sqlite3.connect("terranativa.db")
    c = conn.cursor()
    c.execute("""
        SELECT id, fazenda, profundidade, tipo_coleta, area_ha, grid_amostral, dados_json 
        FROM analises WHERE cliente_id = ?
    """, (cliente_id,))
    rows = c.fetchall()
    conn.close()
    
    lista_dfs = []
    for row in rows:
        analise_id, fazenda, profundidade, tipo_coleta, area_ha, grid_amostral, json_str = row
        df = pd.read_json(StringIO(json_str), orient="records")
        df["analise_db_id"] = analise_id
        df["Fazenda"] = fazenda
        df["Profundidade"] = normalizar_profundidade(profundidade)
        df["Tipo_Coleta"] = tipo_coleta
        df["area_ha"] = area_ha
        df["grid_amostral"] = grid_amostral

        # Identifica coluna de referência de talhão de forma flexível
        col_ref = None
        for col in ["Talhão", "Talhao", "Descricao", "Identificacao"]:
            if col in df.columns:
                col_ref = col
                break

        if col_ref:
            df["Talhao"] = df[col_ref].apply(limpar_e_extrair_talhao)
        else:
            df["Talhao"] = "Geral"

        lista_dfs.append(df)
        
    if lista_dfs:
        return pd.concat(lista_dfs, ignore_index=True)
    return pd.DataFrame()

# --- CLASSIFICAÇÃO FERTIGRAMA ---
def classificar_elemento(val, col_name, row=None):
    if pd.isna(val):
        return None
    val = float(val)
    
    if col_name == "Argila (%)":
        if val < 15: return "Ruim (< 20%)"
        elif val < 20: return "Médio (20 a 40%)"
        elif val < 25: return "Bom (40 a 60%)"
        elif val <= 35: return "Muito Bom (60 a 80%)"
        else: return "Excesso (> 80%)"

    elif col_name in ["P (mg.dm-3)", "P Mehlich-3 (mg.dm-3)", "P Resina (mg.dm-3)"]:
        arg = row.get("Argila (%)") if (row is not None and "Argila (%)" in row) else 30
        meta = 21.0
        if not pd.isna(arg):
            arg = float(arg)
            if arg < 15.0: meta = 42.0
            elif arg < 20.0: meta = 30.0
            elif arg < 26.0: meta = 24.0
            elif arg < 31.0: meta = 21.0
            elif arg < 40.0: meta = 18.0
            elif arg < 50.0: meta = 15.0
            elif arg < 60.0: meta = 12.0
            else: meta = 8.0
            
        if val < 0.5 * meta: return "Ruim (< 20%)"
        elif val < 0.8 * meta: return "Médio (20 a 40%)"
        elif val <= 1.2 * meta: return "Bom (40 a 60%)"
        elif val <= 1.6 * meta: return "Muito Bom (60 a 80%)"
        else: return "Excesso (> 80%)"

    elif col_name in ["K (mg.dm-3)", "K (cmolc.dm-3)"]:
        if "cmolc" in col_name: val = val * 391.0
        ctc_val = row.get("CTC pH 7,0 (cmolc.dm-3)") if (row is not None and "CTC pH 7,0 (cmolc.dm-3)" in row) else 10
        meta_k = 120.0
        if not pd.isna(ctc_val):
            ctc_val = float(ctc_val)
            if ctc_val < 6.0: meta_k = 90.0
            elif ctc_val < 10.0: meta_k = 120.0
            elif ctc_val < 13.0: meta_k = 150.0
            else: meta_k = 180.0
            
        if val < 0.5 * meta_k: return "Ruim (< 20%)"
        elif val < 0.8 * meta_k: return "Médio (20 a 40%)"
        elif val <= 1.2 * meta_k: return "Bom (40 a 60%)"
        elif val <= 1.6 * meta_k: return "Muito Bom (60 a 80%)"
        else: return "Excesso (> 80%)"

    elif col_name == "Mg (cmolc.dm-3)":
        if val < 0.4: return "Ruim (< 20%)"
        elif val < 0.8: return "Médio (20 a 40%)"
        elif val <= 1.2: return "Bom (40 a 60%)"
        elif val <= 1.8: return "Muito Bom (60 a 80%)"
        else: return "Excesso (> 80%)"

    elif col_name == "Ca (cmolc.dm-3)":
        if val < 1.5: return "Ruim (< 20%)"
        elif val < 2.5: return "Médio (20 a 40%)"
        elif val <= 4.0: return "Bom (40 a 60%)"
        elif val <= 6.0: return "Muito Bom (60 a 80%)"
        else: return "Excesso (> 80%)"

    elif col_name == "S (mg.dm-3)":
        if val < 5.0: return "Ruim (< 20%)"
        elif val < 10.0: return "Médio (20 a 40%)"
        elif val <= 15.0: return "Bom (40 a 60%)"
        elif val <= 25.0: return "Muito Bom (60 a 80%)"
        else: return "Excesso (> 80%)"

    elif col_name == "B (mg.dm-3)":
        if val < 0.20: return "Ruim (< 20%)"
        elif val < 0.40: return "Médio (20 a 40%)"
        elif val <= 0.60: return "Bom (40 a 60%)"
        elif val <= 1.00: return "Muito Bom (60 a 80%)"
        else: return "Excesso (> 80%)"

    elif col_name == "Cu (mg.dm-3)":
        if val < 0.4: return "Ruim (< 20%)"
        elif val < 0.8: return "Médio (20 a 40%)"
        elif val <= 1.5: return "Bom (40 a 60%)"
        elif val <= 3.0: return "Muito Bom (60 a 80%)"
        else: return "Excesso (> 80%)"

    elif col_name == "Mn (mg.dm-3)":
        if val < 3.0: return "Ruim (< 20%)"
        elif val < 6.0: return "Médio (20 a 40%)"
        elif val <= 12.0: return "Bom (40 a 60%)"
        elif val <= 20.0: return "Muito Bom (60 a 80%)"
        else: return "Excesso (> 80%)"

    elif col_name == "Zn (mg.dm-3)":
        if val < 1.0: return "Ruim (< 20%)"
        elif val < 2.0: return "Médio (20 a 40%)"
        elif val <= 4.0: return "Bom (40 a 60%)"
        elif val <= 8.0: return "Muito Bom (60 a 80%)"
        else: return "Excesso (> 80%)"

    elif col_name == "Fe (mg.dm-3)":
        if val < 12.0: return "Ruim (< 20%)"
        elif val < 24.0: return "Médio (20 a 40%)"
        elif val <= 45.0: return "Bom (40 a 60%)"
        elif val <= 80.0: return "Muito Bom (60 a 80%)"
        else: return "Excesso (> 80%)"

    elif col_name == "M.O. (%)":
        if val < 1.5: return "Ruim (< 20%)"
        elif val < 2.5: return "Médio (20 a 40%)"
        elif val <= 3.5: return "Bom (40 a 60%)"
        elif val <= 5.0: return "Muito Bom (60 a 80%)"
        else: return "Excesso (> 80%)"

    elif col_name == "Saturacao Bases (%)":
        if val < 40: return "Ruim (< 20%)"
        elif val < 50: return "Médio (20 a 40%)"
        elif val < 60: return "Bom (40 a 60%)"
        elif val < 75: return "Muito Bom (60 a 80%)"
        else: return "Excesso (> 80%)"

    elif col_name == "pH H2O":
        if val < 5.0: return "Ruim (< 20%)"
        elif val < 5.5: return "Médio (20 a 40%)"
        elif val < 6.0: return "Bom (40 a 60%)"
        elif val < 6.5: return "Muito Bom (60 a 80%)"
        else: return "Excesso (> 80%)"

    if val < 1.0: return "Ruim (< 20%)"
    elif val < 3.0: return "Médio (20 a 40%)"
    elif val < 5.0: return "Bom (40 a 60%)"
    elif val < 8.0: return "Muito Bom (60 a 80%)"
    else: return "Excesso (> 80%)"

ORDEM_CLASSES = ["Ruim (< 20%)", "Médio (20 a 40%)", "Bom (40 a 60%)", "Muito Bom (60 a 80%)", "Excesso (> 80%)"]
CORES_CLASSES = {
    "Ruim (< 20%)": "#d9534f",
    "Médio (20 a 40%)": "#f0ad4e",
    "Bom (40 a 60%)": "#5bc0de",
    "Muito Bom (60 a 80%)": "#5cb85c",
    "Excesso (> 80%)": "#0275d8"
}

# --- INTERFACE ---
st.title("🌱 Terra Nativa - Monitoramento de Solo & Fertigrama")

df_clientes = get_clientes()
if not df_clientes.empty:
    opcoes_clientes = {row['nome']: row['id'] for _, row in df_clientes.iterrows()}
    cliente_sel_nome = st.sidebar.selectbox("📂 Cliente Ativo:", list(opcoes_clientes.keys()))
    cliente_id_ativo = opcoes_clientes[cliente_sel_nome]
else:
    st.sidebar.info("Nenhum cliente cadastrado.")
    cliente_id_ativo = None

aba_monit, aba_talhoes, aba_fert, aba_upload, aba_cli = st.tabs([
    "📈 Comparativo Geral", 
    "🎯 Foco por Talhão / Pivô", 
    "📊 Diagnóstico Fertigrama", 
    "📤 Entrar/Importar Laudo", 
    "👤 Gerenciar Clientes & Laudos"
])

# --- ABA 1: COMPARATIVO GERAL ---
with aba_monit:
    st.header("📈 Comparação de Fertilidade (Geral / Monitoramento)")
    if cliente_id_ativo is None:
        st.info("Cadastre e selecione um cliente.")
    else:
        df_dados = get_analises_cliente(cliente_id_ativo)
        if df_dados.empty:
            st.warning("Nenhum laudo encontrado para este cliente.")
        else:
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1:
                fazenda_sel = st.selectbox("Fazenda / Gleba:", df_dados["Fazenda"].dropna().unique())
            with col_m2:
                profs_disp = df_dados[df_dados["Fazenda"] == fazenda_sel]["Profundidade"].dropna().unique()
                prof_sel = st.selectbox("Profundidade:", profs_disp)
            with col_m3:
                df_sub_faz = df_dados[(df_dados["Fazenda"] == fazenda_sel) & (df_dados["Profundidade"] == prof_sel)]
                talhoes_disp = ["Todos os Talhões / Pivôs"] + sorted(list(df_sub_faz["Talhao"].dropna().unique()))
                talhao_sel = st.selectbox("Talhão / Pivô:", talhoes_disp)
            with col_m4:
                nutrientes_opt = [
                    "P (mg.dm-3)", "K (mg.dm-3)", "Mg (cmolc.dm-3)", "Ca (cmolc.dm-3)", "S (mg.dm-3)",
                    "B (mg.dm-3)", "Cu (mg.dm-3)", "Zn (mg.dm-3)", "Mn (mg.dm-3)", "Fe (mg.dm-3)",
                    "M.O. (%)", "pH H2O", "Saturacao Bases (%)", "Argila (%)", "CTC pH 7,0 (cmolc.dm-3)"
                ]
                nutrientes_existentes = [n for n in nutrientes_opt if n in df_dados.columns]
                nutriente_sel = st.selectbox("Parâmetro/Nutriente:", nutrientes_existentes if nutrientes_existentes else nutrientes_opt)

            df_sub = df_sub_faz.copy()
            if talhao_sel != "Todos os Talhões / Pivôs":
                df_sub = df_sub[df_sub["Talhao"] == talhao_sel]

            df_c1 = df_sub[df_sub["Tipo_Coleta"].str.contains("Coleta 1", case=False, na=False)].dropna(subset=[nutriente_sel])
            df_c2 = df_sub[df_sub["Tipo_Coleta"].str.contains("Coleta 2|Monitoramento", case=False, na=False)].dropna(subset=[nutriente_sel])
            
            if df_c1.empty or df_c2.empty:
                st.warning("É necessário ter laudos salvos em 'Coleta 1 (Base)' e 'Coleta 2 (Monitoramento)' para comparar.")
            else:
                st.markdown("---")
                st.subheader(f"📊 Resumo Estatístico: {nutriente_sel} ({talhao_sel})")
                
                med1, med2 = df_c1[nutriente_sel].mean(), df_c2[nutriente_sel].mean()
                mediana1, mediana2 = df_c1[nutriente_sel].median(), df_c2[nutriente_sel].median()
                std1, std2 = df_c1[nutriente_sel].std(), df_c2[nutriente_sel].std()
                min1, min2 = df_c1[nutriente_sel].min(), df_c2[nutriente_sel].min()
                max1, max2 = df_c1[nutriente_sel].max(), df_c2[nutriente_sel].max()

                cv1 = (std1 / med1 * 100) if (med1 and not pd.isna(med1) and med1 != 0) else 0.0
                cv2 = (std2 / med2 * 100) if (med2 and not pd.isna(med2) and med2 != 0) else 0.0

                col_k1, col_k2, col_k3, col_k4 = st.columns(4)
                with col_k1:
                    st.info(f"**Coleta 1 (Base)**\n- **Amostras:** {len(df_c1)}\n- **Média:** {med1:.2f}\n- **Mediana:** {mediana1:.2f}\n- **Mín - Máx:** {min1:.2f} a {max1:.2f}\n- **CV (%):** {cv1:.1f}%")
                with col_k2:
                    st.success(f"**Coleta 2 (Monitoramento)**\n- **Amostras:** {len(df_c2)}\n- **Média:** {med2:.2f}\n- **Mediana:** {mediana2:.2f}\n- **Mín - Máx:** {min2:.2f} a {max2:.2f}\n- **CV (%):** {cv2:.1f}%")
                with col_k3:
                    delta_med = med2 - med1
                    pct_med = (delta_med / med1 * 100) if med1 != 0 else 0
                    st.metric("Variação da Média (Delta)", f"{delta_med:+.2f}", delta=f"{pct_med:+.1f}%")
                    delta_mediana = mediana2 - mediana1
                    st.metric("Variação da Mediana", f"{delta_mediana:+.2f}")
                with col_k4:
                    delta_cv = cv2 - cv1
                    st.metric("Variação do CV (%)", f"{delta_cv:+.1f}%", delta=f"{delta_cv:+.1f}%", delta_color="inverse")
                    st.caption("CV menor indica maior uniformidade no talhão.")

                st.markdown("---")
                st.subheader("📊 Fertigrama Comparativo (% de Distribuição de Área)")
                
                df_c1_class = df_c1.apply(lambda r: classificar_elemento(r[nutriente_sel], nutriente_sel, r), axis=1)
                df_c2_class = df_c2.apply(lambda r: classificar_elemento(r[nutriente_sel], nutriente_sel, r), axis=1)

                dist_c1 = df_c1_class.value_counts(normalize=True) * 100
                dist_c2 = df_c2_class.value_counts(normalize=True) * 100

                df_dist = pd.DataFrame({
                    "Classe": ORDEM_CLASSES,
                    "Coleta 1 (Base) (%)": [dist_c1.get(c, 0.0) for c in ORDEM_CLASSES],
                    "Coleta 2 (Monitoramento) (%)": [dist_c2.get(c, 0.0) for c in ORDEM_CLASSES]
                })

                fig_bar = go.Figure()
                fig_bar.add_trace(go.Bar(
                    x=df_dist["Classe"], 
                    y=df_dist["Coleta 1 (Base) (%)"],
                    name="Coleta 1 (Base)",
                    marker_color="#337ab7"
                ))
                fig_bar.add_trace(go.Bar(
                    x=df_dist["Classe"], 
                    y=df_dist["Coleta 2 (Monitoramento) (%)"],
                    name="Coleta 2 (Monitoramento)",
                    marker_color="#5cb85c"
                ))
                fig_bar.update_layout(
                    barmode="group",
                    title=f"Evolução das Classes de Fertilidade - {nutriente_sel} ({talhao_sel})",
                    xaxis_title="Classe Fertigrama",
                    yaxis_title="% do Total de Amostras",
                    legend_title="Momento da Coleta"
                )
                st.plotly_chart(fig_bar, use_container_width=True)

# --- ABA 2: FOCO POR TALHÃO / PIVÔ (NOVA ABA) ---
with aba_talhoes:
    st.header("🎯 Análise Comparativa Detalhada por Talhão / Pivô")
    if cliente_id_ativo is None:
        st.info("Selecione um cliente.")
    else:
        df_dados = get_analises_cliente(cliente_id_ativo)
        if df_dados.empty:
            st.warning("Nenhum dado cadastrado para este cliente.")
        else:
            col_t1, col_t2, col_t3 = st.columns(3)
            with col_t1:
                faz_t = st.selectbox("Fazenda:", df_dados["Fazenda"].dropna().unique(), key="t_faz")
            with col_t2:
                prof_t = st.selectbox("Profundidade:", df_dados[df_dados["Fazenda"] == faz_t]["Profundidade"].dropna().unique(), key="t_prof")
            with col_t3:
                df_sub_t_faz = df_dados[(df_dados["Fazenda"] == faz_t) & (df_dados["Profundidade"] == prof_t)]
                lista_talhoes_unicos = sorted(list(df_sub_t_faz["Talhao"].dropna().unique()))
                talhao_especifico = st.selectbox("Selecione o Talhão / Pivô Específico:", lista_talhoes_unicos if lista_talhoes_unicos else ["Geral"])

            if talhao_especifico:
                df_talhao_filtrado = df_sub_t_faz[df_sub_t_faz["Talhao"] == talhao_especifico]
                
                # Separa Base e Monitoramento para este talhão
                df_t_c1 = df_talhao_filtrado[df_talhao_filtrado["Tipo_Coleta"].str.contains("Coleta 1", case=False, na=False)]
                df_t_c2 = df_talhao_filtrado[df_talhao_filtrado["Tipo_Coleta"].str.contains("Coleta 2|Monitoramento", case=False, na=False)]

                st.markdown(f"### 📍 Pivô / Talhão: `{talhao_especifico}`")
                st.caption(f"Amostras na Coleta 1 (Base): {len(df_t_c1)} | Amostras no Monitoramento: {len(df_t_c2)}")

                if df_t_c1.empty and df_t_c2.empty:
                    st.info("Nenhum registro encontrado para este talhão específico.")
                else:
                    # Seleção de nutrientes para comparar neste talhão
                    nutrientes_opt = [
                        "P (mg.dm-3)", "K (mg.dm-3)", "Mg (cmolc.dm-3)", "Ca (cmolc.dm-3)", "S (mg.dm-3)",
                        "B (mg.dm-3)", "Cu (mg.dm-3)", "Zn (mg.dm-3)", "Mn (mg.dm-3)", "Fe (mg.dm-3)",
                        "M.O. (%)", "pH H2O", "Saturacao Bases (%)", "Argila (%)", "CTC pH 7,0 (cmolc.dm-3)"
                    ]
                    nutrientes_t_disp = [n for n in nutrientes_opt if n in df_talhao_filtrado.columns]
                    nutriente_t_sel = st.selectbox("Selecione o Atributo para Comparar no Talhão:", nutrientes_t_disp, key="nut_talhao_foco")

                    if nutriente_t_sel:
                        val_c1 = df_t_c1[nutriente_t_sel].dropna() if not df_t_c1.empty else pd.Series(dtype=float)
                        val_c2 = df_t_c2[nutriente_t_sel].dropna() if not df_t_c2.empty else pd.Series(dtype=float)

                        # Métricas lado a lado
                        col_m1, col_m2, col_m3 = st.columns(3)
                        m_c1 = val_c1.mean() if not val_c1.empty else 0.0
                        m_c2 = val_c2.mean() if not val_c2.empty else 0.0
                        dif_m = m_c2 - m_c1
                        pct_m = (dif_m / m_c1 * 100) if m_c1 != 0 else 0.0

                        col_m1.metric("Média Coleta 1 (Base)", f"{m_c1:.2f}")
                        col_m2.metric("Média Monitoramento", f"{m_c2:.2f}")
                        col_m3.metric("Evolução (Delta)", f"{dif_m:+.2f}", f"{pct_m:+.1f}%")

                        # Boxplot comparativo para o talhão selecionado
                        fig_box_talhao = go.Figure()
                        if not val_c1.empty:
                            fig_box_talhao.add_trace(go.Box(y=val_c1, name="Coleta 1 (Base)", boxpoints='all', marker_color="#337ab7"))
                        if not val_c2.empty:
                            fig_box_talhao.add_trace(go.Box(y=val_c2, name="Coleta 2 (Monitoramento)", boxpoints='all', marker_color="#5cb85c"))
                        
                        fig_box_talhao.update_layout(
                            title=f"Distribuição Amostral de {nutriente_t_sel} no Talhão {talhao_especifico}",
                            yaxis_title=nutriente_t_sel,
                            template="plotly_dark"
                        )
                        st.plotly_chart(fig_box_talhao, use_container_width=True)

                        # Tabela resumida de todos os nutrientes para este talhão específico
                        st.markdown(f"#### 📋 Tabela Resumo Comparativa - Talhão `{talhao_especifico}`")
                        resumo_talhao = []
                        for nut in nutrientes_t_disp:
                            s1 = df_t_c1[nut].dropna() if not df_t_c1.empty and nut in df_t_c1.columns else pd.Series(dtype=float)
                            s2 = df_t_c2[nut].dropna() if not df_t_c2.empty and nut in df_t_c2.columns else pd.Series(dtype=float)
                            
                            media_s1 = s1.mean() if not s1.empty else np.nan
                            media_s2 = s2.mean() if not s2.empty else np.nan
                            delta_nut = media_s2 - media_s1 if not pd.isna(media_s1) and not pd.isna(media_s2) else np.nan
                            
                            resumo_talhao.append({
                                "Nutriente / Atributo": nut,
                                "Média Base (C1)": round(media_s1, 2) if not pd.isna(media_s1) else "-",
                                "Média Monitoramento (C2)": round(media_s2, 2) if not pd.isna(media_s2) else "-",
                                "Variação (Delta)": round(delta_nut, 2) if not pd.isna(delta_nut) else "-"
                            })
                        
                        st.dataframe(pd.DataFrame(resumo_talhao), use_container_width=True)

# --- ABA 3: FERTIGRAMA ---
with aba_fert:
    st.header("📊 Fertigrama Geral por Laudo")
    if cliente_id_ativo is None:
        st.info("Selecione um cliente.")
    else:
        df_dados = get_analises_cliente(cliente_id_ativo)
        if df_dados.empty:
            st.warning("Nenhum dado cadastrado.")
        else:
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            with col_f1:
                faz_f = st.selectbox("Fazenda:", df_dados["Fazenda"].dropna().unique(), key="f_faz")
            with col_f2:
                prof_f = st.selectbox("Profundidade:", df_dados[df_dados["Fazenda"] == faz_f]["Profundidade"].dropna().unique(), key="f_prof")
            with col_f3:
                df_sub_f = df_dados[(df_dados["Fazenda"] == faz_f) & (df_dados["Profundidade"] == prof_f)]
                talhoes_f = ["Todos os Talhões / Pivôs"] + sorted(list(df_sub_f["Talhao"].dropna().unique()))
                talhao_f_sel = st.selectbox("Talhão / Pivô:", talhoes_f, key="f_talhao")
            with col_f4:
                tipo_f = st.selectbox("Tipo de Coleta:", df_sub_f["Tipo_Coleta"].dropna().unique(), key="f_tipo")

            df_laudo = df_sub_f[df_sub_f["Tipo_Coleta"] == tipo_f]
            if talhao_f_sel != "Todos os Talhões / Pivôs":
                df_laudo = df_laudo[df_laudo["Talhao"] == talhao_f_sel]
            
            nutrientes_eval = ["Argila (%)", "pH H2O", "P (mg.dm-3)", "K (mg.dm-3)", "Ca (cmolc.dm-3)", "Mg (cmolc.dm-3)", "S (mg.dm-3)", "B (mg.dm-3)", "Cu (mg.dm-3)", "Zn (mg.dm-3)", "Mn (mg.dm-3)", "Saturacao Bases (%)"]
            
            res_fert = []
            for nut in nutrientes_eval:
                if nut in df_laudo.columns:
                    classes = df_laudo.apply(lambda r: classificar_elemento(r[nut], nut, r), axis=1)
                    counts = classes.value_counts(normalize=True) * 100
                    row_dict = {"Nutriente": nut}
                    for c in ORDEM_CLASSES:
                        row_dict[c] = counts.get(c, 0.0)
                    res_fert.append(row_dict)

            if res_fert:
                df_chart_fert = pd.DataFrame(res_fert)
                fig_stack = go.Figure()
                for c in ORDEM_CLASSES:
                    if c in df_chart_fert.columns:
                        fig_stack.add_trace(go.Bar(
                            y=df_chart_fert["Nutriente"],
                            x=df_chart_fert[c],
                            name=c,
                            orientation='h',
                            marker_color=CORES_CLASSES.get(c, "#cccccc")
                        ))

                fig_stack.update_layout(
                    barmode='stack',
                    title=f"Distribuição de Fertilidade - {faz_f} | {talhao_f_sel} ({tipo_f})",
                    xaxis_title="Percentual de Amostras (%)",
                    yaxis_title="Nutriente / Parâmetro"
                )
                st.plotly_chart(fig_stack, use_container_width=True)

# --- ABA 4: UPLOAD ---
with aba_upload:
    st.header("📤 Importar Laudo Excel do Laboratório")
    if df_clientes.empty:
        st.warning("Cadastre um cliente na aba 'Clientes' primeiro.")
    else:
        with st.form("form_upload"):
            up_cliente = st.selectbox("Cliente:", list(opcoes_clientes.keys()))
            up_fazenda = st.text_input("Nome da Fazenda / Gleba:", value="Fazenda Suíça")
            up_prof = st.text_input("Profundidade:", value="0 - 10 cm")
            up_tipo = st.selectbox("Tipo de Coleta:", ["Coleta 1 (Base)", "Coleta 2 (Monitoramento)"])
            up_area = st.number_input("Área Total (ha):", value=100.0)
            up_grid = st.number_input("Grid Amostral (ha/ponto):", value=5.0)
            
            uploaded_file = st.file_uploader("Arquivo Excel do Laboratório (.xlsx)", type=["xlsx"])
            btn_salvar = st.form_submit_button("💾 Salvar Laudo no Banco de Dados")

            if btn_salvar and uploaded_file:
                df_raw = pd.read_excel(uploaded_file).replace("--", np.nan)
                
                colunas_num = [
                    "Argila (%)", "pH H2O", "P (mg.dm-3)", "P Mehlich-3 (mg.dm-3)", "K (mg.dm-3)", 
                    "M.O. (%)", "Ca (cmolc.dm-3)", "Mg (cmolc.dm-3)", "S (mg.dm-3)", "B (mg.dm-3)", 
                    "Cu (mg.dm-3)", "Zn (mg.dm-3)", "Mn (mg.dm-3)", "Fe (mg.dm-3)", "CTC pH 7,0 (cmolc.dm-3)", 
                    "Saturacao Bases (%)"
                ]
                for col in colunas_num:
                    if col in df_raw.columns:
                        df_raw[col] = pd.to_numeric(df_raw[col], errors="coerce")
                
                salvar_analise(opcoes_clientes[up_cliente], up_fazenda, up_prof, up_tipo, up_area, up_grid, df_raw)
                st.success(f"Laudo gravado com sucesso! Total de {len(df_raw)} amostras registradas.")
                st.rerun()

# --- ABA 5: GERENCIAR CLIENTES E LAUDOS ---
with aba_cli:
    st.header("👤 Gerenciamento de Clientes & Laudos Cadastrados")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.subheader("➕ Novo Cliente")
        novo_nome = st.text_input("Nome do Cliente:")
        if st.button("Cadastrar Cliente") and novo_nome.strip():
            add_cliente(novo_nome.strip())
            st.success("Cliente adicionado!")
            st.rerun()

    with col_c2:
        st.subheader("🗑️ Gerenciar Laudos Gravados")
        if cliente_id_ativo:
            conn = sqlite3.connect("terranativa.db")
            df_analises_db = pd.read_sql_query(
                "SELECT id, fazenda, profundidade, tipo_coleta FROM analises WHERE cliente_id = ?", 
                conn, params=(cliente_id_ativo,)
            )
            conn.close()
            
            if df_analises_db.empty:
                st.info("Nenhum laudo gravado no banco de dados para este cliente.")
            else:
                st.dataframe(df_analises_db)
                analise_para_excluir = st.selectbox("Selecione o ID do laudo para excluir/limpar:", df_analises_db["id"])
                if st.button("🗑️ Excluir Laudo Selecionado"):
                    excluir_analise(analise_para_excluir)
                    st.success(f"Laudo ID {analise_para_excluir} removido!")
                    st.rerun()
