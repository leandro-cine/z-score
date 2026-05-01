import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
from datetime import date

# --- CONFIGURAÇÃO DA PÁGINA ---
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
        
        # Garante limites para o sombreado externo
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

# --- FUNÇÕES MATEMÁTICAS E REGRAS DO MINISTÉRIO DA SAÚDE ---
def calcular_z_score(medida, l, m, s):
    if l == 0: return np.log(medida / m) / s
    return (((medida / m) ** l) - 1) / (l * s)

def classificar_z_score(z, parametro):
    """Aplica as regras exatas solicitadas e retorna: Classificação, Regra Escrita e Cor"""
    if parametro == "PC":
        if z > 2: return "PC acima do esperado para a idade", "> +2 escores z", "#f57c00" # Laranja
        elif z >= -2: return "PC adequado para idade", "≤ +2 escores z e ≥ -2 escores z", "#388e3c" # Verde
        else: return "PC abaixo do esperado para idade", "< -2 escores z", "#d32f2f" # Vermelho
        
    elif parametro == "Peso":
        if z > 2: return "Peso elevado para idade", "> escore-z +2", "#f57c00"
        elif z >= -2: return "Peso adequado para idade", "≥ escore-z -2 e ≤ escore-z +2", "#388e3c"
        elif z >= -3: return "Baixo peso para idade", "≥ escore-z -3 e < escore-z -2", "#f57c00"
        else: return "Muito baixo peso para a idade", "< escore-z -3", "#d32f2f"
        
    elif parametro == "Estatura":
        if z >= -2: return "Comprimento adequado para idade", "≥ escore-z -2", "#388e3c"
        elif z >= -3: return "Baixo comprimento para idade", "≥ escore-z -3 e < escore-z -2", "#f57c00"
        else: return "Muito baixo comprimento para idade", "< escore-z -3", "#d32f2f"
        
    elif parametro == "IMC":
        if z > 3: return "Obesidade", "> escore-z +3", "#d32f2f" # Vermelho
        elif z > 2: return "Sobrepeso", "> escore-z +2 e ≤ escore-z +3", "#f57c00" # Laranja
        elif z > 1: return "Risco de sobrepeso", "> escore-z +1 e ≤ escore-z +2", "#fbc02d" # Amarelo/Mostarda
        elif z >= -2: return "Eutrofia", "≥ escore-z -2 e ≤ escore-z +1", "#388e3c" # Verde
        elif z >= -3: return "Magreza", "≥ escore-z -3 e < escore-z -2", "#f57c00" # Laranja
        else: return "Magreza acentuada", "< escore-z -3", "#d32f2f" # Vermelho

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📋 Dados do Paciente")
    sexo = st.selectbox("Sexo", ["Masculino", "Feminino"])
    
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
        idade_dias_calc = max(0, idade_dias_cronologica - ((40 - semanas_gestacao) * 7))
        st.warning("Usando Idade Corrigida para os cálculos.")
    
    meses, dias_sobra = int(idade_dias_calc // 30.4375), int(idade_dias_calc % 30.4375)
    st.success(f"**Idade:** {meses} meses, {dias_sobra // 7} sem. e {dias_sobra % 7} dias.\n\n*(Total: {idade_dias_calc} dias)*")

    st.header("📏 Antropometria Atual")
    peso = st.number_input("Peso (kg)", min_value=0.5, step=0.1, value=12.0)
    estatura = st.number_input("Estatura/Comprimento (cm)", min_value=30.0, step=0.5, value=85.0)
    pc = st.number_input("Perímetro Cefálico (cm)", min_value=20.0, step=0.5, value=48.0)

# --- TEMA DINÂMICO ---
if sexo == "Masculino":
    cor_fundo, cor_titulo = "#f0f8ff", "#0d47a1"
else:
    cor_fundo, cor_titulo = "#fff0f5", "#880e4f"

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
    idade_busca = min(idade_dias_calc, 1856) 
    
    def obter_linha_oms(parametro):
        return tabelas_oms[sexo][parametro][tabelas_oms[sexo][parametro]['Day'] == idade_busca].iloc[0]

    linha_peso, linha_est = obter_linha_oms("Peso"), obter_linha_oms("Estatura")
    linha_imc, linha_pc = obter_linha_oms("IMC"), obter_linha_oms("PC")
    
    z_peso = calcular_z_score(peso, linha_peso['L'], linha_peso['M'], linha_peso['S'])
    z_est = calcular_z_score(estatura, linha_est['L'], linha_est['M'], linha_est['S'])
    z_imc = calcular_z_score(imc, linha_imc['L'], linha_imc['M'], linha_imc['S'])
    z_pc = calcular_z_score(pc, linha_pc['L'], linha_pc['M'], linha_pc['S'])
    
    aba1, aba2, aba3, aba4 = st.tabs(["⚖️ Peso/Idade", "📏 Estatura/Idade", "🧮 IMC/Idade", "🧠 Perímetro Cefálico"])
    
    # FUNÇÃO DO GRÁFICO (SOMBRADOS ESPECÍFICOS E GRADE MENSAL)
    def plotar_curva(df_oms, titulo, parametro_y, medida_atual, parametro_nome, dtick_y):
        fig = go.Figure()
        meses_x = df_oms['Day'] / 30.4375 
        
        # Desenha as áreas sombreadas dependendo da regra do parâmetro
        fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD4neg'], line=dict(width=0), showlegend=False, hoverinfo='skip'))
        
        if parametro_nome == "IMC":
            fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD3neg'], fill='tonexty', fillcolor='rgba(211,47,47,0.15)', line=dict(color='black', width=1, dash='dash'), name='-3 Z'))
            fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD2neg'], fill='tonexty', fillcolor='rgba(245,124,0,0.15)', line=dict(color='red', width=1), name='-2 Z'))
            fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD1'], fill='tonexty', fillcolor='rgba(56,142,60,0.15)', line=dict(color='#fbc02d', width=1, dash='dash'), name='+1 Z'))
            fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD2'], fill='tonexty', fillcolor='rgba(251,192,45,0.2)', line=dict(color='red', width=1), name='+2 Z'))
            fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD3'], fill='tonexty', fillcolor='rgba(245,124,0,0.15)', line=dict(color='black', width=1, dash='dash'), name='+3 Z'))
            fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD4'], fill='tonexty', fillcolor='rgba(211,47,47,0.15)', line=dict(width=0), showlegend=False, hoverinfo='skip'))
        elif parametro_nome == "Estatura":
            fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD3neg'], fill='tonexty', fillcolor='rgba(211,47,47,0.15)', line=dict(color='black', width=1, dash='dash'), name='-3 Z'))
            fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD2neg'], fill='tonexty', fillcolor='rgba(245,124,0,0.15)', line=dict(color='red', width=1), name='-2 Z'))
            fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD4'], fill='tonexty', fillcolor='rgba(56,142,60,0.15)', line=dict(width=0), showlegend=False, hoverinfo='skip'))
            fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD2'], mode='lines', line=dict(color='red', width=1), name='+2 Z'))
            fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD3'], mode='lines', line=dict(color='black', width=1, dash='dash'), name='+3 Z'))
        elif parametro_nome == "Peso":
            fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD3neg'], fill='tonexty', fillcolor='rgba(211,47,47,0.15)', line=dict(color='black', width=1, dash='dash'), name='-3 Z'))
            fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD2neg'], fill='tonexty', fillcolor='rgba(245,124,0,0.15)', line=dict(color='red', width=1), name='-2 Z'))
            fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD2'], fill='tonexty', fillcolor='rgba(56,142,60,0.15)', line=dict(color='red', width=1), name='+2 Z'))
            fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD4'], fill='tonexty', fillcolor='rgba(245,124,0,0.15)', line=dict(width=0), showlegend=False, hoverinfo='skip'))
            fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD3'], mode='lines', line=dict(color='black', width=1, dash='dash'), name='+3 Z'))
        elif parametro_nome == "PC":
            fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD2neg'], fill='tonexty', fillcolor='rgba(211,47,47,0.15)', line=dict(color='red', width=1), name='-2 Z'))
            fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD2'], fill='tonexty', fillcolor='rgba(56,142,60,0.15)', line=dict(color='red', width=1), name='+2 Z'))
            fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD4'], fill='tonexty', fillcolor='rgba(245,124,0,0.15)', line=dict(width=0), showlegend=False, hoverinfo='skip'))
            fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD3neg'], mode='lines', line=dict(color='black', width=1, dash='dash'), name='-3 Z'))
            fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD3'], mode='lines', line=dict(color='black', width=1, dash='dash'), name='+3 Z'))

        # Linha Mediana e Ponto do Paciente
        fig.add_trace(go.Scatter(x=meses_x, y=df_oms['SD0'], line=dict(color='#2e7d32', width=2.5), name='Mediana (0 Z)'))
        idade_paciente_meses = idade_dias_calc / 30.4375
        fig.add_trace(go.Scatter(x=[idade_paciente_meses], y=[medida_atual], mode='markers', 
                                 marker=dict(color='black', size=16, symbol='circle', line=dict(color='white', width=2)), name='Paciente Atual'))
        
        # Zoom inteligente
        if idade_paciente_meses <= 24: range_x = [0, 24]
        else: range_x = [24, 60]

        # Linhas de anos completos
        for ano_meses in [12, 24, 36, 48, 60]:
            if range_x[0] <= ano_meses <= range_x[1]:
                fig.add_vline(x=ano_meses, line_width=1.5, line_dash="solid", line_color="rgba(0,0,0,0.3)")
                fig.add_annotation(x=ano_meses, y=1, yref="paper", text=f"{ano_meses//12} Ano(s)", showarrow=False, yanchor="bottom", font=dict(color="black", size=12))

        # Configuração da Grade (dtick=1 no eixo X faz 1 linha por mês)
        fig.update_layout(
            title=titulo, 
            xaxis_title="Idade (meses)", 
            yaxis_title=parametro_y, 
            template="plotly_white",
            height=750, # Altura elevada para criar o efeito 'achatado' na horizontal
            margin=dict(l=40, r=40, t=60, b=40),
            xaxis=dict(range=range_x, dtick=1, showgrid=True, gridcolor='rgba(0,0,0,0.15)', zeroline=False),
            yaxis=dict(dtick=dtick_y, showgrid=True, gridcolor='rgba(0,0,0,0.15)', zeroline=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        return fig

    # --- Renderização das Abas (Mostrando a informação do intervalo de forma nítida) ---
    def gerar_card_html(titulo_medida, valor_medida, z, classif, intervalo, cor):
        return f"""
        <div style='padding:15px; border-radius:5px; background-color:{cor}; color:white; font-size:16px; margin-bottom: 20px;'>
            <strong>{titulo_medida}: {valor_medida}</strong><br>
            <strong>Escore-Z: {z:.2f} | Percentil: P{norm.cdf(z)*100:.0f}</strong><hr style="margin: 8px 0; border-color: rgba(255,255,255,0.3);">
            <strong>Classificação:</strong> {classif}<br>
            <strong>Critério:</strong> <i>{intervalo}</i>
        </div>
        """

    with aba1:
        classif, intervalo, cor = classificar_z_score(z_peso, "Peso")
        st.markdown(gerar_card_html("Peso Atual", f"{peso:.2f} kg", z_peso, classif, intervalo, cor), unsafe_allow_html=True)
        st.plotly_chart(plotar_curva(tabelas_oms[sexo]["Peso"], "Peso por Idade", "Peso (kg)", peso, "Peso", 1), use_container_width=True)

    with aba2:
        classif, intervalo, cor = classificar_z_score(z_est, "Estatura")
        st.markdown(gerar_card_html("Estatura Atual", f"{estatura:.1f} cm", z_est, classif, intervalo, cor), unsafe_allow_html=True)
        st.plotly_chart(plotar_curva(tabelas_oms[sexo]["Estatura"], "Estatura por Idade", "Estatura (cm)", estatura, "Estatura", 5), use_container_width=True)

    with aba3:
        classif, intervalo, cor = classificar_z_score(z_imc, "IMC")
        st.markdown(gerar_card_html("IMC Calculado", f"{imc:.1f} kg/m²", z_imc, classif, intervalo, cor), unsafe_allow_html=True)
        st.plotly_chart(plotar_curva(tabelas_oms[sexo]["IMC"], "IMC por Idade", "IMC (kg/m²)", imc, "IMC", 1), use_container_width=True)

    with aba4:
        classif, intervalo, cor = classificar_z_score(z_pc, "PC")
        st.markdown(gerar_card_html("PC Atual", f"{pc:.1f} cm", z_pc, classif, intervalo, cor), unsafe_allow_html=True)
        st.plotly_chart(plotar_curva(tabelas_oms[sexo]["PC"], "Perímetro Cefálico por Idade", "PC (cm)", pc, "PC", 1), use_container_width=True)
