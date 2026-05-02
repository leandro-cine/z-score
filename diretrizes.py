# diretrizes.py
# Módulo de diretrizes clínicas e bases de apoio para o app de Puericultura Digital.
# Este arquivo foi estruturado para ser compatível com o app.py atualizado.
# Ele mantém as funções antigas e acrescenta as funções que estavam ausentes:
# - obter_mapa_vacinal_cards
# - calcular_vitamina_a_pnsva
# - calcular_vitamina_d_sbp
# - obter_lista_imagens_app
# - imagem_desenvolvimento_por_faixa

from __future__ import annotations


# ============================================================
# CLASSIFICAÇÃO ANTROPOMÉTRICA
# ============================================================

def obter_classificacao(z, parametro):
    """
    Classificação clínica simplificada por escore-z.
    Parâmetros esperados: Peso, Estatura, IMC, PC.
    Retorna: (classificação, critério, cor)
    """
    if parametro == "PC":
        if z > 2:
            return "PC acima do esperado para a idade", "> +2 escores-z", "#f57c00"
        elif z >= -2:
            return "PC adequado para idade", "≥ -2 e ≤ +2 escores-z", "#388e3c"
        else:
            return "PC abaixo do esperado para idade", "< -2 escores-z", "#d32f2f"

    if parametro == "Peso":
        if z > 2:
            return "Peso elevado para idade", "> +2 escores-z", "#f57c00"
        elif z >= -2:
            return "Peso adequado para idade", "≥ -2 e ≤ +2 escores-z", "#388e3c"
        elif z >= -3:
            return "Baixo peso para idade", "≥ -3 e < -2 escores-z", "#f57c00"
        else:
            return "Muito baixo peso para idade", "< -3 escores-z", "#d32f2f"

    if parametro == "Estatura":
        if z >= -2:
            return "Estatura adequada para idade", "≥ -2 escores-z", "#388e3c"
        elif z >= -3:
            return "Baixa estatura para idade", "≥ -3 e < -2 escores-z", "#f57c00"
        else:
            return "Muito baixa estatura para idade", "< -3 escores-z", "#d32f2f"

    if parametro == "IMC":
        if z > 3:
            return "Obesidade", "> +3 escores-z", "#d32f2f"
        elif z > 2:
            return "Sobrepeso", "> +2 e ≤ +3 escores-z", "#f57c00"
        elif z > 1:
            return "Risco de sobrepeso", "> +1 e ≤ +2 escores-z", "#fbc02d"
        elif z >= -2:
            return "Eutrofia", "≥ -2 e ≤ +1 escores-z", "#388e3c"
        elif z >= -3:
            return "Magreza", "≥ -3 e < -2 escores-z", "#f57c00"
        else:
            return "Magreza acentuada", "< -3 escores-z", "#d32f2f"

    return "Não classificado", "Parâmetro não reconhecido", "#64748b"


# ============================================================
# ORIENTAÇÕES GERAIS POR IDADE
# ============================================================

def obter_orientacoes_detalhadas(meses, prematuro=False, fatores_risco=None):
    """
    Orientações instrucionais por faixa etária.
    Retorna dict categoria -> texto/lista.
    """
    fatores_risco = fatores_risco or []

    base_prematuro = ""
    if prematuro:
        base_prematuro = (
            "Usar idade corrigida para interpretar crescimento e desenvolvimento nos primeiros anos, "
            "sem perder o seguimento pela idade cronológica para calendário vacinal. Reforçar sinais de alerta, "
            "orientação nutricional individualizada e seguimento de risco conforme história neonatal."
        )

    if meses < 1:
        ori = {
            "Aleitamento e nutrição": (
                "Aleitamento materno exclusivo em livre demanda. Avaliar pega, transferência de leite, diurese, evacuações, "
                "perda/recuperação ponderal e dificuldades maternas. Não oferecer água, chás ou outros leites sem indicação."
            ),
            "Sono seguro": (
                "Dormir em decúbito dorsal, em superfície firme, sem travesseiros, protetores, almofadas ou objetos soltos. "
                "Evitar superaquecimento e tabagismo no domicílio."
            ),
            "Sinais de perigo": (
                "Orientar retorno imediato se febre, hipotermia, recusa alimentar, sonolência excessiva, gemência, cianose, "
                "icterícia intensa, vômitos persistentes, convulsão ou dificuldade respiratória."
            ),
            "Prevenção": (
                "Conferir triagens neonatais, vacinação ao nascer, consulta da primeira semana e ganho ponderal."
            ),
            "Pré-termo / risco": base_prematuro,
        }
    elif meses < 6:
        ori = {
            "Aleitamento e alimentação": (
                "Manter aleitamento materno exclusivo até 6 meses. Não oferecer água, chá, suco ou alimentos. "
                "Se uso de fórmula, revisar preparo seguro, volume, frequência e sinais de intolerância."
            ),
            "Desenvolvimento": (
                "Estimular contato visual, fala afetiva, canções, brincadeiras face a face e períodos supervisionados de barriga para baixo."
            ),
            "Sono e rotina": (
                "Sono seguro em decúbito dorsal. Construir rotina previsível, com ambiente calmo à noite e exposição à luz natural durante o dia."
            ),
            "Segurança": (
                "Nunca deixar sozinho em cama, sofá, trocador ou banho. Transporte em bebê-conforto voltado para trás."
            ),
            "Saúde bucal": (
                "Antes dos dentes, não é necessário limpar a boca de rotina; quando iniciar dentição, orientar escovação com creme fluoretado em quantidade mínima."
            ),
            "Pré-termo / risco": base_prematuro,
        }
    elif meses < 12:
        ori = {
            "Alimentação complementar": (
                "Introduzir alimentação complementar a partir de 6 meses, mantendo leite materno até 2 anos ou mais. "
                "Oferecer comida amassada, não liquidificada, com variedade de grupos alimentares e evolução gradual da textura."
            ),
            "Evitar": (
                "Evitar açúcar, mel antes de 1 ano, ultraprocessados, bebidas adoçadas, biscoitos recheados, salgadinhos e sucos como rotina."
            ),
            "Desenvolvimento": (
                "Estimular sentar, engatinhar quando possível, transferência de objetos, brincadeiras de esconder, imitação, leitura de figuras e interação verbal."
            ),
            "Segurança": (
                "Proteger tomadas, quinas, escadas, fios e objetos pequenos. Atenção a engasgo, sufocação, quedas e queimaduras."
            ),
            "Saúde bucal": (
                "Escovar desde o primeiro dente com creme dental fluoretado, quantidade semelhante a um grão de arroz cru."
            ),
            "Pré-termo / risco": base_prematuro,
        }
    elif meses < 24:
        ori = {
            "Alimentação": (
                "Manter alimentação da família com comida de verdade, evitando açúcar e ultraprocessados até 2 anos. "
                "Estimular autonomia progressiva, comer sentado e sem telas."
            ),
            "Comportamento e vínculo": (
                "Rotina previsível, limites consistentes, leitura diária, brincadeiras simbólicas e incentivo à comunicação."
            ),
            "Desenvolvimento": (
                "Estimular andar, subir com ajuda, nomear objetos, apontar, imitar tarefas simples, encaixar peças e brincar com outras crianças."
            ),
            "Segurança": (
                "Risco elevado de intoxicação, afogamento em baldes/piscinas, quedas, queimaduras e ingestão de corpo estranho."
            ),
            "Telas": (
                "Evitar telas antes dos 2 anos, exceto videochamadas com interação familiar."
            ),
            "Pré-termo / risco": base_prematuro,
        }
    elif meses < 60:
        ori = {
            "Alimentação e rotina": (
                "Refeições em família, variedade de alimentos in natura e minimamente processados, rotina de sono e atividade física lúdica."
            ),
            "Desenvolvimento": (
                "Estimular linguagem, desenho, coordenação motora, brincadeira simbólica, autonomia para vestir-se e higiene com supervisão."
            ),
            "Comportamento": (
                "Orientar limites sem violência, manejo de birras, reforço positivo e ambiente com afeto e previsibilidade."
            ),
            "Segurança": (
                "Supervisão em rua, água, cozinha, medicamentos, produtos de limpeza e transporte com dispositivo adequado."
            ),
            "Telas": (
                "Evitar uso excessivo; quando houver, selecionar conteúdo, limitar tempo e assistir junto."
            ),
            "Pré-termo / risco": base_prematuro,
        }
    else:
        ori = {
            "Saúde escolar": (
                "Acompanhar rendimento, sono, alimentação, saúde mental, atividade física, visão, audição e convivência social."
            ),
            "Alimentação": (
                "Priorizar comida de verdade, água, frutas, verduras, feijão e refeições regulares; reduzir ultraprocessados e bebidas adoçadas."
            ),
            "Desenvolvimento": (
                "Estimular leitura, autonomia, esporte, brincadeiras ativas, organização de rotina e habilidades socioemocionais."
            ),
            "Segurança": (
                "Orientar uso de capacete, cinto, cadeirinha/assento conforme idade e altura, segurança digital e prevenção de violência."
            ),
            "Pré-termo / risco": base_prematuro,
        }

    # Remove campo vazio quando não pré-termo.
    return {k: v for k, v in ori.items() if v}


