from __future__ import annotations

from math import ceil

# =========================
# Crescimento e z-score
# =========================

def obter_classificacao(z, parametro):
    if parametro == "PC":
        if z > 2:
            return "PC acima do esperado para a idade", "> +2 escores z", "#f57c00"
        if z >= -2:
            return "PC adequado para idade", "≤ +2 e ≥ -2 escores z", "#388e3c"
        return "PC abaixo do esperado para idade", "< -2 escores z", "#d32f2f"
    if parametro == "Peso":
        if z > 2:
            return "Peso elevado para idade", "> escore-z +2", "#f57c00"
        if z >= -2:
            return "Peso adequado para idade", "≥ escore-z -2 e ≤ +2", "#388e3c"
        if z >= -3:
            return "Baixo peso para idade", "≥ escore-z -3 e < -2", "#f57c00"
        return "Muito baixo peso para idade", "< escore-z -3", "#d32f2f"
    if parametro == "Estatura":
        if z >= -2:
            return "Estatura adequada para idade", "≥ escore-z -2", "#388e3c"
        if z >= -3:
            return "Baixa estatura para idade", "≥ escore-z -3 e < -2", "#f57c00"
        return "Muito baixa estatura para idade", "< escore-z -3", "#d32f2f"
    if parametro == "IMC":
        if z > 3:
            return "Obesidade", "> escore-z +3", "#d32f2f"
        if z > 2:
            return "Sobrepeso", "> +2 e ≤ +3", "#f57c00"
        if z > 1:
            return "Risco de sobrepeso", "> +1 e ≤ +2", "#fbc02d"
        if z >= -2:
            return "Eutrofia", "≥ -2 e ≤ +1", "#388e3c"
        if z >= -3:
            return "Magreza", "≥ -3 e < -2", "#f57c00"
        return "Magreza acentuada", "< escore-z -3", "#d32f2f"
    return "Classificação não disponível", "", "#607d8b"


def obter_faixas_zscore(parametro):
    cores = {
        "verde": ("rgba(46,125,50,.16)", "#2e7d32"),
        "amarelo": ("rgba(251,192,45,.20)", "#8d6e00"),
        "laranja": ("rgba(245,124,0,.20)", "#ef6c00"),
        "vermelho": ("rgba(211,47,47,.18)", "#c62828"),
    }
    if parametro == "IMC":
        base = [(-4,-3,"Magreza acentuada","< -3Z","vermelho"),(-3,-2,"Magreza","-3Z a -2Z","laranja"),(-2,1,"Eutrofia","-2Z a +1Z","verde"),(1,2,"Risco de sobrepeso","+1Z a +2Z","amarelo"),(2,3,"Sobrepeso","+2Z a +3Z","laranja"),(3,4,"Obesidade","> +3Z","vermelho")]
    elif parametro == "Peso":
        base = [(-4,-3,"Muito baixo peso","< -3Z","vermelho"),(-3,-2,"Baixo peso","-3Z a -2Z","laranja"),(-2,2,"Peso adequado","-2Z a +2Z","verde"),(2,4,"Peso elevado","> +2Z","laranja")]
    elif parametro == "Estatura":
        base = [(-4,-3,"Muito baixa estatura","< -3Z","vermelho"),(-3,-2,"Baixa estatura","-3Z a -2Z","laranja"),(-2,4,"Estatura adequada","≥ -2Z","verde")]
    else:
        base = [(-4,-2,"PC abaixo do esperado","< -2Z","vermelho"),(-2,2,"PC adequado","-2Z a +2Z","verde"),(2,4,"PC acima do esperado","> +2Z","laranja")]
    return [{"z_min":a,"z_max":b,"rotulo":r,"intervalo":i,"cor_fill":cores[c][0],"cor_texto":cores[c][1]} for a,b,r,i,c in base]

# =========================
# Nascimento / riscos
# =========================

def classificar_peso_ig(peso_g: float, ig_sem: float):
    riscos = []
    if ig_sem < 28:
        classe_ig = "Pré-termo extremo"
        riscos.append("pré-termo extremo")
    elif ig_sem < 34:
        classe_ig = "Pré-termo moderado"
        riscos.append("pré-termo moderado")
    elif ig_sem < 37:
        classe_ig = "Pré-termo tardio"
        riscos.append("pré-termo tardio")
    elif ig_sem < 42:
        classe_ig = "Termo"
    else:
        classe_ig = "Pós-termo"
        riscos.append("pós-termo")

    if peso_g < 1500:
        classe_peso = "muito baixo peso ao nascer"
        riscos.append("muito baixo peso ao nascer")
    elif peso_g < 2500:
        classe_peso = "baixo peso ao nascer"
        riscos.append("baixo peso ao nascer")
    else:
        classe_peso = "peso adequado presumido se AIG"

    return f"{classe_ig}; {classe_peso}", riscos

