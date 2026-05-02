from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import streamlit as st
from PIL import Image, ImageDraw

try:
    from streamlit_image_coordinates import streamlit_image_coordinates
except Exception:  # O app continua funcionando, mas sem clique direto na imagem.
    streamlit_image_coordinates = None


ASSETS_MAPAS = Path("assets/mapas")


AREAS_LINFONODOS_BEBE = [
    {"nome": "Submentonianos", "box": (0.05, 0.62, 0.18, 0.74)},
    {"nome": "Submandibulares", "box": (0.17, 0.68, 0.32, 0.82)},
    {"nome": "Cervicais anteriores superficiais", "box": (0.33, 0.54, 0.52, 0.70)},
    {"nome": "Cervicais anteriores profundos", "box": (0.35, 0.67, 0.56, 0.83)},
    {"nome": "Supraclaviculares", "box": (0.41, 0.82, 0.58, 0.95)},
    {"nome": "Retroauriculares", "box": (0.31, 0.40, 0.44, 0.55)},
    {"nome": "Occipitais", "box": (0.37, 0.29, 0.54, 0.44)},
    {"nome": "Cervicais posteriores", "box": (0.50, 0.53, 0.66, 0.79)},
]

AREAS_LINFONODOS_CRIANCA = [
    {"nome": "Submentonianos", "box": (0.05, 0.61, 0.20, 0.74)},
    {"nome": "Submandibulares", "box": (0.17, 0.68, 0.33, 0.82)},
    {"nome": "Cervicais anteriores superficiais", "box": (0.33, 0.53, 0.53, 0.70)},
    {"nome": "Cervicais anteriores profundos", "box": (0.35, 0.67, 0.56, 0.83)},
    {"nome": "Supraclaviculares", "box": (0.41, 0.82, 0.58, 0.95)},
    {"nome": "Retroauriculares", "box": (0.31, 0.39, 0.44, 0.53)},
    {"nome": "Occipitais", "box": (0.36, 0.28, 0.54, 0.43)},
    {"nome": "Cervicais posteriores", "box": (0.49, 0.52, 0.66, 0.79)},
]

AREAS_ODONTOGRAMA = [
    {"nome": "Decídua — incisivos superiores", "box": (0.23, 0.21, 0.37, 0.35)},
    {"nome": "Decídua — caninos superiores", "box": (0.17, 0.28, 0.43, 0.42)},
    {"nome": "Decídua — molares superiores", "box": (0.08, 0.35, 0.49, 0.52)},
    {"nome": "Decídua — incisivos inferiores", "box": (0.24, 0.72, 0.38, 0.86)},
    {"nome": "Decídua — caninos inferiores", "box": (0.17, 0.67, 0.45, 0.84)},
    {"nome": "Decídua — molares inferiores", "box": (0.07, 0.55, 0.49, 0.76)},
    {"nome": "Permanente — incisivos superiores", "box": (0.60, 0.16, 0.78, 0.31)},
    {"nome": "Permanente — caninos superiores", "box": (0.56, 0.20, 0.84, 0.35)},
    {"nome": "Permanente — pré-molares superiores", "box": (0.53, 0.30, 0.88, 0.47)},
    {"nome": "Permanente — molares superiores", "box": (0.51, 0.41, 0.91, 0.58)},
    {"nome": "Permanente — incisivos inferiores", "box": (0.64, 0.72, 0.78, 0.86)},
    {"nome": "Permanente — caninos inferiores", "box": (0.57, 0.68, 0.85, 0.84)},
    {"nome": "Permanente — pré-molares inferiores", "box": (0.53, 0.55, 0.89, 0.75)},
    {"nome": "Permanente — molares inferiores", "box": (0.51, 0.44, 0.91, 0.64)},
]


def _abrir_imagem(path: Path, largura_maxima: int = 1100) -> Image.Image:
    img = Image.open(path).convert("RGBA")
    w, h = img.size
    if w > largura_maxima:
        fator = largura_maxima / w
        img = img.resize((largura_maxima, int(h * fator)))
    return img