# ============================================================
# VACINAS
# ============================================================

def obter_esquema_vacinal():
    """
    Esquema simplificado legado, mantido por compatibilidade.
    Para o mapa novo, usar obter_mapa_vacinal_cards().
    """
    return [
        {"idade": "Ao nascer", "cor": "#6a1b9a", "meses_ref": 0, "vacinas": [
            {"nome": "BCG", "dose": "Dose única", "doencas": "Tuberculose"},
            {"nome": "Hepatite B", "dose": "Dose ao nascer", "doencas": "Hepatite B"},
        ]},
        {"idade": "2 meses", "cor": "#1565c0", "meses_ref": 2, "vacinas": [
            {"nome": "Penta", "dose": "1ª dose", "doencas": "Difteria, tétano, coqueluche, Hib, Hep B"},
            {"nome": "VIP", "dose": "1ª dose", "doencas": "Poliomielite"},
            {"nome": "Pneumocócica 10V", "dose": "1ª dose", "doencas": "Pneumonias e meningites"},
            {"nome": "Rotavírus", "dose": "1ª dose", "doencas": "Diarreia por rotavírus"},
        ]},
        {"idade": "3 meses", "cor": "#2e7d32", "meses_ref": 3, "vacinas": [
            {"nome": "Meningocócica C", "dose": "1ª dose", "doencas": "Meningite C"},
        ]},
        {"idade": "4 meses", "cor": "#1565c0", "meses_ref": 4, "vacinas": [
            {"nome": "Penta", "dose": "2ª dose", "doencas": "Difteria, tétano, coqueluche, Hib, Hep B"},
            {"nome": "VIP", "dose": "2ª dose", "doencas": "Poliomielite"},
            {"nome": "Pneumocócica 10V", "dose": "2ª dose", "doencas": "Pneumonias e meningites"},
            {"nome": "Rotavírus", "dose": "2ª dose", "doencas": "Diarreia por rotavírus"},
        ]},
        {"idade": "5 meses", "cor": "#2e7d32", "meses_ref": 5, "vacinas": [
            {"nome": "Meningocócica C", "dose": "2ª dose", "doencas": "Meningite C"},
        ]},
        {"idade": "6 meses", "cor": "#1565c0", "meses_ref": 6, "vacinas": [
            {"nome": "Penta", "dose": "3ª dose", "doencas": "Difteria, tétano, coqueluche, Hib, Hep B"},
            {"nome": "VIP", "dose": "3ª dose", "doencas": "Poliomielite"},
            {"nome": "Covid-19", "dose": "1ª dose", "doencas": "Covid-19"},
            {"nome": "Influenza", "dose": "Dose anual", "doencas": "Influenza"},
        ]},
        {"idade": "9 meses", "cor": "#00838f", "meses_ref": 9, "vacinas": [
            {"nome": "Febre amarela", "dose": "Dose inicial", "doencas": "Febre amarela"},
        ]},
        {"idade": "12 meses", "cor": "#7b1fa2", "meses_ref": 12, "vacinas": [
            {"nome": "Tríplice viral", "dose": "1ª dose", "doencas": "Sarampo, caxumba e rubéola"},
            {"nome": "Pneumocócica 10V", "dose": "Reforço", "doencas": "Doença pneumocócica"},
            {"nome": "Meningocócica C", "dose": "Reforço", "doencas": "Doença meningocócica C"},
        ]},
        {"idade": "15 meses", "cor": "#ef6c00", "meses_ref": 15, "vacinas": [
            {"nome": "DTP", "dose": "1º reforço", "doencas": "Difteria, tétano e coqueluche"},
            {"nome": "VOP", "dose": "1º reforço", "doencas": "Poliomielite"},
            {"nome": "Hepatite A", "dose": "Uma dose", "doencas": "Hepatite A"},
            {"nome": "Tetraviral", "dose": "Uma dose", "doencas": "Sarampo, caxumba, rubéola e varicela"},
        ]},
        {"idade": "4 anos", "cor": "#ad1457", "meses_ref": 48, "vacinas": [
            {"nome": "DTP", "dose": "2º reforço", "doencas": "Difteria, tétano e coqueluche"},
            {"nome": "VOP", "dose": "2º reforço", "doencas": "Poliomielite"},
            {"nome": "Varicela", "dose": "Uma dose", "doencas": "Varicela"},
            {"nome": "Febre amarela", "dose": "Reforço", "doencas": "Febre amarela"},
        ]},
    ]