# =========================
# Suplementação
# =========================

def fatores_risco_anemia():
    return {
        "maternos_gestacionais": [
            "Anemia materna na gestação", "Baixa adesão ao sulfato ferroso gestacional", "Gestação múltipla",
            "Intervalo interpartal curto", "Hemorragia gestacional/periparto", "Insegurança alimentar", "Adolescência materna",
            "Baixa escolaridade/vulnerabilidade social", "Diabetes gestacional", "Hipertensão/pré-eclâmpsia"
        ],
        "crianca": [
            "Prematuridade", "Baixo peso ao nascer (< 2.500 g)", "Muito baixo peso ao nascer (< 1.500 g)",
            "PIG suspeito", "Clampeamento precoce do cordão", "Aleitamento artificial/leite de vaca antes de 12 meses",
            "Introdução alimentar pobre em ferro", "Doença crônica", "Infecções recorrentes", "Perdas sanguíneas", "Parasitose suspeita"
        ]
    }


def obter_sais_ferro():
    return {
        "Sulfato ferroso gotas 25 mg Fe/mL (1 gota ≈ 1 mg)": {"mg_ml":25, "gotas_ml":25, "mg_gota":1.0, "marcas":"Sulfato Ferroso genérico, FURP, Lomfer, Fersil", "obs":"opção clássica; pode causar sintomas gastrointestinais e escurecimento de fezes/dentes.", "imagem":"assets/ferro/sulfato_ferroso_gotas.png"},
        "Ferripolimaltose gotas 50 mg Fe/mL (1 gota ≈ 2,5 mg)": {"mg_ml":50, "gotas_ml":20, "mg_gota":2.5, "marcas":"Noripurum gotas, Ultrafer, genéricos", "obs":"mais concentrado; menor número de gotas.", "imagem":"assets/ferro/noripurum_gotas_50mg.png"},
        "Ferripolimaltose gotas 100 mg Fe/mL (1 gota ≈ 5 mg)": {"mg_ml":100, "gotas_ml":20, "mg_gota":5.0, "marcas":"Dexfer 100 mg/mL", "obs":"muito concentrado; atenção para erro de dose.", "imagem":"assets/ferro/dexfer_gotas_100mg.png"},
        "Ferripolimaltose xarope 10 mg Fe/mL": {"mg_ml":10, "gotas_ml":None, "mg_gota":None, "marcas":"Noripurum xarope", "obs":"cálculo por mL com seringa dosadora.", "imagem":"assets/ferro/noripurum_xarope_10mg.png"},
        "Ferro quelato/glicinato gotas 50 mg Fe/mL (1 gota ≈ 2,5 mg)": {"mg_ml":50, "gotas_ml":20, "mg_gota":2.5, "marcas":"Neutrofer gotas", "obs":"conferir bula/rótulo se expressa ferro elementar.", "imagem":"assets/ferro/neutrofer_gotas.png"},
        "Glicinato férrico associado a vitaminas": {"mg_ml":27.58, "gotas_ml":20, "mg_gota":1.379, "marcas":"Combiron gotas", "obs":"associado a vitaminas; conferir composição e indicação.", "imagem":"assets/ferro/combiron_gotas.png"},
    }


