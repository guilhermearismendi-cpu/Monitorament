import re
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configuração inicial da página Streamlit
st.set_page_config(
    page_title="Sistema Fertigrama & Monitoramento de Solo",
    page_icon="🌱",
    layout="wide",
)


# -----------------------------------------------------------------------------
# FUNÇÃO DE EXTRAÇÃO E LIMPEZA ESTRITA DE TALHÃO / PIVÔ
# -----------------------------------------------------------------------------
def extrair_talhao_limpo(texto):
  """Limpa e padroniza a identificação do talhão/pivô sem misturar pivôs.

  Exemplos de tratamento:
  - '1 - Fazenda_Suica_P01a_Pivo_1_Sede - 0-10' -> 'P01a Pivo 1 Sede'
  - '2 - Fazenda_Suica_P01c_Pivo_1 - 0-10'      -> 'P01c Pivo 1'
  - '3 - Fazenda_Suica_P01d_Pivo_1_Setorial'   -> 'P01d Pivo 1 Setorial'
  """
  if pd.isna(texto):
    return "Geral"
  s = str(texto).strip()

  # 1. Remove número do ponto/amostra no início (ex: "1 - ", "12 - ")
  s = re.sub(r"^\d+\s*-\s*", "", s)

  # 2. Remove profundidade no final (ex: "- 0-10 cm", "- 0 - 10", "- 10-20")
  s = re.sub(r"\s*-\s*\d+.*$", "", s)

  # 3. Remove prefixos da Fazenda
  s = re.sub(r"Fazenda_[A-Za-z0-9_]+?_", "", s, flags=re.IGNORECASE)
  s = re.sub(r"Fazenda\s+[A-Za-z0-9_]+\s*", "", s, flags=re.IGNORECASE)

  # 4. Formata underlines e espaços
  s = s.replace("_", " ").strip()
  s = re.sub(r"\s+", " ", s)

  return s if s else "Geral"


# -----------------------------------------------------------------------------
# CARREGAMENTO E PROCESSAMENTO INICIAL DOS DADOS
# -----------------------------------------------------------------------------
@st.cache_data
def carregar_dados(caminho_excel):
  try:
    df = pd.read_excel(caminho_excel)
  except Exception:
    return pd.DataFrame()

  col_ref = (
      "Descricao"
      if "Descricao" in df.columns
      else ("Identificacao" if "Identificacao" in df.columns else None)
  )

  if col_ref:
    df["Talhao_Limpo"] = df[col_ref].apply(extrair_talhao_limpo)
    df["Talhao"] = df["Talhao_Limpo"]
  else:
    df["Talhao_Limpo"] = "Geral"
    df["Talhao"] = "Geral"

  if "Fazenda" not in df.columns:
    df["Fazenda"] = "Fazenda Suíça"
  if "Profundidade" not in df.columns:
    df["Profundidade"] = "0 - 10 cm"
  if "Tipo_Coleta" not in df.columns:
    df["Tipo_Coleta"] = "Coleta 2 (Monitoramento)"

  return df


# -----------------------------------------------------------------------------
# INTERFACE DO USUÁRIO
# -----------------------------------------------------------------------------
st.title("🌱 Sistema Fertigrama & Monitoramento de Fertilidade")

# Barra Lateral - Upload ou Carregamento da Base
st.sidebar.header("📁 Fonte de Dados")
arquivo_uploaded = st.sidebar.file_uploader(
    "Enviar Planilha Excel (.xlsx)", type=["xlsx", "xls"]
)

if arquivo_uploaded:
  df_dados = carregar_dados(arquivo_uploaded)
else:
  try:
    df_dados = carregar_dados("Monitoramentos Cesar Milho 26.xlsx")
  except Exception:
    df_dados = pd.DataFrame()

# Navegação Superior
aba_selecionada = st.radio(
    "Navegação:",
    [
        "📈 Comparativo de Monitoramento",
        "📊 Diagnóstico Fertigrama",
        "📥 Entrar/Importar Laudo",
        "👤 Gerenciar Clientes & Laudos",
    ],
    horizontal=True,
)

st.markdown("---")

