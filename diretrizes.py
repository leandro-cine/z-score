# diretrizes.py

def obter_classificacao(z, parametro):
    if parametro == "PC":
        if z > 2:
            return "PC acima do esperado para a idade", "> +2 escores z", "#f57c00"
        elif z >= -2:
            return "PC adequado para idade", "≤ +2 e ≥ -2 escores z", "#388e3c"
        else:
            return "PC abaixo do esperado para idade", "< -2 escores z", "#d32f2f"

    elif parametro == "Peso":
        if z > 2:
            return "Peso elevado para idade", "> escore-z +2", "#f57c00"
        elif z >= -2:
            return "Peso adequado para idade", "≥ escore-z -2 e ≤ +2", "#388e3c"
        elif z >= -3:
            return "Baixo peso para idade", "≥ escore-z -3 e < -2", "#f57c00"
        else:
            return "Muito baixo peso para a idade", "< escore-z -3", "#d32f2f"

    elif parametro == "Estatura":
        if z >= -2:
            return "Estatura adequada para idade", "≥ escore-z -2", "#388e3c"
        elif z >= -3:
            return "Baixa estatura para idade", "≥ escore-z -3 e < -2", "#f57c00"
        else:
            return "Muito baixa estatura para idade", "< escore-z -3", "#d32f2f"

    elif parametro == "IMC":
        if z > 3:
            return "Obesidade", "> escore-z +3", "#d32f2f"
        elif z > 2:
            return "Sobrepeso", "> +2 e ≤ +3", "#f57c00"
        elif z > 1:
            return "Risco de sobrepeso", "> +1 e ≤ +2", "#fbc02d"
        elif z >= -2:
            return "Eutrofia", "≥ -2 e ≤ +1", "#388e3c"
        elif z >= -3:
            return "Magreza", "≥ -3 e < -2", "#f57c00"
        else:
            return "Magreza acentuada", "< escore-z -3", "#d32f2f"

    return "Classificação não disponível", "", "#607d8b"


def obter_faixas_zscore(parametro):
    """Faixas usadas para sombrear os gráficos. Usa -4/+4 como limites visuais."""
    cores = {
        "verde": ("rgba(46, 125, 50, 0.16)", "#2e7d32"),
        "amarelo": ("rgba(251, 192, 45, 0.20)", "#8d6e00"),
        "laranja": ("rgba(245, 124, 0, 0.20)", "#ef6c00"),
        "vermelho": ("rgba(211, 47, 47, 0.18)", "#c62828"),
    }

    if parametro == "IMC":
        base = [
            (-4, -3, "Magreza acentuada", "< -3Z", "vermelho"),
            (-3, -2, "Magreza", "-3Z a -2Z", "laranja"),
            (-2, 1, "Eutrofia", "-2Z a +1Z", "verde"),
            (1, 2, "Risco de sobrepeso", "+1Z a +2Z", "amarelo"),
            (2, 3, "Sobrepeso", "+2Z a +3Z", "laranja"),
            (3, 4, "Obesidade", "> +3Z", "vermelho"),
        ]
    elif parametro == "Peso":
        base = [
            (-4, -3, "Muito baixo peso", "< -3Z", "vermelho"),
            (-3, -2, "Baixo peso", "-3Z a -2Z", "laranja"),
            (-2, 2, "Peso adequado", "-2Z a +2Z", "verde"),
            (2, 4, "Peso elevado", "> +2Z", "laranja"),
        ]
    elif parametro == "Estatura":
        base = [
            (-4, -3, "Muito baixa estatura", "< -3Z", "vermelho"),
            (-3, -2, "Baixa estatura", "-3Z a -2Z", "laranja"),
            (-2, 4, "Estatura adequada", "≥ -2Z", "verde"),
        ]
    elif parametro == "PC":
        base = [
            (-4, -2, "PC abaixo do esperado", "< -2Z", "vermelho"),
            (-2, 2, "PC adequado", "-2Z a +2Z", "verde"),
            (2, 4, "PC acima do esperado", "> +2Z", "laranja"),
        ]
    else:
        base = [(-2, 2, "Adequado", "-2Z a +2Z", "verde")]

    return [
        {
            "z_min": z_min,
            "z_max": z_max,
            "rotulo": rotulo,
            "intervalo": intervalo,
            "cor_fill": cores[cor][0],
            "cor_texto": cores[cor][1],
        }
        for z_min, z_max, rotulo, intervalo, cor in base
    ]


