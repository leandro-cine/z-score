from __future__ import annotations

from datetime import date
from pathlib import Path
import json
import math

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import norm
import streamlit as st

from diretrizes import (
    obter_classificacao, obter_faixas_zscore, classificar_peso_ig,
    obter_orientacoes_detalhadas, obter_marcos_vigilancia, classificar_desenvolvimento,
    obter_mapa_vacinal_cards, status_vacina, eventos_adversos_vacinas,
    fatores_risco_anemia, fatores_risco_hipovitaminose_d, fatores_risco_vitamina_b12,
    obter_sais_ferro, recomendacao_ferro, calcular_apresentacao_ferro, modelo_prescricao_ferro,
    calcular_vitamina_a_pnsva, calcular_vitamina_d_sbp, recomendacao_vitaminas,
    imagem_desenvolvimento_por_faixa,
)
# Importação tolerante da estrutura da consulta.
# Evita quebrar o app se o repositório estiver temporariamente com uma versão antiga de estrutura_consulta.py.
try:
    import estrutura_consulta as _ec
except Exception:
    _ec = None

def _ec_get(nome, padrao):
    return getattr(_ec, nome, padrao) if _ec is not None else padrao

INTERROGATORIO_SEGMENTAR = _ec_get("INTERROGATORIO_SEGMENTAR", {})
ANTECEDENTES_MATERNOS = _ec_get("ANTECEDENTES_MATERNOS", [])
INTERCORRENCIAS_PERINATAIS = _ec_get("INTERCORRENCIAS_PERINATAIS", [])
ANTECEDENTES_PATOLOGICOS = _ec_get("ANTECEDENTES_PATOLOGICOS", [])
ANTECEDENTES_FAMILIARES = _ec_get("ANTECEDENTES_FAMILIARES", [])
TRIAGENS_NEONATAIS = _ec_get("TRIAGENS_NEONATAIS", {})
TIPOS_ALEITAMENTO = _ec_get("TIPOS_ALEITAMENTO", ["Aleitamento materno exclusivo", "Aleitamento materno predominante", "Aleitamento misto", "Fórmula infantil exclusiva", "Leite de vaca/outro leite", "Alimentação da família conforme idade"])
HISTORICO_AME = _ec_get("HISTORICO_AME", ["Esteve em AME até 6 meses", "AME interrompido antes de 6 meses", "Não esteve em AME", "Não sabe informar"])
ALIMENTO_LACTEO_ANTES_6M = _ec_get("ALIMENTO_LACTEO_ANTES_6M", ["Fórmula infantil", "Leite de vaca", "Leite de cabra/outro leite", "Misto", "Não sabe informar"])
PADRAO_FEZES = _ec_get("PADRAO_FEZES", ["Diárias", "A cada 2-3 dias", "Constipação", "Diarreia", "Escape fecal"])
PADRAO_URINA = _ec_get("PADRAO_URINA", ["Habitual", "Reduzida", "Aumentada", "Disúria", "Urina escura", "Enurese"])
SONO = _ec_get("SONO", ["Sono adequado", "Despertares noturnos", "Roncos", "Sono agitado", "Sonolência diurna"])
CONDICOES_MORADIA = _ec_get("CONDICOES_MORADIA", ["Casa de alvenaria", "Apartamento", "Área rural", "Saneamento adequado", "Água tratada", "Animais domésticos", "Tabagismo domiciliar", "Aglomeração domiciliar"])
ECTOSCOPIA = _ec_get("ECTOSCOPIA", [])
CABECA_PESCOCO = _ec_get("CABECA_PESCOCO", {})
EXAME_RESPIRATORIO = _ec_get("EXAME_RESPIRATORIO", {})
EXAME_CARDIO = _ec_get("EXAME_CARDIO", {})
EXAME_ABDOMINAL = _ec_get("EXAME_ABDOMINAL", {})
REFLEXOS_PRIMITIVOS = _ec_get("REFLEXOS_PRIMITIVOS", {})
BRISTOL_FEZES = _ec_get("BRISTOL_FEZES", ["Tipo 1", "Tipo 2", "Tipo 3", "Tipo 4", "Tipo 5", "Tipo 6", "Tipo 7"])
EXAME_GENITALIA = _ec_get("EXAME_GENITALIA", [])
EXAME_OSTEOMUSCULAR = _ec_get("EXAME_OSTEOMUSCULAR", [])
EXAME_NEUROLOGICO = _ec_get("EXAME_NEUROLOGICO", [])
EXAME_PELE_FANEROS = _ec_get("EXAME_PELE_FANEROS", [])
DOENCAS_MATERNAS_INFECCIOSAS = _ec_get("DOENCAS_MATERNAS_INFECCIOSAS", [])
DOENCAS_MATERNAS_CLINICAS = _ec_get("DOENCAS_MATERNAS_CLINICAS", [])
VACINAS_GESTACAO = _ec_get("VACINAS_GESTACAO", [])
EXAMES_COMPLEMENTARES_MODELOS = _ec_get("EXAMES_COMPLEMENTARES_MODELOS", {})
from medicamentos_sus import listar_principios_ativos, obter_apresentacoes, checar_medicamento
try:
    from protocolos_ambulatoriais import obter_protocolos_ambulatoriais, campos_do_protocolo, executar_protocolo
except Exception:
    obter_protocolos_ambulatoriais = campos_do_protocolo = executar_protocolo = None
try:
    from ia_prescricao import gerar_passagem_caso_ia, gerar_passagem_caso_local, gerar_orientacao_medicamento_ia, diagnostico_ia_configurada
except Exception:
    gerar_passagem_caso_ia = gerar_passagem_caso_local = gerar_orientacao_medicamento_ia = diagnostico_ia_configurada = None

st.set_page_config(page_title="Puericultura Digital", page_icon="👶", layout="wide", initial_sidebar_state="collapsed")

# =========================
# Utilitários
# =========================

def fmt_data(d: date) -> str:
    return d.strftime("%d/%m/%Y")


