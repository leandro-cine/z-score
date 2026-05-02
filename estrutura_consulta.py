from __future__ import annotations

# Opções estruturadas para anamnese e exame físico pediátrico.
# A ideia é permitir seleção rápida e deixar campo aberto apenas para exceções.

INTERROGATORIO_SEGMENTAR = {
    "Geral": ["febre", "prostração", "irritabilidade", "choro inconsolável", "perda ponderal", "sudorese", "astenia", "sem queixas gerais"],
    "Pele/fâneros": ["exantema", "prurido", "lesões de pele", "palidez", "icterícia", "cianose", "equimoses/petéquias", "sem queixas cutâneas"],
    "Respiratório/ORL": ["coriza", "obstrução nasal", "tosse", "rouquidão", "sibilância", "dispneia", "dor de garganta", "otalgia", "roncos", "apneia", "sem queixas respiratórias/ORL"],
    "Cardiovascular": ["cansaço às mamadas/esforços", "síncope", "palpitações", "edema", "cianose aos esforços", "sem queixas cardiovasculares"],
    "Gastrointestinal": ["vômitos", "regurgitação", "diarreia", "constipação", "dor abdominal", "distensão abdominal", "sangue nas fezes", "inapetência", "sem queixas gastrointestinais"],
    "Geniturinário": ["disúria", "polaciúria", "urgência urinária", "odor forte na urina", "oligúria", "enurese", "corrimento", "sem queixas geniturinárias"],
    "Neurológico/desenvolvimento": ["convulsão", "cefaleia", "sonolência excessiva", "alteração de marcha", "regressão de marcos", "atraso de fala", "assimetria motora", "sem queixas neurológicas"],
    "Osteomuscular": ["dor em membros", "claudicação", "queda frequente", "limitação de movimento", "edema articular", "sem queixas osteomusculares"],
    "Sono/comportamento": ["despertares frequentes", "roncos", "irritabilidade", "agitação", "dificuldade escolar", "uso excessivo de telas", "sem queixas de sono/comportamento"],
}

ANTECEDENTES_MATERNOS = [
    "pré-natal adequado", "pré-natal incompleto", "hipertensão/pré-eclâmpsia", "diabetes gestacional", "infecção urinária",
    "sífilis", "HIV", "toxoplasmose", "rubéola", "citomegalovírus", "hepatite B/C", "sangramento gestacional",
    "ameaça de parto prematuro", "uso de álcool", "tabagismo", "uso de drogas", "anemia materna", "depressão/ansiedade perinatal",
    "vacinação gestacional adequada", "vacinação gestacional incompleta", "uso adequado de ácido fólico", "uso adequado de ferro", "uso adequado de outras suplementações"
]

INTERCORRENCIAS_PERINATAIS = [
    "parto vaginal", "parto cesáreo", "fórceps/vácuo", "bolsa rota prolongada", "líquido meconial", "sofrimento fetal",
    "prematuridade", "baixo peso", "PIG suspeito", "GIG suspeito", "asfixia/hipóxia", "Apgar baixo", "reanimação neonatal",
    "internação neonatal", "UTI neonatal", "fototerapia", "hipoglicemia", "sepse neonatal", "desconforto respiratório", "oxigenoterapia", "ventilação não invasiva", "intubação/VM", "antibiótico neonatal", "transfusão", "triagens neonatais realizadas"
]

ANTECEDENTES_PATOLOGICOS = [
    "internações", "cirurgias", "alergias medicamentosas", "alergias alimentares", "convulsões", "asma/sibilância recorrente",
    "rinite alérgica", "dermatite atópica", "pneumonias de repetição", "otites de repetição", "infecção urinária prévia", "anemia", "verminose", "doença cardíaca", "doença renal", "doença neurológica", "atraso do desenvolvimento", "transfusões", "acidentes/intoxicações"
]

ANTECEDENTES_FAMILIARES = [
    "asma", "rinite/atopia", "dermatite atópica", "diabetes", "hipertensão", "dislipidemia", "obesidade", "doença cardiovascular precoce",
    "epilepsia", "transtorno do neurodesenvolvimento", "doença genética", "tuberculose", "hanseníase", "anemia falciforme/hemoglobinopatia", "doença renal", "doença autoimune", "saúde mental", "tabagismo domiciliar"
]

