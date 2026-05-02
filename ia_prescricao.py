from __future__ import annotations

from typing import Any, Dict, Optional
import json

try:
    import streamlit as st
except Exception:  # permite import fora do Streamlit
    st = None


def _secrets_get(nome: str, default=None):
    try:
        if st is not None:
            return st.secrets.get(nome, default)
    except Exception:
        pass
    return default


def diagnostico_ia_configurada() -> Dict[str, Any]:
    provedor = str(_secrets_get("IA_PROVIDER", "local")).lower()
    return {
        "provedor": provedor,
        "openai_configurada": bool(_secrets_get("OPENAI_API_KEY")),
        "gemini_configurada": bool(_secrets_get("GEMINI_API_KEY")),
        "gemini_model": _secrets_get("GEMINI_MODEL", "gemini-2.5-flash"),
    }


def _resumir_lista(v):
    if not v:
        return "não informado"
    if isinstance(v, str):
        return v
    if isinstance(v, dict):
        return "; ".join([f"{k}: {val}" for k, val in v.items() if val not in (None, "", [], {})]) or "não informado"
    return "; ".join([str(x) for x in v if str(x).strip()]) or "não informado"


def _flatten_selected(obj):
    if not obj:
        return "não informado"
    if isinstance(obj, str):
        return obj or "não informado"
    if isinstance(obj, list):
        vals=[]
        for x in obj:
            if isinstance(x, dict):
                vals.append(_flatten_selected(x))
            elif str(x).strip():
                vals.append(str(x))
        return "; ".join(vals) if vals else "não informado"
    if isinstance(obj, dict):
        vals=[]
        for k,v in obj.items():
            if v in (None, "", [], {}):
                continue
            vals.append(f"{k}: {_flatten_selected(v)}")
        return "; ".join(vals) if vals else "não informado"
    return str(obj)


def _resumir_vacinas(lista):
    if not lista:
        return "sem pendências registradas"
    agrupadas = {}
    for item in lista:
        s = str(item)
        if ":" in s:
            idade, vacina = s.split(":", 1)
            agrupadas.setdefault(idade.strip(), []).append(vacina.strip())
        else:
            agrupadas.setdefault("pendências", []).append(s)
    return "; ".join([f"{idade}: {', '.join(vacs)}" for idade, vacs in agrupadas.items()])


