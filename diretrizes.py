# diretrizes.py
# Base técnico-didática para o app de puericultura.
# Observação: mantenha este arquivo junto do app.py no repositório Streamlit.

from __future__ import annotations


def obter_classificacao(z: float, parametro: str):
    if parametro == "PC":
        if z > 2:
            return "PC acima do esperado para idade", "> +2 escores-z", "#ef6c00"
        if z >= -2:
            return "PC adequado para idade", "entre -2 e +2 escores-z", "#2e7d32"
        return "PC abaixo do esperado para idade", "< -2 escores-z", "#c62828"

    if parametro == "Peso":
        if z > 2:
            return "Peso elevado para idade", "> +2 escores-z", "#ef6c00"
        if z >= -2:
            return "Peso adequado para idade", "entre -2 e +2 escores-z", "#2e7d32"
        if z >= -3:
            return "Baixo peso para idade", "entre -3 e -2 escores-z", "#f9a825"
        return "Muito baixo peso para idade", "< -3 escores-z", "#c62828"

    if parametro == "Estatura":
        if z >= -2:
            return "Estatura adequada para idade", ">= -2 escores-z", "#2e7d32"
        if z >= -3:
            return "Baixa estatura para idade", "entre -3 e -2 escores-z", "#ef6c00"
        return "Muito baixa estatura para idade", "< -3 escores-z", "#c62828"

    if parametro == "IMC":
        if z > 3:
            return "Obesidade", "> +3 escores-z", "#c62828"
        if z > 2:
            return "Sobrepeso", "> +2 e <= +3 escores-z", "#ef6c00"
        if z > 1:
            return "Risco de sobrepeso", "> +1 e <= +2 escores-z", "#f9a825"
        if z >= -2:
            return "Eutrofia", "entre -2 e +1 escores-z", "#2e7d32"
        if z >= -3:
            return "Magreza", "entre -3 e -2 escores-z", "#ef6c00"
        return "Magreza acentuada", "< -3 escores-z", "#c62828"

    return "Sem classificação", "Parâmetro não reconhecido", "#607d8b"


