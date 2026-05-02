from __future__ import annotations

from datetime import date
import math

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
    obter_sais_ferro,
    recomendacao_ferro,
    calcular_apresentacao_ferro,
    recomendacao_vitaminas,
    obter_orientacoes_detalhadas,
    obter_marcos_vigilancia,
    classificar_desenvolvimento,
    obter_calendario_vacinal,
    status_vacina,
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
    # Limites aproximados para manter aparência da Caderneta. Ainda assim, expande se o ponto ficar fora.
    limites = {
        ("Peso", "0 a 2 anos"): (0, 18), ("Peso", "2 a 5 anos"): (7, 32), ("Peso", "5 a 10 anos"): (10, 65),
        ("Estatura", "0 a 2 anos"): (40, 105), ("Estatura", "2 a 5 anos"): (75, 125), ("Estatura", "5 a 10 anos"): (95, 165),
        ("IMC", "0 a 2 anos"): (10, 24), ("IMC", "2 a 5 anos"): (10, 22), ("IMC", "5 a 10 anos"): (10, 28),
        ("PC", "0 a 2 anos"): (30, 55),
    }
    ymin, ymax = limites.get((parametro, faixa), (float(df[["SD3neg", "SD3"]].min().min()), float(df[["SD3neg", "SD3"]].max().max())))
    ymin = min(ymin, valor - abs(valor) * 0.08)
    ymax = max(ymax, valor + abs(valor) * 0.08)
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
    # meses = grid clara nativa; anos = linhas verticais mais escuras.
    for m in range(int(rx[0]), int(rx[1]) + 1):
        if m % 12 == 0:
            fig.add_vline(x=m, line_width=1.6, line_color="rgba(20,20,20,.42)")
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
        height=620,
        template="plotly_white",
        margin=dict(l=30, r=20, t=30, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=-0.28, xanchor="left", x=0),
        xaxis=dict(title="Idade (meses)", range=rx, dtick=1, showgrid=True, gridcolor="rgba(148,163,184,.25)", zeroline=False),
        yaxis=dict(title=f"{titulo} ({unidade})", range=limite_y_caderneta(parametro, faixa, df_plot, valor), showgrid=True, gridcolor="rgba(148,163,184,.30)", zeroline=False),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "toImageButtonOptions": {"format": "png", "filename": f"{parametro.lower()}_puericultura"}, "modeBarButtonsToAdd": ["drawline", "eraseshape"]})


def card(titulo, corpo, icone="ℹ️"):
    st.markdown(f"<div class='soft-card'><div class='soft-title'>{icone} {titulo}</div>{corpo}</div>", unsafe_allow_html=True)