def recomendacao_ferro(idade_meses, peso_kg, peso_nasc_g, ig_sem, ame, fatores_crianca=None, fatores_maternos=None):
    fatores_crianca = fatores_crianca or []
    fatores_maternos = fatores_maternos or []
    risco = bool(fatores_crianca or fatores_maternos or ig_sem < 37 or peso_nasc_g < 2500)
    if idade_meses < 6 and not risco:
        return {"protocolo":"Sem ferro profilático universal antes dos 6 meses", "resumo":"termo, peso adequado e sem fatores de risco", "dose_mg_kg_dia":0, "dose_mg_dia":0, "conduta":"Manter aleitamento/alimentação e iniciar ciclo programático a partir de 6 meses se elegível."}
    if not risco and 6 <= idade_meses < 9:
        dose = 10 if peso_kg <= 10 else 12.5
        return {"protocolo":"MS/SBP — 1º ciclo", "resumo":"criança termo, AME/peso adequado e sem risco: 6 a 9 meses", "dose_mg_kg_dia":dose/max(peso_kg,0.1), "dose_mg_dia":dose, "conduta":"Administrar ferro elementar diário até completar 3 meses de ciclo; depois pausa programática até 12 meses."}
    if not risco and 9 <= idade_meses < 12:
        return {"protocolo":"Pausa entre ciclos", "resumo":"pausa programática dos 9 aos 12 meses", "dose_mg_kg_dia":0, "dose_mg_dia":0, "conduta":"Não há ferro profilático no intervalo; manter alimentação rica em ferro e vigilância."}
    if not risco and 12 <= idade_meses < 15:
        dose = 10 if peso_kg <= 10 else 12.5
        return {"protocolo":"MS/SBP — 2º ciclo", "resumo":"12 a 15 meses", "dose_mg_kg_dia":dose/max(peso_kg,0.1), "dose_mg_dia":dose, "conduta":"Administrar ferro elementar diário até completar 3 meses de ciclo."}
    if not risco and idade_meses >= 15:
        return {"protocolo":"Ciclos concluídos/fora da janela", "resumo":"fora da idade programática de ferro profilático universal", "dose_mg_kg_dia":0, "dose_mg_dia":0, "conduta":"Sem ferro profilático automático; investigar/tratar se anemia ou fatores de risco clínicos."}
    # risco: dose por kg
    if ig_sem < 37 or peso_nasc_g < 2500:
        dose_mgkg = 2.0 if idade_meses < 12 else 1.0
        protocolo = "SBP — risco/prematuridade/baixo peso"
    else:
        dose_mgkg = 1.0
        protocolo = "SBP — fator de risco para deficiência de ferro"
    dose = round(dose_mgkg * peso_kg, 1)
    return {"protocolo":protocolo, "resumo":"dose individualizada por peso e risco", "dose_mg_kg_dia":dose_mgkg, "dose_mg_dia":dose, "conduta":"Usar ferro elementar calculado por kg; conferir tolerância, adesão, alimentação e necessidade de hemograma/ferritina conforme caso."}


def calcular_apresentacao_ferro(dose_mg_dia, apresentacao):
    if dose_mg_dia <= 0:
        return {"texto":"Sem dose diária calculada nesta situação.", "gotas_dia":0, "ml_dia":0}
    mg_gota = apresentacao.get("mg_gota")
    if mg_gota:
        gotas = max(1, int(round(dose_mg_dia / mg_gota)))
        return {"texto":f"{gotas} gota(s) ao dia ≈ {gotas*mg_gota:.1f} mg de ferro elementar/dia", "gotas_dia":gotas, "ml_dia":gotas/(apresentacao.get('gotas_ml') or 20)}
    ml = dose_mg_dia / apresentacao.get("mg_ml", 1)
    return {"texto":f"{ml:.2f} mL ao dia ≈ {dose_mg_dia:.1f} mg de ferro elementar/dia", "gotas_dia":None, "ml_dia":ml}


def modelo_prescricao_ferro(dose_mg_dia, sal_nome, apresentacao, calculo, duracao):
    if dose_mg_dia <= 0:
        return "Sem prescrição profilática automática de ferro neste momento. Reavaliar conforme idade, fatores de risco, hemograma/ferritina e orientação clínica."
    dose_txt = calculo.get("texto", "dose calculada")
    return f"Ferro elementar — {sal_nome}\nAdministrar {dose_txt}, por via oral, 1 vez ao dia, preferencialmente longe de leite e derivados.\nDuração: {duracao}.\nOrientar escurecimento das fezes, possível desconforto gastrointestinal e necessidade de conferir a concentração no rótulo/bula."


def fatores_risco_hipovitaminose_d():
    return ["Prematuridade", "Mãe com hipovitaminose D na gestação", "Aleitamento materno exclusivo", "Pele escura", "Exposição solar inadequada", "Roupas que cobrem quase todo o corpo", "Dieta vegetariana/restritiva", "Obesidade", "Síndrome de má absorção", "Hepatopatia crônica", "Nefropatia crônica", "Uso de anticonvulsivantes", "Uso de corticoide crônico", "Uso de antirretroviral"]


