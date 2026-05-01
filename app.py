import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
from datetime import date
from diretrizes import obter_classificacao, obter_orientacoes, obter_vacinas, obter_marcos

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
    aleitamento_exclusivo = st.checkbox("Em Aleitamento Materno Exclusivo (AME)?", value=True)

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

# CSS Responsivo
tema_cor = "#0d47a1" if sexo == "Masculino" else "#880e4f"
st.markdown(f"""
<style>
    .stApp {{ background-color: {'#f0f8ff' if sexo == 'Masculino' else '#fff0f5'}; }}
    .header-bar {{ background-color: {tema_cor}; color: white; padding: 15px; border-radius: 8px 8px 0px 0px; }}
    .header-title {{ font-size: 20px; font-weight: bold; margin: 0; }}
    .milestone-card {{ background: white; padding: 15px; border-radius: 8px; border-left: 5px solid {tema_cor}; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
    h1, h2, h3 {{ color: {tema_cor} !important; }}
</style>
""", unsafe_allow_html=True)

st.title("🩺 Prontuário Pediátrico Interativo")
st.success(f"**Idade Fisiológica do Paciente:** {anos} ano(s), {meses} mês(es) e {dias} dia(s)")

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
                
                st.markdown(f"""
                <div class="header-bar" style="background-color:{cor_alerta};">
                    <div class="header-title">{titulo_ms} {faixa_etaria}</div>
                    <div>Classificação: <b>{classif}</b> | Critério: {criterio}</div>
                    <div>Z-Score: {z:.2f} | Percentil: P{norm.cdf(z)*100:.1f}</div>
                </div>
                """, unsafe_allow_html=True)
                
                fig = go.Figure()
                mx = df_curva['Day'] / 30.4375
                
                # Áreas coloridas do gráfico
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

    # === ABA 2: DESENVOLVIMENTO ===
    with tab_desenv:
        faixa_nome, marcos_fase = obter_marcos(idade_meses_float)
        st.subheader(f"🎯 Marcos Esperados para a Fase Atual ({faixa_nome})")
        st.markdown("Assinale os marcos que a criança já realiza para monitoramento do neurodesenvolvimento:")
        
        cols = st.columns(2)
        idx = 0
        for dominio, itens in marcos_fase.items():
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="milestone-card">
                    <h4 style="margin-top:0;">{dominio}</h4>
                </div>
                """, unsafe_allow_html=True)
                for item in itens:
                    st.checkbox(item, key=f"marco_{dominio}_{item}")
            idx += 1

    # === ABA 3: VACINAÇÃO ===
    with tab_vac:
        st.subheader("📅 Calendário Vacinal do PNI")
        vacinas_pni = obter_vacinas(idade_meses_float)
        
        # Filtra vacinas pendentes e aplicadas
        aplicadas = [v for v in vacinas_pni if v["idade"] <= idade_meses_float]
        pendentes = [v for v in vacinas_pni if v["idade"] > idade_meses_float]
        
        col1, col2 = st.columns(2)
        with col1:
            st.success("✅ **Vacinas que a criança já deve ter tomado (Conferir caderneta)**")
            for grupo in aplicadas:
                with st.expander(f"Fase: {grupo['intervalo']}"):
                    for vacina in grupo["vacinas"]:
                        st.checkbox(vacina, value=True, key=f"vac_{grupo['intervalo']}_{vacina}")
        with col2:
            st.warning("⏳ **Próximas Doses / Pendentes**")
            for grupo in pendentes:
                st.markdown(f"**{grupo['intervalo']}:** " + ", ".join(grupo["vacinas"]))

    # === ABA 4: ORIENTAÇÕES ===
    with tab_orient:
        st.subheader("📝 Orientações de Puericultura")
        orientacoes = obter_orientacoes(idade_meses_float)
        
        for titulo, conteudo in orientacoes.items():
            st.markdown(f"#### {titulo}")
            st.info(conteudo)

    # === ABA 5: SUPLEMENTAÇÃO (CALCULADORA INTELIGENTE) ===
    with tab_suple:
        st.subheader("💊 Planejamento Profilático (Diretrizes SBP)")
        
        st.markdown("### ☀️ Vitamina D")
        dose_vitd = "400 UI/dia" if idade_meses_float <= 12 else "600 UI/dia"
        st.info(f"**Prescrição recomendada:** Administrar **{dose_vitd}** (Início na 1ª semana de vida).")
        
        st.markdown("---")
        st.markdown("### 🩸 Calculadora de Ferro Profilático")
        
        # Seleção detalhada dos sais baseada na Tabela de Sais 
        opcoes_sais = {
            "Sulfato Ferroso Gotas (ex: FURP, Lomfer) - 25mg Fe/mL [1 gota = 1mg]": {"mg_gota": 1.0, "marcas": "FURP, Lomfer, Fersil"},
            "Ferripolimaltose Gotas 50mg/mL (ex: Noripurum) [1 gota = 2.5mg]": {"mg_gota": 2.5, "marcas": "Noripurum, Ultrafer"},
            "Ferripolimaltose Gotas 100mg/mL (ex: Dexfer) [1 gota = 5mg]": {"mg_gota": 5.0, "marcas": "Dexfer"},
            "Ferro Quelato Glicinato Gotas (ex: Neutrofer) [1 gota = 2.5mg]": {"mg_gota": 2.5, "marcas": "Neutrofer"},
            "Glicinato Férrico Associado (ex: Combiron) [1 gota = 2.5mg]": {"mg_gota": 2.5, "marcas": "Combiron"}
        }
        
        escolha_sal = st.selectbox("Selecione a Apresentação e Sal de Ferro:", list(opcoes_sais.keys()))
        dados_sal = opcoes_sais[escolha_sal]
        
        # Algoritmo de Decisão SBP (Baseado no Peso de Nascimento e Idade) [cite: 89, 90, 87, 88]
        dose_mg_kg = 0
        orientacao_inicio = ""
        
        if prematuro or peso_nasc < 2.5:
            orientacao_inicio = "Início aos 30 dias de vida."
            if idade_meses_float <= 12:
                # 1º Ano de vida
                if peso_nasc < 1.0: dose_mg_kg = 4
                elif peso_nasc <= 1.5: dose_mg_kg = 3
                else: dose_mg_kg = 2
            else:
                # 2º Ano de vida
                dose_mg_kg = 1
        else:
            # Termo / Peso Adequado
            dose_mg_kg = 1
            if aleitamento_exclusivo:
                orientacao_inicio = "Início aos 180 dias de vida."
                if idade_meses_float < 6: dose_mg_kg = 0 # Ainda não tem indicação formal
            else:
                orientacao_inicio = "Início aos 90 dias de vida."
                if idade_meses_float < 3: dose_mg_kg = 0
        
        if dose_mg_kg > 0:
            dose_total_mg = peso * dose_mg_kg
            gotas_dia = max(1, round(dose_total_mg / dados_sal["mg_gota"]))
            
            st.success(f"""
            **📄 Sugestão de Receituário:**
            - **Necessidade (Diretriz SBP):** {dose_mg_kg} mg/kg/dia ({orientacao_inicio})
            - **Dose Alvo Calculada:** {dose_total_mg:.1f} mg de Ferro Elementar/dia
            - **Posologia Recomendada:** Administrar **{gotas_dia} gotas** ao dia via oral.
            - **Apresentação de Referência:** {dados_sal['marcas']}
            """)
            st.caption("Nota: As doses devem ser conferidas com o rótulo do fabricante adquirido pelo paciente, pois concentrações e tamanhos de gotas podem variar[cite: 4].")
        else:
            st.warning(f"**Atenção:** Paciente atual sem indicação de início no momento (Regra: {orientacao_inicio}).")
