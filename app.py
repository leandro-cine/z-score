import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
from scipy.stats import norm
from datetime import date

# --- CARREGAMENTO DOS DADOS REAIS ---
@st.cache_data
def carregar_tabelas():
    def carregar_e_limpar(nome_arquivo):
        # 1. Tenta abrir no padrão Internacional da OMS (separador = vírgula, decimal = ponto)
        try:
            df = pd.read_csv(nome_arquivo, sep=',', decimal='.', encoding='utf-8-sig')
            if len(df.columns) < 5: # Se leu tudo como 1 coluna só, força erro para ir pro plano B
                raise ValueError
        except:
            # 2. Se falhar, tenta o padrão Brasil/Excel (separador = ponto e vírgula, decimal = vírgula)
            df = pd.read_csv(nome_arquivo, sep=';', decimal=',', encoding='utf-8-sig')
        
        # Limpa os cabeçalhos para evitar espaços invisíveis
        df.columns = df.columns.str.strip()
        df.rename(columns={df.columns[0]: 'Day'}, inplace=True)
        
        # Converte TUDO para número matemático de forma limpa (qualquer texto vira NaN)
        df = df.apply(pd.to_numeric, errors='coerce')
        
        # Apaga linhas sujas (ex: cabeçalhos duplos da OMS) que viraram NaN na coluna de Dias
        df = df.dropna(subset=['Day'])
        
        # Garante que os dias são números inteiros puros para a busca funcionar 100%
        df['Day'] = df['Day'].astype(int)
        
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
    except Exception as e:
        st.error(f"⚠️ Erro ao carregar as tabelas: {e}")
        return None

tabelas_oms = carregar_tabelas()

# --- FUNÇÕES MATEMÁTICAS E CLÍNICAS ---
def calcular_z_score(medida, l, m, s):
    if l == 0:
        return np.log(medida / m) / s
    return (((medida / m) ** l) - 1) / (l * s)

def classificar_z_score(z, parametro):
    if z < -3: return "Risco Grave (Muito Baixo)", "#d32f2f"
    elif -3 <= z < -2: return "Atenção (Baixo)", "#f57c00"
    elif -2 <= z <= 2: return "Adequado (Eutrofia)", "#388e3c"
    elif 2 < z <= 3:
        if parametro == "Estatura": return "Adequado", "#388e3c"
        return "Atenção (Elevado)", "#f57c00"
    else:
        if parametro == "Estatura": return "Muito Elevado", "#1976d2"
        return "Risco Grave (Muito Elevado)", "#d32f2f"

