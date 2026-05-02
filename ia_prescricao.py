from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, List
import json


def _get_streamlit_secrets() -> Dict[str, Any]:
    try:
        import streamlit as st  # type: ignore
        return dict(st.secrets)
    except Exception:
        return {}


def _secret(nome: str, padrao: Optional[str] = None) -> Optional[str]:
    valor = _get_streamlit_secrets().get(nome, padrao)
    if valor is None:
        return padrao
    return str(valor)


def diagnostico_ia_configurada() -> Dict[str, Any]:
    provider = (_secret("IA_PROVIDER", "local") or "local").lower().strip()
    return {
        "IA_PROVIDER": provider,
        "GEMINI_API_KEY_configurada": bool(_secret("GEMINI_API_KEY")),
        "GEMINI_MODEL": _secret("GEMINI_MODEL", "gemini-2.5-flash"),
        "OPENAI_API_KEY_configurada": bool(_secret("OPENAI_API_KEY")),
        "OPENAI_MODEL": _secret("OPENAI_MODEL", "gpt-4o-mini"),
    }


def _valor(d: Dict[str, Any], chave: str, padrao: str = "não informado") -> str:
    valor = d.get(chave, padrao)
    if valor is None or valor == "":
        return padrao
    return str(valor)


def _as_list(valor: Any) -> List[str]:
    if valor is None:
        return []
    if isinstance(valor, (list, tuple, set)):
        bruto = list(valor)
    else:
        texto = str(valor)
        for sep in ["\n", "|"]:
            texto = texto.replace(sep, ";")
        bruto = [p.strip() for p in texto.split(";")]
    vistos = set()
    saida: List[str] = []
    for item in bruto:
        s = str(item).strip().strip("-• ").strip()
        if not s or s.lower() in {"—", "nenhuma", "nenhum", "nenhuma informada", "não informado", "nao informado"}:
            continue
        k = s.lower()
        if k not in vistos:
            vistos.add(k)
            saida.append(s)
    return saida


def _join(itens: Any, vazio: str = "não informado") -> str:
    lista = _as_list(itens)
    return "; ".join(lista) if lista else vazio


def _is_not_informado(s: Any) -> bool:
    if s is None:
        return True
    t = str(s).strip().lower()
    return t in {"", "não informado", "nao informado", "não informada", "nenhum", "nenhuma", "—"}


def _dict_get(d: Any, chave: str, padrao: Any = None) -> Any:
    return d.get(chave, padrao) if isinstance(d, dict) else padrao


def _formatar_crescimento(crescimento: Dict[str, Any]) -> str:
    detalhes = crescimento.get("detalhes") if isinstance(crescimento, dict) else None
    if isinstance(detalhes, dict) and detalhes:
        ordem = ["Peso", "Estatura", "IMC", "PC"]
        partes = []
        for nome in ordem:
            r = detalhes.get(nome)
            if not isinstance(r, dict):
                continue
            valor = r.get("valor")
            unidade = r.get("unidade", "")
            cls = r.get("classificacao", "classificação não informada")
            z = r.get("z", "—")
            pct = r.get("percentil", "—")
            partes.append(f"{nome}: {valor} {unidade}, {cls} (Z={z}; P≈{pct})")
        if partes:
            return "; ".join(partes) + "."
    resumo = _dict_get(crescimento, "resumo", "não calculado")
    return str(resumo)


def _formatar_desenvolvimento(dev: Dict[str, Any]) -> str:
    faixa = _dict_get(dev, "faixa_atual", "não informado")
    classificacao = _dict_get(dev, "classificacao", "não informado")
    presentes = _as_list(_dict_get(dev, "marcos_presentes", []))
    ausentes = _as_list(_dict_get(dev, "marcos_ausentes", []))
    nv = _as_list(_dict_get(dev, "marcos_nao_verificados", []))
    fatores = _as_list(_dict_get(dev, "fatores_risco", []))

    partes = [f"faixa avaliada: {faixa}; classificação: {classificacao}"]
    if presentes:
        partes.append("marcos presentes: " + "; ".join(presentes))
    if ausentes:
        partes.append("marcos ausentes: " + "; ".join(ausentes))
    if nv:
        partes.append("não verificados: " + "; ".join(nv))
    if fatores:
        partes.append("fatores de risco para desenvolvimento/seguimento: " + "; ".join(fatores))
    return ". ".join(partes) + "."


