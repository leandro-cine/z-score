# diretrizes.py

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

def obter_orientacoes(meses):
    if meses < 6:
        return {
            "Alimentação": "Aleitamento materno exclusivo sob livre demanda. Sem chás, água ou sucos. A mãe deve manter alimentação rica em nutrientes.",
            "Sono": "Sono seguro: decúbito dorsal (barriga para cima), berço firme e vazio (sem protetores ou ursos). Ciclos médios de 14 a 17h diárias.",
            "Higiene e Cuidados": "Banho morno diário. Cuidados com o coto umbilical (álcool 70%, manter seco). Limpeza oral desnecessária antes da erupção dentária.",
            "Segurança": "Transporte no carro em 'bebê conforto' voltado para trás. Prevenção de quedas do trocador e da cama.",
            "Telas": "Zero tempo de tela. Estimular o contato visual, conversas e cantigas."
        }
    elif meses < 12:
        return {
            "Alimentação": "Introdução da alimentação complementar aos 6 meses (frutas raspadas, papas variadas amassadas). Evitar sal. Manter leite materno. Proibido açúcar e mel.",
            "Sono": "Estabelecimento de rotina do sono. Média de 12 a 15h diárias, com 2 cochilos diurnos.",
            "Higiene e Cuidados": "Início da escovação dentária com o primeiro dente (creme dental com flúor >1000ppm, quantidade de um grão de arroz cru).",
            "Segurança": "Fase do engatinhar e andar: proteger tomadas, quinas de móveis e escadas (usar portões). Cuidado com pequenos objetos (risco de engasgo).",
            "Telas": "Zero exposição a telas (TV, celulares, tablets). Manter estímulos no chão com brinquedos seguros."
        }
    elif meses < 24:
        return {
            "Alimentação": "A partir de 1 ano, alimentação da família ajustada na consistência e corte. Estimular autonomia ao comer. Evitar sucos (preferir a fruta in natura) e ultraprocessados.",
            "Sono": "Cerca de 11 a 14h por dia, com transição para apenas 1 cochilo diurno. Incentivar a autonomia para adormecer.",
            "Higiene e Cuidados": "Higiene oral supervisionada pelos pais pós-refeições. Iniciar transição para desfralde diurno próximo aos 2 anos (se sinais de prontidão).",
            "Segurança": "Supervisão ativa. Risco elevado para intoxicação exógena (trancar medicamentos e produtos de limpeza). Prevenção de afogamentos em baldes e piscinas.",
            "Telas": "Evitar ao máximo. Se houver exposição, máximo de 1h/dia com conteúdo de alta qualidade e interação com os pais."
        }
    else:
        return {
            "Alimentação": "Dieta balanceada, evitando doces, guloseimas e fast foods. Estabelecer rotina e ambiente tranquilo nas refeições, sem o uso de telas.",
            "Sono": "Necessidade de 10 a 13h por noite. Higiene do sono: ambiente escuro, sem telas 1h antes de deitar.",
            "Higiene e Cuidados": "Estimular independência no banho e na lavagem das mãos, porém ainda com supervisão. Ida regular ao odontopediatra.",
            "Segurança": "Cadeirinha adequada no carro. Uso de equipamentos de proteção (capacete) ao andar de bicicleta ou patins. Ensinar regras básicas de trânsito e limites corporais.",
            "Telas": "Limitar a 1 hora diária de uso recreativo. Monitoramento constante dos conteúdos acessados."
        }

def obter_vacinas(meses):
    return [
        {"idade": 0, "intervalo": "Ao nascer", "vacinas": ["BCG", "Hepatite B"]},
        {"idade": 2, "intervalo": "2 meses", "vacinas": ["Penta (1ª dose)", "VIP (1ª dose)", "Pneumo 10 (1ª dose)", "Rotavírus (1ª dose)"]},
        {"idade": 3, "intervalo": "3 meses", "vacinas": ["Meningocócica C (1ª dose)"]},
        {"idade": 4, "intervalo": "4 meses", "vacinas": ["Penta (2ª dose)", "VIP (2ª dose)", "Pneumo 10 (2ª dose)", "Rotavírus (2ª dose)"]},
        {"idade": 5, "intervalo": "5 meses", "vacinas": ["Meningocócica C (2ª dose)"]},
        {"idade": 6, "intervalo": "6 meses", "vacinas": ["Penta (3ª dose)", "VIP (3ª dose)", "Covid-19 (1ª dose)", "Influenza"]},
        {"idade": 7, "intervalo": "7 meses", "vacinas": ["Covid-19 (2ª dose)"]},
        {"idade": 9, "intervalo": "9 meses", "vacinas": ["Febre Amarela (Dose inicial)", "Covid-19 (3ª dose)"]},
        {"idade": 12, "intervalo": "12 meses", "vacinas": ["Tríplice Viral (1ª dose)", "Pneumo 10 (Reforço)", "Meningocócica C (Reforço)"]},
        {"idade": 15, "intervalo": "15 meses", "vacinas": ["DTP (1º Reforço)", "VOP (1º Reforço)", "Hepatite A", "Tetraviral"]},
        {"idade": 48, "intervalo": "4 anos", "vacinas": ["DTP (2º Reforço)", "VOP (2º Reforço)", "Varicela", "Febre Amarela (Reforço)"]}
    ]

