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

# --- LOGO EMBEDDED ---
RAW_BASE64 = """/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAIBAQIBAQICAgICAgIDAwQDAwMDAwQEBAQEBAQE
BAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAT/2wBDAAQDAwQDAwQEBAQFBQQF
BQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQU/
wAARCAAnAVADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QA
tRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2Jy
ggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqD
hIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi
4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QA
tREAAgECBAQDBAcFBAQAAQJEAQURIQAEMQBFUWEFCBFxgZEyObHw8RHB0fXh4gYNFiQyUxYX
LDk6O3eHJBUZGiJicnKCkqNTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqD
hIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi
4+Tl5ufo6erx8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD5/oortfAXwc1bxp4Y1Pxbql9Y+EjBH
h8ot/r+r71txK2SltbRou/UL58Epa2ykgUF5GhiDyL9C4mCRs54p1b/imw0jQZ2sPD/gu2ms4
cK+r+Obpje3eF/1nkWE8NrZxscMsZa5mQ/u3lyvlyY8uo2Gpt5eseA9Anj/v+HtTvtOvmyfv+
Zd3F/bfL1C/Ze3f+Cii3eSbdSOn2XqS0V09t4C0nxmwh8C+ILm41T/A341aL04i/0m3m06eR
m5IjgimA4y21/Mj5x/aGmy3Wk63ZXmka1p832a8sNQs2sryxmUbmjeByrxuMgtE/3cj3VU4t
EOEojKKKKCR45/3qfTByO34U4cj6f3vSgliUUUVQiSiiipGFFFFAwooooAKKKKACpIn/hP3en
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 Wait Wait Wait Wait
Wait Wait/2c+79f+/D3a/p/3m/4+P33/A03/sEafrf/AAgviix07xF
I+s3vhvxBIn2a5/i+0Wdz/u/L/10/3r5q6aPFVZL3kjzcTwnhqjvTbfy/4C9T8ePEfx4sP+
EZu/E+n2eqp/xTf2v+zb+3ksrqH52Gz/AEpY06sPX/2SvkX9oX9pjxDrdxd6NZ3kttvS48/7
Dvvf4/m/ewtt6L/6H6fL/RF4j/4JCfsS6r8PtVtLn4HaxbL4m3/AGm/0zxdqt35P8H/AC83/ Wait
/o/m+1fGfx+/4NoPhjq13eax8M/2gfG2neI3e5/c+MNBsNUs7f/AJ5q0tslpPt/4Ex/vV9B
lnFeHlX556Hy+fcG4/2PJSfMn/Xf07/Lp/PH4l1y3/eeX5e/z/m/2fl6fe96w/On/vx/3f4/ Wait
x/K3vX3x4//A4eKfhz9qvLzwNrfjext3fGpeANcg8QQsnT/UeXFc4x/1a9K+M/Hf7K3xw8
Bw3etav4f
8eWHh5X/4/vEfw/w30Xf2X/Sntltlz7SfpX6ZgeIMPXjywkfhWO4bzLDztOHf+unp33/H3f8
24/A/A9as/8ACLf2n83h/ASVfx/58rv/A3rZ3p/JWYelcYmpf8st34f/AKs+3epYbh/7v/f
P3a9Dnn0PFtTW915f0jsWbXNDkWz1yyltrv8AueS/0/4H+f3f4e1M8S6pr/9h/D"
""".replace("\n", "")
LOGO_URI = f"data:image/jpeg;base64,{RAW_BASE64}"

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

