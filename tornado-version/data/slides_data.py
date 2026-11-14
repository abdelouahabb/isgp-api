"""
Assembleur du support de présentation (Slides) — Édition Python Tornado & Ingénierie des APIs.
Combine SLIDES_PART_A (Parties 0 à 4) et SLIDES_PART_B (Parties 5 à 8) en un jeu complet numéroté.
"""

from __future__ import annotations

try:
    from .slides_part_a import SLIDES_PART_A
except ImportError:
    from slides_part_a import SLIDES_PART_A  # type: ignore

try:
    from .slides_part_b import SLIDES_PART_B
except ImportError:
    from slides_part_b import SLIDES_PART_B  # type: ignore


DECK_META = {
    "title": "Ingénierie des APIs Web & Sites Dynamiques avec Python Tornado",
    "subtitle": "Support de Présentation Complet — Des Fondations HTTP & REST au Portail de Production",
    "institution": "Institut Supérieur de Gestion et de Planification (ISGP)",
    "framework": "tornado",
    "edition": "Volume III — Python Tornado (Event-Loop IOLoop & RequestHandler)",
}


def get_tornado_slides_deck() -> dict:
    raw_slides = list(SLIDES_PART_A) + list(SLIDES_PART_B)
    slides = []
    parts_index: dict[str, dict] = {}

    for idx, item in enumerate(raw_slides, start=1):
        part_id = item.get("part_id", "P0")
        part_title = item.get("part_title", "Présentation")
        slide = {
            "number": idx,
            "part_id": part_id,
            "part_title": part_title,
            "tag": item.get("tag", "Concept"),
            "title": item.get("title", ""),
            "subtitle": item.get("subtitle", ""),
            "definition": item.get("definition", ""),
            "points": item.get("points", []),
            "comparison": item.get("comparison") or None,
            "code_label": item.get("code_label", ""),
            "code_lang": item.get("code_lang", ""),
            "code": (item.get("code") or "").strip("\n"),
            "takeaway": item.get("takeaway", ""),
        }
        slides.append(slide)

        if part_id not in parts_index:
            parts_index[part_id] = {
                "part_id": part_id,
                "part_title": part_title,
                "first_slide": idx,
                "last_slide": idx,
                "count": 0,
            }
        parts_index[part_id]["last_slide"] = idx
        parts_index[part_id]["count"] += 1

    return {
        "meta": {**DECK_META, "total_slides": len(slides)},
        "parts": list(parts_index.values()),
        "slides": slides,
    }