TRIAGENS_NEONATAIS = {
    "Teste do Pezinho": ["normal", "alterado", "não realizado", "não sabe informar"],
    "Teste da Orelhinha": ["normal", "alterado unilateral", "alterado bilateral", "não realizado", "não sabe informar"],
    "Teste do Coraçãozinho": ["normal", "alterado", "não realizado", "não sabe informar"],
    "Teste do Olhinho": ["normal", "reflexo vermelho alterado", "assimetria", "não realizado", "não sabe informar"],
    "Teste da Linguinha": ["normal", "frênulo alterado", "não realizado", "não sabe informar"],
}

TIPOS_ALEITAMENTO = ["aleitamento materno exclusivo atual", "aleitamento materno predominante", "aleitamento misto", "fórmula infantil exclusiva", "leite de vaca", "alimentação complementar", "dieta habitual da família", "dieta seletiva/restritiva"]

HISTORICO_AME = [
    "não se aplica (< 6 meses)",
    "esteve em AME até 6 meses",
    "AME interrompido antes de 6 meses",
    "não esteve em AME",
    "não sabe informar"
]

ALIMENTO_LACTEO_ANTES_6M = [
    "não se aplica/AME",
    "fórmula infantil fortificada",
    "leite de vaca",
    "leite de cabra/outro leite animal",
    "misto com fórmula",
    "misto com leite de vaca",
    "não sabe informar"
]

PADRAO_FEZES = ["diárias", "em dias alternados", "< 3 vezes/semana", "múltiplas ao dia", "endurecidas", "pastosas", "líquidas", "com muco", "com sangue", "dor/esforço evacuatório", "escape fecal"]
PADRAO_URINA = ["diurese habitual", "reduzida", "aumentada", "odor forte", "disúria", "polaciúria", "enurese", "jato urinário fraco"]
SONO = ["sono adequado", "despertares noturnos", "roncos", "pausas respiratórias", "sono agitado", "dificuldade para iniciar sono", "cochilos diurnos adequados", "cochilos excessivos"]

CONDICOES_MORADIA = ["casa", "apartamento", "cômodo único", "alvenaria", "madeira/taipa", "área urbana", "área rural", "água tratada", "esgoto/rede", "fossa", "coleta de lixo", "mofo/umidade", "fumaça domiciliar", "animais domésticos", "aglomeração domiciliar"]

ECTOSCOPIA = ["bom estado geral", "regular estado geral", "mau estado geral", "ativo e reativo", "hipoativo", "hidratado", "desidratado", "corado", "hipocorado", "acianótico", "cianótico", "anicterico", "ictérico", "eupneico", "dispneico", "afebril ao exame", "febril ao exame"]

CABECA_PESCOCO = {
    "Fontanelas": ["normotensa", "abaulada", "deprimida", "bregmática aberta", "bregmática fechada", "fechamento precoce suspeito"],
    "Crânio": ["normocéfalo", "plagiocefalia", "braquicefalia", "dolicocefalia", "macrocefalia", "microcefalia"],
    "Linfonodos": ["sem linfonodomegalias", "linfonodos cervicais móveis/dolorosos", "linfonodomegalia persistente", "linfonodomegalia generalizada"],
    "Oftalmoscopia/olhos": ["reflexo vermelho presente bilateral", "reflexo vermelho alterado", "conjuntivas coradas", "conjuntivite", "estrabismo suspeito"],
    "Oroscopia": ["orofaringe sem alterações", "hiperemia de orofaringe", "exsudato amigdaliano", "lesões orais", "cáries visíveis", "mucosas secas"],
    "Rinoscopia": ["sem alterações", "coriza hialina", "coriza purulenta", "mucosa pálida/edemaciada", "obstrução nasal"],
    "Otoscopia": ["membranas timpânicas sem alterações", "hiperemia timpânica", "abaulamento timpânico", "otorreia", "cerume impactado"]
}