def idade_extenso(idade_dias: int):
    anos = int(idade_dias // 365.25)
    meses = int((idade_dias % 365.25) // 30.4375)
    dias = int((idade_dias % 365.25) % 30.4375)
    return anos, meses, dias


def idade_texto(idade_dias: int):
    a, m, d = idade_extenso(idade_dias)
    return f"{a}a {m}m {d}d"


def col_z(z: int) -> str:
    if z == 0:
        return "SD0"
    return f"SD{z}" if z > 0 else f"SD{abs(z)}neg"


def safe_join(v):
    if not v:
        return ""
    if isinstance(v, str):
        return v
    if isinstance(v, dict):
        return "; ".join([f"{k}: {x}" for k, x in v.items() if x not in (None, "", [], {})])
    return "; ".join([str(x) for x in v if str(x).strip()])


def html_lista(itens):
    if not itens:
        return "<span class='small-muted'>Nenhum item selecionado.</span>"
    return "<ul>" + "".join(f"<li>{x}</li>" for x in itens) + "</ul>"


def escape_html(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def titulo_opcao(valor):
    """Mostra opções com inicial maiúscula sem mudar o valor interno."""
    if valor is None:
        return ""
    texto = str(valor)
    if not texto:
        return texto
    return texto[0].upper() + texto[1:]


def selecionar_opcoes(label, opcoes, key, default=None, cols=2, help=None):
    """Seleção amigável para mobile: usa pills quando disponível; fallback para checkboxes.
    Evita abrir teclado em telas touchscreen, ao contrário do multiselect.
    """
    default = default or []
    if hasattr(st, "pills"):
        try:
            return st.pills(label, opcoes, default=default, selection_mode="multi", key=key, format_func=titulo_opcao, help=help)
        except TypeError:
            pass
    st.markdown(f"**{label}**")
    if help:
        st.caption(help)
    selecionados = []
    colunas = st.columns(cols)
    for i, opcao in enumerate(opcoes):
        with colunas[i % cols]:
            if st.checkbox(titulo_opcao(opcao), value=opcao in default, key=f"{key}_{i}"):
                selecionados.append(opcao)
    return selecionados


def selecionar_um(label, opcoes, key, index=0, help=None):
    return st.selectbox(label, opcoes, index=index, key=key, format_func=titulo_opcao, help=help)


def popover_ou_expander(label, expanded=False):
    return st.popover(label) if hasattr(st, "popover") else st.expander(label, expanded=expanded)


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
            "Masculino": {"Peso": carregar_e_limpar("WFA_boys_z_exp.csv"), "Estatura": carregar_e_limpar("LFA_boys_z_exp.csv"), "IMC": carregar_e_limpar("BFA_boys_z_exp.csv"), "PC": carregar_e_limpar("HCFA_boys_z_exp.csv")},
            "Feminino": {"Peso": carregar_e_limpar("WFA_girls_z_exp.csv"), "Estatura": carregar_e_limpar("LFA_girls_z_exp.csv"), "IMC": carregar_e_limpar("BFA_girls_z_exp.csv"), "PC": carregar_e_limpar("HCFA_girls_z_exp.csv")},
        }
    except Exception as exc:
        st.error(f"Não consegui carregar as tabelas OMS. Verifique os CSVs no repositório. Detalhe: {exc}")
        return None


def calcular_z_lms(valor: float, linha: pd.Series) -> float:
    if linha["L"] != 0:
        return (((valor / linha["M"]) ** linha["L"]) - 1) / (linha["L"] * linha["S"])
    return np.log(valor / linha["M"]) / linha["S"]


def classificar_antropometria(tabelas, sexo, idade_dias, idade_meses, peso, estatura, pc):
    imc = peso / ((estatura / 100) ** 2)
    cfg = {"Peso": peso, "Estatura": estatura, "IMC": imc, "PC": pc}
    res = {}
    if not tabelas:
        return res
    for param, valor in cfg.items():
        if param == "PC" and idade_meses > 24:
            continue
        df = tabelas[sexo][param]
        ref = int(min(max(idade_dias, df["Day"].min()), df["Day"].max()))
        linha = df.iloc[(df["Day"] - ref).abs().argsort()[:1]].iloc[0]
        z = calcular_z_lms(valor, linha)
        cls, crit, cor = obter_classificacao(z, param)
        res[param] = {"valor": valor, "z": round(float(z), 2), "percentil": round(float(norm.cdf(z)*100), 1), "classificacao": cls, "criterio": crit, "cor": cor}
    return res


def faixa_x_por_idade(meses: float):
    if meses <= 24: return "0 a 2 anos", [0, 24]
    if meses <= 60: return "2 a 5 anos", [24, 60]
    return "5 a 10 anos", [60, 120]


def limite_y_caderneta(parametro: str, faixa: str, df: pd.DataFrame, valor: float):
    limites = {
        ("Peso", "0 a 2 anos"): (0,18), ("Peso","2 a 5 anos"):(7,32), ("Peso","5 a 10 anos"):(10,65),
        ("Estatura","0 a 2 anos"):(40,105), ("Estatura","2 a 5 anos"):(75,125), ("Estatura","5 a 10 anos"):(95,165),
        ("IMC","0 a 2 anos"):(10,24), ("IMC","2 a 5 anos"):(10,22), ("IMC","5 a 10 anos"):(10,28),
        ("PC","0 a 2 anos"):(30,55),
    }
    ymin, ymax = limites.get((parametro, faixa), (float(df[["SD3neg","SD3"]].min().min()), float(df[["SD3neg","SD3"]].max().max())))
    ymin = min(ymin, valor - max(abs(valor)*0.08,1))
    ymax = max(ymax, valor + max(abs(valor)*0.08,1))
    return [round(ymin,1), round(ymax,1)]


def adicionar_sombreamento(fig, df_plot, parametro, x):
    for f in obter_faixas_zscore(parametro):
        c1, c2 = col_z(f["z_min"]), col_z(f["z_max"])
        if c1 not in df_plot.columns or c2 not in df_plot.columns:
            continue
        fig.add_trace(go.Scatter(x=x, y=df_plot[c1], mode="lines", line=dict(width=0), hoverinfo="skip", showlegend=False))
        fig.add_trace(go.Scatter(x=x, y=df_plot[c2], mode="lines", line=dict(width=0), fill="tonexty", fillcolor=f["cor_fill"], name=f"{f['rotulo']} ({f['intervalo']})", hoverinfo="skip"))


def adicionar_curvas(fig, df_plot, x):
    curvas = [("SD3neg","-3Z","#9f1239",1.6,"dash"),("SD2neg","-2Z","#ea580c",2,"solid"),("SD1neg","-1Z","#94a3b8",1.1,"dot"),("SD0","Mediana","#15803d",3,"solid"),("SD1","+1Z","#94a3b8",1.1,"dot"),("SD2","+2Z","#ea580c",2,"solid"),("SD3","+3Z","#9f1239",1.6,"dash")]
    for col,nome,cor,larg,dash in curvas:
        if col in df_plot.columns:
            fig.add_trace(go.Scatter(x=x, y=df_plot[col], mode="lines", line=dict(color=cor, width=larg, dash=dash), name=nome, hovertemplate=f"{nome}: %{{y:.2f}}<extra></extra>"))


def plotar_crescimento(df, parametro, titulo, unidade, valor, idade_dias, idade_meses, faixa, rx):
    ref = int(min(max(idade_dias, rx[0]*30.4375), df["Day"].max()))
    linha = df.iloc[(df["Day"] - ref).abs().argsort()[:1]].iloc[0]
    z = calcular_z_lms(valor, linha)
    cls, crit, cor = obter_classificacao(z, parametro)
    pct = norm.cdf(z)*100
    df_plot = df[(df["Day"]/30.4375 >= rx[0]) & (df["Day"]/30.4375 <= rx[1])].copy()
    x = df_plot["Day"] / 30.4375
    st.markdown(f"<div class='result-card' style='--result-color:{cor};'><div><span class='result-label'>{titulo}</span><h3>{cls}</h3></div><div class='result-metrics'>Z = <b>{z:.2f}</b> · Percentil ≈ <b>P{pct:.0f}</b><br><small>{crit}</small></div></div>", unsafe_allow_html=True)
    fig = go.Figure()
    adicionar_sombreamento(fig, df_plot, parametro, x)
    adicionar_curvas(fig, df_plot, x)
    for m in range(int(rx[0]), int(rx[1])+1):
        if m % 12 == 0:
            fig.add_vline(x=m, line_width=1.7, line_color="rgba(15,23,42,.46)")
            if m > 0: fig.add_annotation(x=m, y=1.01, yref="paper", text=f"{m//12}a", showarrow=False, font=dict(size=11))
    fig.add_trace(go.Scatter(x=[idade_meses], y=[valor], mode="markers+text", marker=dict(size=16, color="#0f172a", line=dict(color="white", width=2)), text=[f"{valor:g} {unidade}"], textposition="top center", name="Paciente"))
    fig.update_layout(height=620, template="plotly_white", margin=dict(l=30,r=20,t=30,b=30), legend=dict(orientation="h", yanchor="bottom", y=-0.28, xanchor="left", x=0), xaxis=dict(title="Idade (meses)", range=rx, dtick=1, showgrid=True, gridcolor="rgba(148,163,184,.22)"), yaxis=dict(title=f"{titulo} ({unidade})", range=limite_y_caderneta(parametro, faixa, df_plot, valor), showgrid=True, gridcolor="rgba(148,163,184,.30)"))
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "toImageButtonOptions": {"format":"png", "filename":f"{parametro.lower()}_puericultura"}})
    return {"parametro": parametro, "titulo": titulo, "valor": valor, "unidade": unidade, "z": round(float(z),2), "percentil": round(float(pct),1), "classificacao": cls, "criterio": crit}

# =========================
# Estilo
# =========================

def css(sexo: str):
    accent = "#0f766e" if sexo == "Masculino" else "#7e22ce"
    return f"""
    <style>
    :root {{ --accent:{accent}; --card:rgba(255,255,255,.92); --border:rgba(100,116,139,.24); --text:#0f172a; --muted:#475569; --chip:color-mix(in srgb, var(--accent) 12%, white); --shadow:0 14px 34px rgba(15,23,42,.08); }}
    @media (prefers-color-scheme: dark) {{ :root {{ --card:rgba(15,23,42,.86); --border:rgba(148,163,184,.28); --text:#e2e8f0; --muted:#cbd5e1; --chip:rgba(30,41,59,.9); --shadow:0 16px 34px rgba(0,0,0,.28); }} .stApp {{ background:linear-gradient(135deg,#020617,#111827 55%,#1e293b)!important; color:var(--text); }} }}
    .stApp {{ background:linear-gradient(135deg, color-mix(in srgb, var(--accent) 10%, white), #f8fafc 48%, #ffffff); }}
    .block-container {{ padding-top:4.6rem; max-width:1500px; }}
    h1,h2,h3 {{ color:var(--accent)!important; }}
    .hero {{ padding:1.2rem 1.4rem; border-radius:24px; background:var(--card); border:1px solid var(--border); box-shadow:var(--shadow); margin:.4rem 0 1rem; }}
    .hero h1 {{ margin:0; font-size:clamp(1.6rem,2.5vw,2.4rem); }} .hero p {{ color:var(--muted); margin:.25rem 0 0; }}
    .top-panel {{ position:sticky; top:3.2rem; z-index:999; padding:1rem; border-radius:22px; background:var(--card); border:1px solid var(--border); box-shadow:var(--shadow); backdrop-filter:blur(10px); margin-bottom:1rem; }}
    .metric-pill {{ display:inline-block; padding:.52rem .75rem; border-radius:999px; background:var(--chip); color:var(--accent); font-weight:850; margin:.2rem .35rem .2rem 0; }}
    .soft-card,.risk-box,.vaccine-board,.timeline-card {{ background:var(--card); color:var(--text); border:1px solid var(--border); border-radius:22px; padding:1rem; box-shadow:var(--shadow); margin-bottom:1rem; }}
    .soft-title {{ font-size:1.05rem; font-weight:950; color:var(--accent); margin-bottom:.45rem; }}
    .small-muted {{ color:var(--muted); font-size:.9rem; }}
    .result-card {{ display:flex; justify-content:space-between; gap:1rem; align-items:center; padding:1rem 1.1rem; border-radius:22px; color:white; background:linear-gradient(135deg,var(--result-color), color-mix(in srgb, var(--result-color) 70%, black)); box-shadow:var(--shadow); margin:.5rem 0 1rem; }}
    .result-card h3 {{ color:white!important; margin:.15rem 0 0; }} .result-metrics {{ text-align:right; }}
    .passagem-box,.prescricao {{ white-space:pre-wrap; background:rgba(15,23,42,.05); border:1px solid var(--border); padding:1rem; border-radius:18px; color:var(--text); font-family:inherit; line-height:1.55; }}
    .timeline {{ display:flex; gap:.7rem; overflow-x:auto; padding:.4rem 0 1rem; }} .timeline-card {{ min-width:220px; }} .timeline-card.current {{ border:2px solid var(--accent); }} .timeline-dot {{ width:16px; height:16px; border-radius:50%; background:var(--accent); display:inline-block; margin-right:.4rem; }}
    .dev-instruction {{ background:color-mix(in srgb, var(--accent) 8%, transparent); border:1px dashed var(--accent); padding:.9rem; border-radius:18px; margin:.7rem 0; }}
    /* Vacinas: largura fixa para não alargar quando há poucos cards */
    .vaccine-board {{ overflow-x:auto; padding:1rem; }} .vaccine-board-title {{ font-size:1.15rem; font-weight:950; color:var(--accent); margin:.2rem 0 .75rem; }}
    .vaccine-age-section {{ margin-top:.9rem; }} .vaccine-age-title {{ font-weight:950; color:var(--accent); margin:.55rem 0 .5rem; font-size:.98rem; }}
    .vaccine-card-grid {{ display:grid!important; grid-template-columns:repeat(auto-fill, 150px)!important; gap:.75rem!important; justify-content:flex-start!important; align-items:stretch!important; }}
    .vaccine-card-link {{ width:150px!important; max-width:150px!important; min-height:122px; text-decoration:none!important; color:#111827!important; display:block; border-radius:18px; padding:.72rem .62rem; border:1px solid rgba(15,23,42,.20); box-shadow:0 8px 20px rgba(15,23,42,.12); position:relative; overflow:hidden; transition:.15s; }}
    .vaccine-card-link:hover {{ transform:translateY(-2px); box-shadow:0 12px 26px rgba(15,23,42,.18); filter:saturate(1.08); }} .vaccine-card-link.future {{ filter:saturate(.55); opacity:.58; box-shadow:none; }} .vaccine-card-link.done {{ outline:3px solid rgba(34,197,94,.35); }} .vaccine-card-link.late {{ outline:3px solid rgba(220,38,38,.48); }} .vaccine-card-link.pending {{ outline:3px solid rgba(245,158,11,.42); }}
    .vaccine-card-age {{ font-size:.72rem; font-weight:900; opacity:.82; margin-bottom:.22rem; }} .vaccine-card-name {{ font-size:.9rem; font-weight:950; line-height:1.08; }} .vaccine-card-dose {{ margin-top:.35rem; font-size:.74rem; font-weight:800; opacity:.86; }} .vaccine-card-status {{ position:absolute; left:.5rem; right:.5rem; bottom:.45rem; font-size:.65rem; font-weight:900; background:rgba(255,255,255,.72); border-radius:999px; padding:.18rem .4rem; text-align:center; }}
    .vaccine-modal {{ display:none; position:fixed; z-index:999999; inset:0; padding:5.2rem 1rem 1rem; background:rgba(2,6,23,.62); backdrop-filter:blur(4px); overflow:auto; }} .vaccine-modal:target {{ display:block; }} .vaccine-modal-card {{ max-width:760px; margin:0 auto; background:var(--card); color:var(--text); border:1px solid var(--border); border-radius:24px; padding:1.15rem; box-shadow:0 24px 70px rgba(0,0,0,.35); }} .vaccine-modal-close {{ float:right; text-decoration:none!important; color:var(--text)!important; background:var(--chip); border:1px solid var(--border); border-radius:999px; padding:.28rem .62rem; font-weight:900; }} .vaccine-pill {{ display:inline-block; padding:.22rem .55rem; border-radius:999px; font-size:.78rem; font-weight:850; margin:.1rem .25rem .1rem 0; background:var(--chip); border:1px solid var(--border); color:var(--accent); }}
    @media (max-width:760px) {{ .block-container {{ padding-top:3.8rem; }} .top-panel {{ top:3.55rem; border-radius:18px; }} .result-card {{ flex-direction:column; align-items:flex-start; }} .result-metrics {{ text-align:left; }} .vaccine-card-grid {{ grid-template-columns:repeat(2, minmax(0,1fr))!important; }} .vaccine-card-link {{ width:auto!important; max-width:none!important; min-height:112px; }} }}
    </style>
    """

