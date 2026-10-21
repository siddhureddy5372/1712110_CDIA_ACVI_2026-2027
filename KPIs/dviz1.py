import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.title("Desempenho do projeto")

valor = st.slider("Desempenho (%)", 0, 100, 78)

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=valor,
    gauge={
        "shape": "angular",
        "axis": {"range": [0, 100]},
        "steps": [
            {"range": [0, 40], "color": "#DC6262"},
            {"range": [40, 70], "color": "#E9B949"},
            {"range": [70, 100], "color": "#45A675"}
        ],
        "bar": {"color": "rgba(0,0,0,0)"},
        "bgcolor": "white"
    },
    title={"text": "Desempenho do projeto"}
))

# Desenhar a agulha manualmente
theta = np.pi * (1 - valor / 100)
cx, cy = 0.5, 0.18
r = 0.34
x = cx + r * np.cos(theta)
y = cy + r * np.sin(theta)

fig.add_shape(
    type="line",
    xref="paper", yref="paper",
    x0=cx, y0=cy, x1=x, y1=y,
    line=dict(color="#263957", width=5)
)

fig.add_shape(
    type="circle",
    xref="paper", yref="paper",
    x0=cx-0.015, y0=cy-0.015,
    x1=cx+0.015, y1=cy+0.015,
    fillcolor="#263957",
    line=dict(color="#263957")
)

fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)