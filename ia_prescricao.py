from __future__ import annotations

from typing import Any, Dict, Optional, Tuple


# ============================================================
# IA / PASSAGEM DE CASO
# ------------------------------------------------------------
# Este arquivo funciona em três modos:
# 1) Gemini via Google AI Studio, quando IA_PROVIDER="gemini".
# 2) OpenAI, quando IA_PROVIDER="openai" ou quando o app passa api_key.
# 3) Fallback local, quando a API estiver sem chave, sem cota ou indisponível.
#
# Secrets esperados no Streamlit Cloud:
# IA_PROVIDER = "gemini"
# GEMINI_API_KEY = "sua_chave_nova"
# GEMINI_MODEL = "gemini-2.5-flash"
#
# Para OpenAI, opcional:
# IA_PROVIDER = "openai"
# OPENAI_API_KEY = "sua_chave"
# OPENAI_MODEL = "gpt-4o-mini"
# ============================================================


def _get_streamlit_secrets() -> Dict[str, Any]:
    """Lê st.secrets sem quebrar caso esteja rodando fora do Streamlit."""
    try:
        import streamlit as st  # type: ignore

        return dict(st.secrets)
    except Exception:
        return {}


def _secret(nome: str, padrao: Optional[str] = None) -> Optional[str]:
    secrets = _get_streamlit_secrets()
    valor = secrets.get(nome, padrao)
    if valor is None:
        return padrao
    return str(valor)


def diagnostico_ia_configurada() -> Dict[str, Any]:
    """
    Retorna um diagnóstico seguro, sem expor chaves.
    Útil para mostrar em um expander de debug no app.py.
    """
    provider = (_secret("IA_PROVIDER", "local") or "local").lower().strip()
    return {
        "IA_PROVIDER": provider,
        "GEMINI_API_KEY_configurada": bool(_secret("GEMINI_API_KEY")),
        "GEMINI_MODEL": _secret("GEMINI_MODEL", "gemini-2.5-flash"),
        "OPENAI_API_KEY_configurada": bool(_secret("OPENAI_API_KEY")),
        "OPENAI_MODEL": _secret("OPENAI_MODEL", "gpt-4o-mini"),
    }


def _valor(d: Dict[str, Any], chave: str, padrao: str = "—") -> str:
    valor = d.get(chave, padrao)
    if valor is None or valor == "":
        return padrao
    return str(valor)


def gerar_passagem_caso_local(dados: Dict[str, Any]) -> str:
    """Gera passagem de caso objetiva sem depender de API externa."""
    crianca = dados.get("crianca", {}) or {}
    nascimento = dados.get("nascimento", {}) or {}
    medidas = dados.get("medidas", {}) or {}
    crescimento = dados.get("crescimento", {}) or {}
    vacinas = dados.get("vacinas", {}) or {}
    suplementacao = dados.get("suplementacao", {}) or {}
    desenvolvimento = dados.get("desenvolvimento", {}) or {}
    amb = dados.get("ambulatorio", {}) or {}

    linhas = []
    linhas.append("PASSAGEM DE CASO — PUERICULTURA")
    linhas.append("")
    linhas.append(
        "Identificação: criança do sexo "
        f"{_valor(crianca, 'sexo')}, nascida em {_valor(crianca, 'data_nascimento')}, "
        f"avaliada em {_valor(crianca, 'data_consulta')}."
    )
    linhas.append(
        f"Idade: cronológica {_valor(crianca, 'idade_cronologica')}; "
        f"corrigida {_valor(crianca, 'idade_corrigida')}."
    )
    linhas.append(
        f"Nascimento: IG {_valor(nascimento, 'ig')}, PN {_valor(nascimento, 'peso_nascimento')}, "
        f"classificação {_valor(nascimento, 'classificacao')}."
    )
    linhas.append(
        f"Medidas atuais: peso {_valor(medidas, 'peso')}, "
        f"estatura/comprimento {_valor(medidas, 'estatura')}, "
        f"PC {_valor(medidas, 'pc')}, IMC {_valor(medidas, 'imc')}."
    )

    if crescimento:
        linhas.append(f"Crescimento: {_valor(crescimento, 'resumo', 'sem síntese registrada')}.")
    if desenvolvimento:
        linhas.append(f"Desenvolvimento: {_valor(desenvolvimento, 'resumo', 'sem síntese registrada')}.")
    if vacinas:
        linhas.append(
            f"Imunizações: pendências — {_valor(vacinas, 'atrasadas', 'nenhuma informada')}; "
            f"próximas — {_valor(vacinas, 'proximas', 'não informado')}."
        )
    if suplementacao:
        linhas.append(f"Suplementação: {_valor(suplementacao, 'resumo', 'sem síntese registrada')}.")
    if amb:
        linhas.append(
            f"Queixa/protocolo ambulatorial: {_valor(amb, 'protocolo')}. "
            f"Classificação: {_valor(amb, 'classificacao')}. "
            f"Conduta sugerida: {_valor(amb, 'conduta_resumo')}."
        )

    pontos = dados.get("pontos_atencao", []) or [
        "Conferir caderneta, evolução ponderoestatural, desenvolvimento, suplementação e retorno conforme achados clínicos."
    ]
    linhas.append("")
    linhas.append("Pontos de atenção para seguimento:")
    for item in pontos:
        linhas.append(f"- {item}")

    linhas.append("")
    linhas.append(
        "Observação: modelo de apoio para passagem de caso; revisar e ajustar conforme exame físico, "
        "contexto clínico e julgamento profissional."
    )
    return "\n".join(linhas)