def obter_mapa_vacinal_cards():
    """
    Base do mapa vacinal panorâmico em cards.
    Cada item tem id único, cor, idade, dose, instruções e EAPV resumidos.
    O app.py calcula status: futura, indicada, atrasada, registrada.
    """
    return [
        {
            "id": "bcg",
            "nome": "BCG",
            "idade_label": "Ao nascer",
            "idade_meses": 0,
            "dose": "Dose única",
            "grupo": "Até 12 meses",
            "cor": "#7E8CCB",
            "protecao": "Formas graves de tuberculose, especialmente miliar e meníngea.",
            "via": "Intradérmica",
            "volume": "0,05 mL em RN conforme produto; 0,1 mL a partir de 1 ano conforme produto disponível.",
            "janela": "Ao nascer, preferencialmente ainda na maternidade ou na primeira visita ao serviço de saúde.",
            "atraso": "Aplicar se não houver registro/cicatriz e se a criança estiver dentro da idade indicada pelo PNI. Não reiniciar esquema.",
            "esperado": [
                "Pápula local após aplicação.",
                "Evolução local lenta com pústula, crosta e cicatriz.",
                "Pequena secreção local pode ocorrer durante a evolução habitual."
            ],
            "alerta": [
                "Úlcera extensa ou persistente.",
                "Abscesso frio ou quente.",
                "Linfadenite regional supurada.",
                "Lesões disseminadas ou sinais sistêmicos, especialmente se suspeita de imunodeficiência."
            ],
        },
        {
            "id": "hepb_nascimento",
            "nome": "Hepatite B",
            "idade_label": "Ao nascer",
            "idade_meses": 0,
            "dose": "Dose ao nascer",
            "grupo": "Até 12 meses",
            "cor": "#F4A261",
            "protecao": "Hepatite B.",
            "via": "Intramuscular",
            "volume": "0,5 mL.",
            "janela": "Ao nascer, idealmente nas primeiras 24 horas.",
            "atraso": "Aplicar o quanto antes se dose ao nascer não registrada; completar esquema conforme doses subsequentes.",
            "esperado": ["Dor, rubor ou endurecimento no local.", "Febre baixa, irritabilidade ou mal-estar transitório."],
            "alerta": ["Anafilaxia ou urticária generalizada.", "Febre persistente ou alteração importante do estado geral."],
        },
        {
            "id": "penta_1", "nome": "Penta", "idade_label": "2 meses", "idade_meses": 2, "dose": "1ª dose",
            "grupo": "Até 12 meses", "cor": "#F7C59F", "protecao": "Difteria, tétano, coqueluche, hepatite B e Hib.",
            "via": "Intramuscular", "volume": "0,5 mL.", "janela": "A partir de 2 meses.",
            "atraso": "Aplicar dose pendente respeitando intervalo mínimo entre doses; não reiniciar esquema.",
            "esperado": ["Dor, vermelhidão e edema local.", "Febre nas primeiras 24–48 horas.", "Irritabilidade, sonolência ou choro."],
            "alerta": ["Febre alta persistente.", "Choro persistente/inconsolável.", "Episódio hipotônico-hiporresponsivo.", "Convulsão.", "Sinais de anafilaxia."],
        },
        {
            "id": "penta_2", "nome": "Penta", "idade_label": "4 meses", "idade_meses": 4, "dose": "2ª dose",
            "grupo": "Até 12 meses", "cor": "#F7C59F", "protecao": "Difteria, tétano, coqueluche, hepatite B e Hib.",
            "via": "Intramuscular", "volume": "0,5 mL.", "janela": "A partir de 4 meses.",
            "atraso": "Aplicar dose pendente respeitando intervalo mínimo; não reiniciar esquema.",
            "esperado": ["Dor local.", "Febre baixa.", "Irritabilidade ou sonolência."],
            "alerta": ["Febre alta.", "Choro persistente.", "Episódio hipotônico-hiporresponsivo.", "Convulsão.", "Anafilaxia."],
        },
        {
            "id": "penta_3", "nome": "Penta", "idade_label": "6 meses", "idade_meses": 6, "dose": "3ª dose",
            "grupo": "Até 12 meses", "cor": "#F7C59F", "protecao": "Difteria, tétano, coqueluche, hepatite B e Hib.",
            "via": "Intramuscular", "volume": "0,5 mL.", "janela": "A partir de 6 meses.",
            "atraso": "Aplicar dose pendente respeitando intervalo mínimo; não reiniciar esquema.",
            "esperado": ["Dor local.", "Febre baixa.", "Irritabilidade."],
            "alerta": ["Febre alta.", "Choro persistente.", "Episódio hipotônico-hiporresponsivo.", "Convulsão.", "Anafilaxia."],
        },
        {
            "id": "rota_1", "nome": "Rotavírus humano", "idade_label": "2 meses", "idade_meses": 2, "dose": "1ª dose",
            "grupo": "Até 12 meses", "cor": "#D8A7CA", "protecao": "Gastroenterite por rotavírus.",
            "via": "Oral", "volume": "Conforme apresentação.", "janela": "Observar idade mínima e máxima permitida pelo PNI.",
            "atraso": "Se ultrapassou idade máxima para iniciar/completar, não aplicar. Conferir calendário técnico.",
            "esperado": ["Irritabilidade.", "Diarreia leve ou vômitos transitórios.", "Febre baixa."],
            "alerta": ["Dor abdominal intensa.", "Vômitos persistentes.", "Sangue nas fezes.", "Choro intenso em crises ou sinais sugestivos de invaginação intestinal."],
        },
        {
            "id": "rota_2", "nome": "Rotavírus humano", "idade_label": "4 meses", "idade_meses": 4, "dose": "2ª dose",
            "grupo": "Até 12 meses", "cor": "#D8A7CA", "protecao": "Gastroenterite por rotavírus.",
            "via": "Oral", "volume": "Conforme apresentação.", "janela": "Observar idade máxima para completar esquema.",
            "atraso": "Se ultrapassou idade máxima, não aplicar. Conferir calendário técnico.",
            "esperado": ["Irritabilidade.", "Diarreia leve.", "Vômitos leves."],
            "alerta": ["Dor abdominal intensa.", "Vômitos persistentes.", "Sangue nas fezes.", "Sinais de invaginação intestinal."],
        },
        {
            "id": "pneumo10_1", "nome": "Pneumocócica 10V", "idade_label": "2 meses", "idade_meses": 2, "dose": "1ª dose",
            "grupo": "Até 12 meses", "cor": "#F6F06D", "protecao": "Pneumonias, meningites, otites e doença pneumocócica invasiva.",
            "via": "Intramuscular", "volume": "0,5 mL.", "janela": "A partir de 2 meses.",
            "atraso": "Aplicar conforme idade atual e histórico, respeitando intervalos mínimos.",
            "esperado": ["Dor local.", "Edema/rubor.", "Febre baixa.", "Irritabilidade."],
            "alerta": ["Febre alta persistente.", "Reação local extensa.", "Anafilaxia."],
        },
        {
            "id": "pneumo10_2", "nome": "Pneumocócica 10V", "idade_label": "4 meses", "idade_meses": 4, "dose": "2ª dose",
            "grupo": "Até 12 meses", "cor": "#F6F06D", "protecao": "Pneumonias, meningites, otites e doença pneumocócica invasiva.",
            "via": "Intramuscular", "volume": "0,5 mL.", "janela": "A partir de 4 meses.",
            "atraso": "Aplicar conforme idade atual e histórico, respeitando intervalos mínimos.",
            "esperado": ["Dor local.", "Edema/rubor.", "Febre baixa."],
            "alerta": ["Febre alta persistente.", "Reação local extensa.", "Anafilaxia."],
        },
        {
            "id": "vip_1", "nome": "VIP", "idade_label": "2 meses", "idade_meses": 2, "dose": "1ª dose",
            "grupo": "Até 12 meses", "cor": "#2FB9DF", "protecao": "Poliomielite.",
            "via": "Intramuscular", "volume": "0,5 mL.", "janela": "A partir de 2 meses.",
            "atraso": "Aplicar dose faltante e completar esquema sem reiniciar.",
            "esperado": ["Dor local.", "Febre baixa eventual.", "Irritabilidade."],
            "alerta": ["Anafilaxia.", "Evento neurológico temporalmente associado deve ser avaliado."],
        },
        {
            "id": "vip_2", "nome": "VIP", "idade_label": "4 meses", "idade_meses": 4, "dose": "2ª dose",
            "grupo": "Até 12 meses", "cor": "#2FB9DF", "protecao": "Poliomielite.",
            "via": "Intramuscular", "volume": "0,5 mL.", "janela": "A partir de 4 meses.",
            "atraso": "Aplicar dose faltante e completar esquema sem reiniciar.",
            "esperado": ["Dor local.", "Febre baixa eventual."],
            "alerta": ["Anafilaxia.", "Evento neurológico temporalmente associado deve ser avaliado."],
        },
        {
            "id": "vip_3", "nome": "VIP", "idade_label": "6 meses", "idade_meses": 6, "dose": "3ª dose",
            "grupo": "Até 12 meses", "cor": "#2FB9DF", "protecao": "Poliomielite.",
            "via": "Intramuscular", "volume": "0,5 mL.", "janela": "A partir de 6 meses.",
            "atraso": "Aplicar dose faltante e completar esquema sem reiniciar.",
            "esperado": ["Dor local.", "Febre baixa eventual."],
            "alerta": ["Anafilaxia.", "Evento neurológico temporalmente associado deve ser avaliado."],
        },
        {
            "id": "menc_1", "nome": "Meningocócica C", "idade_label": "3 meses", "idade_meses": 3, "dose": "1ª dose",
            "grupo": "Até 12 meses", "cor": "#BFE3E8", "protecao": "Doença meningocócica pelo sorogrupo C.",
            "via": "Intramuscular", "volume": "0,5 mL.", "janela": "A partir de 3 meses.",
            "atraso": "Aplicar conforme idade atual e histórico vacinal.",
            "esperado": ["Dor local.", "Febre baixa.", "Irritabilidade.", "Sonolência."],
            "alerta": ["Febre alta persistente.", "Reação alérgica importante.", "Anafilaxia."],
        },
        {
            "id": "menc_2", "nome": "Meningocócica C", "idade_label": "5 meses", "idade_meses": 5, "dose": "2ª dose",
            "grupo": "Até 12 meses", "cor": "#BFE3E8", "protecao": "Doença meningocócica pelo sorogrupo C.",
            "via": "Intramuscular", "volume": "0,5 mL.", "janela": "A partir de 5 meses.",
            "atraso": "Aplicar conforme idade atual e histórico vacinal.",
            "esperado": ["Dor local.", "Febre baixa.", "Irritabilidade."],
            "alerta": ["Febre alta persistente.", "Reação alérgica importante.", "Anafilaxia."],
        },
        {
            "id": "febre_amarela_1", "nome": "Febre amarela", "idade_label": "9 meses", "idade_meses": 9, "dose": "Dose inicial",
            "grupo": "Até 12 meses", "cor": "#75C9D2", "protecao": "Febre amarela.",
            "via": "Subcutânea", "volume": "0,5 mL.", "janela": "A partir de 9 meses, conforme área/recomendação do PNI.",
            "atraso": "Aplicar se indicada e não registrada, avaliando contraindicações.",
            "esperado": ["Dor local.", "Febre, cefaleia ou mialgia entre 2 e 10 dias.", "Mal-estar transitório."],
            "alerta": ["Reação alérgica grave.", "Sintomas neurológicos.", "Icterícia, sangramentos ou sinais sistêmicos graves após vacinação."],
        },
        {
            "id": "triplice_viral_1", "nome": "Tríplice viral", "idade_label": "12 meses", "idade_meses": 12, "dose": "1ª dose",
            "grupo": "A partir de 12 meses", "cor": "#D18B8B", "protecao": "Sarampo, caxumba e rubéola.",
            "via": "Subcutânea", "volume": "0,5 mL.", "janela": "Aos 12 meses.",
            "atraso": "Aplicar se pendente, avaliando contraindicações para vacina de vírus vivo.",
            "esperado": ["Febre e exantema geralmente entre 5 e 12 dias.", "Dor local.", "Aumento transitório de linfonodos ou parótidas."],
            "alerta": ["Febre alta persistente.", "Convulsão febril.", "Púrpura/trombocitopenia.", "Anafilaxia.", "Sinais neurológicos."],
        },
        {
            "id": "covid_1", "nome": "Covid-19", "idade_label": "6 meses", "idade_meses": 6, "dose": "1ª dose",
            "grupo": "Até 12 meses", "cor": "#CC168B", "protecao": "Covid-19 e formas graves da doença.",
            "via": "Intramuscular", "volume": "Conforme fabricante.", "janela": "A partir de 6 meses, conforme calendário vigente.",
            "atraso": "Atualizar conforme esquema vigente e produto disponível.",
            "esperado": ["Dor local.", "Febre baixa.", "Cansaço.", "Irritabilidade."],
            "alerta": ["Anafilaxia.", "Dor torácica, dispneia ou palpitações.", "Febre persistente ou alteração importante do estado geral."],
        },
        {
            "id": "influenza_anual", "nome": "Influenza", "idade_label": "6 meses", "idade_meses": 6, "dose": "Anual",
            "grupo": "Até 12 meses", "cor": "#9CA3AF", "protecao": "Influenza e formas graves.",
            "via": "Intramuscular", "volume": "Conforme idade/produto.", "janela": "A partir de 6 meses em campanhas anuais.",
            "atraso": "Atualizar durante campanha ou conforme disponibilidade.",
            "esperado": ["Dor local.", "Febre baixa.", "Mialgia ou mal-estar."],
            "alerta": ["Anafilaxia.", "Sintomas neurológicos importantes.", "Febre persistente."],
        },
        {
            "id": "pneumo10_ref", "nome": "Pneumocócica 10V", "idade_label": "12 meses", "idade_meses": 12, "dose": "Reforço",
            "grupo": "A partir de 12 meses", "cor": "#F6F06D", "protecao": "Doença pneumocócica.",
            "via": "Intramuscular", "volume": "0,5 mL.", "janela": "Aos 12 meses.",
            "atraso": "Aplicar reforço se pendente, respeitando idade e histórico.",
            "esperado": ["Dor local.", "Febre baixa.", "Irritabilidade."],
            "alerta": ["Febre alta persistente.", "Reação local extensa.", "Anafilaxia."],
        },
        {
            "id": "menc_ref", "nome": "Meningocócica C", "idade_label": "12 meses", "idade_meses": 12, "dose": "Reforço",
            "grupo": "A partir de 12 meses", "cor": "#BFE3E8", "protecao": "Doença meningocócica C.",
            "via": "Intramuscular", "volume": "0,5 mL.", "janela": "Aos 12 meses.",
            "atraso": "Aplicar reforço se pendente conforme histórico.",
            "esperado": ["Dor local.", "Febre baixa.", "Sonolência ou irritabilidade."],
            "alerta": ["Anafilaxia.", "Febre alta persistente."],
        },
        {
            "id": "dtp_ref1", "nome": "DTP", "idade_label": "15 meses", "idade_meses": 15, "dose": "1º reforço",
            "grupo": "A partir de 12 meses", "cor": "#F4DDC8", "protecao": "Difteria, tétano e coqueluche.",
            "via": "Intramuscular", "volume": "0,5 mL.", "janela": "Aos 15 meses.",
            "atraso": "Aplicar reforço pendente, respeitando intervalo mínimo.",
            "esperado": ["Dor, edema e vermelhidão local.", "Febre.", "Irritabilidade."],
            "alerta": ["Reação local extensa.", "Febre alta.", "Choro persistente.", "EHH.", "Convulsão.", "Anafilaxia."],
        },
        {
            "id": "dtp_ref2", "nome": "DTP", "idade_label": "4 anos", "idade_meses": 48, "dose": "2º reforço",
            "grupo": "A partir de 12 meses", "cor": "#F4DDC8", "protecao": "Difteria, tétano e coqueluche.",
            "via": "Intramuscular", "volume": "0,5 mL.", "janela": "Aos 4 anos.",
            "atraso": "Aplicar reforço pendente, respeitando intervalo mínimo.",
            "esperado": ["Dor local.", "Edema local.", "Febre."],
            "alerta": ["Reação local extensa.", "Febre alta.", "EHH.", "Convulsão.", "Anafilaxia."],
        },
        {
            "id": "vop_ref1", "nome": "VOP", "idade_label": "15 meses", "idade_meses": 15, "dose": "1º reforço",
            "grupo": "A partir de 12 meses", "cor": "#73C9D1", "protecao": "Poliomielite.",
            "via": "Oral", "volume": "Conforme apresentação.", "janela": "Aos 15 meses, conforme calendário vigente.",
            "atraso": "Verificar calendário técnico vigente; aplicar se indicada e sem contraindicação.",
            "esperado": ["Geralmente bem tolerada.", "Sintomas gastrointestinais leves podem ocorrer."],
            "alerta": ["Paralisia flácida aguda temporalmente associada.", "Contraindicada em imunodeficiência."],
        },
        {
            "id": "vop_ref2", "nome": "VOP", "idade_label": "4 anos", "idade_meses": 48, "dose": "2º reforço",
            "grupo": "A partir de 12 meses", "cor": "#73C9D1", "protecao": "Poliomielite.",
            "via": "Oral", "volume": "Conforme apresentação.", "janela": "Aos 4 anos, conforme calendário vigente.",
            "atraso": "Verificar calendário técnico vigente; aplicar se indicada e sem contraindicação.",
            "esperado": ["Geralmente bem tolerada."],
            "alerta": ["Paralisia flácida aguda temporalmente associada.", "Contraindicada em imunodeficiência."],
        },
        {
            "id": "tetraviral", "nome": "Tetraviral", "idade_label": "15 meses", "idade_meses": 15, "dose": "Uma dose",
            "grupo": "A partir de 12 meses", "cor": "#DDAAAA", "protecao": "Sarampo, caxumba, rubéola e varicela.",
            "via": "Subcutânea", "volume": "0,5 mL.", "janela": "Aos 15 meses, após tríplice viral.",
            "atraso": "Aplicar se pendente e se não houver contraindicação para vacina de vírus vivo.",
            "esperado": ["Febre.", "Exantema.", "Dor local.", "Lesões tipo varicela leves podem ocorrer."],
            "alerta": ["Febre alta.", "Convulsão febril.", "Anafilaxia.", "Exantema intenso/disseminado.", "Sinais neurológicos."],
        },
        {
            "id": "varicela", "nome": "Varicela", "idade_label": "4 anos", "idade_meses": 48, "dose": "Uma dose",
            "grupo": "A partir de 12 meses", "cor": "#E8CCCC", "protecao": "Varicela.",
            "via": "Subcutânea", "volume": "0,5 mL.", "janela": "Aos 4 anos, conforme calendário.",
            "atraso": "Aplicar se pendente e se não houver contraindicação para vacina de vírus vivo.",
            "esperado": ["Dor local.", "Febre baixa.", "Exantema leve ou vesículas isoladas."],
            "alerta": ["Exantema disseminado.", "Anafilaxia.", "Sinais neurológicos."],
        },
        {
            "id": "hepa", "nome": "Hepatite A", "idade_label": "15 meses", "idade_meses": 15, "dose": "Uma dose",
            "grupo": "A partir de 12 meses", "cor": "#B3B08A", "protecao": "Hepatite A.",
            "via": "Intramuscular", "volume": "0,5 mL.", "janela": "Aos 15 meses.",
            "atraso": "Aplicar se pendente conforme idade permitida pelo PNI.",
            "esperado": ["Dor local.", "Cefaleia.", "Febre baixa.", "Mal-estar."],
            "alerta": ["Anafilaxia.", "Febre persistente ou alteração importante do estado geral."],
        },
        {
            "id": "hpv_1", "nome": "HPV", "idade_label": "9–14 anos", "idade_meses": 108, "dose": "Dose conforme PNI",
            "grupo": "A partir de 9 anos", "cor": "#A493C4", "protecao": "Infecções persistentes e cânceres associados ao HPV.",
            "via": "Intramuscular", "volume": "0,5 mL.", "janela": "Conforme faixa etária do calendário vigente.",
            "atraso": "Aplicar conforme idade, sexo/grupo e calendário vigente.",
            "esperado": ["Dor local.", "Cefaleia.", "Febre baixa.", "Síncope relacionada ao procedimento pode ocorrer em adolescentes."],
            "alerta": ["Anafilaxia.", "Síncope com trauma.", "Sintomas neurológicos persistentes."],
        },
        {
            "id": "pneumo23_indigena", "nome": "Pneumocócica 23V", "idade_label": "5 anos", "idade_meses": 60, "dose": "Uma dose",
            "grupo": "Povos indígenas", "cor": "#F7941D", "protecao": "Doença pneumocócica por sorotipos incluídos na VPP23.",
            "via": "Intramuscular", "volume": "0,5 mL.", "janela": "Indicada para povos indígenas conforme calendário.",
            "atraso": "Aplicar conforme indicação específica e histórico vacinal.",
            "esperado": ["Dor local.", "Endurecimento.", "Febre baixa."],
            "alerta": ["Reação local intensa.", "Anafilaxia."],
        },
    ]