def fatores_risco_vitamina_b12():
    return ["Mãe vegetariana/vegana sem suplementação", "Dieta vegetariana/vegana da criança", "Baixa ingestão de alimentos de origem animal", "Má absorção intestinal", "Cirurgia gastrointestinal", "Uso crônico de metformina/IBP na mãe ou adolescente", "Anemia macrocítica suspeita", "Atraso/regressão do desenvolvimento associado a risco nutricional"]


def calcular_vitamina_a_pnsva(idade_meses, regiao_prioritaria=False, cadastro_unico=False, dsei=False, dose_6_11_recebida=False, ultima_dose_meses=None):
    if idade_meses < 6:
        return {"indicada":False,"dose":"Não indicada pela idade","frequencia":"—","motivo":"menor de 6 meses","orientacao":"Aguardar idade programática.","alerta":"Não administrar megadose fora da faixa programática sem indicação específica."}
    if idade_meses > 59:
        return {"indicada":False,"dose":"Fora da faixa do PNSVA","frequencia":"—","motivo":"maior de 59 meses","orientacao":"Avaliar individualmente se houver suspeita de deficiência.","alerta":"Não usar megadose programática fora dos critérios."}
    elegivel = False; motivos=[]
    if dsei:
        elegivel=True; motivos.append("DSEI: oferta universal 6–59 meses")
    if regiao_prioritaria and 6 <= idade_meses <= 23:
        elegivel=True; motivos.append("região prioritária: universal 6–23 meses")
    if regiao_prioritaria and 24 <= idade_meses <= 59 and cadastro_unico:
        elegivel=True; motivos.append("região prioritária + CadÚnico")
    if (not regiao_prioritaria) and cadastro_unico and 6 <= idade_meses <= 23:
        elegivel=True; motivos.append("CadÚnico em município aderido, se aplicável")
    dose = "100.000 UI" if idade_meses <= 11 else "200.000 UI"
    cor = "cápsula amarela" if idade_meses <= 11 else "cápsula vermelha"
    freq = "uma dose" if idade_meses <= 11 else "a cada 6 meses"
    return {"indicada":elegivel,"dose":dose,"cor_capsula":cor,"frequencia":freq,"motivo":"; ".join(motivos) if motivos else "critérios programáticos não preenchidos automaticamente", "orientacao":"Conferir se já recebeu a megadose correspondente à idade. Administrar por via oral e registrar na caderneta/sistema.", "alerta":"Não substituir 200.000 UI por duas cápsulas de 100.000 UI; não fracionar cápsula de 200.000 UI."}


def calcular_vitamina_d_sbp(idade_meses, peso_atual_kg, prematuro=False, peso_nascimento_g=None, fatores_risco=None):
    fatores_risco = fatores_risco or []
    if prematuro and peso_atual_kg < 1.5:
        return {"indicada":False,"dose":"Aguardar peso > 1.500 g","orientacao":"Em prematuros, individualizar com equipe neonatal.","prescricao":"Sem prescrição profilática automática pelo peso atual.","fatores":fatores_risco}
    if idade_meses < 12:
        dose = 400
    elif idade_meses < 24:
        dose = 600
    else:
        dose = 600 if fatores_risco else 0
    if dose == 0:
        return {"indicada":False,"dose":"Sem profilaxia universal automática após 24 meses","orientacao":"Sem suplementação universal automática; investigar/tratar se fatores de risco ou deficiência suspeita.","prescricao":"Sem prescrição automática.","fatores":fatores_risco}
    return {"indicada":True,"dose":f"{dose} UI/dia","orientacao":"Usar colecalciferol (vitamina D3), ajustando gotas/mL conforme apresentação comercial.","prescricao":f"Colecalciferol {dose} UI por via oral, 1 vez ao dia.","fatores":fatores_risco}


def recomendacao_vitaminas(idade_meses, fatores_d=None, fatores_b12=None):
    fatores_d = fatores_d or []
    fatores_b12 = fatores_b12 or []
    return {
        "Vitamina D": {"status":"Risco presente" if fatores_d else "Sem fatores selecionados", "orientacao":"Considerar suplementação/investigação conforme idade e fatores."},
        "Vitamina A": {"status":"Conferir PNSVA", "orientacao":"Verificar região/critério, idade e registro de megadose."},
        "Vitamina B12": {"status":"Risco presente" if fatores_b12 else "Sem fatores selecionados", "orientacao":"Se risco, avaliar dieta materna/infantil e necessidade de investigação/suplementação."},
    }

# =========================
# Vacinas
# =========================