# =========================
# Vacinas HTML
# =========================

def _hex_rgba(hex_color: str, alpha: float):
    h = hex_color.replace("#", "")
    try:
        r,g,b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        return f"rgba({r},{g},{b},{alpha})"
    except Exception:
        return f"rgba(229,231,235,{alpha})"


def _slug(texto: str):
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in str(texto)).strip("-")


def _status_vac_card(v, idade_meses, registrada):
    if registrada: return {"classe":"done", "rotulo":"✅ Registrada", "opacidade":1.0}
    atraso = idade_meses - float(v.get("idade_meses",0))
    if atraso >= 1: return {"classe":"late", "rotulo":"⚠️ Atrasada/pendente", "opacidade":1.0}
    if -0.25 <= atraso < 1: return {"classe":"pending", "rotulo":"📌 Indicada agora", "opacidade":1.0}
    if float(v.get("idade_meses",0)) - idade_meses <= 3: return {"classe":"future", "rotulo":f"🔜 Próxima", "opacidade":.66}
    return {"classe":"future", "rotulo":"Programada", "opacidade":.48}


def _items_html(items):
    if isinstance(items, str): items = [items]
    return "<ul>" + "".join(f"<li>{i}</li>" for i in (items or [])) + "</ul>"


def render_mapa_vacinal(idade_meses):
    vacinas = sorted(obter_mapa_vacinal_cards(), key=lambda v: (float(v.get("idade_meses",0)), v.get("nome",""), v.get("dose","")))
    if "vacinas_registradas" not in st.session_state:
        st.session_state["vacinas_registradas"] = {}
    with st.expander("🧾 Marcar vacinas já registradas na caderneta", expanded=False):
        cols = st.columns(3)
        for i, v in enumerate(vacinas):
            with cols[i % 3]:
                key = f"vac_reg_{v['id']}"
                st.session_state["vacinas_registradas"][v["id"]] = st.checkbox(f"{v['idade_label']} — {v['nome']} ({v['dose']})", key=key, value=st.session_state["vacinas_registradas"].get(v["id"], False))
    grupos = {}
    atrasadas, proximas = [], []
    modais = []
    for v in vacinas:
        grupos.setdefault(v["idade_label"], []).append(v)
    html = "<div id='imunizacoes' class='vaccine-board'><div class='vaccine-board-title'>Registro panorâmico clicável — agrupado por idade do Calendário Nacional</div><p class='small-muted'>Cards em cor normal: vacinas já esperadas para a idade. Cards sombreados: vacinas futuras. Clique no card para abrir técnica, atraso e EAPV.</p>"
    for grupo, itens in grupos.items():
        html += f"<div class='vaccine-age-section'><div class='vaccine-age-title'>{grupo}</div><div class='vaccine-card-grid'>"
        for v in itens:
            registrada = st.session_state["vacinas_registradas"].get(v["id"], False)
            stt = _status_vac_card(v, idade_meses, registrada)
            if stt["classe"] == "late": atrasadas.append(f"{grupo}: {v['nome']} — {v['dose']}")
            if stt["classe"] in ("pending", "future") and float(v.get("idade_meses",0)) >= idade_meses: proximas.append(f"{grupo}: {v['nome']} — {v['dose']}")
            modal_id = "vac-" + _slug(v["id"])
            bg = _hex_rgba(v.get("cor", "#e5e7eb"), stt["opacidade"])
            html += f"<a class='vaccine-card-link {stt['classe']}' href='#{modal_id}' style='background:{bg};'><div class='vaccine-card-age'>{v['idade_label']}</div><div class='vaccine-card-name'>{v['nome']}</div><div class='vaccine-card-dose'>{v['dose']}</div><div class='vaccine-card-status'>{stt['rotulo']}</div></a>"
            modais.append(f"<div id='{modal_id}' class='vaccine-modal'><div class='vaccine-modal-card'><a href='#imunizacoes' class='vaccine-modal-close'>Fechar ✕</a><h3>{v['nome']} — {v['dose']}</h3><span class='vaccine-pill'>{v['idade_label']}</span><span class='vaccine-pill'>{stt['rotulo']}</span><h4>🛡️ Proteção</h4><p>{v['protecao']}</p><h4>💉 Técnica</h4><p><b>Via:</b> {v['via']}<br><b>Volume:</b> {v['volume']}<br><b>Janela:</b> {v['janela']}</p><h4>⏱️ Se estiver atrasada</h4><p>{v['atraso']}</p><h4>✅ Eventos esperados</h4>{_items_html(v.get('esperado'))}<h4>🚨 Sinais de alerta</h4>{_items_html(v.get('alerta'))}<h4>🧾 Registro</h4><p>Registrar data, lote, laboratório/produto, unidade e assinatura/carimbo.</p></div></div>")
        html += "</div></div>"
    html += "</div>" + "".join(modais)
    st.markdown(html, unsafe_allow_html=True)
    return atrasadas, proximas

# =========================
# Passagem
# =========================

def montar_dados_passagem():
    return {
        "crianca": st.session_state.get("passagem_crianca", {}),
        "nascimento": st.session_state.get("passagem_nascimento", {}),
        "consulta": st.session_state.get("passagem_consulta", {}),
        "exame_fisico": st.session_state.get("passagem_exame", {}),
        "crescimento": st.session_state.get("passagem_crescimento", {}),
        "desenvolvimento": st.session_state.get("passagem_desenvolvimento", {}),
        "vacinas": st.session_state.get("passagem_vacinas", {}),
        "suplementacao": st.session_state.get("passagem_suplementacao", {}),
        "ambulatorio": st.session_state.get("passagem_ambulatorio", {}),
        "plano_sugerido": st.session_state.get("passagem_plano", []),
    }


def abrir_passagem():
    dados = montar_dados_passagem()
    usar_ia = st.session_state.get("usar_ia_passagem", False)
    if usar_ia and gerar_passagem_caso_ia:
        texto = gerar_passagem_caso_ia(dados)
    elif gerar_passagem_caso_local:
        texto = gerar_passagem_caso_local(dados)
    else:
        texto = json.dumps(dados, ensure_ascii=False, indent=2)
    try:
        @st.dialog("🧾 Passagem de caso")
        def _dialog():
            st.markdown("<div class='passagem-box'>" + escape_html(texto) + "</div>", unsafe_allow_html=True)
            st.download_button("Baixar .txt", data=texto, file_name="passagem_de_caso.txt", mime="text/plain")
        _dialog()
    except Exception:
        st.markdown("<div class='passagem-box'>" + escape_html(texto) + "</div>", unsafe_allow_html=True)
        st.download_button("Baixar .txt", data=texto, file_name="passagem_de_caso.txt", mime="text/plain")

def classificar_idade_gestacional(ig_sem_float: float) -> str:
    if ig_sem_float < 28:
        return "Pré-termo extremo"
    if ig_sem_float < 34:
        return "Pré-termo moderado"
    if ig_sem_float < 37:
        return "Pré-termo tardio"
    if ig_sem_float < 42:
        return "Termo"
    return "Pós-termo"


def render_medicamento(prefix: str, titulo: str, idade_txt: str, peso_kg: float, expanded: bool = True):
    with st.expander(titulo, expanded=expanded):
        opcoes = listar_principios_ativos()
        principio = st.selectbox("Princípio ativo / produto", opcoes, key=f"{prefix}_principio")
        if principio == "Outro/não listado":
            principio_final = st.text_input("Informar princípio ativo/produto", key=f"{prefix}_outro")
            apresentacao_final = st.text_input("Apresentação", key=f"{prefix}_ap_outro")
            via_final = st.selectbox("Via", ["oral", "inalatória", "tópica", "intramuscular", "endovenosa", "subcutânea", "retal", "nasal", "ocular", "outra"], key=f"{prefix}_via_outro")
            disp = {"rename": False, "remume": False, "apresentacoes": []}
        else:
            principio_final = principio
            aps = obter_apresentacoes(principio)
            ap_txts = [a["texto"] for a in aps] or ["Apresentação não cadastrada — preencher manualmente"]
            apresentacao_final = st.selectbox("Apresentação disponível", ap_txts, key=f"{prefix}_ap")
            via_sugerida = next((a.get("via", "") for a in aps if a.get("texto") == apresentacao_final), "")
            via_final = st.text_input("Via de administração", value=via_sugerida, key=f"{prefix}_via")
            disp = checar_medicamento(principio)
            st.caption(f"SUS: {'disponível/identificado' if disp.get('sus') else 'não identificado na base local'}")
        p1,p2 = st.columns(2)
        with p1:
            posologia = st.text_input("Posologia/frequência/duração", key=f"{prefix}_pos")
        with p2:
            indicacao = st.text_input("Indicação/motivo", key=f"{prefix}_ind")
        observacao = st.text_area("Observações", height=55, key=f"{prefix}_obs")
        if principio_final and gerar_orientacao_medicamento_ia and st.button("🔎 Consultar IA/fontes sobre apresentação e segurança", key=f"{prefix}_ia"):
            st.info(gerar_orientacao_medicamento_ia(f"{principio_final} — {apresentacao_final} — via {via_final}", idade_txt, peso_kg, indicacao))
        return {"principio": principio_final, "apresentacao": apresentacao_final, "via": via_final, "posologia": posologia, "indicacao": indicacao, "observacao": observacao, "sus": disp.get("sus")}