def _agrupar_vacinas_por_idade(itens: Any) -> str:
    lista = _as_list(itens)
    if not lista:
        return "nenhuma pendência informada"
    grupos: Dict[str, List[str]] = {}
    for item in lista:
        idade = "idade não especificada"
        nome_dose = item
        if "(" in item and ")" in item:
            idade = item.split("(")[-1].split(")")[0].strip()
            nome_dose = item.rsplit("(", 1)[0].strip().strip("—").strip()
        grupos.setdefault(idade, []).append(nome_dose)

    ordem = ["Ao nascer", "2 meses", "3 meses", "4 meses", "5 meses", "6 meses", "9 meses", "12 meses", "15 meses", "4 anos", "5 anos", "9 a 14 anos", "Conforme produto", "Conforme PNI", "idade não especificada"]
    chaves = sorted(grupos.keys(), key=lambda x: ordem.index(x) if x in ordem else 999)
    partes = []
    for idade in chaves:
        vacs = "; ".join(grupos[idade])
        partes.append(f"{idade}: {vacs}")
    return ". ".join(partes) + "."


def _formatar_suplementacao(sup: Dict[str, Any]) -> str:
    if not isinstance(sup, dict):
        return "não informado"
    rec = sup.get("ferro", {}) if isinstance(sup.get("ferro", {}), dict) else {}
    vit_a = sup.get("vitamina_a", {}) if isinstance(sup.get("vitamina_a", {}), dict) else {}
    vit_d = sup.get("vitamina_d", {}) if isinstance(sup.get("vitamina_d", {}), dict) else {}
    vit_b12 = sup.get("vitamina_b12", {}) if isinstance(sup.get("vitamina_b12", {}), dict) else {}

    fat_m = _as_list(sup.get("fatores_risco_anemia_maternos"))
    fat_c = _as_list(sup.get("fatores_risco_anemia_crianca"))
    fat_d = _as_list(sup.get("fatores_risco_vitamina_d"))
    fat_b12 = _as_list(_dict_get(vit_b12, "fatores_risco", []))

    partes = []
    if rec:
        dose = rec.get("dose_mg_dia", 0)
        partes.append(f"Ferro: {rec.get('protocolo', 'protocolo não informado')}; {rec.get('resumo', '')}; dose calculada {dose} mg/dia. Fatores de risco para anemia/ferro — maternos: {_join(fat_m, 'não informados')}; criança: {_join(fat_c, 'não informados')}")
    else:
        partes.append(f"Ferro: não informado. Fatores de risco para anemia/ferro — maternos: {_join(fat_m, 'não informados')}; criança: {_join(fat_c, 'não informados')}")

    if vit_a:
        indicada = "indicada" if vit_a.get("indicada") else "não indicada automaticamente/conferir critérios"
        partes.append(f"Vitamina A: {vit_a.get('dose', 'dose não informada')}, {vit_a.get('frequencia', 'frequência não informada')}; situação: {indicada}; critério/motivo: {vit_a.get('motivo', 'não informado')}. Verificar se já recebeu a megadose correspondente à idade e registrar na caderneta quando aplicável")
    else:
        partes.append("Vitamina A: não informada; verificar se já recebeu a megadose correspondente à idade quando fizer parte do público programático")

    if vit_d:
        partes.append(f"Vitamina D: {vit_d.get('dose', 'dose não informada')}; {vit_d.get('orientacao', '')}. Fatores de risco: {_join(fat_d, 'não informados')}")
    else:
        partes.append(f"Vitamina D: não informada. Fatores de risco: {_join(fat_d, 'não informados')}")

    partes.append(f"Vitamina B12: fatores de risco: {_join(fat_b12, 'não informados')}")
    return "\n".join(f"- {p}" for p in partes)


def _formatar_exame_fisico(ef: Dict[str, Any]) -> str:
    if not isinstance(ef, dict):
        return "não informado"
    itens = []
    for k, label in [
        ("sinais_vitais", "sinais vitais"), ("estado_geral", "estado geral"), ("hidratacao", "hidratação"),
        ("perfusao", "perfusão"), ("respiratorio", "respiratório"), ("cardiovascular", "cardiovascular"),
        ("abdome", "abdome"), ("pele_mucosas", "pele/mucosas"), ("orl", "ORL"), ("neurologico", "neurológico"), ("outros", "outros achados"),
    ]:
        v = ef.get(k)
        if not _is_not_informado(v):
            itens.append(f"{label}: {v}")
    return "; ".join(itens) if itens else "não informado"