def obter_mapa_vacinal_cards():
    def v(id, nome, idade, meses, dose, cor, protecao, via="IM", volume="0,5 mL", grupo="Rotina", janela="Conforme PNI", atraso="Aplicar dose faltante se elegível, sem reiniciar esquema; respeitar idade máxima e intervalo mínimo.", esperado=None, alerta=None):
        return {"id":id,"nome":nome,"idade_label":idade,"idade_meses":meses,"dose":dose,"cor":cor,"protecao":protecao,"via":via,"volume":volume,"grupo":grupo,"janela":janela,"atraso":atraso,"esperado":esperado or ["Dor local, febre baixa ou irritabilidade leve podem ocorrer."],"alerta":alerta or ["Anafilaxia, febre alta persistente, alteração importante do estado geral ou evento intenso/persistente."]}
    return [
        v("bcg","BCG","Ao nascer",0,"Dose única","#7E8CF2","Formas graves de tuberculose.","ID","0,05–0,1 mL","Ao nascer","Ao nascer, preferencialmente maternidade.","Aplicar se não registrada/cicatriz conforme idade e PNI.",["Pápula local, pústula/crosta e cicatriz são evolução habitual."],["Úlcera extensa, abscesso, linfadenite supurada ou lesão disseminada."]),
        v("hepb_nasc","Hepatite B","Ao nascer",0,"Dose ao nascer","#FDBA74","Hepatite B.","IM","0,5 mL","Ao nascer","Idealmente nas primeiras 24 horas."),
        v("penta1","Penta","2 meses",2,"1ª dose","#FED7AA","Difteria, tétano, coqueluche, hepatite B e Hib."),
        v("pneumo1","Pneumocócica 10V","2 meses",2,"1ª dose","#FEF08A","Doença pneumocócica invasiva, pneumonias e otites."),
        v("rota1","Rotavírus humano","2 meses",2,"1ª dose","#E879F9","Gastroenterite por rotavírus.","Oral","Conforme produto","2 meses","Observar idade máxima do produto/PNI.","Se ultrapassou idade máxima, não aplicar.",["Irritabilidade, diarreia/vômitos leves."],["Dor abdominal intensa, vômitos persistentes, sangue nas fezes ou suspeita de invaginação."]),
        v("vip1","VIP","2 meses",2,"1ª dose","#22D3EE","Poliomielite."),
        v("menc1","Meningocócica C","3 meses",3,"1ª dose","#BAE6FD","Doença meningocócica C."),
        v("penta2","Penta","4 meses",4,"2ª dose","#FED7AA","Difteria, tétano, coqueluche, hepatite B e Hib."),
        v("pneumo2","Pneumocócica 10V","4 meses",4,"2ª dose","#FEF08A","Doença pneumocócica invasiva, pneumonias e otites."),
        v("rota2","Rotavírus humano","4 meses",4,"2ª dose","#E879F9","Gastroenterite por rotavírus.","Oral","Conforme produto","4 meses","Observar idade máxima do produto/PNI.","Se ultrapassou idade máxima, não aplicar.",["Irritabilidade, diarreia/vômitos leves."],["Dor abdominal intensa, vômitos persistentes, sangue nas fezes ou suspeita de invaginação."]),
        v("vip2","VIP","4 meses",4,"2ª dose","#22D3EE","Poliomielite."),
        v("menc2","Meningocócica C","5 meses",5,"2ª dose","#BAE6FD","Doença meningocócica C."),
        v("penta3","Penta","6 meses",6,"3ª dose","#FED7AA","Difteria, tétano, coqueluche, hepatite B e Hib."),
        v("vip3","VIP","6 meses",6,"3ª dose","#22D3EE","Poliomielite."),
        v("covid1","Covid-19","6 meses",6,"1ª dose","#DB2777","Covid-19 e formas graves.","IM","Conforme produto"),
        v("influenza","Influenza","6 meses",6,"Anual","#86EFAC","Influenza e complicações.","IM","0,25–0,5 mL conforme idade/produto"),
        v("fa9","Febre amarela","9 meses",9,"Dose","#67E8F9","Febre amarela.","SC","0,5 mL","9 meses","Conforme área/recomendação.","Aplicar se indicada e sem contraindicação.",["Febre, cefaleia ou mialgia entre 2 e 10 dias."],["Reação alérgica grave, sinais neurológicos, icterícia/sangramento ou doença sistêmica grave."]),
        v("tv1","Tríplice viral","12 meses",12,"1ª dose","#FCA5A5","Sarampo, caxumba e rubéola.","SC","0,5 mL","12 meses","Aos 12 meses.","Aplicar se pendente e sem contraindicação.",["Febre/exantema geralmente 5–12 dias após."],["Febre alta, púrpura, convulsão, anafilaxia ou sinais neurológicos."]),
        v("pneumo_ref","Pneumocócica 10V","12 meses",12,"Reforço","#FEF08A","Doença pneumocócica."),
        v("menc_ref","Meningocócica C","12 meses",12,"Reforço","#BAE6FD","Doença meningocócica C."),
        v("dtp_ref1","DTP","15 meses",15,"1º reforço","#FDE7D3","Difteria, tétano e coqueluche."),
        v("vop_ref1","VOP","15 meses",15,"1º reforço","#67E8F9","Poliomielite.","Oral","Conforme produto","15 meses","Conforme calendário vigente.","Verificar indicação/contraindicação.",["Geralmente bem tolerada."],["Paralisia flácida aguda temporalmente associada; contraindicação em imunodeficiência."]),
        v("tetraviral","Tetraviral","15 meses",15,"Uma dose","#FCA5A5","Sarampo, caxumba, rubéola e varicela.","SC","0,5 mL"),
        v("hepa","Hepatite A","15 meses",15,"Uma dose","#C4B98B","Hepatite A."),
        v("dtp_ref2","DTP","4 anos",48,"2º reforço","#FDE7D3","Difteria, tétano e coqueluche."),
        v("vop_ref2","VOP","4 anos",48,"2º reforço","#67E8F9","Poliomielite.","Oral","Conforme produto"),
        v("varicela","Varicela","4 anos",48,"Uma dose","#E9D5FF","Varicela.","SC","0,5 mL"),
        v("fa_ref","Febre amarela","4 anos",48,"Reforço","#67E8F9","Febre amarela.","SC","0,5 mL"),
        v("pneumo23_ind","Pneumocócica 23V","5 anos",60,"Povos indígenas","#FB923C","Doença pneumocócica por sorotipos incluídos.","IM","0,5 mL"),
        v("hpv","HPV","9 a 14 anos",108,"Dose","#A78BFA","Infecções persistentes e cânceres associados ao HPV."),
    ]