def gerar_passagem_caso_local(dados: Dict[str, Any]) -> str:
    c = dados.get("crianca", {})
    nasc = dados.get("nascimento", {})
    cresc = dados.get("crescimento", {})
    consulta = dados.get("consulta", {})
    exame = dados.get("exame_fisico", {})
    vac = dados.get("vacinas", {})
    sup = dados.get("suplementacao", {})
    dev = dados.get("desenvolvimento", {})
    amb = dados.get("ambulatorio", {})

    motivo = consulta.get("queixa_hda") or "consulta de puericultura/seguimento ambulatorial"
    filhos = consulta.get("filhos", {})
    ant_mat = consulta.get("antecedentes_maternos", {})
    hab = consulta.get("habitos", {})

    texto = []
    texto.append("PASSAGEM DE CASO — PUERICULTURA")
    texto.append("")
    texto.append(
        f"Criança do sexo {c.get('sexo','não informado')}, nascida em {c.get('data_nascimento','—')}, "
        f"avaliada em {c.get('data_consulta','—')}, com idade cronológica de {c.get('idade_cronologica','—')} "
        f"e idade corrigida de {c.get('idade_corrigida','—')}. O motivo da avaliação é: {motivo}."
    )
    texto.append(
        f"Antecedentes gestacionais/perinatais: paridade materna {consulta.get('paridade','não informada')}; "
        f"filhos vivos: {_flatten_selected(filhos)}. Gestação com antecedentes maternos: {_flatten_selected(ant_mat)}. "
        f"Medicamentos na gestação: {_flatten_selected(consulta.get('medicamentos_gestacao'))}. "
        f"Suplementações na gestação: {_flatten_selected(consulta.get('suplementacoes_gestacao'))}. "
        f"Vacinação gestacional: {_flatten_selected(consulta.get('vacinacao_gestacao'))}. "
        f"Nascimento com IG {nasc.get('ig','—')}, peso ao nascer {nasc.get('peso_nascimento','—')}, classificado como {nasc.get('classificacao','—')}. "
        f"Intercorrências perinatais/neonatais: {_flatten_selected(consulta.get('antecedentes_perinatais'))}."
    )
    texto.append(f"Triagens neonatais: {_flatten_selected(consulta.get('triagens_neonatais'))}.")
    texto.append(f"Interrogatório sintomatológico segmentar: {_flatten_selected(consulta.get('interrogatorio'))}.")
    texto.append(
        f"Antecedentes patológicos: {_flatten_selected(consulta.get('antecedentes_patologicos'))}. "
        f"Medicamentos em uso/suplementações: {_flatten_selected(consulta.get('medicamentos_uso'))}. "
        f"Antecedentes familiares: {_flatten_selected(consulta.get('antecedentes_familiares'))}."
    )
    texto.append(f"Hábitos e contexto: {_flatten_selected(hab)}. Condições socioeconômicas/moradia: {_flatten_selected(consulta.get('socioeconomico'))}.")
    texto.append(f"Exame físico: sinais vitais {exame.get('sinais_vitais','não informados')}; antropometria {exame.get('antropometria','não informada')}. Achados segmentares: {_flatten_selected({k:v for k,v in exame.items() if k not in ['sinais_vitais','antropometria']})}.")
    if cresc:
        texto.append(f"Crescimento: {_flatten_selected(cresc.get('resumos') or cresc.get('resumo'))}.")
    if dev:
        texto.append(
            f"Desenvolvimento: {dev.get('resumo','não informado')}. "
            f"Marcos presentes/confirmados: {_flatten_selected(dev.get('presentes'))}. "
            f"Marcos ausentes ou não verificados: {_flatten_selected(dev.get('pendentes'))}."
        )
    texto.append(
        f"Imunizações: pendências identificadas na caderneta — {_resumir_vacinas(vac.get('atrasadas'))}. "
        f"Próximas doses programadas — {_resumir_vacinas(vac.get('proximas'))}."
    )
    texto.append(
        f"Suplementação e riscos nutricionais: {_flatten_selected(sup.get('resumo'))}. "
        f"Fatores de risco selecionados: {_flatten_selected(sup.get('fatores_risco'))}."
    )
    if amb:
        texto.append(f"Protocolo ambulatorial: {amb.get('protocolo','—')}; classificação {amb.get('classificacao','—')}; conduta/prescrição: {amb.get('conduta_resumo','—')} {amb.get('prescricao','')}")

    plano = dados.get("plano_sugerido") or []
    texto.append("Plano sugerido: " + ("; ".join(plano) if plano else "orientar conduta conforme motivo da procura, achados de exame físico e evolução clínica; manter vigilância de crescimento, desenvolvimento, suplementação e imunizações") + ".")
    texto.append("Observação: revisar a passagem conforme exame físico presencial, contexto familiar, exames disponíveis e julgamento clínico.")
    return "\n\n".join(texto)

def _prompt_passagem(dados: Dict[str, Any]) -> str:
    return (
        "Você é um assistente de DOCUMENTAÇÃO clínica pediátrica para passagem de caso entre profissionais. "
        "Escreva em português do Brasil, em texto fluido, clínico e objetivo, mas informativo. NÃO responda em formato de JSON, tabela ou checklist bruto. "
        "NÃO invente dados. Se algo não foi informado, diga apenas quando for relevante. "
        "A passagem deve ter subtítulos curtos e parágrafos: Identificação e motivo; Anamnese; Antecedentes gestacionais/perinatais; Antecedentes pessoais/familiares; Hábitos e contexto; Exame físico; Crescimento e desenvolvimento; Imunizações e suplementação; Impressão e plano. "
        "Use raciocínio clínico estruturado: conecte os dados, não apenas liste. "
        "CRESCIMENTO: informe explicitamente se peso, estatura/comprimento, IMC e PC estão adequados ou alterados, usando as classificações e Z-scores fornecidos. Não escreva só que foram registrados. "
        "DESENVOLVIMENTO: se adequado, cite os marcos presentes; se houver ausência ou não verificação, destaque quais e a conduta de vigilância/estimulação. "
        "VACINAS: quando houver atraso, liste claramente as vacinas/doses faltantes agrupadas por idade do calendário. Não escreva 'revisar caderneta' como substituto, pois a caderneta já foi revisada no app. "
        "SUPLEMENTAÇÃO: se ferro/vitamina D estiverem fora da janela por idade, diga isso diretamente; para vitamina A, indique verificar/aplicar a megadose correspondente à idade quando elegível; informe presença ou ausência dos fatores de risco selecionados para anemia, hipovitaminose D e B12. "
        "PLANO: faça sugestões compatíveis com o motivo da procura, sintomas, exame físico, crescimento, desenvolvimento, imunização e suplementação. "
        "Não inclua frases genéricas longas nem recomendações fora dos dados.\n\n"
        f"DADOS ESTRUTURADOS JSON:\n{json.dumps(dados, ensure_ascii=False, indent=2)}"
    )

