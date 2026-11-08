"""
Agrégation des modules pédagogiques structurés par dossier :
day_0/, day_1/, day_2/, day_3/, day_4/, day_5/
et fusion avec le Manuel de Référence Approfondi (enrichment_d0_d1, enrichment_d2_d3, enrichment_d4_d5).
"""

from day_0.lesson_data import DAY_0_DATA
from day_1.lesson_data import DAY_1_DATA
from day_2.lesson_data import DAY_2_DATA
from day_3.lesson_data import DAY_3_DATA
from day_4.lesson_data import DAY_4_DATA
from day_5.lesson_data import DAY_5_DATA

from data.enrichment_d0_d1 import ENRICHMENT_D0_D1
from data.enrichment_d2_d3 import ENRICHMENT_D2_D3
from data.enrichment_d4_d5 import ENRICHMENT_D4_D5

ALL_ENRICHMENTS = {}
ALL_ENRICHMENTS.update(ENRICHMENT_D0_D1)
ALL_ENRICHMENTS.update(ENRICHMENT_D2_D3)
ALL_ENRICHMENTS.update(ENRICHMENT_D4_D5)

DAYS_CURRICULUM = [
    DAY_0_DATA,
    DAY_1_DATA,
    DAY_2_DATA,
    DAY_3_DATA,
    DAY_4_DATA,
    DAY_5_DATA,
]

for _day in DAYS_CURRICULUM:
    for _lesson in _day.get("lessons", []):
        _enrichment = ALL_ENRICHMENTS.get(_lesson.get("id"))
        if _enrichment:
            for _key, _val in _enrichment.items():
                _lesson[_key] = _val

STARTER_FILES_CONTENT = {
    d["day_number"]: d["lessons"][-1]["code"] for d in DAYS_CURRICULUM
}
