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
from estrutura_consulta import (
    INTERROGATORIO_SEGMENTAR, ANTECEDENTES_MATERNOS, INTERCORRENCIAS_PERINATAIS,
    ANTECEDENTES_PATOLOGICOS, ANTECEDENTES_FAMILIARES, TRIAGENS_NEONATAIS,
    TIPOS_ALEITAMENTO, PADRAO_FEZES, PADRAO_URINA, SONO, CONDICOES_MORADIA,
    ECTOSCOPIA, CABECA_PESCOCO, EXAME_RESPIRATORIO, EXAME_CARDIO, EXAME_ABDOMINAL,
    EXAME_OUTROS, REFLEXOS_PRIMITIVOS, checar_disponibilidade_medicamento,
)
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

# =========================
# Render principal
# =========================

tabelas = carregar_tabelas()

st.markdown("<div class='hero'><h1>👶 Puericultura Digital</h1><p>Análise clínica por idade, sexo, crescimento, desenvolvimento, imunizações, suplementação, orientações e passagem de caso.</p></div>", unsafe_allow_html=True)

with st.expander("🧾 Identificação, nascimento e exame físico objetivo", expanded=True):
    st.markdown("### Identificação e nascimento")
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        sexo = st.selectbox("Sexo", ["Masculino", "Feminino"])
        data_nasc = st.date_input("Data de nascimento", value=date(2023,1,1), format="DD/MM/YYYY")
    with c2:
        data_aval = st.date_input("Data da consulta", value=date.today(), format="DD/MM/YYYY")
        aleitamento_exclusivo = st.checkbox("Aleitamento materno exclusivo?", value=True)
    with c3:
        peso_nasc_g = st.number_input("Peso ao nascer (g)", 300, 6500, 3200, step=10)
        ig_sem = st.number_input("IG ao nascer — semanas", 22, 42, 39, step=1)
    with c4:
        ig_dias = st.number_input("IG ao nascer — dias", 0, 6, 0, step=1)
        idade_gest_sem = float(ig_sem) + float(ig_dias)/7
        prematuro = idade_gest_sem < 37
        st.toggle("Pré-termo?", value=prematuro, disabled=True)
    st.markdown("### Exame físico — sinais vitais e antropometria atual")
    v1,v2,v3,v4,v5 = st.columns(5)
    with v1: temp = st.number_input("Temp. (°C)", 34.0, 42.0, 36.5, step=0.1)
    with v2: fc = st.number_input("FC (bpm)", 40, 240, 100, step=1)
    with v3: fr = st.number_input("FR (irpm)", 10, 100, 24, step=1)
    with v4: spo2 = st.number_input("SpO₂ (%)", 50, 100, 98, step=1)
    with v5: pa = st.text_input("PA", value="")
    a1,a2,a3 = st.columns(3)
    with a1: peso = st.number_input("Peso atual (kg)", 0.5, 100.0, 10.0, step=0.1)
    with a2: estatura = st.number_input("Comprimento/estatura atual (cm)", 30.0, 170.0, 80.0, step=0.5)
    with a3: pc = st.number_input("Perímetro cefálico atual (cm)", 20.0, 70.0, 45.0, step=0.1)

idade_dias_cron = max(0, (data_aval - data_nasc).days)
correcao_dias = max(0, int(round((40 - idade_gest_sem) * 7))) if prematuro else 0
idade_dias = max(0, idade_dias_cron - correcao_dias)
idade_meses_float = idade_dias / 30.4375
idade_meses_cron = idade_dias_cron / 30.4375
class_nasc, riscos_nasc = classificar_peso_ig(peso_nasc_g, idade_gest_sem)
imc = peso / ((estatura/100)**2)
res_ant = classificar_antropometria(tabelas, sexo, idade_dias, idade_meses_float, peso, estatura, pc) if tabelas else {}

st.markdown(css(sexo), unsafe_allow_html=True)

st.session_state["passagem_crianca"] = {"sexo": sexo, "data_nascimento": fmt_data(data_nasc), "data_consulta": fmt_data(data_aval), "idade_cronologica": idade_texto(idade_dias_cron), "idade_corrigida": idade_texto(idade_dias)}
st.session_state["passagem_nascimento"] = {"ig": f"{ig_sem}s {ig_dias}d", "peso_nascimento": f"{peso_nasc_g:.0f} g", "classificacao": class_nasc, "riscos": riscos_nasc}