def _gerar_gemini(prompt: str, api_key: str, model: str) -> str:
    from google import genai  # type: ignore
    try:
        from google.genai import types  # type: ignore
    except Exception:
        types = None
    client = genai.Client(api_key=api_key)
    # Google Search grounding é tentado quando disponível, mas o app funciona sem ele.
    try:
        if types is not None:
            tool = types.Tool(google_search=types.GoogleSearch())
            config = types.GenerateContentConfig(temperature=0.2, tools=[tool])
            resp = client.models.generate_content(model=model, contents=prompt, config=config)
        else:
            resp = client.models.generate_content(model=model, contents=prompt)
    except TypeError:
        resp = client.models.generate_content(model=model, contents=prompt)
    return getattr(resp, "text", "") or ""


def _gerar_openai(prompt: str, api_key: str, model: str) -> str:
    from openai import OpenAI  # type: ignore
    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role":"system", "content":"Você é um assistente de documentação clínica pediátrica. Não substitui julgamento profissional."},
            {"role":"user", "content":prompt},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content or ""


def gerar_passagem_caso_ia(dados: Dict[str, Any], api_key: Optional[str] = None, model: Optional[str] = None) -> str:
    prompt = _prompt_passagem(dados)
    provider = str(_secrets_get("IA_PROVIDER", "local")).lower()
    try:
        if provider == "gemini":
            key = _secrets_get("GEMINI_API_KEY")
            mdl = _secrets_get("GEMINI_MODEL", "gemini-2.5-flash")
            if not key:
                return gerar_passagem_caso_local(dados) + "\n\n[IA Gemini não configurada: GEMINI_API_KEY ausente.]"
            return _gerar_gemini(prompt, key, mdl)
        if provider == "openai":
            key = api_key or _secrets_get("OPENAI_API_KEY")
            mdl = model or _secrets_get("OPENAI_MODEL", "gpt-4o-mini")
            if not key:
                return gerar_passagem_caso_local(dados) + "\n\n[IA OpenAI não configurada: OPENAI_API_KEY ausente.]"
            return _gerar_openai(prompt, key, mdl)
    except Exception as exc:
        return gerar_passagem_caso_local(dados) + f"\n\n[IA indisponível: foi usada a versão local. Detalhe técnico: {exc}]"
    return gerar_passagem_caso_local(dados)


def gerar_orientacao_medicamento_ia(nome: str, idade: str, peso: float, finalidade: str = "") -> str:
    dados = {"medicamento": nome, "idade": idade, "peso_kg": peso, "finalidade": finalidade}
    prompt = (
        "Forneça apoio técnico para conferência de medicamento em pediatria, em português do Brasil. "
        "Use fontes oficiais quando houver ferramenta de busca disponível: RENAME/Ministério da Saúde, REMUME local quando aplicável, bulário/ANVISA, SBP ou diretrizes reconhecidas. "
        "Não substitua prescrição médica. Informe apresentação usual, alertas de segurança, necessidade de ajuste por peso/idade e disponibilidade provável em RENAME/REMUME se souber. "
        "Não invente dose se não tiver segurança; peça conferência em bula/diretriz.\n\n"
        f"DADOS: {json.dumps(dados, ensure_ascii=False)}"
    )
    provider = str(_secrets_get("IA_PROVIDER", "local")).lower()
    try:
        if provider == "gemini" and _secrets_get("GEMINI_API_KEY"):
            return _gerar_gemini(prompt, _secrets_get("GEMINI_API_KEY"), _secrets_get("GEMINI_MODEL", "gemini-2.5-flash"))
        if provider == "openai" and _secrets_get("OPENAI_API_KEY"):
            return _gerar_openai(prompt, _secrets_get("OPENAI_API_KEY"), _secrets_get("OPENAI_MODEL", "gpt-4o-mini"))
    except Exception as exc:
        return f"IA indisponível para checagem medicamentosa. Detalhe: {exc}"
    return "IA não configurada. Confira apresentação, dose pediátrica, contraindicações e disponibilidade na RENAME/REMUME/bula oficial antes de prescrever."
