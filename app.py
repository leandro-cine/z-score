import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
from datetime import date
from diretrizes import obter_classificacao, obter_orientacoes, obter_esquema_vacinal, obter_marcos_caderneta

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Puericultura Digital", layout="wide", initial_sidebar_state="expanded")

@st.cache_data
def carregar_tabelas():
    def carregar_e_limpar(nome_arquivo):
        try:
            df = pd.read_csv(nome_arquivo, sep=',', decimal='.', encoding='utf-8-sig')
            if len(df.columns) < 5: raise ValueError
        except:
            df = pd.read_csv(nome_arquivo, sep=';', decimal=',', encoding='utf-8-sig')
        df.columns = df.columns.str.strip().str.replace('\ufeff', '')
        df.rename(columns={df.columns[0]: 'Day'}, inplace=True)
        df = df.apply(pd.to_numeric, errors='coerce').dropna(subset=['Day'])
        df['Day'] = df['Day'].astype(int)
        if 'SD4' not in df.columns: df['SD4'] = df['SD3'] + (df['SD3'] - df['SD2'])
        if 'SD4neg' not in df.columns: df['SD4neg'] = df['SD3neg'] - (df['SD2neg'] - df['SD3neg'])
        return df
    try:
        return {
            "Masculino": {
                "Peso": carregar_e_limpar("WFA_boys_z_exp.csv"), "Estatura": carregar_e_limpar("LFA_boys_z_exp.csv"),
                "IMC": carregar_e_limpar("BFA_boys_z_exp.csv"), "PC": carregar_e_limpar("HCFA_boys_z_exp.csv")
            },
            "Feminino": {
                "Peso": carregar_e_limpar("WFA_girls_z_exp.csv"), "Estatura": carregar_e_limpar("LFA_girls_z_exp.csv"),
                "IMC": carregar_e_limpar("BFA_girls_z_exp.csv"), "PC": carregar_e_limpar("HCFA_girls_z_exp.csv")
            }
        }
    except Exception as e:
        st.error(f"Erro nos arquivos: {e}")
        return None

tabelas_oms = carregar_tabelas()

