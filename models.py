#!/usr/bin/env python3
from enum import Enum
from typing import NamedTuple, Union

from telegram import Update
from telegram.ext import CallbackContext


class MenuElementValues(NamedTuple):
    """Menu Element name and data tuple.

    data: char data for each Menu Element
    name: name of the Menu Element
    """
    data: chr
    name: str


def __create_menu_elements() -> Enum:
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
    return Enum('MenuElements', {k: MenuElementValues(data=v1, name=v2)
                                 for k, v1, v2 in zip(menu_keys, menu_values_chr, menu_values_str)})


# Menu Elements
MenuElements = __create_menu_elements()


class Tables(Enum):
    """Database table names."""
    DAILY_REFLECTION = "DAILY_REFLECTION"
    JUST_FOR_TODAY = "JUST_FOR_TODAY"
    PRAYERS = "PRAYERS"
    MOTIVATIONAL_QUOTES = "MOTIVATIONAL_QUOTES"
    USERS = "USERS"


class Columns(Enum):
    """Database column names."""
    DATE = "date"
    DAY = "day"
    MONTH = "month"
    TITLE = "title"
    SNIPPET = "snippet"
    REFERENCE = "reference"
    PAGE = "page"
    CONTENT = "content"
    JUST_FOR_TODAY = "just_for_today"
    COPYRIGHT = "copyright"
    WEBSITE = "website"
    NAME = "name"
    PRAYER = "prayer"
    SL_NO = "sl_no"
    QUOTE = "quote"
    USER_ID = "user_id"
    USER_NAME = "user_name"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    ADDICTIONS = "addictions"
    CLEAN_DATE = "clean_date"
    UTC_OFFSET = "utc_offset"
    DAILY_NOTIFICATION = "daily_notification"


class DatabaseParams(NamedTuple):
    """Database parameters (NAME, TOKEN).

    name: Database file name
    token: Encryption token
    """
    name: str
    token: str


class DBKeyValue(NamedTuple):
    """Database key value pair tuple.

    key: Columns type with column names
    value: Union[str, int]
    """
    key: Columns
    value: Union[str, int]


class BotUCM(NamedTuple):
    """
    Common tuple with basic data (Update, CallbackContext, and Message) used sending messages to user.

    update: Telegram Update
    context: CallbackContext
    message: String to be sent
    """
    update: Update
    context: CallbackContext
    message: str