def idade_extenso(idade_dias: int):
    anos = int(idade_dias // 365.25)
    meses = int((idade_dias % 365.25) // 30.4375)
    dias = int((idade_dias % 365.25) % 30.4375)
    return anos, meses, dias


def css(sexo):
    accent = "#0f766e" if sexo == "Masculino" else "#7e22ce"
    return f"""
    <style>
    :root {{ --accent:{accent}; --card:rgba(255,255,255,.88); --border:rgba(100,116,139,.22); --text:#0f172a; --muted:#475569; }}
    @media (prefers-color-scheme: dark) {{
      :root {{ --card:rgba(15,23,42,.78); --border:rgba(148,163,184,.25); --text:#e2e8f0; --muted:#cbd5e1; }}
      .stApp {{ background: linear-gradient(135deg,#020617,#111827 55%,#1e293b)!important; color:var(--text); }}
      .soft-card,.top-panel,.vax-card,.dev-card,.result-card,.risk-box {{ color:var(--text); }}
    }}
    .stApp {{ background: linear-gradient(135deg, color-mix(in srgb, var(--accent) 10%, white), #f8fafc 48%, #ffffff); }}
    .block-container {{ padding-top: 1rem; max-width: 1500px; }}
    h1,h2,h3 {{ color: var(--accent)!important; }}
    .hero {{ padding: 1.2rem 1.4rem; border-radius: 24px; background: var(--card); border:1px solid var(--border); box-shadow:0 14px 34px rgba(15,23,42,.08); margin-bottom: 1rem; }}
    .hero h1 {{ margin:0; font-size: clamp(1.6rem, 2.5vw, 2.4rem); }}
    .hero p {{ color:var(--muted); margin:.25rem 0 0 0; }}
    .top-panel {{ position: sticky; top: .4rem; z-index: 999; padding: 1rem; border-radius: 22px; background: var(--card); border:1px solid var(--border); box-shadow:0 12px 30px rgba(15,23,42,.10); backdrop-filter: blur(10px); margin-bottom: 1rem; }}
    .metric-pill {{ display:inline-block; padding:.55rem .8rem; border-radius:999px; background:color-mix(in srgb, var(--accent) 12%, white); color:var(--accent); font-weight:800; margin:.2rem .35rem .2rem 0; }}
    .result-card {{ display:flex; justify-content:space-between; gap:1rem; align-items:center; padding:1rem 1.1rem; border-radius:22px; color:white; background:linear-gradient(135deg,var(--result-color), color-mix(in srgb, var(--result-color) 70%, black)); box-shadow:0 14px 30px rgba(15,23,42,.12); margin:.5rem 0 1rem; }}
    .result-card h3 {{ color:white!important; margin:.15rem 0 0; }} .result-label {{ opacity:.88; font-weight:800; }} .result-metrics {{ text-align:right; }}
    .soft-card,.risk-box {{ background:var(--card); border:1px solid var(--border); border-radius:22px; padding:1rem; box-shadow:0 10px 24px rgba(15,23,42,.06); margin-bottom:1rem; }}
    .soft-title {{ font-size:1.05rem; font-weight:900; color:var(--accent); margin-bottom:.45rem; }}
    .vax-card {{ background:var(--card); border:1px solid var(--border); border-radius:24px; overflow:hidden; box-shadow:0 10px 26px rgba(15,23,42,.07); margin-bottom:1rem; }}
    .vax-head {{ padding:1rem 1.1rem; color:white; display:flex; align-items:center; justify-content:space-between; gap:.6rem; }}
    .vax-body {{ padding:1rem; }} .vax-item {{ border:1px solid var(--border); border-radius:18px; padding:.85rem; margin-bottom:.7rem; }}
    .badge {{ display:inline-block; border-radius:999px; padding:.25rem .55rem; color:white; font-weight:800; font-size:.76rem; }}
    .dev-card {{ background:var(--card); border:1px solid var(--border); border-radius:22px; padding:1rem; margin-bottom:.8rem; box-shadow:0 8px 20px rgba(15,23,42,.06); }}
    .dev-top {{ display:flex; align-items:center; justify-content:space-between; gap:.6rem; }} .area {{ border-radius:999px; padding:.25rem .55rem; background:color-mix(in srgb, var(--accent) 12%, white); color:var(--accent); font-weight:900; font-size:.78rem; }}
    .small-muted {{ color:var(--muted); font-size:.9rem; }}
    .grid2 {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:1rem; }}
    ul {{ margin-bottom:.2rem; }}
    @media (max-width: 800px) {{ .top-panel {{ position: relative; top:0; }} .result-card {{ flex-direction:column; align-items:flex-start; }} .result-metrics {{ text-align:left; }} }}
    </style>
    """


tabelas_oms = carregar_tabelas()

st.markdown("""
<div class='hero'>
  <h1>👶 Puericultura Digital</h1>
  <p>Consulta técnica baseada em idade, sexo, crescimento, desenvolvimento, imunizações, suplementação e orientações clínicas.</p>
</div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='top-panel'>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1.1, 1, 1, 1])
    with c1:
        sexo = st.selectbox("Sexo", ["Masculino", "Feminino"], key="sexo_top")
    with c2:
        data_nasc = st.date_input("Nascimento", value=date(2023, 1, 1), key="dn")
    with c3:
        data_aval = st.date_input("Consulta", value=date.today(), key="da")
    with c4:
        prematuro = st.checkbox("Nasceu pré-termo?", key="prem")

    p1, p2, p3, p4, p5 = st.columns(5)
    with p1:
        idade_gestacional = st.number_input("IG ao nascer", 22, 42, 39, disabled=not prematuro)
    with p2:
        peso_nascer = st.number_input("Peso ao nascer (g)", 400, 6000, 3200, step=50)
    with p3:
        peso = st.number_input("Peso atual (kg)", 0.5, 100.0, 10.0, step=0.1)
    with p4:
        estatura = st.number_input("Comprimento/estatura (cm)", 30.0, 170.0, 80.0, step=0.5)
    with p5:
        pc = st.number_input("PC atual (cm)", 20.0, 70.0, 45.0, step=0.1)

    idade_cron_dias = max(0, (data_aval - data_nasc).days)
    correcao_dias = max(0, (40 - idade_gestacional) * 7) if prematuro else 0
    idade_corr_dias = max(0, idade_cron_dias - correcao_dias)
    idade_usada_dias = idade_corr_dias if prematuro else idade_cron_dias
    idade_meses = idade_usada_dias / 30.4375
    anos, meses_i, dias_i = idade_extenso(idade_usada_dias)
    baixo_peso = peso_nascer < 2500
    st.markdown(f"<span class='metric-pill'>Idade usada no app: {anos}a {meses_i}m {dias_i}d</span><span class='metric-pill'>Idade cronológica: {idade_cron_dias/30.4375:.1f} meses</span><span class='metric-pill'>Peso nascer: {peso_nascer:g} g</span>", unsafe_allow_html=True)
    if prematuro:
        st.info("Pré-termo selecionado: o app usa idade corrigida para desenvolvimento e análise inicial. A seção de prematuridade está destacada para futura integração de curvas/intervenções específicas.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(css(sexo), unsafe_allow_html=True)

if tabelas_oms is None:
    st.stop()

imc = peso / ((estatura / 100) ** 2)
faixa, rx = faixa_x_por_idade(idade_meses)

tabs = st.tabs(["📈 Crescimento", "💊 Ferro e vitaminas", "🧠 Desenvolvimento", "💉 Imunizações", "📝 Orientações"])

with tabs[0]:
    st.subheader("📈 Crescimento e estado nutricional")
    st.caption("Grade mensal clara, linhas anuais mais escuras, zoom por faixa etária e botão nativo de download da imagem no Plotly.")
    if prematuro:
        card("Área reservada para pré-termo", "<p>Para crianças pré-termo, as curvas podem exigir padrão específico e idade corrigida. Esta versão já separa idade cronológica/corrigida e deixa o bloco técnico preparado para receber as curvas correspondentes.</p>", "🟣")
    sub = st.tabs(["⚖️ Peso", "📏 Estatura", "🧮 IMC", "🧠 Perímetro cefálico"])
    cfg = [
        ("Peso", "Peso/idade", "kg", peso, faixa, rx),
        ("Estatura", "Comprimento/estatura por idade", "cm", estatura, faixa, rx),
        ("IMC", "IMC/idade", "kg/m²", imc, faixa, rx),
        ("PC", "Perímetro cefálico/idade", "cm", pc, "0 a 2 anos", [0, 24]),
    ]
    for tab, (param, titulo, unidade, valor, faixa_param, rx_param) in zip(sub, cfg):
        with tab:
            if param == "PC" and idade_meses > 24:
                st.warning("O perímetro cefálico é acompanhado rotineiramente nos gráficos até 2 anos. Interprete valores após essa idade conforme indicação clínica.")
            df = tabelas_oms[sexo][param]
            plotar_crescimento(df, param, titulo, unidade, valor, idade_usada_dias, idade_meses, faixa_param, rx_param)

with tabs[1]:
    st.subheader("💊 Suplementação de ferro, vitamina D, vitamina A e B12")
    st.caption("Bloco técnico para triagem de risco, cálculo em ferro elementar e orientação prática por idade/peso/especificidades.")
    cA, cB = st.columns([1, 1])
    with cA:
        protocolo_ferro = st.radio("Protocolo de ferro profilático", ["Ministério da Saúde — 10 a 12,5 mg/dia em ciclos", "SBP — 1 mg/kg/dia até 24 meses"], horizontal=False)
        recebe_formula = st.checkbox("Recebe ≥500 mL/dia de fórmula infantil fortificada?", value=False)
        area_vit_a = st.checkbox("Município/região com rotina/programa de suplementação de vitamina A?", value=False)
    with cB:
        st.markdown("<div class='risk-box'><b>Fatores de risco para anemia ferropriva</b>", unsafe_allow_html=True)
        riscos_anemia_selecionados = []
        for grupo, itens in fatores_risco_anemia().items():
            with st.expander(f"Riscos {grupo}", expanded=(grupo == "criança")):
                for item in itens:
                    if st.checkbox(item, key=f"anemia_{grupo}_{item}", value=(item == "Prematuridade" and prematuro) or (item.startswith("Baixo peso") and baixo_peso)):
                        riscos_anemia_selecionados.append(item)
        st.markdown("</div>", unsafe_allow_html=True)

    r_ferro = recomendacao_ferro(idade_meses, peso, prematuro, baixo_peso, protocolo_ferro, recebe_formula, riscos_anemia_selecionados)
    sal_nome = st.selectbox("Apresentação de ferro para cálculo", list(obter_sais_ferro().keys()))
    sal = obter_sais_ferro()[sal_nome]
    dose_pratica = calcular_apresentacao_ferro(r_ferro["dose_mg_dia"], sal)
    card("Recomendação atual de ferro", f"<h3>{r_ferro['status']}</h3><p>{r_ferro['texto']}</p><p><b>Ciclo/tempo:</b> {r_ferro['ciclo']}</p><p><b>Dose calculada:</b> {r_ferro['dose_mg_dia']:g} mg/dia de ferro elementar</p><p><b>Com {sal_nome}:</b> {dose_pratica}</p><p class='small-muted'>{sal['uso']} · Marcas/exemplos: {sal['marcas']}</p><p><b>Atenção:</b> {r_ferro['alerta']}</p>", "🩸")

    d1, d2 = st.columns(2)
    with d1:
        riscos_d = st.multiselect("Fatores de risco para hipovitaminose D", fatores_risco_hipovitaminose_d(), default=["Prematuridade"] if prematuro else [])
    with d2:
        riscos_b12 = st.multiselect("Fatores de risco para deficiência de B12", fatores_risco_vitamina_b12())
    rec_vits = recomendacao_vitaminas(idade_meses, prematuro, riscos_d, riscos_b12, area_vit_a)
    cols = st.columns(3)
    for col, (k, v) in zip(cols, rec_vits.items()):
        with col:
            card(k, f"<p>{v}</p>", "☀️" if k == "Vitamina D" else "💊")

with tabs[2]:
    st.subheader("🧠 Desenvolvimento neuropsicomotor")
    atual, anterior, _ = obter_marcos_vigilancia(idade_meses, prematuro)
    st.markdown(f"<span class='metric-pill'>Faixa atual: {atual['faixa']}</span>", unsafe_allow_html=True)
    st.caption("Marque os marcos observados. A classificação usa a lógica da Caderneta: ausência de marco da faixa atual = alerta; ausência de dois ou mais da faixa anterior, PC alterado ou dismorfismos importantes = provável atraso.")

    fatores_dev = st.multiselect("Fatores de risco para desenvolvimento", ["Prematuridade", "Baixo peso ao nascer", "STORCH/Zika ou infecção gestacional", "Pré-natal incompleto", "Icterícia grave", "Internação neonatal", "Meningite/convulsões/TCE", "Violência, depressão materna, álcool/drogas no domicílio", "Consanguinidade"], default=(["Prematuridade"] if prematuro else []) + (["Baixo peso ao nascer"] if baixo_peso else []))
    pc_alterado = st.checkbox("PC < -2Z ou > +2Z?", value=False)
    fenotipicas = st.checkbox("3 ou mais alterações fenotípicas relevantes?", value=False)
    ausentes_ant = st.number_input("Número de marcos ausentes na faixa anterior", 0, 10, 0)

    st.markdown("### O que a criança já deve fazer nesta idade")
    status = {}
    for area, marco in atual["marcos"]:
        st.markdown(f"<div class='dev-card'><div class='dev-top'><b>{marco}</b><span class='area'>{area}</span></div>", unsafe_allow_html=True)
        status[marco] = st.radio("Status", ["Presente", "Ausente", "Não verificado"], horizontal=True, key=f"dev_{marco}", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

    impressao, conduta, cor_dev = classificar_desenvolvimento(status, bool(fatores_dev), pc_alterado, fenotipicas, int(ausentes_ant))
    st.markdown(f"<div class='result-card' style='--result-color:{cor_dev};'><div><span class='result-label'>Classificação do desenvolvimento</span><h3>{impressao}</h3></div><div class='result-metrics'>{conduta}</div></div>", unsafe_allow_html=True)

    st.markdown("### Como orientar o genitor para estimular a próxima fase")
    html = "<ul>" + "".join(f"<li>{x}</li>" for x in atual["proxima"]) + "</ul>"
    card("Estimulação domiciliar orientada", html, "🎯")

with tabs[3]:
    st.subheader("💉 Imunizações — calendário técnico e pendências")
    st.caption("O layout usa cards largos e calcula o status por idade. Para atraso: conferir caderneta, aplicar doses faltantes sem reiniciar esquema e respeitar idade máxima/intervalo mínimo.")
    calendario = obter_calendario_vacinal()
    proximas = []
    for bloco in calendario:
        with st.expander(f"{bloco['idade']} — {len(bloco['vacinas'])} vacina(s)", expanded=(bloco["mes"] <= idade_meses <= bloco["mes"] + 2)):
            st.markdown(f"<div class='vax-card'><div class='vax-head' style='background:{bloco['cor']}'><b>{bloco['idade']}</b><span>PNI criança</span></div><div class='vax-body'>", unsafe_allow_html=True)
            for vacina in bloco["vacinas"]:
                aplicada = st.checkbox(f"Registro: {vacina['nome']} — {vacina['dose']}", key=f"vax_{bloco['idade']}_{vacina['nome']}_{vacina['dose']}")
                stt, cor, instr = status_vacina(idade_meses, bloco["mes"], aplicada)
                if not aplicada and bloco["mes"] >= idade_meses:
                    proximas.append((bloco["mes"], vacina["nome"], vacina["dose"], bloco["idade"]))
                st.markdown(f"""
                <div class='vax-item'>
                    <span class='badge' style='background:{cor}'>{stt}</span>
                    <h4 style='margin:.45rem 0 .15rem 0'>{vacina['nome']} — {vacina['dose']}</h4>
                    <p><b>Proteção:</b> {vacina['protege']}<br><b>Intervalo:</b> {vacina['intervalo']}</p>
                    <p><b>Se atrasada/pendente:</b> {vacina['atraso']}</p>
                    <p class='small-muted'>{instr}</p>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div></div>", unsafe_allow_html=True)
    proximas = sorted(proximas, key=lambda x: x[0])[:8]
    if proximas:
        lista = "<ul>" + "".join(f"<li><b>{idade}</b>: {nome} — {dose}</li>" for _, nome, dose, idade in proximas) + "</ul>"
        card("Próximas imunizações programadas", lista, "📌")

with tabs[4]:
    st.subheader("📝 Orientações clínicas e familiares por idade")
    orientacoes = obter_orientacoes_detalhadas(idade_meses, prematuro, {})
    for bloco in orientacoes:
        itens = "<ul>" + "".join(f"<li>{item}</li>" for item in bloco["itens"]) + "</ul>"
        corpo = itens + f"<p><b>Conduta/orientação:</b> {bloco['conduta']}</p>"
        card(bloco["titulo"], corpo, bloco["icone"])

st.markdown("<div class='small-muted'>Ferramenta de apoio clínico/educacional. Não substitui avaliação médica, caderneta física, protocolos locais, bula de imunobiológicos/medicamentos ou julgamento clínico.</div>", unsafe_allow_html=True)