def render_lista_medicamentos(prefix: str, titulo: str, idade_txt: str, peso_kg: float, maximo: int = 10):
    st.markdown(f"### {titulo}")
    n = st.number_input(f"Quantidade — {titulo}", 0, maximo, 0, step=1, key=f"{prefix}_n")
    itens = []
    for i in range(int(n)):
        itens.append(render_medicamento(f"{prefix}_{i}", f"{titulo} {i+1}", idade_txt, peso_kg, expanded=True))
    return itens

# =========================
# Render principal
# =========================

tabelas = carregar_tabelas()

st.markdown("<div class='hero'><h1>👶 Puericultura Digital</h1><p>Análise clínica por idade, sexo, crescimento, desenvolvimento, imunizações, suplementação, orientações e passagem de caso.</p></div>", unsafe_allow_html=True)

with st.expander("🧾 Identificação, nascimento e exame físico objetivo", expanded=True):
    st.markdown("### Identificação")
    c1, c2, c3 = st.columns(3)
    with c1:
        sexo = st.selectbox("Sexo", ["Masculino", "Feminino"])
    with c2:
        data_nasc = st.date_input("Data de nascimento", value=date(2023, 1, 1), format="DD/MM/YYYY")
    with c3:
        data_aval = st.date_input("Data da consulta", value=date.today(), format="DD/MM/YYYY")

    st.markdown("### Dados ao nascer")
    n1, n2, n3, n4, n5 = st.columns([1, 1, 1, 1, 1])
    with n1:
        peso_nasc_g = st.number_input("Peso ao nascer (g)", 300, 6500, 3200, step=10)
    with n2:
        estatura_nasc_cm = st.number_input("Estatura ao nascer (cm)", 0.0, 70.0, 0.0, step=0.5)
    with n3:
        pc_nasc_cm = st.number_input("PC ao nascer (cm)", 0.0, 50.0, 0.0, step=0.1)
    with n4:
        ig_sem = st.number_input("IG ao nascer — semanas", 22, 42, 39, step=1)
    with n5:
        ig_dias = st.number_input("IG ao nascer — dias", 0, 6, 0, step=1)
    ap1, ap2 = st.columns(2)
    with ap1:
        apgar1 = st.number_input("Apgar 1º minuto", 0, 10, 0, step=1)
    with ap2:
        apgar5 = st.number_input("Apgar 5º minuto", 0, 10, 0, step=1)
    idade_gest_sem = float(ig_sem) + float(ig_dias) / 7
    prematuro = idade_gest_sem < 37

    st.markdown("### Exame físico — sinais vitais e antropometria atual")
    v1, v2, v3, v4, v5 = st.columns(5)
    with v1:
        temp = st.number_input("Temp. (°C)", 34.0, 42.0, 36.5, step=0.1)
    with v2:
        fc = st.number_input("FC (bpm)", 0, 240, 0, step=1)
    with v3:
        fr = st.number_input("FR (irpm)", 0, 100, 0, step=1)
    with v4:
        spo2 = st.number_input("SpO₂ (%)", 0, 100, 0, step=1)
    with v5:
        pa = st.text_input("PA", value="")
    a1, a2, a3 = st.columns(3)
    with a1:
        peso = st.number_input("Peso atual (kg)", 0.5, 100.0, 10.0, step=0.1)
    with a2:
        estatura = st.number_input("Comprimento/estatura atual (cm)", 30.0, 170.0, 80.0, step=0.5)
    with a3:
        pc = st.number_input("Perímetro cefálico atual (cm)", 20.0, 70.0, 45.0, step=0.1)

idade_dias_cron = max(0, (data_aval - data_nasc).days)
correcao_dias = max(0, int(round((40 - idade_gest_sem) * 7))) if prematuro else 0
idade_dias = max(0, idade_dias_cron - correcao_dias)
idade_meses_float = idade_dias / 30.4375
idade_meses_cron = idade_dias_cron / 30.4375
class_ig = classificar_idade_gestacional(idade_gest_sem)
class_nasc, riscos_nasc = classificar_peso_ig(peso_nasc_g, idade_gest_sem)
imc = peso / ((estatura/100)**2)
res_ant = classificar_antropometria(tabelas, sexo, idade_dias, idade_meses_float, peso, estatura, pc) if tabelas else {}

st.markdown(css(sexo), unsafe_allow_html=True)

st.session_state["passagem_crianca"] = {"sexo": sexo, "data_nascimento": fmt_data(data_nasc), "data_consulta": fmt_data(data_aval), "idade_cronologica": idade_texto(idade_dias_cron), "idade_corrigida": idade_texto(idade_dias)}
st.session_state["passagem_nascimento"] = {"ig": f"{ig_sem}s {ig_dias}d", "classificacao_ig": class_ig, "peso_nascimento": f"{peso_nasc_g:.0f} g", "estatura_nascimento": f"{estatura_nasc_cm:.1f} cm" if estatura_nasc_cm else "não informado", "pc_nascimento": f"{pc_nasc_cm:.1f} cm" if pc_nasc_cm else "não informado", "apgar": f"1º min {apgar1}; 5º min {apgar5}", "classificacao": class_nasc, "riscos": riscos_nasc}

st.markdown(f"""
<div class='top-panel'><b>Resumo fixo da criança</b><br>
<span class='metric-pill'>Sexo: {sexo}</span><span class='metric-pill'>Nascimento: {fmt_data(data_nasc)}</span><span class='metric-pill'>Consulta: {fmt_data(data_aval)}</span>
<span class='metric-pill'>Idade cronológica: {idade_texto(idade_dias_cron)}</span><span class='metric-pill'>Idade corrigida: {idade_texto(idade_dias)}</span>
<span class='metric-pill'>IG: {ig_sem}s {ig_dias}d · {class_ig}</span><span class='metric-pill'>PN: {peso_nasc_g:.0f}g · {class_nasc}</span><span class='metric-pill'>Apgar: {apgar1}/{apgar5}</span>
<span class='metric-pill'>Atual: {peso:.1f}kg · {estatura:.1f}cm · PC {pc:.1f}cm · IMC {imc:.1f}</span></div>
""", unsafe_allow_html=True)

c_ia1, c_ia2, c_ia3 = st.columns([1,1,2])
with c_ia1:
    st.session_state["usar_ia_passagem"] = st.toggle("Usar IA na passagem", value=False)
with c_ia2:
    if st.button("🧾 Gerar passagem de caso", use_container_width=True):
        st.session_state["abrir_passagem_flag"] = True
with c_ia3:
    if diagnostico_ia_configurada:
        diag = diagnostico_ia_configurada()
        st.caption(f"IA: {diag.get('provedor')} · Gemini: {diag.get('gemini_configurada')} · OpenAI: {diag.get('openai_configurada')}")

if tabelas is None:
    st.stop()

faixa, rx = faixa_x_por_idade(idade_meses_float)

tabs = st.tabs(["🩺 Anamnese e exame", "📈 Crescimento", "🧠 Desenvolvimento", "💉 Imunizações", "💊 Ferro e vitaminas", "🩺 Ambulatório", "📝 Orientações"])