# ============================================================
# DESENVOLVIMENTO
# ============================================================

def obter_marcos_vigilancia(meses):
    """
    Função legada: retorna chave da faixa atual e dicionário simples de marcos.
    """
    marcos = {
        "0 a 2 meses": ["Observa um rosto?", "Reage ao som?", "Eleva a cabeça?", "Sorriso social?"],
        "2 a 4 meses": ["Responde ao contato social?", "Emite sons (oooo/aaaa)?", "Sustenta a cabeça?", "Leva mãos à boca?"],
        "4 a 6 meses": ["Busca objeto?", "Dá risada?", "Rola?", "Senta com apoio?"],
        "6 a 9 meses": ["Localiza o som?", "Duplica sílabas (mamã/babá)?", "Senta sem apoio?", "Transfere objetos?"],
        "9 a 12 meses": ["Brinca de esconde-achou?", "Imita gestos (tchau)?", "Senta sozinho?", "Pinça completa?"],
        "12 a 18 meses": ["Anda com ou sem apoio?", "Fala palavras com significado?", "Aponta para pedir?", "Empilha blocos?"],
        "18 a 24 meses": ["Corre?", "Fala várias palavras?", "Brinca de faz de conta?", "Usa colher com ajuda?"],
        "2 a 3 anos": ["Forma frases curtas?", "Sobe escadas com ajuda?", "Imita adultos?", "Brinca ao lado de outras crianças?"],
        "3 a 5 anos": ["Conta histórias simples?", "Pula?", "Desenha formas simples?", "Brinca cooperativamente?"],
        "5 a 10 anos": ["Acompanha escola?", "Tem coordenação motora compatível?", "Interage socialmente?", "Realiza autocuidado progressivo?"],
    }

    faixas = list(marcos.keys())
    limites = [2, 4, 6, 9, 12, 18, 24, 36, 60, 120]
    chave = faixas[-1]
    for faixa, limite in zip(faixas, limites):
        if meses <= limite:
            chave = faixa
            break
    return chave, marcos


