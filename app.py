from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import norm
import streamlit as st

from diretrizes import (
    obter_classificacao,
    obter_faixas_zscore,
    fatores_risco_anemia,
    fatores_risco_hipovitaminose_d,
    fatores_risco_vitamina_b12,
    classificar_peso_ig,
    obter_sais_ferro,
    recomendacao_ferro,
    calcular_apresentacao_ferro,
    modelo_prescricao_ferro,
    recomendacao_vitaminas,
    obter_orientacoes_detalhadas,
    obter_marcos_vigilancia,
    classificar_desenvolvimento,
    obter_calendario_vacinal,
    status_vacina,
    eventos_adversos_vacinas,
    obter_matriz_caderneta_vacinas,
)

st.set_page_config(page_title="Puericultura Digital", page_icon="👶", layout="wide", initial_sidebar_state="collapsed")


@st.cache_data(show_spinner=False)
def carregar_tabelas():
    def carregar_e_limpar(nome_arquivo: str):
        try:
            df = pd.read_csv(nome_arquivo, sep=",", decimal=".", encoding="utf-8-sig")
            if len(df.columns) < 5:
                raise ValueError
        except Exception:
            df = pd.read_csv(nome_arquivo, sep=";", decimal=",", encoding="utf-8-sig")
        df.columns = df.columns.str.strip().str.replace("\ufeff", "", regex=False)
        df.rename(columns={df.columns[0]: "Day"}, inplace=True)
        df = df.apply(pd.to_numeric, errors="coerce").dropna(subset=["Day"])
        df["Day"] = df["Day"].astype(int)
        if "SD4" not in df.columns and {"SD2", "SD3"}.issubset(df.columns):
            df["SD4"] = df["SD3"] + (df["SD3"] - df["SD2"])
        if "SD4neg" not in df.columns and {"SD2neg", "SD3neg"}.issubset(df.columns):
            df["SD4neg"] = df["SD3neg"] - (df["SD2neg"] - df["SD3neg"])
        return df
    try:
        return {
            "Masculino": {
                "Peso": carregar_e_limpar("WFA_boys_z_exp.csv"),
                "Estatura": carregar_e_limpar("LFA_boys_z_exp.csv"),
                "IMC": carregar_e_limpar("BFA_boys_z_exp.csv"),
                "PC": carregar_e_limpar("HCFA_boys_z_exp.csv"),
            },
            "Feminino": {
                "Peso": carregar_e_limpar("WFA_girls_z_exp.csv"),
                "Estatura": carregar_e_limpar("LFA_girls_z_exp.csv"),
                "IMC": carregar_e_limpar("BFA_girls_z_exp.csv"),
                "PC": carregar_e_limpar("HCFA_girls_z_exp.csv"),
            },
        }
    except Exception as exc:
        st.error(f"Não consegui carregar as tabelas OMS. Verifique os CSVs no repositório. Detalhe: {exc}")
        return None


