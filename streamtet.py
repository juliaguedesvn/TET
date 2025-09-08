import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# Carregar dados
# -------------------------------
tettot = pd.read_csv("tettot.csv", encoding="latin1")

st.set_page_config(page_title="Observatório do Tétano", layout="wide")
st.title("🧪 Observatório do Tétano Acidental no Brasil")
st.markdown("Casos confirmados no SUS (2007–2023)")

# -------------------------------
# Filtros interativos
# -------------------------------
anos = sorted(tettot["NU_ANO"].unique())
ufs = sorted(tettot["SG_UF_NOT"].unique())
sexos = sorted(tettot["CS_SEXO"].unique())

filtro_ano = st.multiselect("Ano", anos, default=anos)
filtro_uf = st.multiselect("UF", ufs, default=ufs)
filtro_sexo = st.multiselect("Sexo", sexos, default=sexos)

# Aplicar filtros
df_filtrado = tettot[
    (tettot["NU_ANO"].isin(filtro_ano)) &
    (tettot["SG_UF_NOT"].isin(filtro_uf)) &
    (tettot["CS_SEXO"].isin(filtro_sexo))
]

# -------------------------------
# Abas principais
# -------------------------------
aba1, aba2, aba3, aba4 = st.tabs([
    "📊 Panorama Nacional",
    "👥 Perfil dos Casos",
    "💉 Infecção & Vacinação",
    "🏥 Clínico & Evolução"
])

# -------------------------------
# ABA 1 – Panorama Nacional
# -------------------------------
with aba1:
    st.subheader("Série temporal de casos confirmados")
    serie = df_filtrado.groupby("NU_ANO").size().reset_index(name="Casos")
    fig1 = px.line(serie, x="NU_ANO", y="Casos", markers=True)
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Distribuição geográfica (por UF)")
    casos_uf = df_filtrado.groupby("SG_UF_NOT").size().reset_index(name="Casos")
    fig2 = px.choropleth(
        casos_uf,
        geojson="https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson",
        locations="SG_UF_NOT",
        featureidkey="properties.sigla",
        color="Casos",
        color_continuous_scale="Reds",
        title="Casos confirmados por UF"
    )
    fig2.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Tabela resumo: Casos por ano e UF")
    resumo = df_filtrado.groupby(["NU_ANO", "SG_UF_NOT"]).size().reset_index(name="Casos")
    st.dataframe(resumo)

# -------------------------------
# ABA 2 – Perfil dos Casos
# -------------------------------
with aba2:
    def grafico_contagem(df, coluna, titulo):
        counts = df[coluna].value_counts().reset_index()
        counts.columns = [coluna, "Casos"]
        fig = px.bar(counts, x=coluna, y="Casos", title=titulo)
        st.plotly_chart(fig, use_container_width=True)

    grafico_contagem(df_filtrado, "CS_SEXO", "Distribuição por Sexo")
    fig_idade = px.histogram(df_filtrado, x="IDADE", nbins=20, labels={"IDADE":"Idade"}, title="Distribuição Etária")
    st.plotly_chart(fig_idade, use_container_width=True)
    grafico_contagem(df_filtrado, "CS_ESCOL_N", "Escolaridade")
    grafico_contagem(df_filtrado, "CS_RACA", "Raça/Cor")

# -------------------------------
# ABA 3 – Infecção e Vacinação
# -------------------------------
with aba3:
    grafico_contagem(df_filtrado, "TP_LOCALLE", "Local provável da infecção")
    
    dose_counts = df_filtrado["NU_DOSE"].value_counts().reset_index()
    dose_counts.columns = ["NU_DOSE", "Casos"]
    dose_counts = dose_counts.sort_values("NU_DOSE")
    fig_dose = px.bar(dose_counts, x="NU_DOSE", y="Casos", title="Número de doses recebidas")
    st.plotly_chart(fig_dose, use_container_width=True)
    
    grafico_contagem(df_filtrado, "TP_PROFILA", "Profilaxia pós-exposição")

# -------------------------------
# ABA 4 – Clínico & Evolução
# -------------------------------
with aba4:
    sintomas = ["CS_TRISMO", "CS_RISO", "CS_OPISTOT", "CS_NUCA",
                "CS_ABDOMIN", "CS_MEMBROS", "CS_CRISES"]
    freq = df_filtrado[sintomas].apply(lambda col: (col == "Sim").sum())
    freq_df = freq.reset_index()
    freq_df.columns = ["Sintoma", "Casos"]
    fig_sintomas = px.bar(freq_df, x="Sintoma", y="Casos", title="Sintomas mais frequentes")
    st.plotly_chart(fig_sintomas, use_container_width=True)

    grafico_contagem(df_filtrado, "EVOLUCAO", "Evolução dos casos")
    
    letalidade = (
        df_filtrado.groupby("NU_ANO")
        .apply(lambda x: (x["EVOLUCAO"] == "Óbito").mean() * 100)
        .reset_index(name="Letalidade")
    )
    fig_letalidade = px.line(letalidade, x="NU_ANO", y="Letalidade", markers=True, title="Taxa de letalidade (%) por ano")
    st.plotly_chart(fig_letalidade, use_container_width=True)
    
    obitos = df_filtrado[df_filtrado["EVOLUCAO"] == "Óbito"]
    st.subheader("Tabela de óbitos")
    st.dataframe(obitos[["NU_ANO", "SG_UF_NOT", "IDADE", "CS_SEXO", "DT_OBITO"]])