def obter_linha_tempo_desenvolvimento():
    """
    Estrutura mais completa para linha do tempo:
    - marcos esperados
    - como avaliar na consulta
    - estimulação próxima
    - sinais de alerta
    """
    return [
        {
            "faixa": "0 a 3 meses",
            "min_meses": 0,
            "max_meses": 3,
            "imagem_base": "avaliacao_0_3_meses",
            "marcos": [
                {"area": "Social", "marco": "Fixa e acompanha faces brevemente.", "avaliar": "Aproxime o rosto a 20–30 cm e observe fixação/seguimento."},
                {"area": "Audição", "marco": "Reage a sons.", "avaliar": "Produza som suave fora do campo visual e observe sobressalto, pausa ou procura."},
                {"area": "Motor", "marco": "Eleva a cabeça em prono progressivamente.", "avaliar": "Coloque em prono acordado e supervisionado por poucos minutos."},
                {"area": "Linguagem", "marco": "Emite sons guturais e inicia sorriso social.", "avaliar": "Fale com a criança face a face e observe vocalização/sorriso."},
            ],
            "estimulo": [
                "Conversar olhando para o bebê.",
                "Cantar e responder aos sons.",
                "Tummy time acordado e supervisionado.",
                "Alternar posição da cabeça e oferecer estímulos visuais simples."
            ],
            "alerta": [
                "Não reage a sons fortes.",
                "Não fixa o olhar.",
                "Hipotonia ou hipertonia importante.",
                "Assimetria persistente."
            ],
        },
        {
            "faixa": "4 a 6 meses",
            "min_meses": 4,
            "max_meses": 6,
            "imagem_base": "avaliacao_4_6_meses",
            "marcos": [
                {"area": "Motor", "marco": "Sustenta melhor a cabeça e rola.", "avaliar": "Observar controle cervical em tração para sentar e em prono."},
                {"area": "Social", "marco": "Sorri, dá risada e busca interação.", "avaliar": "Interaja com expressões e observe reciprocidade."},
                {"area": "Motor fino", "marco": "Leva mãos à boca e busca objetos.", "avaliar": "Ofereça brinquedo leve na linha média."},
                {"area": "Linguagem", "marco": "Balbucia sons vocálicos.", "avaliar": "Fale com a criança e aguarde resposta vocal."},
            ],
            "estimulo": [
                "Oferecer brinquedos leves e seguros.",
                "Brincar de rolar com supervisão.",
                "Estimular alcance na linha média.",
                "Conversar e imitar sons do bebê."
            ],
            "alerta": [
                "Não sustenta cabeça.",
                "Não sorri ou não interage.",
                "Não leva mãos à boca.",
                "Muita rigidez ou flacidez."
            ],
        },
        {
            "faixa": "7 a 9 meses",
            "min_meses": 7,
            "max_meses": 9,
            "imagem_base": "avaliacao_7_9_meses",
            "marcos": [
                {"area": "Motor", "marco": "Senta sem apoio progressivamente.", "avaliar": "Coloque sentado em superfície segura e observe equilíbrio."},
                {"area": "Motor fino", "marco": "Transfere objetos entre as mãos.", "avaliar": "Ofereça brinquedo e observe troca de mão."},
                {"area": "Linguagem", "marco": "Duplica sílabas.", "avaliar": "Escutar balbucios como babá, mamã sem significado específico."},
                {"area": "Social", "marco": "Brinca de esconder/achou.", "avaliar": "Cubra o rosto e reapareça observando antecipação e riso."},
            ],
            "estimulo": [
                "Brincar no chão em local seguro.",
                "Oferecer potes, blocos grandes e brinquedos de encaixe simples.",
                "Estimular apontar e pedir.",
                "Ler livros de figuras."
            ],
            "alerta": [
                "Não senta com apoio.",
                "Não busca objetos.",
                "Não vocaliza.",
                "Perda de habilidades adquiridas."
            ],
        },
        {
            "faixa": "10 a 12 meses",
            "min_meses": 10,
            "max_meses": 12,
            "imagem_base": "avaliacao_10_12_meses",
            "marcos": [
                {"area": "Motor", "marco": "Fica em pé com apoio e pode iniciar passos laterais.", "avaliar": "Permitir apoio seguro em móvel baixo e observar estabilidade."},
                {"area": "Motor fino", "marco": "Pinça mais precisa.", "avaliar": "Ofereça pequeno alimento seguro ou objeto grande o suficiente para não aspirar."},
                {"area": "Linguagem", "marco": "Entende comandos simples com gesto.", "avaliar": "Peça 'dá tchau' ou 'cadê?' com contexto."},
                {"area": "Social", "marco": "Imita gestos.", "avaliar": "Fazer tchau, bater palmas e observar imitação."},
            ],
            "estimulo": [
                "Estimular gestos: tchau, beijo, bater palmas.",
                "Nomear objetos e pessoas.",
                "Permitir exploração segura no chão.",
                "Brincar de colocar e tirar objetos de potes."
            ],
            "alerta": [
                "Não senta sem apoio.",
                "Não responde ao nome.",
                "Não balbucia.",
                "Não demonstra interesse social."
            ],
        },
        {
            "faixa": "13 a 18 meses",
            "min_meses": 13,
            "max_meses": 18,
            "imagem_base": "avaliacao_13_18_meses",
            "marcos": [
                {"area": "Motor", "marco": "Anda com ou sem apoio.", "avaliar": "Observar marcha em ambiente seguro."},
                {"area": "Linguagem", "marco": "Fala palavras com significado.", "avaliar": "Perguntar aos cuidadores palavras usadas consistentemente."},
                {"area": "Social", "marco": "Aponta para pedir ou mostrar.", "avaliar": "Observar se aponta para objetos de interesse."},
                {"area": "Motor fino", "marco": "Empilha blocos ou manipula objetos.", "avaliar": "Oferecer blocos grandes e observar coordenação."},
            ],
            "estimulo": [
                "Ler livros nomeando figuras.",
                "Dar escolhas simples.",
                "Estimular andar com segurança, sem andador.",
                "Brincar de encaixar e empilhar."
            ],
            "alerta": [
                "Não anda até 18 meses.",
                "Não fala nenhuma palavra com significado.",
                "Não aponta.",
                "Pouco contato visual ou pouca reciprocidade."
            ],
        },
        {
            "faixa": "19 a 24 meses",
            "min_meses": 19,
            "max_meses": 24,
            "imagem_base": "avaliacao_19_24_meses",
            "marcos": [
                {"area": "Motor", "marco": "Corre e sobe degraus com ajuda.", "avaliar": "Observar mobilidade e equilíbrio."},
                {"area": "Linguagem", "marco": "Amplia vocabulário e combina palavras.", "avaliar": "Perguntar frases espontâneas e compreensão de comandos."},
                {"area": "Social", "marco": "Brinca de faz de conta simples.", "avaliar": "Oferecer boneco/carrinho e observar simbolismo."},
                {"area": "Autonomia", "marco": "Ajuda a vestir-se e usa colher com derrames.", "avaliar": "Perguntar rotina aos cuidadores."},
            ],
            "estimulo": [
                "Narrar atividades do dia.",
                "Estimular brincadeira simbólica.",
                "Oferecer lápis grosso para rabiscos.",
                "Incentivar autonomia supervisionada."
            ],
            "alerta": [
                "Não combina palavras aos 24 meses.",
                "Não imita ações.",
                "Não compreende comandos simples.",
                "Perda de fala ou interação."
            ],
        },
        {
            "faixa": "2 a 3 anos",
            "min_meses": 24,
            "max_meses": 36,
            "imagem_base": "avaliacao_2_3_anos",
            "marcos": [
                {"area": "Linguagem", "marco": "Forma frases curtas.", "avaliar": "Observar fala espontânea e inteligibilidade."},
                {"area": "Motor", "marco": "Sobe escadas com ajuda e chuta bola.", "avaliar": "Perguntar/observar coordenação motora ampla."},
                {"area": "Social", "marco": "Brinca ao lado de outras crianças.", "avaliar": "Investigar interação em casa/escola."},
                {"area": "Motor fino", "marco": "Rabiscos e início de traços.", "avaliar": "Oferecer papel e giz/lápis grosso."},
            ],
            "estimulo": [
                "Ler diariamente.",
                "Conversar em frases completas.",
                "Estimular brincadeiras motoras.",
                "Evitar telas como substituto de interação."
            ],
            "alerta": [
                "Não fala frases.",
                "Não compreende ordens simples.",
                "Isolamento social importante.",
                "Quedas muito frequentes ou regressão."
            ],
        },
        {
            "faixa": "3 a 5 anos",
            "min_meses": 36,
            "max_meses": 60,
            "imagem_base": "avaliacao_3_5_anos",
            "marcos": [
                {"area": "Linguagem", "marco": "Conta histórias simples e faz perguntas.", "avaliar": "Conversar e observar narrativa."},
                {"area": "Motor", "marco": "Pula, corre e melhora equilíbrio.", "avaliar": "Observar brincadeiras motoras."},
                {"area": "Motor fino", "marco": "Desenha formas simples.", "avaliar": "Solicitar círculo/cruz conforme idade."},
                {"area": "Social", "marco": "Brinca cooperativamente.", "avaliar": "Perguntar sobre escola e interação."},
            ],
            "estimulo": [
                "Brincadeiras de imaginação.",
                "Desenho, recorte supervisionado e massinha.",
                "Jogos com regras simples.",
                "Estimular autonomia em higiene e vestir."
            ],
            "alerta": [
                "Fala pouco inteligível.",
                "Não brinca com outras crianças.",
                "Dificuldade motora importante.",
                "Comportamentos restritos com prejuízo funcional."
            ],
        },
        {
            "faixa": "5 a 10 anos",
            "min_meses": 60,
            "max_meses": 120,
            "imagem_base": "avaliacao_5_10_anos",
            "marcos": [
                {"area": "Escolar", "marco": "Acompanha aprendizagem esperada.", "avaliar": "Investigar leitura, escrita, atenção e desempenho escolar."},
                {"area": "Social", "marco": "Mantém amizades e brincadeiras com regras.", "avaliar": "Perguntar convivência e comportamento."},
                {"area": "Motor", "marco": "Coordenação motora progressiva.", "avaliar": "Observar corrida, salto, equilíbrio e atividades esportivas."},
                {"area": "Autonomia", "marco": "Autocuidado progressivo.", "avaliar": "Perguntar higiene, sono, organização e responsabilidades."},
            ],
            "estimulo": [
                "Rotina de sono e estudo.",
                "Leitura diária.",
                "Atividade física regular.",
                "Redução de telas e supervisão digital."
            ],
            "alerta": [
                "Dificuldade escolar persistente.",
                "Isolamento social.",
                "Desatenção/hiperatividade com prejuízo.",
                "Regressão de habilidades."
            ],
        },
    ]


