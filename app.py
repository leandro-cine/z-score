import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
from datetime import date
from diretrizes import obter_classificacao, obter_orientacoes, obter_vacinas, obter_marcos

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Puericultura Digital", layout="wide", initial_sidebar_state="expanded")

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

# --- INTERFACE LATERAL (REATIVA) ---
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

    anos = int(idade_dias // 365.25)
    dias_restantes = idade_dias % 365.25
    meses = int(dias_restantes // 30.4375)
    dias = int(dias_restantes % 30.4375)
    idade_meses_float = idade_dias / 30.4375
    
    st.success(f"**Idade exata:**\n\n{anos} ano(s), {meses} mês(es) e {dias} dia(s)")

    st.header("📏 Medidas")
    peso = st.number_input("Peso (kg)", 0.5, 150.0, 10.0, step=0.1)
    estatura = st.number_input("Estatura (cm)", 30.0, 220.0, 75.0, step=0.5)
    pc = st.number_input("PC (cm)", 20.0, 80.0, 45.0, step=0.1)

# Estilos CSS
tema_cor = "#0d47a1" if sexo == "Masculino" else "#880e4f"
st.markdown(f"""
<style>
    .stApp {{ background-color: {'#f0f8ff' if sexo == 'Masculino' else '#fff0f5'}; }}
    .header-bar {{ background-color: {tema_cor}; color: white; padding: 15px; border-radius: 8px 8px 0px 0px; display: flex; flex-direction: column; justify-content: center; }}
    .header-title {{ font-size: 20px; font-weight: bold; margin: 0; }}
    h1, h2, h3 {{ color: {tema_cor} !important; }}
</style>
""", unsafe_allow_html=True)

st.title("🩺 Prontuário Pediátrico Digital")

# Sem botão! O app renderiza as abas automaticamente baseando-se nas entradas
if tabelas_oms:
    imc = peso / ((estatura/100)**2)
    idade_busca = min(idade_dias, 1856) 
    
    tab_cresc, tab_desenv, tab_vac, tab_orient, tab_suple = st.tabs(["📈 Crescimento", "🧠 Desenvolvimento", "💉 Vacinação", "📝 Orientações", "💊 Suplementação"])

    # --- 1. ABA CRESCIMENTO (GRÁFICOS RESTAURADOS) ---
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
                
                st.markdown(f"""
                <div class="header-bar" style="background-color:{cor_alerta};">
                    <div class="header-title">{titulo_ms} {faixa_etaria}</div>
                    <div>Classificação: <b>{classif}</b> | Critério: {criterio}</div>
                    <div>Z-Score: {z:.2f} | Percentil: P{norm.cdf(z)*100:.1f}</div>
                </div>
                """, unsafe_allow_html=True)
                
                fig = go.Figure()
                mx = df_curva['Day'] / 30.4375
                
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
                fig.add_trace(go.Scatter(x=[idade_meses_float], y=[valor], mode='markers', marker=dict(size=14, color='black', symbol='x'), name='Paciente'))

                for ano in [12, 24, 36, 48, 60, 72, 84, 96, 108, 120]:
                    if cur_range[0] <= ano <= cur_range[1]:
                        fig.add_vline(x=ano, line_width=1.5, line_dash="solid", line_color="rgba(0,0,0,0.25)")
                        fig.add_annotation(x=ano, y=0.01, yref="paper", text=f"{ano//12} ano(s)", showarrow=False, font=dict(size=12, color="black"), yanchor="bottom")

                if key == "PC": limite_y = [30, 52]
                elif key == "Peso":
                    if idade_meses_float <= 24: limite_y = [2, 18]
                    elif idade_meses_float <= 60: limite_y = [10, 30]
                    else: limite_y = [15, 55]
                elif key == "Estatura":
                    if idade_meses_float <= 24: limite_y = [45, 95]
                    elif idade_meses_float <= 60: limite_y = [80, 120]
                    else: limite_y = [95, 185]
                elif key == "IMC":
                    limite_y = [10, 22] if idade_meses_float <= 60 else [12, 30]

                if valor > limite_y[1]: limite_y[1] = valor + (dtick_y * 1)
                if valor < limite_y[0]: limite_y[0] = valor - (dtick_y * 1)

                fig.update_layout(
                    margin=dict(l=40, r=20, t=20, b=40), height=600, template="plotly_white",
                    xaxis=dict(title="Idade (meses)", range=cur_range, dtick=1, showgrid=True, gridcolor='rgba(0,0,0,0.06)', showline=True, linewidth=1, linecolor='black', mirror=True),
                    yaxis=dict(title=rotulo_y, range=limite_y, dtick=dtick_y, showgrid=True, gridcolor='rgba(0,0,0,0.06)', showline=True, linewidth=1, linecolor='black', mirror=True),
                    legend=dict(orientation="h", y=1.02, x=1, xanchor="right")
                )
                st.plotly_chart(fig, use_container_width=True)

    # --- 2. ABA DESENVOLVIMENTO ---
    with tab_desenv:
        st.subheader("Marcos do Desenvolvimento")
        marcos = obter_marcos(idade_meses_float)
        col_ant, col_atual = st.columns(2)
        with col_ant:
            st.markdown("### ⏪ Marcos Anteriores")
            for m, lista in marcos.items():
                if m < idade_meses_float:
                    for item in lista: st.checkbox(item, value=True, key=f"ant_{item}")
        with col_atual:
            st.markdown("### 🎯 Esperados para a fase")
            for m, lista in marcos.items():
                if m >= idade_meses_float and m <= idade_meses_float + 6:
                    for item in lista: st.checkbox(item, value=False, key=f"atu_{item}")

    # --- 3. ABA VACINAÇÃO ---
    with tab_vac:
        tomadas, proximas = obter_vacinas(idade_meses_float)
        c1, c2 = st.columns(2)
        c1.markdown("### ✅ Vacinas para conferir no cartão")
        for v in tomadas: c1.write(f"- {', '.join(v) if isinstance(v, list) else v}")
        c2.markdown("### ⏳ Próximas Vacinas (PNI)")
        for v in proximas: c2.write(f"- {', '.join(v) if isinstance(v, list) else v}")

    # --- 4. ABA ORIENTAÇÕES ---
    with tab_orient:
        st.subheader("Orientações de Puericultura para a Faixa Etária")
        ori = obter_orientacoes(idade_meses_float)
        for cat, texto in ori.items():
            with st.expander(f"📍 {cat}"): st.write(texto)

    # --- 5. ABA SUPLEMENTAÇÃO ---
    with tab_suple:
        st.subheader("Planejamento de Suplementação (Consensos SBP)")
        
        st.info("☀️ **Vitamina D:** 400 UI/dia de 1 semana até 12 meses; 600 UI/dia de 12 a 24 meses.")
        
        st.markdown("### 🩸 Calculadora de Profilaxia de Ferro")
        tipo_ferro = st.selectbox("Selecione o Sal de Ferro prescrito", ["Sulfato Ferroso (25mg/mL de Fe elementar)", "Ferro Quelato/Polimaltosado (50mg/mL de Fe elementar)"])
        
        if prematuro or peso < 2.5:
            dose_mg_kg = 2 if peso > 1.5 else 3
        else:
            dose_mg_kg = 1 
            
        dose_total_mg = peso * dose_mg_kg
        
        if "Sulfato" in tipo_ferro:
            gotas = round(dose_total_mg / 1.25)
            marcas, conc = "Fer-in-sol, Sulferrol", "1 gota ≈ 1.25mg Fe elementar"
        else:
            gotas = round(dose_total_mg / 2.5)
            marcas, conc = "Neutrofer, Noripurum", "1 gota ≈ 2.5mg Fe elementar"

        st.success(f"""
        **Prescrição Sugerida baseada no peso ({peso}kg):**
        - **Dose Alvo (SBP):** {dose_mg_kg} mg/kg/dia
        - **Necessidade Total:** {dose_total_mg:.1f} mg de Ferro Elementar
        - **Posologia:** Administrar **{max(1, gotas)} gotas** ao dia.
        - **Marcas sugeridas:** {marcas}
        """)
