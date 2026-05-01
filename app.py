import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
from datetime import date

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Dashboard Pediátrico", layout="wide", initial_sidebar_state="expanded")

# --- CARREGAMENTO DOS FICHEIROS (BLINDADO) ---
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
        df = df.apply(pd.to_numeric, errors='coerce')
        df = df.dropna(subset=['Day'])
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
    except Exception as e:
        st.error(f"⚠️ Erro ao carregar as tabelas: {e}")
        return None

tabelas_oms = carregar_tabelas()

# --- REGRAS DE CLASSIFICAÇÃO (MINISTÉRIO DA SAÚDE) ---
def obter_classificacao(z, parametro):
    if parametro == "PC":
        if z > 2: return "PC acima do esperado para a idade", "> +2 escores z", "#f57c00"
        elif z >= -2: return "PC adequado para idade", "≤ +2 e ≥ -2 escores z", "#388e3c"
        else: return "PC abaixo do esperado para idade", "< -2 escores z", "#d32f2f"
    elif parametro == "Peso":
        if z > 2: return "Peso elevado para idade", "> escore-z +2", "#f57c00"
        elif z >= -2: return "Peso adequado para idade", "≥ escore-z -2 e ≤ +2", "#388e3c"
        elif z >= -3: return "Baixo peso para idade", "≥ escore-z -3 e < -2", "#f57c00"
        else: return "Muito baixo peso para a idade", "< escore-z -3", "#d32f2f"
    elif parametro == "Estatura":
        if z >= -2: return "Comprimento/Estatura adequada para idade", "≥ escore-z -2", "#388e3c"
        elif z >= -3: return "Baixo(a) comprimento/estatura", "≥ escore-z -3 e < -2", "#f57c00"
        else: return "Muito baixo(a) comprimento/estatura", "< escore-z -3", "#d32f2f"
    elif parametro == "IMC":
        if z > 3: return "Obesidade", "> escore-z +3", "#d32f2f"
        elif z > 2: return "Sobrepeso", "> +2 e ≤ +3", "#f57c00"
        elif z > 1: return "Risco de sobrepeso", "> +1 e ≤ +2", "#fbc02d"
        elif z >= -2: return "Eutrofia", "≥ -2 e ≤ +1", "#388e3c"
        elif z >= -3: return "Magreza", "≥ -3 e < -2", "#f57c00"
        else: return "Magreza acentuada", "< escore-z -3", "#d32f2f"