def idade_extenso(idade_dias: int):
    anos = int(idade_dias // 365.25)
    meses = int((idade_dias % 365.25) // 30.4375)
    dias = int((idade_dias % 365.25) % 30.4375)
    return anos, meses, dias


def col_z(z: int) -> str:
    if z == 0:
        return "SD0"
    return f"SD{z}" if z > 0 else f"SD{abs(z)}neg"


def calcular_z_lms(valor: float, linha: pd.Series) -> float:
    if linha["L"] != 0:
        return (((valor / linha["M"]) ** linha["L"]) - 1) / (linha["L"] * linha["S"])
    return np.log(valor / linha["M"]) / linha["S"]


def faixa_x_por_idade(meses: float):
    if meses <= 24:
        return "0 a 2 anos", [0, 24]
    if meses <= 60:
        return "2 a 5 anos", [24, 60]
    return "5 a 10 anos", [60, 120]


def limite_y_caderneta(parametro: str, faixa: str, df: pd.DataFrame, valor: float):
    limites = {
        ("Peso", "0 a 2 anos"): (0, 18), ("Peso", "2 a 5 anos"): (7, 32), ("Peso", "5 a 10 anos"): (10, 65),
        ("Estatura", "0 a 2 anos"): (40, 105), ("Estatura", "2 a 5 anos"): (75, 125), ("Estatura", "5 a 10 anos"): (95, 165),
        ("IMC", "0 a 2 anos"): (10, 24), ("IMC", "2 a 5 anos"): (10, 22), ("IMC", "5 a 10 anos"): (10, 28),
        ("PC", "0 a 2 anos"): (30, 55),
    }
    ymin, ymax = limites.get((parametro, faixa), (float(df[["SD3neg", "SD3"]].min().min()), float(df[["SD3neg", "SD3"]].max().max())))
    ymin = min(ymin, valor - max(abs(valor) * 0.08, 1))
    ymax = max(ymax, valor + max(abs(valor) * 0.08, 1))
    return [round(ymin, 1), round(ymax, 1)]


def adicionar_sombreamento(fig, df_plot, parametro, x):
    for f in obter_faixas_zscore(parametro):
        c1, c2 = col_z(f["z_min"]), col_z(f["z_max"])
        if c1 not in df_plot.columns or c2 not in df_plot.columns:
            continue
        fig.add_trace(go.Scatter(x=x, y=df_plot[c1], mode="lines", line=dict(width=0), hoverinfo="skip", showlegend=False))
        fig.add_trace(go.Scatter(x=x, y=df_plot[c2], mode="lines", line=dict(width=0), fill="tonexty", fillcolor=f["cor_fill"], name=f"{f['rotulo']} ({f['intervalo']})", hoverinfo="skip"))


def adicionar_curvas(fig, df_plot, x):
    curvas = [
        ("SD3neg", "-3Z", "#9f1239", 1.6, "dash"), ("SD2neg", "-2Z", "#ea580c", 2.0, "solid"),
        ("SD1neg", "-1Z", "#94a3b8", 1.1, "dot"), ("SD0", "Mediana", "#15803d", 3.0, "solid"),
        ("SD1", "+1Z", "#94a3b8", 1.1, "dot"), ("SD2", "+2Z", "#ea580c", 2.0, "solid"),
        ("SD3", "+3Z", "#9f1239", 1.6, "dash"),
    ]
    for col, nome, cor, largura, dash in curvas:
        if col in df_plot.columns:
            fig.add_trace(go.Scatter(x=x, y=df_plot[col], mode="lines", line=dict(color=cor, width=largura, dash=dash), name=nome, hovertemplate=f"{nome}: %{{y:.2f}}<extra></extra>"))


def adicionar_grade_caderneta(fig, rx):
    for m in range(int(rx[0]), int(rx[1]) + 1):
        if m % 12 == 0:
            fig.add_vline(x=m, line_width=1.7, line_color="rgba(15,23,42,.46)")
            if m > 0:
                fig.add_annotation(x=m, y=1.01, yref="paper", text=f"{m//12}a", showarrow=False, font=dict(size=11, color="#334155"))


def plotar_crescimento(df, parametro, titulo, unidade, valor, idade_dias, idade_meses, faixa, rx):
    max_day = int(min(max(idade_dias, rx[0] * 30.4375), df["Day"].max()))
    linha = df.iloc[(df["Day"] - max_day).abs().argsort()[:1]].iloc[0]
    z = calcular_z_lms(valor, linha)
    cls, crit, cor = obter_classificacao(z, parametro)
    pct = norm.cdf(z) * 100

    df_plot = df[(df["Day"] / 30.4375 >= rx[0]) & (df["Day"] / 30.4375 <= rx[1])].copy()
    x = df_plot["Day"] / 30.4375

    st.markdown(f"""
    <div class='result-card' style='--result-color:{cor};'>
      <div><span class='result-label'>{titulo}</span><h3>{cls}</h3></div>
      <div class='result-metrics'>Z = <b>{z:.2f}</b> · Percentil ≈ <b>P{pct:.0f}</b><br><small>{crit}</small></div>
    </div>
    """, unsafe_allow_html=True)

    fig = go.Figure()
    adicionar_sombreamento(fig, df_plot, parametro, x)
    adicionar_curvas(fig, df_plot, x)
    adicionar_grade_caderneta(fig, rx)
    fig.add_trace(go.Scatter(
        x=[idade_meses], y=[valor], mode="markers+text", name="Paciente",
        marker=dict(size=16, color="#0f172a", line=dict(color="white", width=2)),
        text=[f"{valor:g} {unidade}"], textposition="top center",
        hovertemplate=f"Paciente<br>Idade: %{{x:.1f}} meses<br>{titulo}: %{{y:.2f}} {unidade}<br>Z: {z:.2f}<extra></extra>",
    ))
    fig.update_layout(
        height=620, template="plotly_white", margin=dict(l=30, r=20, t=30, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=-0.28, xanchor="left", x=0),
        xaxis=dict(title="Idade (meses)", range=rx, dtick=1, showgrid=True, gridcolor="rgba(148,163,184,.22)", zeroline=False),
        yaxis=dict(title=f"{titulo} ({unidade})", range=limite_y_caderneta(parametro, faixa, df_plot, valor), showgrid=True, gridcolor="rgba(148,163,184,.30)", zeroline=False),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "toImageButtonOptions": {"format": "png", "filename": f"{parametro.lower()}_puericultura"}, "modeBarButtonsToAdd": ["drawline", "eraseshape"]})


def css(sexo: str):
    accent = "#0f766e" if sexo == "Masculino" else "#7e22ce"
    return f"""
    <style>
    :root {{ --accent:{accent}; --card:rgba(255,255,255,.90); --border:rgba(100,116,139,.25); --text:#0f172a; --muted:#475569; --chip:color-mix(in srgb, var(--accent) 12%, white); --shadow:0 14px 34px rgba(15,23,42,.08); }}
    html[data-theme="dark"], [data-testid="stAppViewContainer"] {{ color: var(--text); }}
    @media (prefers-color-scheme: dark) {{
      :root {{ --card:rgba(15,23,42,.84); --border:rgba(148,163,184,.28); --text:#e2e8f0; --muted:#cbd5e1; --chip:rgba(30,41,59,.88); --shadow:0 16px 34px rgba(0,0,0,.28); }}
      .stApp {{ background: linear-gradient(135deg,#020617,#111827 55%,#1e293b)!important; color:var(--text); }}
      .soft-card,.top-panel,.vax-card,.dev-card,.result-card,.risk-box,.caderneta-wrap,.timeline-card {{ color:var(--text); }}
      .vax-table-mini td .field {{ color:#e5e7eb!important; }}
    }}
    .stApp {{ background: linear-gradient(135deg, color-mix(in srgb, var(--accent) 10%, white), #f8fafc 48%, #ffffff); }}
    .block-container {{ padding-top: 1rem; max-width: 1500px; }}
    h1,h2,h3 {{ color: var(--accent)!important; }}
    .hero {{ padding: 1.2rem 1.4rem; border-radius: 24px; background: var(--card); border:1px solid var(--border); box-shadow:var(--shadow); margin-bottom: 1rem; }}
    .hero h1 {{ margin:0; font-size: clamp(1.55rem, 2.5vw, 2.4rem); }}
    .hero p {{ color:var(--muted); margin:.25rem 0 0 0; }}
    .top-panel {{ position: sticky; top: .35rem; z-index: 999; padding: .9rem 1rem; border-radius: 22px; background: var(--card); border:1px solid var(--border); box-shadow:var(--shadow); backdrop-filter: blur(12px); margin-bottom: 1rem; }}
    .metric-pill {{ display:inline-block; padding:.50rem .75rem; border-radius:999px; background:var(--chip); color:var(--accent); font-weight:800; margin:.15rem .25rem .15rem 0; border:1px solid var(--border); }}
    .result-card {{ display:flex; justify-content:space-between; gap:1rem; align-items:center; padding:1rem 1.1rem; border-radius:22px; color:white; background:linear-gradient(135deg,var(--result-color), color-mix(in srgb, var(--result-color) 70%, black)); box-shadow:var(--shadow); margin:.5rem 0 1rem; }}
    .result-card h3 {{ color:white!important; margin:.2rem 0 0 0; }}
    .result-label {{ opacity:.9; font-size:.86rem; text-transform:uppercase; letter-spacing:.04em; }}
    .result-metrics {{ text-align:right; font-size:1.02rem; }}
    .soft-card,.vax-card,.dev-card,.risk-box,.caderneta-wrap,.timeline-card {{ background:var(--card); border:1px solid var(--border); border-radius:22px; padding:1rem; box-shadow:var(--shadow); margin-bottom:1rem; }}
    .soft-title {{ font-weight:900; color:var(--accent); margin-bottom:.55rem; font-size:1.05rem; }}
    .soft-card li {{ margin:.25rem 0; }}
    .risk-box {{ border-left:6px solid var(--accent); }}
    .vax-grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap:1rem; }}
    .vax-head {{ display:flex; justify-content:space-between; gap:.5rem; align-items:center; margin-bottom:.6rem; }}
    .badge {{ display:inline-block; padding:.28rem .55rem; border-radius:999px; color:white; font-weight:800; font-size:.78rem; }}
    .vax-line {{ border-top:1px solid var(--border); padding:.6rem 0; }}
    .vax-name {{ font-weight:900; color:var(--accent); }}
    .small-muted {{ color:var(--muted); font-size:.9rem; }}
    .timeline {{ display:flex; gap:.7rem; overflow-x:auto; padding:.4rem 0 1rem; }}
    .timeline-card {{ min-width:230px; position:relative; }}
    .timeline-card.current {{ border:2px solid var(--accent); transform:translateY(-2px); }}
    .timeline-dot {{ width:16px; height:16px; border-radius:50%; background:var(--accent); display:inline-block; margin-right:.4rem; }}
    .dev-instruction {{ background:color-mix(in srgb, var(--accent) 8%, transparent); border:1px dashed var(--accent); padding:.9rem; border-radius:18px; margin:.7rem 0; }}
    .caderneta-wrap {{ overflow-x:auto; }}
    .vax-table-mini {{ border-collapse:collapse; min-width:1050px; width:100%; font-size:.78rem; }}
    .vax-table-mini th,.vax-table-mini td {{ border:1px solid #334155; padding:.35rem; vertical-align:top; color:#111827; }}
    .vax-table-mini th {{ color:#1e1b4b; text-align:center; font-weight:900; }}
    .vax-table-mini .field {{ display:block; font-style:italic; line-height:1.4; color:#111827; margin-top:.25rem; }}
    .prescricao {{ white-space:pre-wrap; background:rgba(15,23,42,.06); border:1px dashed var(--border); padding:1rem; border-radius:16px; color:var(--text); }}
    @media (max-width: 760px) {{
      .result-card {{ flex-direction:column; align-items:flex-start; }} .result-metrics {{ text-align:left; }}
      .top-panel {{ top:.1rem; border-radius:18px; }}
      .metric-pill {{ font-size:.82rem; padding:.42rem .55rem; }}
      .hero {{ padding:1rem; }}
    }}
    </style>
    """


def html_lista(itens):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in itens) + "</ul>"