def obter_calendario_vacinal():
    # Mantido para compatibilidade com versões antigas do app.
    grupos = []
    for v in obter_mapa_vacinal_cards():
        grupos.append({"idade":v["idade_label"],"meses_ref":v["idade_meses"],"cor":v["cor"],"vacinas":[{"nome":v["nome"],"dose":v["dose"],"doencas":v["protecao"]}]})
    return grupos


def obter_esquema_vacinal():
    return obter_calendario_vacinal()


def status_vacina(idade_meses_float, meses_ref, registrada=False):
    if registrada: return "Registrada", "#16a34a"
    atraso = idade_meses_float - meses_ref
    if atraso >= 1: return "Atrasada/pendente", "#dc2626"
    if -0.25 <= atraso < 1: return "Indicada agora", "#f59e0b"
    return "Futura", "#64748b"


def eventos_adversos_vacinas():
    return {v["nome"]:{"esperado":"; ".join(v["esperado"]),"alerta":"; ".join(v["alerta"])} for v in obter_mapa_vacinal_cards()}


def obter_matriz_caderneta_vacinas():
    return []

# =========================
# Desenvolvimento / orientações
# =========================

def obter_marcos_vigilancia(meses, prematuro=False):
    faixas = [
        {"faixa":"0 a 3 meses", "min":0,"max":3, "avaliacao":"Observar interação, postura, tônus, controle cervical inicial, audição e visão.", "marcos":[("Social","Fixa o olhar e acompanha face/objeto"),("Linguagem","Emite sons/gorjeios"),("Motor","Eleva a cabeça em prono"),("Audição","Reage a sons")], "proxima":["Conversar olhando nos olhos", "Tummy time supervisionado", "Estimular seguimento visual com objetos contrastantes"]},
        {"faixa":"4 a 6 meses", "min":4,"max":6, "avaliacao":"Avaliar controle cervical, rolar, apoio em antebraços, alcance e interação.", "marcos":[("Motor","Sustenta bem a cabeça"),("Motor","Rola ou inicia rolar"),("Motor fino","Leva mãos/objetos à boca"),("Social","Sorri e interage")], "proxima":["Oferecer brinquedos seguros ao alcance", "Estimular rolar dos dois lados", "Brincar no chão com supervisão"]},
        {"faixa":"7 a 9 meses", "min":7,"max":9, "avaliacao":"Verificar sentar, transferência de objetos, balbucio e resposta ao nome.", "marcos":[("Motor","Senta sem apoio ou com mínimo apoio"),("Motor fino","Transfere objetos entre as mãos"),("Linguagem","Balbucia sílabas"),("Social","Estranha pessoas e reconhece cuidadores")], "proxima":["Estimular apontar e pedir", "Ler livros de figuras", "Oferecer potes, blocos e encaixes grandes", "Permitir exploração segura"]},
        {"faixa":"10 a 12 meses", "min":10,"max":12, "avaliacao":"Avaliar engatinhar/ficar em pé, pinça, comunicação gestual e brincadeiras sociais.", "marcos":[("Motor","Fica em pé com apoio"),("Motor fino","Faz pinça"),("Linguagem","Fala mama/papa inespecífico ou gestos"),("Social","Dá tchau/bate palmas")], "proxima":["Estimular marcha com segurança", "Nomear objetos", "Brincar de esconder/achar", "Oferecer alimentos em pedaços seguros"]},
        {"faixa":"13 a 18 meses", "min":13,"max":18, "avaliacao":"Observar marcha, linguagem inicial, compreensão de comandos e autonomia.", "marcos":[("Motor","Anda com ou sem apoio"),("Linguagem","Fala algumas palavras"),("Cognição","Compreende comandos simples"),("Social","Imita atividades")], "proxima":["Estimular nomeação", "Brincar de faz de conta simples", "Permitir alimentação assistida", "Estabelecer rotina"]},
        {"faixa":"19 a 24 meses", "min":19,"max":24, "avaliacao":"Avaliar corrida, frases, jogo simbólico e autonomia.", "marcos":[("Motor","Corre ou sobe degraus com ajuda"),("Linguagem","Combina duas palavras"),("Social","Brinca de faz de conta"),("Autonomia","Ajuda a vestir/retirar peças")], "proxima":["Ler diariamente", "Estimular frases curtas", "Brincadeiras motoras seguras", "Iniciar noções de desfralde se sinais de prontidão"]},
        {"faixa":"2 a 3 anos", "min":24,"max":36, "avaliacao":"Avaliar linguagem, interação, marcha/corrida e autonomia.", "marcos":[("Linguagem","Forma frases simples"),("Motor","Corre e chuta bola"),("Social","Brinca ao lado/com outras crianças"),("Autonomia","Participa de higiene e alimentação")], "proxima":["Contar histórias", "Estimular brincadeira simbólica", "Limitar telas", "Rotina de sono e alimentação"]},
        {"faixa":"3 a 5 anos", "min":36,"max":60, "avaliacao":"Avaliar fala compreensível, coordenação, socialização e autonomia.", "marcos":[("Linguagem","Fala compreensível para familiares/estranhos"),("Motor","Pula/corre com coordenação"),("Motor fino","Desenha traços/círculos conforme idade"),("Social","Brinca cooperativamente")], "proxima":["Estimular desenho, recorte supervisionado e livros", "Brincadeiras com regras simples", "Atividade física diária", "Preparar rotina escolar"]},
        {"faixa":"5 a 10 anos", "min":60,"max":120, "avaliacao":"Avaliar desempenho escolar, socialização, sono, atividade física e comportamento.", "marcos":[("Escolar","Aprendizagem compatível"),("Social","Tem amigos e participa de regras"),("Motor","Coordenação para jogos"),("Comportamento","Regulação emocional progressiva")], "proxima":["Rotina de estudos e sono", "Atividade física", "Leitura", "Redução de telas"]},
    ]
    atual = next((f for f in faixas if f["min"] <= meses <= f["max"]), faixas[-1])
    idx = faixas.index(atual)
    anterior = faixas[idx-1] if idx > 0 else None
    proxima = faixas[idx+1] if idx < len(faixas)-1 else None
    return atual, anterior, proxima, faixas