def obter_marcos(meses):
    marcos_gerais = {
        "0 a 2 meses": {
            "Social/Emocional": ["Acalma-se quando atendida", "Sorriso social", "Olha para o rosto"],
            "Linguagem": ["Faz outros sons além de chorar", "Reage a sons altos"],
            "Cognitivo": ["Observa você enquanto se move", "Olha para um brinquedo fixamente"],
            "Motor": ["Sustenta a cabeça", "Move os dois braços e pernas de forma simétrica"]
        },
        "2 a 4 meses": {
            "Social/Emocional": ["Sorri sozinha para chamar atenção", "Dá risadas ao interagir"],
            "Linguagem": ["Faz sons como 'oooo' e 'aahh'", "Responde com sons quando você fala"],
            "Cognitivo": ["Leva as mãos à boca", "Olha para as mãos com interesse"],
            "Motor": ["Rola de lado", "Alcança e segura brinquedos", "Mantém a cabeça firme"]
        },
        "4 a 6 meses": {
            "Social/Emocional": ["Reconhece pessoas conhecidas", "Gosta de se olhar no espelho"],
            "Linguagem": ["Faz sons diferentes", "Balbucia"],
            "Cognitivo": ["Coloca coisas na boca para explorar", "Passa objetos de uma mão para outra"],
            "Motor": ["Senta com apoio", "Eleva o tronco com os braços esticados (de bruços)"]
        },
        "6 a 9 meses": {
            "Social/Emocional": ["Estranha pessoas desconhecidas", "Brinca de 'esconde-achou'"],
            "Linguagem": ["Entende o 'não'", "Faz 'mamama' e 'bababa'"],
            "Cognitivo": ["Procura objetos caídos ou escondidos"],
            "Motor": ["Senta sem apoio", "Engatinha", "Puxa para levantar-se"]
        },
        "9 a 12 meses": {
            "Social/Emocional": ["Bate palmas", "Acena 'tchau'"],
            "Linguagem": ["Fala 'mama' ou 'dada' com sentido", "Responde ao próprio nome"],
            "Cognitivo": ["Bate dois objetos", "Pinça lateral e completa"],
            "Motor": ["Anda com apoio (segurando nos móveis)", "Dá os primeiros passos soltos"]
        },
        "12 a 18 meses": {
            "Social/Emocional": ["Brinca de 'faz de conta' simples", "Mostra afeto (abraça/beija)"],
            "Linguagem": ["Fala algumas palavras soltas além de mama/dada", "Aponta para pedir coisas"],
            "Cognitivo": ["Empilha 2 a 3 blocos", "Rabisca espontaneamente"],
            "Motor": ["Anda sem apoio", "Começa a tentar usar a colher e o copo"]
        },
        "18 a 24 meses": {
            "Social/Emocional": ["Percebe se os outros estão tristes", "Imita adultos"],
            "Linguagem": ["Junta duas palavras (ex: 'quer água')", "Aponta para partes do corpo"],
            "Cognitivo": ["Brinca com mais de um brinquedo ao mesmo tempo"],
            "Motor": ["Corre", "Chuta bola", "Sobe em móveis sem ajuda"]
        }
    }
    
    # Determina a chave apropriada baseada nos meses
    if meses <= 2: chave = "0 a 2 meses"
    elif meses <= 4: chave = "2 a 4 meses"
    elif meses <= 6: chave = "4 a 6 meses"
    elif meses <= 9: chave = "6 a 9 meses"
    elif meses <= 12: chave = "9 a 12 meses"
    elif meses <= 18: chave = "12 a 18 meses"
    else: chave = "18 a 24 meses"
    
    return chave, marcos_gerais[chave]
