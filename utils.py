import datetime
import json
import os
import random
from collections import namedtuple
from enum import Enum
from typing import Union

from dateutil.relativedelta import relativedelta
from telegram import Chat

WORKING_DIR = os.getcwd()


def create_menu_elements():
    """
    Create Menu Elements

    :return: Menu elements as an enum in the format KEY_WORD -> Vales(char, KeyWord)
    """
    menu_keys = ["MAIN_MENU", "CLEAN_TIME", "READINGS", "PRAYERS", "DAILY_REFLECTION", "JUST_FOR_TODAY", "LORDS_PRAYER",
                 "SERENITY_PRAYER", "ST_JOSEPHS_PRAYER", "TENDER_AND_COMPASSIONATE_GOD", "THIRD_STEP_PRAYER",
                 "SEVENTH_STEP_PRAYER", "ELEVENTH_STEP_PRAYER", "INVALID"]
    menu_values_chr = [chr(ch) for ch in range(len(menu_keys))]
    menu_values_str = ["MainMenu", "CleanTime", "Readings", "Prayers", "DailyReflection", "JustForToday", "LordsPrayer",
                       "SerenityPrayer", "StJosephsPrayer", "TenderAndCompassionateGod", "ThirdStepPrayer",
                       "SeventhStepPrayer", "EleventhStepPrayer", "Invalid"]
    values = namedtuple('Values', 'data name')
    return Enum('MenuElements', {k: values(data=v1, name=v2)
                                 for k, v1, v2 in zip(menu_keys, menu_values_chr, menu_values_str)})


# Menu Elements
MenuElements = create_menu_elements()


def get_menu_element_from_chr(ch) -> MenuElements:
    for me in MenuElements:
        if ch == me.value[0]:
            return me
    return MenuElements.INVALID


class Users(object):
    """User profile class"""

    def __init__(self, user_dict):
        """Constructor"""
        for key in user_dict:
            setattr(self, key, user_dict[key])

    def __repr__(self):
        """Get Users class attributes"""
        return str([x for x in dir(self) if "__" not in x])


def check_user_exists(user_id: int):
    """
    Check if user already exists
    :param user_id: User ID
    :return: boolean
    """
    with open(f'{WORKING_DIR}/JSONs/Users.json', 'r') as fhd:
        data = json.load(fhd)
    return True if str(user_id) in data.keys() else False


def create_user(chat: Chat) -> Chat:
    """Create new user profile and store in Users.json file"""
    with open(f'{WORKING_DIR}/JSONs/Users.json', 'r') as fhd:
        data = json.load(fhd)
        new_data = {str(chat.id): {
            "UserID": chat.id,
            "UserName": chat.username,
            "FirstName": chat.first_name,
            "LastName": chat.last_name,
            "SubstanceOfChoice": [],
            "CleanDateTime": "",
        }}
    data.update(new_data)
    with open(f'{WORKING_DIR}/JSONs/Users.json', 'w') as fhd:
        json.dump(data, fhd, indent=4)
    return new_data[str(chat.id)]


def get_user(user_id: int) -> dict:
    """
    Get user profile

    :param user_id: User ID
    :return: User profile
    """
    if check_user_exists(user_id):
        with open(f'{WORKING_DIR}/JSONs/Users.json', 'r') as fhd:
            data = json.load(fhd)
            user = data[str(user_id)]

    else:
        user = None
    return user


def get_user_ids():
    """
    Get all registered users in the database

    :return: List of user IDs registered in the database
    """
    with open(f'{WORKING_DIR}/JSONs/Users.json', 'r') as fhd:
        data = json.load(fhd)
    user_ids = data.keys
    return user_ids


def get_time_offset(user_id: int) -> relativedelta:
    """
    Get UTC offset for user

    :param user_id: User chat
    :return:
    """
    with open(f'{WORKING_DIR}/JSONs/Users.json', 'r') as fhd:
        data = json.load(fhd)
    offset_str = data[str(user_id)]['UTCOffset']
    if offset_str:
        hr = int(offset_str[1:].split(':')[0])
        mn = int(offset_str[1:].split(':')[1])
        offset = relativedelta(hours=hr, minutes=mn, seconds=0)
    else:
        offset = relativedelta(hours=0, minute=0, seconds=0)
    return offset


def get_user_profile(user: dict, user_job):
    user_profile_str = f"Name: {user['FirstName']} {user['LastName']}"
    if user['SubstanceOfChoice']:
        user_profile_str += f"\nSubstance of Choice: {', '.join(user['SubstanceOfChoice'])}"
    if user['CleanDateTime']:
        user_profile_str += f"\nClean Date: {user['CleanDateTime']}"
    if user['UTCOffset']:
        user_profile_str += f"\nUTC Offset: {user['UTCOffset']}"
    if user_job:
        notification_time = convert_utc_time_to_local_time(user_job[0].job.next_run_time,
                                                           get_time_offset(user['UserID']))
        user_profile_str += f"\nDaily Notification Time: {notification_time.time()}"
    return user_profile_str


def update_user_utc_time_offset(user_id: int, utc_offset: str) -> bool:
    """
    Update user's UTC time offset

    :param user_id: User chat ID
    :param utc_offset: UTC offset string
    :return: True if UTC offset was updated, otherwise False
    """

    def check_offset_format_is_correct(offset: str):
        return len(offset.split(':')[0]) == 3 and len(offset.split(':')[1]) == 2

    if check_user_exists(user_id):
        with open(f'{WORKING_DIR}/JSONs/Users.json', 'r') as fhd:
            data = json.load(fhd)
        if check_offset_format_is_correct(utc_offset):
            data[str(user_id)]['UTCOffset'] = utc_offset
            with open(f'{WORKING_DIR}/JSONs/Users.json', 'w') as f:
                json.dump(data, fhd, indent=4)
            return True
    return False


