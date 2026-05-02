# diretrizes.py
# Base técnica para app Streamlit de puericultura.
# Estrutura modular para facilitar atualização conforme MS/SBP/PNI.

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple
import math


def obter_classificacao(z: float, parametro: str):
    if parametro == "PC":
        if z > 2:
            return "PC acima do esperado para a idade", "> +2 escores-z", "#f97316"
        if z >= -2:
            return "PC adequado para idade", "entre -2 e +2 escores-z", "#16a34a"
        return "PC abaixo do esperado para idade", "< -2 escores-z", "#dc2626"
    if parametro == "Peso":
        if z > 2:
            return "Peso elevado para idade", "> +2 escores-z", "#f97316"
        if z >= -2:
            return "Peso adequado para idade", "entre -2 e +2 escores-z", "#16a34a"
        if z >= -3:
            return "Baixo peso para idade", "entre -3 e -2 escores-z", "#f59e0b"
        return "Muito baixo peso para idade", "< -3 escores-z", "#dc2626"
    if parametro == "Estatura":
        if z >= -2:
            return "Estatura adequada para idade", ">= -2 escores-z", "#16a34a"
        if z >= -3:
            return "Baixa estatura para idade", "entre -3 e -2 escores-z", "#f59e0b"
        return "Muito baixa estatura para idade", "< -3 escores-z", "#dc2626"
    if parametro == "IMC":
        if z > 3:
            return "Obesidade", "> +3 escores-z", "#dc2626"
        if z > 2:
            return "Sobrepeso", "> +2 e <= +3 escores-z", "#f97316"
        if z > 1:
            return "Risco de sobrepeso", "> +1 e <= +2 escores-z", "#eab308"
        if z >= -2:
            return "Eutrofia", "entre -2 e +1 escores-z", "#16a34a"
        if z >= -3:
            return "Magreza", "entre -3 e -2 escores-z", "#f59e0b"
        return "Magreza acentuada", "< -3 escores-z", "#dc2626"
    return "Sem classificação", "", "#64748b"


def obter_faixas_zscore(parametro: str):
    if parametro == "IMC":
        return [
            {"z_min": -4, "z_max": -3, "rotulo": "Magreza acentuada", "intervalo": "< -3Z", "cor_fill": "rgba(220,38,38,.14)"},
            {"z_min": -3, "z_max": -2, "rotulo": "Magreza", "intervalo": "-3Z a -2Z", "cor_fill": "rgba(245,158,11,.16)"},
            {"z_min": -2, "z_max": 1, "rotulo": "Eutrofia", "intervalo": "-2Z a +1Z", "cor_fill": "rgba(34,197,94,.13)"},
            {"z_min": 1, "z_max": 2, "rotulo": "Risco de sobrepeso", "intervalo": "+1Z a +2Z", "cor_fill": "rgba(234,179,8,.16)"},
            {"z_min": 2, "z_max": 3, "rotulo": "Sobrepeso", "intervalo": "+2Z a +3Z", "cor_fill": "rgba(249,115,22,.16)"},
            {"z_min": 3, "z_max": 4, "rotulo": "Obesidade", "intervalo": "> +3Z", "cor_fill": "rgba(220,38,38,.16)"},
        ]
    if parametro == "Estatura":
        return [
            {"z_min": -4, "z_max": -3, "rotulo": "Muito baixa estatura", "intervalo": "< -3Z", "cor_fill": "rgba(220,38,38,.14)"},
            {"z_min": -3, "z_max": -2, "rotulo": "Baixa estatura", "intervalo": "-3Z a -2Z", "cor_fill": "rgba(245,158,11,.16)"},
            {"z_min": -2, "z_max": 4, "rotulo": "Estatura adequada", "intervalo": ">= -2Z", "cor_fill": "rgba(34,197,94,.12)"},
        ]
    if parametro == "Peso":
        return [
            {"z_min": -4, "z_max": -3, "rotulo": "Muito baixo peso", "intervalo": "< -3Z", "cor_fill": "rgba(220,38,38,.14)"},
            {"z_min": -3, "z_max": -2, "rotulo": "Baixo peso", "intervalo": "-3Z a -2Z", "cor_fill": "rgba(245,158,11,.16)"},
            {"z_min": -2, "z_max": 2, "rotulo": "Peso adequado", "intervalo": "-2Z a +2Z", "cor_fill": "rgba(34,197,94,.12)"},
            {"z_min": 2, "z_max": 4, "rotulo": "Peso elevado", "intervalo": "> +2Z", "cor_fill": "rgba(249,115,22,.15)"},
        ]
    return [
        {"z_min": -4, "z_max": -2, "rotulo": "PC baixo", "intervalo": "< -2Z", "cor_fill": "rgba(220,38,38,.14)"},
        {"z_min": -2, "z_max": 2, "rotulo": "PC adequado", "intervalo": "-2Z a +2Z", "cor_fill": "rgba(34,197,94,.12)"},
        {"z_min": 2, "z_max": 4, "rotulo": "PC elevado", "intervalo": "> +2Z", "cor_fill": "rgba(249,115,22,.15)"},
    ]


def fatores_risco_anemia():
    return {
        "maternos_gestacionais": [
            "Anemia materna ou deficiência de ferro na gestação", "Baixa adesão ao pré-natal ou vulnerabilidade social",
            "Gestação múltipla", "Intervalo interpartal curto", "Sangramento gestacional importante",
            "Restrição alimentar materna importante ou dieta vegetariana/vegana sem suplementação adequada"
        ],
        "crianca": [
            "Prematuridade", "Baixo peso ao nascer (< 2.500 g)", "Pequeno para idade gestacional (PIG)",
            "Gemelaridade", "Aleitamento materno exclusivo após 6 meses sem alimentação rica em ferro",
            "Uso de leite de vaca antes de 12 meses", "Alimentação complementar pobre em ferro",
            "Doença crônica, inflamatória ou gastrointestinal", "Perdas sanguíneas ou parasitoses", "Crescimento acelerado/catch-up"
        ]
    }


def fatores_risco_hipovitaminose_d():
    return [
        "Pouca exposição solar", "Pele escura com baixa exposição solar", "Uso constante de roupas muito fechadas/protetor sem orientação",
        "Prematuridade", "Obesidade", "Má absorção intestinal", "Doença hepática ou renal crônica",
        "Uso de anticonvulsivantes, glicocorticoides ou antirretrovirais", "Mãe com deficiência de vitamina D"
    ]


def fatores_risco_vitamina_b12():
    return [
        "Mãe vegetariana/vegana sem suplementação", "Mãe com cirurgia bariátrica", "Mãe com anemia megaloblástica ou deficiência de B12",
        "Lactente em aleitamento materno exclusivo com risco materno", "Dieta restritiva da criança", "Doença gastrointestinal/má absorção"
    ]


def classificar_peso_ig(peso_nasc_g: float, idade_gest_sem: float):
    # Triagem simplificada; classificação formal AIG/PIG/GIG exige curva por IG/sexo.
    if peso_nasc_g <= 0:
        return "Não informado", []
    riscos = []
    if idade_gest_sem < 37:
        riscos.append("pré-termo")
    if peso_nasc_g < 2500:
        riscos.append("baixo peso ao nascer")
    if peso_nasc_g < 1500:
        riscos.append("muito baixo peso ao nascer")
    if peso_nasc_g >= 4000:
        riscos.append("macrossomia")
    resumo = ", ".join(riscos) if riscos else "termo/peso adequado presumido, se AIG"
    return resumo, riscos