def imagem_desenvolvimento_por_faixa(faixa_ou_meses):
    """
    Retorna nome-base de imagem em assets/desenvolvimento/ sem extensão.
    Aceita string com faixa ou número de meses.
    O app.py deve procurar extensões: png, jpg, jpeg, webp, bmp, gif.
    """
    linha = obter_linha_tempo_desenvolvimento()

    if isinstance(faixa_ou_meses, (int, float)):
        meses = float(faixa_ou_meses)
        for item in linha:
            if item["min_meses"] <= meses <= item["max_meses"]:
                return item["imagem_base"]
        return "avaliacao_5_10_anos"

    texto = str(faixa_ou_meses).strip().lower()
    for item in linha:
        if item["faixa"].lower() == texto:
            return item["imagem_base"]

    # fallback por trechos
    mapa = {
        "0": "avaliacao_0_3_meses",
        "4": "avaliacao_4_6_meses",
        "7": "avaliacao_7_9_meses",
        "10": "avaliacao_10_12_meses",
        "13": "avaliacao_13_18_meses",
        "19": "avaliacao_19_24_meses",
        "2 a 3": "avaliacao_2_3_anos",
        "3 a 5": "avaliacao_3_5_anos",
        "5 a 10": "avaliacao_5_10_anos",
    }
    for chave, img in mapa.items():
        if chave in texto:
            return img
    return None


# ============================================================
# SUPLEMENTAÇÃO: FERRO
# ============================================================

