import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
from datetime import date
from diretrizes import (obter_classificacao, obter_orientacoes, 
                        obter_esquema_vacinal, obter_marcos_vigilancia)

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Puericultura Digital", layout="wide", initial_sidebar_state="expanded")

# --- CARREGAMENTO DOS FICHEIROS ---
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
                "Peso": carregar_e_limpar("WFA_boys_z_exp.csv"),
                "Estatura": carregar_e_limpar("LFA_boys_z_exp.csv"),
                "IMC": carregar_e_limpar("BFA_boys_z_exp.csv"),
                "PC": carregar_e_limpar("HCFA_boys_z_exp.csv")
            },
            "Feminino": {
                "Peso": carregar_e_limpar("WFA_girls_z_exp.csv"),
                "Estatura": carregar_e_limpar("LFA_girls_z_exp.csv"),
                "IMC": carregar_e_limpar("BFA_girls_z_exp.csv"),
                "PC": carregar_e_limpar("HCFA_girls_z_exp.csv")
            }
        }
    except Exception as e:
        st.error(f"⚠️ Erro ao carregar as tabelas: {e}")
        return None

tabelas_oms = carregar_tabelas()

# --- INTERFACE LATERAL ---
with st.sidebar:
    st.header("👶 Perfil do Paciente")
    sexo = st.selectbox("Sexo", ["Masculino", "Feminino"])
    data_nasc = st.date_input("Nascimento", value=date(2023, 1, 1), format="DD/MM/YYYY")
    data_aval = st.date_input("Consulta Atual", value=date.today(), format="DD/MM/YYYY")
    
    idade_dias_cron = (data_aval - data_nasc).days
    
    st.markdown("---")
    st.subheader("Histórico de Nascimento")
    prematuro = st.checkbox("Bebê Pré-termo (< 37 semanas)")
    idade_dias = idade_dias_cron
    if prematuro:
        sem_gest = st.number_input("Semanas Gestacionais", 24, 36, 34)
        idade_dias = max(0, idade_dias_cron - ((40 - sem_gest) * 7))
        
    peso_nasc = st.number_input("Peso ao nascer (kg)", 0.5, 6.0, 3.2, step=0.1)
    aleitamento_exclusivo = st.checkbox("Aleitamento Materno Exclusivo (AME)?", value=True)

    st.markdown("---")
    st.subheader("📏 Medidas Atuais")
    peso = st.number_input("Peso Atual (kg)", 0.5, 150.0, 10.0, step=0.1)
    estatura = st.number_input("Estatura Atual (cm)", 30.0, 220.0, 75.0, step=0.5)
    pc = st.number_input("PC Atual (cm)", 20.0, 80.0, 45.0, step=0.1)
    
    anos = int(idade_dias // 365.25)
    dias_restantes = idade_dias % 365.25
    meses = int(dias_restantes // 30.4375)
    dias = int(dias_restantes % 30.4375)
    idade_meses_float = idade_dias / 30.4375

# --- ESTILO "CADERNETA" RESPONSIVO ---
tema_cor = "#0d47a1" if sexo == "Masculino" else "#880e4f"
bg_sidebar = "rgba(13, 71, 161, 0.05)" if sexo == "Masculino" else "rgba(136, 14, 79, 0.05)"

st.markdown(f"""
<style>
    h1, h2, h3, h4, h5, h6 {{ color: {tema_cor} !important; }}
    [data-testid="stSidebar"] {{ background-color: {bg_sidebar}; }}
    
    /* Layout Tabelas da Caderneta */
    .caderneta-table {{
        width: 100%; border-collapse: collapse; margin-bottom: 20px;
        background-color: transparent; border: 2px solid {tema_cor};
    }}
    .caderneta-table th {{
        background-color: {tema_cor}; color: white; padding: 10px; text-align: left;
    }}
    .caderneta-table td {{
        border: 1px solid rgba(128,128,128,0.3); padding: 8px; font-size: 14px;
    }}
    
    /* Indicador de Desenvolvimento */
    .marco-row {{
        display: flex; justify-content: space-between; align-items: center;
        padding: 10px; border-bottom: 1px dashed rgba(128,128,128,0.5);
    }}
    .marco-tag {{
        font-weight: bold; color: {tema_cor}; font-size: 0.9em;
    }}
</style>
""", unsafe_allow_html=True)

st.title("🩺 Prontuário Pediátrico Interativo")
st.success(f"**Idade Fisiológica:** {anos} ano(s), {meses} mês(es) e {dias} dia(s)")

if tabelas_oms:
    imc = peso / ((estatura/100)**2)
    idade_busca = min(idade_dias, 1856) 
    
    tab_cresc, tab_desenv, tab_vac, tab_orient, tab_suple = st.tabs(["📈 Crescimento", "🧠 Desenvolvimento", "💉 Vacinação", "📝 Orientações", "💊 Suplementação"])

    # === ABA 1: CRESCIMENTO ===
    with tab_cresc:
        if idade_meses_float <= 24: faixa_titulo, range_grafico = "0 a 2 anos", [0, 24]
        elif idade_meses_float <= 60: faixa_titulo, range_grafico = "2 a 5 anos", [24, 60]
        else: faixa_titulo, range_grafico = "5 a 10 anos", [60, 120]
            
        sub_tabs = st.tabs(["⚖️ Peso", "📏 Estatura", "🧮 IMC", "🧠 PC"])
        config_graficos = [
            ("Peso", "Peso para idade", "Peso (kg)", peso, 1.0, faixa_titulo, range_grafico),
            ("Estatura", "Estatura para idade", "Estatura (cm)", estatura, 5.0, faixa_titulo, range_grafico),
            ("IMC", "IMC para idade", "IMC (kg/m²)", imc, 1.0, faixa_titulo, range_grafico),
            ("PC", "PC para idade", "PC (cm)", pc, 1.0, "0 a 2 anos", [0, 24] if idade_meses_float <= 24 else range_grafico)
        ]

        for stab, (key, titulo_ms, rotulo_y, valor, dtick_y, faixa_etaria, cur_range) in zip(sub_tabs, config_graficos):
            with stab:
                df_curva = tabelas_oms[sexo][key]
                linha = df_curva[df_curva['Day'] == idade_busca].iloc[0]
                z = (((valor / linha['M'])**linha['L'])-1)/(linha['L']*linha['S']) if linha['L'] != 0 else np.log(valor/linha['M'])/linha['S']
                classif, criterio, cor_alerta = obter_classificacao(z, key)
                
                st.markdown(f"<div style='background-color:{tema_cor}; color:white; padding:15px; border-radius:8px 8px 0 0;'><b>{titulo_ms} {faixa_etaria}</b><br>Classificação: {classif} | Z-Score: {z:.2f}</div>", unsafe_allow_html=True)
                
                fig = go.Figure()
                mx = df_curva['Day'] / 30.4375
                # (Lógica de desenho mantida conforme versão anterior)
                fig.add_trace(go.Scatter(x=mx, y=df_curva['SD2neg'], fill='none', line=dict(color='red', width=1), name='-2Z'))
                fig.add_trace(go.Scatter(x=mx, y=df_curva['SD2'], fill='tonexty', fillcolor='rgba(56,142,60,0.1)', line=dict(color='red', width=1), name='+2Z'))
                fig.add_trace(go.Scatter(x=mx, y=df_curva['SD0'], line=dict(color='green', width=3), name='Mediana'))
                fig.add_trace(go.Scatter(x=[idade_meses_float], y=[valor], mode='markers', marker=dict(size=14, color='royalblue'), name='Paciente'))
                
                fig.update_layout(margin=dict(l=40, r=20, t=20, b=40), height=500, xaxis=dict(range=cur_range, dtick=1, showline=True, mirror=True), yaxis=dict(showline=True, mirror=True), legend=dict(orientation="h", y=1.1))
                st.plotly_chart(fig, use_container_width=True, theme="streamlit")

    # === ABA 2: DESENVOLVIMENTO (ESTILO VIGILÂNCIA CADERNETA) ===
    with tab_desenv:
        faixa_nome, marcos = obter_marcos_vigilancia(idade_meses_float)
        st.subheader(f"🔍 Vigilância do Desenvolvimento ({faixa_nome})")
        st.caption("Marque o status para cada marco conforme observado ou relatado [P = Presente, A = Ausente, NV = Não Verificado]")
        
        for marco in marcos:
            col_text, col_opt = st.columns([3, 2])
            with col_text:
                st.markdown(f"<div class='marco-row'><span>{marco}</span></div>", unsafe_allow_html=True)
            with col_opt:
                st.radio(f"Status_{marco}", ["P", "A", "NV"], horizontal=True, key=f"dev_{marco}", label_visibility="collapsed")

    # === ABA 3: VACINAÇÃO (ESTILO TABELA DA CADERNETA) ===
    with tab_vac:
        st.subheader("💉 Registro de Imunização (PNI)")
        esquema = obter_esquema_vacinal()
        
        html_tabela = f"""
        <table class="caderneta-table">
            <thead>
                <tr>
                    <th>Idade Recomendada</th>
                    <th>Vacina / Dose</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
        """
        for fase in esquema:
            bg_fase = "rgba(128,128,128,0.05)" if fase["idade"] == "Ao nascer" else "transparent"
            for i, (vac, dose) in enumerate(fase["vacinas"]):
                linha_idade = f"<td rowspan='{len(fase['vacinas'])}' style='font-weight:bold;'>{fase['idade']}</td>" if i == 0 else ""
                status_icon = "🟢" if (isinstance(fase["idade"], str) and "nascer" in fase["idade"]) or (isinstance(fase["idade"], int) and fase["idade"] <= idade_meses_float) else "⚪"
                html_tabela += f"<tr style='background-color:{bg_fase};'>{linha_idade}<td>{vac} ({dose})</td><td>{status_icon}</td></tr>"
        
        html_tabela += "</tbody></table>"
        st.markdown(html_tabela, unsafe_allow_html=True)
        st.caption("🟢 Recomendada para a idade atual ou já passada. | ⚪ Dose futura.")

    # === ABA 4: ORIENTAÇÕES ===
    with tab_orient:
        st.subheader("📝 Guia de Puericultura")
        ori = obter_orientacoes(idade_meses_float)
        for cat, texto in ori.items():
            st.markdown(f"**{cat}:** {texto}")

    # === ABA 5: SUPLEMENTAÇÃO (FERRO SBP 2021) ===
    with tab_suple:
        st.subheader("💊 Profilaxia de Ferro e Vitamina D")
        
        opcoes_sais = {
            "Sulfato Ferroso Gotas (25mg Fe/mL) [1 gota = 1mg]": 1.0,
            "Ferripolimaltose Gotas (50mg Fe/mL) [1 gota = 2.5mg]": 2.5,
            "Ferro Quelato Glicinato (Neutrofer) [1 gota = 2.5mg]": 2.5
        }
        escolha = st.selectbox("Selecione o Sal:", list(opcoes_sais.keys()))
        
        # Algoritmo SBP 2021 [cite: 81-90]
        dose_mg = 0
        if prematuro or peso_nasc < 2.5:
            if idade_meses_float >= 1: # Inicia aos 30 dias
                if peso_nasc < 1.0: dose_mg = 4
                elif peso_nasc <= 1.5: dose_mg = 3
                else: dose_mg = 2
        else:
            if aleitamento_exclusivo and idade_meses_float >= 6: dose_mg = 1
            elif not aleitamento_exclusivo and idade_meses_float >= 3: dose_mg = 1
            
        if dose_mg > 0:
            gotas = round((peso * dose_mg) / opcoes_sais[escolha])
            st.success(f"Dose: {dose_mg}mg/kg/dia. Prescrever **{max(1, gotas)} gotas/dia**.")
        else:
            st.warning("Paciente fora da janela de início ou sem indicação de profilaxia no momento.")
