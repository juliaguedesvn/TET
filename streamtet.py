# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Título do app
st.title("Análise de Casos Confirmados de Tétano no Brasil")

# Carregar dados
@st.cache_data
def load_data():
    # Usar encoding latin1 para evitar UnicodeDecodeError
    df = pd.read_csv("tettot.csv", encoding="latin1")
    
    # Converter datas
    df["DT_INVEST"] = pd.to_datetime(df["DT_INVEST"], errors="coerce")
    df["DT_OBITO"] = pd.to_datetime(df["DT_OBITO"], errors="coerce")
    
    # Garantir ano como string para filtros
    df["NU_ANO"] = df["NU_ANO"].astype(str)
    
    return df

df = load_data()

# --- Filtros ---
anos = st.multiselect(
    "Selecione o(s) ano(s)", 
    options=df["NU_ANO"].unique(), 
    default=df["NU_ANO"].unique()
)
ufs = st.multiselect(
    "Selecione o(s) estado(s)", 
    options=df["SG_UF_NOT"].unique(), 
    default=df["SG_UF_NOT"].unique()
)

df_filtrado = df[(df["NU_ANO"].isin(anos)) & (df["SG_UF_NOT"].isin(ufs))]

st.subheader("Dados filtrados")
st.write(f"Total de registros: {len(df_filtrado)}")

# --- Pirâmide Etária ---
st.subheader("Pirâmide Etária dos Casos Confirmados")

piramide = df_filtrado.groupby(["IDADE", "CS_SEXO"]).size().unstack(fill_value=0)
piramide = piramide.rename(columns={"Masculino": "Homens", "Feminino": "Mulheres"})

if "Homens" in piramide.columns:
    piramide["Homens"] = -piramide["Homens"]

fig, ax = plt.subplots(figsize=(8,6))
if "Homens" in piramide.columns:
    ax.barh(piramide.index, piramide["Homens"], color="steelblue", label="Homens")
if "Mulheres" in piramide.columns:
    ax.barh(piramide.index, piramide["Mulheres"], color="salmon", label="Mulheres")

ax.set_xlabel("Número de casos")
ax.set_ylabel("Idade")
ax.set_title("Pirâmide etária dos casos confirmados de tétano")
ax.legend()
st.pyplot(fig)

# --- Série Temporal ---
st.subheader("Casos e Óbitos por Mês")

df_filtrado["MES_INVEST"] = df_filtrado["DT_INVEST"].dt.to_period("M")
df_filtrado["MES_OBITO"] = df_filtrado["DT_OBITO"].dt.to_period("M")

casos = df_filtrado.groupby("MES_INVEST").size()
obitos = df_filtrado.groupby("MES_OBITO").size()

serie = pd.DataFrame({"Casos": casos, "Óbitos": obitos}).fillna(0)

fig2, ax2 = plt.subplots(figsize=(10,6))
serie["Casos"].plot(ax=ax2, label="Casos", linewidth=2)
serie["Óbitos"].plot(ax=ax2, label="Óbitos", linewidth=2)

ax2.set_ylabel("Número de notificações")
ax2.set_xlabel("Mês")
ax2.set_title("Casos e óbitos confirmados de tétano por mês")
ax2.legend()
st.pyplot(fig2)