# --- BARRA LATERAL: DADOS DO PACIENTE ---
with st.sidebar:
    st.header("📋 Dados do Paciente")
    sexo = st.selectbox("Sexo", ["Masculino", "Feminino"])
    
    # Entradas de Data
    data_nasc = st.date_input("Data de Nascimento", value=date(2023, 1, 1), max_value="today", format="DD/MM/YYYY")
    data_aval = st.date_input("Data da Avaliação", value="today", format="DD/MM/YYYY")
    
    # Cálculo exato de dias
    idade_dias_cronologica = (data_aval - data_nasc).days

    if idade_dias_cronologica < 0:
        st.error("A data de avaliação não pode ser anterior ao nascimento.")
        st.stop()
        
    prematuro = st.checkbox("Nascido Pré-termo (< 37 semanas)")
    idade_dias_calc = idade_dias_cronologica
    
    if prematuro:
        semanas_gestacao = st.number_input("Semanas de Gestação ao Nascer", min_value=24, max_value=36, step=1, value=34)
        dias_perdidos = (40 - semanas_gestacao) * 7
        idade_dias_calc = max(0, idade_dias_cronologica - dias_perdidos)
        st.warning("Usando Idade Corrigida para os cálculos.")
    
    # Decomposição da idade em Meses, Semanas e Dias
    meses = int(idade_dias_calc // 30.4375)
    dias_sobra = int(idade_dias_calc % 30.4375)
    semanas = dias_sobra // 7
    dias_finais = dias_sobra % 7
    
    st.success(f"**Idade exata:** {meses} meses, {semanas} sem. e {dias_finais} dias.\n\n*(Total: {idade_dias_calc} dias)*")

    st.header("📏 Antropometria Atual")
    peso = st.number_input("Peso (kg)", min_value=0.5, step=0.1, value=7.0)
    estatura = st.number_input("Estatura/Comprimento (cm)", min_value=30.0, step=0.5, value=65.0)
    pc = st.number_input("Perímetro Cefálico (cm)", min_value=20.0, step=0.5, value=42.0)

# --- PROCESSAMENTO E GRÁFICOS ---
if st.sidebar.button("Gerar Avaliação Completa", type="primary") and tabelas_oms:
    
    imc = peso / ((estatura/100)**2)
    idade_busca = min(idade_dias_calc, 1856) # Limite de 5 anos da tabela
    
    def obter_linha_oms(parametro):
        df = tabelas_oms[sexo][parametro]
        return df[df['Day'] == idade_busca].iloc[0]

    linha_peso = obter_linha_oms("Peso")
    linha_est = obter_linha_oms("Estatura")
    linha_imc = obter_linha_oms("IMC")
    linha_pc = obter_linha_oms("PC")
    
    z_peso = calcular_z_score(peso, linha_peso['L'], linha_peso['M'], linha_peso['S'])
    z_est = calcular_z_score(estatura, linha_est['L'], linha_est['M'], linha_est['S'])
    z_imc = calcular_z_score(imc, linha_imc['L'], linha_imc['M'], linha_imc['S'])
    z_pc = calcular_z_score(pc, linha_pc['L'], linha_pc['M'], linha_pc['S'])

    st.subheader(f"Resumo Clínico - Avaliação de {data_aval.strftime('%d/%m/%Y')}")
    
    aba1, aba2, aba3, aba4 = st.tabs(["⚖️ Peso/Idade", "📏 Estatura/Idade", "🧮 IMC/Idade", "🧠 Perímetro Cefálico"])
    
    def plotar_curva(df_oms, titulo, parametro_y, z_score, medida_atual):
        fig = go.Figure()
        meses_x = df_oms['Day'] / 30.4375 
        
        fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD3'], name='+3 Z', line=dict(color='black', width=1)))
        fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD2'], name='+2 Z', line=dict(color='red', width=1)))
        fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD0'], name='Mediana', line=dict(color='green', width=2)))
        fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD2neg'], name='-2 Z', line=dict(color='red', width=1)))
        fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD3neg'], name='-3 Z', line=dict(color='black', width=1)))
        
        idade_paciente_meses = idade_busca / 30.4375
        fig.add_trace(go.Scatter(x=[idade_paciente_meses], y=[medida_atual], mode='markers', 
                                 marker=dict(color='blue', size=14, symbol='x'), name='Paciente Atual'))
        
        fig.update_layout(title=titulo, xaxis_title="Idade (meses)", yaxis_title=parametro_y, template="plotly_white")
        return fig

    with aba1:
        classif, cor = classificar_z_score(z_peso, "Peso")
        st.markdown(f"<h4 style='color:{cor};'>Z-Score: {z_peso:.2f} | Percentil: P{norm.cdf(z_peso)*100:.0f} | {classif}</h4>", unsafe_allow_html=True)
        st.plotly_chart(plotar_curva(tabelas_oms[sexo]["Peso"], "Peso por Idade", "Peso (kg)", z_peso, peso), use_container_width=True)

    with aba2:
        classif, cor = classificar_z_score(z_est, "Estatura")
        st.markdown(f"<h4 style='color:{cor};'>Z-Score: {z_est:.2f} | Percentil: P{norm.cdf(z_est)*100:.0f} | {classif}</h4>", unsafe_allow_html=True)
        st.plotly_chart(plotar_curva(tabelas_oms[sexo]["Estatura"], "Estatura por Idade", "Estatura (cm)", z_est, estatura), use_container_width=True)

    with aba3:
        classif, cor = classificar_z_score(z_imc, "IMC")
        st.markdown(f"**IMC Calculado:** {imc:.1f} kg/m²")
        st.markdown(f"<h4 style='color:{cor};'>Z-Score: {z_imc:.2f} | Percentil: P{norm.cdf(z_imc)*100:.0f} | {classif}</h4>", unsafe_allow_html=True)
        st.plotly_chart(plotar_curva(tabelas_oms[sexo]["IMC"], "IMC por Idade", "IMC (kg/m²)", z_imc, imc), use_container_width=True)

    with aba4:
        classif, cor = classificar_z_score(z_pc, "PC")
        st.markdown(f"<h4 style='color:{cor};'>Z-Score: {z_pc:.2f} | Percentil: P{norm.cdf(z_pc)*100:.0f} | {classif}</h4>", unsafe_allow_html=True)
        st.plotly_chart(plotar_curva(tabelas_oms[sexo]["PC"], "Perímetro Cefálico por Idade", "PC (cm)", z_pc, pc), use_container_width=True)