def _desenhar_areas(img: Image.Image, areas: List[Dict], selecionadas: List[str]) -> Image.Image:
    overlay = img.copy()
    draw = ImageDraw.Draw(overlay, "RGBA")
    w, h = img.size
    for area in areas:
        x1, y1, x2, y2 = area["box"]
        box = (int(x1 * w), int(y1 * h), int(x2 * w), int(y2 * h))
        if area["nome"] in selecionadas:
            fill = (20, 184, 166, 95)
            outline = (45, 212, 191, 255)
            width = 4
        else:
            fill = (59, 130, 246, 32)
            outline = (147, 197, 253, 210)
            width = 2
        draw.rounded_rectangle(box, radius=12, fill=fill, outline=outline, width=width)
    return overlay


def _area_do_click(value: Optional[Dict], img: Image.Image, areas: List[Dict]) -> Optional[str]:
    if not value:
        return None
    x = value.get("x")
    y = value.get("y")
    if x is None or y is None:
        return None
    w, h = img.size
    nx, ny = x / w, y / h
    for area in areas:
        x1, y1, x2, y2 = area["box"]
        if x1 <= nx <= x2 and y1 <= ny <= y2:
            return area["nome"]
    return None


def _render_mapa(titulo: str, path: Path, areas: List[Dict], key: str):
    st.markdown(f"#### {titulo}")
    if key not in st.session_state:
        st.session_state[key] = []
    selecionadas = st.session_state[key]

    if not path.exists():
        st.warning(f"Imagem não encontrada: `{path}`. Crie a pasta `assets/mapas/` e envie a imagem com esse nome.")
        return selecionadas

    img = _abrir_imagem(path)
    img_overlay = _desenhar_areas(img, areas, selecionadas)

    if streamlit_image_coordinates is None:
        st.image(img_overlay, use_container_width=True)
        st.info("Para clicar diretamente na imagem, adicione `streamlit-image-coordinates` ao requirements.txt. Enquanto isso, use a seleção abaixo.")
        escolhidas = st.multiselect("Selecionar áreas", [a["nome"] for a in areas], default=selecionadas, key=f"fallback_{key}")
        st.session_state[key] = escolhidas
    else:
        value = streamlit_image_coordinates(img_overlay, key=f"coords_{key}", use_column_width=True)
        clicada = _area_do_click(value, img_overlay, areas)
        if clicada:
            if clicada in st.session_state[key]:
                st.session_state[key].remove(clicada)
            else:
                st.session_state[key].append(clicada)
            st.rerun()

    outra = st.text_input("Outra área/alteração não listada", key=f"outra_{key}", placeholder="Descreva se não estiver no mapa")
    resultado = list(st.session_state[key])
    if outra.strip():
        resultado.append(outra.strip())

    if resultado:
        st.success("Selecionado: " + "; ".join(resultado))
    else:
        st.caption("Clique nas áreas destacadas ou selecione na lista alternativa.")
    return resultado


def selecionar_linfodos_por_imagem(tipo: str = "criança"):
    tipo = (tipo or "criança").lower()
    if tipo.startswith("beb"):
        return _render_mapa("Mapa anatômico — linfonodos em bebê", ASSETS_MAPAS / "linfonodos_bebe.png", AREAS_LINFONODOS_BEBE, "mapa_linfodos_bebe")
    return _render_mapa("Mapa anatômico — linfonodos em criança", ASSETS_MAPAS / "linfonodos_crianca.png", AREAS_LINFONODOS_CRIANCA, "mapa_linfodos_crianca")


def selecionar_odontograma_por_imagem():
    return _render_mapa("Mapa dentário — dentição decídua e permanente", ASSETS_MAPAS / "odontograma.png", AREAS_ODONTOGRAMA, "mapa_odontograma")
