import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
from datetime import date
from diretrizes import (
    obter_classificacao,
    obter_orientacoes_detalhadas,
    obter_esquema_vacinal,
    obter_marcos_vigilancia,
    obter_sais_ferro,
    obter_faixas_zscore,
)

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Puericultura Digital", layout="wide", initial_sidebar_state="expanded")

@st.cache_data
def carregar_tabelas():
    def carregar_e_limpar(nome_arquivo):
        try:
            df = pd.read_csv(nome_arquivo, sep=',', decimal='.', encoding='utf-8-sig')
            if len(df.columns) < 5:
                raise ValueError
        except Exception:
            df = pd.read_csv(nome_arquivo, sep=';', decimal=',', encoding='utf-8-sig')

        df.columns = df.columns.str.strip().str.replace('\ufeff', '')
        df.rename(columns={df.columns[0]: 'Day'}, inplace=True)
        df = df.apply(pd.to_numeric, errors='coerce').dropna(subset=['Day'])
        df['Day'] = df['Day'].astype(int)

        # Curvas extras para permitir sombreamento nas extremidades.
        if 'SD4' not in df.columns and {'SD2', 'SD3'}.issubset(df.columns):
            df['SD4'] = df['SD3'] + (df['SD3'] - df['SD2'])
        if 'SD4neg' not in df.columns and {'SD2neg', 'SD3neg'}.issubset(df.columns):
            df['SD4neg'] = df['SD3neg'] - (df['SD2neg'] - df['SD3neg'])
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
        st.error(f"Não foi possível carregar as tabelas OMS. Verifique se os CSVs estão no repositório. Detalhe: {exc}")
        return None


def coluna_z(z):
    """Converte escore-z em nome de coluna esperado nos arquivos OMS."""
    if z == 0:
        return "SD0"
    if z > 0:
        return f"SD{z}"
    return f"SD{abs(z)}neg"


def adicionar_sombreamento_z(fig, df, parametro, x):
    """Adiciona faixas coloridas entre curvas z, com legendas clínicas."""
    for faixa in obter_faixas_zscore(parametro):
        col_inf = coluna_z(faixa["z_min"])
        col_sup = coluna_z(faixa["z_max"])
        if col_inf not in df.columns or col_sup not in df.columns:
            continue

        fig.add_trace(
            go.Scatter(
                x=x,
                y=df[col_inf],
                mode="lines",
                line=dict(width=0),
                hoverinfo="skip",
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=x,
                y=df[col_sup],
                mode="lines",
                line=dict(width=0),
                fill="tonexty",
                fillcolor=faixa["cor_fill"],
                name=faixa["rotulo"],
                hovertemplate=f"{faixa['rotulo']}<extra></extra>",
            )
        )


def adicionar_curvas_referencia(fig, df, x):
    curvas = [
        ("SD3neg", "-3Z", "#b71c1c", 1.4, "dash"),
        ("SD2neg", "-2Z", "#e65100", 1.8, "solid"),
        ("SD1neg", "-1Z", "#9e9e9e", 1.0, "dot"),
        ("SD0", "Mediana", "#1b5e20", 3.0, "solid"),
        ("SD1", "+1Z", "#9e9e9e", 1.0, "dot"),
        ("SD2", "+2Z", "#e65100", 1.8, "solid"),
        ("SD3", "+3Z", "#b71c1c", 1.4, "dash"),
    ]
    for col, nome, cor, largura, dash in curvas:
        if col in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=df[col],
                    mode="lines",
                    line=dict(color=cor, width=largura, dash=dash),
                    name=nome,
                    hovertemplate=f"{nome}: %{{y:.2f}}<extra></extra>",
                )
            )


def render_status_chip(texto, status):
    mapa = {
        "P": ("Presente", "#e8f5e9", "#1b5e20"),
        "A": ("Ausente", "#ffebee", "#b71c1c"),
        "NV": ("Não verificado", "#f5f5f5", "#424242"),
    }
    label, bg, fg = mapa.get(status, (status, "#f5f5f5", "#424242"))
    st.markdown(
        f"<span class='chip' style='background:{bg};color:{fg};'>{texto}: {label}</span>",
        unsafe_allow_html=True,
    )