def obter_sais_ferro():
    """
    Apresentações líquidas de ferro elementar.
    imagem_base deve corresponder ao nome do arquivo em assets/ferro/ sem extensão.
    O app.py pode aceitar png/jpg/jpeg/webp/bmp/gif.
    """
    return {
        "Sulfato Ferroso (25 mg Fe/mL) [1 gota = 1 mg]": {
            "tipo": "Sulfato ferroso gotas",
            "mg_ml": 25.0,
            "gotas_ml": 25,
            "mg_gota": 1.0,
            "marcas": "Sulfato Ferroso genérico; FURP; Lomfer; Fersil",
            "preco": "Aprox. R$ 3,50 a R$ 15 para 30 mL",
            "observacao": "Opção clássica e barata; pode causar desconforto gastrointestinal, escurecimento de fezes e manchas dentárias.",
            "imagem_base": "sulfato_ferroso_gotas",
        },
        "Ferripolimaltose (50 mg Fe/mL) [1 gota = 2,5 mg]": {
            "tipo": "Ferripolimaltose / hidróxido férrico polimaltosado gotas 50 mg/mL",
            "mg_ml": 50.0,
            "gotas_ml": 20,
            "mg_gota": 2.5,
            "marcas": "Noripurum gotas 50 mg/mL; Ultrafer; genéricos",
            "preco": "Aprox. R$ 43 a R$ 55 para 30 mL",
            "observacao": "Mais concentrado; facilita menor número de gotas.",
            "imagem_base": "noripurum_gotas_50mg",
        },
        "Ferripolimaltose (100 mg Fe/mL) [1 gota = 5 mg]": {
            "tipo": "Ferripolimaltose gotas 100 mg/mL",
            "mg_ml": 100.0,
            "gotas_ml": 20,
            "mg_gota": 5.0,
            "marcas": "Dexfer 100 mg/mL",
            "preco": "Aprox. R$ 45 a R$ 70 conforme disponibilidade",
            "observacao": "Muito concentrado; exige atenção para evitar erro de dose.",
            "imagem_base": "dexfer_gotas_100mg",
        },
        "Ferripolimaltose xarope (10 mg Fe/mL)": {
            "tipo": "Ferripolimaltose / hidróxido férrico polimaltosado xarope 10 mg/mL",
            "mg_ml": 10.0,
            "gotas_ml": None,
            "mg_gota": None,
            "marcas": "Noripurum xarope 10 mg/mL",
            "preco": "Aprox. R$ 32 a R$ 40 para 120 mL",
            "observacao": "Cálculo por mL; útil para seringa dosadora.",
            "imagem_base": "noripurum_xarope_10mg",
        },
        "Ferro quelato glicinato (50 mg Fe/mL) [1 gota = 2,5 mg]": {
            "tipo": "Ferro quelato glicinato / glicinato férrico gotas",
            "mg_ml": 50.0,
            "gotas_ml": 20,
            "mg_gota": 2.5,
            "marcas": "Neutrofer gotas",
            "preco": "Aprox. R$ 52 a R$ 65 para 30 mL",
            "observacao": "Conferir bula: sempre calcular por ferro elementar.",
            "imagem_base": "neutrofer_gotas",
        },
        "Glicinato férrico associado [1 gota ≈ 2,7 mg]": {
            "tipo": "Glicinato férrico associado a vitaminas",
            "mg_ml": 27.58,
            "gotas_ml": 20,
            "mg_gota": 2.7,
            "marcas": "Combiron gotas",
            "preco": "Variável conforme farmácia",
            "observacao": "Possui associação com vitaminas; atenção para duplicidade de suplementos.",
            "imagem_base": "combiron_gotas",
        },
    }


def calcular_ferro_profilatico(
    idade_meses,
    peso_kg,
    prematuro=False,
    peso_nascimento_g=None,
    termo_peso_adequado_sem_risco=True,
    fatores_risco=None,
):
    """
    Retorna recomendação resumida de ferro profilático.
    - Termo, peso adequado e sem risco: pode seguir esquema MS/SBP harmonizado em ciclos de 10–12,5 mg/dia.
    - Prematuro, baixo peso ou risco: individualiza por mg/kg/dia.
    """
    fatores_risco = fatores_risco or []
    peso_nascimento_g = peso_nascimento_g or 0

    if idade_meses < 3:
        return {
            "indicado": prematuro or peso_nascimento_g < 2500 or bool(fatores_risco),
            "regime": "Avaliar risco neonatal",
            "dose_mg_dia": 0 if not (prematuro or peso_nascimento_g < 2500 or fatores_risco) else round(peso_kg * 2, 1),
            "texto": "Antes de 3 meses, suplementação depende de prematuridade, peso ao nascer, condição neonatal e orientação pediátrica.",
        }

    if termo_peso_adequado_sem_risco and (not prematuro) and peso_nascimento_g >= 2500 and not fatores_risco:
        if 6 <= idade_meses < 9:
            return {
                "indicado": True,
                "regime": "MS/SBP — 1º ciclo",
                "dose_mg_dia": 10,
                "faixa_dose": "10 a 12,5 mg/dia",
                "texto": "1º ciclo profilático dos 6 aos 9 meses. Pausa dos 9 aos 12 meses.",
            }
        if 9 <= idade_meses < 12:
            return {
                "indicado": False,
                "regime": "Pausa entre ciclos",
                "dose_mg_dia": 0,
                "faixa_dose": "—",
                "texto": "Pausa programática dos 9 aos 12 meses se 1º ciclo realizado.",
            }
        if 12 <= idade_meses < 15:
            return {
                "indicado": True,
                "regime": "MS/SBP — 2º ciclo",
                "dose_mg_dia": 10,
                "faixa_dose": "10 a 12,5 mg/dia",
                "texto": "2º ciclo profilático dos 12 aos 15 meses.",
            }
        return {
            "indicado": False,
            "regime": "Fora do ciclo universal",
            "dose_mg_dia": 0,
            "faixa_dose": "—",
            "texto": "Para termo, peso adequado e sem risco, verificar se ciclos foram completos; após isso, avaliar risco e dieta.",
        }

    # Situações de risco: regra de apoio.
    if prematuro or peso_nascimento_g < 2500:
        if idade_meses < 12:
            dose = 2.0
            if peso_nascimento_g and peso_nascimento_g < 1500:
                dose = 3.0
            if peso_nascimento_g and peso_nascimento_g < 1000:
                dose = 4.0
            return {
                "indicado": True,
                "regime": "SBP — prematuro/baixo peso no primeiro ano",
                "dose_mg_kg_dia": dose,
                "dose_mg_dia": round(peso_kg * dose, 1),
                "texto": f"Dose estimada: {dose} mg/kg/dia no primeiro ano, ajustável conforme peso ao nascer e condição clínica.",
            }
        if idade_meses < 24:
            return {
                "indicado": True,
                "regime": "SBP — segundo ano em prematuro/baixo peso",
                "dose_mg_kg_dia": 1.0,
                "dose_mg_dia": round(peso_kg * 1.0, 1),
                "texto": "Após o primeiro ano, usar 1 mg/kg/dia até 24 meses, conforme avaliação clínica.",
            }

    if fatores_risco:
        return {
            "indicado": True,
            "regime": "Risco para anemia — individualizar",
            "dose_mg_kg_dia": 1.0,
            "dose_mg_dia": round(peso_kg * 1.0, 1),
            "texto": "Há fatores de risco para deficiência de ferro/anemia; avaliar dieta, hemograma/ferritina quando indicado e considerar 1 mg/kg/dia.",
        }

    return {
        "indicado": False,
        "regime": "Sem indicação automática",
        "dose_mg_dia": 0,
        "texto": "Não há indicação automática calculada; avaliar dieta, história e exames quando necessário.",
    }