def obter_sais_ferro():
    return {
        "Sulfato ferroso gotas 25 mg Fe/mL (≈ 1 mg/gota)": {
            "tipo": "gotas", "mg_por_unidade": 1.0, "unidade": "gota", "concentracao": "25 mg de ferro elementar/mL", "marcas": "Sulfato ferroso genérico, FURP, Lomfer, Fersil", "obs": "Opção clássica e econômica; pode causar desconforto gastrointestinal e escurecimento das fezes.", "imagem": "assets/ferro/sulfato_ferroso.png"
        },
        "Ferripolimaltose gotas 50 mg Fe/mL (≈ 2,5 mg/gota)": {
            "tipo": "gotas", "mg_por_unidade": 2.5, "unidade": "gota", "concentracao": "50 mg de ferro elementar/mL", "marcas": "Noripurum gotas, Ultrafer, genéricos", "obs": "Mais concentrado; menor número de gotas. Conferir bula e equivalência de ferro elementar.", "imagem": "https://cosmos.bluesoft.com.br/assets/produtos/7896641805479"
        },
        "Ferripolimaltose gotas 100 mg Fe/mL (≈ 5 mg/gota)": {
            "tipo": "gotas", "mg_por_unidade": 5.0, "unidade": "gota", "concentracao": "100 mg de ferro elementar/mL", "marcas": "Dexfer e apresentações equivalentes", "obs": "Muito concentrado; atenção para evitar erro de dose.", "imagem": "assets/ferro/ferripolimaltose_100.png"
        },
        "Ferripolimaltose xarope 10 mg Fe/mL": {
            "tipo": "mL", "mg_por_unidade": 10.0, "unidade": "mL", "concentracao": "10 mg de ferro elementar/mL", "marcas": "Noripurum xarope e equivalentes", "obs": "Cálculo em mL; útil com seringa dosadora.", "imagem": "assets/ferro/noripurum_xarope.png"
        },
        "Ferro quelato glicinato gotas 50 mg Fe/mL (≈ 2,5 mg/gota)": {
            "tipo": "gotas", "mg_por_unidade": 2.5, "unidade": "gota", "concentracao": "50 mg de ferro elementar/mL", "marcas": "Neutrofer gotas e equivalentes", "obs": "Conferir se a bula informa sal total ou ferro elementar.", "imagem": "https://www.santaluciadrogarias.com.br/arquivos/ids/193615-800-800?v=637793663575630000&width=800&height=800&aspect=true"
        },
        "Glicinato férrico associado a vitaminas (≈ 2,7 mg/gota)": {
            "tipo": "gotas", "mg_por_unidade": 2.7, "unidade": "gota", "concentracao": "aprox. 27,5 mg Fe/mL, conforme apresentação", "marcas": "Combiron gotas e similares", "obs": "Atenção aos componentes associados e à faixa etária indicada na bula.", "imagem": "assets/ferro/combiron.png"
        },
    }


def recomendacao_ferro(meses: float, peso_atual_kg: float, peso_nasc_g: float, idade_gest_sem: float, aleitamento_exclusivo: bool, fatores_crianca: List[str], fatores_maternos: List[str]):
    termo = idade_gest_sem >= 37
    peso_adequado = peso_nasc_g >= 2500
    tem_risco = (not termo) or (not peso_adequado) or bool(fatores_crianca) or bool(fatores_maternos)

    if meses < 3 and not tem_risco:
        return {
            "protocolo": "Aguardando idade de início",
            "dose_mg_dia": 0.0,
            "dose_mg_kg_dia": 0.0,
            "resumo": "Criança sem fator de risco informado e com menos de 3 meses: em geral, ainda sem início de ferro profilático de rotina.",
            "conduta": "Reavaliar aos 3–6 meses conforme protocolo escolhido, alimentação e risco.",
        }

    if termo and peso_adequado and not fatores_crianca and not fatores_maternos:
        if 6 <= meses < 9 or 12 <= meses < 15:
            dose = 12.5 if peso_atual_kg >= 8 else 10.0
            return {
                "protocolo": "MS/SBP — termo, AIG/peso adequado, sem fatores de risco",
                "dose_mg_dia": dose,
                "dose_mg_kg_dia": dose / peso_atual_kg if peso_atual_kg else 0,
                "resumo": "Profilaxia em ciclos: 6–9 meses e 12–15 meses, com 10 a 12,5 mg/dia de ferro elementar.",
                "conduta": "Prescrever ciclo de 3 meses; pausar entre 9–12 meses; reiniciar de 12–15 meses. Associar orientação alimentar rica em ferro.",
            }
        if 9 <= meses < 12:
            return {"protocolo": "Pausa entre ciclos", "dose_mg_dia": 0.0, "dose_mg_kg_dia": 0.0, "resumo": "Intervalo de pausa entre 9 e 12 meses para criança termo, peso adequado e sem fatores de risco.", "conduta": "Manter alimentação rica em ferro e reavaliar no início do 2º ciclo."}
        if meses < 6:
            return {"protocolo": "Aguardar 6 meses", "dose_mg_dia": 0.0, "dose_mg_kg_dia": 0.0, "resumo": "Para termo, peso adequado e sem fatores de risco, iniciar aos 6 meses.", "conduta": "Orientar aleitamento materno e alimentação materna; reavaliar aos 6 meses."}
        return {"protocolo": "Ciclos concluídos/fora da janela", "dose_mg_dia": 0.0, "dose_mg_kg_dia": 0.0, "resumo": "Fora dos ciclos profiláticos de rotina para termo sem risco.", "conduta": "Investigar dieta, sintomas e hemograma/ferritina conforme clínica."}

    # Situações especiais: seguir lógica SBP em mg/kg/dia, com maior intensidade no primeiro ano.
    if idade_gest_sem < 37 or peso_nasc_g < 2500:
        if peso_nasc_g < 1500:
            alvo = 3.0
        elif peso_nasc_g < 2500:
            alvo = 2.0
        else:
            alvo = 2.0
        if meses >= 12:
            alvo = 1.0
        dose = peso_atual_kg * alvo
        return {"protocolo": "Pré-termo/baixo peso", "dose_mg_dia": dose, "dose_mg_kg_dia": alvo, "resumo": f"Criança com prematuridade/baixo peso: usar {alvo:g} mg/kg/dia de ferro elementar nesta etapa.", "conduta": "Individualizar conforme peso ao nascer, idade corrigida, dieta, exames e seguimento de risco."}

    alvo = 1.0 if meses >= 3 else 0.0
    dose = peso_atual_kg * alvo
    return {"protocolo": "Presença de fatores de risco", "dose_mg_dia": dose, "dose_mg_kg_dia": alvo, "resumo": "Há fatores de risco maternos ou da criança; usar dose em mg/kg/dia e acompanhar resposta/adesão.", "conduta": "Investigar anemia/deficiência de ferro se sinais clínicos, dieta inadequada ou múltiplos fatores de risco."}


def calcular_apresentacao_ferro(dose_mg_dia: float, apresentacao: dict):
    if dose_mg_dia <= 0:
        return {"quantidade": 0, "texto": "Sem dose profilática calculada no momento."}
    qtd = dose_mg_dia / apresentacao["mg_por_unidade"]
    if apresentacao["tipo"] == "gotas":
        qtd_arred = max(1, int(round(qtd)))
        return {"quantidade": qtd_arred, "texto": f"{qtd_arred} gota(s) VO 1 vez ao dia"}
    qtd_arred = round(qtd, 2)
    return {"quantidade": qtd_arred, "texto": f"{qtd_arred} mL VO 1 vez ao dia"}


def modelo_prescricao_ferro(dose_mg_dia: float, sal_nome: str, apresentacao: dict, calculo: dict, duracao: str = "90 dias"):
    if dose_mg_dia <= 0:
        return "Sem prescrição de ferro profilático calculada para esta idade/risco no momento. Reavaliar conforme protocolo, dieta e exames."
    return (
        f"{sal_nome}\n"
        f"Concentração: {apresentacao['concentracao']}\n"
        f"Dose calculada: {dose_mg_dia:.1f} mg/dia de ferro elementar.\n"
        f"Prescrever: {calculo['texto']}, preferencialmente no mesmo horário, por {duracao}.\n"
        "Orientar administração conforme tolerância, evitar administrar junto de leite/cálcio quando possível, "
        "explicar escurecimento das fezes e reforçar retorno se vômitos persistentes, dor abdominal importante, reação alérgica ou erro de dose."
    )


