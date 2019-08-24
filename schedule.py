import io
import csv
import sys
import json
import requests

from bs4 import BeautifulSoup

from exceptions import NoSuchGroupID
from config import MAI_SCHEDULE_URL


def exist_group(group_id: str) -> bool:
    """
    Checks if group id exists
    """

    req = requests.get(MAI_SCHEDULE_URL)
    soup = BeautifulSoup(req.text, "html.parser")

    groups = soup.select(".sc-group-item")
    for group in groups:
        if group.string == group_id:
            return True
    else:
        return False


def iter_groups_of_mai():
    """
    Iterates over groups id
    """

    queue = []
    json_file = io.open("schedule.json", "r", encoding="utf8")
    structure = json.load(json_file)
    json_file.close()
    queue.extend(list(structure.items()))

    while len(queue) > 0:
        key, value = queue.pop()

        if key in ("Аспирантура", "Бакалавриат", "Магистратура", "Специалитет"):
            for group_id in value:
                yield group_id
        else:
            queue.extend(list(value.items()))


def get_structure_of_mai():
    """
    Get structure MAI
    """

    req = requests.get(MAI_SCHEDULE_URL)
    soup = BeautifulSoup(req.text, "html.parser")

    result = {}

    grades = soup.select(".sc-container")
    for grade in grades:
        grade_level = grade.select_one(".sc-container-header").string
        result[grade_level] = {}

        facults = grade.select(".sc-table-row")
        for facult in facults:
            facult_name = facult.select_one("a.sc-table-col").string
            result[grade_level][facult_name] = {}

            grade_programs = facult.spasselect(".sc-groups")
            for grade_program in grade_programs:
                program_name = grade_program.select_one(".sc-program").string

                program_items = grade_program.select(".sc-group-item")
                groups = [item.string for item in program_items]
                result[grade_level][facult_name][program_name] = groups

    return result