def modelo_prescricao_ferro(nome_sal, dados_sal, dose_mg_dia):
    """
    Gera prescrição textual baseada na dose de ferro elementar/dia e apresentação.
    """
    if not dose_mg_dia or dose_mg_dia <= 0:
        return "Sem prescrição profilática automática no momento."

    marcas = dados_sal.get("marcas", nome_sal)
    mg_gota = dados_sal.get("mg_gota")
    mg_ml = dados_sal.get("mg_ml")

    if mg_gota:
        gotas = max(1, round(dose_mg_dia / mg_gota))
        dose_real = round(gotas * mg_gota, 1)
        return (
            f"{marcas}: administrar {gotas} gota(s) por via oral 1 vez ao dia "
            f"({dose_real} mg/dia de ferro elementar), preferencialmente longe de leite e derivados. "
            f"Reavaliar adesão, tolerância e necessidade de continuidade conforme faixa etária e risco."
        )

    if mg_ml:
        ml = round(dose_mg_dia / mg_ml, 2)
        dose_real = round(ml * mg_ml, 1)
        return (
            f"{marcas}: administrar {ml} mL por via oral 1 vez ao dia "
            f"({dose_real} mg/dia de ferro elementar), com seringa dosadora. "
            f"Reavaliar adesão, tolerância e necessidade de continuidade conforme faixa etária e risco."
        )

    return "Não foi possível calcular apresentação: conferir ferro elementar por gota ou mL."


# ============================================================
# SUPLEMENTAÇÃO: VITAMINA A
# ============================================================

def calcular_vitamina_a_pnsva(idade_meses, regiao_prioritaria=False, cadastro_unico=False, dsei=False):
    """
    PNSVA/MS:
    - 6 a 11 meses: 100.000 UI, uma dose.
    - 12 a 59 meses: 200.000 UI, a cada 6 meses.
    Critérios programáticos dependem de região, CadÚnico e DSEI.
    """
    idade_meses = float(idade_meses)

    if idade_meses < 6:
        return {
            "indicada": False,
            "dose": "Não indicada pela idade",
            "cor_capsula": "—",
            "frequencia": "—",
            "motivo": "Menor de 6 meses.",
            "orientacao": "Aguardar 6 meses, salvo indicação médica específica.",
            "alerta": "Não administrar megadose fora da faixa etária programática sem indicação específica.",
        }

    if idade_meses > 59:
        return {
            "indicada": False,
            "dose": "Fora da faixa do PNSVA",
            "cor_capsula": "—",
            "frequencia": "—",
            "motivo": "Maior de 59 meses.",
            "orientacao": "Avaliar deficiência suspeita individualmente.",
            "alerta": "PNSVA é direcionado a crianças de 6 a 59 meses conforme critérios.",
        }

    motivos = []
    elegivel = False

    if dsei:
        elegivel = True
        motivos.append("DSEI: oferta universal de 6 a 59 meses.")

    if regiao_prioritaria and 6 <= idade_meses <= 23:
        elegivel = True
        motivos.append("Região prioritária: oferta universal de 6 a 23 meses.")

    if regiao_prioritaria and 24 <= idade_meses <= 59 and cadastro_unico:
        elegivel = True
        motivos.append("Região prioritária + CadÚnico: oferta de 24 a 59 meses.")

    if (not regiao_prioritaria) and cadastro_unico and 6 <= idade_meses <= 23:
        elegivel = True
        motivos.append("Sul/Sudeste: priorizar 6 a 23 meses no CadÚnico em municípios aderidos.")

    if 6 <= idade_meses <= 11:
        dose = "100.000 UI"
        cor_capsula = "cápsula amarela"
        frequencia = "Uma dose"
    else:
        dose = "200.000 UI"
        cor_capsula = "cápsula vermelha"
        frequencia = "Uma vez a cada 6 meses"

    return {
        "indicada": elegivel,
        "dose": dose,
        "cor_capsula": cor_capsula,
        "frequencia": frequencia,
        "motivo": " | ".join(motivos) if motivos else "Critérios programáticos não preenchidos automaticamente.",
        "orientacao": (
            "Administrar por via oral, abrindo a cápsula no momento do uso e garantindo ingestão de todo o conteúdo. "
            "Registrar na Caderneta da Criança e no sistema da APS."
        ),
        "alerta": (
            "Não substituir 200.000 UI por duas cápsulas de 100.000 UI e não usar meia cápsula de 200.000 UI "
            "para simular 100.000 UI. Conferir dose, validade e rótulo antes da administração."
        ),
    }


# ============================================================
# SUPLEMENTAÇÃO: VITAMINA D
# ============================================================

def calcular_vitamina_d_sbp(idade_meses, peso_atual_kg, prematuro=False, peso_nascimento_g=None, fatores_risco=None):
    """
    Prevenção de hipovitaminose D em pediatria.
    Regra prática usada no app:
    - 0 a 12 meses: 400 UI/dia.
    - 12 a 24 meses: 600 UI/dia.
    - Após 24 meses: avaliar risco; se risco presente, sugerir 600 UI/dia ou individualização.
    - Prematuro com peso atual < 1.500 g: sinalizar início quando > 1.500 g salvo conduta neonatal.
    """
    idade_meses = float(idade_meses)
    peso_atual_kg = float(peso_atual_kg or 0)
    fatores_risco = fatores_risco or []

    if prematuro and peso_atual_kg and peso_atual_kg < 1.5:
        return {
            "indicada": False,
            "dose": "Aguardar peso > 1.500 g",
            "orientacao": "Em prematuros, iniciar suplementação oral quando peso for maior que 1.500 g, salvo conduta neonatal específica.",
            "risco": fatores_risco,
            "prescricao": "Ainda sem prescrição profilática automática pelo peso atual.",
        }

    if idade_meses < 12:
        dose_ui = 400
    elif idade_meses < 24:
        dose_ui = 600
    else:
        dose_ui = 600 if fatores_risco else 0

    if dose_ui == 0:
        return {
            "indicada": False,
            "dose": "Sem profilaxia universal automática após 24 meses",
            "orientacao": "Avaliar dieta, exposição solar segura, fatores de risco e necessidade de dosagem/tratamento.",
            "risco": fatores_risco,
            "prescricao": "Sem prescrição automática.",
        }

    return {
        "indicada": True,
        "dose": f"{dose_ui} UI/dia",
        "orientacao": (
            "Usar colecalciferol (vitamina D3). Ajustar conforme apresentação comercial em gotas ou mL. "
            "Evitar manipulações quando houver risco de erro de dose."
        ),
        "risco": fatores_risco,
        "prescricao": f"Colecalciferol {dose_ui} UI por via oral, 1 vez ao dia.",
    }


# ============================================================
# LISTAS DE IMAGENS ESPERADAS PELO APP
# ============================================================

def obter_lista_imagens_app():
    """
    Lista de nomes-base das imagens que podem ser anexadas ao repositório.
    O app.py deve aceitar extensões variadas: .png, .jpg, .jpeg, .webp, .bmp, .gif.

    Estrutura sugerida:
    assets/ferro/<nome_base>.<ext>
    assets/desenvolvimento/<nome_base>.<ext>
    """
    return {
        "ferro": [
            "sulfato_ferroso_gotas",
            "noripurum_gotas_50mg",
            "dexfer_gotas_100mg",
            "noripurum_xarope_10mg",
            "neutrofer_gotas",
            "combiron_gotas",
        ],
        "desenvolvimento": [
            "avaliacao_0_3_meses",
            "avaliacao_4_6_meses",
            "avaliacao_7_9_meses",
            "avaliacao_10_12_meses",
            "avaliacao_13_18_meses",
            "avaliacao_19_24_meses",
            "avaliacao_2_3_anos",
            "avaliacao_3_5_anos",
            "avaliacao_5_10_anos",
        ],
        "pastas": [
            "assets/ferro/",
            "assets/desenvolvimento/",
        ],
        "extensoes_aceitas": [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"],
    }


# ============================================================
# UTILITÁRIOS DE RISCO
# ============================================================

def classificar_risco_nascimento(idade_gestacional_semanas, peso_nascimento_g):
    """
    Classificação de apoio para risco em puericultura.
    Não substitui curva peso/idade gestacional.
    """
    ig = float(idade_gestacional_semanas or 0)
    peso = float(peso_nascimento_g or 0)

    riscos = []
    if ig and ig < 37:
        riscos.append("Pré-termo")
    if peso:
        if peso < 1000:
            riscos.append("Extremo baixo peso")
        elif peso < 1500:
            riscos.append("Muito baixo peso")
        elif peso < 2500:
            riscos.append("Baixo peso ao nascer")
        else:
            riscos.append("Peso ≥ 2.500 g")

    if not riscos:
        riscos.append("Dados de nascimento incompletos")

    return riscos
