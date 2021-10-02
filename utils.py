#!/usr/bin/env python3
import datetime
import os
from collections import namedtuple
from enum import Enum
from typing import Union, Tuple

from dateutil.relativedelta import relativedelta
from telegram import Update

import utils
from strings import Strings

WORKING_DIR = os.getcwd()


def create_menu_elements() -> Enum:
    """Create Menu Elements.

    :return: Menu elements as an enum in the format KEY_WORD -> Vales(char, KeyWord)
    """
    menu_keys = ["MAIN_MENU", "PROFILE", "CLEAN_TIME", "READINGS", "PRAYERS", "DAILY_REFLECTION", "JUST_FOR_TODAY",
                 "LORDS_PRAYER", "SERENITY_PRAYER", "ST_JOSEPHS_PRAYER", "TENDER_AND_COMPASSIONATE_GOD",
                 "THIRD_STEP_PRAYER", "SEVENTH_STEP_PRAYER", "ELEVENTH_STEP_PRAYER"]
    menu_values_chr = [chr(ch) for ch in range(len(menu_keys))]
    menu_values_str = ["MainMenu", "Profile", "CleanTime", "Readings", "Prayers", "DailyReflection", "JustForToday",
                       "LordsPrayer", "SerenityPrayer", "StJosephsPrayer", "TenderAndCompassionateGod",
                       "ThirdStepPrayer", "SeventhStepPrayer", "EleventhStepPrayer"]
    values = namedtuple('Values', 'data name')
    return Enum('MenuElements', {k: values(data=v1, name=v2)
                                 for k, v1, v2 in zip(menu_keys, menu_values_chr, menu_values_str)})


# Menu Elements
MenuElements = create_menu_elements()


def get_menu_element_from_chr(ch) -> Union[MenuElements, None]:
    """Get menu element from char data."""
    for me in MenuElements:
        if ch == me.value[0]:
            return me
    return None


def check_offset_format_is_correct(offset: str):
    """Check if provided UTC offset is in correct time."""
    if len(offset.split(':')):
        return False
    offset_split_1 = offset.split(':')[0]
    offset_split_2 = offset.split(':')[1]
    if len(offset_split_1) == 3 and len(offset_split_2) == 2:
        try:
            int(offset_split_1[1:])
            int(offset_split_2)
            return True
        except ValueError:
            return False
    return False


def convert_local_time_to_utc_time(local_time: datetime.datetime, offset: relativedelta) -> datetime.datetime:
    """Convert local time to UTC time based on offset."""
    return local_time - offset


def convert_utc_time_to_local_time(local_time: datetime.datetime, offset: relativedelta) -> datetime.datetime:
    """Convert UTC time to local time based on offset."""
    return local_time + offset


def convert_str_to_datetime(str_date: str) -> Union[datetime.datetime, None]:
    """Convert string date in the format YYYY-MM-DD HH:MM:SS to datetime.datetime object.

    :param str_date: String date in the format YYYY-MM-DD HH:MM:SS
    :return: datetime.datetime object for success and None for failure
    """
    dt, sc = split_str_date_dt_sc(str_date)
    if len(dt.split('-')) != 3 or len(sc.split(':')) != 3:
        return None
    yr, mo, dy = dt.split('-')
    hr, mn, sc = sc.split(':')
    itr = iter([mo, dy, hr, mn, sc])
    no_char_accepted = 2
    if len(yr) != 4 or any(len(elem) > no_char_accepted for elem in itr):
        return None
    dt_tuple = [int(x) for x in [yr, mo, dy, hr, mn, sc] if x.isdigit()]
    return datetime.datetime(dt_tuple[0], dt_tuple[1], dt_tuple[2], dt_tuple[3], dt_tuple[4],
                             dt_tuple[5]) if len(dt_tuple) == 6 else None


def split_str_date_dt_sc(str_date: str) -> Tuple:
    """Split string date to date and time.

    :param str_date: String date in the format YYYY-MM-DD
    :return: Tuple with date and time
    """
    if ' ' not in str_date:
        dt = str_date
        sc = '00:00:00'
    else:
        dt, sc = str_date.split()
    return dt, sc


def build_clean_time_str(dt_delta: relativedelta) -> str:
    """Format and create clean time string.

    :param dt_delta Relative time delta between NOW and clean date.
    :return: Cleaned string representation of Clean Time
    """
    # Number of days need correction as relativedelta calculates weeks and days separately and not together.
    days_corrected = dt_delta.days - dt_delta.weeks * 7
    fmt_str = f'{format_string(dt_delta.years, "year")}{format_string(dt_delta.months, "month")}' \
              f'{format_string(dt_delta.weeks, "week")}{format_string(days_corrected, "day")}' \
              f'and{format_string(dt_delta.hours, "hour")}{format_string(dt_delta.minutes, "minute")}' \
              f'{format_string(dt_delta.seconds, "second")}'
    return fmt_str.strip()