def obter_orientacoes_detalhadas(meses):
    if meses < 6:
        return {
            "Alimentação": {
                "itens": [
                    "Manter aleitamento materno exclusivo sob livre demanda.",
                    "Não oferecer água, chás, sucos, leites artificiais ou alimentos antes dos 6 meses, salvo indicação clínica.",
                    "Observar pega, sucção efetiva, ganho ponderal e sinais de saciedade.",
                    "Reforçar sinais de alerta: recusa persistente, sonolência excessiva, perda de peso ou diurese reduzida.",
                ],
                "nota": "A consulta deve valorizar apoio à família, técnica de amamentação e prevenção do desmame precoce.",
            },
            "Sono seguro": {
                "itens": [
                    "Dormir em decúbito dorsal, em superfície firme e sem travesseiros, protetores ou objetos soltos.",
                    "Evitar superaquecimento e exposição ao tabaco.",
                    "Orientar rotina previsível de sono, respeitando os despertares esperados da idade.",
                ],
                "nota": "Sono seguro é orientação obrigatória nas consultas de lactentes pequenos.",
            },
            "Segurança e prevenção": {
                "itens": [
                    "Usar bebê conforto no banco traseiro, voltado para trás.",
                    "Nunca deixar sozinho em cama, sofá, trocador ou superfícies altas.",
                    "Checar temperatura do banho e evitar líquidos quentes próximos ao bebê.",
                    "Orientar lavagem das mãos e evitar contato com pessoas sintomáticas respiratórias.",
                ]
            },
            "Estímulos e vínculo": {
                "itens": [
                    "Conversar, cantar, sorrir e responder aos sons do bebê.",
                    "Realizar tummy time acordado e supervisionado, aumentando o tempo gradualmente.",
                    "Estimular contato visual, acompanhamento de objetos e interação com cuidadores.",
                ]
            },
        }

    elif meses < 12:
        return {
            "Alimentação complementar": {
                "itens": [
                    "Iniciar alimentação complementar a partir dos 6 meses, mantendo aleitamento materno.",
                    "Oferecer comida amassada no garfo, evoluindo textura conforme aceitação; evitar liquidificar/peneirar de rotina.",
                    "Incluir diariamente alimentos de diferentes grupos: cereais/tubérculos, leguminosas, carnes/ovos, verduras, legumes e frutas.",
                    "Evitar açúcar, mel, ultraprocessados, refrigerantes, sucos artificiais e alimentos com risco de engasgo.",
                ],
                "nota": "A família deve ser orientada sobre sinais de fome/saciedade e exposição repetida aos alimentos sem coerção.",
            },
            "Saúde bucal": {
                "itens": [
                    "Iniciar escovação desde o primeiro dente com creme dental fluoretado.",
                    "Usar quantidade equivalente a um grão de arroz cru.",
                    "Evitar mamadeira noturna açucarada e beliscos frequentes doces.",
                ]
            },
            "Segurança domiciliar": {
                "itens": [
                    "Proteger tomadas, quinas, escadas e locais de queda.",
                    "Manter objetos pequenos, medicamentos, produtos de limpeza e pilhas fora do alcance.",
                    "Supervisionar alimentação por risco de engasgo; evitar pipoca, castanhas, uvas inteiras e pedaços duros.",
                ]
            },
            "Estímulos e desenvolvimento": {
                "itens": [
                    "Brincar de esconder-achou, chamar pelo nome e estimular imitação de gestos.",
                    "Estimular sentar, engatinhar/arrastar, alcançar objetos e transferir de uma mão para outra.",
                    "Oferecer brinquedos simples, seguros, coloridos e laváveis.",
                ]
            },
        }

    else:
        return {
            "Alimentação da família": {
                "itens": [
                    "Manter refeições em horários regulares, com comida da família adaptada em sal e textura.",
                    "Evitar açúcar e ultraprocessados até 2 anos; depois, manter consumo raro e orientado.",
                    "Estimular água como bebida principal e evitar sucos como rotina.",
                    "Valorizar autonomia: permitir que a criança tente comer sozinha, com supervisão.",
                ]
            },
            "Comportamento e rotina": {
                "itens": [
                    "Estabelecer rotina previsível para sono, banho, refeições e brincadeiras.",
                    "Ler livros, nomear objetos, cantar e conversar durante atividades diárias.",
                    "Evitar telas antes dos 2 anos; após essa idade, limitar tempo e assistir junto.",
                    "Usar disciplina positiva: orientar, redirecionar e manter limites consistentes.",
                ]
            },
            "Segurança": {
                "itens": [
                    "Prevenir intoxicações: guardar medicamentos e produtos de limpeza trancados.",
                    "Prevenir afogamento: atenção a baldes, banheiras, piscinas e vasos sanitários.",
                    "Manter cadeira adequada no carro, conforme idade/peso/altura.",
                    "Supervisionar brincadeiras e orientar prevenção de quedas, queimaduras e choque elétrico.",
                ]
            },
            "Desenvolvimento e autonomia": {
                "itens": [
                    "Estimular marcha, coordenação motora fina, encaixes, rabiscos e brincadeiras simbólicas.",
                    "Observar linguagem: apontar, compreender comandos simples, falar palavras e ampliar vocabulário.",
                    "Investigar perda de marcos, ausência de interação social, falta de resposta ao nome ou atraso global.",
                ],
                "nota": "Ausência ou perda de marcos deve gerar reavaliação, orientação familiar e encaminhamento quando indicado.",
            },
        }