def _montar_prompt_passagem(dados: Dict[str, Any]) -> str:
    return (
        "Gere uma passagem de caso pediátrica simples, correta e objetiva, em português do Brasil. "
        "Use SOMENTE os dados fornecidos. Não invente diagnósticos, medicamentos, doses, exames ou achados. "
        "Quando alguma informação estiver ausente, escreva 'não informado' ou omita o item, sem supor. "
        "Estruture em tópicos curtos com estes títulos: Identificação; Dados perinatais; Medidas atuais; "
        "Crescimento e desenvolvimento; Imunizações e suplementação; Queixa/protocolo ambulatorial se houver; "
        "Pendências; Plano de seguimento. "
        "Finalize exatamente com: 'Revisar conforme exame físico e julgamento clínico'.\n\n"
        f"DADOS ESTRUTURADOS:\n{dados}"
    )


def _gerar_com_gemini(prompt: str) -> Tuple[Optional[str], Optional[str]]:
    """Retorna (texto, erro)."""
    api_key = _secret("GEMINI_API_KEY")
    model = _secret("GEMINI_MODEL", "gemini-2.5-flash") or "gemini-2.5-flash"

    if not api_key:
        return None, "GEMINI_API_KEY não configurada nos Secrets."

    try:
        from google import genai  # type: ignore

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
        texto = getattr(response, "text", None)
        if texto and str(texto).strip():
            return str(texto).strip(), None
        return None, "Gemini retornou resposta vazia."
    except Exception as exc:
        return None, str(exc)


def _gerar_com_openai(prompt: str, api_key: Optional[str] = None, model: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
    """Retorna (texto, erro)."""
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
                {
                    "role": "system",
                    "content": (
                        "Você é um assistente de documentação clínica pediátrica. "
                        "Você não substitui julgamento profissional."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        texto = resp.choices[0].message.content
        if texto and texto.strip():
            return texto.strip(), None
        return None, "OpenAI retornou resposta vazia."
    except Exception as exc:
        return None, str(exc)


def gerar_passagem_caso_ia(
    dados: Dict[str, Any],
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    mostrar_erro: bool = True,
) -> str:
    """
    Gera passagem de caso usando IA configurada no Streamlit Secrets.

    Compatível com app.py antigo que chama:
        gerar_passagem_caso_ia(dados, api_key=api_key)

    Regras:
    - IA_PROVIDER='gemini': usa Gemini.
    - IA_PROVIDER='openai': usa OpenAI.
    - IA_PROVIDER ausente e api_key informado: usa OpenAI por compatibilidade.
    - Qualquer falha: usa versão local e mostra detalhe técnico no final.
    """
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


# Aliases opcionais para compatibilidade com nomes diferentes em versões futuras/antigas.
def gerar_passagem_de_caso_local(dados: Dict[str, Any]) -> str:
    return gerar_passagem_caso_local(dados)


def gerar_passagem_de_caso_ia(dados: Dict[str, Any], api_key: Optional[str] = None, model: Optional[str] = None) -> str:
    return gerar_passagem_caso_ia(dados, api_key=api_key, model=model)
