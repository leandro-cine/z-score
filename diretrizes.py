# diretrizes.py

def obter_sais_ferro():
    return {
        "Sulfato Ferroso (Genérico/Lomfer)": {"conc": 25, "gotas_ml": 25, "mg_por_gota": 1.0, "obs": "Custo baixo; maior risco de gosto metálico."},
        "Ferripolimaltose (Noripurum/Ultrafer)": {"conc": 50, "gotas_ml": 20, "mg_por_gota": 2.5, "obs": "Gosto agradável; não escurece dentes."},
        "Ferro Quelato Glicinato (Neutrofer)": {"conc": 50, "gotas_ml": 20, "mg_por_gota": 2.5, "obs": "Excelente absorção e tolerância."},
        "Bisglicinato Ferroso (Ferrini/Vi-Ferrin)": {"conc": 30, "gotas_ml": 20, "mg_por_gota": 1.5, "obs": "Alta biodisponibilidade."},
        "Combiron Gotas": {"conc": 27.58, "gotas_ml": 10, "mg_por_gota": 2.7, "obs": "Contém vitaminas associadas."}
    }

def obter_orientacoes_detalhadas(meses):
    if meses < 6:
        return {
            "Alimentação": "Aleitamento materno exclusivo. O leite materno supre todas as necessidades, inclusive água.",
            "Prevenção de Acidentes": "Dormir de barriga para cima; sem protetores de berço ou bichos de pelúcia que possam sufocar.",
            "Estímulos": "Tummy time (barriga para baixo) vigiado para fortalecer o pescoço. Conversar e cantar.",
            "Sinais de Alerta": "Febre (>37.8°C), recusa alimentar, gemência ou falta de ar. Procurar emergência."
        }
    elif meses < 12:
        return {
            "Alimentação": "Introdução de sólidos. Iniciar com comida amassada (não batida). Variar grupos alimentares.",
            "Higiene Bucal": "Escovação 2x ao dia com pasta de dente com flúor (mínimo 1000 ppm).",
            "Segurança": "Fase de engatinhar: proteger tomadas e quinas. Cuidado com baldes e bacias com água.",
            "Suplementação": "Garantir adesão à Vitamina D e Ferro conforme prescrição."
        }
    else:
        return {
            "Alimentação": "Comida da família. Evitar açúcar e ultraprocessados até os 2 anos. Estimular a colher.",
            "Comportamento": "Estabelecer rotinas claras. Ler livros e limitar telas (ideal zero até 2 anos).",
            "Segurança": "Cuidado com intoxicações por produtos de limpeza. Manter em locais altos e trancados.",
            "Vacinas": "Atenção aos reforços de 12 e 15 meses."
        }

# (Mantenha as funções obter_classificacao, obter_esquema_vacinal e obter_marcos_caderneta anteriores)