def obter_esquema_vacinal():
    return [
        {"idade": "Ao nascer", "cor": "#6a1b9a", "meses_ref": 0, "vacinas": [
            {"nome": "BCG", "dose": "Dose única", "doencas": "Formas graves de tuberculose"},
            {"nome": "Hepatite B", "dose": "Dose ao nascer", "doencas": "Hepatite B"},
        ]},
        {"idade": "2 meses", "cor": "#1565c0", "meses_ref": 2, "vacinas": [
            {"nome": "Penta", "dose": "1ª dose", "doencas": "Difteria, tétano, coqueluche, Hib e hepatite B"},
            {"nome": "VIP", "dose": "1ª dose", "doencas": "Poliomielite"},
            {"nome": "Pneumocócica 10V", "dose": "1ª dose", "doencas": "Pneumonias, meningites e otites pneumocócicas"},
            {"nome": "Rotavírus", "dose": "1ª dose", "doencas": "Diarreia por rotavírus"},
        ]},
        {"idade": "3 meses", "cor": "#2e7d32", "meses_ref": 3, "vacinas": [
            {"nome": "Meningocócica C", "dose": "1ª dose", "doencas": "Doença meningocócica C"},
        ]},
        {"idade": "4 meses", "cor": "#0277bd", "meses_ref": 4, "vacinas": [
            {"nome": "Penta", "dose": "2ª dose", "doencas": "Difteria, tétano, coqueluche, Hib e hepatite B"},
            {"nome": "VIP", "dose": "2ª dose", "doencas": "Poliomielite"},
            {"nome": "Pneumocócica 10V", "dose": "2ª dose", "doencas": "Pneumonias, meningites e otites pneumocócicas"},
            {"nome": "Rotavírus", "dose": "2ª dose", "doencas": "Diarreia por rotavírus"},
        ]},
        {"idade": "5 meses", "cor": "#00897b", "meses_ref": 5, "vacinas": [
            {"nome": "Meningocócica C", "dose": "2ª dose", "doencas": "Doença meningocócica C"},
        ]},
        {"idade": "6 meses", "cor": "#c2185b", "meses_ref": 6, "vacinas": [
            {"nome": "Penta", "dose": "3ª dose", "doencas": "Difteria, tétano, coqueluche, Hib e hepatite B"},
            {"nome": "VIP", "dose": "3ª dose", "doencas": "Poliomielite"},
            {"nome": "Covid-19", "dose": "1ª dose", "doencas": "Covid-19"},
            {"nome": "Influenza", "dose": "Dose anual", "doencas": "Gripe e complicações"},
        ]},
        {"idade": "9 meses", "cor": "#ef6c00", "meses_ref": 9, "vacinas": [
            {"nome": "Febre amarela", "dose": "1 dose", "doencas": "Febre amarela em áreas com recomendação"},
        ]},
        {"idade": "12 meses", "cor": "#7b1fa2", "meses_ref": 12, "vacinas": [
            {"nome": "Tríplice viral", "dose": "1ª dose", "doencas": "Sarampo, caxumba e rubéola"},
            {"nome": "Pneumocócica 10V", "dose": "Reforço", "doencas": "Doença pneumocócica"},
            {"nome": "Meningocócica C", "dose": "Reforço", "doencas": "Doença meningocócica C"},
        ]},
        {"idade": "15 meses", "cor": "#5d4037", "meses_ref": 15, "vacinas": [
            {"nome": "DTP", "dose": "1º reforço", "doencas": "Difteria, tétano e coqueluche"},
            {"nome": "VOP", "dose": "1º reforço", "doencas": "Poliomielite"},
            {"nome": "Hepatite A", "dose": "Dose única", "doencas": "Hepatite A"},
            {"nome": "Tetra viral / Varicela", "dose": "Conforme disponibilidade", "doencas": "Sarampo, caxumba, rubéola e varicela"},
        ]},
    ]