st.markdown(f"""
<div class='top-panel'><b>Resumo fixo da criança</b><br>
<span class='metric-pill'>Sexo: {sexo}</span><span class='metric-pill'>Nascimento: {fmt_data(data_nasc)}</span><span class='metric-pill'>Consulta: {fmt_data(data_aval)}</span>
<span class='metric-pill'>Idade cronológica: {idade_texto(idade_dias_cron)}</span><span class='metric-pill'>Idade corrigida: {idade_texto(idade_dias)}</span>
<span class='metric-pill'>IG: {ig_sem}s {ig_dias}d</span><span class='metric-pill'>PN: {peso_nasc_g:.0f}g · {class_nasc}</span>
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
    queixa = st.text_area("Queixa principal / História da doença atual", placeholder="Ex.: responsável refere tosse há 3 dias, febre...", height=110)
    st.markdown("### Interrogatório sintomatológico segmentar")
    inter = {}
    cols = st.columns(2)
    for i, (seg, ops) in enumerate(INTERROGATORIO_SEGMENTAR.items()):
        with cols[i % 2]:
            inter[seg] = st.multiselect(seg, ops, key=f"is_{seg}")
    inter_obs = st.text_area("Complemento do interrogatório sintomatológico", height=70)

    st.markdown("### Medicamentos em uso / suplementações")
    n_meds = st.number_input("Número de medicamentos/suplementos em uso", 0, 8, 0, step=1)
    meds = []
    for i in range(int(n_meds)):
        with st.expander(f"Medicamento/suplemento {i+1}", expanded=True):
            mc1,mc2,mc3,mc4 = st.columns(4)
            with mc1: nome_med = st.text_input("Fármaco/produto", key=f"med_nome_{i}")
            with mc2: apresentacao_med = st.text_input("Apresentação", key=f"med_ap_{i}")
            with mc3: posologia_med = st.text_input("Posologia", key=f"med_pos_{i}")
            with mc4: motivo_med = st.text_input("Indicação/motivo", key=f"med_mot_{i}")
            disp = checar_disponibilidade_medicamento(nome_med)
            if nome_med:
                st.caption(f"Disponibilidade local estimada — RENAME: {'sim' if disp['rename'] else 'não identificado'} · REMUME PMVC: {'sim' if disp['remume'] else 'não identificado'} · Apresentações: {', '.join(disp['apresentacoes']) or '—'}")
            if nome_med and gerar_orientacao_medicamento_ia and st.button("🔎 Apoio IA para conferir medicamento", key=f"med_ia_{i}"):
                st.info(gerar_orientacao_medicamento_ia(nome_med, idade_texto(idade_dias), peso, motivo_med))
            meds.append({"nome":nome_med, "apresentacao":apresentacao_med, "posologia":posologia_med, "motivo":motivo_med, "rename":disp})

    st.markdown("### Antecedentes maternos, gestacionais e obstétricos")
    mat1, mat2, mat3 = st.columns(3)
    with mat1: paridade = st.text_input("Paridade", value="G__ PN__ PC__ A__", help="Formato: G__ PN__ PC__ A__")
    with mat2: n_filhos = st.number_input("Número de filhos vivos", 0, 20, 0, step=1)
    with mat3: filhos_desc = st.text_input("Filhos: sexo e idade", placeholder="Ex.: M 8a; F 3a")
    ant_mat = st.multiselect("Doenças/comorbidades/intercorrências gestacionais/obstétricas", ANTECEDENTES_MATERNOS)
    med_gest = st.text_area("Medicamentos/suplementações maternas na gestação e adequação", placeholder="Ex.: sulfato ferroso regular; ácido fólico até 12 semanas; vacinas...", height=70)

    st.markdown("### Antecedentes perinatais e triagens neonatais")
    ant_peri = st.multiselect("Intercorrências perinatais/neonatais", INTERCORRENCIAS_PERINATAIS)
    peri_det = {}
    if "internação neonatal" in ant_peri or "UTI neonatal" in ant_peri:
        peri_det["internacao"] = st.text_input("Internação neonatal: motivo e duração")
    if "fototerapia" in ant_peri:
        peri_det["fototerapia"] = st.text_input("Fototerapia: motivo/duração")
    if "antibiótico neonatal" in ant_peri:
        peri_det["antibiotico"] = st.text_input("Antibiótico neonatal: qual/motivo/duração")
    triagens = {}
    tcols = st.columns(3)
    for i, (teste, ops) in enumerate(TRIAGENS_NEONATAIS.items()):
        with tcols[i % 3]:
            val = st.selectbox(teste, ops, key=f"triagem_{teste}")
            triagens[teste] = val
            if val not in ("normal", "não sabe informar"):
                triagens[teste + " — detalhe"] = st.text_input(f"Detalhe: {teste}", key=f"triagem_det_{teste}")

    st.markdown("### Antecedentes patológicos, familiares, hábitos e contexto")
    ant_pat = st.multiselect("Antecedentes patológicos", ANTECEDENTES_PATOLOGICOS)
    det_pat = {}
    for item in ["internações", "cirurgias", "alergias medicamentosas", "alergias alimentares", "convulsões", "transfusões", "acidentes/intoxicações"]:
        if item in ant_pat:
            det_pat[item] = st.text_input(f"Detalhar {item}: motivo, data, duração/procedimento", key=f"det_{item}")
    ant_fam = st.multiselect("Antecedentes familiares", ANTECEDENTES_FAMILIARES)

    hab1,hab2 = st.columns(2)
    with hab1:
        alimentacao = st.multiselect("Alimentação/aleitamento", TIPOS_ALEITAMENTO)
        formula = ""
        if "fórmula infantil exclusiva" in alimentacao or "aleitamento misto" in alimentacao:
            formula = st.text_input("Fórmula: marca/tipo, volume, frequência, diluição")
        sono = st.multiselect("Sono", SONO)
        telas = st.selectbox("Telas", ["não usa", "uso ocasional", "< 1h/dia", "1–2h/dia", "> 2h/dia", "não informado"])
    with hab2:
        fezes = st.multiselect("Fezes", PADRAO_FEZES)
        urina = st.multiselect("Micção", PADRAO_URINA)
        desfralde = st.selectbox("Desfralde/controle esfincteriano", ["não se aplica pela idade", "não iniciado", "em treinamento", "diurno adquirido", "diurno e noturno adquiridos", "regressão/perdas"])
        atividade = st.text_input("Atividade física/brincadeiras/creche/escola")
    socio = st.multiselect("Condições socioeconômicas/moradia", CONDICOES_MORADIA)
    coabit = st.text_input("Coabitantes/cuidadores principais")

    st.markdown("### Exame físico segmentar")
    geral = st.multiselect("Ectoscopia/estado geral", ECTOSCOPIA, default=["bom estado geral", "ativo e reativo", "hidratado", "corado", "acianótico", "anicterico", "eupneico"])
    pesco = {}
    with st.expander("Cabeça e pescoço", expanded=False):
        cc = st.columns(2)
        for i,(sec, ops) in enumerate(CABECA_PESCOCO.items()):
            with cc[i%2]: pesco[sec] = st.multiselect(sec, ops, key=f"cab_{sec}")
    resp = {}; cardio = {}; abd = {}; outros = {}; reflexos = []
    with st.expander("Respiratório", expanded=False):
        cols = st.columns(2)
        for i,(sec, ops) in enumerate(EXAME_RESPIRATORIO.items()):
            with cols[i%2]: resp[sec] = st.multiselect(sec, ops, key=f"resp_{sec}")
    with st.expander("Cardiovascular", expanded=False):
        for sec, ops in EXAME_CARDIO.items(): cardio[sec] = st.multiselect(sec, ops, key=f"cardio_{sec}")
    with st.expander("Abdominal", expanded=False):
        cols = st.columns(2)
        for i,(sec, ops) in enumerate(EXAME_ABDOMINAL.items()):
            with cols[i%2]: abd[sec] = st.multiselect(sec, ops, key=f"abd_{sec}")
    with st.expander("Genitália, osteomuscular, neurológico, pele e reflexos", expanded=False):
        cols = st.columns(2)
        for i,(sec, ops) in enumerate(EXAME_OUTROS.items()):
            with cols[i%2]: outros[sec] = st.multiselect(sec, ops, key=f"out_{sec}")
        reflexos = st.multiselect("Reflexos primitivos — RN/lactente", REFLEXOS_PRIMITIVOS)
    exames_comp = st.text_area("Exames complementares realizados/solicitados e resultados", height=90)

    consulta_dados = {
        "queixa_hda": queixa, "interrogatorio": {**inter, "complemento": inter_obs}, "medicamentos_uso": meds,
        "paridade": paridade, "filhos": {"numero": n_filhos, "descricao": filhos_desc}, "antecedentes_maternos": ant_mat, "medicamentos_gestacao": med_gest,
        "antecedentes_perinatais": {"selecionados": ant_peri, "detalhes": peri_det}, "triagens_neonatais": triagens,
        "antecedentes_patologicos": {"selecionados": ant_pat, "detalhes": det_pat}, "antecedentes_familiares": ant_fam,
        "habitos": {"alimentacao": alimentacao, "formula": formula, "sono": sono, "telas": telas, "fezes": fezes, "urina": urina, "desfralde": desfralde, "atividade": atividade},
        "socioeconomico": {"moradia": socio, "coabitantes": coabit},
    }
    exame_dados = {"sinais_vitais": f"T {temp:.1f}°C; FC {fc} bpm; FR {fr} irpm; SpO₂ {spo2}%; PA {pa or 'não aferida'}", "antropometria": f"Peso {peso:.1f} kg; estatura {estatura:.1f} cm; PC {pc:.1f} cm; IMC {imc:.1f}", "geral": geral, "cabeca_pescoco": pesco, "respiratorio": resp, "cardiovascular": cardio, "abdominal": abd, "outros": outros, "reflexos_primitivos": reflexos, "exames_complementares": exames_comp}
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
    fatores_dev = st.multiselect("Fatores de risco para desenvolvimento", ["Prematuridade", "Baixo peso ao nascer", "Internação neonatal prolongada", "Asfixia/hipóxia", "Infecção congênita", "Alteração auditiva/visual", "Vulnerabilidade social", "Suspeita de TEA ou regressão"], default=["Prematuridade"] if prematuro else [])
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
    with c1: fat_maternos = st.multiselect("Fatores maternos/gestacionais para anemia", riscos["maternos_gestacionais"])
    with c2:
        defaults=[]
        if prematuro: defaults.append("Prematuridade")
        if peso_nasc_g < 2500: defaults.append("Baixo peso ao nascer (< 2.500 g)")
        fat_crianca = st.multiselect("Fatores da criança para anemia", riscos["crianca"], default=defaults)
    rec = recomendacao_ferro(idade_meses_float, peso, peso_nasc_g, idade_gest_sem, aleitamento_exclusivo, fat_crianca, fat_maternos)
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
    fat_d=st.multiselect("Fatores de risco para hipovitaminose D", fatores_risco_hipovitaminose_d(), default=["Prematuridade"] if prematuro else [])
    vit_d=calcular_vitamina_d_sbp(idade_meses_float, peso, prematuro, peso_nasc_g, fat_d)
    fat_b12=st.multiselect("Fatores de risco para deficiência de B12", fatores_risco_vitamina_b12())
    st.markdown(f"<div class='soft-card'><div class='soft-title'>Vitamina D</div><p><b>Dose:</b> {vit_d['dose']}</p><p>{vit_d['orientacao']}</p><div class='prescricao'>{vit_d['prescricao']}</div></div>", unsafe_allow_html=True)
    st.session_state["passagem_suplementacao"] = {"resumo": [f"Ferro: {rec['protocolo']} — {rec['resumo']} — {rec['dose_mg_dia']:.1f} mg/dia", f"Vitamina A: {vit_a['dose']} — {'indicada' if vit_a['indicada'] else 'conferir critérios'}", f"Vitamina D: {vit_d['dose']}", f"B12: {'risco presente' if fat_b12 else 'sem fatores de risco selecionados'}"], "fatores_risco": {"anemia_crianca": fat_crianca, "anemia_maternos": fat_maternos, "vitamina_d": fat_d, "b12": fat_b12}}

with tabs[5]:
    st.subheader("🩺 Protocolos ambulatoriais")
    if obter_protocolos_ambulatoriais:
        protos = obter_protocolos_ambulatoriais(); nome = st.selectbox("Protocolo", list(protos.keys()))
        respostas = {}
        for campo in campos_do_protocolo(nome):
            cid=campo.get("id"); label=campo.get("label", cid); tipo=campo.get("tipo", "text"); ops=campo.get("opcoes", [])
            if tipo == "checkbox": respostas[cid] = st.checkbox(label, key=f"proto_{nome}_{cid}")
            elif tipo == "select": respostas[cid] = st.selectbox(label, ops, key=f"proto_{nome}_{cid}")
            elif tipo == "multiselect": respostas[cid] = st.multiselect(label, ops, key=f"proto_{nome}_{cid}")
            elif tipo == "number": respostas[cid] = st.number_input(label, value=campo.get("value",0), key=f"proto_{nome}_{cid}")
            else: respostas[cid] = st.text_input(label, key=f"proto_{nome}_{cid}")
        res = executar_protocolo(nome, respostas, {"idade_meses":idade_meses_float,"peso":peso})
        st.markdown(f"<div class='soft-card'><div class='soft-title'>Classificação</div>{res.get('classificacao','—')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='prescricao'>{res.get('prescricao','Sem prescrição automática.')}</div>", unsafe_allow_html=True)
        st.markdown("<div class='soft-card'><div class='soft-title'>Orientações</div>" + html_lista(res.get('orientacoes', [])) + "</div>", unsafe_allow_html=True)
        st.session_state["passagem_ambulatorio"] = {"protocolo": nome, "classificacao": res.get("classificacao"), "conduta_resumo": safe_join(res.get("conduta", res.get("orientacoes", []))), "prescricao": res.get("prescricao")}
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