def render_caderneta_vacinas():
    for bloco in obter_matriz_caderneta_vacinas():
        rows = []
        for linha in bloco["linhas"]:
            cells = []
            for nome, dose, cor in linha:
                if nome:
                    cells.append(f"<td style='background:{cor};'><b>{nome}</b><br><b>{dose}</b><span class='field'>Data: ____/____/______<br>Lote:<br>Lab./Produt:<br>Unidade:<br>Ass.:</span></td>")
                else:
                    cells.append(f"<td style='background:{cor}; text-align:center; font-weight:800;'>{dose}</td>")
            rows.append("<tr>" + "".join(cells) + "</tr>")
        html = f"""
        <div class='caderneta-wrap'>
        <h3 style='margin:.2rem 0 .7rem;'>Registro da Aplicação das Vacinas do Calendário Nacional — {bloco['grupo']}</h3>
        <table class='vax-table-mini'>
        <tr><th colspan='7' style='text-align:left;background:#fff;'>NOME: ________________________________ &nbsp;&nbsp;&nbsp; Data de nascimento: ____/____/______</th></tr>
        {''.join(rows)}
        </table></div>
        """
        st.markdown(html, unsafe_allow_html=True)


def render_imagem_ferro(src: str):
    if not src:
        st.info("Imagem da apresentação não configurada.")
        return
    try:
        if src.startswith("http"):
            st.image(src, caption="Imagem ilustrativa da apresentação comercial. Conferir sempre bula/rótulo.", use_container_width=True)
        else:
            p = Path(src)
            if p.exists():
                st.image(str(p), caption="Imagem ilustrativa da apresentação comercial. Conferir sempre bula/rótulo.", use_container_width=True)
            else:
                st.info("Imagem comercial não encontrada no repositório. Você pode adicionar o arquivo em `assets/ferro/` mantendo o nome previsto no dicionário.")
    except Exception:
        st.info("Não foi possível carregar a imagem desta apresentação. O cálculo e a prescrição permanecem disponíveis.")