def recomendacao_vitaminas(meses: float, fatores_d: List[str], fatores_b12: List[str]):
    return {
        "Vitamina D": {
            "status": "avaliar risco" if fatores_d else "rotina conforme protocolo local",
            "orientacao": "Considerar suplementação profilática no lactente e maior atenção se houver prematuridade, pouca exposição solar, má absorção, doença crônica ou uso de medicamentos que interfiram no metabolismo da vitamina D.",
            "fatores": fatores_d,
        },
        "Vitamina A": {
            "status": "verificar programa local",
            "orientacao": "Verificar se o município participa de estratégia de suplementação de vitamina A e registrar doses quando aplicável. Reforçar alimentos fontes de carotenoides e vitamina A.",
            "fatores": [],
        },
        "Vitamina B12": {
            "status": "risco aumentado" if fatores_b12 else "sem fator informado",
            "orientacao": "Se houver risco materno ou dieta restritiva, considerar avaliação clínica/laboratorial e suplementação conforme prescrição. Deficiência pode cursar com anemia e atraso do desenvolvimento.",
            "fatores": fatores_b12,
        },
    }


def obter_orientacoes_detalhadas(meses: float, prematuro: bool = False):
    blocos = []
    if prematuro:
        blocos.append({"titulo": "Pré-termo: acompanhamento diferenciado", "icone": "👶", "itens": ["Usar idade corrigida para crescimento/desenvolvimento nos primeiros 2 anos, quando aplicável.", "Avaliar alimentação, ganho ponderal, anemia, saúde óssea, visão, audição e seguimento especializado conforme risco neonatal.", "Reforçar sinais de alerta e retorno precoce."], "conduta": "Manter área reservada para curvas específicas de prematuros quando os CSVs forem adicionados ao projeto."})
    if meses < 6:
        blocos += [
            {"titulo": "Alimentação", "icone": "🤱", "itens": ["Aleitamento materno exclusivo sob livre demanda até 6 meses, sem água, chás ou outros alimentos.", "Observar pega, sucção, diurese, evacuações, ganho ponderal e sinais de saciedade.", "Se não amamentado, registrar fórmula, volume, preparo e técnica de oferta."], "conduta": "Orientar rede de apoio, manejo de fissuras/dor e retorno se perda ponderal, sonolência ou baixa diurese."},
            {"titulo": "Sono seguro", "icone": "🌙", "itens": ["Dormir de barriga para cima, em superfície firme, sem travesseiros, protetores, cobertas soltas ou brinquedos.", "Evitar tabagismo passivo e superaquecimento.", "Construir rotina simples e previsível, sem telas."], "conduta": "Reforçar em toda consulta do lactente pequeno."},
            {"titulo": "Segurança e sinais de perigo", "icone": "🛡️", "itens": ["Bebê conforto no banco traseiro, voltado para trás.", "Nunca deixar sozinho em cama, sofá, trocador ou banho.", "Retornar imediatamente se febre em menor de 3 meses, recusa alimentar, gemência, cianose, convulsão ou prostração."], "conduta": "Registrar orientação dada ao cuidador."},
            {"titulo": "Estímulo e vínculo", "icone": "🧠", "itens": ["Conversar, cantar, olhar nos olhos e responder aos sons do bebê.", "Tummy time acordado e supervisionado, progressivo.", "Mostrar objetos coloridos a cerca de 30 cm e estimular seguimento visual."], "conduta": "Estimular sem forçar; observar simetria, tônus e interação."},
        ]
    elif meses < 12:
        blocos += [
            {"titulo": "Alimentação complementar", "icone": "🥣", "itens": ["A partir de 6 meses, manter leite materno e iniciar alimentos in natura/minimamente processados.", "Oferecer comida amassada no garfo, evoluindo textura; evitar liquidificar/peneirar como rotina.", "Incluir fontes de ferro: carnes, ovos, feijões e vísceras quando aceitas; associar frutas ricas em vitamina C.", "Evitar açúcar, mel, ultraprocessados, sucos artificiais e alimentos com risco de engasgo."], "conduta": "Acompanhar aceitação, textura, autonomia e responsividade alimentar."},
            {"titulo": "Saúde bucal", "icone": "🦷", "itens": ["Desde o primeiro dente, escovar com creme dental fluoretado.", "Quantidade semelhante a grão de arroz cru.", "Evitar mamadeira noturna açucarada e beliscos doces."], "conduta": "Registrar dentes, higiene e encaminhar odontologia conforme rede."},
            {"titulo": "Segurança domiciliar", "icone": "🏠", "itens": ["Proteger tomadas, quinas, escadas, janelas e móveis instáveis.", "Manter medicamentos, produtos de limpeza, objetos pequenos e pilhas fora do alcance.", "Supervisionar alimentação por risco de engasgo."], "conduta": "A criança passa a rolar, sentar, engatinhar e explorar o ambiente."},
            {"titulo": "Estímulo", "icone": "🎲", "itens": ["Brincar de esconder-achou, chamar pelo nome e estimular imitação.", "Oferecer brinquedos seguros para alcançar, transferir, bater e encaixar.", "Estimular sentar, engatinhar/arrastar e pinça, respeitando a etapa motora."], "conduta": "Ausência de marcos deve gerar orientação e reavaliação."},
        ]
    elif meses < 24:
        blocos += [
            {"titulo": "Alimentação da família", "icone": "🍽️", "itens": ["Manter comida da família, com pouca adição de sal e sem açúcar/ultraprocessados até 2 anos.", "Estimular água, frutas inteiras e refeições em família.", "Permitir que a criança tente comer sozinha, com supervisão."], "conduta": "Investigar seletividade, excesso de leite, constipação e deficiência de ferro."},
            {"titulo": "Linguagem, leitura e brincadeira", "icone": "📚", "itens": ["Ler livros, nomear objetos, cantar e conversar durante a rotina.", "Estimular apontar, pedir, imitar, empilhar, encaixar e brincar de faz de conta.", "Evitar telas antes de 2 anos."], "conduta": "Triar TEA entre 18 e 24 meses com instrumento adequado quando aplicável."},
            {"titulo": "Segurança", "icone": "🚗", "itens": ["Usar dispositivo de retenção adequado no carro.", "Prevenir quedas, queimaduras, intoxicações e afogamentos.", "Guardar baldes vazios, piscinas protegidas e produtos trancados."], "conduta": "Orientar conforme habilidade nova: andar, escalar e abrir gavetas."},
        ]
    else:
        blocos += [
            {"titulo": "Hábitos e crescimento saudável", "icone": "🌱", "itens": ["Manter refeições regulares, comida de verdade e baixa exposição a ultraprocessados.", "Estimular brincadeiras ativas e sono adequado.", "Avaliar IMC, pressão arterial quando indicado, saúde bucal, visão e audição."], "conduta": "Se sobrepeso/obesidade, avaliar história alimentar, rotina, sono, telas e exames conforme clínica."},
            {"titulo": "Desenvolvimento, escola e comportamento", "icone": "🏫", "itens": ["Investigar linguagem, coordenação, interação social, autonomia e desempenho escolar.", "Orientar leitura, brincadeiras simbólicas, regras simples e disciplina positiva.", "Limitar telas e evitar exposição a conteúdo inadequado."], "conduta": "Perda de habilidades ou atraso persistente exige avaliação especializada."},
            {"titulo": "Prevenção de acidentes", "icone": "⚠️", "itens": ["Reforçar segurança no trânsito, uso de capacete e supervisão em rua/piscina.", "Manter medicamentos, armas, objetos cortantes e produtos químicos inacessíveis.", "Orientar proteção contra violência e negligência."], "conduta": "Registrar orientação preventiva por faixa etária."},
        ]
    return blocos