# --- SIDEBAR ---
with st.sidebar:
    st.header("👶 Perfil")
    sexo = st.selectbox("Sexo", ["Masculino", "Feminino"])
    data_nasc = st.date_input("Nascimento", value=date(2023, 1, 1))
    data_aval = st.date_input("Consulta Atual", value=date.today())
    
    idade_dias = (data_aval - data_nasc).days
    prematuro = st.checkbox("Pré-termo")
    if prematuro:
        sem_gest = st.number_input("Semanas Gestacionais", 24, 36, 34)
        idade_dias = max(0, idade_dias - ((40 - sem_gest) * 7))

    anos, meses, dias = int(idade_dias//365.25), int((idade_dias%365.25)//30.4375), int((idade_dias%365.25)%30.4375)
    st.success(f"{anos}a {meses}m {dias}d")
    
    st.subheader("📏 Medidas")
    peso = st.number_input("Peso (kg)", 0.5, 100.0, 10.0, step=0.1)
    estatura = st.number_input("Estatura (cm)", 30.0, 150.0, 80.0, step=0.5)
    pc = st.number_input("PC (cm)", 20.0, 70.0, 45.0, step=0.1)

# --- CSS ESTILIZADO (BLOCKS E CARDS) ---
tema_cor = "#0d47a1" if sexo == "Masculino" else "#880e4f"
st.markdown(f"""
<style>
:root {{ --title-color: {tema_cor}; }}
.stApp {{ background-color: {'#f0f8ff' if sexo == 'Masculino' else '#fff0f5'}; }}
h1, h2, h3, h4 {{ color: var(--title-color) !important; }}

/* Bloco de Vacina */
.vax-block {{
    background: white; border-radius: 12px; border: 2px solid var(--title-color);
    margin-bottom: 20px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.08);
}}
.vax-header {{
    padding: 10px 15px; color: white; font-weight: bold; font-size: 18px;
}}
.vax-table {{
    width: 100%; border-collapse: collapse; background: white;
}}
.vax-table th {{
    background: #f8f9fa; color: #555; font-size: 13px; text-align: left; padding: 8px 15px; border-bottom: 1px solid #eee;
}}
.vax-table td {{
    padding: 10px 15px; border-bottom: 1px solid #eee; font-size: 14px; color: #333;
}}

/* Critérios Card */
.crit-card {{
    padding: 15px; border-radius: 8px; color: white; margin-bottom: 20px;
}}
</style>
""", unsafe_allow_html=True)

st.title("🩺 Prontuário Pediátrico Interativo")

if tabelas_oms:
    imc = peso / ((estatura/100)**2)
    idade_meses_float = idade_dias / 30.4375
    
    tabs = st.tabs(["📈 Crescimento", "🧠 Desenvolvimento", "💉 Vacinação", "📝 Orientações", "💊 Suplementação"])

    with tabs[0]: # CRESCIMENTO
        if idade_meses_float <= 24: fx, r_x = "0 a 2 anos", [0, 24]
        elif idade_meses_float <= 60: fx, r_x = "2 a 5 anos", [24, 60]
        else: fx, r_x = "5 a 10 anos", [60, 120]
        
        stabs = st.tabs(["⚖️ Peso", "📏 Estatura", "🧮 IMC", "🧠 PC"])
        cfg = [
            ("Peso", "Peso/Idade", "kg", peso, 1.0, fx, r_x),
            ("Estatura", "Estatura/Idade", "cm", estatura, 5.0, fx, r_x),
            ("IMC", "IMC/Idade", "kg/m²", imc, 1.0, fx, r_x),
            ("PC", "PC/Idade", "cm", pc, 1.0, "0 a 2 anos", [0, 24])
        ]
        
        for s, (k, t, ry, v, dy, fxa, rx) in zip(stabs, cfg):
            with s:
                df = tabelas_oms[sexo][k]
                l = df[df['Day'] == min(int(idade_dias), 1856)].iloc[0]
                z = (((v / l['M'])**l['L'])-1)/(l['L']*l['S']) if l['L'] != 0 else np.log(v/l['M'])/l['S']
                cls, crit, cor = obter_classificacao(z, k)
                
                # Card de Critérios Restaurado
                st.markdown(f"<div class='crit-card' style='background:{cor};'><b>{t} ({fxa})</b><br>Z-Score: {z:.2f} | Percentil: P{norm.cdf(z)*100:.0f}<br><i>Critério: {crit}</i></div>", unsafe_allow_html=True)
                
                fig = go.Figure()
                mx = df['Day'] / 30.4375
                fig.add_trace(go.Scatter(x=mx, y=df['SD2neg'], line=dict(color='red', width=1), name='-2Z'))
                fig.add_trace(go.Scatter(x=mx, y=df['SD0'], line=dict(color='green', width=3), name='Mediana'))
                fig.add_trace(go.Scatter(x=mx, y=df['SD2'], fill='tonexty', fillcolor='rgba(56,142,60,0.1)', line=dict(color='red', width=1), name='+2Z'))
                fig.add_trace(go.Scatter(x=[idade_meses_float], y=[v], mode='markers', marker=dict(size=14, color='royalblue'), name='Paciente'))
                
                # Grades Verticais Fortes de Anos Restauradas
                for a in [12, 24, 36, 48, 60]:
                    if rx[0] <= a <= rx[1]:
                        fig.add_vline(x=a, line_width=2, line_dash="dot", line_color="gray")
                        fig.add_annotation(x=a, y=0.01, yref="paper", text=f"<b>{a//12} ano(s)</b>", showarrow=False)

                fig.update_layout(height=600, xaxis=dict(range=rx, dtick=1, showgrid=True, gridcolor='rgba(0,0,0,0.15)'), template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

    with tabs[1]: # DESENVOLVIMENTO (ESTILO CADERNETA)
        chave, todos_marcos = obter_marcos_caderneta(idade_meses_float)
        st.subheader("📑 Vigilância do Desenvolvimento")
        for f, lista in todos_marcos.items():
            exp = (f == chave)
            with st.expander(f"Marcos: {f}", expanded=exp):
                for m in lista:
                    c1, c2 = st.columns([3, 1])
                    c1.markdown(f"**{m}**")
                    st.radio(f"Status_{m}", ["P", "A", "NV"], horizontal=True, key=f"d_{m}", label_visibility="collapsed")

    with tabs[2]: # VACINAÇÃO (EM BLOCOS IGUAL À IMAGEM)
        st.subheader("💉 Calendário de Vacinação em Blocos")
        esquema = obter_esquema_vacinal()
        
        # Grid de 2 colunas para os blocos
        cols = st.columns(2)
        for i, b in enumerate(esquema):
            with cols[i % 2]:
                rows = "".join([f"<tr><td>{v['nome']}</td><td>{v['dose']}</td><td>{v['doencas']}</td></tr>" for v in b['vacinas']])
                html = f"""
                <div class="vax-block">
                    <div class="vax-header" style="background:{b['cor']};">{b['idade']}</div>
                    <table class="vax-table">
                        <thead><tr><th>Vacina</th><th>Dose</th><th>Doenças Evitadas</th></tr></thead>
                        <tbody>{rows}</tbody>
                    </table>
                </div>
                """
                st.markdown(html, unsafe_allow_html=True)

    with tabs[4]: # SUPLEMENTAÇÃO
        st.subheader("💊 Profilaxia de Ferro (SBP 2021)")
        # (Lógica de cálculo mantida conforme última versão aprovada)
        if prematuro or peso < 2.5: dose = 2
        else: dose = 1 if idade_meses_float >= 3 else 0
        if dose > 0: st.success(f"Dose recomendada: {dose}mg/kg/dia.")
        else: st.warning("Sem indicação formal de início neste momento.")