tabelas_oms = carregar_tabelas()

# Entradas superiores
st.markdown("<div class='hero'><h1>👶 Puericultura Digital</h1><p>Análise clínica por idade, sexo, crescimento, desenvolvimento, imunizações, suplementação e orientações.</p></div>", unsafe_allow_html=True)

with st.expander("🧾 Dados da criança e da consulta", expanded=True):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        sexo = st.selectbox("Sexo", ["Masculino", "Feminino"])
        data_nasc = st.date_input("Data de nascimento", value=date(2023, 1, 1), format="DD/MM/YYYY")
    with c2:
        data_aval = st.date_input("Data da consulta", value=date.today(), format="DD/MM/YYYY")
        aleitamento_exclusivo = st.checkbox("Aleitamento materno exclusivo?", value=True)
    with c3:
        peso_nasc_g = st.number_input("Peso ao nascer (g)", min_value=300, max_value=6500, value=3200, step=10)
        idade_gest_sem = st.number_input("Idade gestacional ao nascer (semanas)", min_value=22.0, max_value=42.0, value=39.0, step=0.1, format="%.1f")
    with c4:
        prematuro = idade_gest_sem < 37
        st.toggle("Pré-termo?", value=prematuro, disabled=True, help="Calculado automaticamente pela idade gestacional ao nascer < 37 semanas.")
        st.caption("A idade corrigida é usada para vigilância quando pré-termo.")

    m1, m2, m3 = st.columns(3)
    with m1:
        peso = st.number_input("Peso atual (kg)", 0.5, 100.0, 10.0, step=0.1)
    with m2:
        estatura = st.number_input("Comprimento/estatura atual (cm)", 30.0, 170.0, 80.0, step=0.5)
    with m3:
        pc = st.number_input("Perímetro cefálico atual (cm)", 20.0, 70.0, 45.0, step=0.1)

