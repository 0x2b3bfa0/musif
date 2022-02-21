import re
from typing import Dict, List, Union

from music21.note import Note

from musif.config import Configuration
from musif.extract.common import filter_parts_data
from musif.extract.features.core.handler import DATA_KEY, DATA_NOTES
from musif.extract.features.prefix import get_part_feature, get_score_feature
from musif.musicxml import get_degrees_and_accidentals
from .constants import *
from ...constants import DATA_PART_ABBREVIATION


def update_part_objects(score_data: dict, part_data: dict, cfg: Configuration, part_features: dict):
    notes = part_data[DATA_NOTES]
    tonality = score_data[DATA_KEY]
    notes_per_degree = get_notes_per_degree(str(tonality), notes)

    all_degrees = sum(value for value in notes_per_degree.values())
    for key, value in notes_per_degree.items():
        part_features[DEGREE_COUNT.format(key=key)] = value
        part_features[DEGREE_PER.format(key=key)] = value / all_degrees if all_degrees != 0 else 0

def update_score_objects(score_data: dict, parts_data: List[dict], cfg: Configuration, parts_features: List[dict], score_features: dict):
    parts_data = filter_parts_data(parts_data, cfg.parts_filter)
    if len(parts_data) == 0:
        return

    tonality = score_data[DATA_KEY]
    score_notes_per_degree = {}
    for part_data in parts_data:
        notes = part_data[DATA_NOTES]
        part_notes_per_degree = get_notes_per_degree(str(tonality), notes)
        for degree, notes in part_notes_per_degree.items():
            if degree not in score_notes_per_degree:
                score_notes_per_degree[degree] = 0
            score_notes_per_degree[degree] += notes
    all_score_degrees = sum(value for value in score_notes_per_degree.values())
    for key, value in score_notes_per_degree.items():
        score_features[get_score_feature(DEGREE_COUNT.format(key=key))] = value
        score_features[get_score_feature(DEGREE_PER.format(key=key))] = value / all_score_degrees if all_score_degrees != 0 else 0

    for part_data, parts_features in zip(parts_data, parts_features):
        part = part_data[DATA_PART_ABBREVIATION]
        degree_count_pattern = DEGREE_COUNT.format(key=".+")
        degree_per_pattern = DEGREE_PER.format(key=".+")
        for feature in parts_features:
            if re.match(degree_count_pattern, feature) or re.match(degree_per_pattern, feature):
                score_features[get_part_feature(part, feature)] = parts_features[feature]


def get_notes_per_degree(key: str, notes: List[Note]) -> Dict[str, int]:
    notes_per_degree = {
        to_full_degree(degree, accidental): 0
        for accidental in ["", "sharp", "flat"]
        for degree in [1, 2, 3, 4, 5, 6, 7]
    }
    all_degrees = 0
    for degree, accidental in get_degrees_and_accidentals(key, notes):
        if to_full_degree(degree, accidental) not in notes_per_degree:
            continue
        notes_per_degree[to_full_degree(degree, accidental)] += 1
        all_degrees += 1
    return notes_per_degree


def to_full_degree(degree: Union[int, str], accidental: str) -> str:
    return f"{ACCIDENTAL_ABBREVIATION[accidental]}{degree}"