# -----------------------------------------------------------------------------
# ABA 1: COMPARATIVO DE MONITORAMENTO
# -----------------------------------------------------------------------------
if aba_selecionada == "📈 Comparativo de Monitoramento":
  st.header("📈 Comparação de Fertilidade (Talhão / Monitoramento)")

  if df_dados.empty:
    st.info(
        "Nenhum dado carregado. Por favor, envie uma planilha na barra"
        " lateral."
    )
  else:
    # 1. Filtros de Seleção
    col1, col2, col3, col4 = st.columns(4)

    with col1:
      fazendas = sorted(list(df_dados["Fazenda"].dropna().unique()))
      fazenda_sel = st.selectbox(
          "Fazenda / Gleba:", fazendas if fazendas else ["Fazenda Suíça"]
      )

    df_sub_faz = (
        df_dados[df_dados["Fazenda"] == fazenda_sel]
        if "Fazenda" in df_dados.columns
        else df_dados
    )

    with col2:
      profs = (
          sorted(list(df_sub_faz["Profundidade"].dropna().unique()))
          if "Profundidade" in df_sub_faz.columns
          else ["0 - 10 cm"]
      )
      prof_sel = st.selectbox("Profundidade:", profs)

    with col3:
      # Mantém cada pivô individual (P01a, P01c, P01d) estritamente separado
      talhoes_disp = sorted(list(df_sub_faz["Talhao_Limpo"].dropna().unique()))
      opcoes_talhao = ["Todos os Talhões / Pivôs"] + talhoes_disp
      talhao_sel = st.selectbox("Talhão / Pivô:", opcoes_talhao)

    with col4:
      cols_excluir = [
          "Descricao",
          "Identificacao",
          "Talhao",
          "Talhao_Limpo",
          "Fazenda",
          "Profundidade",
          "Tipo_Coleta",
          "Ponto",
      ]
      nutrientes = [
          c
          for c in df_sub_faz.columns
          if c not in cols_excluir
          and pd.api.types.is_numeric_dtype(df_sub_faz[c])
      ]
      nutriente_sel = st.selectbox(
          "Parâmetro/Nutriente:",
          nutrientes if nutrientes else ["P (mg.dm-3)"],
      )

    # 2. Filtragem de Dados com Regra Estrita
    df_filtrado = df_sub_faz.copy()
    if "Profundidade" in df_filtrado.columns:
      df_filtrado = df_filtrado[df_filtrado["Profundidade"] == prof_sel]

    if talhao_sel == "Todos os Talhões / Pivôs":
      df_c1 = df_filtrado[
          df_filtrado["Tipo_Coleta"].str.contains(
              "Coleta 1|Base", case=False, na=False
          )
      ].dropna(subset=[nutriente_sel])
      df_c2 = df_filtrado[
          df_filtrado["Tipo_Coleta"].str.contains(
              "Coleta 2|Monitoramento", case=False, na=False
          )
      ].dropna(subset=[nutriente_sel])
    else:
      # Busca o nome EXATO do pivô selecionado para garantir que pivôs diferentes não se misturem
      df_sub_t = df_filtrado[df_filtrado["Talhao_Limpo"] == talhao_sel]
      df_c1 = df_sub_t[
          df_sub_t["Tipo_Coleta"].str.contains(
              "Coleta 1|Base", case=False, na=False
          )
      ].dropna(subset=[nutriente_sel])
      df_c2 = df_sub_t[
          df_sub_t["Tipo_Coleta"].str.contains(
              "Coleta 2|Monitoramento", case=False, na=False
          )
      ].dropna(subset=[nutriente_sel])

    # 3. Validação e Apresentação dos Resultados
    if df_c1.empty or df_c2.empty:
      st.warning(
          "⚠️ É necessário ter laudos salvos em 'Coleta 1 (Base)' e 'Coleta 2"
          " (Monitoramento)' para comparar."
      )

      with st.expander("ℹ️ Detalhes da Validação de Laudos"):
        st.write(f"**Talhão/Pivô Selecionado:** `{talhao_sel}`")
        st.write(f"**Pontos na Coleta 1 (Base):** {len(df_c1)}")
        st.write(f"**Pontos na Coleta 2 (Monitoramento):** {len(df_c2)}")
        st.info(
            f"Para ver o comparativo direto do pivô **'{talhao_sel}'**, garanta"
            " que o laudo de amostragem na **Coleta 1 (Base)** está cadastrado"
            " exatamente com esse mesmo nome."
        )
    else:
        st.success(
            f"Exibindo comparação para **{talhao_sel}** —"
            f" **{nutriente_sel}**"
        )

        m1 = df_c1[nutriente_sel].mean()
        m2 = df_c2[nutriente_sel].mean()
        diff = m2 - m1
        pct = (diff / m1) * 100 if m1 != 0 else 0

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Média Coleta 1 (Base)", f"{m1:.2f}")
        col_m2.metric("Média Coleta 2 (Monitoramento)", f"{m2:.2f}")
        col_m3.metric("Variação Directa", f"{diff:+.2f}", f"{pct:+.1f}%")

        # Gráfico Boxplot
        fig = go.Figure()
        fig.add_trace(
            go.Box(
                y=df_c1[nutriente_sel],
                name="Coleta 1 (Base)",
                boxpoints="all",
                jitter=0.3,
            )
        )
        fig.add_trace(
            go.Box(
                y=df_c2[nutriente_sel],
                name="Coleta 2 (Monitoramento)",
                boxpoints="all",
                jitter=0.3,
            )
        )
        fig.update_layout(
            title=f"Distribuição de {nutriente_sel} — {talhao_sel}",
            yaxis_title=nutriente_sel,
            template="plotly_dark",
        )
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------------------
# DEMAIS ABAS
# -----------------------------------------------------------------------------
elif aba_selecionada == "📊 Diagnóstico Fertigrama":
  st.header("📊 Diagnóstico Fertigrama")
  st.info("Aba de análise de fertilidade e níveis críticos de nutrientes.")

elif aba_selecionada == "📥 Entrar/Importar Laudo":
  st.header("📥 Importação e Cadastro de Laudos")
  st.info("Área de entrada e upload de novos laudos.")

elif aba_selecionada == "👤 Gerenciar Clientes & Laudos":
  st.header("👤 Gerenciar Clientes & Laudos")
  st.info("Gerenciamento de amostras, edições e alinhamento de nomenclatura.")