idade_dias_cron = max(0, (data_aval - data_nasc).days)
correcao_dias = max(0, int(round((40 - idade_gest_sem) * 7))) if prematuro else 0
idade_dias = max(0, idade_dias_cron - correcao_dias)
idade_meses_float = idade_dias / 30.4375
idade_meses_cron = idade_dias_cron / 30.4375
anos, meses, dias = idade_extenso(idade_dias_cron)
anos_c, meses_c, dias_c = idade_extenso(idade_dias)
class_nasc, riscos_nasc = classificar_peso_ig(peso_nasc_g, idade_gest_sem)
imc = peso / ((estatura / 100) ** 2)

st.markdown(css(sexo), unsafe_allow_html=True)

# Cabeçalho flutuante de resumo
st.markdown(f"""
<div class='top-panel'>
  <b>Resumo fixo da criança</b><br>
  <span class='metric-pill'>Sexo: {sexo}</span>
  <span class='metric-pill'>Nascimento: {data_nasc.strftime('%d/%m/%Y')}</span>
  <span class='metric-pill'>Consulta: {data_aval.strftime('%d/%m/%Y')}</span>
  <span class='metric-pill'>Idade cronológica: {anos}a {meses}m {dias}d</span>
  <span class='metric-pill'>Idade corrigida: {anos_c}a {meses_c}m {dias_c}d</span>
  <span class='metric-pill'>IG ao nascer: {idade_gest_sem:.1f}s</span>
  <span class='metric-pill'>PN: {peso_nasc_g:.0f}g · {class_nasc}</span>
  <span class='metric-pill'>Atual: {peso:.1f}kg · {estatura:.1f}cm · PC {pc:.1f}cm · IMC {imc:.1f}</span>
</div>
""", unsafe_allow_html=True)