def classificar_desenvolvimento(status_atual, status_anterior=None, fatores=None):
    status_anterior = status_anterior or []
    fatores = fatores or []
    aus = status_atual.count("Ausente") + status_anterior.count("Ausente")
    nv = status_atual.count("Não verificado") + status_anterior.count("Não verificado")
    if aus >= 2:
        return "Provável atraso/alerta importante", f"{aus} marcos ausentes; orientar estimulação e reavaliar/encaminhar.", "#dc2626"
    if aus == 1:
        return "Alerta para o desenvolvimento", "1 marco ausente; orientar estimulação e reavaliar em curto prazo.", "#f59e0b"
    if fatores:
        return "Adequado com fatores de risco", "Marcos presentes, mas há fatores de risco selecionados; manter vigilância.", "#f59e0b"
    if nv:
        return "Adequado pelo observado, com itens não verificados", f"Sem ausências marcadas; {nv} item(ns) não verificado(s).", "#0f766e"
    return "Desenvolvimento adequado para a faixa", "Marcos esperados marcados como presentes.", "#16a34a"


def imagem_desenvolvimento_por_faixa(faixa):
    mapa = {
        "0 a 3 meses":"assets/desenvolvimento/avaliacao_0_3_meses.png",
        "4 a 6 meses":"assets/desenvolvimento/avaliacao_4_6_meses.png",
        "7 a 9 meses":"assets/desenvolvimento/avaliacao_7_9_meses.png",
        "10 a 12 meses":"assets/desenvolvimento/avaliacao_10_12_meses.png",
        "13 a 18 meses":"assets/desenvolvimento/avaliacao_13_18_meses.png",
        "19 a 24 meses":"assets/desenvolvimento/avaliacao_19_24_meses.png",
        "2 a 3 anos":"assets/desenvolvimento/avaliacao_2_3_anos.png",
        "3 a 5 anos":"assets/desenvolvimento/avaliacao_3_5_anos.png",
        "5 a 10 anos":"assets/desenvolvimento/avaliacao_5_10_anos.png",
    }
    return mapa.get(faixa)