with tabs[0]:
    st.subheader("🩺 Anamnese estruturada e exame físico")

    st.markdown("## Anamnese")
    queixa = st.text_area("Queixa principal / História da doença atual", placeholder="Ex.: responsável refere tosse há 3 dias, febre...", height=120)

    st.markdown("### Interrogatório sintomatológico segmentar")
    inter = {}
    cols = st.columns(2)
    for i, (seg, ops) in enumerate(INTERROGATORIO_SEGMENTAR.items()):
        with cols[i % 2]:
            inter[seg] = selecionar_opcoes(seg, ops, key=f"is_{seg}")
    inter_obs = st.text_area("Complemento do interrogatório sintomatológico", height=70)

    meds = render_lista_medicamentos("meduso", "Medicamentos em uso / suplementações profiláticas", idade_texto(idade_dias), peso, maximo=10)

    st.markdown("### Antecedentes maternos, gestacionais e obstétricos")
    g1,g2,g3,g4 = st.columns(4)
    with g1: gestas = st.number_input("Gestações (G)", 0, 20, 1, step=1)
    with g2: partos_normais = st.number_input("Partos normais (PN)", 0, 20, 0, step=1)
    with g3: partos_cesareos = st.number_input("Partos cesáreos (PC)", 0, 20, 0, step=1)
    with g4: abortos = st.number_input("Abortos (A)", 0, 20, 0, step=1)
    paridade = f"G{gestas} PN{partos_normais} PC{partos_cesareos} A{abortos}"

    n_filhos = st.number_input("Número de filhos vivos", 0, 20, 0, step=1)
    filhos = []
    if n_filhos:
        with st.expander("Filhos vivos — sexo e idade", expanded=False):
            for i in range(int(n_filhos)):
                fc1,fc2,fc3 = st.columns([1,1,2])
                with fc1: sx_f = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro/não informado"], key=f"filho_sx_{i}")
                with fc2: idade_f = st.text_input("Idade", key=f"filho_idade_{i}", placeholder="Ex.: 7a; 3m")
                with fc3: obs_f = st.text_input("Observação", key=f"filho_obs_{i}")
                filhos.append({"sexo": sx_f, "idade": idade_f, "observacao": obs_f})

    ant_mat_inf = selecionar_opcoes("Infecções/intercorrências infecciosas maternas", DOENCAS_MATERNAS_INFECCIOSAS, key="ant_mat_inf")
    ant_mat_clin = selecionar_opcoes("Doenças/comorbidades/intercorrências clínicas/obstétricas maternas", DOENCAS_MATERNAS_CLINICAS, key="ant_mat_clin")
    ant_mat_det = {}
    for inf in ant_mat_inf:
        with st.expander(f"Detalhes — {inf}", expanded=False):
            d1,d2,d3 = st.columns(3)
            with d1: trat = st.selectbox("Tratada adequadamente?", ["sim", "não", "parcial", "não sabe"], key=f"inf_trat_{inf}")
            with d2: ctrl = st.selectbox("Controlada/resolvida?", ["sim", "não", "em acompanhamento", "não sabe"], key=f"inf_ctrl_{inf}")
            with d3: reperc = st.selectbox("Repercussão fetal/neonatal?", ["não", "sim", "não sabe"], key=f"inf_rep_{inf}")
            obs = st.text_input("Observação", key=f"inf_obs_{inf}")
            ant_mat_det[inf] = {"tratada": trat, "controlada": ctrl, "repercussao": reperc, "observacao": obs}
    for cond in ant_mat_clin:
        with st.expander(f"Controle/observação — {cond}", expanded=False):
            ctrl = st.selectbox("Controle durante a gestação", ["adequado", "parcial", "inadequado", "não sabe"], key=f"clin_ctrl_{cond}")
            obs = st.text_input("Observação", key=f"clin_obs_{cond}")
            ant_mat_det[cond] = {"controle": ctrl, "observacao": obs}

    meds_gest = render_lista_medicamentos("medgest", "Medicamentos maternos usados na gestação", idade_texto(idade_dias), peso, maximo=8)
    sups_gest = render_lista_medicamentos("supgest", "Suplementações maternas na gestação", idade_texto(idade_dias), peso, maximo=6)
    vac_gest = selecionar_opcoes("Vacinação na gestação", VACINAS_GESTACAO, key="vac_gest")
    vac_gest_obs = st.text_input("Observações sobre vacinação gestacional")

    st.markdown("### Antecedentes perinatais e triagens neonatais")
    ant_peri = selecionar_opcoes("Intercorrências perinatais/neonatais", INTERCORRENCIAS_PERINATAIS, key="ant_peri")
    peri_det = {}
    campos_peri = {
        "internação neonatal": "Internação neonatal: motivo e duração",
        "UTI neonatal": "UTI neonatal: motivo e duração",
        "fototerapia": "Fototerapia: motivo/duração",
        "antibiótico neonatal": "Antibiótico neonatal: qual/motivo/duração",
        "reanimação neonatal": "Reanimação: passos necessários e resposta",
        "desconforto respiratório": "Desconforto respiratório: suporte usado e duração",
        "transfusão": "Transfusão: tipo/motivo",
    }
    for item, label in campos_peri.items():
        if item in ant_peri:
            peri_det[item] = st.text_input(label, key=f"peri_{item}")
    triagens = {}
    tcols = st.columns(3)
    for i, (teste, ops) in enumerate(TRIAGENS_NEONATAIS.items()):
        with tcols[i % 3]:
            val = st.selectbox(teste, ops, key=f"triagem_{teste}")
            triagens[teste] = val
            if val not in ("normal", "não sabe informar"):
                triagens[teste + " — detalhe"] = st.text_input(f"Detalhe: {teste}", key=f"triagem_det_{teste}")

    st.markdown("### Antecedentes patológicos e familiares")
    ant_pat = selecionar_opcoes("Antecedentes patológicos", ANTECEDENTES_PATOLOGICOS, key="ant_pat")
    det_pat = {}
    for item in ["internações", "cirurgias", "alergias medicamentosas", "alergias alimentares", "convulsões", "transfusões", "acidentes/intoxicações"]:
        if item in ant_pat:
            det_pat[item] = st.text_input(f"Detalhar {item}: motivo, data, duração/procedimento", key=f"det_{item}")
    meds_pat = render_lista_medicamentos("medpat", "Medicamentos já utilizados para antecedentes patológicos", idade_texto(idade_dias), peso, maximo=8)
    ant_fam = selecionar_opcoes("Antecedentes familiares", ANTECEDENTES_FAMILIARES, key="ant_fam")

    st.markdown("### Hábitos de vida")
    hab1,hab2 = st.columns(2)
    with hab1:
        alimentacao = selecionar_opcoes("Alimentação/aleitamento atual", TIPOS_ALEITAMENTO, key="alimentacao")
        # Histórico de AME permanece relevante mesmo após a introdução alimentar,
        # pois influencia a análise de ferro profilático e risco de anemia.
        if idade_meses_cron >= 6:
            historico_ame = st.selectbox("Histórico de AME até 6 meses", HISTORICO_AME[1:], help="Use para saber se a criança recebeu aleitamento materno exclusivo até 6 meses, mesmo que já esteja em alimentação complementar.")
        else:
            historico_ame = st.selectbox("Histórico/condição atual de AME", ["AME em curso", "não está em AME", "não sabe informar"], help="Em menores de 6 meses, indica se o aleitamento materno exclusivo está em curso.")
        lacteo_precoce = ""
        if historico_ame in ("AME interrompido antes de 6 meses", "não esteve em AME", "não está em AME"):
            lacteo_precoce = st.selectbox("Principal substituto lácteo antes dos 6 meses", ALIMENTO_LACTEO_ANTES_6M[1:])
        formula = ""
        if "fórmula infantil exclusiva" in alimentacao or "aleitamento misto" in alimentacao:
            formula = st.text_input("Fórmula atual: marca/tipo, volume, frequência, diluição")
        sono = selecionar_opcoes("Sono", SONO, key="sono")
        telas = selecionar_um("Telas", ["não usa", "uso ocasional", "< 1h/dia", "1–2h/dia", "> 2h/dia", "não informado"], key="telas")
    with hab2:
        fezes = selecionar_opcoes("Fezes — queixas/padrão", PADRAO_FEZES, key="fezes")
        bristol = st.selectbox("Escala de Bristol", BRISTOL_FEZES, format_func=titulo_opcao)
        freq_fezes = st.text_input("Frequência evacuatória", value="0", help="Ex.: 1x/dia, 3x/semana, 5x/dia")
        urina = selecionar_opcoes("Micção/diurese", PADRAO_URINA, key="urina")
        freq_urina = st.text_input("Frequência urinária/diurese", value="0", help="Ex.: 6 fraldas/dia, 5 micções/dia")
        desfralde = selecionar_um("Desfralde/controle esfincteriano", ["não se aplica pela idade", "não iniciado", "em treinamento", "diurno adquirido", "diurno e noturno adquiridos", "regressão/perdas"], key="desfralde")
        atividade = st.text_input("Atividade física/brincadeiras/creche/escola")
    ame_adequado_para_ferro = (historico_ame in ("esteve em AME até 6 meses", "AME em curso"))
    fatores_alimentares_anemia_auto = []
    if lacteo_precoce in ("leite de vaca", "leite de cabra/outro leite animal", "misto com leite de vaca"):
        fatores_alimentares_anemia_auto.append("leite animal antes de 6 meses/antes de 12 meses")
    elif historico_ame in ("AME interrompido antes de 6 meses", "não esteve em AME", "não está em AME"):
        fatores_alimentares_anemia_auto.append("AME ausente/interrompido antes de 6 meses — avaliar dieta/fórmula fortificada")

    st.markdown("### Condições socioeconômicas")
    socio = selecionar_opcoes("Condições socioeconômicas/moradia", CONDICOES_MORADIA, key="socio")
    sc1,sc2,sc3 = st.columns(3)
    with sc1: tipo_casa = st.selectbox("Tipo de moradia", ["não informado", "casa", "apartamento", "cômodo", "zona rural", "outro"])
    with sc2: comodos = st.number_input("Número de cômodos", 0, 20, 0, step=1)
    with sc3: moradores = st.number_input("Número de moradores", 0, 30, 0, step=1)
    animais = st.text_input("Animais domésticos")
    coabit = st.text_input("Coabitantes/cuidadores principais")

    st.markdown("## Exame físico")
    geral = selecionar_opcoes(
        "Geral / ectoscopia",
        ECTOSCOPIA,
        key="geral_ectoscopia",
        default=["bom estado geral", "ativo e reativo", "hidratado", "corado", "acianótico", "anicterico", "eupneico"],
    )
    geral_obs = st.text_area("Descrição geral", value="Criança em bom estado geral, ativa e reativa, hidratada, corada, acianótica, anictérica e eupneica ao exame.", height=70)

    pele_dict = {}
    with st.expander("Pele e fâneros", expanded=False):
        pele = selecionar_opcoes("Achados de pele/fâneros", EXAME_PELE_FANEROS, key="pele_faneros")
        pele_obs = st.text_area("Descrição — pele e fâneros", value="Pele íntegra, sem lesões elementares relevantes, sem petéquias/equimoses, fâneros sem alterações aparentes.", height=70)
        pele_dict = {"achados": pele, "obs": pele_obs}

    pesco = {}
    with st.expander("Cabeça e pescoço", expanded=False):
        st.markdown("#### Fontanelas")
        f1, f2 = st.columns(2)
        with f1:
            font_ant_status = st.selectbox("Fontanela anterior", ["aberta normotensa", "fechada", "abaulada", "deprimida", "fechamento precoce suspeito"], key="font_ant", format_func=titulo_opcao)
            font_ant_tam = st.number_input("Abertura FA — maior diâmetro (cm)", 0.0, 10.0, 0.0, step=0.1, key="font_ant_tam")
        with f2:
            font_post_status = st.selectbox("Fontanela posterior", ["fechada", "aberta normotensa", "abaulada", "deprimida"], key="font_post", format_func=titulo_opcao)
            font_post_tam = st.number_input("Abertura FP — maior diâmetro (cm)", 0.0, 5.0, 0.0, step=0.1, key="font_post_tam")
        if "aberta" in font_ant_status and idade_meses_cron > 18:
            st.warning("Fontanela anterior aberta após ~18 meses: correlacionar com crescimento craniano, exame físico e contexto clínico.")
        if "aberta" in font_post_status and idade_meses_cron > 3:
            st.warning("Fontanela posterior aberta após ~2–3 meses: avaliar contexto clínico e desenvolvimento craniano.")
        font_obs = st.text_area("Descrição — fontanelas", value="Fontanela anterior normotensa quando aberta; fontanela posterior fechada ou sem alterações para a idade.", height=60)
        pesco["Fontanelas"] = {"anterior": font_ant_status, "tamanho_anterior_cm": font_ant_tam, "posterior": font_post_status, "tamanho_posterior_cm": font_post_tam, "obs": font_obs}

        st.markdown("#### Crânio")
        cranio = selecionar_opcoes("Formato/achados cranianos", CABECA_PESCOCO.get("Crânio", []), key="cranio")
        cranio_obs = st.text_area("Descrição — crânio", value="Crânio normocéfalo, sem deformidades aparentes relevantes.", height=60)
        pesco["Crânio"] = {"achados": cranio, "obs": cranio_obs}

        st.markdown("#### Linfonodos")
        regioes_linfo = ["Occipital", "Pré-auricular", "Retroauricular", "Submandibular", "Submentoniana", "Cervical anterior", "Cervical posterior", "Supraclavicular", "Infraclavicular", "Axilar", "Epitroclear"]
        with popover_ou_expander("📍 Localizações anatômicas dos linfonodos", expanded=False):
            st.caption("Selecione as cadeias palpáveis. Visual anatômico interativo 3D pode ser acoplado futuramente por asset/HTML; aqui fica a seleção estruturada estável no Streamlit.")
            linfo_loc = selecionar_opcoes("Cadeias acometidas", regioes_linfo, key="linfo_loc", cols=3)
        lc1, lc2, lc3 = st.columns(3)
        with lc1:
            linfo_qtd = st.number_input("Quantidade aproximada", 0, 50, 0, step=1, key="linfo_qtd")
        with lc2:
            linfo_tam = st.number_input("Maior tamanho (cm)", 0.0, 10.0, 0.0, step=0.1, key="linfo_tam")
        with lc3:
            linfo_lado = st.selectbox("Lateralidade", ["não se aplica", "direita", "esquerda", "bilateral"], key="linfo_lado", format_func=titulo_opcao)
        linfo_carac = selecionar_opcoes("Características", ["amolecido", "endurecido", "móvel", "fixo", "único", "múltiplos", "coalescente", "doloroso", "indolor", "com sinais flogísticos", "sem sinais flogísticos"], key="linfo_carac", cols=3)
        linfo_obs = st.text_area("Descrição — linfonodos", value="Sem linfonodomegalias palpáveis clinicamente relevantes.", height=60)
        pesco["Linfonodos"] = {"localizacoes": linfo_loc, "quantidade": linfo_qtd, "maior_tamanho_cm": linfo_tam, "lateralidade": linfo_lado, "caracteristicas": linfo_carac, "obs": linfo_obs}

        st.markdown("#### Oftalmoscopia / olhos")
        olhos = {}
        oc1, oc2 = st.columns(2)
        with oc1:
            olhos["reflexo_vermelho"] = st.selectbox("Reflexo vermelho", ["presente e simétrico bilateralmente", "alterado", "assimétrico", "não avaliado"], key="olho_reflexo", format_func=titulo_opcao)
            olhos["conjuntivas"] = st.selectbox("Conjuntivas", ["coradas", "hipocoradas", "hiperemiadas", "ictéricas"], key="olho_conj", format_func=titulo_opcao)
            olhos["pupilas"] = st.selectbox("Pupilas", ["isocóricas e fotorreagentes", "anisocoria", "fotorreação alterada", "não avaliado"], key="olho_pup", format_func=titulo_opcao)
        with oc2:
            olhos["motricidade_ocular"] = st.selectbox("Motricidade ocular/alinhamento", ["sem alterações aparentes", "estrabismo suspeito", "nistagmo", "alteração de seguimento visual"], key="olho_mot", format_func=titulo_opcao)
            olhos["secrecao"] = st.selectbox("Secreção/lacrimejamento", ["ausente", "secreção ocular", "lacrimejamento", "fotofobia"], key="olho_sec", format_func=titulo_opcao)
            olhos["fundoscopia"] = st.text_input("Fundoscopia/observação", value="Sem alterações aparentes quando avaliado.", key="olho_fundo")
        pesco["Oftalmoscopia/olhos"] = olhos

        st.markdown("#### Rinoscopia")
        rino = {}
        rc1, rc2 = st.columns(2)
        with rc1:
            rino["nariz"] = st.selectbox("Nariz", ["sem deformidades", "obstrução nasal", "batimento de asa nasal", "lesão externa"], key="rino_nariz", format_func=titulo_opcao)
            rino["septo"] = st.selectbox("Septo nasal", ["centralizado", "desvio septal suspeito", "lesão/crosta", "não avaliado"], key="rino_septo", format_func=titulo_opcao)
        with rc2:
            rino["cornetos"] = st.selectbox("Cornetos/mucosa", ["sem edema relevante", "edemaciados", "pálidos", "hiperemiados"], key="rino_cornetos", format_func=titulo_opcao)
            rino["muco"] = st.selectbox("Muco/secreção", ["ausente", "hialino", "purulento", "sanguinolento"], key="rino_muco", format_func=titulo_opcao)
        rino["obs"] = st.text_area("Descrição — rinoscopia", value="Rinoscopia anterior sem alterações relevantes; sem secreção patológica evidente.", height=60)
        pesco["Rinoscopia"] = rino

        st.markdown("#### Oroscopia")
        oro = {}
        denticoes = ["não se aplica/sem dentes", "decídua", "mista", "permanente"]
        o1, o2 = st.columns(2)
        with o1:
            oro["lábios"] = st.text_input("Lábios", value="Íntegros, sem lesões.")
            oro["mucosa_jugal"] = st.text_input("Mucosa jugal", value="Úmida, corada, sem lesões.")
            oro["denticao"] = st.selectbox("Dentição", denticoes, key="denticao", format_func=titulo_opcao)
            oro["palato"] = st.text_input("Palato", value="Íntegro, sem alterações aparentes.")
        with o2:
            oro["língua"] = st.text_input("Língua", value="Sem alterações aparentes.")
            oro["tonsilas_amigdalas"] = st.text_input("Tonsilas/amígdalas", value="Sem hipertrofia importante, sem exsudato.")
            oro["orofaringe"] = st.text_input("Orofaringe", value="Sem hiperemia ou exsudato.")
        with popover_ou_expander("🦷 Mapa dental estruturado", expanded=False):
            st.caption("Selecione dentes/regiões com alteração. Um mapa 3D real pode ser acoplado futuramente por imagem/HTML; esta versão mantém registro estruturado e estável.")
            dentes_deciduos = ["55", "54", "53", "52", "51", "61", "62", "63", "64", "65", "85", "84", "83", "82", "81", "71", "72", "73", "74", "75"]
            dentes_perm = ["18", "17", "16", "15", "14", "13", "12", "11", "21", "22", "23", "24", "25", "26", "27", "28", "48", "47", "46", "45", "44", "43", "42", "41", "31", "32", "33", "34", "35", "36", "37", "38"]
            dentes_lista = dentes_deciduos if oro["denticao"] == "decídua" else (dentes_deciduos + dentes_perm if oro["denticao"] == "mista" else dentes_perm)
            dentes_alt = selecionar_opcoes("Dentes com alteração", dentes_lista, key="dentes_alt", cols=5)
            alteracoes_dent = selecionar_opcoes("Tipo de alteração dental", ["cárie", "fratura", "sangramento gengival", "mobilidade", "mancha", "ausência", "dor", "má oclusão"], key="alt_dental", cols=3)
            oro["dentes_alterados"] = dentes_alt
            oro["alteracoes_dentarias"] = alteracoes_dent
        pesco["Oroscopia"] = oro

        st.markdown("#### Otoscopia")
        oto = {}
        ot1, ot2 = st.columns(2)
        with ot1:
            oto["pavilhao_direito"] = st.selectbox("Pavilhão auricular direito", ["sem alterações", "malformação", "dor à mobilização", "lesão"], key="oto_pd", format_func=titulo_opcao)
            oto["meato_direito"] = st.selectbox("Meato/canal direito", ["pérvio", "cerume", "edema", "otorreia", "corpo estranho"], key="oto_md", format_func=titulo_opcao)
            oto["mt_direita"] = st.selectbox("Membrana timpânica direita", ["íntegra e translúcida", "hiperemiada", "opaca", "abaulada", "perfurada", "não visualizada"], key="oto_mtd", format_func=titulo_opcao)
        with ot2:
            oto["pavilhao_esquerdo"] = st.selectbox("Pavilhão auricular esquerdo", ["sem alterações", "malformação", "dor à mobilização", "lesão"], key="oto_pe", format_func=titulo_opcao)
            oto["meato_esquerdo"] = st.selectbox("Meato/canal esquerdo", ["pérvio", "cerume", "edema", "otorreia", "corpo estranho"], key="oto_me", format_func=titulo_opcao)
            oto["mt_esquerda"] = st.selectbox("Membrana timpânica esquerda", ["íntegra e translúcida", "hiperemiada", "opaca", "abaulada", "perfurada", "não visualizada"], key="oto_mte", format_func=titulo_opcao)
        oto["obs"] = st.text_area("Descrição — otoscopia", value="Pavilhões auriculares sem alterações; condutos auditivos pérvios; membranas timpânicas íntegras, translúcidas e sem abaulamento quando visualizadas.", height=60)
        pesco["Otoscopia"] = oto

    resp = {}; cardio = {}; abd = {}
    with st.expander("Respiratório", expanded=False):
        cols = st.columns(2)
        for i, (sec, ops) in enumerate(EXAME_RESPIRATORIO.items()):
            with cols[i % 2]:
                resp[sec] = selecionar_opcoes(sec, ops, key=f"resp_{sec}")
        resp["descrição"] = st.text_area("Descrição respiratória", value="Tórax sem deformidades, expansibilidade preservada, som claro pulmonar e murmúrio vesicular presente bilateralmente, sem ruídos adventícios.", height=70)
    with st.expander("Cardiovascular", expanded=False):
        for sec, ops in EXAME_CARDIO.items():
            cardio[sec] = selecionar_opcoes(sec, ops, key=f"cardio_{sec}")
        cardio["descrição"] = st.text_area("Descrição cardiovascular", value="Ritmo cardíaco regular em dois tempos, bulhas normofonéticas, sem sopros audíveis; pulsos periféricos palpáveis e perfusão adequada.", height=70)
    with st.expander("Abdominal", expanded=False):
        cols = st.columns(2)
        for i, (sec, ops) in enumerate(EXAME_ABDOMINAL.items()):
            with cols[i % 2]:
                abd[sec] = selecionar_opcoes(sec, ops, key=f"abd_{sec}")
        abd["descrição"] = st.text_area("Descrição abdominal", value="Abdome plano ou globoso conforme biotipo, flácido, indolor à palpação, sem visceromegalias ou massas palpáveis; ruídos hidroaéreos presentes.", height=70)
    with st.expander("Genitália", expanded=False):
        gc1, gc2, gc3 = st.columns(3)
        with gc1:
            gen_tipo = st.selectbox("Caracterização", ["típica feminina", "típica masculina", "atípica/ambígua", "não avaliada"], key="gen_tipo", format_func=titulo_opcao)
        with gc2:
            gen_pelos = st.selectbox("Pilificação pubiana", ["ausente", "presente", "não avaliada"], key="gen_pelos", format_func=titulo_opcao)
        with gc3:
            tanner = st.selectbox("Tanner", ["G1/P1", "G2/P2", "G3/P3", "G4/P4", "G5/P5", "M1/P1", "M2/P2", "M3/P3", "M4/P4", "M5/P5", "não se aplica/não avaliado"], key="tanner")
        genitalia = selecionar_opcoes("Achados de genitália", EXAME_GENITALIA, key="genitalia")
        genitalia_obs = st.text_area("Descrição — genitália", value="Genitália externa típica para sexo informado, sem lesões, secreções ou sinais inflamatórios aparentes; pilificação compatível com idade quando aplicável.", height=70)
    with st.expander("Osteomuscular / extremidades", expanded=False):
        axial = selecionar_opcoes("Esqueleto axial / coluna", ["sem desvios aparentes", "cifose", "lordose acentuada", "escoliose suspeita", "dor à palpação", "limitação de mobilidade"], key="osteo_axial")
        apendicular = selecionar_opcoes("Esqueleto apendicular / membros", EXAME_OSTEOMUSCULAR, key="osteo_apendicular")
        osteo = {"axial": axial, "apendicular": apendicular}
        osteo_obs = st.text_area("Descrição — osteomuscular", value="Coluna sem desvios aparentes; membros sem deformidades, assimetrias ou limitação de mobilidade; marcha compatível com a idade quando aplicável.", height=70)
    with st.expander("Neurológico e reflexos", expanded=False):
        sentidos = selecionar_opcoes("Sentidos / responsividade sensorial", ["visão aparentemente preservada", "audição aparentemente preservada", "responde a estímulos sonoros", "fixa e acompanha objetos", "alteração visual suspeita", "alteração auditiva suspeita"], key="neuro_sentidos")
        marcha = st.selectbox("Marcha", ["não se aplica pela idade", "adequada para idade", "alterada", "claudicante", "atáxica", "não avaliada"], key="neuro_marcha", format_func=titulo_opcao)
        neuro = selecionar_opcoes("Achados neurológicos", EXAME_NEUROLOGICO, key="neuro")
        reflexos = selecionar_opcoes("Reflexos primitivos — RN/lactente", REFLEXOS_PRIMITIVOS, key="reflexos", cols=1)
        marcos_auto = st.session_state.get("passagem_desenvolvimento", {}).get("marcos_presentes", [])
        st.caption("Marcos do desenvolvimento assinalados na aba Desenvolvimento serão incorporados automaticamente à passagem.")
        neuro_obs = st.text_area("Descrição — neurológico/reflexos", value="Criança alerta e interativa, tônus e força globalmente preservados, sem assimetrias motoras evidentes; reflexos e marcha compatíveis com idade quando aplicável.", height=70)
    st.markdown("### Exames complementares")
    n_exames = st.number_input("Número de exames complementares", 0, 12, 0, step=1)
    exames_comp = []
    for i in range(int(n_exames)):
        with st.expander(f"Exame complementar {i+1}", expanded=False):
            e1,e2,e3 = st.columns([1.5,1,1])
            with e1: tipo_ex = st.selectbox("Tipo de exame", list(EXAMES_COMPLEMENTARES_MODELOS.keys()), key=f"ex_tipo_{i}")
            with e2: data_ex = st.date_input("Data", value=data_aval, format="DD/MM/YYYY", key=f"ex_data_{i}")
            with e3: status_ex = st.selectbox("Interpretação", ["normal", "alterado", "pendente", "não avaliado"], key=f"ex_status_{i}")
            params = {}
            pcols = st.columns(2)
            for j, param in enumerate(EXAMES_COMPLEMENTARES_MODELOS.get(tipo_ex, [])):
                with pcols[j % 2]: params[param] = st.text_input(param, key=f"ex_{i}_{param}")
            alerta_ex = ""
            if status_ex == "alterado":
                alerta_ex = st.text_area("Alerta/conduta complementar por alteração", key=f"ex_alerta_{i}", height=70)
            exames_comp.append({"tipo": tipo_ex, "data": fmt_data(data_ex), "status": status_ex, "parametros": params, "alerta": alerta_ex})

    consulta_dados = {
        "queixa_hda": queixa, "interrogatorio": {**inter, "complemento": inter_obs}, "medicamentos_uso": meds,
        "paridade": paridade, "filhos": {"numero": n_filhos, "lista": filhos},
        "antecedentes_maternos": {"infecciosos": ant_mat_inf, "clinicos_obstetricos": ant_mat_clin, "detalhes": ant_mat_det},
        "medicamentos_gestacao": meds_gest, "suplementacoes_gestacao": sups_gest, "vacinacao_gestacao": {"selecionadas": vac_gest, "obs": vac_gest_obs},
        "antecedentes_perinatais": {"selecionados": ant_peri, "detalhes": peri_det}, "triagens_neonatais": triagens,
        "antecedentes_patologicos": {"selecionados": ant_pat, "detalhes": det_pat, "medicamentos_previos": meds_pat}, "antecedentes_familiares": ant_fam,
        "habitos": {"alimentacao_atual": alimentacao, "historico_ame": historico_ame, "substituto_lacteo_precoce": lacteo_precoce, "formula": formula, "sono": sono, "telas": telas, "fezes": fezes, "frequencia_fezes": freq_fezes, "bristol": bristol, "urina": urina, "frequencia_urina": freq_urina, "desfralde": desfralde, "atividade": atividade},
        "socioeconomico": {"moradia": socio, "tipo_casa": tipo_casa, "comodos": comodos, "moradores": moradores, "animais": animais, "coabitantes": coabit},
    }
    exame_dados = {"sinais_vitais": f"T {temp:.1f}°C; FC {fc} bpm; FR {fr} irpm; SpO₂ {spo2}%; PA {pa or 'não aferida'}", "antropometria": f"Peso {peso:.1f} kg; estatura {estatura:.1f} cm; PC {pc:.1f} cm; IMC {imc:.1f}", "geral": {"achados": geral, "obs": geral_obs}, "pele_faneros": pele_dict, "cabeca_pescoco": pesco, "respiratorio": resp, "cardiovascular": cardio, "abdominal": abd, "genitalia": {"caracterizacao": gen_tipo, "pilificacao": gen_pelos, "tanner": tanner, "achados": genitalia, "obs": genitalia_obs}, "osteomuscular": {"achados": osteo, "obs": osteo_obs}, "neurologico": {"sentidos": sentidos, "marcha": marcha, "achados": neuro, "reflexos": reflexos, "marcos_auto": marcos_auto, "obs": neuro_obs}, "exames_complementares": exames_comp}
    st.session_state["passagem_consulta"] = consulta_dados
    st.session_state["passagem_exame"] = exame_dados

