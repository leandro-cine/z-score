import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
from datetime import date

# --- CONFIGURAÇÃO DA PÁGINA (WIDE E RESPONSIVA) ---
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
        # Nota: Certifique-se de que os nomes dos ficheiros no GitHub correspondem a estes:
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
        if z >= -2: return "Estatura adequada para idade", "≥ escore-z -2", "#388e3c"
        elif z >= -3: return "Baixa estatura para idade", "≥ escore-z -3 e < -2", "#f57c00"
        else: return "Muito baixa estatura para idade", "< escore-z -3", "#d32f2f"
    elif parametro == "IMC":
        if z > 3: return "Obesidade", "> escore-z +3", "#d32f2f"
        elif z > 2: return "Sobrepeso", "> +2 e ≤ +3", "#f57c00"
        elif z > 1: return "Risco de sobrepeso", "> +1 e ≤ +2", "#fbc02d"
        elif z >= -2: return "Eutrofia", "≥ -2 e ≤ +1", "#388e3c"
        elif z >= -3: return "Magreza", "≥ -3 e < -2", "#f57c00"
        else: return "Magreza acentuada", "< escore-z -3", "#d32f2f"

# --- INTERFACE E CSS RESPONSIVO ---
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
    .main-container {{ max-width: 1200px; margin: auto; }}
    @media (max-width: 600px) {{
        .header-title {{ font-size: 16px; }}
        .stPlotlyChart {{ height: 500px !important; }}
    }}
</style>
""", unsafe_allow_html=True)

# --- CÁLCULOS E ABAS ---
if st.sidebar.button("📊 Gerar Gráficos", use_container_width=True):
    imc = peso / ((estatura/100)**2)
    idade_busca = min(idade_dias, 1856)
    
    tabs = st.tabs(["⚖️ Peso", "📏 Estatura", "🧮 IMC", "🧠 PC"])
    
    config_graficos = [
        ("Peso", "Peso para idade", "Peso (kg)", peso, 1.0, "0 a 5 anos"),
        ("Estatura", "Estatura para idade", "Estatura (cm)", estatura, 5.0, "0 a 5 anos"),
        ("IMC", "IMC para idade", "IMC (kg/m²)", imc, 1.0, "0 a 5 anos"),
        ("PC", "PC para idade", "PC (cm)", pc, 1.0, "0 a 2 anos")
    ]

    for tab, (key, titulo_ms, rotulo_y, valor, dtick_y, faixa_etaria) in zip(tabs, config_graficos):
        with tab:
            df_curva = tabelas_oms[sexo][key]
            linha = df_curva[df_curva['Day'] == idade_busca].iloc[0]
            z = (((valor / linha['M'])**linha['L'])-1)/(linha['L']*linha['S']) if linha['L'] != 0 else np.log(valor/linha['M'])/linha['S']
            
            classif, criterio, cor_alerta = obter_classificacao(z, key)
            
            # Cabeçalho Retangular Superior (Estilo Ministério da Saúde)
            st.markdown(f"""
            <div class="header-bar">
                <div class="header-title">{titulo_ms} {faixa_etaria}</div>
                <div class="header-info">Classificação: <b>{classif}</b> | Critério: {criterio}</div>
                <div class="header-info">Z-Score: {z:.2f} | Percentil: P{norm.cdf(z)*100:.1f}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Gráfico com Plotly
            fig = go.Figure()
            mx = df_curva['Day'] / 30.4375
            
            # Áreas Sombreadas
            fig.add_trace(go.Scatter(x=mx, y=df_curva['SD3neg'], fill=None, line_color='black', line_dash='dash', name='-3Z', showlegend=False))
            fig.add_trace(go.Scatter(x=mx, y=df_curva['SD2neg'], fill='tonexty', fillcolor='rgba(211,47,47,0.1)', line_color='red', name='-2Z'))
            fig.add_trace(go.Scatter(x=mx, y=df_curva['SD2'], fill='tonexty', fillcolor='rgba(56,142,60,0.1)', line_color='red', name='+2Z'))
            fig.add_trace(go.Scatter(x=mx, y=df_curva['SD3'], fill='tonexty', fillcolor='rgba(245,124,0,0.1)', line_color='black', line_dash='dash', name='+3Z'))
            fig.add_trace(go.Scatter(x=mx, y=df_curva['SD0'], line=dict(color='green', width=3), name='Mediana'))
            
            # Ponto do Paciente
            paciente_x = idade_dias / 30.4375
            fig.add_trace(go.Scatter(x=[paciente_x], y=[valor], mode='markers', marker=dict(size=14, color='black', symbol='x'), name='Paciente'))

            # Zoom e Anos
            range_x = [0, 24] if key == "PC" else [0, 60]
            for ano in [12, 24, 36, 48, 60]:
                if range_x[0] <= ano <= range_x[1]:
                    fig.add_vline(x=ano, line_width=1, line_dash="solid", line_color="rgba(0,0,0,0.3)")
                    fig.add_annotation(x=ano, y=0.02, yref="paper", text=f"{ano//12} ano(s)", showarrow=False, font=dict(size=12, color="black"))

            fig.update_layout(
                margin=dict(l=40, r=20, t=20, b=40),
                height=600,
                template="plotly_white",
                xaxis=dict(title="Idade (meses)", range=range_x, dtick=1, showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
                yaxis=dict(title=rotulo_y, dtick=dtick_y, showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
                legend=dict(orientation="h", y=1.02, x=1, xanchor="right")
            )
            st.plotly_chart(fig, use_container_width=True)