def obter_lista_imagens_app():
    return ["assets/ferro/sulfato_ferroso_gotas.png", "assets/ferro/noripurum_gotas_50mg.png", "assets/ferro/dexfer_gotas_100mg.png", "assets/ferro/noripurum_xarope_10mg.png", "assets/ferro/neutrofer_gotas.png", "assets/ferro/combiron_gotas.png"]


def obter_orientacoes_detalhadas(meses, prematuro=False):
    blocos = []
    if meses < 6:
        blocos.append({"icone":"🤱","titulo":"Alimentação","itens":["Manter aleitamento materno exclusivo até 6 meses, se possível.","Não oferecer água, chás, sucos ou alimentos antes de 6 meses sem indicação."],"conduta":"Apoiar pega, demanda livre e ganho ponderal."})
    elif meses < 24:
        blocos.append({"icone":"🍽️","titulo":"Alimentação complementar","itens":["Manter leite materno até 2 anos ou mais, se possível.","Oferecer comida de verdade, com variedade e fonte de ferro.","Evitar ultraprocessados, açúcar e bebidas adoçadas."],"conduta":"Ajustar textura e frequência conforme idade e aceitação."})
    else:
        blocos.append({"icone":"🍽️","titulo":"Alimentação saudável","itens":["Priorizar alimentos in natura/minimamente processados.","Evitar ultraprocessados e bebidas açucaradas.","Manter rotina de refeições em família."],"conduta":"Orientar conforme estado nutricional e queixa."})
    blocos += [
        {"icone":"🛌","titulo":"Sono e rotina","itens":["Manter horários regulares.","Evitar telas antes de dormir.","Investigar roncos, pausas respiratórias e despertares frequentes."],"conduta":"Adequar orientação à idade e queixa."},
        {"icone":"🦷","titulo":"Saúde bucal","itens":["Higiene oral/dental conforme dentição.","Evitar mamadeira noturna açucarada.","Encaminhar ao dentista conforme necessidade."],"conduta":"Reforçar prevenção de cárie."},
        {"icone":"🛡️","titulo":"Prevenção de acidentes","itens":["Orientar riscos domiciliares conforme idade.","Supervisionar água, quedas, queimaduras, intoxicações e engasgos.","Usar dispositivo de transporte adequado."],"conduta":"Antecipar riscos dos próximos marcos motores."},
    ]
    if prematuro:
        blocos.append({"icone":"⏱️","titulo":"Pré-termo","itens":["Usar idade corrigida para desenvolvimento nos primeiros anos.","Atenção a alimentação, crescimento e suplementação diferenciada."],"conduta":"Seguimento individualizado conforme IG, peso ao nascer e intercorrências."})
    return blocos
