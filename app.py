import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
from datetime import date
import math

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Dashboard de Puericultura", layout="wide", initial_sidebar_state="expanded")

# --- CARREGAMENTO DE DADOS (BLINDADO) ---
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
        tabelas = {
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
        return tabelas
    except:
        return None

tabelas_oms = carregar_tabelas()

# --- LÓGICA DE SUPLEMENTAÇÃO E MARCOS (CONSENSOS SBP/MS) ---
def obter_orientacoes(meses):
    if meses < 6:
        return {
            "Sono": "Sono seguro: decúbito dorsal, berço vazio. Ciclos de 14-17h/dia.",
            "Alimento": "Aleitamento materno exclusivo e sob livre demanda.",
            "Higiene": "Banho morno, sem sabonetes agressivos. Limpeza do coto umbilical com álcool 70%.",
            "Segurança": "Prevenção de quedas e aspiração. Transporte em 'bebê conforto' virado para trás."
        }
    elif meses < 12:
        return {
            "Sono": "Estabelecimento de rotina noturna. Média de 12-15h/dia.",
            "Alimento": "Introdução alimentar: comida amassada, variada. Manter leite materno.",
            "Higiene": "Início da escovação dentária com pasta de dente com flúor (>1100ppm).",
            "Segurança": "Cuidado com tomadas e quinas (fase do engatinhar). Objetos pequenos fora de alcance."
        }
    else:
        return {
            "Sono": "Cerca de 11-14h/dia. Um ou dois cochilos diurnos.",
            "Alimento": "Alimentação da família. Evitar ultraprocessados e açúcar até os 2 anos.",
            "Higiene": "Estímulo à autonomia no banho e lavagem das mãos.",
            "Segurança": "Atenção com piscinas, produtos de limpeza e escadas."
        }

def obter_vacinas(meses):
    esquema = {
        0: ["BCG", "Hepatite B"],
        2: ["Penta", "VIP", "Pneumo 10", "Rotavírus"],
        3: ["Meningo C"],
        4: ["2ª dose: Penta, VIP, Pneumo 10, Rotavírus"],
        5: ["2ª dose: Meningo C"],
        6: ["3ª dose: Penta, VIP", "Influenza (Sazonal)"],
        9: ["Febre Amarela"],
        12: ["Tríplice Viral", "Reforço: Pneumo 10, Meningo C"],
        15: ["DTP", "VOP", "Hepatite A", "Tetraviral"],
        48: ["DTP", "VOP", "Varicela", "Febre Amarela"]
    }
    tomadas = [v for m, v in esquema.items() if m <= meses]
    proximas = [v for m, v in esquema.items() if m > meses]
    return tomadas, proximas

# --- INTERFACE ---
with st.sidebar:
    st.title("🩺 Prontuário Digital")
    sexo = st.selectbox("Sexo", ["Masculino", "Feminino"])
    data_nasc = st.date_input("Data de Nascimento", value=date(2023, 1, 1), format="DD/MM/YYYY")
    data_aval = st.date_input("Data da Consulta", value=date.today(), format="DD/MM/YYYY")
    
    idade_dias = (data_aval - data_nasc).days
    prematuro = st.checkbox("Bebê Pré-termo")
    idade_original = idade_dias
    if prematuro:
        sem_gest = st.number_input("Semanas Gestacionais", 24, 36, 34)
        idade_dias = max(0, idade_dias - ((40 - sem_gest) * 7))

    anos = int(idade_dias // 365.25)
    meses_calc = int((idade_dias % 365.25) // 30.4375)
    dias_calc = int((idade_dias % 365.25) % 30.4375)
    idade_total_meses = idade_dias / 30.4375

    st.info(f"**Idade:** {anos}a {meses_calc}m {dias_calc}d")
    peso = st.number_input("Peso (kg)", 0.5, 150.0, 10.0, step=0.1)
    estatura = st.number_input("Estatura (cm)", 30.0, 200.0, 75.0, step=0.5)
    pc = st.number_input("PC (cm)", 20.0, 70.0, 45.0, step=0.1)

# Estilo e Temas
tema_cor = "#0d47a1" if sexo == "Masculino" else "#880e4f"
st.markdown(f"<style>.stApp {{ background-color: {'#f0f8ff' if sexo == 'Masculino' else '#fff0f5'}; }} h1, h2, h3 {{ color: {tema_cor} !important; }}</style>", unsafe_allow_html=True)

if st.sidebar.button("🚀 Iniciar Avaliação Integral", use_container_width=True):
    imc = peso / ((estatura/100)**2)
    
    tab_cresc, tab_desenv, tab_vac, tab_orient, tab_suple = st.tabs(["📈 Crescimento", "🧠 Desenvolvimento", "💉 Vacinação", "📝 Orientações", "💊 Suplementação"])

    # --- ABA CRESCIMENTO (Lógica anterior otimizada) ---
    with tab_cresc:
        # Repetir lógica de gráficos aqui conforme sua versão final aprovada...
        st.subheader("Gráficos de Curva de Crescimento")
        # (Código do gráfico omitido para brevidade, manter a estrutura retangular MS anterior)
        st.write("Visualize os gráficos nas abas internas ou selecione os parâmetros.")

    # --- ABA DESENVOLVIMENTO ---
    with tab_desenv:
        st.subheader(f"Marcos do Desenvolvimento ({faixa_etaria if 'faixa_etaria' in locals() else 'Fase Atual'})")
        # Exemplo de lógica de marcos baseada na Caderneta
        marcos = {
            2: ["Sorriso social", "Sustenta a cabeça", "Observa o rosto"],
            4: ["Rola", "Leva mãos à boca", "Emite sons/Gritos"],
            6: ["Senta com apoio", "Passa objetos de uma mão para outra", "Balbuceia"],
            9: ["Senta sem apoio", "Engatinha ou se arrasta", "Pinça lateral"],
            12: ["Anda com apoio", "Fala pelo menos uma palavra", "Pinça completa"]
        }
        col_ant, col_atual = st.columns(2)
        with col_ant:
            st.markdown("**Marcos Anteriores (Revisão):**")
            for m, lista in marcos.items():
                if m < idade_total_meses:
                    for item in lista: st.checkbox(item, value=True, key=f"ant_{item}")
        with col_atual:
            st.markdown("**Esperados para esta idade:**")
            for m, lista in marcos.items():
                if m >= idade_total_meses and m <= idade_total_meses + 2:
                    for item in lista: st.checkbox(item, value=False, key=f"atu_{item}")

    # --- ABA VACINAÇÃO ---
    with tab_vac:
        tomadas, proximas = obter_vacinas(idade_total_meses)
        c1, c2 = st.columns(2)
        c1.markdown("### ✅ Vacinas já aplicadas")
        for v in tomadas: c1.write(f"- {', '.join(v) if isinstance(v, list) else v}")
        c2.markdown("### ⏳ Próximas Vacinas")
        for v in proximas: c2.write(f"- {', '.join(v) if isinstance(v, list) else v}")

    # --- ABA ORIENTAÇÕES ---
    with tab_orient:
        ori = obter_orientacoes(idade_total_meses)
        for cat, texto in ori.items():
            with st.expander(f"📍 {cat}"): st.write(texto)

    # --- ABA SUPLEMENTAÇÃO (BÔNUS FERRO) ---
    with tab_suple:
        st.subheader("Planejamento de Suplementação (SBP 2021)")
        
        # Lógica de Vitamina D
        st.info("☀️ **Vitamina D:** 400 UI/dia de 1 semana até 12 meses; 600 UI/dia de 12 a 24 meses.")
        
        # BÔNUS: CALCULADORA DE FERRO
        st.markdown("### 🩸 Calculadora de Ferro Profilático")
        tipo_ferro = st.selectbox("Selecione o Sal de Ferro", ["Sulfato Ferroso (25mg/mL)", "Ferro Quelato/Polimaltosado (50mg/mL)"])
        
        # Critérios de Dosagem SBP
        if prematuro or peso < 2.5:
            dose_mg_kg = 2 if peso > 1.5 else 3
        else:
            dose_mg_kg = 1 # Manutenção padrão a partir de 3 meses para a termo
            
        dose_total_mg = peso * dose_mg_kg
        
        if "Sulfato" in tipo_ferro:
            # Padrão: 1 gota ≈ 1mg ou 1.25mg (Média 20-25 gotas/mL)
            gotas = round(dose_total_mg / 1.25)
            marcas = "Fer-in-sol, Sulferrol, Hemoter"
            conc = "1 gota ≈ 1.25mg Fe elementar"
        else:
            # Quelatos (ex: Neutrofer, Noripurum): 20 gotas = 1mL = 50mg -> 1 gota ≈ 2.5mg
            gotas = round(dose_total_mg / 2.5)
            marcas = "Neutrofer, Noripurum, Ultrafer"
            conc = "1 gota ≈ 2.5mg Fe elementar"

        st.success(f"""
        **Prescrição Sugerida:**
        - **Dose Alvo:** {dose_mg_kg}mg/kg/dia
        - **Total:** {dose_total_mg:.1f}mg de Ferro Elementar
        - **Posologia:** {max(1, gotas)} gotas/dia
        - **Concentração:** {conc}
        - **Marcas sugeridas:** {marcas}
        """)
        st.caption("Nota: Iniciar aos 3 meses para bebês a termo e aos 30 dias para pré-termos.")