if tabelas_oms is None:
    st.stop()

if prematuro:
    st.warning("Área reservada para pré-termo: este app já calcula idade corrigida, risco para suplementação e orientação diferenciada. Para curvas específicas de prematuros, adicione os CSVs de Intergrowth/Fenton e conecte na função `carregar_tabelas()`.")

faixa, rx = faixa_x_por_idade(idade_meses_float)

tabs = st.tabs(["📈 Crescimento", "🧠 Desenvolvimento", "💉 Imunizações", "💊 Ferro e vitaminas", "📝 Orientações"])

with tabs[0]:
    st.subheader("📈 Crescimento antropométrico")
    st.caption("As curvas preservam zoom, seleção e download de imagem do Plotly. As linhas mensais são claras e os marcos anuais aparecem mais escuros.")
    stabs = st.tabs(["⚖️ Peso", "📏 Estatura", "🧮 IMC", "🧠 PC"])
    cfg = [
        ("Peso", "Peso/idade", "kg", peso, faixa, rx),
        ("Estatura", "Comprimento/estatura por idade", "cm", estatura, faixa, rx),
        ("IMC", "IMC/idade", "kg/m²", imc, faixa, rx),
        ("PC", "Perímetro cefálico/idade", "cm", pc, "0 a 2 anos", [0, 24]),
    ]
    for tab, (param, titulo, unidade, valor, fx, r_x) in zip(stabs, cfg):
        with tab:
            if param == "PC" and idade_meses_float > 24:
                st.info("O gráfico de perímetro cefálico está reservado para 0–2 anos, conforme uso rotineiro da caderneta.")
                continue
            df = tabelas_oms[sexo][param]
            plotar_crescimento(df, param, titulo, unidade, valor, idade_dias, idade_meses_float, fx, r_x)

with tabs[1]:
    st.subheader("🧠 Desenvolvimento neuropsicomotor")
    atual, anterior, proxima, todas = obter_marcos_vigilancia(idade_meses_float, prematuro)
    st.markdown("<div class='timeline'>" + "".join(
        f"<div class='timeline-card {'current' if f['faixa']==atual['faixa'] else ''}'><span class='timeline-dot'></span><b>{f['faixa']}</b><br><span class='small-muted'>{'faixa atual' if f['faixa']==atual['faixa'] else 'vigilância'}</span></div>" for f in todas
    ) + "</div>", unsafe_allow_html=True)

    if anterior:
        st.markdown(f"<div class='dev-instruction'><b>1) Confirmar marcos imediatamente anteriores: {anterior['faixa']}</b><br>{anterior['avaliacao']}</div>", unsafe_allow_html=True)
        status_anterior = []
        for area, marco in anterior["marcos"]:
            cols = st.columns([1.2, 3, 2])
            cols[0].markdown(f"**{area}**")
            cols[1].write(marco)
            status_anterior.append(cols[2].radio("Status", ["Presente", "Ausente", "Não verificado"], horizontal=True, key=f"ant_{area}_{marco}", label_visibility="collapsed"))
    else:
        status_anterior = []

    st.markdown(f"<div class='dev-instruction'><b>2) Avaliar marcos esperados para a idade atual: {atual['faixa']}</b><br>{atual['avaliacao']}</div>", unsafe_allow_html=True)
    status_atual = []
    for area, marco in atual["marcos"]:
        cols = st.columns([1.2, 3, 2])
        cols[0].markdown(f"**{area}**")
        cols[1].write(marco)
        status_atual.append(cols[2].radio("Status", ["Presente", "Ausente", "Não verificado"], horizontal=True, key=f"atu_{area}_{marco}", label_visibility="collapsed"))

    fatores_dev = []
    with st.expander("Fatores de risco para desenvolvimento/seguimento diferenciado"):
        opcoes_dev = ["Prematuridade", "Baixo peso ao nascer", "PIG suspeito", "Internação neonatal prolongada", "Asfixia/hipóxia", "Infecção congênita", "Microcefalia/macrocefalia", "Alteração auditiva/visual", "Vulnerabilidade social", "Suspeita de TEA ou regressão de habilidades"]
        fatores_dev = st.multiselect("Selecione fatores presentes", opcoes_dev, default=[r.replace("pré-termo", "Prematuridade") for r in riscos_nasc if r == "pré-termo"])

    clas_dev, texto_dev, cor_dev = classificar_desenvolvimento(status_atual, status_anterior, fatores_dev)
    st.markdown(f"<div class='result-card' style='--result-color:{cor_dev};'><div><span class='result-label'>Síntese do desenvolvimento</span><h3>{clas_dev}</h3></div><div class='result-metrics'>{texto_dev}</div></div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='soft-card'><div class='soft-title'>🎯 Orientação se houver atraso/ausência</div><ul><li>Iniciar orientação de estimulação imediatamente, sem aguardar diagnóstico fechado.</li><li>Reavaliar em curto prazo e considerar encaminhamento para equipe multiprofissional conforme gravidade.</li><li>Investigar audição, visão, interação social, tônus, assimetrias, alimentação, sono e contexto familiar.</li></ul></div>", unsafe_allow_html=True)
    with c2:
        prox = proxima or atual
        st.markdown(f"<div class='soft-card'><div class='soft-title'>🚀 Estimular próximos marcos — {prox['faixa']}</div>{html_lista(prox['proxima'])}</div>", unsafe_allow_html=True)

