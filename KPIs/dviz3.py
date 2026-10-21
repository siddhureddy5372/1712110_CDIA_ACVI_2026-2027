
import streamlit as st
import pandas as pd
import numpy as np
from keplergl import KeplerGl
from streamlit_keplergl import keplergl_static

# --------------------------------------------------
# 1. Configuração da aplicação
# --------------------------------------------------
st.set_page_config(
    page_title="iDashboard Regional",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ iDashboard — Desenvolvimento Regional")
st.caption(
    "Exploração territorial de indicadores socioeconómicos "
    "e equipamentos. Todos os dados são fictícios."
)

# --------------------------------------------------
# 2. Geração dos dados fictícios
# --------------------------------------------------
@st.cache_data
def gerar_dados():
    rng = np.random.default_rng(42)

    municipios = [
        ("Porto", 41.1579, -8.6291, "Norte"),
        ("Braga", 41.5454, -8.4265, "Norte"),
        ("Vila Real", 41.3006, -7.7441, "Norte"),
        ("Bragança", 41.8061, -6.7567, "Norte"),
        ("Guarda", 40.5373, -7.2676, "Centro"),
        ("Viseu", 40.6566, -7.9125, "Centro"),
        ("Coimbra", 40.2033, -8.4103, "Centro"),
        ("Aveiro", 40.6405, -8.6538, "Centro"),
        ("Castelo Branco", 39.8222, -7.4909, "Centro"),
        ("Leiria", 39.7436, -8.8071, "Centro"),
        ("Lisboa", 38.7223, -9.1393, "Lisboa e Vale do Tejo"),
        ("Santarém", 39.2369, -8.6860, "Lisboa e Vale do Tejo"),
        ("Setúbal", 38.5244, -8.8882, "Lisboa e Vale do Tejo"),
        ("Évora", 38.5714, -7.9135, "Alentejo"),
        ("Beja", 38.0151, -7.8632, "Alentejo"),
        ("Portalegre", 39.2967, -7.4285, "Alentejo"),
        ("Faro", 37.0194, -7.9304, "Algarve"),
        ("Lagos", 37.1028, -8.6730, "Algarve"),
        ("Funchal", 32.6669, -16.9241, "Madeira"),
        ("Ponta Delgada", 37.7412, -25.6756, "Açores"),
    ]

    linhas = []

    for nome, lat, lon, regiao in municipios:
        populacao = int(rng.integers(12000, 250000))
        desenvolvimento = round(float(rng.uniform(35, 90)), 1)
        emprego = round(float(rng.uniform(45, 80)), 1)

        linhas.append({
            "local": nome,
            "regiao": regiao,
            "tipo": "Município",
            "latitude": lat,
            "longitude": lon,
            "populacao": populacao,
            "indice_desenvolvimento": desenvolvimento,
            "taxa_emprego": emprego,
            "equipamento": "N/A",
            "dimensao": populacao
        })

        # Equipamentos fictícios em redor de cada município
        for _ in range(int(rng.integers(2, 6))):
            categoria = rng.choice(
                ["Escola", "Hospital", "Polo empresarial"]
            )

            linhas.append({
                "local": nome,
                "regiao": regiao,
                "tipo": "Equipamento",
                "latitude": lat + rng.normal(0, 0.025),
                "longitude": lon + rng.normal(0, 0.025),
                "populacao": np.nan,
                "indice_desenvolvimento": np.nan,
                "taxa_emprego": np.nan,
                "equipamento": categoria,
                "dimensao": int(rng.integers(1, 10))
            })

    return pd.DataFrame(linhas)


dados = gerar_dados()

# --------------------------------------------------
# 3. Filtros
# --------------------------------------------------
st.sidebar.header("Filtros territoriais")

regioes = sorted(dados["regiao"].unique())
regioes_escolhidas = st.sidebar.multiselect(
    "Regiões",
    options=regioes,
    default=regioes
)

tipos_escolhidos = st.sidebar.multiselect(
    "Elementos no mapa",
    options=["Município", "Equipamento"],
    default=["Município", "Equipamento"]
)

categorias = sorted(
    dados.loc[
        dados["tipo"] == "Equipamento", "equipamento"
    ].unique()
)

categorias_escolhidas = st.sidebar.multiselect(
    "Tipos de equipamento",
    options=categorias,
    default=categorias
)

indice_min, indice_max = st.sidebar.slider(
    "Intervalo do índice de desenvolvimento",
    min_value=0,
    max_value=100,
    value=(0, 100)
)

# --------------------------------------------------
# 4. Aplicação dos filtros
# --------------------------------------------------
filtrado = dados[
    dados["regiao"].isin(regioes_escolhidas)
    & dados["tipo"].isin(tipos_escolhidos)
].copy()

# Filtra categorias apenas nos equipamentos.
filtrado = filtrado[
    (filtrado["tipo"] == "Município")
    | (
        filtrado["equipamento"].isin(categorias_escolhidas)
    )
]

# O intervalo do índice aplica-se aos municípios.
filtrado = filtrado[
    (filtrado["tipo"] == "Equipamento")
    | (
        filtrado["indice_desenvolvimento"].between(
            indice_min, indice_max
        )
    )
]

municipios_filtrados = filtrado[
    filtrado["tipo"] == "Município"
]

equipamentos_filtrados = filtrado[
    filtrado["tipo"] == "Equipamento"
]

# --------------------------------------------------
# 5. Indicadores principais
# --------------------------------------------------
st.subheader("Indicadores territoriais")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Municípios selecionados",
    len(municipios_filtrados)
)

k2.metric(
    "População representada",
    f"{municipios_filtrados['populacao'].sum():,.0f}".replace(",", " ")
)

if len(municipios_filtrados):
    indice_medio = municipios_filtrados[
        "indice_desenvolvimento"
    ].mean()
    emprego_medio = municipios_filtrados[
        "taxa_emprego"
    ].mean()
else:
    indice_medio = np.nan
    emprego_medio = np.nan

k3.metric(
    "Índice médio de desenvolvimento",
    f"{indice_medio:.1f}/100" if pd.notna(indice_medio) else "—"
)

k4.metric(
    "Taxa média de emprego",
    f"{emprego_medio:.1f}%" if pd.notna(emprego_medio) else "—"
)

st.divider()

# --------------------------------------------------
# 6. Mapa Kepler.gl
# --------------------------------------------------
st.subheader("Exploração geográfica")
st.write(
    "Utiliza o painel de camadas do mapa para configurar "
    "a visualização. Podes aproximar, afastar, selecionar "
    "pontos e experimentar diferentes representações."
)

if filtrado.empty:
    st.warning("Não existem dados para os filtros selecionados.")
else:
    dados_mapa = filtrado[
        [
            "local", "regiao", "tipo",
            "latitude", "longitude", "populacao",
            "indice_desenvolvimento", "taxa_emprego",
            "equipamento", "dimensao"
        ]
    ].copy()

    mapa = KeplerGl(
        height=680,
        data={"Indicadores regionais": dados_mapa}
    )

    keplergl_static(
        mapa,
        height=680,
        center_map=True
    )

# --------------------------------------------------
# 7. Tabela de dados
# --------------------------------------------------
with st.expander("Consultar os dados filtrados"):
    st.dataframe(
        filtrado,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Descarregar CSV",
        data=filtrado.to_csv(index=False).encode("utf-8-sig"),
        file_name="dados_regionais_filtrados.csv",
        mime="text/csv"
    )

st.caption(
    "Demonstração académica. Indicadores e localizações "
    "gerados artificialmente; não utilizar para decisões reais."
)
