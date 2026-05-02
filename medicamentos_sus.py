from __future__ import annotations

# Base local de apoio extraída/estruturada a partir das listas SUS enviadas (RENAME/REMUME).
# Serve para seleção de princípio ativo, apresentação e via. A tela sinaliza apenas "SUS" para simplificar.
# Para ampliar, acrescente novas apresentações em MEDICAMENTOS_SUS mantendo a ordem alfabética.

MEDICAMENTOS_SUS = {
    "Aciclovir": {"apresentacoes":[{"texto":"200 mg — comprimido", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Ácido acetilsalicílico": {"apresentacoes":[{"texto":"100 mg — comprimido", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Ácido fólico": {"apresentacoes":[{"texto":"5 mg — comprimido", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Ácido valproico": {"apresentacoes":[{"texto":"50 mg/mL — solução oral/xarope", "via":"oral"},{"texto":"500 mg — comprimido", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Albendazol": {"apresentacoes":[{"texto":"40 mg/mL — suspensão oral", "via":"oral"},{"texto":"400 mg — comprimido", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Alopurinol": {"apresentacoes":[{"texto":"100 mg — comprimido", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Amoxicilina": {"apresentacoes":[{"texto":"50 mg/mL — suspensão oral", "via":"oral"},{"texto":"500 mg — cápsula/comprimido", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Amoxicilina + clavulanato de potássio": {"apresentacoes":[{"texto":"50 mg + 12,5 mg/mL — suspensão oral", "via":"oral"},{"texto":"500 mg + 125 mg — comprimido", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Azitromicina": {"apresentacoes":[{"texto":"40 mg/mL — suspensão oral", "via":"oral"},{"texto":"500 mg — comprimido", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Beclometasona": {"apresentacoes":[{"texto":"50 mcg/dose — aerossol", "via":"inalatória"},{"texto":"200 mcg/dose — aerossol", "via":"inalatória"}], "rename": True, "remume_pmvc": True},
    "Benzilpenicilina benzatina": {"apresentacoes":[{"texto":"1.200.000 UI — frasco-ampola", "via":"intramuscular"}], "rename": True, "remume_pmvc": True},
    "Budesonida": {"apresentacoes":[{"texto":"50 mcg/dose (equivale a 32 mcg) — aerossol/spray", "via":"inalatória/nasal"}], "rename": True, "remume_pmvc": True},
    "Carbamazepina": {"apresentacoes":[{"texto":"20 mg/mL — solução oral/xarope", "via":"oral"},{"texto":"200 mg — comprimido", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Carbonato de cálcio + colecalciferol": {"apresentacoes":[{"texto":"500 mg Ca elementar + 400 UI — comprimido", "via":"oral"},{"texto":"600 mg Ca elementar + 400 UI — comprimido", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Cefalexina": {"apresentacoes":[{"texto":"50 mg/mL — suspensão oral", "via":"oral"},{"texto":"500 mg — comprimido/cápsula", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Ciprofloxacino": {"apresentacoes":[{"texto":"500 mg — comprimido", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Clonazepam": {"apresentacoes":[{"texto":"2 mg — comprimido", "via":"oral"},{"texto":"2,5 mg/mL — solução oral/gotas", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Colecalciferol": {"apresentacoes":[{"texto":"gotas — concentração variável conforme produto", "via":"oral"},{"texto":"associado a cálcio em comprimido", "via":"oral"}], "rename": True, "remume_pmvc": False},
    "Dexametasona": {"apresentacoes":[{"texto":"1 mg/g — creme", "via":"tópica"}], "rename": True, "remume_pmvc": True},
    "Dexclorfeniramina": {"apresentacoes":[{"texto":"0,4 mg/mL — solução oral/xarope", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Diazepam": {"apresentacoes":[{"texto":"5 mg — comprimido", "via":"oral"},{"texto":"10 mg — comprimido", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Dimenidrinato + vitamina B6": {"apresentacoes":[{"texto":"100 mg + vitamina B6 — comprimido", "via":"oral"}], "rename": False, "remume_pmvc": True},
    "Dipirona": {"apresentacoes":[{"texto":"500 mg/mL — solução oral/gotas", "via":"oral"},{"texto":"500 mg — comprimido", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Fenoterol": {"apresentacoes":[{"texto":"5 mg/mL — solução para inalação", "via":"inalatória/nebulização"}], "rename": True, "remume_pmvc": True},
    "Fenoximetilpenicilina": {"apresentacoes":[{"texto":"80.000 UI/mL — solução oral", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Fluconazol": {"apresentacoes":[{"texto":"150 mg — comprimido/cápsula", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Glicerol": {"apresentacoes":[{"texto":"120 mg/mL — solução retal", "via":"retal"},{"texto":"72 mg — supositório retal", "via":"retal"}], "rename": True, "remume_pmvc": False},
    "Hidróxido de alumínio": {"apresentacoes":[{"texto":"60 mg/mL — suspensão oral", "via":"oral"},{"texto":"230 mg — comprimido", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Ibuprofeno": {"apresentacoes":[{"texto":"50 mg/mL — solução oral/gotas", "via":"oral"},{"texto":"600 mg — comprimido", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Ipratrópio": {"apresentacoes":[{"texto":"0,25 mg/mL — solução para inalação", "via":"inalatória/nebulização"}], "rename": True, "remume_pmvc": True},
    "Ivermectina": {"apresentacoes":[{"texto":"6 mg — comprimido", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Lactulose": {"apresentacoes":[{"texto":"667 mg/mL — solução oral/xarope", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Loratadina": {"apresentacoes":[{"texto":"1 mg/mL — solução oral/xarope", "via":"oral"},{"texto":"10 mg — comprimido", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Metoclopramida": {"apresentacoes":[{"texto":"4 mg/mL — solução oral", "via":"oral"},{"texto":"10 mg — comprimido", "via":"oral"},{"texto":"5 mg/mL — solução injetável", "via":"intramuscular/endovenosa"}], "rename": True, "remume_pmvc": False},
    "Metronidazol": {"apresentacoes":[{"texto":"40 mg/mL — suspensão oral", "via":"oral"},{"texto":"250 mg — comprimido", "via":"oral"},{"texto":"100 mg/g — creme vaginal", "via":"vaginal"}], "rename": True, "remume_pmvc": True},
    "Mikania glomerata (guaco)": {"apresentacoes":[{"texto":"116 mg/mL — solução oral/xarope", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Neomicina + bacitracina": {"apresentacoes":[{"texto":"5 mg + 250 UI/g — pomada", "via":"tópica"}], "rename": True, "remume_pmvc": True},
    "Nistatina": {"apresentacoes":[{"texto":"100.000 UI/mL — solução oral", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Omeprazol": {"apresentacoes":[{"texto":"20 mg — cápsula", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Ondansetrona": {"apresentacoes":[{"texto":"4 mg — comprimido", "via":"oral"},{"texto":"4 mg — comprimido orodispersível", "via":"oral"},{"texto":"8 mg — comprimido", "via":"oral"},{"texto":"8 mg — comprimido orodispersível", "via":"oral"}], "rename": True, "remume_pmvc": False},
    "Oseltamivir": {"apresentacoes":[{"texto":"30 mg — cápsula/comprimido", "via":"oral"},{"texto":"45 mg — cápsula/comprimido", "via":"oral"},{"texto":"75 mg — cápsula/comprimido", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Óxido de zinco + vitaminas A e D": {"apresentacoes":[{"texto":"pomada", "via":"tópica"}], "rename": False, "remume_pmvc": True},
    "Paracetamol": {"apresentacoes":[{"texto":"200 mg/mL — solução oral/gotas", "via":"oral"},{"texto":"500 mg — comprimido", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Permetrina": {"apresentacoes":[{"texto":"10 mg/mL — creme capilar/loção", "via":"tópica"}], "rename": True, "remume_pmvc": True},
    "Praziquantel": {"apresentacoes":[{"texto":"600 mg — comprimido", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Prednisolona": {"apresentacoes":[{"texto":"3 mg/mL — solução oral/xarope", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Prednisona": {"apresentacoes":[{"texto":"5 mg — comprimido", "via":"oral"},{"texto":"20 mg — comprimido", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Prometazina": {"apresentacoes":[{"texto":"25 mg — comprimido", "via":"oral"},{"texto":"25 mg/mL — solução injetável", "via":"intramuscular/endovenosa"}], "rename": True, "remume_pmvc": True},
    "Sais de reidratação oral": {"apresentacoes":[{"texto":"pó para solução oral", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Salbutamol": {"apresentacoes":[{"texto":"120,5 mcg/dose (equivale a 100 mcg) — aerossol", "via":"inalatória"}], "rename": True, "remume_pmvc": True},
    "Sulfametoxazol + trimetoprima": {"apresentacoes":[{"texto":"40 mg/mL + 8 mg/mL — solução oral/xarope", "via":"oral"},{"texto":"400 mg + 80 mg — comprimido", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Sulfato ferroso": {"apresentacoes":[{"texto":"25 mg/mL — solução oral/gotas", "via":"oral"},{"texto":"40 mg — comprimido", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Tiamina": {"apresentacoes":[{"texto":"300 mg — comprimido", "via":"oral"}], "rename": True, "remume_pmvc": True},
    "Vitaminas do complexo B": {"apresentacoes":[{"texto":"comprimido", "via":"oral"}], "rename": False, "remume_pmvc": True},
}


def listar_principios_ativos():
    return sorted(MEDICAMENTOS_SUS.keys(), key=lambda x: x.lower()) + ["Outro/não listado"]


def obter_apresentacoes(principio: str):
    return MEDICAMENTOS_SUS.get(principio, {}).get("apresentacoes", [])


def checar_medicamento(principio: str):
    dado = MEDICAMENTOS_SUS.get(principio, {})
    sus = bool(dado.get("rename") or dado.get("remume_pmvc"))
    return {"sus": sus, "apresentacoes": [a["texto"] for a in dado.get("apresentacoes", [])]}
