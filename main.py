import pytz, datetime

from ics import Calendar, Event
from colorama import Fore, Style
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException

from schedule import exist_group
from exceptions import NoSuchGroupID
from config import MAI_SCHEDULE_DETAIL


def main():
    group_id = input(Fore.WHITE + Style.BRIGHT + "Enter group id: " + Style.RESET_ALL)
    result_filename = f"{group_id}.ics"
    local = pytz.timezone("Europe/Moscow")
    study_calendar = Calendar()

    try:
        print(Fore.WHITE, Style.BRIGHT, "Checking for the existence of a group...", Style.RESET_ALL, end="")

        if not exist_group(group_id):
            raise NoSuchGroupID(group_id)

        print(Fore.GREEN, Style.BRIGHT, " Ok", Style.RESET_ALL)

        opts = Options()
        opts.set_headless()
        browser = Firefox(options=opts)
        base_url = f"{MAI_SCHEDULE_DETAIL}?group={group_id}"

        browser.get(base_url)

        print(Fore.WHITE, Style.BRIGHT, "Number of university weeks:", Style.RESET_ALL, end="")

        number_study_weeks = len(browser.find_elements_by_css_selector(".table tr a")) # get all weeks

        print(number_study_weeks)

        for i in range(1, number_study_weeks + 1): # iterates over weeks
            print(Fore.WHITE, Style.BRIGHT, f"\nGetting {i} week schedule...", Style.RESET_ALL)

            browser.get(f"{base_url}&week={i}")

            # get year of current week
            stud_weeks = browser.find_elements_by_css_selector(".table tr a")
            year = stud_weeks[i - 1].text[-4:]

            stud_days = browser.find_elements_by_class_name("sc-container")
            for stud_day in stud_days:
                day, month = stud_day.find_element_by_class_name(
                    "sc-day-header").text[: 5].split(".")

                start_date = f"{year}-{month}-{day}" # YYYY-MM-DD

                items = stud_day.find_elements_by_css_selector(
                    ".sc-table-detail > .sc-table-row")

                for item in items:
                    event = Event()
                    start_time, end_time = item.find_element_by_class_name(
                        "sc-item-time").text.split(" – ")

                    event.name = item.find_element_by_class_name("sc-title").text # get title of study item

                    # convert local begin time to utc
                    naive = datetime.datetime.strptime(f"{start_date} {end_time}", "%Y-%m-%d %H:%M")
                    local_dt = local.localize(naive, is_dst=None)
                    utc_dt = local_dt.astimezone(pytz.utc)
                    event.end = utc_dt.strftime ("%Y-%m-%d %H:%M") 

                    # convert local end time to utc
                    naive = datetime.datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
                    local_dt = local.localize(naive, is_dst=None)
                    utc_dt = local_dt.astimezone(pytz.utc)
                    event.begin = utc_dt.strftime ("%Y-%m-%d %H:%M")

                    type_lesson = item.find_element_by_class_name(
                        "sc-item-type").text

                    location = item.find_element_by_class_name(
                        "sc-item-location").text # get audience in MAI

                    # handle case when lecturer field is empty
                    try:
                        lecturer = item.find_element_by_class_name(
                            "sc-lecturer").text
                    except NoSuchElementException:
                        lecturer = ''

                    event.description = f"Type: {type_lesson}\nLocation: {location}\nLecturer: {lecturer}\n"

                    study_calendar.events.add(event)

                print(Fore.WHITE, Style.BRIGHT, f'\t{start_date} -', Fore.GREEN, '\u2713', Style.RESET_ALL)

        # save ics file
        with open(result_filename, "w") as ics_file:
            ics_file.writelines(study_calendar)

        print(Fore.GREEN, Style.BRIGHT, f"\n  Done! Created {result_filename}\n", Style.RESET_ALL)

    except NoSuchGroupID as e:
        print(Fore.RED, Style.BRIGHT, e, Style.RESET_ALL)

if __name__ == "__main__":
    main()