from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


def _dose_ml_por_dia(dose_mg_dia: float, concentracao_mg_ml: float) -> float:
    if concentracao_mg_ml <= 0:
        return 0.0
    return round(dose_mg_dia / concentracao_mg_ml, 2)


def _linhas(itens: List[str]) -> str:
    return "\n".join([f"- {i}" for i in itens])


PROTOCOLOS: Dict[str, Dict[str, Any]] = {
    "Diarreia aguda": {
        "categoria": "Gastrointestinal",
        "objetivo": "Classificar hidratação, orientar reidratação, sinais de alarme e medidas de suporte.",
        "campos": [
            {"id": "duracao_dias", "label": "Duração do quadro (dias)", "tipo": "number", "min": 0, "max": 30, "default": 1},
            {"id": "evacuacoes_dia", "label": "Evacuações líquidas nas últimas 24h", "tipo": "number", "min": 0, "max": 30, "default": 4},
            {"id": "vomitos", "label": "Vômitos", "tipo": "checkbox"},
            {"id": "sangue_fezes", "label": "Sangue nas fezes", "tipo": "checkbox"},
            {"id": "febre", "label": "Febre", "tipo": "checkbox"},
            {"id": "sinais_desidratacao", "label": "Sinais de desidratação", "tipo": "select", "opcoes": ["Ausentes", "Algum sinal", "Desidratação grave"], "default": "Ausentes"},
            {"id": "aceita_liquidos", "label": "Aceita líquidos/SRO", "tipo": "select", "opcoes": ["Sim", "Com dificuldade", "Não aceita"], "default": "Sim"},
        ],
    },
    "Constipação funcional": {
        "categoria": "Gastrointestinal",
        "objetivo": "Triar sinais de alarme, hábitos, critérios clínicos e medidas terapêuticas iniciais.",
        "campos": [
            {"id": "frequencia", "label": "Frequência evacuatória", "tipo": "select", "opcoes": [">= 3x/semana", "< 3x/semana", "Sem evacuar há > 7 dias"], "default": "< 3x/semana"},
            {"id": "fezes_duras", "label": "Fezes endurecidas/volumosas", "tipo": "checkbox"},
            {"id": "dor", "label": "Dor ou esforço importante ao evacuar", "tipo": "checkbox"},
            {"id": "escape", "label": "Escape fecal/soiling", "tipo": "checkbox"},
            {"id": "retencao", "label": "Postura retentiva/evita evacuar", "tipo": "checkbox"},
            {"id": "sinais_alarme", "label": "Sinais de alarme", "tipo": "multiselect", "opcoes": ["Início no primeiro mês de vida", "Atraso na eliminação de mecônio", "Perda ponderal", "Vômitos biliosos", "Distensão importante", "Sangramento sem fissura", "Alteração neurológica/lombossacra", "Febre persistente"]},
            {"id": "tratamentos_previos", "label": "Tratamentos prévios", "tipo": "multiselect", "opcoes": ["Aumento de fibras/água", "Lactulose", "Polietilenoglicol", "Supositório/enema", "Óleo mineral", "Nenhum"]},
        ],
    },
    "Asma / sibilância recorrente": {
        "categoria": "Respiratório",
        "objetivo": "Avaliar controle, gravidade do episódio atual, tratamento prévio e necessidade de plano de ação.",
        "campos": [
            {"id": "diagnostico_previo", "label": "Já tem diagnóstico prévio de asma/sibilância recorrente?", "tipo": "checkbox"},
            {"id": "sintomas_diurnos", "label": "Sintomas diurnos", "tipo": "select", "opcoes": ["≤ 2x/semana", "> 2x/semana", "Diários"], "default": "≤ 2x/semana"},
            {"id": "despertares", "label": "Despertares noturnos", "tipo": "select", "opcoes": ["Não", "1–2x/mês", "Semanal/frequente"], "default": "Não"},
            {"id": "limitacao", "label": "Limitação de atividade/brincar", "tipo": "checkbox"},
            {"id": "saba", "label": "Uso de broncodilatador de alívio", "tipo": "select", "opcoes": ["Raro/≤2x semana", ">2x semana", "Diário ou quase diário"], "default": "Raro/≤2x semana"},
            {"id": "exacerbacoes", "label": "Exacerbações no último ano", "tipo": "number", "min": 0, "max": 20, "default": 0},
            {"id": "gravidade_atual", "label": "Quadro atual", "tipo": "select", "opcoes": ["Sem crise no momento", "Crise leve", "Crise moderada", "Crise grave/sinais de perigo"], "default": "Sem crise no momento"},
            {"id": "tratamento_atual", "label": "Tratamento atual", "tipo": "multiselect", "opcoes": ["Nenhum", "SABA se necessário", "Corticoide inalatório baixa dose", "Corticoide inalatório média/alta dose", "LABA associado", "Montelucaste", "Corticoide oral recente"]},
        ],
    },
    "IVAS / resfriado comum": {
        "categoria": "Respiratório",
        "objetivo": "Diferenciar quadro viral simples de sinais de gravidade ou complicação bacteriana.",
        "campos": [
            {"id": "duracao_dias", "label": "Duração dos sintomas (dias)", "tipo": "number", "min": 0, "max": 30, "default": 3},
            {"id": "febre", "label": "Febre", "tipo": "checkbox"},
            {"id": "tosse", "label": "Tosse", "tipo": "checkbox"},
            {"id": "coriza", "label": "Coriza/obstrução nasal", "tipo": "checkbox"},
            {"id": "dispneia", "label": "Dispneia, tiragem ou saturação baixa", "tipo": "checkbox"},
            {"id": "otalgia", "label": "Otalgia ou irritabilidade importante", "tipo": "checkbox"},
            {"id": "piora", "label": "Piora após melhora inicial", "tipo": "checkbox"},
        ],
    },
    "Otite média aguda": {
        "categoria": "Otorrino/Respiratório",
        "objetivo": "Apoiar avaliação de dor, febre, bilateralidade e necessidade de antibiótico conforme gravidade.",
        "campos": [
            {"id": "otalgia", "label": "Otalgia/irritabilidade", "tipo": "checkbox"},
            {"id": "febre_alta", "label": "Febre ≥ 39°C ou toxemia", "tipo": "checkbox"},
            {"id": "otorreia", "label": "Otorreia", "tipo": "checkbox"},
            {"id": "bilateral", "label": "Bilateral", "tipo": "checkbox"},
            {"id": "idade_menor_2", "label": "Criança menor de 2 anos", "tipo": "checkbox"},
            {"id": "alergia_penicilina", "label": "Alergia a penicilina relatada", "tipo": "checkbox"},
        ],
    },
}


