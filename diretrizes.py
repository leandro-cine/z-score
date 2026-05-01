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
    # Estrutura em blocos conforme imagem enviada
    return [
        {"idade": "Ao nascer", "cor": "#6a1b9a", "meses_ref": 0, "vacinas": [
            {"nome": "BCG", "dose": "Dose única", "doencas": "Tuberculose"},
            {"nome": "Hepatite B", "dose": "Dose ao nascer", "doencas": "Hepatite B"}
        ]},
        {"idade": "2 meses", "cor": "#1565c0", "meses_ref": 2, "vacinas": [
            {"nome": "Penta", "dose": "1ª dose", "doencas": "Difteria, Tétano, Coqueluche, Hib, Hep B"},
            {"nome": "VIP", "dose": "1ª dose", "doencas": "Paralisia Infantil"},
            {"nome": "Pneumocócica 10V", "dose": "1ª dose", "doencas": "Pneumonia, Meningite, Otite"},
            {"nome": "Rotavírus", "dose": "1ª dose", "doencas": "Diarreia por Rotavírus"}
        ]},
        {"idade": "3 meses", "cor": "#2e7d32", "meses_ref": 3, "vacinas": [
            {"nome": "Meningocócica C", "dose": "1ª dose", "doencas": "Meningite C"}
        ]},
        {"idade": "4 meses", "cor": "#1565c0", "meses_ref": 4, "vacinas": [
            {"nome": "Penta", "dose": "2ª dose", "doencas": "Difteria, Tétano, Coqueluche, Hib, Hep B"},
            {"nome": "VIP", "dose": "2ª dose", "doencas": "Paralisia Infantil"},
            {"nome": "Pneumocócica 10V", "dose": "2ª dose", "doencas": "Pneumonia, Meningite, Otite"},
            {"nome": "Rotavírus", "dose": "2ª dose", "doencas": "Diarreia por Rotavírus"}
        ]},
        {"idade": "5 meses", "cor": "#2e7d32", "meses_ref": 5, "vacinas": [
            {"nome": "Meningocócica C", "dose": "2ª dose", "doencas": "Meningite C"}
        ]},
        {"idade": "6 meses", "cor": "#1565c0", "meses_ref": 6, "vacinas": [
            {"nome": "Penta", "dose": "3ª dose", "doencas": "Difteria, Tétano, Coqueluche, Hib, Hep B"},
            {"nome": "VIP", "dose": "3ª dose", "doencas": "Paralisia Infantil"},
            {"nome": "Covid-19", "dose": "1ª dose", "doencas": "Covid-19"},
            {"nome": "Influenza", "dose": "Dose anual", "doencas": "Gripe"}
        ]}
    ]

def obter_marcos_caderneta(meses):
    # Vigilância oficial da Caderneta
    marcos = {
        "0 a 2 meses": ["Observa um rosto?", "Reage ao som?", "Eleva a cabeça?", "Sorriso social?"],
        "2 a 4 meses": ["Responde ao contato social?", "Emite sons (oooo/aaaa)?", "Sustenta a cabeça?", "Leva mãos à boca?"],
        "4 a 6 meses": ["Busca objeto?", "Dá risada?", "Rola?", "Senta com apoio?"],
        "6 a 9 meses": ["Localiza o som?", "Duplica sílabas (mamã/babá)?", "Senta sem apoio?", "Transfere objetos de mão?"],
        "9 a 12 meses": ["Brinca de esconde-achou?", "Imita gestos (tchau)?", "Senta sozinho?", "Pinça completa?"]
    }
    
    if meses <= 2: chave = "0 a 2 meses"
    elif meses <= 4: chave = "2 a 4 meses"
    elif meses <= 6: chave = "4 a 6 meses"
    elif meses <= 9: chave = "6 a 9 meses"
    else: chave = "9 a 12 meses"
    
    return chave, marcos
