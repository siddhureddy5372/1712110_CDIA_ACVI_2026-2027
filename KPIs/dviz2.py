
import streamlit as st
import plotly.graph_objects as go
from streamlit_sortables import sort_items

st.set_page_config(
    page_title="Simulador de Governo",
    page_icon="🏛️",
    layout="wide"
)

st.title("🏛️ Dashboard — Viabilidade Parlamentar")
st.write(
    "Simulador de cenários para avaliar a viabilidade "
    "parlamentar da aprovação de um programa de governo."
)

# Dados fictícios: nome -> número de deputados
partidos = {
    "Partido A (85)": 85,
    "Partido B (60)": 60,
    "Partido C (40)": 40,
    "Partido D (25)": 25,
    "Partido E (20)": 20,
    "Partido F (2)": 2
}

total_deputados = sum(partidos.values())

maioria = st.sidebar.number_input(
    "Limiar de aprovação (votos favoráveis)",
    min_value=1,
    max_value=total_deputados,
    value=116
)

# Inicializar as duas áreas
if "areas" not in st.session_state:
    st.session_state.areas = [
        {
            "header": "Partidos disponíveis",
            "items": list(partidos.keys())
        },
        {
            "header": "Coligação do governo",
            "items": []
        }
    ]

st.subheader("1. Construir a coligação")

st.write("Arrasta os partidos para a área da coligação.")

areas = sort_items(
    st.session_state.areas,
    multi_containers=True,
    key="coligacao"
)

st.session_state.areas = areas

# Identificar os partidos selecionados
coligacao = next(
    (
        a["items"] for a in areas
        if a["header"] == "Coligação do governo"
    ),
    []
)

# Calcular os indicadores com base nos deputados
deputados_coligacao = sum(
    partidos[p] for p in coligacao if p in partidos
)

# Hipótese explícita: todos os deputados selecionados votam a favor
votos_favoraveis = deputados_coligacao

margem = votos_favoraveis - maioria
percentagem = 100 * votos_favoraveis / total_deputados

# KPI 1: viabilidade parlamentar
viavel = votos_favoraveis >= maioria

if viavel:
    viabilidade = "Viável"
    explicacao = (
        "O cenário atinge ou ultrapassa o limiar "
        "de votos definido."
    )
else:
    viabilidade = "Insuficiente"
    explicacao = (
        f"Faltam {maioria - votos_favoraveis} votos "
        "para atingir o limiar definido."
    )

# --------------------------------------------------
# KPIs
# --------------------------------------------------

st.divider()
st.subheader("2. Indicadores-chave de desempenho (KPIs)")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "KPI 1 — Viabilidade de aprovação",
    viabilidade
)

k2.metric(
    "KPI 2 — Votos favoráveis previstos",
    votos_favoraveis
)

k3.metric(
    "KPI 3 — Margem de aprovação",
    f"{margem:+d} votos"
)

k4.metric(
    "KPI 4 — Estabilidade da coligação",
    "N/D"
)

st.caption(
    "N/D = não disponível. Não foram fornecidos dados "
    "que permitam estimar a estabilidade política da coligação."
)

if viavel:
    st.success(explicacao)
else:
    st.warning(explicacao)

st.info(
    "Pressuposto do modelo: todos os deputados dos partidos "
    "selecionados votam a favor do programa. Os votos previstos "
    "são, portanto, uma estimativa condicional, não uma previsão "
    "do comportamento real dos deputados."
)

# --------------------------------------------------
# Gráfico de composição da coligação
# --------------------------------------------------

st.divider()
st.subheader("3. Composição da coligação")

fig = go.Figure()

for partido in coligacao:
    if partido in partidos:
        fig.add_trace(go.Bar(
            x=[partidos[partido]],
            y=["Coligação"],
            name=partido,
            orientation="h"
        ))

fig.update_layout(
    barmode="stack",
    title="Deputados por partido na coligação",
    xaxis_title="Número de deputados",
    height=350
)

fig.add_vline(
    x=maioria,
    line_dash="dash",
    line_color="red",
    annotation_text=f"Limiar: {maioria}"
)

st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# Repor o simulador
# --------------------------------------------------

if st.button("Repor partidos"):
    st.session_state.pop("areas", None)
    st.rerun()