def obter_marcos_vigilancia(meses: float, prematuro: bool = False):
    faixas = [
        {"faixa": "0 a 2 meses", "min": 0, "max": 2, "avaliacao": "Em decúbito dorsal e ventral, observar alerta, contato visual, resposta ao som e elevação breve da cabeça.", "marcos": [("Social", "Observa um rosto e acalma com voz familiar"), ("Audição", "Reage a sons"), ("Motor", "Eleva a cabeça brevemente em prono"), ("Comunicação", "Emite sons e inicia sorriso social")], "proxima": ["Aumentar tummy time supervisionado", "Conversar face a face", "Mostrar objetos contrastantes/coloridos", "Cantar e responder aos sons"]},
        {"faixa": "2 a 4 meses", "min": 2, "max": 4, "avaliacao": "Observar em colo e no colchonete: sustentação cefálica, sorriso responsivo, vocalização e mãos à linha média.", "marcos": [("Social", "Sorri em resposta e busca contato social"), ("Linguagem", "Vocaliza sons como aaa/ooo"), ("Motor", "Sustenta melhor a cabeça"), ("Motor fino", "Leva as mãos à boca e observa as mãos")], "proxima": ["Oferecer brinquedos leves para tocar", "Estimular rolar com brincadeiras laterais", "Conversar nomeando pessoas e objetos", "Manter tempo de barriga para baixo"]},
        {"faixa": "4 a 6 meses", "min": 4, "max": 6, "avaliacao": "Oferecer objeto colorido na linha média, avaliar alcance, riso, rolar e sentar com apoio.", "marcos": [("Motor fino", "Busca e alcança objetos"), ("Social", "Dá risada e interage"), ("Motor", "Rola ou inicia rolar"), ("Postura", "Senta com apoio")], "proxima": ["Brincar no chão com segurança", "Oferecer objetos para transferir", "Estimular sentar com apoio", "Preparar alimentação complementar aos 6 meses"]},
        {"faixa": "6 a 9 meses", "min": 6, "max": 9, "avaliacao": "Chamar lateralmente, oferecer dois objetos, observar sentar sem apoio e reação a brincadeiras sociais.", "marcos": [("Audição", "Localiza sons"), ("Linguagem", "Duplica sílabas"), ("Postura", "Senta sem apoio"), ("Motor fino", "Transfere objetos entre as mãos")], "proxima": ["Brincar de esconder-achou", "Estimular engatinhar/arrastar sem andador", "Oferecer alimentos com textura segura", "Nomear objetos e pessoas"]},
        {"faixa": "9 a 12 meses", "min": 9, "max": 12, "avaliacao": "Avaliar imitação, pinça com objeto pequeno seguro, ficar em pé com apoio e comunicação gestual.", "marcos": [("Social", "Brinca de esconde-achou"), ("Comunicação", "Imita gestos como tchau"), ("Motor", "Fica em pé com apoio"), ("Motor fino", "Faz pinça")], "proxima": ["Estimular apontar e pedir", "Ler livros de figuras", "Oferecer potes, blocos e encaixes grandes", "Permitir exploração segura"]},
        {"faixa": "12 a 18 meses", "min": 12, "max": 18, "avaliacao": "Observar marcha, palavras com significado, apontar, imitação funcional e compreensão de comandos simples.", "marcos": [("Motor", "Anda com ou sem apoio"), ("Linguagem", "Fala palavras com significado"), ("Social", "Imita atividades domésticas"), ("Cognição", "Aponta para mostrar interesse")], "proxima": ["Nomear partes do corpo", "Dar comandos simples", "Brincar de empilhar e encaixar", "Estimular colher/copo com supervisão"]},
        {"faixa": "18 a 24 meses", "min": 18, "max": 24, "avaliacao": "Observar corrida, rabiscos, faz de conta, apontar compartilhado e combinação de palavras.", "marcos": [("Linguagem", "Aumenta vocabulário e junta ideias simples"), ("Motor", "Corre com pouca queda"), ("Social", "Brinca de faz de conta simples"), ("Motor fino", "Rabisca espontaneamente")], "proxima": ["Ler diariamente", "Estimular frases curtas", "Brincar de faz de conta", "Oferecer massinha/lápis grosso com supervisão"]},
        {"faixa": "2 a 3 anos", "min": 24, "max": 36, "avaliacao": "Avaliar linguagem funcional, compreensão de ordens, coordenação, autonomia e brincadeira simbólica.", "marcos": [("Linguagem", "Forma frases e compreende ordens de 2 etapas"), ("Motor", "Sobe escadas com apoio"), ("Autonomia", "Ajuda a vestir e lavar mãos"), ("Social", "Brinca ao lado de outras crianças")], "proxima": ["Conversar sem telas", "Incentivar autonomia com limites", "Brincadeiras de encaixe, desenho e música", "Rotina de sono e desfralde sem punição"]},
        {"faixa": "3 a 5 anos", "min": 36, "max": 60, "avaliacao": "Pedir para contar algo, copiar formas simples, pular, correr, brincar com regras e interagir com pares.", "marcos": [("Linguagem", "Conta histórias simples e é compreendida"), ("Motor", "Pula, corre e pedala/triciclo"), ("Motor fino", "Copia formas simples"), ("Social", "Brinca com outras crianças e segue regras simples")], "proxima": ["Ler e pedir que reconte histórias", "Estimular desenho e recorte supervisionado", "Jogos com regras simples", "Brincadeiras ao ar livre"]},
        {"faixa": "5 a 10 anos", "min": 60, "max": 120, "avaliacao": "Avaliar aprendizagem, coordenação motora, autonomia, relação com pares, sono, telas e saúde mental.", "marcos": [("Escolar", "Acompanha aprendizagem esperada"), ("Motor", "Coordenação ampla progressiva"), ("Social", "Relaciona-se com pares"), ("Autonomia", "Cuidados pessoais crescentes")], "proxima": ["Estimular leitura", "Atividade física regular", "Rotina de sono", "Acompanhar escola, visão, audição e saúde mental"]},
    ]
    atual = next((f for f in faixas if f["min"] <= meses < f["max"]), faixas[-1])
    idx = faixas.index(atual)
    anterior = faixas[idx - 1] if idx > 0 else None
    proxima = faixas[idx + 1] if idx < len(faixas) - 1 else None
    return atual, anterior, proxima, faixas


def classificar_desenvolvimento(status_atual: List[str], status_anterior: List[str], fatores_risco: List[str] | None = None):
    fatores_risco = fatores_risco or []
    ausentes_atual = sum(1 for s in status_atual if s == "Ausente")
    ausentes_ant = sum(1 for s in status_anterior if s == "Ausente")
    if ausentes_ant > 0:
        return "Provável atraso / marco anterior ausente", "Ausência de marco da faixa anterior exige intervenção e reavaliação/encaminhamento conforme contexto.", "#dc2626"
    if ausentes_atual >= 2:
        return "Alerta para desenvolvimento", "Dois ou mais marcos da faixa atual ausentes: orientar estimulação, reavaliar em curto prazo e considerar encaminhamento.", "#f97316"
    if ausentes_atual == 1:
        return "Atenção / reavaliar", "Um marco da faixa atual ausente: orientar estimulação específica e reavaliar.", "#eab308"
    if fatores_risco:
        return "Adequado com fatores de risco", "Marcos presentes, mas há risco biológico/social; manter vigilância e estimulação ativa.", "#0ea5e9"
    return "Desenvolvimento adequado para a faixa", "Marcos esperados presentes. Orientar estimulação dos próximos marcos.", "#16a34a"


