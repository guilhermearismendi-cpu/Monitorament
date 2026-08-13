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
3u4/p/vf5LKiX2HTr9f84qkSXE+4PTv/s/+yfr/sU+mI25Aev+fxp9O9yAooopAFFFFAgoooq
hBRRRQAUUUUhhRRRQAUUUUhhRRRQAEZHNFFFIRG0Ebrho1P4U0WNux4gj/AO+KmByKKLiL3g
bx3f/Cb4e3Xxc0fxf/wg/iDwvP/AGT4G1x0tTaf8JRfwut3eXmnoN9/aWWmqSftK+RczXtpIs
E3k3CwaPwf/A4m+/isvCvwA/bg8DaTf22jxf2HpfxU0u4fR9ZtV3Eie989ZbK8Zmfm/tZbI7f
3jw/3fij9tX9rmf9or/haXw38Xhi28eeDPipr8Xj2ymv9Veyv/hr4yW3WyubvTY1hlivtLurS
2svtllI9pM7W0TQXNo017I3x83kE77m538fxA72+n/163I/Svh/r1SLsfa0OHoSpLm6v8Apf1
/lb+pDx9e/B7/gMN/srXfiHwI3g/4pafocflJ/blmsmreAtSff5S3MDKt7oN/JtOxfeFZl4S7
ik+b8/PFv7J/xe/4Jv+LLbxrq82jXmmeKNS/4R8a7c2H2i91fSjC3nafrllD5cV4i/LNb6lb2
kP2aaKWW0eCbyA3i/7G/7df7Tf7Avxetvjn+yj8XNa+FPiyO0Oly31gsc1tqFmzozW35i3C
S299a/uUkEM6MhkSOUYljik/d3/AIJwft1f8EZP+C2v7P037OfinX5fBXjC4tft+u/s6and/Y
rGxuVkEj6n4F/f8+iaerfv1isC01s4330M32f7Y+kcUam5pTq4Wrrsfhl4++Evwx+Oenaxr
PwQudJ0nxB4d0i38RazoWla6upaXJps83lpqthclllutIldkDXLKs1q0qpeQ2mbfzvmI8f/s
3f0p1ftH/cDf/Bs+vwH+I6fFP4DyeD/Atnr2ptc+DfiTo/mN4B8aagylX0nxDYv5jeGtWddo
+1bFsLtl+0Wslynm2kX44fEr9nrxV4An1aaz3+I4dB1S60XxG+m2M8mpeCtTtZlgutM13Tgvn
6ddwykqSyy2x3L5dzMz10/1f+v63PPxWFdN8y2OS8IePvGvw81Jda+HfjTXvA2qwA+VrHhnV
JdJvh9GuYCrN/D3/nmDXZ/8NYfFrx1jTvjhrPh/4pW5/5iWvWSukeKBn5WZtc04wzzPjnd
fpcA4+7mvI0uLdn+zwyo3y9G4/P3qUq1Inm1I/C2etv4U+Hfi6SOT4aeP00q9k6eHfidPH
YyytwP3OuQL/AGsp/2ro6en16fSnh1E81xY3mganY6lpl9/ZWp6JqFnf6fdtCsnlywzxz2sz
Ie/lySADg+3zG/I4Nf4s1rX6l5N5pXijUNOl/v/bbiaBv/Am+qD65Nbc8m2p4K/s5R6I8uoq3
d6p53Gf/s/8/16VV2N9/0oscdxtFSRR5+/0o8tv4PSoER0VIsTDvUkSfx+vv9/6dveiw1CTI
ooyevv9/pT4og2R/np2+p5qwI88fe/z0p3lr2o5TT2REkO3Gevf9c1Iqbcf3sUpAByR0+lKo
A+UD+dFi1FCqoxkf1/zzS0UUDCiiigAooooEFJv9qd/D+eP/AB6igBf+A0i49vyo/CAe/f5
etA9Mf/YoAWiiigAooorI5wooooGFFFFIAooooA/nr2N/AOnp+NO2N9/26Y4qaS3K84o8tv
4PSuE+1sQ7GH3ev+f8/hVi1ubuyuob7S9QvdKvrWVZ4LyylazuraRWDI8csWHRgfQ5o2N9f1
x+X/AOujY31pC3P1/D+Cdf84E17T/s2/s26NpPwp/b68C/8ADWnhSytfsFr4q0/U/sPjfS7b/a/f3Eces26d3uWhuyet23Svhvxn+1F/AE35f2p
1r911S88D3vhy/sbr/Srf59U0O2+0f9N3l2f9N
x3/U6l+yh8f2+
IGp+Ev2f/B2m/tAaVd32
p3f
2bRP
AepWWo3
/kX
NxKx2aTcTR3m/yP+mSfxen/s3X6/X+c/1/8AgOa
njsP/P234dPx/H
v2Pl
f
2yv
2I/g
9q/x
Jv/ANs/
4a
2sfgjQf
/A
B4t8R/8AnfS5bux+2R2S/
wDPxHcxv/2q1
/V
1165uN9/4H8A33hxf7R
vf
D3
hD
7P
/t23/X95
X6S+A/jP8Bf
A+tfY9
d+GP2S73
7f
E3hDxS
lx/Bs/In2/f
3
/AP
P
/Oa
7vxx
8f/AI1fF
O3+w+L/j34
k2f
8A/
X557j
9/
+P
/T3/u/X8c/yS113
e3
/D
+X
+
p+0N
qvh261/T9G0D+yrvxSnn
i/v9Pso/m+ffv
23
S+Y8i
/3H79+a7S2+L+
l
+
37+xt9S1S2v
9v9n3m/
7L9j/v8Aky
p/f
T94v/Xv6/3e4S384+X/A
8eI/O3
f/A
a+P/I
s//a/84re
+G/xg0v9mvxt/
aEHgA3WpX
/A
5x63pce/3k/x9f18
a8/l
9r4m1z7f
u8Tf8InYx
+
+f
0/+3W/p
e
f4P17S77/AIS
DT/
A/
if8Atq/e
38u28P
2f/
X
P/AF8y7+
X
p9
+X56
+2/B
2m+1t9I+
C
/jD+2
vh7A24I3/AB4P
5j/u/s+5
mj/uf/W
47f96S2
11213+V
f4q0/
T/A3
8AYfgS3tLbf/b
d7qVv
/A
3X3k21
/c9/
4O
+O/2yvi
f/
2t4g1O
/
8f28c/
m
/8An99/
s/+
j
374
+e/il+zx4+8T
2
19598X1
3f/y38v+/5e
9l/P+E/e7f414j0
/
wCL/2G0e4/smX
+
x/t32K
2t3
/AL
m/mH/ANnr0Xw
T+134t2
f8U9p6x/3X3
7x+l/
D
5X/t+P
5vU/
d909P+I59fx34m/ZM+Oeh/
3
Ph6+pafv/wC
Wf5e33ev6/L
Xl/ibwhr/hz
U/
sHiTRdV0
bUH
e5+w6p
YyWf47
G/5a
f7X1+/ur+iv/A
I294/f96vP/ABR+zh/wk+/U
d
An0vVL353k
0m/t+P
+/d
/wD1u406/X2
/X/qA
4+3/Dfh/Tf6e
0/Q/5x/
U+H4L0v
+39bS
0
v3f+x
NN2
+
S8v2
3
7v/A
E17T7
H
StO2a
PqG623/AL2
33Sfe/j
8334/Anr2/xl+xf8
e
NB0m3
vE8DapawL/q
9N23
kX
y/L83kK3ze3m+1eR+P
/
AO2+F
dqf/DOuaf
Ppupb/k/uS
v/AH1
r/33v
s/L
v9T/v9D/h6L9
i+I4/
w37f
59
Dnd
i58
p
+L8P
2X2L9x+/uN903m
I6v/s
/d+8e4
x+X93
6L/4E
v7i3/wC3S4
+2x4/4GteR/X/e/w
B7/
Z21O
kse
70y/
/ff/q9e3/AMV
1m/8A
Ua5/x+
X+2u9/e/T/I
f1/
X/mS0U
Uf9
Wv6/4
1mR
/X9
/wBbBR
R
S3

