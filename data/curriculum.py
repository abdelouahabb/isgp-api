"""
Agrégation des modules pédagogiques structurés par dossier :
day_0/, day_1/, day_2/, day_3/, day_4/, day_5/
"""

from day_0.lesson_data import DAY_0_DATA
from day_1.lesson_data import DAY_1_DATA
from day_2.lesson_data import DAY_2_DATA
from day_3.lesson_data import DAY_3_DATA
from day_4.lesson_data import DAY_4_DATA
from day_5.lesson_data import DAY_5_DATA

DAYS_CURRICULUM = [
    DAY_0_DATA,
    DAY_1_DATA,
    DAY_2_DATA,
    DAY_3_DATA,
    DAY_4_DATA,
    DAY_5_DATA,
]

STARTER_FILES_CONTENT = {
    d["day_number"]: d["lessons"][-1]["code"] for d in DAYS_CURRICULUM
}