def convert_local_time_to_utc_time(local_time: datetime.datetime, offset: relativedelta):
    """Convert local time to UTC time based on offset"""
    return local_time - offset


def convert_utc_time_to_local_time(local_time: datetime.datetime, offset: relativedelta):
    """Convert UTC time to local time based on offset"""
    return local_time + offset


def convert_str_to_datetime(str_date: str) -> Union[datetime.datetime, None]:
    """
    Convert string date in the format YYYY-MM-DD to datetime.date object

    :param str_date: String date in the format YYYY-MM-DD
    :return: datetime.date object
    """
    if ' ' not in str_date:
        dt = str_date
        sc = '00:00:00'
    else:
        dt, sc = str_date.split()
    yr, mo, dy = dt.split('-')
    hr, mn, sc = sc.split(':')
    if len(yr) != 4 or len(mo) > 2 or len(dy) > 2 or len(hr) > 2 or len(mn) > 2 or len(sc) > 2:
        return None
    yr, mo, dy, hr, mn, sc = [int(x) for x in [yr, mo, dy, hr, mn, sc]]
    return datetime.datetime(yr, mo, dy, hr, mn, sc)


def get_clean_time(clean_date_time) -> str:
    """
    Get clean time based on user specified clean date

    :param clean_date_time: datetime.datetime object specifying the clean date
    :return: Clean time string
    """

    def create_clean_time_str(dt_delta) -> str:
        """
        Format and create clean time string

        :param dt_delta Relative time delta between NOW and clean date.
        :return: Cleaned string representation of Clean Time
        """

        def clean_time_str_helper(x: int, frame: str) -> str:
            """
            Helper function to format individual time frames

            :param x: Integer
            :param frame: Time frame
            :return: Formatted time string
            """
            return '' if x == 0 else f' {x} {frame} ' if x == 1 else f' {x} {frame}s '

        # Number of days need correction as relativedelta calculates weeks and days separately and not together.
        days_corrected = dt_delta.days - dt_delta.weeks * 7
        fmt_str = f'{clean_time_str_helper(dt_delta.years, "year")}{clean_time_str_helper(dt_delta.months, "month")}' \
                  f'{clean_time_str_helper(dt_delta.weeks, "week")}{clean_time_str_helper(days_corrected, "day")}' \
                  f'and{clean_time_str_helper(dt_delta.hours, "hour")}' \
                  f'{clean_time_str_helper(dt_delta.minutes, "minute")}' \
                  f'{clean_time_str_helper(dt_delta.seconds, "second")}'
        return fmt_str.strip()

    if not clean_date_time:
        return "User profile not set. Set user profile to get clean time data."
    date_time_delta = relativedelta(datetime.datetime.today(), clean_date_time)
    clean_time_str = create_clean_time_str(date_time_delta)
    days_since = (datetime.datetime.today() - clean_date_time).days
    return f'Yaay!!!👏👏👏, you have {clean_time_str} or {days_since} days of clean time.'


def get_reading(book: str, date: datetime.datetime = datetime.datetime.today()) -> str:
    """
    Get reading for a day to user

    :param book: Name of the book (Alcoholic Anonymous or Narcotics Anonymous)
    :param date: Date for the reading (default is current date). Date will be modified to have the year 2020 to support
    leap year :return Reading for the day
    :return Reading for a day
    """

    def format_reading(book_name: str, reading_dict: dict) -> str:
        """
        Format the reading

        :param book_name: Name of the book (Alcoholic Anonymous or Narcotics Anonymous)
        :param reading_dict: Reading
        :return: Formatted reading
        """
        fmt = ''
        if book_name == MenuElements.DAILY_REFLECTION.value.name:
            fmt += '<i><u><b>Daily Reflection</b></u></i>\n\n'
        elif book_name == MenuElements.JUST_FOR_TODAY.value.name:
            fmt += "<i><u><b>Just For Today</b></u></i>\n\n"
        fmt += (
            f'{reading_dict["Month"]} {reading_dict["Day"]}: '
            f'<b><u>{reading_dict["Title"]}</u></b>\n\n'
            f'<i>{reading_dict["Snippet"]}\n\n'
            f'{reading_dict["Content"]}</i> \n\n'
        )
        if book_name == 'JustForToday':
            fmt += f"<i>Just for Today: {reading_dict['JustForToday']}</i>\n\n"

        if not reading_dict['Reference']:
            fmt += f"<i>\n\n{reading_dict['Reference']}  P.{reading_dict['Page']}</i>"
        return fmt

    date = datetime.datetime(2020, date.month, date.day)
    with open(f'{WORKING_DIR}/JSONs/{book}.json', 'r') as fhd:
        data = json.load(fhd)
        reading = data[str(date.date())]
    return format_reading(book, reading)


def get_prayer(prayer_name: str) -> str:
    """
    Get prayer

    :param prayer_name: Name of the Prayer
    :return Prayer
    """

    def format_prayer(prayer: dict) -> str:
        """
        Format the reading

        :param prayer Name of the prayer
        :return: Formatted prayer
        """
        return f'<i><u><b>{prayer["Title"]}</b></u></i>\n\n{prayer["Prayer"]}'

    with open(f'{WORKING_DIR}/JSONs/Prayers.json', 'r') as fhd:
        data = json.load(fhd)[prayer_name]
    return format_prayer(data)


def get_random_motivational_str() -> str:
    """Get a random quote from the list of quotes"""
    with open(f'{WORKING_DIR}/JSONs/MotivationalQuotes.json', 'r') as fhd:
        motivational_quotes = json.load(fhd)
        rand_int = random.randrange(len(motivational_quotes))
        quote = motivational_quotes[rand_int]
    return quote