def obter_calendario_vacinal():
    return [
        {"idade": "Ao nascer", "meses_ref": 0, "cor": "#818cf8", "vacinas": [{"nome": "BCG", "dose": "Dose única", "doencas": "Formas graves de tuberculose", "intervalo": "Dose única", "idade_max": 59}, {"nome": "Hepatite B", "dose": "Dose ao nascer", "doencas": "Hepatite B", "intervalo": "Preferencialmente até 30 dias", "idade_max": 999}]},
        {"idade": "2 meses", "meses_ref": 2, "cor": "#fb923c", "vacinas": [{"nome": "Penta", "dose": "1ª dose", "doencas": "Difteria, tétano, coqueluche, Hib, hepatite B", "intervalo": "60 dias; mínimo 30 dias"}, {"nome": "VIP", "dose": "1ª dose", "doencas": "Poliomielite", "intervalo": "60 dias; mínimo 30 dias"}, {"nome": "Pneumocócica 10V", "dose": "1ª dose", "doencas": "Pneumonias, meningites, otites", "intervalo": "60 dias; mínimo 30 dias"}, {"nome": "Rotavírus humano", "dose": "1ª dose", "doencas": "Diarreia por rotavírus", "intervalo": "Respeitar idade máxima"}]},
        {"idade": "3 meses", "meses_ref": 3, "cor": "#67e8f9", "vacinas": [{"nome": "Meningocócica C", "dose": "1ª dose", "doencas": "Doença meningocócica C", "intervalo": "60 dias; mínimo 30 dias"}]},
        {"idade": "4 meses", "meses_ref": 4, "cor": "#fb923c", "vacinas": [{"nome": "Penta", "dose": "2ª dose", "doencas": "Difteria, tétano, coqueluche, Hib, hepatite B", "intervalo": "60 dias; mínimo 30 dias"}, {"nome": "VIP", "dose": "2ª dose", "doencas": "Poliomielite", "intervalo": "60 dias; mínimo 30 dias"}, {"nome": "Pneumocócica 10V", "dose": "2ª dose", "doencas": "Pneumonias, meningites, otites", "intervalo": "60 dias; mínimo 30 dias"}, {"nome": "Rotavírus humano", "dose": "2ª dose", "doencas": "Diarreia por rotavírus", "intervalo": "Respeitar idade máxima"}]},
        {"idade": "5 meses", "meses_ref": 5, "cor": "#67e8f9", "vacinas": [{"nome": "Meningocócica C", "dose": "2ª dose", "doencas": "Doença meningocócica C", "intervalo": "60 dias; mínimo 30 dias"}]},
        {"idade": "6 meses", "meses_ref": 6, "cor": "#22d3ee", "vacinas": [{"nome": "Penta", "dose": "3ª dose", "doencas": "Difteria, tétano, coqueluche, Hib, hepatite B", "intervalo": "60 dias; mínimo 30 dias"}, {"nome": "VIP", "dose": "3ª dose", "doencas": "Poliomielite", "intervalo": "60 dias; mínimo 30 dias"}, {"nome": "Covid-19", "dose": "1ª dose", "doencas": "Covid-19", "intervalo": "Conforme produto"}, {"nome": "Influenza", "dose": "Anual", "doencas": "Influenza", "intervalo": "Anual"}]},
        {"idade": "9 meses", "meses_ref": 9, "cor": "#7dd3fc", "vacinas": [{"nome": "Febre amarela", "dose": "Dose", "doencas": "Febre amarela", "intervalo": "Reforço aos 4 anos"}]},
        {"idade": "12 meses", "meses_ref": 12, "cor": "#fca5a5", "vacinas": [{"nome": "Tríplice viral", "dose": "1ª dose", "doencas": "Sarampo, caxumba, rubéola", "intervalo": "Reforçar conforme calendário"}, {"nome": "Pneumocócica 10V", "dose": "Reforço", "doencas": "Pneumococo", "intervalo": "Após esquema básico"}, {"nome": "Meningocócica C", "dose": "Reforço", "doencas": "Meningite C", "intervalo": "Após esquema básico"}]},
        {"idade": "15 meses", "meses_ref": 15, "cor": "#d8b4fe", "vacinas": [{"nome": "DTP", "dose": "1º reforço", "doencas": "Difteria, tétano, coqueluche", "intervalo": "Reforço"}, {"nome": "VOP", "dose": "1º reforço", "doencas": "Poliomielite", "intervalo": "Reforço"}, {"nome": "Hepatite A", "dose": "Uma dose", "doencas": "Hepatite A", "intervalo": "Dose única"}, {"nome": "Tetraviral/Varicela", "dose": "Uma dose", "doencas": "Sarampo, caxumba, rubéola e varicela", "intervalo": "Conforme disponibilidade"}]},
        {"idade": "4 anos", "meses_ref": 48, "cor": "#c084fc", "vacinas": [{"nome": "DTP", "dose": "2º reforço", "doencas": "Difteria, tétano, coqueluche", "intervalo": "Reforço"}, {"nome": "VOP", "dose": "2º reforço", "doencas": "Poliomielite", "intervalo": "Reforço"}, {"nome": "Febre amarela", "dose": "Reforço", "doencas": "Febre amarela", "intervalo": "Reforço"}, {"nome": "Varicela", "dose": "Uma dose", "doencas": "Varicela", "intervalo": "Conforme calendário"}]},
        {"idade": "9 a 10 anos", "meses_ref": 108, "cor": "#f59e0b", "vacinas": [{"nome": "HPV", "dose": "Dose", "doencas": "HPV", "intervalo": "Conforme calendário vigente"}, {"nome": "Pneumocócica 23V", "dose": "Indígenas", "doencas": "Pneumococo", "intervalo": "Grupo específico"}]},
    ]


def status_vacina(meses: float, meses_ref: float, registrada: bool):
    if registrada:
        return "Registrada", "#16a34a"
    atraso = meses - meses_ref
    if atraso >= 1:
        return "Atrasada/pendente", "#dc2626"
    if -0.25 <= atraso < 1:
        return "Indicada agora", "#f97316"
    if -2 <= atraso < -0.25:
        return f"Próxima em ~{abs(atraso):.1f} mês(es)", "#0ea5e9"
    return "Programada", "#64748b"