EXAME_RESPIRATORIO = {
    "Inspeção": ["eupneico", "taquipneico", "tiragens", "batimento de asa nasal", "gemência", "uso de musculatura acessória"],
    "Palpação": ["expansibilidade preservada", "expansibilidade reduzida", "frêmito preservado", "frêmito alterado"],
    "Percussão": ["som claro pulmonar", "submacicez", "hipersonoridade"],
    "Ausculta": ["murmúrio vesicular presente bilateral", "sibilos", "roncos", "estertores", "MV reduzido", "estridor"]
}
EXAME_CARDIO = {
    "Inspeção/palpação": ["precórdio sem abaulamentos", "ictus não visível", "pulsos periféricos palpáveis", "pulsos reduzidos", "perfusão periférica adequada", "TEC > 3s"],
    "Ausculta": ["ritmo cardíaco regular em 2T", "bulhas normofonéticas", "sopro sistólico", "sopro diastólico", "desdobramento alterado", "taquicardia", "bradicardia"]
}
EXAME_ABDOMINAL = {
    "Inspeção": ["abdome plano", "abdome globoso", "distendido", "cicatriz umbilical sem alterações", "hérnia umbilical"],
    "Ausculta": ["ruídos hidroaéreos presentes", "RHA aumentados", "RHA reduzidos"],
    "Palpação": ["flácido", "doloroso", "defesa", "massa palpável", "fígado palpável", "baço palpável"],
    "Percussão": ["timpanismo habitual", "macicez alterada"]
}
EXAME_OUTROS = {
    "Genitália": ["sem alterações aparentes", "fimose fisiológica", "criptorquidia", "hidrocele", "sinéquia labial", "corrimento", "assaduras/dermatite"],
    "Osteomuscular/extremidades": ["sem deformidades", "amplitude preservada", "assimetria de pregas", "Ortolani/Barlow negativos", "pé torto suspeito", "edema", "dor à mobilização"],
    "Neurológico": ["alerta", "tônus adequado", "hipotonia", "hipertonia", "força preservada", "assimetria motora", "marcha adequada para idade", "marcha alterada"],
    "Pele": ["sem lesões", "dermatite", "exantema", "lesões impetiginizadas", "escabiose suspeita", "palidez", "icterícia", "cianose", "petéquias"]
}

REFLEXOS_PRIMITIVOS = [
    "Moro presente (habitual até 4–6 meses; persistência além disso sugere alerta)",
    "Sucção presente (esperado no RN/lactente jovem)",
    "Busca/voracidade presente (esperado nos primeiros meses)",
    "Preensão palmar presente (habitual até 4–6 meses)",
    "Preensão plantar presente (pode persistir até 9–12 meses)",
    "Marcha automática presente (desaparece em torno de 2 meses)",
    "RTCA/esgrimista presente (habitual até 4–6 meses)",
    "Reflexos primitivos ausentes quando já deveriam estar integrados",
    "Persistência patológica de reflexos primitivos para a idade"
]

# Lista compacta para checagem local de disponibilidade. Não substitui RENAME/REMUME oficial.
RENAME_COMUNS = {
    "amoxicilina": ["50 mg/mL suspensão oral", "500 mg cápsula/comprimido"],
    "amoxicilina clavulanato": ["50 mg + 12,5 mg/mL suspensão oral", "500 mg + 125 mg comprimido"],
    "azitromicina": ["40 mg/mL suspensão oral", "500 mg comprimido"],
    "cefalexina": ["50 mg/mL suspensão oral", "500 mg cápsula/comprimido"],
    "sais de reidratação oral": ["pó para solução oral"],
    "paracetamol": ["200 mg/mL solução oral", "500 mg comprimido"],
    "dipirona": ["500 mg/mL solução oral", "500 mg comprimido"],
    "ibuprofeno": ["50 mg/mL solução oral", "600 mg comprimido"],
    "prednisolona": ["3 mg/mL solução oral/xarope"],
    "prednisona": ["5 mg comprimido", "20 mg comprimido"],
    "salbutamol": ["100 mcg/dose aerossol"],
    "beclometasona": ["50 mcg/dose aerossol", "200 mcg/dose aerossol"],
    "fenoterol": ["5 mg/mL solução para inalação"],
    "ipratrópio": ["0,25 mg/mL solução para inalação"],
    "loratadina": ["1 mg/mL solução oral", "10 mg comprimido"],
    "dexclorfeniramina": ["0,4 mg/mL solução oral/xarope"],
    "lactulose": ["667 mg/mL xarope"],
    "glicerol": ["solução/supositório retal"],
    "albendazol": ["40 mg/mL suspensão oral", "400 mg comprimido"],
    "sulfato ferroso": ["25 mg/mL solução oral", "40 mg comprimido"],
    "ácido fólico": ["5 mg comprimido"],
    "ondansetrona": ["4 mg comprimido/orodispersível", "8 mg comprimido/orodispersível"],
}

REMUME_PMVC_COMUNS = {
    "amoxicilina", "amoxicilina clavulanato", "azitromicina", "cefalexina", "sais de reidratação oral", "paracetamol", "dipirona", "ibuprofeno", "prednisolona", "prednisona", "salbutamol", "beclometasona", "fenoterol", "ipratrópio", "loratadina", "lactulose", "albendazol", "sulfato ferroso", "ácido fólico"
}


