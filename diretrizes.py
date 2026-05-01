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

def obter_orientacoes(meses):
    if meses < 6:
        return {
            "Alimentação": "Aleitamento materno exclusivo sob livre demanda. Sem chás, água ou sucos.",
            "Sono": "Sono seguro: decúbito dorsal, berço firme e vazio. Média de 14 a 17h diárias.",
            "Higiene": "Banho morno diário. Limpeza do coto umbilical com álcool 70%.",
            "Segurança": "Transporte em 'bebê conforto' voltado para trás. Prevenção de quedas.",
            "Telas": "Zero exposição a telas. Estimular contato visual e conversas."
        }
    elif meses < 12:
        return {
            "Alimentação": "Introdução alimentar aos 6 meses. Manter leite materno. Sem sal e açúcar.",
            "Sono": "Rotina do sono. Média de 12 a 15h diárias, com 2 cochilos.",
            "Higiene": "Início da escovação com flúor (>1000ppm) desde o primeiro dente.",
            "Segurança": "Proteger tomadas, quinas e escadas. Cuidado com objetos pequenos.",
            "Telas": "Zero exposição a telas."
        }
    else:
        return {
            "Alimentação": "Alimentação da família. Estimular autonomia. Evitar ultraprocessados.",
            "Sono": "11 a 14h por dia. Transição para 1 cochilo diurno.",
            "Higiene": "Higiene oral supervisionada. Iniciar sinais para desfralde.",
            "Segurança": "Trancar medicamentos e produtos de limpeza. Cuidado com afogamentos.",
            "Telas": "Evitar. Se houver, máximo 1h/dia com supervisão."
        }

def obter_esquema_vacinal():
    # Estrutura tabular igual à caderneta 
    return [
        {"idade": "Ao nascer", "vacinas": [("BCG", "Dose única"), ("Hepatite B", "Dose ao nascer")]},
        {"idade": "2 meses", "vacinas": [("Penta", "1ª dose"), ("VIP", "1ª dose"), ("Pneumo 10", "1ª dose"), ("Rotavírus", "1ª dose")]},
        {"idade": "3 meses", "vacinas": [("Meningo C", "1ª dose")]},
        {"idade": "4 meses", "vacinas": [("Penta", "2ª dose"), ("VIP", "2ª dose"), ("Pneumo 10", "2ª dose"), ("Rotavírus", "2ª dose")]},
        {"idade": "5 meses", "vacinas": [("Meningo C", "2ª dose")]},
        {"idade": "6 meses", "vacinas": [("Penta", "3ª dose"), ("VIP", "3ª dose"), ("Febre Amarela", "Dose inicial")]},
        {"idade": "9 meses", "vacinas": [("Febre Amarela", "Dose inicial (se não tomada)")]},
        {"idade": "12 meses", "vacinas": [("Tríplice Viral", "1ª dose"), ("Pneumo 10", "Reforço"), ("Meningo C", "Reforço")]},
        {"idade": "15 meses", "vacinas": [("DTP", "1º Reforço"), ("VOP", "1º Reforço"), ("Hepatite A", "Dose única"), ("Tetraviral", "Dose única")]},
        {"idade": "4 anos", "vacinas": [("DTP", "2º Reforço"), ("VOP", "2º Reforço"), ("Varicela", "Dose única"), ("Febre Amarela", "Reforço")]}
    ]

def obter_marcos_vigilancia(meses):
    # Marcos organizados por faixa etária da caderneta [cite: 1062, 1063]
    marcos = {
        "0 a 2 meses": ["Observa um rosto?", "Reage ao som?", "Eleva a cabeça?", "Sorriso social?"],
        "2 a 4 meses": ["Responde ativamente ao contato social?", "Emite sons?", "Sustenta a cabeça?", "Leva mãos à boca?"],
        "4 a 6 meses": ["Busca ativamente objeto?", "Dá risada?", "Rola?", "Senta com apoio?"],
        "6 a 9 meses": ["Localiza o som?", "Duplica sílabas (mamã, babá)?", "Senta sem apoio?", "Transfere objetos de mão?"],
        "9 a 12 meses": ["Brinca de esconde-achou?", "Imita gestos (tchau, palmas)?", "Engatinha ou senta sozinho?", "Pinça completa (polegar e indicador)?"],
        "12 a 15 meses": ["Diz uma palavra com sentido?", "Anda com apoio?", "Coloca objetos em recipientes?", "Usa copo/colher?"],
        "15 a 18 meses": ["Diz pelo menos 3 palavras?", "Anda sem apoio?", "Rabisca papel?", "Obedece ordens simples?"],
        "18 a 24 meses": ["Junta duas palavras?", "Chuta bola?", "Sobe em móveis?", "Imita tarefas domésticas?"]
    }
    
    if meses <= 2: chave = "0 a 2 meses"
    elif meses <= 4: chave = "2 a 4 meses"
    elif meses <= 6: chave = "4 a 6 meses"
    elif meses <= 9: chave = "6 a 9 meses"
    elif meses <= 12: chave = "9 a 12 meses"
    elif meses <= 15: chave = "12 a 15 meses"
    elif meses <= 18: chave = "15 a 18 meses"
    else: chave = "18 a 24 meses"
    
    return chave, marcos[chave]
