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


def gerar_passagem_caso_local(dados: Dict[str, Any]) -> str:
    c = dados.get("crianca", {})
    nasc = dados.get("nascimento", {})
    antro = dados.get("crescimento", {})
    consulta = dados.get("consulta", {})
    exame = dados.get("exame_fisico", {})
    vac = dados.get("vacinas", {})
    sup = dados.get("suplementacao", {})
    dev = dados.get("desenvolvimento", {})
    amb = dados.get("ambulatorio", {})

    partes = []
    partes.append("PASSAGEM DE CASO — PUERICULTURA")
    partes.append("")
    partes.append(
        f"Criança do sexo {c.get('sexo','não informado')}, DN {c.get('data_nascimento','—')}, "
        f"avaliada em {c.get('data_consulta','—')}, com idade cronológica {c.get('idade_cronologica','—')} "
        f"e idade corrigida {c.get('idade_corrigida','—')}."
    )
    motivo = consulta.get("queixa_hda") or consulta.get("motivo") or "consulta de puericultura/avaliação pediátrica"
    partes.append(f"Motivo/HDA: {motivo}")
    partes.append(
        f"Antecedentes gestacionais e perinatais: mãe {consulta.get('paridade','G__PN__PC__A__')}; "
        f"intercorrências maternas: {_resumir_lista(consulta.get('antecedentes_maternos'))}. "
        f"Nascimento com IG {nasc.get('ig','—')}, PN {nasc.get('peso_nascimento','—')}, classificação {nasc.get('classificacao','—')}. "
        f"Intercorrências perinatais: {_resumir_lista(consulta.get('antecedentes_perinatais'))}."
    )
    if consulta.get("triagens_neonatais"):
        partes.append(f"Triagens neonatais: {_resumir_lista(consulta.get('triagens_neonatais'))}.")
    partes.append(f"Interrogatório sintomatológico: {_resumir_lista(consulta.get('interrogatorio'))}.")
    partes.append(f"Antecedentes patológicos: {_resumir_lista(consulta.get('antecedentes_patologicos'))}. Medicamentos em uso: {_resumir_lista(consulta.get('medicamentos_uso'))}.")
    partes.append(f"Antecedentes familiares: {_resumir_lista(consulta.get('antecedentes_familiares'))}.")
    partes.append(f"Hábitos de vida/alimentação/sono/eliminações: {_resumir_lista(consulta.get('habitos'))}.")
    partes.append(f"Condições socioeconômicas e moradia: {_resumir_lista(consulta.get('socioeconomico'))}.")
    if exame:
        partes.append(f"Exame físico: {_resumir_lista(exame)}.")
    if antro:
        partes.append(f"Crescimento: {_resumir_lista(antro.get('resumos') or antro.get('resumo'))}.")
    if dev:
        partes.append(f"Desenvolvimento: {dev.get('resumo','não informado')}. Marcos presentes: {_resumir_lista(dev.get('presentes'))}. Marcos ausentes/não verificados: {_resumir_lista(dev.get('pendentes'))}.")
    if vac:
        partes.append(f"Imunizações: faltantes/pendentes — {_resumir_lista(vac.get('atrasadas'))}. Próximas — {_resumir_lista(vac.get('proximas'))}.")
    if sup:
        partes.append(f"Suplementação: {_resumir_lista(sup.get('resumo'))}. Fatores de risco: {_resumir_lista(sup.get('fatores_risco'))}.")
    if amb:
        partes.append(f"Protocolo ambulatorial selecionado: {amb.get('protocolo','—')}. Classificação: {amb.get('classificacao','—')}. Conduta: {amb.get('conduta_resumo','—')}.")

    plano = dados.get("plano_sugerido") or []
    if not plano:
        plano = ["adequar conduta ao motivo da procura", "atualizar imunizações pendentes", "manter vigilância de crescimento e desenvolvimento", "orientar retorno conforme evolução clínica"]
    partes.append("Plano sugerido: " + "; ".join(plano) + ".")
    partes.append("Revisar conforme exame físico completo, contexto familiar e julgamento clínico.")
    return "\n\n".join(partes)


def _prompt_passagem(dados: Dict[str, Any]) -> str:
    return (
        "Você é um assistente de documentação clínica pediátrica. Gere uma PASSAGEM DE CASO em português do Brasil, "
        "com raciocínio clínico estruturado, fluido e útil para um médico/pediatra. NÃO invente dados, diagnósticos, doses ou exames. "
        "Use apenas os dados fornecidos. Quando houver classificação de crescimento, diga se peso, estatura/comprimento, IMC e PC estão adequados ou alterados; não escreva apenas 'registrados'. "
        "Quando desenvolvimento estiver adequado, cite os marcos presentes marcados no formulário; se ausentes, destaque. "
        "Em imunizações, liste objetivamente as vacinas/doses faltantes agrupadas por idade, sem dizer 'revisar caderneta' como substituto da lista. "
        "Em suplementação, diga se há ou não fatores de risco para anemia/hipovitaminose D/B12 e se vitamina A da idade já deve ser conferida/aplicada conforme critérios. "
        "Estruture em parágrafos com subtítulos curtos: Identificação e motivo; Anamnese; Antecedentes; Hábitos e contexto; Exame físico; Crescimento e desenvolvimento; Imunizações e suplementação; Impressão/pendências; Plano sugerido. "
        "O plano deve ser sugestivo e compatível com o motivo da procura e achados selecionados.\n\n"
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
