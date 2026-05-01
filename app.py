# Dentro do arquivo app.py, na seção das Tabs:

    with tabs[3]: # ORIENTAÇÕES
        st.subheader("📋 Orientações de Puericultura")
        content = obter_orientacoes_detalhadas(idade_meses_float)
        
        c1, c2 = st.columns(2)
        with c1:
            st.info(f"**🍽️ Alimentação:** \n\n {content['Alimentação']}")
            st.warning(f"**⚠️ Segurança:** \n\n {content['Prevenção de Acidentes' if 'Prevenção de Acidentes' in content else 'Segurança']}")
        with c2:
            st.success(f"**🧠 Estímulos:** \n\n {content['Estímulos' if 'Estímulos' in content else 'Comportamento']}")
            st.error(f"**🚨 Alerta:** \n\n {content.get('Sinais de Alerta', 'Manter acompanhamento mensal.')}")

    with tabs[4]: # SUPLEMENTAÇÃO
        st.subheader("💊 Cálculo de Suplementação")
        
        col_sup1, col_sup2 = st.columns(2)
        
        with col_sup1:
            st.markdown("**1. Critérios de Risco (SBP 2021)**")
            if prematuro or peso < 2.5:
                alvo_ferro = 2.0
                st.error("⚠️ Alvo: 2mg/kg/dia (Prematuro/Baixo Peso)")
            else:
                alvo_ferro = 1.0
                st.success("✅ Alvo: 1mg/kg/dia (Termo/Peso Adequado)")
            
            vit_d = "400 UI/dia" if idade_meses_float < 12 else "600 UI/dia"
            st.metric("Vitamina D Recomendada", vit_d)

        with col_sup2:
            st.markdown("**2. Seleção do Sal e Posologia**")
            sais = obter_sais_ferro()
            sal_escolhido = st.selectbox("Selecione o Sal de Ferro:", list(sais.keys()))
            
            dados_sal = sais[sal_escolhido]
            necessidade_total = peso * alvo_ferro
            
            # Cálculo de gotas
            gotas_necessarias = int(np.ceil(necessidade_total / dados_sal['mg_por_gota']))
            
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #0d47a1;">
                <h4 style="margin:0;">Prescrição Sugerida:</h4>
                <p style="font-size: 18px; color: #d32f2f; font-weight: bold;">
                    {sal_escolhido}: Dar {gotas_necessarias} gotas, 1x ao dia.
                </p>
                <small><b>Info Técnica:</b> 1 gota = {dados_sal['mg_por_gota']}mg de Fe elementar. <br>
                <i>{dados_sal['obs']}</i></small>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        st.caption("Nota: Iniciar Ferro aos 3 meses para crianças a termo e aos 30 dias para prematuros. Manter até 24 meses.")