def checar_disponibilidade_medicamento(nome: str):
    n = (nome or "").lower().strip()
    if not n:
        return {"rename": False, "remume": False, "apresentacoes": []}
    achou = None
    for med, aps in RENAME_COMUNS.items():
        if med in n or n in med:
            achou = med; break
    return {"rename": bool(achou), "remume": bool(achou and achou in REMUME_PMVC_COMUNS), "apresentacoes": RENAME_COMUNS.get(achou, []) if achou else []}

# Complementos estruturais adicionados
BRISTOL_FEZES = [
    "Tipo 1 — caroços duros separados (constipação importante)",
    "Tipo 2 — formato de salsicha, mas grumosa (constipação)",
    "Tipo 3 — salsicha com rachaduras (tendência ao normal)",
    "Tipo 4 — salsicha/cobra lisa e macia (ideal)",
    "Tipo 5 — pedaços macios com bordas definidas (trânsito acelerado)",
    "Tipo 6 — pedaços fofos/pastosos (diarreia leve)",
    "Tipo 7 — aquosa, sem pedaços sólidos (diarreia)",
    "Não se aplica/não observado",
]

EXAME_GENITALIA = ["sem alterações aparentes", "fimose fisiológica", "fimose patológica suspeita", "criptorquidia", "hidrocele", "hérnia inguinal", "sinéquia labial", "corrimento", "assaduras/dermatite", "lesões/trauma"]
EXAME_OSTEOMUSCULAR = ["sem deformidades", "amplitude preservada", "assimetria de pregas", "Ortolani/Barlow negativos", "Ortolani/Barlow alterados", "pé torto suspeito", "dor à mobilização", "edema articular", "claudicação", "alteração de marcha"]
EXAME_NEUROLOGICO = ["alerta", "interage adequadamente", "tônus adequado", "hipotonia", "hipertonia", "força preservada", "assimetria motora", "marcha adequada para idade", "marcha alterada", "coordenação alterada", "sinais meníngeos ausentes"]
EXAME_PELE_FANEROS = ["pele íntegra", "sem lesões", "dermatite", "exantema", "lesões impetiginizadas", "escabiose suspeita", "palidez", "icterícia", "cianose", "petéquias", "equimoses", "alteração de unhas/cabelos"]

DOENCAS_MATERNAS_INFECCIOSAS = ["sífilis", "HIV", "toxoplasmose", "rubéola", "citomegalovírus", "hepatite B", "hepatite C", "infecção urinária", "corioamnionite", "COVID-19", "zika/chikungunya/dengue"]
DOENCAS_MATERNAS_CLINICAS = ["hipertensão/pré-eclâmpsia", "diabetes gestacional", "anemia materna", "tireoidopatia", "epilepsia", "asma", "doença renal", "doença cardíaca", "depressão/ansiedade perinatal", "sangramento gestacional", "ameaça de parto prematuro", "uso de álcool", "tabagismo", "uso de outras drogas"]
VACINAS_GESTACAO = ["dTpa adequada", "influenza adequada", "hepatite B adequada", "COVID-19 adequada", "vacinação incompleta", "não sabe informar"]

EXAMES_COMPLEMENTARES_MODELOS = {
    "Hemograma": ["Hb", "Ht", "leucócitos", "neutrófilos", "linfócitos", "plaquetas", "observação"],
    "Ferritina/ferro": ["ferritina", "ferro sérico", "saturação de transferrina", "PCR associada", "observação"],
    "PCR/VHS": ["PCR", "VHS", "observação"],
    "EAS/Urina tipo 1": ["leucócitos", "nitrito", "hemácias", "densidade", "observação"],
    "Urocultura": ["resultado", "UFC", "antibiograma", "observação"],
    "Parasitológico de fezes": ["resultado", "observação"],
    "Coprocultura/pesquisa viral": ["resultado", "observação"],
    "Glicemia": ["valor", "jejum?", "observação"],
    "Vitamina D 25(OH)D": ["25(OH)D", "cálcio", "fósforo", "FA", "PTH", "observação"],
    "Vitamina B12/folato": ["B12", "folato", "VCM", "observação"],
    "Radiografia de tórax": ["achado principal", "laudo", "observação"],
    "Ultrassonografia": ["região", "achado principal", "laudo", "observação"],
    "Outro": ["nome do exame", "resultado", "observação"],
}
