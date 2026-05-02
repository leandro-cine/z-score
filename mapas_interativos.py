from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import streamlit as st
from PIL import Image, ImageDraw

try:
    from streamlit_image_coordinates import streamlit_image_coordinates
except Exception:
    streamlit_image_coordinates = None


def _asset_dir() -> Path:
    candidates = [
        Path.cwd() / "assets" / "mapas",
        Path(__file__).resolve().parent / "assets" / "mapas",
        Path("/mnt/data/assets/mapas"),
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[0]

ASSETS_MAPAS = _asset_dir()

# Áreas em coordenadas relativas (x1, y1, x2, y2). Ajustáveis conforme a imagem final.
AREAS_LINFONODOS_BEBE = [
    {"nome": "Submentonianos", "box": (0.03, 0.61, 0.22, 0.72)},
    {"nome": "Submandibulares", "box": (0.13, 0.70, 0.34, 0.83)},
    {"nome": "Cervicais anteriores superficiais", "box": (0.39, 0.55, 0.58, 0.70)},
    {"nome": "Cervicais anteriores profundos", "box": (0.39, 0.68, 0.60, 0.84)},
    {"nome": "Supraclaviculares", "box": (0.45, 0.82, 0.64, 0.96)},
    {"nome": "Retroauriculares", "box": (0.78, 0.38, 0.96, 0.52)},
    {"nome": "Occipitais", "box": (0.80, 0.27, 0.98, 0.40)},
    {"nome": "Cervicais posteriores", "box": (0.78, 0.53, 0.98, 0.75)},
]

AREAS_LINFONODOS_CRIANCA = [
    {"nome": "Submentonianos", "box": (0.03, 0.61, 0.22, 0.73)},
    {"nome": "Submandibulares", "box": (0.13, 0.70, 0.34, 0.83)},
    {"nome": "Cervicais anteriores superficiais", "box": (0.39, 0.55, 0.58, 0.70)},
    {"nome": "Cervicais anteriores profundos", "box": (0.39, 0.68, 0.60, 0.84)},
    {"nome": "Supraclaviculares", "box": (0.45, 0.82, 0.64, 0.96)},
    {"nome": "Retroauriculares", "box": (0.78, 0.38, 0.96, 0.52)},
    {"nome": "Occipitais", "box": (0.80, 0.27, 0.98, 0.40)},
    {"nome": "Cervicais posteriores", "box": (0.78, 0.53, 0.98, 0.75)},
]

AREAS_ODONTOGRAMA = [
    {"nome": "Decídua — incisivos superiores", "box": (0.23, 0.20, 0.39, 0.35)},
    {"nome": "Decídua — caninos superiores", "box": (0.16, 0.27, 0.46, 0.42)},
    {"nome": "Decídua — molares superiores", "box": (0.08, 0.35, 0.50, 0.52)},
    {"nome": "Decídua — incisivos inferiores", "box": (0.23, 0.73, 0.40, 0.86)},
    {"nome": "Decídua — caninos inferiores", "box": (0.16, 0.66, 0.46, 0.84)},
    {"nome": "Decídua — molares inferiores", "box": (0.07, 0.54, 0.50, 0.77)},
    {"nome": "Permanente — incisivos superiores", "box": (0.58, 0.15, 0.78, 0.31)},
    {"nome": "Permanente — caninos superiores", "box": (0.55, 0.20, 0.86, 0.35)},
    {"nome": "Permanente — pré-molares superiores", "box": (0.52, 0.30, 0.90, 0.47)},
    {"nome": "Permanente — molares superiores", "box": (0.50, 0.40, 0.92, 0.58)},
    {"nome": "Permanente — incisivos inferiores", "box": (0.62, 0.72, 0.80, 0.86)},
    {"nome": "Permanente — caninos inferiores", "box": (0.56, 0.68, 0.87, 0.84)},
    {"nome": "Permanente — pré-molares inferiores", "box": (0.52, 0.55, 0.90, 0.75)},
    {"nome": "Permanente — molares inferiores", "box": (0.50, 0.44, 0.92, 0.64)},
]


def _resolver_path(nome: str) -> Path:
    primary = ASSETS_MAPAS / nome
    if primary.exists():
        return primary
    # fallback para nomes originais quando o usuário ainda não renomeou
    fallbacks = {
        "linfonodos_bebe.png": ["Gemini_Generated_Image_bojf8kbojf8kbojf.png"],
        "linfonodos_crianca.png": ["Gemini_Generated_Image_dl29vydl29vydl29.png"],
        "odontograma.png": ["Gemini_Generated_Image_dtaa23dtaa23dtaa.png"],
    }
    roots = [Path.cwd(), Path(__file__).resolve().parent, Path("/mnt/data")]
    for fname in fallbacks.get(nome, []):
        for root in roots:
            p = root / fname
            if p.exists():
                return p
    return primary


def _abrir_imagem(path: Path, largura_maxima: int = 1100) -> Image.Image:
    img = Image.open(path).convert("RGB")
    w, h = img.size
    if w > largura_maxima:
        fator = largura_maxima / w
        img = img.resize((largura_maxima, int(h * fator)))
    return img


def _desenhar_marcadores(img: Image.Image, areas: List[Dict], selecionadas: List[str]) -> Image.Image:
    # Não desenha retângulos grandes: preserva a imagem anatômica.
    out = img.copy().convert("RGBA")
    draw = ImageDraw.Draw(out, "RGBA")
    w, h = out.size
    for idx, area in enumerate(areas, start=1):
        x1, y1, x2, y2 = area["box"]
        cx = int(((x1 + x2) / 2) * w)
        cy = int(((y1 + y2) / 2) * h)
        selected = area["nome"] in selecionadas
        fill = (13, 148, 136, 235) if selected else (37, 99, 235, 210)
        outline = (255, 255, 255, 255)
        r = 15 if selected else 12
        draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=fill, outline=outline, width=2)
        draw.text((cx-(4 if idx<10 else 7), cy-7), str(idx), fill=(255,255,255,255))
    return out.convert("RGB")


