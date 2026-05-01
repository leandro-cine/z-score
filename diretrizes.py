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
            "Sono": "Sono seguro: decúbito dorsal, berço vazio. Ciclos de 14-17h/dia.",
            "Alimentação": "Aleitamento materno exclusivo e sob livre demanda.",
            "Higiene": "Banho morno, sem sabonetes agressivos. Limpeza do coto umbilical com álcool 70%.",
            "Segurança": "Prevenção de quedas e aspiração. Transporte em 'bebê conforto' virado para trás."
        }
    elif meses < 12:
        return {
            "Sono": "Estabelecimento de rotina noturna. Média de 12-15h/dia.",
            "Alimentação": "Introdução alimentar: comida amassada, variada. Manter leite materno.",
            "Higiene": "Início da escovação dentária com pasta de dente com flúor (>1000ppm).",
            "Segurança": "Cuidado com tomadas e quinas (fase do engatinhar). Objetos pequenos fora de alcance."
        }
    else:
        return {
            "Sono": "Cerca de 11-14h/dia. Um ou dois cochilos diurnos.",
            "Alimentação": "Alimentação da família. Evitar ultraprocessados e açúcar até os 2 anos.",
            "Higiene": "Estímulo à autonomia no banho e lavagem das mãos.",
            "Segurança": "Atenção com piscinas, produtos de limpeza e escadas."
        }

def obter_vacinas(meses):
    esquema = {
        0: ["BCG", "Hepatite B"],
        2: ["Penta (1ª dose)", "VIP (1ª dose)", "Pneumo 10 (1ª dose)", "Rotavírus (1ª dose)"],
        3: ["Meningo C (1ª dose)"],
        4: ["Penta (2ª dose)", "VIP (2ª dose)", "Pneumo 10 (2ª dose)", "Rotavírus (2ª dose)"],
        5: ["Meningo C (2ª dose)"],
        6: ["Penta (3ª dose)", "VIP (3ª dose)", "Influenza (Sazonal)"],
        9: ["Febre Amarela (1ª dose)"],
        12: ["Tríplice Viral (1ª dose)", "Reforço: Pneumo 10", "Reforço: Meningo C"],
        15: ["DTP (1º Reforço)", "VOP (1º Reforço)", "Hepatite A", "Tetraviral"],
        48: ["DTP (2º Reforço)", "VOP (2º Reforço)", "Varicela", "Febre Amarela (Reforço)"]
    }
    tomadas = [v for m, v in esquema.items() if m <= meses]
    proximas = [v for m, v in esquema.items() if m > meses]
    return tomadas, proximas

def obter_marcos(meses):
    return {
        2: ["Sorriso social", "Sustenta a cabeça", "Observa o rosto"],
        4: ["Rola", "Leva mãos à boca", "Emite sons/Gritos"],
        6: ["Senta com apoio", "Passa objetos de uma mão para outra", "Balbuceia"],
        9: ["Senta sem apoio", "Engatinha ou se arrasta", "Pinça lateral"],
        12: ["Anda com apoio", "Fala pelo menos uma palavra", "Pinça completa"],
        18: ["Anda sem apoio", "Fala frases curtas", "Começa a comer sozinho"],
        24: ["Corre", "Junta duas palavras", "Brinca de faz de conta"]
    }