def _formatar_ambulatorio(amb: Dict[str, Any]) -> str:
    if not isinstance(amb, dict):
        return "não informado"
    protocolo = amb.get("protocolo", "não informado")
    if _is_not_informado(protocolo):
        return "sem protocolo ambulatorial específico selecionado"
    partes = [f"protocolo: {protocolo}"]
    for k in ["classificacao", "gravidade"]:
        if not _is_not_informado(amb.get(k)):
            partes.append(f"{k}: {amb.get(k)}")
    cond = _as_list(amb.get("conduta"))
    if cond:
        partes.append("conduta do protocolo: " + "; ".join(cond))
    presc = amb.get("prescricao")
    if not _is_not_informado(presc):
        partes.append("prescrição/orientação sugerida pelo protocolo: " + str(presc))
    return ". ".join(partes) + "."


def gerar_passagem_caso_local(dados: Dict[str, Any]) -> str:
    crianca = dados.get("crianca", {}) or {}
    mae = dados.get("mae_gestacao", {}) or {}
    nascimento = dados.get("nascimento", {}) or {}
    habitos = dados.get("habitos", {}) or {}
    isint = dados.get("interrogatorio_sintomatologico", {}) or {}
    ant_pat = dados.get("antecedentes_patologicos", {}) or {}
    ant_fam = dados.get("antecedentes_familiares", {}) or {}
    ef = dados.get("exame_fisico", {}) or {}
    exames = dados.get("exames_complementares", {}) or {}
    medidas = dados.get("medidas", {}) or {}
    crescimento = dados.get("crescimento", {}) or {}
    dev = dados.get("desenvolvimento", {}) or {}
    vacinas = dados.get("vacinas", {}) or {}
    sup = dados.get("suplementacao", {}) or {}
    amb = dados.get("ambulatorio", {}) or {}

    motivo = _valor(crianca, "motivo_procura", "puericultura/seguimento")
    crescimento_txt = _formatar_crescimento(crescimento)
    dev_txt = _formatar_desenvolvimento(dev)
    vac_atrasadas = _as_list(vacinas.get("atrasadas"))
    vac_proximas = _as_list(vacinas.get("proximas"))
    vac_atrasadas_txt = _agrupar_vacinas_por_idade(vac_atrasadas) if vac_atrasadas else "sem vacinas faltantes informadas"
    vac_proximas_txt = _agrupar_vacinas_por_idade(vac_proximas) if vac_proximas else "sem próximas doses informadas"
    suplementacao_txt = _formatar_suplementacao(sup)
    amb_txt = _formatar_ambulatorio(amb)

    sintomas_presentes = _join(isint.get("presentes"), "sem sintomas presentes selecionados")
    sintomas_negados = _join(isint.get("negados"), "sem negativas dirigidas registradas")
    detalhes_sint = _valor(isint, "detalhes", "não informado")

    antecedentes_pat = _join(ant_pat.get("itens"), "não informados")
    if not _is_not_informado(ant_pat.get("detalhes")):
        antecedentes_pat += f"; detalhes: {ant_pat.get('detalhes')}"
    antecedentes_fam = _join(ant_fam.get("itens"), "não informados")
    if not _is_not_informado(ant_fam.get("detalhes")):
        antecedentes_fam += f"; detalhes: {ant_fam.get('detalhes')}"

    exame_txt = _formatar_exame_fisico(ef)
    exames_txt = _join(exames.get("itens"), "não informados")
    if not _is_not_informado(exames.get("resultados")):
        exames_txt += f"; resultados/observações: {exames.get('resultados')}"

    # Plano sugestivo baseado no motivo da procura e achados selecionados
    plano = []
    if vac_atrasadas:
        plano.append("atualizar as vacinas faltantes identificadas, respeitando idade atual, intervalos mínimos, idade máxima e contraindicações; registrar as doses aplicadas")
    if "Diarreia" in _as_list(isint.get("presentes")) or "Vômitos" in _as_list(isint.get("presentes")):
        plano.append("se queixa gastrointestinal estiver ativa, avaliar hidratação, aceitação oral, diurese, presença de sangue nas fezes e necessidade de SRO/retorno precoce")
    if "Sibilância/chiado" in _as_list(isint.get("presentes")) or "Dispneia/esforço respiratório" in _as_list(isint.get("presentes")):
        plano.append("se queixa respiratória estiver ativa, estratificar gravidade respiratória, saturação, frequência respiratória e resposta a broncodilatador conforme protocolo")
    if _as_list(dev.get("marcos_ausentes")):
        plano.append("orientar estimulação dos marcos ausentes e programar reavaliação em curto prazo, considerando encaminhamento conforme gravidade e fatores de risco")
    else:
        plano.append("manter vigilância do desenvolvimento e orientar estímulos compatíveis com a próxima faixa etária")
    plano.append("correlacionar achados antropométricos com a curva longitudinal e contexto alimentar/familiar")
    if sup:
        plano.append("confirmar fatores de risco e histórico de suplementação; verificar megadose de vitamina A correspondente à idade quando aplicável")
    if _formatar_ambulatorio(amb) != "sem protocolo ambulatorial específico selecionado":
        plano.append("adequar o plano final ao protocolo ambulatorial selecionado e ao exame físico")

    texto = f"""# Passagem de caso — puericultura

## Identificação e motivo da consulta
Criança do sexo {_valor(crianca, 'sexo')}, nascida em {_valor(crianca, 'data_nascimento')}, avaliada em {_valor(crianca, 'data_consulta')}, com idade cronológica de {_valor(crianca, 'idade_cronologica')} e idade corrigida de {_valor(crianca, 'idade_corrigida')}. Motivo da procura informado: {motivo}.

## Antecedentes pessoais, gestacionais e perinatais
Antecedentes materno-gestacionais: paridade {_valor(mae, 'paridade')}; doenças maternas prévias {_valor(mae, 'doencas_previas')}; intercorrências gestacionais {_valor(mae, 'doencas_intercorrencias_gestacionais')}; vacinação gestacional {_valor(mae, 'vacinacao_gestante')}. Nascimento por {_valor(mae, 'tipo_parto')}, com intercorrências no parto/nascimento: {_valor(mae, 'intercorrencias_parto')}.

Ao nascer: IG {_valor(nascimento, 'ig')}, peso {_valor(nascimento, 'peso_nascimento')}, comprimento {_valor(nascimento, 'comprimento_nascimento')}, PC {_valor(nascimento, 'pc_nascimento')}, Apgar {_valor(nascimento, 'apgar')}. Classificação perinatal: {_valor(nascimento, 'classificacao')}; riscos registrados: {_join(nascimento.get('riscos'), 'não informados')}. Internação neonatal/triagens: {_valor(nascimento, 'internacao_triagens')}.

Antecedentes patológicos pessoais: {antecedentes_pat}. Antecedentes familiares: {antecedentes_fam}.

## História atual, hábitos e interrogatório sintomatológico
Sintomas presentes: {sintomas_presentes}. Negativas dirigidas: {sintomas_negados}. Detalhes adicionais: {detalhes_sint}.

Hábitos e rotina: alimentação — {_valor(habitos, 'alimentacao')}; sono — {_valor(habitos, 'sono')}; higiene/saúde bucal — {_valor(habitos, 'higiene_saude_bucal')}; diurese — {_valor(habitos, 'diurese')}; evacuações — {_valor(habitos, 'defecacao')}; telas/atividade/creche — {_valor(habitos, 'telas_atividade_creche')}; alergias, medicações e tratamentos/exames prévios — {_valor(habitos, 'alergias_medicacoes_exames')}.

## Exame físico e exames complementares
Exame físico registrado: {exame_txt}.

Exames complementares: {exames_txt}.

## Crescimento e desenvolvimento
Medidas atuais: peso {_valor(medidas, 'peso')}, estatura/comprimento {_valor(medidas, 'estatura')}, perímetro cefálico {_valor(medidas, 'pc')} e IMC {_valor(medidas, 'imc')}. Interpretação antropométrica: {crescimento_txt}

Desenvolvimento: {dev_txt}

## Imunizações
Vacinas/doses faltantes identificadas após revisão no app: {vac_atrasadas_txt}
Próximas vacinas/reforços previstos: {vac_proximas_txt}

## Suplementação e prevenção de carências
{suplementacao_txt}

## Protocolo ambulatorial selecionado
{amb_txt}

## Impressão e plano sugestivo
"""
    for p in plano:
        texto += f"- {p}.\n"
    texto += "\nRevisar conforme exame físico, contexto da consulta, disponibilidade local e julgamento clínico."
    return texto