def _area_do_click(value: Optional[Dict], img: Image.Image, areas: List[Dict]) -> Optional[str]:
    if not value:
        return None
    x, y = value.get("x"), value.get("y")
    if x is None or y is None:
        return None
    w, h = img.size
    nx, ny = x / w, y / h
    for area in areas:
        x1, y1, x2, y2 = area["box"]
        if x1 <= nx <= x2 and y1 <= ny <= y2:
            return area["nome"]
    return None


def _render_mapa(titulo: str, nome_imagem: str, areas: List[Dict], key: str):
    st.markdown(f"#### {titulo}")
    if key not in st.session_state:
        st.session_state[key] = []
    selecionadas = st.session_state[key]

    path = _resolver_path(nome_imagem)
    if not path.exists():
        st.warning(
            f"Imagem não encontrada: `{nome_imagem}`. Envie para `assets/mapas/` ou use o ZIP completo com as imagens."
        )
        escolhidas = st.multiselect("Selecionar áreas manualmente", [a["nome"] for a in areas], default=selecionadas, key=f"fallback_{key}")
        st.session_state[key] = escolhidas
        return escolhidas

    img = _abrir_imagem(path)
    img_click = _desenhar_marcadores(img, areas, selecionadas)

    if streamlit_image_coordinates is None:
        st.image(img_click, use_container_width=True)
        st.info("Para clicar diretamente na imagem, adicione `streamlit-image-coordinates` ao requirements.txt. Enquanto isso, use a seleção manual.")
        escolhidas = st.multiselect("Selecionar áreas", [a["nome"] for a in areas], default=selecionadas, key=f"fallback_{key}")
        st.session_state[key] = escolhidas
    else:
        value = streamlit_image_coordinates(img_click, key=f"coords_{key}", use_column_width=True)
        clicada = _area_do_click(value, img_click, areas)
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
        st.caption("Clique na região anatômica da imagem ou use a seleção manual se necessário.")
    return resultado


def selecionar_linfodos_por_imagem(tipo: str = "criança", key_suffix: str = ""):
    tipo = (tipo or "criança").lower()
    key = f"mapa_linfodos_bebe_{key_suffix}" if tipo.startswith("beb") else f"mapa_linfodos_crianca_{key_suffix}"
    if tipo.startswith("beb"):
        return _render_mapa("Mapa anatômico — linfonodos em bebê", "linfonodos_bebe.png", AREAS_LINFONODOS_BEBE, key)
    return _render_mapa("Mapa anatômico — linfonodos em criança", "linfonodos_crianca.png", AREAS_LINFONODOS_CRIANCA, key)


def selecionar_odontograma_por_imagem(key_suffix: str = ""):
    return _render_mapa("Mapa dentário — dentição decídua e permanente", "odontograma.png", AREAS_ODONTOGRAMA, f"mapa_odontograma_{key_suffix}")