def obter_marcos_vigilancia(meses):
    marcos = {
        "0 a 2 meses": [
            {"area": "Social", "marco": "Observa um rosto?", "alerta": "Espera-se fixação visual progressiva e interesse pela face do cuidador."},
            {"area": "Audição", "marco": "Reage ao som?", "alerta": "Observar susto, pausa ou mudança de comportamento diante de sons."},
            {"area": "Motor", "marco": "Eleva a cabeça?", "alerta": "Avaliar em prono, sempre acordado e supervisionado."},
            {"area": "Social", "marco": "Sorriso social?", "alerta": "Costuma aparecer por volta de 6 a 8 semanas."},
        ],
        "2 a 4 meses": [
            {"area": "Social", "marco": "Responde ao contato social?", "alerta": "Sorri, vocaliza ou movimenta-se em resposta ao cuidador."},
            {"area": "Linguagem", "marco": "Emite sons vocálicos?", "alerta": "Ex.: 'ooo', 'aaa', arrulhos e vocalizações."},
            {"area": "Motor", "marco": "Sustenta a cabeça?", "alerta": "Observar controle cervical em colo e prono."},
            {"area": "Motor fino", "marco": "Leva mãos à boca?", "alerta": "Integra exploração corporal e coordenação inicial."},
        ],
        "4 a 6 meses": [
            {"area": "Motor fino", "marco": "Busca objeto?", "alerta": "Tenta alcançar objetos apresentados na linha média."},
            {"area": "Social", "marco": "Dá risada?", "alerta": "Resposta social a brincadeiras e interação."},
            {"area": "Motor", "marco": "Rola?", "alerta": "Observar rolar parcial ou completo conforme oportunidade de estímulo."},
            {"area": "Motor", "marco": "Senta com apoio?", "alerta": "Avaliar controle de tronco e equilíbrio com suporte."},
        ],
        "6 a 9 meses": [
            {"area": "Audição", "marco": "Localiza o som?", "alerta": "Vira a cabeça ou procura a fonte sonora."},
            {"area": "Linguagem", "marco": "Duplica sílabas?", "alerta": "Ex.: 'mama', 'baba', 'dada', ainda sem significado específico."},
            {"area": "Motor", "marco": "Senta sem apoio?", "alerta": "Manter-se sentado com equilíbrio por alguns segundos/minutos."},
            {"area": "Motor fino", "marco": "Transfere objetos?", "alerta": "Passa objeto de uma mão para outra."},
        ],
        "9 a 12 meses": [
            {"area": "Social", "marco": "Brinca de esconde-achou?", "alerta": "Demonstra permanência do objeto e interação social."},
            {"area": "Social", "marco": "Imita gestos?", "alerta": "Ex.: tchau, bater palmas, mandar beijo."},
            {"area": "Motor", "marco": "Senta sozinho?", "alerta": "Consegue sentar e manter postura com autonomia."},
            {"area": "Motor fino", "marco": "Faz pinça?", "alerta": "Pega pequenos objetos com polegar e indicador."},
        ],
    }

    if meses <= 2:
        chave = "0 a 2 meses"
    elif meses <= 4:
        chave = "2 a 4 meses"
    elif meses <= 6:
        chave = "4 a 6 meses"
    elif meses <= 9:
        chave = "6 a 9 meses"
    else:
        chave = "9 a 12 meses"
    return chave, marcos


def obter_sais_ferro():
    return {
        "Sulfato Ferroso (25mg Fe/mL) [1 gota = 1mg]": {"mg_gota": 1.0, "marcas": "FURP, Lomfer, Fersil"},
        "Ferripolimaltose (50mg Fe/mL) [1 gota = 2,5mg]": {"mg_gota": 2.5, "marcas": "Noripurum, Ultrafer"},
        "Ferripolimaltose (100mg Fe/mL) [1 gota = 5mg]": {"mg_gota": 5.0, "marcas": "Dexfer"},
        "Ferro Quelato Glicinato (50mg Fe/mL) [1 gota = 2,5mg]": {"mg_gota": 2.5, "marcas": "Neutrofer"},
        "Glicinato Férrico Associado [1 gota = 2,7mg]": {"mg_gota": 2.7, "marcas": "Combiron Gotas"},
    }