with tabs[2]:
    st.subheader("💉 Imunizações")
    st.caption("Primeiro, uma visualização inspirada no registro da Caderneta da Criança; abaixo, a área clínica interativa com atraso, próximas doses e EAPV.")
    render_caderneta_vacinas()

    st.markdown("### Área clínica interativa")
    calendario = obter_calendario_vacinal()
    eapv = eventos_adversos_vacinas()
    atrasadas, proximas = [], []
    st.markdown("<div class='vax-grid'>", unsafe_allow_html=True)
    for bloco in calendario:
        inner = f"<div class='vax-card'><div class='vax-head'><h3 style='margin:0'>{bloco['idade']}</h3><span class='badge' style='background:{bloco['cor']}'>PNI</span></div>"
        st.markdown(inner, unsafe_allow_html=True)
        for v in bloco["vacinas"]:
            key = f"vax_{bloco['idade']}_{v['nome']}_{v['dose']}"
            registrada = st.checkbox(f"{v['nome']} — {v['dose']} registrada", key=key)
            stt, cor = status_vacina(idade_meses_float, bloco["meses_ref"], registrada)
            if stt == "Atrasada/pendente":
                atrasadas.append(f"{v['nome']} ({v['dose']})")
            if "Próxima" in stt or stt == "Indicada agora":
                proximas.append(f"{v['nome']} ({v['dose']}) — {bloco['idade']}")
            ev = eapv.get(v["nome"], eapv.get(v["nome"].split()[0], {}))
            st.markdown(f"""
            <div class='vax-line'>
              <div class='vax-name'>{v['nome']} · {v['dose']} <span class='badge' style='background:{cor}'>{stt}</span></div>
              <div class='small-muted'><b>Proteção:</b> {v['doencas']} · <b>Intervalo:</b> {v.get('intervalo','conforme calendário')}</div>
              <details><summary>Orientar EAPV esperado e sinais de alerta</summary>
                <div class='small-muted'><b>Esperado:</b> {ev.get('esperado','Dor local, febre baixa ou sintomas leves podem ocorrer conforme vacina.')}<br>
                <b>Alerta:</b> {ev.get('alerta','Procurar serviço se evento intenso, persistente ou sinais de alergia/gravidade.')}</div>
              </details>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='risk-box'><div class='soft-title'>🚨 Vacinas atrasadas/pendentes</div>" + (html_lista(atrasadas) if atrasadas else "Nenhuma pendência marcada pelo cálculo atual.") + "<p class='small-muted'>Conduta geral: conferir caderneta e histórico, aplicar dose faltante quando elegível, sem reiniciar esquema; respeitar idade máxima, intervalo mínimo e contraindicações.</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='risk-box'><div class='soft-title'>📅 Próximas imunizações</div>" + (html_lista(proximas[:8]) if proximas else "Sem próximas doses no intervalo imediato pelo cálculo atual.") + "</div>", unsafe_allow_html=True)

with tabs[3]:
    st.subheader("💊 Ferro profilático e vitaminas")
    riscos = fatores_risco_anemia()
    c1, c2 = st.columns(2)
    with c1:
        fat_maternos = st.multiselect("Fatores maternos/gestacionais para anemia", riscos["maternos_gestacionais"])
    with c2:
        default_crianca = []
        if prematuro:
            default_crianca.append("Prematuridade")
        if peso_nasc_g < 2500:
            default_crianca.append("Baixo peso ao nascer (< 2.500 g)")
        fat_crianca = st.multiselect("Fatores da criança para anemia", riscos["crianca"], default=default_crianca)

    rec = recomendacao_ferro(idade_meses_float, peso, peso_nasc_g, idade_gest_sem, aleitamento_exclusivo, fat_crianca, fat_maternos)
    st.markdown(f"<div class='result-card' style='--result-color:#0f766e;'><div><span class='result-label'>Protocolo de ferro</span><h3>{rec['protocolo']}</h3></div><div class='result-metrics'>{rec['resumo']}<br><b>{rec['dose_mg_dia']:.1f} mg/dia</b> · {rec['dose_mg_kg_dia']:.2f} mg/kg/dia</div></div>", unsafe_allow_html=True)
    st.info(rec["conduta"])

    sais = obter_sais_ferro()
    c1, c2 = st.columns([1.4, 1])
    with c1:
        sal_nome = st.selectbox("Apresentação do sal de ferro", list(sais.keys()))
        duracao = st.selectbox("Duração sugerida", ["90 dias", "30 dias", "60 dias", "até a próxima consulta"], index=0)
        apresentacao = sais[sal_nome]
        calc = calcular_apresentacao_ferro(rec["dose_mg_dia"], apresentacao)
        st.markdown(f"<div class='soft-card'><div class='soft-title'>🧮 Cálculo pela apresentação escolhida</div><b>{calc['texto']}</b><br><span class='small-muted'>{apresentacao['marcas']} · {apresentacao['obs']}</span></div>", unsafe_allow_html=True)
        st.markdown("<div class='soft-title'>Modelo de prescrição</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='prescricao'>{modelo_prescricao_ferro(rec['dose_mg_dia'], sal_nome, apresentacao, calc, duracao)}</div>", unsafe_allow_html=True)
    with c2:
        render_imagem_ferro(apresentacao.get("imagem", ""))

    st.markdown("### Vitaminas e micronutrientes")
    v1, v2 = st.columns(2)
    with v1:
        fat_d = st.multiselect("Risco para hipovitaminose D", fatores_risco_hipovitaminose_d(), default=["Prematuridade"] if prematuro else [])
    with v2:
        fat_b12 = st.multiselect("Risco para deficiência de B12", fatores_risco_vitamina_b12())
    vitaminas = recomendacao_vitaminas(idade_meses_float, fat_d, fat_b12)
    cols = st.columns(3)
    for col, (nome, info) in zip(cols, vitaminas.items()):
        with col:
            st.markdown(f"<div class='soft-card'><div class='soft-title'>{nome}</div><b>{info['status']}</b><p class='small-muted'>{info['orientacao']}</p></div>", unsafe_allow_html=True)

with tabs[4]:
    st.subheader("📝 Orientações por idade e achados")
    for bloco in obter_orientacoes_detalhadas(idade_meses_float, prematuro):
        st.markdown(f"<div class='soft-card'><div class='soft-title'>{bloco['icone']} {bloco['titulo']}</div>{html_lista(bloco['itens'])}<p class='small-muted'><b>Conduta/orientação:</b> {bloco['conduta']}</p></div>", unsafe_allow_html=True)
