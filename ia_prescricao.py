from __future__ import annotations

from typing import Any, Dict, Optional


def gerar_passagem_caso_local(dados: Dict[str, Any]) -> str:
    """Gera passagem de caso objetiva sem depender de API externa."""
    crianca = dados.get("crianca", {})
    nascimento = dados.get("nascimento", {})
    medidas = dados.get("medidas", {})
    crescimento = dados.get("crescimento", {})
    vacinas = dados.get("vacinas", {})
    suplementacao = dados.get("suplementacao", {})
    desenvolvimento = dados.get("desenvolvimento", {})
    amb = dados.get("ambulatorio", {})

    linhas = []
    linhas.append("PASSAGEM DE CASO — PUERICULTURA")
    linhas.append("")
    linhas.append(f"Identificação: criança do sexo {crianca.get('sexo','—')}, nascida em {crianca.get('data_nascimento','—')}, avaliada em {crianca.get('data_consulta','—')}.")
    linhas.append(f"Idade: cronológica {crianca.get('idade_cronologica','—')}; corrigida {crianca.get('idade_corrigida','—')}.")
    linhas.append(f"Nascimento: IG {nascimento.get('ig','—')}, PN {nascimento.get('peso_nascimento','—')}, classificação {nascimento.get('classificacao','—')}.")
    linhas.append(f"Medidas atuais: peso {medidas.get('peso','—')}, estatura/comprimento {medidas.get('estatura','—')}, PC {medidas.get('pc','—')}, IMC {medidas.get('imc','—')}.")
    if crescimento:
        linhas.append(f"Crescimento: {crescimento.get('resumo','sem síntese registrada')}.")
    if desenvolvimento:
        linhas.append(f"Desenvolvimento: {desenvolvimento.get('resumo','sem síntese registrada')}.")
    if vacinas:
        linhas.append(f"Imunizações: pendências — {vacinas.get('atrasadas','nenhuma informada')}; próximas — {vacinas.get('proximas','não informado')}.")
    if suplementacao:
        linhas.append(f"Suplementação: {suplementacao.get('resumo','sem síntese registrada')}.")
    if amb:
        linhas.append(f"Queixa/protocolo ambulatorial: {amb.get('protocolo','—')}. Classificação: {amb.get('classificacao','—')}. Conduta sugerida: {amb.get('conduta_resumo','—')}.")
    linhas.append("")
    linhas.append("Pontos de atenção para seguimento:")
    for item in dados.get("pontos_atencao", []) or ["Conferir caderneta, evolução ponderoestatural, desenvolvimento, suplementação e retorno conforme achados clínicos."]:
        linhas.append(f"- {item}")
    linhas.append("")
    linhas.append("Observação: modelo de apoio para passagem de caso; revisar e ajustar conforme exame físico, contexto clínico e julgamento profissional.")
    return "\n".join(linhas)


def gerar_passagem_caso_ia(dados: Dict[str, Any], api_key: Optional[str] = None, model: str = "gpt-4o-mini") -> str:
    """
    Usa IA apenas como redatora, sem extrapolar os dados enviados.
    Se não houver API/chave/biblioteca, retorna versão local.
    """
    if not api_key:
        return gerar_passagem_caso_local(dados)

    try:
        from openai import OpenAI  # type: ignore
        client = OpenAI(api_key=api_key)
        prompt = (
            "Gere uma passagem de caso pediátrica simples, correta e objetiva, em português do Brasil. "
            "Use somente os dados fornecidos. Não invente diagnósticos, medicamentos, doses ou achados. "
            "Estruture em: Identificação, dados perinatais, medidas atuais, crescimento/desenvolvimento, "
            "imunizações/suplementação, queixa/conduta ambulatorial se houver, pendências e plano de seguimento. "
            "Finalize com a frase: 'Revisar conforme exame físico e julgamento clínico'.\n\n"
            f"DADOS ESTRUTURADOS:\n{dados}"
        )
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Você é um assistente de documentação clínica pediátrica. Não substitui julgamento profissional."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content or gerar_passagem_caso_local(dados)
    except Exception as exc:
        return gerar_passagem_caso_local(dados) + f"\n\n[IA indisponível: foi usada a versão local. Detalhe técnico: {exc}]"