def eventos_adversos_vacinas():
    comum_local = "Dor, edema, vermelhidão ou endurecimento local nas primeiras 24–72h."
    alerta_geral = "Procurar serviço se febre persistente/alta, prostração importante, choro inconsolável, convulsão, sinais de alergia, dificuldade respiratória, púrpura, alteração neurológica ou evento que preocupe a família."
    return {
        "BCG": {"esperado": "Lesão local progressiva com pápula/nódulo, possível pequena úlcera e cicatriz ao longo das semanas.", "alerta": "Abscesso extenso, linfonodo supurado, lesões disseminadas ou ausência de cicatrização com piora importante."},
        "Hepatite B": {"esperado": comum_local + " Pode ocorrer febre baixa e mal-estar.", "alerta": alerta_geral},
        "Penta": {"esperado": comum_local + " Febre, irritabilidade, sonolência e inapetência podem ocorrer nas primeiras 24–72h.", "alerta": "Episódio hipotônico-hiporresponsivo, convulsão, choro persistente por horas, febre alta ou reação alérgica."},
        "DTP": {"esperado": comum_local + " Febre e irritabilidade são relativamente esperadas.", "alerta": "Choro persistente, EHH, convulsão, febre alta ou reação de hipersensibilidade."},
        "VIP": {"esperado": comum_local + " Eventos sistêmicos são incomuns.", "alerta": alerta_geral},
        "VOP": {"esperado": "Geralmente bem tolerada.", "alerta": "Déficit motor flácido ou sinais neurológicos após vacinação exigem avaliação imediata."},
        "Pneumocócica 10V": {"esperado": comum_local + " Febre, irritabilidade, sonolência ou redução do apetite podem ocorrer.", "alerta": alerta_geral},
        "Pneumocócica 23V": {"esperado": comum_local + " Febre baixa e mialgia podem ocorrer.", "alerta": alerta_geral},
        "Meningocócica C": {"esperado": comum_local + " Febre, sonolência e irritabilidade podem ocorrer.", "alerta": alerta_geral},
        "Rotavírus humano": {"esperado": "Irritabilidade, febre baixa, vômitos ou diarreia leve podem ocorrer nos dias seguintes.", "alerta": "Dor abdominal intensa, vômitos persistentes, sangue nas fezes, distensão abdominal ou choro em crises — avaliar invaginação intestinal."},
        "Febre amarela": {"esperado": "Dor local, febre, cefaleia e mialgia geralmente entre 2 e 10 dias.", "alerta": "Icterícia, sangramentos, alteração neurológica, rigidez de nuca, dispneia ou piora sistêmica intensa."},
        "Tríplice viral": {"esperado": "Febre e exantema podem ocorrer entre 5 e 12 dias; parotidite/artralgia são possíveis.", "alerta": "Febre alta persistente, sinais neurológicos, púrpura, reação alérgica ou prostração importante."},
        "Tetraviral/Varicela": {"esperado": "Febre e exantema leve podem ocorrer dias após; lesões tipo varicela podem ser discretas.", "alerta": "Exantema intenso/disseminado, sinais neurológicos, infecção secundária importante ou reação alérgica."},
        "Varicela": {"esperado": "Dor local e poucas lesões vesiculares podem ocorrer.", "alerta": "Lesões disseminadas, imunossupressão não reconhecida ou sinais sistêmicos importantes."},
        "Hepatite A": {"esperado": comum_local + " Febre baixa, cefaleia, mal-estar e sintomas gastrointestinais leves podem ocorrer.", "alerta": alerta_geral},
        "HPV": {"esperado": comum_local + " Pode ocorrer tontura/síncope relacionada à aplicação; observar por alguns minutos.", "alerta": "Síncope com trauma, reação alérgica, sintomas neurológicos ou evento persistente."},
        "Covid-19": {"esperado": comum_local + " Febre, fadiga, cefaleia, mialgia ou irritabilidade podem ocorrer.", "alerta": "Dor torácica, dispneia, palpitações, reação alérgica, febre persistente ou prostração importante."},
        "Influenza": {"esperado": comum_local + " Febre baixa, mialgia e mal-estar por 1–2 dias.", "alerta": "Reação alérgica, sintomas neurológicos ou febre persistente."},
    }


def obter_matriz_caderneta_vacinas():
    return [
        {"grupo": "Até 12 meses", "linhas": [
            [("BCG", "Dose única", "#818cf8"), ("Hepatite B", "Dose ao nascer", "#fdba74"), ("Penta", "1ª Dose", "#fed7aa"), ("Penta", "2ª Dose", "#fed7aa"), ("Penta", "3ª Dose", "#fed7aa"), ("Rotavírus humano", "1ª Dose", "#f0abfc"), ("Rotavírus humano", "2ª Dose", "#f0abfc")],
            [("Pneumocócica 10V", "1ª Dose", "#fef08a"), ("Pneumocócica 10V", "2ª Dose", "#fef08a"), ("VIP", "1ª Dose", "#22d3ee"), ("VIP", "2ª Dose", "#22d3ee"), ("VIP", "3ª Dose", "#22d3ee"), ("Meningocócica C", "1ª Dose", "#bae6fd"), ("Meningocócica C", "2ª Dose", "#bae6fd")],
            [("Febre amarela", "Dose", "#67e8f9"), ("Tríplice viral", "1ª Dose", "#fca5a5"), ("Covid-19", "1ª Dose", "#db2777"), ("Covid-19", "2ª Dose", "#db2777"), ("Covid-19", "3ª Dose", "#db2777"), ("Influenza", "Anual", "#86efac"), ("", "", "#f8fafc")],
        ]},
        {"grupo": "A partir de 12 meses", "linhas": [
            [("Pneumocócica 10V", "Reforço", "#fef08a"), ("Meningocócica C", "Reforço", "#bae6fd"), ("DTP", "1º Reforço", "#ffedd5"), ("DTP", "2º Reforço", "#ffedd5"), ("VOP", "1º Reforço", "#67e8f9"), ("VOP", "2º Reforço", "#67e8f9"), ("Tetraviral", "Uma dose", "#fecaca")],
            [("Varicela", "Uma dose", "#fee2e2"), ("Febre amarela", "Reforço", "#67e8f9"), ("Hepatite A", "Uma dose", "#d9f99d"), ("HPV", "Dose", "#c4b5fd"), ("HPV", "Dose", "#c4b5fd"), ("Pneumocócica 23V", "Indígenas", "#fdba74"), ("", "Mantenha a vacinação atualizada", "#fff7ed")],
        ]}
    ]


# ============================================================
# Atualizações: mapa vacinal clicável, vitamina A/D e imagens
# ============================================================

def obter_lista_imagens_app():
    """Arquivos de imagem opcionais que podem ser anexados ao repositório.
    O app funciona sem eles; quando presentes, são exibidos automaticamente.
    """
    return {
        "ferro": [
            "assets/ferro/sulfato_ferroso_gotas.png",
            "assets/ferro/noripurum_gotas_50mg.png",
            "assets/ferro/dexfer_gotas_100mg.png",
            "assets/ferro/noripurum_xarope_10mg.png",
            "assets/ferro/neutrofer_gotas.png",
            "assets/ferro/combiron_gotas.png",
        ],
        "desenvolvimento": [
            "assets/desenvolvimento/avaliacao_0_3_meses.png",
            "assets/desenvolvimento/avaliacao_4_6_meses.png",
            "assets/desenvolvimento/avaliacao_7_9_meses.png",
            "assets/desenvolvimento/avaliacao_10_12_meses.png",
            "assets/desenvolvimento/avaliacao_13_18_meses.png",
            "assets/desenvolvimento/avaliacao_19_24_meses.png",
            "assets/desenvolvimento/avaliacao_2_3_anos.png",
            "assets/desenvolvimento/avaliacao_3_5_anos.png",
            "assets/desenvolvimento/avaliacao_5_10_anos.png",
        ],
    }


def imagem_desenvolvimento_por_faixa(faixa: str):
    mapa = {
        "0 a 2 meses": "assets/desenvolvimento/avaliacao_0_3_meses.png",
        "2 a 4 meses": "assets/desenvolvimento/avaliacao_0_3_meses.png",
        "4 a 6 meses": "assets/desenvolvimento/avaliacao_4_6_meses.png",
        "6 a 9 meses": "assets/desenvolvimento/avaliacao_7_9_meses.png",
        "9 a 12 meses": "assets/desenvolvimento/avaliacao_10_12_meses.png",
        "12 a 18 meses": "assets/desenvolvimento/avaliacao_13_18_meses.png",
        "18 a 24 meses": "assets/desenvolvimento/avaliacao_19_24_meses.png",
        "2 a 3 anos": "assets/desenvolvimento/avaliacao_2_3_anos.png",
        "3 a 5 anos": "assets/desenvolvimento/avaliacao_3_5_anos.png",
        "5 a 10 anos": "assets/desenvolvimento/avaliacao_5_10_anos.png",
    }
    return mapa.get(faixa, "")


