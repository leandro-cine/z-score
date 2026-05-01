import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
from datetime import date

# --- CONFIGURAÇÃO DA PÁGINA (Modo Amplo) ---
st.set_page_config(page_title="Dashboard Pediátrico", layout="wide")

# --- CARREGAMENTO DOS DADOS REAIS (BLINDADO) ---
@st.cache_data
def carregar_tabelas():
    def carregar_e_limpar(nome_arquivo):
        try:
            df = pd.read_csv(nome_arquivo, sep=',', decimal='.', encoding='utf-8-sig')
            if len(df.columns) < 5: raise ValueError
        except:
            df = pd.read_csv(nome_arquivo, sep=';', decimal=',', encoding='utf-8-sig')
        
        df.columns = df.columns.str.strip()
        df.rename(columns={df.columns[0]: 'Day'}, inplace=True)
        df = df.apply(pd.to_numeric, errors='coerce')
        df = df.dropna(subset=['Day'])
        df['Day'] = df['Day'].astype(int)
        
        # Garante que temos uma coluna limite para o sombreado externo, se faltar na OMS
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
    except Exception as e:
        st.error(f"⚠️ Erro ao carregar as tabelas: {e}")
        return None

tabelas_oms = carregar_tabelas()

# --- FUNÇÕES MATEMÁTICAS E CLÍNICAS ---
def calcular_z_score(medida, l, m, s):
    if l == 0: return np.log(medida / m) / s
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
    
    meses = int(idade_dias_calc // 30.4375)
    dias_sobra = int(idade_dias_calc % 30.4375)
    semanas = dias_sobra // 7
    dias_finais = dias_sobra % 7
    
    st.success(f"**Idade:** {meses} meses, {semanas} sem. e {dias_finais} dias.\n\n*(Total: {idade_dias_calc} dias)*")

    st.header("📏 Antropometria Atual")
    peso = st.number_input("Peso (kg)", min_value=0.5, step=0.1, value=12.0)
    estatura = st.number_input("Estatura/Comprimento (cm)", min_value=30.0, step=0.5, value=85.0)
    pc = st.number_input("Perímetro Cefálico (cm)", min_value=20.0, step=0.5, value=48.0)

# --- TEMA DINÂMICO DO SITE ---
if sexo == "Masculino":
    cor_fundo = "#f0f8ff" # Azul Alice
    cor_titulo = "#0d47a1" # Azul Escuro
else:
    cor_fundo = "#fff0f5" # Rosa Lavanda
    cor_titulo = "#880e4f" # Rosa Escuro

st.markdown(f"""
<style>
    .stApp {{ background-color: {cor_fundo}; }}
    h1, h2, h3 {{ color: {cor_titulo} !important; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 20px; }}
    .stTabs [data-baseweb="tab"] {{ height: 50px; font-size: 16px; font-weight: bold; }}
</style>
""", unsafe_allow_html=True)

st.title("📊 Avaliação de Crescimento Infantil")

# --- PROCESSAMENTO E GRÁFICOS ---
if st.sidebar.button("Gerar Avaliação Completa", type="primary", use_container_width=True) and tabelas_oms:
    
    imc = peso / ((estatura/100)**2)
    # Limita a busca a 1856 dias (limite das tabelas atuais de 5 anos)
    idade_busca = min(idade_dias_calc, 1856) 
    
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
    
    aba1, aba2, aba3, aba4 = st.tabs(["⚖️ Peso/Idade", "📏 Estatura/Idade", "🧮 IMC/Idade", "🧠 Perímetro Cefálico"])
    
    # FUNÇÃO DO GRÁFICO (SOMBRADOS, ZOOM E LINHAS NÍTIDAS)
    def plotar_curva(df_oms, titulo, parametro_y, z_score, medida_atual):
        fig = go.Figure()
        meses_x = df_oms['Day'] / 30.4375 
        
        # --- PREENCHIMENTOS SOMBREADOS ---
        # 1. Base invisível inferior
        fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD4neg'], line=dict(width=0), showlegend=False, hoverinfo='skip'))
        # 2. Área Vermelha (Abaixo de -3Z)
        fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD3neg'], fill='tonexty', fillcolor='rgba(211,47,47,0.15)', line=dict(color='#d32f2f', width=1, dash='dash'), name='-3 Z'))
        # 3. Área Laranja (-3Z a -2Z)
        fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD2neg'], fill='tonexty', fillcolor='rgba(245,124,0,0.15)', line=dict(color='#f57c00', width=1), name='-2 Z'))
        # 4. Área Verde (Adequado: -2Z a +2Z)
        fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD2'], fill='tonexty', fillcolor='rgba(56,142,60,0.15)', line=dict(color='#f57c00', width=1), name='+2 Z'))
        # 5. Área Laranja (+2Z a +3Z)
        fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD3'], fill='tonexty', fillcolor='rgba(245,124,0,0.15)', line=dict(color='#d32f2f', width=1, dash='dash'), name='+3 Z'))
        # 6. Área Vermelha (Acima de +3Z)
        fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD4'], fill='tonexty', fillcolor='rgba(211,47,47,0.15)', line=dict(width=0), showlegend=False, hoverinfo='skip'))
        
        # Linha da Mediana Verde Escura
        fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD0'], line=dict(color='#2e7d32', width=2.5), name='Mediana (0 Z)'))
        
        # Ponto do paciente (Grande e em destaque)
        idade_paciente_meses = idade_dias_calc / 30.4375
        fig.add_trace(go.Scatter(x=[idade_paciente_meses], y=[medida_atual], mode='markers', 
                                 marker=dict(color='black', size=16, symbol='circle', line=dict(color='white', width=2)), name='Paciente Atual'))
        
        # --- ZOOM INTELIGENTE ---
        if idade_paciente_meses <= 24:
            range_x = [0, 24]
            dtick_x = 2
        elif idade_paciente_meses <= 60:
            range_x = [24, 60]
            dtick_x = 6
        else:
            # Prepara a janela para as futuras planilhas de 5-10 anos
            range_x = [60, 120]
            dtick_x = 12

        # --- LINHAS DE GRADE (ANOS NÍTIDOS) ---
        for ano_meses in [12, 24, 36, 48, 60, 72, 84, 96, 108, 120]:
            if range_x[0] <= ano_meses <= range_x[1]:
                # Adiciona linha vertical forte
                fig.add_vline(x=ano_meses, line_width=1.5, line_dash="dot", line_color="rgba(0,0,0,0.4)")
                # Adiciona o texto "1 Ano", "2 Anos" no eixo
                fig.add_annotation(x=ano_meses, y=1, yref="paper", text=f"{ano_meses//12} Ano(s)", showarrow=False, yanchor="bottom", font=dict(color="black", size=12))

        # --- APROVEITAMENTO DE TELA ---
        fig.update_layout(
            title=titulo, 
            xaxis_title="Idade (meses)", 
            yaxis_title=parametro_y, 
            template="plotly_white",
            height=650, # Aumenta bastante a altura do gráfico
            margin=dict(l=40, r=40, t=60, b=40), # Reduz o espaço em branco ao redor
            xaxis=dict(range=range_x, dtick=dtick_x, showgrid=True, gridcolor='rgba(0,0,0,0.1)', zeroline=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)', zeroline=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1) # Coloca legenda no topo em 1 linha
        )
        return fig

    # --- Renderização das Abas ---
    with aba1:
        classif, cor = classificar_z_score(z_peso, "Peso")
        st.markdown(f"<div style='padding:10px; border-radius:5px; background-color:{cor}; color:white; font-size:18px;'><strong>Z-Score: {z_peso:.2f} | Percentil: P{norm.cdf(z_peso)*100:.0f} | Classificação: {classif}</strong></div>", unsafe_allow_html=True)
        st.plotly_chart(plotar_curva(tabelas_oms[sexo]["Peso"], "Curva de Peso por Idade", "Peso (kg)", z_peso, peso), use_container_width=True)

    with aba2:
        classif, cor = classificar_z_score(z_est, "Estatura")
        st.markdown(f"<div style='padding:10px; border-radius:5px; background-color:{cor}; color:white; font-size:18px;'><strong>Z-Score: {z_est:.2f} | Percentil: P{norm.cdf(z_est)*100:.0f} | Classificação: {classif}</strong></div>", unsafe_allow_html=True)
        st.plotly_chart(plotar_curva(tabelas_oms[sexo]["Estatura"], "Curva de Estatura por Idade", "Estatura (cm)", z_est, estatura), use_container_width=True)

    with aba3:
        classif, cor = classificar_z_score(z_imc, "IMC")
        st.markdown(f"<div style='padding:10px; border-radius:5px; background-color:{cor}; color:white; font-size:18px;'><strong>IMC Atual: {imc:.1f} kg/m² | Z-Score: {z_imc:.2f} | Percentil: P{norm.cdf(z_imc)*100:.0f} | Classificação: {classif}</strong></div>", unsafe_allow_html=True)
        st.plotly_chart(plotar_curva(tabelas_oms[sexo]["IMC"], "Curva de IMC por Idade", "IMC (kg/m²)", z_imc, imc), use_container_width=True)

    with aba4:
        classif, cor = classificar_z_score(z_pc, "PC")
        st.markdown(f"<div style='padding:10px; border-radius:5px; background-color:{cor}; color:white; font-size:18px;'><strong>Z-Score: {z_pc:.2f} | Percentil: P{norm.cdf(z_pc)*100:.0f} | Classificação: {classif}</strong></div>", unsafe_allow_html=True)
        st.plotly_chart(plotar_curva(tabelas_oms[sexo]["PC"], "Perímetro Cefálico por Idade", "PC (cm)", z_pc, pc), use_container_width=True)