def _montar_prompt_passagem(dados: Dict[str, Any]) -> str:
    local_base = gerar_passagem_caso_local(dados)
    dados_json = json.dumps(dados, ensure_ascii=False, indent=2, default=str)
    return f"""
Você é um assistente de documentação clínica pediátrica para PUERICULTURA ambulatorial. Gere uma PASSAGEM DE CASO em português do Brasil, fluida, útil para comunicação entre profissionais de saúde e com raciocínio clínico estruturado.

REGRAS OBRIGATÓRIAS:
1. Use somente os dados fornecidos. Não invente exame físico, diagnósticos, medicamentos, resultados ou condutas.
2. Crescimento: NÃO escreva apenas que medidas foram registradas. Informe a classificação de peso, estatura/comprimento, IMC e PC quando fornecida, incluindo Z-score/percentil de forma resumida.
3. Desenvolvimento: se estiver adequado, informe QUAIS marcos/habilidades presentes foram registrados; se houver ausentes/não verificados, destaque objetivamente.
4. Vacinas: se a caderneta já foi revisada no app, NÃO escreva “revisar caderneta” como informação principal. Liste claramente as vacinas/doses faltantes agrupadas por idade, de forma prática. Pode orientar completar/atualizar conforme PNI, mas sem substituir a lista.
5. Suplementação: se ferro/vitamina D estiver fora da faixa/ciclo, diga isso de modo direto. Para vitamina A, diga que deve verificar se já tomou a megadose correspondente à idade quando elegível. Informe fatores de risco registrados para anemia/ferro, hipovitaminose D e B12.
6. Inclua as seções: Identificação e motivo; Antecedentes pessoais/gestacionais/perinatais; História atual e interrogatório sintomatológico; Antecedentes familiares; Exame físico; Exames complementares; Crescimento e desenvolvimento; Imunizações; Suplementação; Impressão e plano sugestivo.
7. O plano final deve ser sugestivo e coerente com o motivo da procura e os sintomas/protocolo selecionado. Não faça conduta definitiva se faltar dado clínico essencial.
8. Evite texto telegráfico demais, mas mantenha objetividade médica. Não use markdown excessivamente complexo.
9. Finalize com: “Revisar conforme exame físico e julgamento clínico.”

DADOS ESTRUTURADOS:
{dados_json}

RASCUNHO LOCAL A SER MELHORADO, PRESERVANDO AS INFORMAÇÕES:
{local_base}
""".strip()