def obter_sais_ferro():
    # Sobrescreve a versão anterior para remover URLs externas e usar imagens locais opcionais.
    return {
        "Sulfato ferroso gotas 25 mg Fe/mL (≈ 1 mg/gota)": {
            "tipo": "gotas", "mg_por_unidade": 1.0, "unidade": "gota", "concentracao": "25 mg de ferro elementar/mL",
            "marcas": "Sulfato ferroso genérico, FURP, Lomfer, Fersil", "obs": "Opção clássica e econômica; pode causar desconforto gastrointestinal e escurecimento das fezes.",
            "imagem": "assets/ferro/sulfato_ferroso_gotas.png"
        },
        "Ferripolimaltose gotas 50 mg Fe/mL (≈ 2,5 mg/gota)": {
            "tipo": "gotas", "mg_por_unidade": 2.5, "unidade": "gota", "concentracao": "50 mg de ferro elementar/mL",
            "marcas": "Noripurum gotas, Ultrafer, ferripolimaltose genérica", "obs": "Mais concentrado; menor número de gotas. Conferir bula e equivalência de ferro elementar.",
            "imagem": "assets/ferro/noripurum_gotas_50mg.png"
        },
        "Ferripolimaltose gotas 100 mg Fe/mL (≈ 5 mg/gota)": {
            "tipo": "gotas", "mg_por_unidade": 5.0, "unidade": "gota", "concentracao": "100 mg de ferro elementar/mL",
            "marcas": "Dexfer e apresentações equivalentes", "obs": "Muito concentrado; atenção para evitar erro de dose.",
            "imagem": "assets/ferro/dexfer_gotas_100mg.png"
        },
        "Ferripolimaltose xarope 10 mg Fe/mL": {
            "tipo": "mL", "mg_por_unidade": 10.0, "unidade": "mL", "concentracao": "10 mg de ferro elementar/mL",
            "marcas": "Noripurum xarope e equivalentes", "obs": "Cálculo em mL; útil com seringa dosadora.",
            "imagem": "assets/ferro/noripurum_xarope_10mg.png"
        },
        "Ferro quelato glicinato gotas 50 mg Fe/mL (≈ 2,5 mg/gota)": {
            "tipo": "gotas", "mg_por_unidade": 2.5, "unidade": "gota", "concentracao": "50 mg de ferro elementar/mL",
            "marcas": "Neutrofer gotas e equivalentes", "obs": "Conferir se a bula informa sal total ou ferro elementar.",
            "imagem": "assets/ferro/neutrofer_gotas.png"
        },
        "Glicinato férrico associado a vitaminas (≈ 2,7 mg/gota)": {
            "tipo": "gotas", "mg_por_unidade": 2.7, "unidade": "gota", "concentracao": "aprox. 27,5 mg Fe/mL, conforme apresentação",
            "marcas": "Combiron gotas e similares", "obs": "Atenção aos componentes associados e à faixa etária indicada na bula.",
            "imagem": "assets/ferro/combiron_gotas.png"
        },
    }


def obter_mapa_vacinal_cards():
    """Mapa panorâmico tipo Caderneta: cada entrada vira card clicável/suspenso no app."""
    eapv = eventos_adversos_vacinas()
    def ev(nome):
        return eapv.get(nome, eapv.get(nome.split()[0], {"esperado": "Dor local, febre baixa ou sintomas leves podem ocorrer conforme vacina.", "alerta": "Procurar serviço se evento intenso, persistente ou sinais de alergia/gravidade."}))
    base = [
        ("bcg", "BCG", "Dose única", "Ao nascer", 0, "Até 12 meses", "#818cf8", "Formas graves de tuberculose", "Intradérmica", "0,05 mL em RN até 11m29d conforme produto; 0,1 mL a partir de 1 ano conforme produto.", "Ao nascer, preferencialmente na maternidade."),
        ("hepb_nasc", "Hepatite B", "Dose ao nascer", "Ao nascer", 0, "Até 12 meses", "#fdba74", "Hepatite B", "Intramuscular", "0,5 mL", "Ao nascer, idealmente nas primeiras 24 horas."),
        ("penta_1", "Penta", "1ª dose", "2 meses", 2, "Até 12 meses", "#fed7aa", "Difteria, tétano, coqueluche, Hib e hepatite B", "Intramuscular", "0,5 mL", "A partir de 2 meses."),
        ("penta_2", "Penta", "2ª dose", "4 meses", 4, "Até 12 meses", "#fed7aa", "Difteria, tétano, coqueluche, Hib e hepatite B", "Intramuscular", "0,5 mL", "A partir de 4 meses."),
        ("penta_3", "Penta", "3ª dose", "6 meses", 6, "Até 12 meses", "#fed7aa", "Difteria, tétano, coqueluche, Hib e hepatite B", "Intramuscular", "0,5 mL", "A partir de 6 meses."),
        ("rota_1", "Rotavírus humano", "1ª dose", "2 meses", 2, "Até 12 meses", "#f0abfc", "Diarreia por rotavírus", "Oral", "Conforme apresentação", "Observar idade mínima e máxima permitida pelo calendário técnico."),
        ("rota_2", "Rotavírus humano", "2ª dose", "4 meses", 4, "Até 12 meses", "#f0abfc", "Diarreia por rotavírus", "Oral", "Conforme apresentação", "Observar idade máxima para completar esquema."),
        ("pneumo10_1", "Pneumocócica 10V", "1ª dose", "2 meses", 2, "Até 12 meses", "#fef08a", "Pneumonias, meningites, otites e doença pneumocócica invasiva", "Intramuscular", "0,5 mL", "A partir de 2 meses."),
        ("pneumo10_2", "Pneumocócica 10V", "2ª dose", "4 meses", 4, "Até 12 meses", "#fef08a", "Pneumonias, meningites, otites e doença pneumocócica invasiva", "Intramuscular", "0,5 mL", "A partir de 4 meses."),
        ("vip_1", "VIP", "1ª dose", "2 meses", 2, "Até 12 meses", "#22d3ee", "Poliomielite", "Intramuscular", "0,5 mL", "A partir de 2 meses."),
        ("vip_2", "VIP", "2ª dose", "4 meses", 4, "Até 12 meses", "#22d3ee", "Poliomielite", "Intramuscular", "0,5 mL", "A partir de 4 meses."),
        ("vip_3", "VIP", "3ª dose", "6 meses", 6, "Até 12 meses", "#22d3ee", "Poliomielite", "Intramuscular", "0,5 mL", "A partir de 6 meses."),
        ("menc_1", "Meningocócica C", "1ª dose", "3 meses", 3, "Até 12 meses", "#bae6fd", "Doença meningocócica C", "Intramuscular", "0,5 mL", "A partir de 3 meses."),
        ("menc_2", "Meningocócica C", "2ª dose", "5 meses", 5, "Até 12 meses", "#bae6fd", "Doença meningocócica C", "Intramuscular", "0,5 mL", "A partir de 5 meses."),
        ("febre_amarela_1", "Febre amarela", "Dose", "9 meses", 9, "Até 12 meses", "#67e8f9", "Febre amarela", "Subcutânea", "0,5 mL", "A partir de 9 meses, conforme indicação territorial/calendário."),
        ("triplice_viral_1", "Tríplice viral", "1ª dose", "12 meses", 12, "Até 12 meses", "#fca5a5", "Sarampo, caxumba e rubéola", "Subcutânea", "0,5 mL", "Aos 12 meses."),
        ("covid_1", "Covid-19", "1ª dose", "6 meses", 6, "Até 12 meses", "#db2777", "Covid-19 e formas graves", "Intramuscular", "Conforme fabricante", "A partir de 6 meses, conforme calendário vigente/produto."),
        ("covid_2", "Covid-19", "2ª dose", "Conforme produto", 7, "Até 12 meses", "#db2777", "Covid-19 e formas graves", "Intramuscular", "Conforme fabricante", "Conforme produto e calendário vigente."),
        ("covid_3", "Covid-19", "3ª dose", "Conforme produto", 8, "Até 12 meses", "#db2777", "Covid-19 e formas graves", "Intramuscular", "Conforme fabricante", "Conforme produto e calendário vigente."),
        ("influenza", "Influenza", "Anual", "6 meses", 6, "Até 12 meses", "#86efac", "Influenza", "Intramuscular", "0,5 mL conforme produto", "A partir de 6 meses, dose anual conforme campanha/calendário."),
        ("pneumo10_ref", "Pneumocócica 10V", "Reforço", "12 meses", 12, "A partir de 12 meses", "#fef08a", "Doença pneumocócica", "Intramuscular", "0,5 mL", "Aos 12 meses."),
        ("menc_ref", "Meningocócica C", "Reforço", "12 meses", 12, "A partir de 12 meses", "#bae6fd", "Doença meningocócica C", "Intramuscular", "0,5 mL", "Aos 12 meses."),
        ("dtp_ref1", "DTP", "1º reforço", "15 meses", 15, "A partir de 12 meses", "#ffedd5", "Difteria, tétano e coqueluche", "Intramuscular", "0,5 mL", "Aos 15 meses."),
        ("dtp_ref2", "DTP", "2º reforço", "4 anos", 48, "A partir de 12 meses", "#ffedd5", "Difteria, tétano e coqueluche", "Intramuscular", "0,5 mL", "Aos 4 anos."),
        ("vop_ref1", "VOP", "1º reforço", "15 meses", 15, "A partir de 12 meses", "#67e8f9", "Poliomielite", "Oral", "Conforme apresentação", "Aos 15 meses, conforme calendário vigente."),
        ("vop_ref2", "VOP", "2º reforço", "4 anos", 48, "A partir de 12 meses", "#67e8f9", "Poliomielite", "Oral", "Conforme apresentação", "Aos 4 anos, conforme calendário vigente."),
        ("tetraviral", "Tetraviral", "Uma dose", "15 meses", 15, "A partir de 12 meses", "#fecaca", "Sarampo, caxumba, rubéola e varicela", "Subcutânea", "0,5 mL", "Aos 15 meses, após tríplice viral."),
        ("varicela", "Varicela", "Uma dose", "4 anos", 48, "A partir de 12 meses", "#fee2e2", "Varicela", "Subcutânea", "0,5 mL", "Aos 4 anos."),
        ("febre_amarela_ref", "Febre amarela", "Reforço", "4 anos", 48, "A partir de 12 meses", "#67e8f9", "Febre amarela", "Subcutânea", "0,5 mL", "Aos 4 anos, conforme calendário/indicação."),
        ("hepa", "Hepatite A", "Uma dose", "15 meses", 15, "A partir de 12 meses", "#d9f99d", "Hepatite A", "Intramuscular", "0,5 mL", "Aos 15 meses."),
        ("hpv_1", "HPV", "Dose", "9 a 14 anos", 108, "A partir de 12 meses", "#c4b5fd", "Infecções e cânceres associados ao HPV", "Intramuscular", "0,5 mL", "Conforme faixa etária e calendário vigente."),
        ("hpv_2", "HPV", "Dose", "Conforme PNI", 109, "A partir de 12 meses", "#c4b5fd", "Infecções e cânceres associados ao HPV", "Intramuscular", "0,5 mL", "Conforme esquema vigente."),
        ("pneumo23_indigena", "Pneumocócica 23V", "Povos indígenas", "5 anos", 60, "A partir de 12 meses", "#fdba74", "Doença pneumocócica por sorotipos incluídos na VPP23", "Intramuscular", "0,5 mL", "Indicada para povos indígenas conforme calendário."),
    ]
    out = []
    for vid, nome, dose, idade_label, idade_meses, grupo, cor, protecao, via, volume, janela in base:
        e = ev(nome if nome != "Tetraviral" else "Tetraviral/Varicela")
        out.append({
            "id": vid, "nome": nome, "dose": dose, "idade_label": idade_label, "idade_meses": idade_meses,
            "grupo": grupo, "cor": cor, "protecao": protecao, "via": via, "volume": volume, "janela": janela,
            "atraso": "Conferir caderneta e histórico, aplicar dose faltante quando elegível, sem reiniciar esquema; respeitar idade máxima, intervalo mínimo e contraindicações.",
            "esperado": e.get("esperado", ""), "alerta": e.get("alerta", ""),
        })
    return out