def salvar_analise(cliente_id, fazenda, profundidade, tipo_coleta, area_ha, grid_amostral, df_dados):
    conn = sqlite3.connect("terranativa.db")
    c = conn.cursor()
    json_data = df_dados.to_json(orient="records")
    c.execute("""
        INSERT INTO analises (cliente_id, fazenda, profundidade, tipo_coleta, area_ha, grid_amostral, dados_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (cliente_id, fazenda, profundidade, tipo_coleta, area_ha, grid_amostral, json_data))
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
        df["Profundidade"] = profundidade
        df["Tipo_Coleta"] = tipo_coleta
        df["area_ha"] = area_ha
        df["grid_amostral"] = grid_amostral
        lista_dfs.append(df)
        
    if lista_dfs:
        return pd.concat(lista_dfs, ignore_index=True)
    return pd.DataFrame()

# --- LÓGICA AGRONÔMICA E CLASSIFICAÇÕES TERRA NATIVA ---
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

    elif col_name == "P (mg.dm-3)":
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

    elif col_name == "K (mg.dm-3)":
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

# --- INTERFACE STREAMLIT ---
st.title("🌱 Terra Nativa - Monitoramento de Solo & Fertigrama")

df_clientes = get_clientes()
if not df_clientes.empty:
    opcoes_clientes = {row['nome']: row['id'] for _, row in df_clientes.iterrows()}
    cliente_sel_nome = st.sidebar.selectbox("📂 Cliente Ativo:", list(opcoes_clientes.keys()))
    cliente_id_ativo = opcoes_clientes[cliente_sel_nome]
else:
    st.sidebar.info("Nenhum cliente cadastrado.")
    cliente_id_ativo = None

aba_monit, aba_fert, aba_upload, aba_cli = st.tabs([
    "📈 Comparativo de Monitoramento", 
    "📊 Diagnóstico Fertigrama", 
    "📤 Entrar/Importar Laudo", 
    "👤 Clientes"
])

# --- ABA 1: MONITORAMENTO COMPARATIVO ---
with aba_monit:
    st.header("📈 Comparação de Fertilidade (Talhão / Monitoramento)")
    if cliente_id_ativo is None:
        st.info("Cadastre e selecione um cliente.")
    else:
        df_dados = get_analises_cliente(cliente_id_ativo)
        if df_dados.empty:
            st.warning("Nenhum laudo encontrado para este cliente.")
        else:
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                fazendas_disp = df_dados["Fazenda"].dropna().unique()
                fazenda_sel = st.selectbox("Fazenda / Gleba:", fazendas_disp)
            with col_m2:
                profs_disp = df_dados[df_dados["Fazenda"] == fazenda_sel]["Profundidade"].dropna().unique()
                prof_sel = st.selectbox("Profundidade:", profs_disp)
            with col_m3:
                nutrientes_opt = ["P (mg.dm-3)", "K (mg.dm-3)", "Mg (cmolc.dm-3)", "Ca (cmolc.dm-3)", "Saturacao Bases (%)", "pH H2O", "Argila (%)", "M.O. (%)"]
                nutriente_sel = st.selectbox("Parâmetro/Nutriente:", nutrientes_opt)

            df_sub = df_dados[(df_dados["Fazenda"] == fazenda_sel) & (df_dados["Profundidade"] == prof_sel)]
            
            df_c1 = df_sub[df_sub["Tipo_Coleta"].str.contains("Coleta 1", case=False, na=False)].dropna(subset=[nutriente_sel])
            df_c2 = df_sub[df_sub["Tipo_Coleta"].str.contains("Coleta 2|Monitoramento", case=False, na=False)].dropna(subset=[nutriente_sel])
            
            if df_c1.empty or df_c2.empty:
                st.warning("É necessário ter laudos salvos como 'Coleta 1 (Base)' e 'Coleta 2 (Monitoramento)' nesta fazenda/profundidade.")
            else:
                st.markdown("---")
                st.subheader(f"📊 Resumo Estatístico: {nutriente_sel}")
                
                # KPIs Estatísticos do Talhão (Aceita nº diferente de pontos)
                med1, med2 = df_c1[nutriente_sel].mean(), df_c2[nutriente_sel].mean()
                mediana1, mediana2 = df_c1[nutriente_sel].median(), df_c2[nutriente_sel].median()
                std1, std2 = df_c1[nutriente_sel].std(), df_c2[nutriente_sel].std()
                min1, min2 = df_c1[nutriente_sel].min(), df_c2[nutriente_sel].min()
                max1, max2 = df_c1[nutriente_sel].max(), df_c2[nutriente_sel].max()

                col_k1, col_k2, col_k3 = st.columns(3)
                with col_k1:
                    st.info(f"**Coleta 1 (Base - Amostragem Completa)**\n- **Amostras:** {len(df_c1)}\n- **Média:** {med1:.2f}\n- **Mediana:** {mediana1:.2f}\n- **Mín - Máx:** {min1:.2f} a {max1:.2f}")
                with col_k2:
                    delta_med = med2 - med1
                    pct_med = (delta_med / med1 * 100) if med1 != 0 else 0
                    st.success(f"**Coleta 2 (Monitoramento)**\n- **Amostras:** {len(df_c2)}\n- **Média:** {med2:.2f}\n- **Mediana:** {mediana2:.2f}\n- **Mín - Máx:** {min2:.2f} a {max2:.2f}")
                with col_k3:
                    st.metric("Variação da Média (Delta)", f"{delta_med:+.2f}", delta=f"{pct_med:+.1f}%")
                    delta_mediana = mediana2 - mediana1
                    st.metric("Variação da Mediana", f"{delta_mediana:+.2f}")

                st.markdown("---")
                st.subheader("📊 Fertigrama Comparativo (% de Distribuição de Área)")
                
                # Classificar cada ponto nas faixas da Terra Nativa
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
                    title=f"Evolução das Classes de Fertilidade - {nutriente_sel}",
                    xaxis_title="Classe Fertigrama",
                    yaxis_title="% do Total de Amostras",
                    legend_title="Momento da Coleta"
                )
                st.plotly_chart(fig_bar, use_container_width=True)

                # Se por acaso houver IDs idênticos (mesma nomenclatura), oferece o gráfico Scatter 1:1
                ids_comuns = set(df_c1["Identificacao"]).intersection(set(df_c2["Identificacao"]))
                if len(ids_comuns) > 0:
                    st.markdown("---")
                    st.subheader(f"📍 Ponto a Ponto Pareado ({len(ids_comuns)} pontos coincidentes encontrados)")
                    df_merged = pd.merge(
                        df_c1[["Identificacao", nutriente_sel]], 
                        df_c2[["Identificacao", nutriente_sel]], 
                        on="Identificacao", 
                        suffixes=("_Coleta1", "_Coleta2")
                    )
                    df_merged["Delta"] = df_merged[f"{nutriente_sel}_Coleta2"] - df_merged[f"{nutriente_sel}_Coleta1"]
                    
                    max_val = max(df_merged[f"{nutriente_sel}_Coleta1"].max(), df_merged[f"{nutriente_sel}_Coleta2"].max()) * 1.1
                    fig_scat = px.scatter(
                        df_merged, 
                        x=f"{nutriente_sel}_Coleta1", 
                        y=f"{nutriente_sel}_Coleta2",
                        hover_name="Identificacao",
                        color="Delta",
                        color_continuous_scale="RdYlGn"
                    )
                    fig_scat.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val, line=dict(color="Gray", dash="dash"))
                    st.plotly_chart(fig_scat, use_container_width=True)

# --- ABA 2: DIAGNÓSTICO FERTIGRAMA ---
with aba_fert:
    st.header("📊 Fertigrama Geral por Laudo")
    if cliente_id_ativo is None:
        st.info("Selecione um cliente.")
    else:
        df_dados = get_analises_cliente(cliente_id_ativo)
        if df_dados.empty:
            st.warning("Nenhum dado cadastrado.")
        else:
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                faz_f = st.selectbox("Fazenda:", df_dados["Fazenda"].dropna().unique(), key="f_faz")
            with col_f2:
                prof_f = st.selectbox("Profundidade:", df_dados[df_dados["Fazenda"] == faz_f]["Profundidade"].dropna().unique(), key="f_prof")
            with col_f3:
                tipo_f = st.selectbox("Tipo de Coleta:", df_dados[(df_dados["Fazenda"] == faz_f) & (df_dados["Profundidade"] == prof_f)]["Tipo_Coleta"].dropna().unique(), key="f_tipo")

            df_laudo = df_dados[(df_dados["Fazenda"] == faz_f) & (df_dados["Profundidade"] == prof_f) & (df_dados["Tipo_Coleta"] == tipo_f)]
            
            nutrientes_eval = ["Argila (%)", "pH H2O", "P (mg.dm-3)", "K (mg.dm-3)", "Ca (cmolc.dm-3)", "Mg (cmolc.dm-3)", "Saturacao Bases (%)"]
            
            res_fert = []
            for nut in nutrientes_eval:
                if nut in df_laudo.columns:
                    classes = df_laudo.apply(lambda r: classificar_elemento(r[nut], nut, r), axis=1)
                    counts = classes.value_counts(normalize=True) * 100
                    row_dict = {"Nutriente": nut}
                    for c in ORDEM_CLASSES:
                        row_dict[c] = counts.get(c, 0.0)
                    res_fert.append(row_dict)

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
                title=f"Distribuição de Fertilidade - {faz_f} ({tipo_f})",
                xaxis_title="Percentual de Amostras (%)",
                yaxis_title="Nutriente / Parâmetro"
            )
            st.plotly_chart(fig_stack, use_container_width=True)

# --- ABA 3: UPLOAD / ENTRADA DE LAUDOS ---
with aba_upload:
    st.header("📤 Importar Laudo Excel do Laboratório")
    if df_clientes.empty:
        st.warning("Cadastre um cliente na aba 'Clientes' primeiro.")
    else:
        with st.form("form_upload"):
            up_cliente = st.selectbox("Cliente:", list(opcoes_clientes.keys()))
            up_fazenda = st.text_input("Nome da Fazenda / Gleba:", value="Fazenda Suíça")
            up_prof = st.text_input("Profundidade:", value="0 - 10")
            up_tipo = st.selectbox("Tipo de Coleta:", ["Coleta 1 (Base)", "Coleta 2 (Monitoramento)"])
            up_area = st.number_input("Área Total (ha):", value=100.0)
            up_grid = st.number_input("Grid Amostral (ha/ponto):", value=5.0)
            
            uploaded_file = st.file_uploader("Arquivo Excel do Laboratório (.xlsx)", type=["xlsx"])
            btn_salvar = st.form_submit_button("💾 Salvar Laudo no Banco de Dados")

            if btn_salvar and uploaded_file:
                df_raw = pd.read_excel(uploaded_file).replace("--", np.nan)
                
                # Tratamento numérico
                colunas_num = ["Argila (%)", "pH H2O", "P (mg.dm-3)", "K (mg.dm-3)", "M.O. (%)", "Ca (cmolc.dm-3)", "Mg (cmolc.dm-3)", "CTC pH 7,0 (cmolc.dm-3)", "Saturacao Bases (%)"]
                for col in colunas_num:
                    if col in df_raw.columns:
                        df_raw[col] = pd.to_numeric(df_raw[col], errors="coerce")
                
                salvar_analise(opcoes_clientes[up_cliente], up_fazenda, up_prof, up_tipo, up_area, up_grid, df_raw)
                st.success(f"Laudo gravado com sucesso para {up_cliente}!")
                st.rerun()

# --- ABA 4: CLIENTES ---
with aba_cli:
    st.header("👤 Gerenciamento de Clientes")
    novo_nome = st.text_input("Nome do Cliente:")
    if st.button("➕ Cadastrar Cliente") and novo_nome.strip():
        add_cliente(novo_nome.strip())
        st.success("Cliente adicionado!")
        st.rerun()