tabelas_oms = carregar_tabelas()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 👶 Perfil da criança")
    sexo = st.selectbox("Sexo", ["Masculino", "Feminino"])
    data_nasc = st.date_input("Nascimento", value=date(2023, 1, 1))
    data_aval = st.date_input("Consulta atual", value=date.today())
    idade_dias = max(0, (data_aval - data_nasc).days)

    prematuro = st.checkbox("Pré-termo")
    if prematuro:
        sem_gest = st.number_input("Semanas gestacionais ao nascer", 24, 36, 34)
        idade_dias = max(0, idade_dias - ((40 - sem_gest) * 7))

    anos = int(idade_dias // 365.25)
    meses = int((idade_dias % 365.25) // 30.4375)
    dias = int((idade_dias % 365.25) % 30.4375)
    st.markdown(f"<div class='age-box'>Idade corrigida/cronológica<br><b>{anos}a {meses}m {dias}d</b></div>", unsafe_allow_html=True)

    st.markdown("### 📏 Medidas atuais")
    peso = st.number_input("Peso atual (kg)", 0.5, 100.0, 10.0, step=0.1)
    estatura = st.number_input("Estatura atual (cm)", 30.0, 150.0, 80.0, step=0.5)
    pc = st.number_input("PC atual (cm)", 20.0, 70.0, 45.0, step=0.1)
    aleitamento_exclusivo = st.checkbox("Aleitamento materno exclusivo?", value=True)

# --- CSS / IDENTIDADE VISUAL ---
tema_cor = "#0d47a1" if sexo == "Masculino" else "#880e4f"
fundo = "linear-gradient(135deg, #eef7ff 0%, #f8fbff 45%, #ffffff 100%)" if sexo == "Masculino" else "linear-gradient(135deg, #fff0f7 0%, #fff8fb 45%, #ffffff 100%)"

st.markdown(
    f"""
<style>
:root {{
    --title-color: {tema_cor};
    --soft-border: rgba(20, 20, 20, .08);
    --card-shadow: 0 10px 30px rgba(0,0,0,.07);
}}
.stApp {{ background: {fundo}; }}
h1, h2, h3, h4 {{ color: var(--title-color) !important; }}
.block-container {{ padding-top: 1.4rem; }}
.hero {{
    padding: 22px 26px;
    border-radius: 24px;
    background: rgba(255,255,255,.82);
    border: 1px solid var(--soft-border);
    box-shadow: var(--card-shadow);
    margin-bottom: 18px;
}}
.hero h1 {{ margin-bottom: 2px; }}
.hero p {{ margin: 0; color: #455a64; font-size: 1rem; }}
.age-box {{
    border-radius: 18px;
    padding: 14px 16px;
    margin: 12px 0 18px 0;
    background: white;
    border-left: 6px solid var(--title-color);
    box-shadow: 0 6px 18px rgba(0,0,0,.06);
}}
.crit-card {{
    padding: 18px;
    border-radius: 18px;
    color: white;
    margin-bottom: 14px;
    box-shadow: var(--card-shadow);
}}
.crit-card .big {{ font-size: 1.45rem; font-weight: 800; }}
.crit-card .small {{ opacity: .95; font-size: .95rem; }}
.legend-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 10px; margin: 10px 0 18px 0; }}
.legend-item {{ border-radius: 14px; padding: 10px 12px; background: white; border: 1px solid var(--soft-border); box-shadow: 0 4px 14px rgba(0,0,0,.04); font-size: .88rem; }}
.dev-card, .vaccine-card, .orient-card {{
    background: rgba(255,255,255,.92);
    border: 1px solid var(--soft-border);
    border-radius: 22px;
    padding: 18px;
    margin-bottom: 16px;
    box-shadow: var(--card-shadow);
}}
.dev-header {{ display:flex; justify-content:space-between; gap:12px; align-items:center; margin-bottom: 8px; }}
.dev-title {{ font-weight: 800; font-size: 1.05rem; color: #263238; }}
.dev-area {{ border-radius: 999px; padding: 4px 10px; background: #eef2ff; color: #283593; font-weight: 700; font-size: .8rem; }}
.chip {{ display:inline-block; border-radius: 999px; padding: 5px 10px; margin: 3px 4px 3px 0; font-size: .78rem; font-weight: 700; }}
.vaccine-card {{ padding: 0; overflow: hidden; }}
.vaccine-head {{
    padding: 16px 18px;
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}
.vaccine-head .age {{ font-size: 1.25rem; font-weight: 900; }}
.vaccine-head .tag {{ background: rgba(255,255,255,.22); border-radius: 999px; padding: 5px 10px; font-size: .78rem; font-weight: 700; }}
.vaccine-body {{ padding: 14px 16px 16px 16px; }}
.vax-row {{
    display: grid;
    grid-template-columns: minmax(120px, 1.1fr) minmax(75px, .55fr) 1.7fr;
    gap: 10px;
    border-bottom: 1px dashed #e0e0e0;
    padding: 10px 0;
    align-items: start;
}}
.vax-row:last-child {{ border-bottom: 0; }}
.vax-name {{ font-weight: 850; color: #263238; }}
.vax-dose {{ display:inline-block; width: fit-content; border-radius: 999px; padding: 4px 9px; background: #f1f5f9; color: #334155; font-size: .8rem; font-weight: 750; }}
.vax-disease {{ color: #455a64; font-size: .9rem; }}
.orient-card h4 {{ margin: 0 0 6px 0; }}
.orient-card ul {{ margin-bottom: 0; padding-left: 1.1rem; }}
.orient-note {{ background: #fff8e1; border-left: 5px solid #ffb300; border-radius: 14px; padding: 12px 14px; margin-top: 10px; color: #5d4037; }}
[data-testid="stSidebar"] {{ background: rgba(255,255,255,.88); }}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="hero">
    <h1>👶 Puericultura Digital</h1>
    <p>Curvas OMS com interpretação visual por escore-z, vigilância do desenvolvimento, calendário vacinal e orientações por idade.</p>
</div>
""",
    unsafe_allow_html=True,
)

if tabelas_oms:
    imc = peso / ((estatura / 100) ** 2)
    idade_meses_float = idade_dias / 30.4375

    tabs = st.tabs(["📈 Crescimento", "🧠 Desenvolvimento", "💉 Vacinação", "📝 Orientações", "💊 Suplementação"])

    with tabs[0]:
        fx, r_x = (
            ("0 a 2 anos", [0, 24])
            if idade_meses_float <= 24
            else (("2 a 5 anos", [24, 60]) if idade_meses_float <= 60 else ("5 a 10 anos", [60, 120]))
        )
        stabs = st.tabs(["⚖️ Peso", "📏 Estatura", "🧮 IMC", "🧠 PC"])
        cfg = [
            ("Peso", "Peso/Idade", "kg", peso, fx, r_x),
            ("Estatura", "Estatura/Idade", "cm", estatura, fx, r_x),
            ("IMC", "IMC/Idade", "kg/m²", imc, fx, r_x),
            ("PC", "Perímetro cefálico/Idade", "cm", pc, "0 a 2 anos", [0, 24]),
        ]

        for subtab, (k, titulo, unidade, valor, faixa_nome, rx) in zip(stabs, cfg):
            with subtab:
                df = tabelas_oms[sexo][k]
                idade_ref = min(max(int(idade_dias), int(df["Day"].min())), int(df["Day"].max()))
                linha = df.iloc[(df["Day"] - idade_ref).abs().argsort()[:1]].iloc[0]
                z = (((valor / linha["M"]) ** linha["L"]) - 1) / (linha["L"] * linha["S"]) if linha["L"] != 0 else np.log(valor / linha["M"]) / linha["S"]
                classificacao, criterio, cor = obter_classificacao(z, k)
                percentil = norm.cdf(z) * 100

                st.markdown(
                    f"""
<div class="crit-card" style="background: linear-gradient(135deg, {cor}, #263238);">
    <div class="small">{titulo} • {faixa_nome}</div>
    <div class="big">{classificacao}</div>
    <div class="small">Z-score: <b>{z:.2f}</b> • Percentil aproximado: <b>P{percentil:.0f}</b> • Critério: {criterio}</div>
</div>
""",
                    unsafe_allow_html=True,
                )

                legendas = "".join(
                    [
                        f"<div class='legend-item'><b style='color:{f['cor_texto']};'>{f['rotulo']}</b><br><span>{f['intervalo']}</span></div>"
                        for f in obter_faixas_zscore(k)
                    ]
                )
                st.markdown(f"<div class='legend-grid'>{legendas}</div>", unsafe_allow_html=True)

                fig = go.Figure()
                mx = df["Day"] / 30.4375
                adicionar_sombreamento_z(fig, df, k, mx)
                adicionar_curvas_referencia(fig, df, mx)

                fig.add_trace(
                    go.Scatter(
                        x=[idade_meses_float],
                        y=[valor],
                        mode="markers+text",
                        marker=dict(size=18, color="#111827", line=dict(width=3, color="white")),
                        text=["Paciente"],
                        textposition="top center",
                        name="Paciente",
                        hovertemplate=f"Paciente: {valor:.2f} {unidade}<br>Idade: {idade_meses_float:.1f} meses<extra></extra>",
                    )
                )

                for ano_mes in [12, 24, 36, 48, 60, 72, 84, 96, 108, 120]:
                    if rx[0] <= ano_mes <= rx[1]:
                        fig.add_vline(x=ano_mes, line_width=1, line_dash="dot", line_color="rgba(0,0,0,.25)")
                        fig.add_annotation(x=ano_mes, y=0.01, yref="paper", text=f"<b>{ano_mes//12}a</b>", showarrow=False)

                fig.update_layout(
                    height=620,
                    template="plotly_white",
                    margin=dict(l=10, r=10, t=20, b=10),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                    xaxis=dict(title="Idade (meses)", range=rx, dtick=1 if rx[1] <= 24 else 3, showgrid=True, gridcolor="rgba(0,0,0,0.08)"),
                    yaxis=dict(title=f"{titulo} ({unidade})", showgrid=True, gridcolor="rgba(0,0,0,0.08)"),
                )
                st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        chave, todos_marcos = obter_marcos_vigilancia(idade_meses_float)
        st.subheader("🧠 Vigilância do desenvolvimento")
        st.caption("Marque P quando o marco estiver presente, A quando estiver ausente e NV quando não foi verificado na consulta.")

        for faixa, lista in todos_marcos.items():
            expandir = faixa == chave
            with st.expander(f"{faixa} {'• faixa atual' if expandir else ''}", expanded=expandir):
                cols = st.columns(2)
                for i, item in enumerate(lista):
                    marco = item["marco"] if isinstance(item, dict) else item
                    area = item.get("area", "Marco") if isinstance(item, dict) else "Marco"
                    alerta = item.get("alerta", "") if isinstance(item, dict) else ""
                    with cols[i % 2]:
                        st.markdown(
                            f"""
<div class="dev-card">
    <div class="dev-header">
        <div class="dev-title">{marco}</div>
        <div class="dev-area">{area}</div>
    </div>
    <div style="color:#607d8b;font-size:.88rem;min-height:34px;">{alerta}</div>
</div>
""",
                            unsafe_allow_html=True,
                        )
                        status = st.radio(
                            f"Status - {faixa} - {marco}",
                            ["P", "A", "NV"],
                            horizontal=True,
                            key=f"dev_{faixa}_{marco}",
                            label_visibility="collapsed",
                        )
                        render_status_chip("Registro", status)

    with tabs[2]:
        st.subheader("💉 Calendário vacinal")
        st.caption("Visual em cartões, com destaque automático para vacinas da idade atual ou próximas da idade da criança.")
        esquema = obter_esquema_vacinal()
        cols = st.columns(2)
        for i, bloco in enumerate(esquema):
            meses_ref = bloco.get("meses_ref", 0)
            distancia = meses_ref - idade_meses_float
            if -1 <= distancia <= 1:
                etiqueta = "Agora"
            elif distancia > 1:
                etiqueta = f"Em ~{int(round(distancia))} meses"
            else:
                etiqueta = "Verificar registro"

            linhas = "".join(
                [
                    f"""
<div class="vax-row">
    <div class="vax-name">{vac['nome']}</div>
    <div><span class="vax-dose">{vac['dose']}</span></div>
    <div class="vax-disease">{vac['doencas']}</div>
</div>
"""
                    for vac in bloco["vacinas"]
                ]
            )
            with cols[i % 2]:
                st.markdown(
                    f"""
<div class="vaccine-card">
    <div class="vaccine-head" style="background: linear-gradient(135deg, {bloco['cor']}, #263238);">
        <div class="age">{bloco['idade']}</div>
        <div class="tag">{etiqueta}</div>
    </div>
    <div class="vaccine-body">{linhas}</div>
</div>
""",
                    unsafe_allow_html=True,
                )

    with tabs[3]:
        st.subheader("📝 Orientações por idade")
        orientacoes = obter_orientacoes_detalhadas(idade_meses_float)
        cols = st.columns(2)
        for i, (categoria, conteudo) in enumerate(orientacoes.items()):
            if isinstance(conteudo, dict):
                itens = "".join([f"<li>{x}</li>" for x in conteudo.get("itens", [])])
                nota = conteudo.get("nota", "")
            else:
                itens = f"<li>{conteudo}</li>"
                nota = ""
            with cols[i % 2]:
                st.markdown(
                    f"""
<div class="orient-card">
    <h4>📍 {categoria}</h4>
    <ul>{itens}</ul>
    {f'<div class="orient-note">{nota}</div>' if nota else ''}
</div>
""",
                    unsafe_allow_html=True,
                )

    with tabs[4]:
        st.subheader("💊 Calculadora de suplementação de ferro")
        sais = obter_sais_ferro()
        sal = st.selectbox("Sal de ferro", list(sais.keys()))
        alvo = 2.0 if (prematuro or peso < 2.5) else (1.0 if idade_meses_float >= 3 else 0.0)
        if alvo > 0:
            necessidade = peso * alvo
            gotas = round(necessidade / sais[sal]["mg_gota"])
            st.success(
                f"Dose alvo: **{alvo} mg/kg/dia** | Necessidade: **{necessidade:.1f} mg/dia** | Prescrever aproximadamente: **{max(1, gotas)} gota(s)/dia** de {sais[sal]['marcas']}"
            )
        else:
            st.warning("Sem indicação automática de início de ferro pelo critério usado no app. Confirmar com protocolo local e avaliação clínica.")
else:
    st.stop()