def calcular_vitamina_a_pnsva(idade_meses, regiao_prioritaria=False, cadastro_unico=False, dsei=False):
    if idade_meses < 6:
        return {"indicada": False, "dose": "Não indicada pela idade", "cor_capsula": "—", "frequencia": "—", "motivo": "Aguardar 6 meses.", "orientacao": "Não administrar megadose programática antes de 6 meses sem indicação específica.", "alerta": "Conferir idade antes de administrar."}
    if idade_meses > 59:
        return {"indicada": False, "dose": "Fora da faixa do PNSVA", "cor_capsula": "—", "frequencia": "—", "motivo": "PNSVA se aplica de 6 a 59 meses conforme critérios.", "orientacao": "Avaliar suspeita de deficiência individualmente.", "alerta": "Evitar megadose fora dos critérios sem avaliação."}
    motivos = []
    indicada = False
    if dsei:
        indicada = True; motivos.append("DSEI: oferta universal de 6 a 59 meses")
    if regiao_prioritaria and 6 <= idade_meses <= 23:
        indicada = True; motivos.append("Região prioritária: oferta universal de 6 a 23 meses")
    if regiao_prioritaria and 24 <= idade_meses <= 59 and cadastro_unico:
        indicada = True; motivos.append("Região prioritária + CadÚnico: 24 a 59 meses")
    if (not regiao_prioritaria) and cadastro_unico and 6 <= idade_meses <= 23:
        indicada = True; motivos.append("Sul/Sudeste: priorizar 6 a 23 meses no CadÚnico em municípios aderidos")
    if 6 <= idade_meses <= 11:
        dose, cor, freq = "100.000 UI", "cápsula amarela", "Uma dose"
    else:
        dose, cor, freq = "200.000 UI", "cápsula vermelha", "A cada 6 meses"
    return {
        "indicada": indicada, "dose": dose, "cor_capsula": cor, "frequencia": freq,
        "motivo": " | ".join(motivos) if motivos else "Critérios programáticos não preenchidos automaticamente.",
        "orientacao": "Administrar por via oral, abrindo a cápsula no momento do uso e garantindo ingestão do conteúdo. Registrar na Caderneta e no sistema local.",
        "alerta": "Não substituir 200.000 UI por duas cápsulas de 100.000 UI e não usar meia cápsula de 200.000 UI para simular 100.000 UI. Conferir dose, validade e rótulo.",
    }


def calcular_vitamina_d_sbp(idade_meses, peso_atual_kg, prematuro=False, peso_nascimento_g=None, fatores_risco=None):
    fatores_risco = fatores_risco or []
    if prematuro and peso_atual_kg < 1.5:
        return {"indicada": False, "dose": "Aguardar peso > 1.500 g", "orientacao": "Em prematuros, iniciar suplementação oral quando peso for maior que 1.500 g, salvo conduta neonatal específica.", "prescricao": "Ainda sem prescrição profilática automática pelo peso atual.", "risco": fatores_risco}
    if idade_meses < 12:
        dose_ui = 400
    elif idade_meses < 24:
        dose_ui = 600
    else:
        dose_ui = 600 if fatores_risco else 0
    if dose_ui == 0:
        return {"indicada": False, "dose": "Sem profilaxia universal automática após 24 meses", "orientacao": "Avaliar dieta, risco, exposição solar segura, doenças crônicas e necessidade de dosagem/tratamento.", "prescricao": "Sem prescrição automática.", "risco": fatores_risco}
    return {"indicada": True, "dose": f"{dose_ui} UI/dia", "orientacao": "Usar colecalciferol (vitamina D3). Ajustar número de gotas/mL conforme apresentação comercial. Evitar manipulações quando houver risco de erro.", "prescricao": f"Colecalciferol {dose_ui} UI por via oral, 1 vez ao dia.", "risco": fatores_risco}