# --- INTERFACE LATERAL ---
with st.sidebar:
    st.header("👶 Dados do Paciente")
    sexo = st.selectbox("Sexo", ["Masculino", "Feminino"])
    data_nasc = st.date_input("Nascimento", value=date(2023, 1, 1), format="DD/MM/YYYY")
    data_aval = st.date_input("Avaliação", value=date.today(), format="DD/MM/YYYY")
    
    idade_dias = (data_aval - data_nasc).days
    prematuro = st.checkbox("Pré-termo (< 37 semanas)")
    if prematuro:
        sem_gest = st.number_input("Semanas de Gestação", 24, 36, 34)
        idade_dias = max(0, idade_dias - ((40 - sem_gest) * 7))

    # Cálculo da Idade em Anos, Meses e Dias
    anos = int(idade_dias // 365.25)
    dias_restantes = idade_dias % 365.25
    meses = int(dias_restantes // 30.4375)
    dias = int(dias_restantes % 30.4375)
    
    st.success(f"**Idade exata:**\n\n{anos} ano(s), {meses} mês(es) e {dias} dia(s)\n\n*(Total de {idade_dias} dias)*")

    st.header("📏 Medidas")
    peso = st.number_input("Peso (kg)", 0.5, 100.0, 10.0, step=0.1)
    estatura = st.number_input("Estatura (cm)", 30.0, 200.0, 75.0, step=0.5)
    pc = st.number_input("PC (cm)", 20.0, 70.0, 45.0, step=0.1)

# Estilo Dinâmico (Azul/Rosa) e Responsividade
tema_cor = "#0d47a1" if sexo == "Masculino" else "#880e4f"
tema_bg = "#f0f8ff" if sexo == "Masculino" else "#fff0f5"

st.markdown(f"""
<style>
    .stApp {{ background-color: {tema_bg}; }}
    .header-bar {{
        background-color: {tema_cor};
        color: white;
        padding: 15px;
        border-radius: 8px 8px 0px 0px;
        margin-bottom: 0px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}
    .header-title {{ font-size: 20px; font-weight: bold; margin: 0; }}
    .header-info {{ font-size: 14px; opacity: 0.9; }}
    @media (max-width: 600px) {{
        .header-title {{ font-size: 16px; }}
        .stPlotlyChart {{ height: 500px !important; }}
    }}
</style>
""", unsafe_allow_html=True)

# --- CÁLCULOS E ABAS ---
if st.sidebar.button("📊 Gerar Gráficos", use_container_width=True):
    imc = peso / ((estatura/100)**2)
    idade_busca = min(idade_dias, 1856) # Limite para as tabelas atuais de 5 anos (mudar para 3652 se incluir as de 10 anos)
    
    # Determinação Dinâmica do Intervalo e Títulos do Gráfico (0-2, 2-5, 5-10)
    idade_meses_float = idade_dias / 30.4375
    if idade_meses_float <= 24:
        faixa_titulo = "0 a 2 anos"
        range_grafico = [0, 24]
    elif idade_meses_float <= 60:
        faixa_titulo = "2 a 5 anos"
        range_grafico = [24, 60]
    else:
        faixa_titulo = "5 a 10 anos"
        range_grafico = [60, 120]
        
    tabs = st.tabs(["⚖️ Peso", "📏 Estatura", "🧮 IMC", "🧠 PC"])
    
    config_graficos = [
        ("Peso", "Peso para idade", "Peso (kg)", peso, 1.0, faixa_titulo, range_grafico),
        ("Estatura", "Estatura para idade", "Estatura/Comp. (cm)", estatura, 5.0, faixa_titulo, range_grafico),
        ("IMC", "IMC para idade", "IMC (kg/m²)", imc, 1.0, faixa_titulo, range_grafico),
        ("PC", "Perímetro Cefálico para idade", "PC (cm)", pc, 1.0, "0 a 2 anos", [0, 24] if idade_meses_float <= 24 else range_grafico)
    ]

    for tab, (key, titulo_ms, rotulo_y, valor, dtick_y, faixa_etaria, current_range) in zip(tabs, config_graficos):
        with tab:
            df_curva = tabelas_oms[sexo][key]
            linha = df_curva[df_curva['Day'] == idade_busca].iloc[0]
            z = (((valor / linha['M'])**linha['L'])-1)/(linha['L']*linha['S']) if linha['L'] != 0 else np.log(valor/linha['M'])/linha['S']
            
            classif, criterio, cor_alerta = obter_classificacao(z, key)
            
            st.markdown(f"""
            <div class="header-bar">
                <div class="header-title">{titulo_ms} {faixa_etaria}</div>
                <div class="header-info">Classificação: <b>{classif}</b> | Critério: {criterio}</div>
                <div class="header-info">Z-Score: {z:.2f} | Percentil: P{norm.cdf(z)*100:.1f}</div>
            </div>
            """, unsafe_allow_html=True)
            
            fig = go.Figure()
            mx = df_curva['Day'] / 30.4375
            
            # Desenha as áreas de forma similar ao MS
            if key == "IMC":
                fig.add_trace(go.Scatter(x=mx, y=df_curva['SD3neg'], fill=None, line=dict(color='black', width=1, dash='dash'), showlegend=False))
                fig.add_trace(go.Scatter(x=mx, y=df_curva['SD2neg'], fill='tonexty', fillcolor='rgba(211,47,47,0.1)', line=dict(color='red', width=1), name='-2Z'))
                fig.add_trace(go.Scatter(x=mx, y=df_curva['SD1'], fill='tonexty', fillcolor='rgba(56,142,60,0.1)', line=dict(color='#fbc02d', width=1, dash='dash'), name='+1Z'))
                fig.add_trace(go.Scatter(x=mx, y=df_curva['SD2'], fill='tonexty', fillcolor='rgba(251,192,45,0.2)', line=dict(color='red', width=1), name='+2Z'))
                fig.add_trace(go.Scatter(x=mx, y=df_curva['SD3'], fill='tonexty', fillcolor='rgba(245,124,0,0.1)', line=dict(color='black', width=1, dash='dash'), name='+3Z'))
                fig.add_trace(go.Scatter(x=mx, y=df_curva['SD4'], fill='tonexty', fillcolor='rgba(211,47,47,0.1)', line=dict(width=0), showlegend=False))
            else:
                fig.add_trace(go.Scatter(x=mx, y=df_curva['SD3neg'], fill=None, line=dict(color='black', width=1, dash='dash'), name='-3Z', showlegend=(key!="PC")))
                fig.add_trace(go.Scatter(x=mx, y=df_curva['SD2neg'], fill='tonexty', fillcolor='rgba(211,47,47,0.1)', line=dict(color='red', width=1), name='-2Z'))
                fig.add_trace(go.Scatter(x=mx, y=df_curva['SD2'], fill='tonexty', fillcolor='rgba(56,142,60,0.1)', line=dict(color='red', width=1), name='+2Z'))
                
                if key == "PC":
                    fig.add_trace(go.Scatter(x=mx, y=df_curva['SD3'], fill='tonexty', fillcolor='rgba(211,47,47,0.1)', line=dict(color='black', width=1, dash='dash'), name='+3Z'))
                else:
                    fig.add_trace(go.Scatter(x=mx, y=df_curva['SD3'], fill='tonexty', fillcolor='rgba(245,124,0,0.1)', line=dict(color='black', width=1, dash='dash'), name='+3Z'))
                    fig.add_trace(go.Scatter(x=mx, y=df_curva['SD4'], fill='tonexty', fillcolor='rgba(211,47,47,0.1)', line=dict(width=0), showlegend=False))
            
            fig.add_trace(go.Scatter(x=mx, y=df_curva['SD0'], line=dict(color='green', width=3), name='Mediana'))
            
            paciente_x = idade_dias / 30.4375
            fig.add_trace(go.Scatter(x=[paciente_x], y=[valor], mode='markers', marker=dict(size=14, color='black', symbol='x'), name='Paciente'))

            # Linhas de anos baseadas no range visível
            for ano in [12, 24, 36, 48, 60, 72, 84, 96, 108, 120]:
                if current_range[0] <= ano <= current_range[1]:
                    fig.add_vline(x=ano, line_width=1.5, line_dash="solid", line_color="rgba(0,0,0,0.25)")
                    fig.add_annotation(x=ano, y=0.01, yref="paper", text=f"{ano//12} ano(s)", showarrow=False, font=dict(size=12, color="black"), yanchor="bottom")

            fig.update_layout(
                margin=dict(l=40, r=20, t=20, b=40),
                height=600,
                template="plotly_white",
                xaxis=dict(title="Idade (meses)", range=current_range, dtick=1, showgrid=True, gridcolor='rgba(0,0,0,0.06)', tick0=current_range[0]),
                yaxis=dict(title=rotulo_y, dtick=dtick_y, showgrid=True, gridcolor='rgba(0,0,0,0.06)'),
                legend=dict(orientation="h", y=1.02, x=1, xanchor="right")
            )
            st.plotly_chart(fig, use_container_width=True)