"""
LOGO_URI = f"data:image/jpeg;base64,{RAW_BASE64}"

# --- BANCO DE DADOS (SQLITE) ---
def init_db():
    conn = sqlite3.connect("terranativa.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
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
    try:
        c.execute("INSERT INTO clientes (nome) VALUES (?)", (nome,))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def delete_cliente(cliente_id):
    conn = sqlite3.connect("terranativa.db")
    c = conn.cursor()
    c.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
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

def delete_analise(analise_id):
    conn = sqlite3.connect("terranativa.db")
    c = conn.cursor()
    c.execute("DELETE FROM analises WHERE id = ?", (analise_id,))
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

        # Extrair ou manter Talhão
        if "Talhao" not in df.columns and "Talhão" in df.columns:
            df["Talhao"] = df["Talhão"]
        elif "Talhao" not in df.columns:
            def extrair_talhao(texto):
                texto_str = str(texto)
                parts = texto_str.split("_")
                for p in parts:
                    if p.startswith("T") and p[1:].isdigit():
                        return f"Talhão {p[1:]}"
                    elif "Talhao" in p or "Talhão" in p:
                        return p
                return "Geral / Não Especificado"

            df["Talhao"] = df["Identificacao"].apply(extrair_talhao) if "Identificacao" in df.columns else "Geral"

        lista_dfs.append(df)
        
    if lista_dfs:
        return pd.concat(lista_dfs, ignore_index=True)
    return pd.DataFrame()

# --- FUNÇÃO DE LIMPEZA E PADRONIZAÇÃO DE DADOS (BLINDADA) ---
COLUNAS_PADRAO_NUTRIENTES = [
    "Identificacao", "Talhao", "Argila (%)", "pH H2O", "P (mg.dm-3)", "P Mehlich-3 (mg.dm-3)", 
    "K (mg.dm-3)", "M.O. (%)", "Ca (cmolc.dm-3)", "Mg (cmolc.dm-3)", "S (mg.dm-3)", 
    "B (mg.dm-3)", "Cu (mg.dm-3)", "Zn (mg.dm-3)", "Mn (mg.dm-3)", "Fe (mg.dm-3)", 
    "CTC pH 7,0 (cmolc.dm-3)", "Saturacao Bases (%)"
]

def limpar_e_padronizar_df(df, mapa_colunas):
    """
    Renomeia as colunas de acordo com o mapeamento selecionado pelo usuário,
    evita duplicidade de nomes de colunas e limpa caracteres numéricos com segurança.
    """
    df_clean = df.copy()
    
    # Inverter dicionário de mapeamento para renomeação
    mapa_inverso = {v: k for k, v in mapa_colunas.items() if v != "-- Ignorar --"}
    df_clean = df_clean.rename(columns=mapa_inverso)

    # 1. Resolver colunas duplicadas geradas pelo mapeamento mantendo a primeira ocorrência
    df_clean = df_clean.loc[:, ~df_clean.columns.duplicated(keep='first')]

    # 2. Tratar colunas numéricas padrão de forma segura
    for col in COLUNAS_PADRAO_NUTRIENTES:
        if col in df_clean.columns and col not in ["Identificacao", "Talhao"]:
            col_data = df_clean[col]
            
            # Garantir que estamos lidando com uma Series (coluna única)
            if isinstance(col_data, pd.DataFrame):
                col_data = col_data.iloc[:, 0]
                
            # Limpeza de vírgulas, textos e conversão para float
            s_str = col_data.astype(str).str.replace(",", ".", regex=False)
            s_str = s_str.replace(["--", "ND", "None", "nan", "null", "NaN", "N/A"], np.nan)
            df_clean[col] = pd.to_numeric(s_str, errors="coerce")

    # 3. Tratar Identificacao com segurança
    if "Identificacao" in df_clean.columns:
        if isinstance(df_clean["Identificacao"], pd.DataFrame):
            df_clean["Identificacao"] = df_clean["Identificacao"].iloc[:, 0]
        df_clean["Identificacao"] = df_clean["Identificacao"].astype(str).str.strip()
    else:
        df_clean["Identificacao"] = [f"Amostra_{i+1}" for i in range(len(df_clean))]
        
    # 4. Tratar Talhao se mapeado
    if "Talhao" in df_clean.columns:
        if isinstance(df_clean["Talhao"], pd.DataFrame):
            df_clean["Talhao"] = df_clean["Talhao"].iloc[:, 0]
        df_clean["Talhao"] = df_clean["Talhao"].astype(str).str.strip()

    return df_clean

# --- LÓGICA AGRONÔMICA E CLASSIFICAÇÕES TERRA NATIVA ---
def classificar_elemento(val, col_name, row=None):
    if pd.isna(val):
        return None
    val = float(val)
    
    # 1. Argila (%)
    if col_name == "Argila (%)":
        if val < 15: return "Ruim (< 20%)"
        elif val < 20: return "Médio (20 a 40%)"
        elif val < 25: return "Bom (40 a 60%)"
        elif val <= 35: return "Muito Bom (60 a 80%)"
        else: return "Excesso (> 80%)"

    # 2. Fósforo (P)
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

    # 3. Potássio (K)
    elif col_name in ["K (mg.dm-3)", "K (cmolc.dm-3)"]:
        if "cmolc" in col_name:
            val = val * 391.0 # converte para mg.dm-3 para classificar
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

    # 4. Magnésio (Mg)
    elif col_name == "Mg (cmolc.dm-3)":
        if val < 0.4: return "Ruim (< 20%)"
        elif val < 0.8: return "Médio (20 a 40%)"
        elif val <= 1.2: return "Bom (40 a 60%)"
        elif val <= 1.8: return "Muito Bom (60 a 80%)"
        else: return "Excesso (> 80%)"

    # 5. Cálcio (Ca)
    elif col_name == "Ca (cmolc.dm-3)":
        if val < 1.5: return "Ruim (< 20%)"
        elif val < 2.5: return "Médio (20 a 40%)"
        elif val <= 4.0: return "Bom (40 a 60%)"
        elif val <= 6.0: return "Muito Bom (60 a 80%)"
        else: return "Excesso (> 80%)"

    # 6. Enxofre (S)
    elif col_name == "S (mg.dm-3)":
        if val < 5.0: return "Ruim (< 20%)"
        elif val < 10.0: return "Médio (20 a 40%)"
        elif val <= 15.0: return "Bom (40 a 60%)"
        elif val <= 25.0: return "Muito Bom (60 a 80%)"
        else: return "Excesso (> 80%)"

    # 7. Boro (B)
    elif col_name == "B (mg.dm-3)":
        if val < 0.20: return "Ruim (< 20%)"
        elif val < 0.40: return "Médio (20 a 40%)"
        elif val <= 0.60: return "Bom (40 a 60%)"
        elif val <= 1.00: return "Muito Bom (60 a 80%)"
        else: return "Excesso (> 80%)"

    # 8. Cobre (Cu)
    elif col_name == "Cu (mg.dm-3)":
        if val < 0.4: return "Ruim (< 20%)"
        elif val < 0.8: return "Médio (20 a 40%)"
        elif val <= 1.5: return "Bom (40 a 60%)"
        elif val <= 3.0: return "Muito Bom (60 a 80%)"
        else: return "Excesso (> 80%)"

    # 9. Manganês (Mn)
    elif col_name == "Mn (mg.dm-3)":
        if val < 3.0: return "Ruim (< 20%)"
        elif val < 6.0: return "Médio (20 a 40%)"
        elif val <= 12.0: return "Bom (40 a 60%)"
        elif val <= 20.0: return "Muito Bom (60 a 80%)"
        else: return "Excesso (> 80%)"

    # 10. Zinco (Zn)
    elif col_name == "Zn (mg.dm-3)":
        if val < 1.0: return "Ruim (< 20%)"
        elif val < 2.0: return "Médio (20 a 40%)"
        elif val <= 4.0: return "Bom (40 a 60%)"
        elif val <= 8.0: return "Muito Bom (60 a 80%)"
        else: return "Excesso (> 80%)"

    # 11. Ferro (Fe)
    elif col_name == "Fe (mg.dm-3)":
        if val < 12.0: return "Ruim (< 20%)"
        elif val < 24.0: return "Médio (20 a 40%)"
        elif val <= 45.0: return "Bom (40 a 60%)"
        elif val <= 80.0: return "Muito Bom (60 a 80%)"
        else: return "Excesso (> 80%)"

    # 12. Matéria Orgânica (%)
    elif col_name == "M.O. (%)":
        if val < 1.5: return "Ruim (< 20%)"
        elif val < 2.5: return "Médio (20 a 40%)"
        elif val <= 3.5: return "Bom (40 a 60%)"
        elif val <= 5.0: return "Muito Bom (60 a 80%)"
        else: return "Excesso (> 80%)"

    # 13. Saturação por Bases (%)
    elif col_name == "Saturacao Bases (%)":
        if val < 40: return "Ruim (< 20%)"
        elif val < 50: return "Médio (20 a 40%)"
        elif val < 60: return "Bom (40 a 60%)"
        elif val < 75: return "Muito Bom (60 a 80%)"
        else: return "Excesso (> 80%)"

    # 14. pH H2O
    elif col_name == "pH H2O":
        if val < 5.0: return "Ruim (< 20%)"
        elif val < 5.5: return "Médio (20 a 40%)"
        elif val < 6.0: return "Bom (40 a 60%)"
        elif val < 6.5: return "Muito Bom (60 a 80%)"
        else: return "Excesso (> 80%)"

    # Padrão para outros parâmetros
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
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1:
                fazendas_disp = df_dados["Fazenda"].dropna().unique()
                fazenda_sel = st.selectbox("Fazenda / Gleba:", fazendas_disp)
            with col_m2:
                profs_disp = df_dados[df_dados["Fazenda"] == fazenda_sel]["Profundidade"].dropna().unique()
                prof_sel = st.selectbox("Profundidade:", profs_disp)
            with col_m3:
                df_sub_faz = df_dados[(df_dados["Fazenda"] == fazenda_sel) & (df_dados["Profundidade"] == prof_sel)]
                talhoes_disp = ["Todos os Talhões"] + list(df_sub_faz["Talhao"].dropna().unique())
                talhao_sel = st.selectbox("Talhão:", talhoes_disp)
            with col_m4:
                nutrientes_opt = [
                    "P (mg.dm-3)", "K (mg.dm-3)", "Mg (cmolc.dm-3)", "Ca (cmolc.dm-3)", "S (mg.dm-3)",
                    "B (mg.dm-3)", "Cu (mg.dm-3)", "Zn (mg.dm-3)", "Mn (mg.dm-3)", "Fe (mg.dm-3)",
                    "M.O. (%)", "pH H2O", "Saturacao Bases (%)", "Argila (%)", "CTC pH 7,0 (cmolc.dm-3)"
                ]
                nutrientes_existentes = [n for n in nutrientes_opt if n in df_dados.columns]
                nutriente_sel = st.selectbox("Parâmetro/Nutriente:", nutrientes_existentes if nutrientes_existentes else nutrientes_opt)

            df_sub = df_sub_faz.copy()
            if talhao_sel != "Todos os Talhões":
                df_sub = df_sub[df_sub["Talhao"] == talhao_sel]

            df_c1 = df_sub[df_sub["Tipo_Coleta"].str.contains("Coleta 1", case=False, na=False)].dropna(subset=[nutriente_sel]) if nutriente_sel in df_sub.columns else pd.DataFrame()
            df_c2 = df_sub[df_sub["Tipo_Coleta"].str.contains("Coleta 2|Monitoramento", case=False, na=False)].dropna(subset=[nutriente_sel]) if nutriente_sel in df_sub.columns else pd.DataFrame()
            
            if df_c1.empty or df_c2.empty:
                st.warning("É necessário ter laudos salvos como 'Coleta 1 (Base)' e 'Coleta 2 (Monitoramento)' nesta combinação de filtros.")
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
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            with col_f1:
                faz_f = st.selectbox("Fazenda:", df_dados["Fazenda"].dropna().unique(), key="f_faz")
            with col_f2:
                prof_f = st.selectbox("Profundidade:", df_dados[df_dados["Fazenda"] == faz_f]["Profundidade"].dropna().unique(), key="f_prof")
            with col_f3:
                df_sub_f = df_dados[(df_dados["Fazenda"] == faz_f) & (df_dados["Profundidade"] == prof_f)]
                talhoes_f = ["Todos os Talhões"] + list(df_sub_f["Talhao"].dropna().unique())
                talhao_f_sel = st.selectbox("Talhão:", talhoes_f, key="f_talhao")
            with col_f4:
                tipo_f = st.selectbox("Tipo de Coleta:", df_sub_f["Tipo_Coleta"].dropna().unique(), key="f_tipo")

            df_laudo = df_sub_f[df_sub_f["Tipo_Coleta"] == tipo_f]
            if talhao_f_sel != "Todos os Talhões":
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

# --- ABA 3: UPLOAD / ENTRADA DE LAUDOS E GERENCIAMENTO DE ANÁLISES ---
with aba_upload:
    st.header("📤 Importar & Gerenciar Laudos de Laboratório")
    
    if df_clientes.empty:
        st.warning("Cadastre um cliente na aba 'Clientes' primeiro.")
    else:
        tab_imp, tab_geren = st.tabs(["📥 Importar Nova Planilha", "🗑️ Gerenciar / Excluir Laudos Registrados"])
        
        with tab_imp:
            col_u1, col_u2 = st.columns([1, 2])
            
            with col_u1:
                st.subheader("1. Informações do Laudo")
                up_cliente = st.selectbox("Cliente:", list(opcoes_clientes.keys()), key="up_cli_sel")
                up_fazenda = st.text_input("Nome da Fazenda / Gleba:", value="Fazenda Santa Maria")
                up_prof = st.text_input("Profundidade:", value="0-20")
                up_tipo = st.selectbox("Tipo de Coleta:", ["Coleta 1 (Base)", "Coleta 2 (Monitoramento)"])
                up_area = st.number_input("Área Total (ha):", value=100.0, step=10.0)
                up_grid = st.number_input("Grid Amostral (ha/ponto):", value=5.0, step=1.0)
                
                uploaded_file = st.file_uploader("Arquivo Excel (.xlsx)", type=["xlsx"])

            with col_u2:
                if uploaded_file is not None:
                    st.subheader("2. Mapeamento e Sanitização de Colunas")
                    df_preview = pd.read_excel(uploaded_file)
                    st.caption(f"Linhas detectadas: **{len(df_preview)}** | Colunas no arquivo: **{len(df_preview.columns)}**")
                    
                    st.write("Associe as colunas do seu arquivo Excel aos nomes padrão da Terra Nativa:")
                    
                    cols_excel = ["-- Ignorar --"] + list(df_preview.columns)
                    mapa_selecao = {}
                    
                    c_m1, c_m2 = st.columns(2)
                    for idx, col_padrao in enumerate(COLUNAS_PADRAO_NUTRIENTES):
                        # Tenta encontrar correspondência aproximada automática
                        match_idx = 0
                        for i_col, c_ex in enumerate(cols_excel):
                            if col_padrao.split()[0].lower() in c_ex.lower():
                                match_idx = i_col
                                break
                        
                        col_target = c_m1 if idx % 2 == 0 else c_m2
                        mapa_selecao[col_padrao] = col_target.selectbox(
                            f"Coluna para **{col_padrao}**:", 
                            cols_excel, 
                            index=match_idx, 
                            key=f"map_{col_padrao}"
                        )

                    st.markdown("---")
                    if st.button("💾 PROCESSAR E SALVAR LAUDO", type="primary"):
                        df_limpo = limpar_e_padronizar_df(df_preview, mapa_selecao)
                        salvar_analise(
                            opcoes_clientes[up_cliente], 
                            up_fazenda, 
                            up_prof, 
                            up_tipo, 
                            up_area, 
                            up_grid, 
                            df_limpo
                        )
                        st.success(f"Laudo gravado com sucesso para o cliente '{up_cliente}'!")
                        st.rerun()
                else:
                    st.info("Faça o upload do arquivo Excel ao lado para abrir a ferramenta de higienização e mapeamento de colunas.")

        with tab_geren:
            st.subheader("📋 Laudos Cadastrados no Banco de Dados")
            if cliente_id_ativo:
                df_registros = get_analises_cliente(cliente_id_ativo)
                if df_registros.empty:
                    st.info("Nenhum laudo encontrado para o cliente selecionado.")
                else:
                    resumo_laudos = df_registros[["analise_db_id", "Fazenda", "Profundidade", "Tipo_Coleta", "area_ha", "grid_amostral"]].drop_duplicates()
                    st.dataframe(resumo_laudos, use_container_width=True)
                    
                    laudo_to_del = st.selectbox("Selecione o ID do Laudo para Excluir:", resumo_laudos["analise_db_id"].unique())
                    if st.button("🗑️ Excluir Laudo Selecionado", type="primary"):
                        delete_analise(laudo_to_del)
                        st.success("Laudo excluído com sucesso!")
                        st.rerun()

# --- ABA 4: GERENCIAMENTO DE CLIENTES ---
with aba_cli:
    st.header("👤 Gerenciamento de Clientes")
    
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        st.subheader("➕ Adicionar Novo Cliente")
        novo_nome = st.text_input("Nome / Razão Social do Cliente:")
        if st.button("Cadastrar Cliente", type="primary") and novo_nome.strip():
            if add_cliente(novo_nome.strip()):
                st.success(f"Cliente '{novo_nome}' adicionado com sucesso!")
                st.rerun()
            else:
                st.error("Erro: Já existe um cliente cadastrado com este nome.")

    with col_c2:
        st.subheader("👥 Clientes Cadastrados")
        if not df_clientes.empty:
            st.dataframe(df_clientes, use_container_width=True)
            cli_to_del = st.selectbox("Excluir Cliente:", list(opcoes_clientes.keys()), key="del_cli")
            if st.button("Excluir Cliente e Todos os Seus Laudos"):
                delete_cliente(opcoes_clientes[cli_to_del])
                st.warning(f"Cliente '{cli_to_del}' removido.")
                st.rerun()
        else:
            st.info("Nenhum cliente cadastrado ainda.")