def obter_faixas_zscore(parametro: str):
    cores = {
        "vermelho": ("rgba(198,40,40,.15)", "#c62828"),
        "laranja": ("rgba(239,108,0,.15)", "#ef6c00"),
        "amarelo": ("rgba(249,168,37,.18)", "#f9a825"),
        "verde": ("rgba(46,125,50,.15)", "#2e7d32"),
        "azul": ("rgba(21,101,192,.12)", "#1565c0"),
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
    elif parametro == "Estatura":
        base = [
            (-4, -3, "Muito baixa estatura", "< -3Z", "vermelho"),
            (-3, -2, "Baixa estatura", "-3Z a -2Z", "laranja"),
            (-2, 4, "Estatura adequada", ">= -2Z", "verde"),
        ]
    elif parametro == "PC":
        base = [
            (-4, -2, "PC abaixo do esperado", "< -2Z", "vermelho"),
            (-2, 2, "PC adequado", "-2Z a +2Z", "verde"),
            (2, 4, "PC acima do esperado", "> +2Z", "laranja"),
        ]
    else:
        base = [
            (-4, -3, "Muito baixo peso", "< -3Z", "vermelho"),
            (-3, -2, "Baixo peso", "-3Z a -2Z", "laranja"),
            (-2, 2, "Peso adequado", "-2Z a +2Z", "verde"),
            (2, 4, "Peso elevado", "> +2Z", "laranja"),
        ]
    return [
        {"z_min": a, "z_max": b, "rotulo": r, "intervalo": i, "cor_fill": cores[c][0], "cor_texto": cores[c][1]}
        for a, b, r, i, c in base
    ]


def fatores_risco_anemia():
    return {
        "maternos": [
            "Dieta materna deficiente em ferro",
            "Não suplementação de ferro na gestação/lactação",
            "Perdas sanguíneas maternas ou anemia materna",
            "Gestações múltiplas ou pouco intervalo intergestacional",
        ],
        "criança": [
            "Prematuridade",
            "Baixo peso ao nascer (< 2.500 g)",
            "Clampeamento do cordão antes de 1 minuto",
            "Crescimento rápido / canal ascendente importante",
            "AME prolongado sem alimentação complementar rica em ferro após 6 meses",
            "Alimentação complementar pobre em ferro ou baixa biodisponibilidade",
            "Leite de vaca antes de 12 meses",
            "Dieta vegetariana/vegana sem orientação e suplementação",
            "Baixa adesão à suplementação profilática",
            "Sangramento digestivo, verminose, doença inflamatória intestinal ou perdas crônicas",
        ],
    }


def fatores_risco_hipovitaminose_d():
    return [
        "Baixa exposição solar ou criança permanece muito coberta/em ambiente fechado",
        "Pele escura associada a baixa exposição solar",
        "Uso crônico de anticonvulsivantes, glicocorticoides ou antirretrovirais",
        "Doença hepática, renal, má absorção ou colestase",
        "Obesidade",
        "Prematuridade",
        "Dieta restritiva ou baixa ingestão de fontes alimentares de vitamina D/cálcio",
    ]


def fatores_risco_vitamina_b12():
    return [
        "Mãe vegetariana estrita/vegana sem suplementação",
        "Criança vegetariana/vegana",
        "Baixa ingestão de alimentos de origem animal",
        "Doença gastrointestinal/má absorção ou cirurgia intestinal",
    ]


def obter_sais_ferro():
    return {
        "Sulfato ferroso gotas — 25 mg Fe/mL; 1 gota ≈ 1 mg": {
            "mg_gota": 1.0, "mg_ml": 25, "marcas": "FURP, Lomfer, Fersil, genéricos", "uso": "preferir longe das refeições; pode causar constipação, diarreia, escurecimento dental/fezes"},
        "Ferripolimaltose gotas — 50 mg Fe/mL; 1 gota ≈ 2,5 mg": {
            "mg_gota": 2.5, "mg_ml": 50, "marcas": "Noripurum, Ultrafer, genéricos", "uso": "pode ser administrada com refeições; menor número de gotas"},
        "Ferripolimaltose gotas — 100 mg Fe/mL; 1 gota ≈ 5 mg": {
            "mg_gota": 5.0, "mg_ml": 100, "marcas": "Dexfer e similares", "uso": "muito concentrado; conferir dose para evitar erro"},
        "Ferripolimaltose xarope — 10 mg Fe/mL": {
            "mg_gota": None, "mg_ml": 10, "marcas": "Noripurum xarope e similares", "uso": "cálculo por mL com seringa dosadora"},
        "Ferro quelato glicinato gotas — 50 mg Fe/mL; 1 gota ≈ 2,5 mg": {
            "mg_gota": 2.5, "mg_ml": 50, "marcas": "Neutrofer e similares", "uso": "conferir ferro elementar na bula"},
        "Glicinato férrico associado — 1 gota ≈ 2,7 mg": {
            "mg_gota": 2.7, "mg_ml": 27, "marcas": "Combiron gotas", "uso": "produto associado; conferir composição e adequação clínica"},
    }


def recomendacao_ferro(meses: float, peso: float, prematuro: bool, baixo_peso: bool, protocolo: str, recebe_formula_500ml: bool, riscos: list[str]):
    if recebe_formula_500ml:
        return {
            "status": "Avaliar necessidade individual",
            "dose_mg_dia": 0,
            "texto": "Criança recebe ≥500 mL/dia de fórmula infantil: a suplementação profilática pode não ser necessária, mas deve ser individualizada conforme risco, dieta e exames.",
            "ciclo": "Conferir ferro fornecido pela fórmula e alimentação complementar.",
            "alerta": "Não suspender suplementação em pré-termo/baixo peso sem avaliação clínica.",
        }

    if prematuro or baixo_peso:
        # Reserva técnica solicitada: pré-termo tem gráficos, orientações e suplementação diferentes.
        dose = round(peso * 2.0, 1)
        return {
            "status": "Pré-termo/baixo peso: protocolo especial",
            "dose_mg_dia": dose,
            "texto": "Para pré-termo ou baixo peso, manter área técnica reservada para ajustar por idade corrigida, peso ao nascer e evolução ponderal. Como ponto de partida conservador no app: 2 mg/kg/dia, com necessidade de individualização.",
            "ciclo": "Início geralmente mais precoce do que no termo; revisar peso atual, idade corrigida, fórmula/leite humano fortificado e exames.",
            "alerta": "Ajustar com o protocolo neonatal/local. O app deixa esta seção destacada para revisão médica antes de prescrever.",
        }

    if protocolo.startswith("Ministério"):
        if meses < 6:
            return {
                "status": "Ainda não iniciou pelo MS",
                "dose_mg_dia": 0,
                "texto": "RN a termo e com peso adequado: pelo esquema do Ministério da Saúde, iniciar ferro profilático aos 6 meses.",
                "ciclo": "Programar 1º ciclo dos 6 aos 9 meses.",
                "alerta": "Antecipar investigação se houver fatores de risco importantes ou sinais clínicos/laboratoriais.",
            }
        if 6 <= meses < 9:
            return {"status": "1º ciclo em curso", "dose_mg_dia": 12.5, "texto": "Ferro elementar 10 a 12,5 mg/dia independentemente do peso.", "ciclo": "1º ciclo: 6 a 9 meses.", "alerta": "Reforçar adesão, modo de uso e alimentação rica em ferro."}
        if 9 <= meses < 12:
            return {"status": "Pausa programada", "dose_mg_dia": 0, "texto": "Pausa entre ciclos, se a criança completou o primeiro ciclo adequadamente.", "ciclo": "Pausa: 9 a 12 meses.", "alerta": "Se não completou o ciclo ou há alto risco, reavaliar conduta."}
        if 12 <= meses < 15:
            return {"status": "2º ciclo em curso", "dose_mg_dia": 12.5, "texto": "Ferro elementar 10 a 12,5 mg/dia independentemente do peso.", "ciclo": "2º ciclo: 12 a 15 meses.", "alerta": "Conferir dieta, sinais de anemia e necessidade de hemograma/ferritina."}
        return {"status": "Ciclo MS concluído", "dose_mg_dia": 0, "texto": "Após 15 meses, manter orientação alimentar e rastrear anemia conforme risco/achados clínicos.", "ciclo": "Suplementação profilática de rotina pelo ciclo MS já concluída.", "alerta": "Fatores de risco ou sintomas indicam avaliação laboratorial."}

    # SBP / prevenção clássica
    if meses < 3:
        return {"status": "Programar início", "dose_mg_dia": 0, "texto": "Pelo protocolo SBP, RN a termo costuma iniciar 1 mg/kg/dia a partir dos 3 meses.", "ciclo": "Programar de 3 meses até 24 meses.", "alerta": "Riscos importantes podem exigir avaliação individual."}
    if meses <= 24:
        dose = round(peso * 1.0, 1)
        if riscos:
            dose = round(max(dose, peso * 1.0), 1)
        return {"status": "Profilaxia indicada", "dose_mg_dia": dose, "texto": "Ferro elementar 1 mg/kg/dia para criança a termo, com ajuste conforme risco, dieta e exames.", "ciclo": "Manter até 24 meses, se indicado.", "alerta": "Não confundir profilaxia com tratamento: anemia ferropriva confirmada usa doses terapêuticas."}
    return {"status": "Avaliar risco", "dose_mg_dia": 0, "texto": "Após 24 meses, suplementação não é automática: avaliar dieta, risco e exames.", "ciclo": "Sem ciclo profilático automático.", "alerta": "Se anemia confirmada, usar esquema terapêutico e investigação etiológica."}


def calcular_apresentacao_ferro(dose_mg_dia: float, sal: dict):
    if dose_mg_dia <= 0:
        return "Sem cálculo de dose diária neste momento."
    if sal.get("mg_gota"):
        gotas = max(1, round(dose_mg_dia / sal["mg_gota"]))
        return f"≈ {gotas} gota(s)/dia para atingir cerca de {dose_mg_dia:g} mg/dia de ferro elementar."
    ml = round(dose_mg_dia / sal["mg_ml"], 2)
    return f"≈ {ml} mL/dia para atingir cerca de {dose_mg_dia:g} mg/dia de ferro elementar."


def recomendacao_vitaminas(meses: float, prematuro: bool, riscos_d: list[str], riscos_b12: list[str], area_vit_a: bool):
    vit_d = "400 UI/dia até completar 12 meses; 600 UI/dia de 12 a 24 meses."
    if meses >= 24 and riscos_d:
        vit_d = "Após 2 anos, manter/avaliar vitamina D conforme risco clínico, exposição solar, dieta e exames."
    elif meses >= 24:
        vit_d = "Após 2 anos, não é rotina universal; avaliar conforme risco clínico, dieta, exposição solar e exames."
    if prematuro:
        vit_d += " Pré-termo: ajustar no seguimento neonatal/pediátrico conforme idade corrigida, peso e comorbidades."

    vit_a = "Vitamina A: indicar conforme programa do MS em áreas/grupos com recomendação."
    if area_vit_a:
        if 6 <= meses < 12:
            vit_a = "Vitamina A: 100.000 UI para 6 a 11 meses, conforme programa local/MS."
        elif 12 <= meses < 60:
            vit_a = "Vitamina A: 200.000 UI para 12 a 59 meses, conforme programa local/MS, em intervalos programáticos."
        else:
            vit_a = "Vitamina A: fora da faixa programática principal; conferir indicação local."

    b12 = "Vitamina B12: não é suplementação universal; investigar dieta materna/infantil."
    if riscos_b12:
        b12 = "Vitamina B12: risco presente. Considerar suplementação da mãe lactante e/ou da criança e avaliação laboratorial conforme dieta e contexto clínico."

    return {"Vitamina D": vit_d, "Vitamina A": vit_a, "Vitamina B12": b12}


def obter_orientacoes_detalhadas(meses: float, prematuro: bool = False, riscos: dict | None = None):
    riscos = riscos or {}
    blocos = []
    if prematuro:
        blocos.append({
            "titulo": "Pré-termo: usar idade corrigida e seguimento diferenciado",
            "icone": "🟣",
            "itens": [
                "Para desenvolvimento e crescimento inicial, interpretar pela idade corrigida até o limite recomendado pelo serviço.",
                "Revisar peso ao nascer, idade gestacional, internação neonatal, anemia da prematuridade, suplementação e fortificação do leite.",
                "Manter vigilância mais estreita para alimentação, neurodesenvolvimento, visão, audição e intercorrências respiratórias.",
            ],
            "conduta": "Esta seção do app fica reservada para protocolo específico de prematuridade e curvas próprias.",
        })

    if meses < 6:
        blocos += [
            {"titulo": "Aleitamento e nutrição", "icone": "🤱", "itens": ["Aleitamento materno exclusivo sob livre demanda até 6 meses, sem água, chás ou outros alimentos.", "Observar pega, sucção, diurese, evacuações, ganho ponderal e sinais de saciedade.", "Se não amamentado, registrar fórmula, volume, preparo e técnica de oferta."], "conduta": "Orientar rede de apoio, manejo de fissuras/dor e retorno se perda ponderal, sonolência ou baixa diurese."},
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
        {"faixa": "0 a 2 meses", "min": 0, "max": 2, "marcos": [
            ("Social", "Observa um rosto e acalma com voz familiar"), ("Audição", "Reage a sons"), ("Motor", "Eleva a cabeça brevemente em prono"), ("Comunicação", "Emite sons e inicia sorriso social")],
         "proxima": ["Aumentar tummy time supervisionado", "Conversar face a face", "Mostrar objetos contrastantes/coloridos", "Cantar e responder aos sons"]},
        {"faixa": "2 a 4 meses", "min": 2, "max": 4, "marcos": [
            ("Social", "Sorri em resposta e busca contato social"), ("Linguagem", "Vocaliza sons como aaa/ooo"), ("Motor", "Sustenta melhor a cabeça"), ("Motor fino", "Leva as mãos à boca e observa as mãos")],
         "proxima": ["Oferecer brinquedos leves para tocar", "Estimular rolar com brincadeiras laterais", "Conversar nomeando pessoas e objetos", "Manter tempo de barriga para baixo"]},
        {"faixa": "4 a 6 meses", "min": 4, "max": 6, "marcos": [
            ("Motor fino", "Busca e alcança objetos"), ("Social", "Dá risada e interage"), ("Motor", "Rola ou inicia rolar"), ("Postura", "Senta com apoio")],
         "proxima": ["Brincar no chão com segurança", "Oferecer objetos para transferir de uma mão à outra", "Estimular sentar com apoio", "Preparar família para alimentação complementar aos 6 meses"]},
        {"faixa": "6 a 9 meses", "min": 6, "max": 9, "marcos": [
            ("Audição", "Localiza sons"), ("Linguagem", "Duplica sílabas"), ("Postura", "Senta sem apoio"), ("Motor fino", "Transfere objetos entre as mãos")],
         "proxima": ["Brincar de esconder-achou", "Estimular engatinhar/arrastar sem andador", "Oferecer alimentos com textura segura", "Nomear objetos e pessoas"]},
        {"faixa": "9 a 12 meses", "min": 9, "max": 12, "marcos": [
            ("Social", "Brinca de esconde-achou"), ("Comunicação", "Imita gestos como tchau"), ("Motor", "Fica em pé com apoio"), ("Motor fino", "Faz pinça")],
         "proxima": ["Estimular apontar e pedir", "Ler livros de figuras", "Oferecer potes, blocos e encaixes grandes", "Permitir exploração segura do ambiente"]},
        {"faixa": "12 a 18 meses", "min": 12, "max": 18, "marcos": [
            ("Motor", "Anda com ou sem apoio"), ("Linguagem", "Fala palavras com significado"), ("Social", "Imita atividades domésticas"), ("Cognição", "Aponta para mostrar interesse")],
         "proxima": ["Nomear partes do corpo", "Dar comandos simples", "Brincar de empilhar e encaixar", "Estimular colher/copo com supervisão"]},
        {"faixa": "18 a 24 meses", "min": 18, "max": 24, "marcos": [
            ("Linguagem", "Aumenta vocabulário e junta ideias simples"), ("Motor", "Corre com pouca queda"), ("Social", "Brinca de faz de conta simples"), ("Motor fino", "Rabisca espontaneamente")],
         "proxima": ["Ler diariamente", "Estimular frases curtas", "Brincar de faz de conta", "Oferecer massinha/lápis grosso com supervisão"]},
        {"faixa": "2 a 3 anos", "min": 24, "max": 36, "marcos": [
            ("Linguagem", "Forma frases e compreende ordens de 2 etapas"), ("Motor", "Sobe escadas com apoio"), ("Autonomia", "Ajuda a vestir e lavar mãos"), ("Social", "Brinca ao lado de outras crianças")],
         "proxima": ["Conversar sem telas", "Incentivar autonomia com limites", "Brincadeiras de encaixe, desenho e música", "Rotina de sono e desfralde sem punição"]},
        {"faixa": "3 a 5 anos", "min": 36, "max": 60, "marcos": [
            ("Linguagem", "Conta histórias simples e é compreendida"), ("Motor", "Pula, corre e pedala/triciclo"), ("Motor fino", "Copia formas simples"), ("Social", "Brinca com outras crianças e segue regras simples")],
         "proxima": ["Ler e pedir que reconte histórias", "Estimular desenho e recorte supervisionado", "Jogos com regras simples", "Brincadeiras ao ar livre"]},
        {"faixa": "5 a 10 anos", "min": 60, "max": 120, "marcos": [
            ("Escolar", "Acompanha aprendizagem esperada"), ("Motor", "Coordenação ampla progressiva"), ("Social", "Relaciona-se com pares"), ("Autonomia", "Cuidados pessoais crescentes")],
         "proxima": ["Estimular leitura", "Atividade física regular", "Rotina de sono", "Acompanhar escola, visão, audição e saúde mental"]},
    ]
    atual = next((f for f in faixas if f["min"] <= meses < f["max"]), faixas[-1])
    anterior = None
    for i, f in enumerate(faixas):
        if f == atual and i > 0:
            anterior = faixas[i - 1]
            break
    return atual, anterior, faixas


def classificar_desenvolvimento(status_marcos: dict, tem_risco: bool, pc_alterado: bool, fenotipicas_3_ou_mais: bool, ausentes_faixa_anterior: int):
    ausentes_atual = sum(1 for v in status_marcos.values() if v == "Ausente")
    if pc_alterado or fenotipicas_3_ou_mais or ausentes_faixa_anterior >= 2:
        return "Provável atraso no desenvolvimento", "Encaminhar para avaliação neuropsicomotora/serviço especializado e manter estimulação familiar orientada.", "#c62828"
    if ausentes_atual >= 1:
        return "Alerta para o desenvolvimento", "Orientar estimulação da criança e marcar retorno em 30 dias para reavaliação.", "#ef6c00"
    if tem_risco:
        return "Desenvolvimento adequado com fatores de risco", "Elogiar, orientar estimulação e informar sinais de alerta; manter vigilância mais estreita.", "#f9a825"
    return "Desenvolvimento adequado", "Elogiar cuidador, orientar continuidade dos estímulos e retorno de rotina.", "#2e7d32"


def obter_calendario_vacinal():
    return [
        {"idade": "Ao nascer", "mes": 0, "cor": "#6a1b9a", "vacinas": [
            {"nome": "BCG", "dose": "Dose única", "protege": "Formas graves de tuberculose", "idade_limite": 59, "intervalo": "—", "atraso": "Aplicar se não houver registro/cicatriz conforme avaliação; indicada até 4 anos, 11 meses e 29 dias."},
            {"nome": "Hepatite B", "dose": "Dose ao nascer", "protege": "Hepatite B", "idade_limite": 0.99, "intervalo": "Preferencialmente nas primeiras 24–30 horas", "atraso": "Se não aplicada ao nascer, completar proteção com esquema contendo hepatite B conforme idade e histórico."},
        ]},
        {"idade": "2 meses", "mes": 2, "cor": "#1565c0", "vacinas": [
            {"nome": "Penta", "dose": "1ª dose", "protege": "Difteria, tétano, coqueluche, Hib e hepatite B", "idade_limite": 83, "intervalo": "60 dias; mínimo 30 dias", "atraso": "Não reiniciar esquema. Aplicar dose faltante e respeitar intervalo mínimo."},
            {"nome": "VIP", "dose": "1ª dose", "protege": "Poliomielite", "idade_limite": 59, "intervalo": "60 dias; mínimo 30 dias", "atraso": "Aplicar dose faltante e completar esquema."},
            {"nome": "Pneumocócica 10V", "dose": "1ª dose", "protege": "Doença pneumocócica", "idade_limite": 59, "intervalo": "60 dias; mínimo 30 dias", "atraso": "Adequar número de doses conforme idade de início."},
            {"nome": "Rotavírus", "dose": "1ª dose", "protege": "Diarreia por rotavírus", "idade_limite": 7.5, "intervalo": "Mínimo 30 dias", "atraso": "Atenção aos limites máximos de idade para iniciar/completar."},
        ]},
        {"idade": "3 meses", "mes": 3, "cor": "#2e7d32", "vacinas": [
            {"nome": "Meningocócica C", "dose": "1ª dose", "protege": "Doença meningocócica C", "idade_limite": 59, "intervalo": "60 dias; mínimo 30 dias", "atraso": "Aplicar dose faltante e reforço conforme idade."},
        ]},
        {"idade": "4 meses", "mes": 4, "cor": "#0277bd", "vacinas": [
            {"nome": "Penta", "dose": "2ª dose", "protege": "Difteria, tétano, coqueluche, Hib e hepatite B", "idade_limite": 83, "intervalo": "60 dias; mínimo 30 dias", "atraso": "Não reiniciar; continuar a partir da dose válida."},
            {"nome": "VIP", "dose": "2ª dose", "protege": "Poliomielite", "idade_limite": 59, "intervalo": "60 dias; mínimo 30 dias", "atraso": "Completar esquema conforme doses prévias."},
            {"nome": "Pneumocócica 10V", "dose": "2ª dose", "protege": "Doença pneumocócica", "idade_limite": 59, "intervalo": "60 dias; mínimo 30 dias", "atraso": "Adequar pelo histórico."},
            {"nome": "Rotavírus", "dose": "2ª dose", "protege": "Diarreia por rotavírus", "idade_limite": 7.5, "intervalo": "Mínimo 30 dias", "atraso": "Conferir limite máximo para segunda dose."},
        ]},
        {"idade": "5 meses", "mes": 5, "cor": "#00897b", "vacinas": [
            {"nome": "Meningocócica C", "dose": "2ª dose", "protege": "Doença meningocócica C", "idade_limite": 59, "intervalo": "60 dias; mínimo 30 dias", "atraso": "Completar esquema e programar reforço."},
        ]},
        {"idade": "6 meses", "mes": 6, "cor": "#c2185b", "vacinas": [
            {"nome": "Penta", "dose": "3ª dose", "protege": "Difteria, tétano, coqueluche, Hib e hepatite B", "idade_limite": 83, "intervalo": "60 dias; mínimo 30 dias", "atraso": "Completar esquema básico sem reiniciar."},
            {"nome": "VIP", "dose": "3ª dose", "protege": "Poliomielite", "idade_limite": 59, "intervalo": "60 dias; mínimo 30 dias", "atraso": "Completar esquema básico."},
            {"nome": "Covid-19", "dose": "1ª dose", "protege": "Covid-19", "idade_limite": 120, "intervalo": "Conforme produto disponível", "atraso": "Atualizar conforme norma vigente/produto."},
            {"nome": "Influenza", "dose": "Dose anual", "protege": "Influenza e complicações", "idade_limite": 120, "intervalo": "Anual", "atraso": "Aplicar na campanha vigente se elegível."},
        ]},
        {"idade": "9 meses", "mes": 9, "cor": "#ef6c00", "vacinas": [
            {"nome": "Febre amarela", "dose": "1 dose", "protege": "Febre amarela", "idade_limite": 120, "intervalo": "Conforme área/recomendação", "atraso": "Aplicar se área com recomendação e sem contraindicação."},
        ]},
        {"idade": "12 meses", "mes": 12, "cor": "#7b1fa2", "vacinas": [
            {"nome": "Tríplice viral", "dose": "1ª dose", "protege": "Sarampo, caxumba e rubéola", "idade_limite": 120, "intervalo": "Mínimo 30 dias para doses subsequentes", "atraso": "Aplicar e programar segunda dose conforme calendário."},
            {"nome": "Pneumocócica 10V", "dose": "Reforço", "protege": "Doença pneumocócica", "idade_limite": 59, "intervalo": "Após esquema básico", "atraso": "Aplicar reforço conforme histórico e idade."},
            {"nome": "Meningocócica C", "dose": "Reforço", "protege": "Doença meningocócica C", "idade_limite": 59, "intervalo": "Após esquema básico", "atraso": "Aplicar reforço conforme histórico."},
        ]},
        {"idade": "15 meses", "mes": 15, "cor": "#5d4037", "vacinas": [
            {"nome": "DTP", "dose": "1º reforço", "protege": "Difteria, tétano e coqueluche", "idade_limite": 83, "intervalo": "Após esquema básico", "atraso": "Aplicar reforço pendente; nunca reiniciar esquema."},
            {"nome": "VOP", "dose": "Reforço", "protege": "Poliomielite", "idade_limite": 59, "intervalo": "Após VIP", "atraso": "Atualizar conforme normas vigentes do PNI."},
            {"nome": "Hepatite A", "dose": "Dose única", "protege": "Hepatite A", "idade_limite": 59, "intervalo": "—", "atraso": "Aplicar se não recebeu e estiver na faixa etária indicada."},
            {"nome": "Tetra viral/Varicela", "dose": "Dose conforme disponibilidade", "protege": "Sarampo, caxumba, rubéola e varicela", "idade_limite": 120, "intervalo": "Atenção a vacinas virais vivas", "atraso": "Se não simultânea com FA/SCR/varicela, respeitar intervalos técnicos."},
        ]},
        {"idade": "4 anos", "mes": 48, "cor": "#455a64", "vacinas": [
            {"nome": "DTP", "dose": "2º reforço", "protege": "Difteria, tétano e coqueluche", "idade_limite": 83, "intervalo": "Após reforço anterior", "atraso": "Aplicar reforço se pendente."},
            {"nome": "Febre amarela", "dose": "Reforço quando indicado", "protege": "Febre amarela", "idade_limite": 120, "intervalo": "Conforme histórico", "atraso": "Conferir área com recomendação e dose prévia."},
            {"nome": "Varicela", "dose": "Dose/reforço", "protege": "Varicela", "idade_limite": 83, "intervalo": "Conforme histórico", "atraso": "Completar conforme registro vacinal."},
        ]},
    ]


def status_vacina(meses: float, mes_ref: float, aplicada: bool):
    if aplicada:
        return "Registrada", "#2e7d32", "Registro informado no app."
    if meses + 1 < mes_ref:
        falta = round(mes_ref - meses, 1)
        return "Próxima", "#1565c0", f"Programar em aproximadamente {falta:g} mês(es)."
    if mes_ref - 1 <= meses < mes_ref:
        return "Em breve", "#0277bd", "Orientar retorno na idade indicada."
    if abs(meses - mes_ref) <= 0.75 or meses >= mes_ref:
        if meses > mes_ref + 1:
            return "Atrasada/pendente", "#c62828", "Conferir caderneta. Se não aplicada, atualizar sem reiniciar esquema, respeitando idade máxima e intervalo mínimo."
        return "Indicada agora", "#ef6c00", "Aplicar na visita se não houver contraindicação."
    return "Avaliar", "#607d8b", "Conferir histórico vacinal."