def _gerar_com_gemini(prompt: str) -> Tuple[Optional[str], Optional[str]]:
    api_key = _secret("GEMINI_API_KEY")
    model = _secret("GEMINI_MODEL", "gemini-2.5-flash") or "gemini-2.5-flash"
    if not api_key:
        return None, "GEMINI_API_KEY não configurada nos Secrets."
    try:
        from google import genai  # type: ignore
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model=model, contents=prompt)
        texto = getattr(response, "text", None)
        if texto and str(texto).strip():
            return str(texto).strip(), None
        return None, "Gemini retornou resposta vazia."
    except Exception as exc:
        return None, str(exc)


def _gerar_com_openai(prompt: str, api_key: Optional[str] = None, model: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
    api_key = api_key or _secret("OPENAI_API_KEY")
    model = model or _secret("OPENAI_MODEL", "gpt-4o-mini") or "gpt-4o-mini"
    if not api_key:
        return None, "OPENAI_API_KEY não configurada nos Secrets."
    try:
        from openai import OpenAI  # type: ignore
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Você é um assistente de documentação clínica pediátrica. Ajude a redigir passagens de caso sem substituir o julgamento profissional."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )
        texto = resp.choices[0].message.content
        if texto and texto.strip():
            return texto.strip(), None
        return None, "OpenAI retornou resposta vazia."
    except Exception as exc:
        return None, str(exc)


def gerar_passagem_caso_ia(dados: Dict[str, Any], api_key: Optional[str] = None, model: Optional[str] = None, mostrar_erro: bool = True) -> str:
    prompt = _montar_prompt_passagem(dados)
    provider = (_secret("IA_PROVIDER", "") or "").lower().strip()
    if not provider:
        provider = "openai" if api_key else "local"

    texto: Optional[str] = None
    erro: Optional[str] = None
    if provider == "gemini":
        texto, erro = _gerar_com_gemini(prompt)
    elif provider == "openai":
        texto, erro = _gerar_com_openai(prompt, api_key=api_key, model=model)
    elif provider in {"local", "off", "desativada", "desativado"}:
        return gerar_passagem_caso_local(dados)
    else:
        erro = f"IA_PROVIDER='{provider}' não reconhecido. Use 'gemini', 'openai' ou 'local'."

    if texto:
        return texto
    local = gerar_passagem_caso_local(dados)
    if mostrar_erro and erro:
        return local + f"\n\n[IA indisponível: foi usada a versão local. Detalhe técnico: {erro}]"
    return local


def gerar_passagem_de_caso_local(dados: Dict[str, Any]) -> str:
    return gerar_passagem_caso_local(dados)


def gerar_passagem_de_caso_ia(dados: Dict[str, Any], api_key: Optional[str] = None, model: Optional[str] = None) -> str:
    return gerar_passagem_caso_ia(dados, api_key=api_key, model=model)