with tabs[1]:
    st.subheader("📈 Crescimento antropométrico")
    st.caption("Antropometria integrada ao exame físico; aqui aparecem as curvas, z-scores, percentis e classificação.")
    growth_summaries = []
    stabs = st.tabs(["⚖️ Peso", "📏 Estatura", "🧮 IMC", "🧠 PC"])
    cfg = [("Peso","Peso/idade","kg",peso,faixa,rx),("Estatura","Comprimento/estatura por idade","cm",estatura,faixa,rx),("IMC","IMC/idade","kg/m²",imc,faixa,rx),("PC","Perímetro cefálico/idade","cm",pc,"0 a 2 anos",[0,24])]
    for tab,(param,titulo,unidade,valor,fx,r_x) in zip(stabs,cfg):
        with tab:
            if param == "PC" and idade_meses_float > 24:
                st.info("Perímetro cefálico rotineiro em gráfico até 2 anos; medida pode ser registrada conforme contexto clínico.")
                continue
            resumo = plotar_crescimento(tabelas[sexo][param], param, titulo, unidade, valor, idade_dias, idade_meses_float, fx, r_x)
            growth_summaries.append(resumo)
    st.session_state["passagem_crescimento"] = {"resumos": [f"{r['titulo']}: {r['classificacao']} (Z {r['z']}, P{r['percentil']})" for r in growth_summaries]}