def obter_protocolos_ambulatoriais() -> Dict[str, Dict[str, Any]]:
    return PROTOCOLOS


def campos_do_protocolo(nome: str) -> List[Dict[str, Any]]:
    return PROTOCOLOS.get(nome, {}).get("campos", [])


def executar_protocolo(nome: str, respostas: Dict[str, Any], dados_crianca: Dict[str, Any]) -> Dict[str, Any]:
    peso = float(dados_crianca.get("peso", 0) or 0)
    idade_meses = float(dados_crianca.get("idade_meses", 0) or 0)

    if nome == "Diarreia aguda":
        grave = respostas.get("sinais_desidratacao") == "Desidratação grave" or respostas.get("aceita_liquidos") == "Não aceita"
        disenteria = bool(respostas.get("sangue_fezes"))
        classificacao = "Diarreia aguda com desidratação grave" if grave else ("Diarreia com sangue/disenteria provável" if disenteria else "Diarreia aguda sem sinais de gravidade")
        conduta = [
            "Avaliar hidratação, diurese, estado geral, mucosas, olhos, sede, perfusão e peso.",
            "Manter aleitamento materno e alimentação habitual conforme aceitação.",
            "Oferecer solução de reidratação oral em pequenas quantidades e com frequência.",
            "Evitar antidiarreicos e bebidas açucaradas/refrigerantes.",
        ]
        if grave:
            conduta.insert(0, "Encaminhar para avaliação urgente/reidratação supervisionada.")
        if disenteria:
            conduta.append("Sangue nas fezes exige avaliação clínica para etiologia invasiva e necessidade de tratamento específico.")
        prescricao = "Solução de Reidratação Oral: oferecer após cada evacuação líquida e conforme sede/aceitação.\nOrientar retorno imediato se sinais de desidratação, sangue nas fezes, vômitos persistentes, letargia ou piora clínica."
        return {"classificacao": classificacao, "gravidade": "Alta" if grave else "Baixa/moderada", "conduta": conduta, "prescricao": prescricao, "orientacoes": ["Higiene das mãos", "Manter dieta", "Retorno se piora ou sinais de alarme"]}

    if nome == "Constipação funcional":
        alarmes = respostas.get("sinais_alarme") or []
        criterios = sum(bool(respostas.get(k)) for k in ["fezes_duras", "dor", "escape", "retencao"])
        if respostas.get("frequencia") != ">= 3x/semana":
            criterios += 1
        classificacao = "Constipação com sinais de alarme" if alarmes else ("Constipação funcional provável" if criterios >= 2 else "Constipação possível — complementar anamnese")
        conduta = [
            "Revisar dieta, ingestão hídrica, rotina de banheiro, dor ao evacuar e comportamento retentivo.",
            "Orientar sentar no vaso após refeições, com apoio para os pés e sem punições.",
            "Aumentar oferta de alimentos in natura/minimamente processados e fibras conforme idade.",
            "Se fecaloma/suspeita de impactação, avaliar desimpactação conforme protocolo local antes da manutenção.",
        ]
        if alarmes:
            conduta.insert(0, "Sinais de alarme presentes: investigar causa orgânica e considerar encaminhamento.")
        prescricao = "Modelo: laxativo osmótico conforme avaliação clínica, peso, idade e disponibilidade local. Associar plano comportamental e retorno programado.\nRevisar resposta terapêutica e adesão antes de escalonar tratamento."
        return {"classificacao": classificacao, "gravidade": "Atenção" if alarmes else "Habitual", "conduta": conduta, "prescricao": prescricao, "orientacoes": ["Não punir escapes", "Rotina diária de banheiro", "Retorno se dor intensa, vômitos, distensão, sangue ou perda de peso"]}

    if nome == "Asma / sibilância recorrente":
        controle_ruim = 0
        controle_ruim += respostas.get("sintomas_diurnos") in ["> 2x/semana", "Diários"]
        controle_ruim += respostas.get("despertares") in ["1–2x/mês", "Semanal/frequente"]
        controle_ruim += bool(respostas.get("limitacao"))
        controle_ruim += respostas.get("saba") in [">2x semana", "Diário ou quase diário"]
        grave_atual = respostas.get("gravidade_atual") == "Crise grave/sinais de perigo"
        moderada = respostas.get("gravidade_atual") == "Crise moderada"
        classificacao = "Crise grave / sinais de perigo" if grave_atual else ("Crise moderada" if moderada else ("Asma/sibilância não controlada" if controle_ruim >= 3 else ("Asma parcialmente controlada" if controle_ruim in [1,2] else "Asma/sibilância controlada ou sem crise atual")))
        conduta = [
            "Conferir técnica inalatória, espaçador, adesão, gatilhos, exposição a fumaça e rinite/atopia associada.",
            "Construir plano de ação por escrito: alívio, controle, sinais de piora e quando procurar urgência.",
            "Reavaliar controle e necessidade de corticoide inalatório conforme frequência de sintomas e exacerbações.",
        ]
        if grave_atual:
            conduta.insert(0, "Encaminhar/avaliar urgência: fala entrecortada, exaustão, cianose, SpO₂ baixa, tiragem importante ou ausência de resposta inicial.")
        elif moderada:
            conduta.insert(0, "Tratar crise conforme protocolo local e reavaliar resposta clínica em curto intervalo.")
        prescricao = "Modelo: prescrever medicação inalatória conforme classificação, idade, peso, disponibilidade e protocolo local.\nIncluir espaçador, técnica de uso, lavagem oral quando corticoide inalatório e retorno para reavaliação do controle."
        return {"classificacao": classificacao, "gravidade": "Alta" if grave_atual else ("Moderada" if moderada else "Variável"), "conduta": conduta, "prescricao": prescricao, "orientacoes": ["Evitar fumaça", "Ensinar técnica inalatória", "Plano de ação", "Retorno se necessidade frequente de medicação de alívio"]}

    if nome == "IVAS / resfriado comum":
        alerta = bool(respostas.get("dispneia")) or bool(respostas.get("piora"))
        classificacao = "IVAS com sinal de alerta/complicação possível" if alerta else "IVAS/resfriado comum provável"
        conduta = ["Lavagem nasal com solução salina", "Hidratação e alimentação conforme aceitação", "Antitérmico/analgésico se febre ou dor conforme peso", "Evitar antibiótico sem critério clínico de infecção bacteriana"]
        if alerta:
            conduta.insert(0, "Reavaliar presencialmente sinais respiratórios e possibilidade de pneumonia, broncoespasmo, otite ou sinusite conforme idade/duração.")
        prescricao = "Modelo: solução salina nasal e medidas de suporte. Antitérmico/analgésico conforme peso se febre/dor. Retorno se dispneia, prostração, febre persistente, piora ou baixa ingesta."
        return {"classificacao": classificacao, "gravidade": "Atenção" if alerta else "Baixa", "conduta": conduta, "prescricao": prescricao, "orientacoes": ["Lavagem nasal", "Hidratação", "Evitar automedicação", "Sinais de alarme"]}

    if nome == "Otite média aguda":
        grave = bool(respostas.get("febre_alta")) or bool(respostas.get("otorreia"))
        maior_risco = bool(respostas.get("bilateral")) and bool(respostas.get("idade_menor_2"))
        classificacao = "OMA com critério de maior gravidade" if grave else ("OMA bilateral em menor de 2 anos" if maior_risco else "OMA não grave / avaliar observação clínica")
        conduta = ["Analgesia adequada é prioridade.", "Confirmar diagnóstico por otoscopia: abaulamento de membrana timpânica/otorreia ou sinais inflamatórios compatíveis.", "Definir antibiótico conforme idade, gravidade, lateralidade, alergias e protocolo local."]
        if respostas.get("alergia_penicilina"):
            conduta.append("Alergia a penicilina relatada: caracterizar reação antes de escolher alternativa.")
        prescricao = "Modelo: analgesia conforme peso. Antibiótico apenas quando critérios clínicos preenchidos; orientar retorno se piora, febre persistente, otorreia ou dor intensa."
        return {"classificacao": classificacao, "gravidade": "Atenção" if (grave or maior_risco) else "Baixa/moderada", "conduta": conduta, "prescricao": prescricao, "orientacoes": ["Analgesia", "Reavaliação se piora", "Não pingar medicação sem orientação"]}

    return {"classificacao": "Protocolo não implementado", "gravidade": "—", "conduta": [], "prescricao": "", "orientacoes": []}