def format_string(x: int, frame: str) -> str:
    """Helper function to format individual time frames.

    :param x: Integer
    :param frame: Time frame
    :return: Formatted time string
    """
    return '' if x == 0 else f' {x} {frame} ' if x == 1 else f' {x} {frame}s '


def format_reading(book_name: str, reading_dict: dict) -> str:
    """Format the reading.

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


def format_prayer(prayer: dict) -> str:
    """Format the reading.

    :param prayer Name of the prayer
    :return: Formatted prayer
    """
    return f'<i><u><b>{prayer["Name"]}</b></u></i>\n\n{prayer["Prayer"]}'


def get_reading_prayer_name(update: Update) -> str:
    """Get Reading or Prayer name."""
    if hasattr(update.message, 'text'):
        return MenuElements[update.message.text[1:].upper()].value.name
    else:
        ch = update.callback_query.data
        return get_menu_element_from_chr(ch)


def convert_tuple_to_user_dict(tuple_data: Tuple) -> dict:
    """Convert tuple record from DB to user dictionary.

    :param tuple_data: User data from DB
    :return: Dict in the format -> {UserID
                                    UserName
                                    FirstName
                                    LastName
                                    Addictions
                                    CleanDateTime
                                    UTCOffset
                                    DailyNotification}
    """
    addictions = tuple_data[4].split(", ")
    if addictions[0] == "":
        addictions = []
    user = {"UserID": tuple_data[0],
            "UserName": tuple_data[1],
            "FirstName": tuple_data[2],
            "LastName": tuple_data[3],
            "Addictions": addictions,
            "CleanDateTime": tuple_data[5],
            "UTCOffset": tuple_data[6],
            "DailyNotification": tuple_data[7]}
    return user


def convert_tuple_to_reading_dict(tuple_data: Tuple) -> dict:
    """Convert tuple record from DB to reading dictionary.
    
    :param tuple_data: Reading data from DB
    :return: Dict in the format -> {Date
                                    Day
                                    Month
                                    Title
                                    Snippet
                                    Reference
                                    Page
                                    Content
                                    JustForToday # Not for Daily Reflection and only for Just For Today
                                    Copyright
                                    Website}
    """
    reading = {"Date": tuple_data[0],
               "Day": tuple_data[1],
               "Month": tuple_data[2],
               "Title": tuple_data[3],
               "Snippet": tuple_data[4],
               "Reference": tuple_data[5],
               "Page": tuple_data[6],
               "Content": tuple_data[7]}
    if len(tuple_data) == 11:  # Just For Today
        reading["JustForToday"] = tuple_data[8]
        reading["Copyright"] = tuple_data[9]
        reading["Website"] = tuple_data[10]
    else:  # Daily Reflection
        reading["Copyright"] = tuple_data[8]
        reading["Website"] = tuple_data[9]
    return reading


def convert_tuple_to_prayer_dict(tuple_data: Tuple) -> dict:
    """Convert tuple record from DB to prayer dictionary.

    :param tuple_data: Prayer data from DB
    :return: Dict in thr format -> {Title
                                    Name
                                    Prayer}
    """
    prayer = {"Title": tuple_data[0],
              "Name": tuple_data[1],
              "Prayer": tuple_data[2]}
    return prayer


def convert_utc_offset_str_relativedelta(offset_str) -> relativedelta:
    if offset_str:
        hr = int(offset_str[1:].split(':')[0])
        mn = int(offset_str[1:].split(':')[1])
        offset = relativedelta(hours=hr, minutes=mn, seconds=0)
    else:
        offset = relativedelta(hours=0, minute=0, seconds=0)
    return offset


def get_user_profile_str(user: dict) -> str:
    """Get user profile string."""
    user_profile_str = Strings.PROFILE_FIRSTNAME_LASTNAME.format(user['FirstName'], user['LastName'])
    if user['Addictions']:
        user_profile_str += "\n" + Strings.PROFILE_ADDICTIONS.format(', '.join(user['Addictions']))
    if user['CleanDateTime']:
        user_profile_str += "\n" + Strings.PROFILE_CLEAN_DATE.format(user['CleanDateTime'])
    if user['UTCOffset']:
        user_profile_str += "\n" + Strings.PROFILE_UTC_OFFSET.format(user['UTCOffset'])
    if user['DailyNotification']:
        user_profile_str += "\n" + Strings.PROFILE_DAILY_NOTIFICATION.format(user['DailyNotification'])
    return user_profile_str