with tabs[2]:
    st.subheader("🧠 Desenvolvimento neuropsicomotor")
    atual, anterior, proxima, todas = obter_marcos_vigilancia(idade_meses_float, prematuro)
    st.markdown("<div class='timeline'>" + "".join(f"<div class='timeline-card {'current' if f['faixa']==atual['faixa'] else ''}'><span class='timeline-dot'></span><b>{f['faixa']}</b><br><span class='small-muted'>{'faixa atual' if f['faixa']==atual['faixa'] else 'vigilância'}</span></div>" for f in todas) + "</div>", unsafe_allow_html=True)
    status_anterior=[]; presentes=[]; pendentes=[]
    if anterior:
        st.markdown(f"<div class='dev-instruction'><b>Confirmar faixa anterior: {anterior['faixa']}</b><br>{anterior['avaliacao']}</div>", unsafe_allow_html=True)
        for area, marco in anterior["marcos"]:
            cols=st.columns([1.2,3,2]); cols[0].markdown(f"**{area}**"); cols[1].write(marco)
            stt=cols[2].radio("Status", ["Presente","Ausente","Não verificado"], horizontal=True, key=f"ant_{area}_{marco}", label_visibility="collapsed")
            status_anterior.append(stt); (presentes if stt=="Presente" else pendentes).append(f"{area}: {marco} ({stt})")
    st.markdown(f"<div class='dev-instruction'><b>Faixa atual: {atual['faixa']}</b><br>{atual['avaliacao']}</div>", unsafe_allow_html=True)
    img_dev = imagem_desenvolvimento_por_faixa(atual["faixa"])
    if img_dev and Path(img_dev).exists(): st.image(img_dev, caption=f"Imagem de apoio — {atual['faixa']}", use_container_width=True)
    status_atual=[]
    for area, marco in atual["marcos"]:
        cols=st.columns([1.2,3,2]); cols[0].markdown(f"**{area}**"); cols[1].write(marco)
        stt=cols[2].radio("Status", ["Presente","Ausente","Não verificado"], horizontal=True, key=f"atu_{area}_{marco}", label_visibility="collapsed")
        status_atual.append(stt); (presentes if stt=="Presente" else pendentes).append(f"{area}: {marco} ({stt})")
    fatores_dev = selecionar_opcoes("Fatores de risco para desenvolvimento", ["Prematuridade", "Baixo peso ao nascer", "Internação neonatal prolongada", "Asfixia/hipóxia", "Infecção congênita", "Alteração auditiva/visual", "Vulnerabilidade social", "Suspeita de TEA ou regressão"], key="fatores_dev", default=["Prematuridade"] if prematuro else [])
    clas_dev, texto_dev, cor_dev = classificar_desenvolvimento(status_atual, status_anterior, fatores_dev)
    st.markdown(f"<div class='result-card' style='--result-color:{cor_dev};'><div><span class='result-label'>Síntese</span><h3>{clas_dev}</h3></div><div class='result-metrics'>{texto_dev}</div></div>", unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1: st.markdown("<div class='soft-card'><div class='soft-title'>🎯 Se houver atraso/ausência</div><ul><li>Iniciar estimulação imediatamente.</li><li>Reavaliar em curto prazo e considerar equipe multiprofissional.</li><li>Investigar audição, visão, interação, tônus, assimetrias, sono e contexto familiar.</li></ul></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='soft-card'><div class='soft-title'>🚀 Próximos marcos — {(proxima or atual)['faixa']}</div>{html_lista((proxima or atual)['proxima'])}</div>", unsafe_allow_html=True)
    st.session_state["passagem_desenvolvimento"] = {"resumo": f"{clas_dev}. {texto_dev}", "presentes": presentes, "pendentes": pendentes, "fatores": fatores_dev}

with tabs[3]:
    st.subheader("💉 Imunizações")
    atrasadas, proximas = render_mapa_vacinal(idade_meses_float)
    c1,c2=st.columns(2)
    with c1: st.markdown("<div class='risk-box'><div class='soft-title'>🚨 Vacinas atrasadas/pendentes</div>" + html_lista(atrasadas) + "</div>", unsafe_allow_html=True)
    with c2: st.markdown("<div class='risk-box'><div class='soft-title'>📅 Próximas imunizações</div>" + html_lista(proximas[:12]) + "</div>", unsafe_allow_html=True)
    st.session_state["passagem_vacinas"] = {"atrasadas": atrasadas, "proximas": proximas[:12]}

with tabs[4]:
    st.subheader("💊 Ferro profilático e vitaminas")
    riscos = fatores_risco_anemia()
    c1,c2=st.columns(2)
    with c1: fat_maternos = selecionar_opcoes("Fatores maternos/gestacionais para anemia", riscos["maternos_gestacionais"], key="fat_maternos_anemia")
    with c2:
        defaults=[]
        if prematuro: defaults.append("Prematuridade")
        if peso_nasc_g < 2500: defaults.append("Baixo peso ao nascer (< 2.500 g)")
        fat_crianca_sel = selecionar_opcoes("Fatores da criança para anemia", riscos["crianca"], key="fat_crianca_anemia", default=defaults)
    fat_crianca = list(dict.fromkeys(list(fat_crianca_sel) + fatores_alimentares_anemia_auto))
    if fatores_alimentares_anemia_auto:
        st.warning("Fator alimentar acrescentado automaticamente à análise de anemia/ferro: " + "; ".join(fatores_alimentares_anemia_auto))
    rec = recomendacao_ferro(idade_meses_float, peso, peso_nasc_g, idade_gest_sem, ame_adequado_para_ferro, fat_crianca, fat_maternos)
    st.markdown(f"<div class='result-card' style='--result-color:#0f766e;'><div><span class='result-label'>Ferro</span><h3>{rec['protocolo']}</h3></div><div class='result-metrics'>{rec['resumo']}<br><b>{rec['dose_mg_dia']:.1f} mg/dia</b></div></div>", unsafe_allow_html=True)
    st.info(rec["conduta"])
    sais = obter_sais_ferro(); sal_nome = st.selectbox("Apresentação do sal de ferro", list(sais.keys())); duracao = st.selectbox("Duração", ["90 dias","30 dias","60 dias","até a próxima consulta"]); ap=sais[sal_nome]; calc=calcular_apresentacao_ferro(rec["dose_mg_dia"], ap)
    st.markdown(f"<div class='soft-card'><div class='soft-title'>🧮 Cálculo</div><b>{calc['texto']}</b><br><span class='small-muted'>{ap['marcas']} · {ap['obs']}</span></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='prescricao'>{modelo_prescricao_ferro(rec['dose_mg_dia'], sal_nome, ap, calc, duracao)}</div>", unsafe_allow_html=True)
    st.markdown("### Vitamina A — PNSVA/MS")
    va1,va2,va3=st.columns(3)
    with va1: regiao_va=st.checkbox("Região prioritária?", help="Norte, Nordeste, Centro-Oeste, Vale do Jequitinhonha, Vale do Mucuri, Vale do Ribeira ou Norte de Minas.")
    with va2: cad_va=st.checkbox("CadÚnico?")
    with va3: dsei_va=st.checkbox("DSEI?")
    vit_a=calcular_vitamina_a_pnsva(idade_meses_float, regiao_va, cad_va, dsei_va)
    st.markdown(f"<div class='soft-card'><div class='soft-title'>Vitamina A</div><b>{'Indicada' if vit_a['indicada'] else 'Conferir critérios/não automática'}</b><p>Dose: {vit_a['dose']} · {vit_a.get('cor_capsula','—')} · {vit_a['frequencia']}</p><p>{vit_a['orientacao']}</p><p class='small-muted'>{vit_a['alerta']}</p></div>", unsafe_allow_html=True)
    st.markdown("### Vitamina D e B12")
    fat_d=selecionar_opcoes("Fatores de risco para hipovitaminose D", fatores_risco_hipovitaminose_d(), key="fat_vitd", default=["Prematuridade"] if prematuro else [])
    vit_d=calcular_vitamina_d_sbp(idade_meses_float, peso, prematuro, peso_nasc_g, fat_d)
    fat_b12=selecionar_opcoes("Fatores de risco para deficiência de B12", fatores_risco_vitamina_b12(), key="fat_b12")
    st.markdown(f"<div class='soft-card'><div class='soft-title'>Vitamina D</div><p><b>Dose:</b> {vit_d['dose']}</p><p>{vit_d['orientacao']}</p><div class='prescricao'>{vit_d['prescricao']}</div></div>", unsafe_allow_html=True)
    st.session_state["passagem_suplementacao"] = {"resumo": [f"Ferro: {rec['protocolo']} — {rec['resumo']} — {rec['dose_mg_dia']:.1f} mg/dia", f"Vitamina A: {vit_a['dose']} — {'indicada' if vit_a['indicada'] else 'conferir critérios'}", f"Vitamina D: {vit_d['dose']}", f"B12: {'risco presente' if fat_b12 else 'sem fatores de risco selecionados'}"], "fatores_risco": {"anemia_crianca": fat_crianca, "anemia_maternos": fat_maternos, "vitamina_d": fat_d, "b12": fat_b12}, "historico_ame": historico_ame, "substituto_lacteo_precoce": lacteo_precoce}

with tabs[5]:
    st.subheader("🩺 Protocolos ambulatoriais")
    if obter_protocolos_ambulatoriais:
        protos = obter_protocolos_ambulatoriais(); nome = st.selectbox("Protocolo", list(protos.keys()))
        respostas = {}
        for campo in campos_do_protocolo(nome):
            cid=campo.get("id"); label=campo.get("label", cid); tipo=campo.get("tipo", "text"); ops=campo.get("opcoes", [])
            if tipo == "checkbox": respostas[cid] = st.checkbox(label, key=f"proto_{nome}_{cid}")
            elif tipo == "select": respostas[cid] = st.selectbox(label, ops, key=f"proto_{nome}_{cid}")
            elif tipo == "multiselect": respostas[cid] = selecionar_opcoes(label, ops, key=f"proto_{nome}_{cid}")
            elif tipo == "number": respostas[cid] = st.number_input(label, value=campo.get("value",0), key=f"proto_{nome}_{cid}")
            else: respostas[cid] = st.text_input(label, key=f"proto_{nome}_{cid}")
        res = executar_protocolo(nome, respostas, {"idade_meses":idade_meses_float,"peso":peso})
        st.markdown(f"<div class='soft-card'><div class='soft-title'>Classificação</div>{res.get('classificacao','—')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='prescricao'>{res.get('prescricao','Sem prescrição automática.')}</div>", unsafe_allow_html=True)
        meds_proto = render_lista_medicamentos("proto_meds", "Medicamentos efetivamente prescritos/orientados neste protocolo", idade_texto(idade_dias), peso, maximo=8)
        st.markdown("<div class='soft-card'><div class='soft-title'>Orientações</div>" + html_lista(res.get('orientacoes', [])) + "</div>", unsafe_allow_html=True)
        st.session_state["passagem_ambulatorio"] = {"protocolo": nome, "classificacao": res.get("classificacao"), "conduta_resumo": safe_join(res.get("conduta", res.get("orientacoes", []))), "prescricao": res.get("prescricao"), "medicamentos": meds_proto}
    else:
        st.info("Arquivo protocolos_ambulatoriais.py não carregado.")

with tabs[6]:
    st.subheader("📝 Orientações por idade e achados")
    for bloco in obter_orientacoes_detalhadas(idade_meses_float, prematuro):
        st.markdown(f"<div class='soft-card'><div class='soft-title'>{bloco['icone']} {bloco['titulo']}</div>{html_lista(bloco['itens'])}<p class='small-muted'><b>Conduta/orientação:</b> {bloco['conduta']}</p></div>", unsafe_allow_html=True)

# Plano sugestivo básico para passagem
plano = []
qc = st.session_state.get("passagem_consulta", {}).get("queixa_hda", "")
if qc:
    plano.append("conduzir queixa principal conforme hipótese clínica e protocolo selecionado")
if st.session_state.get("passagem_vacinas", {}).get("atrasadas"):
    plano.append("regularizar vacinas faltantes listadas, respeitando intervalos e idade máxima")
if st.session_state.get("passagem_suplementacao"):
    plano.append("ajustar suplementação conforme idade, fatores de risco e registros prévios")
if st.session_state.get("passagem_desenvolvimento", {}).get("pendentes"):
    plano.append("orientar estimulação e reavaliar marcos ausentes/não verificados")
plano.append("programar retorno conforme achados clínicos, crescimento, desenvolvimento e demanda familiar")
st.session_state["passagem_plano"] = plano


# Abre a passagem no fim da execução, após todas as seções atualizarem o session_state.
if st.session_state.pop("abrir_passagem_flag", False):
    abrir_passagem()
