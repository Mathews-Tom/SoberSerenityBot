#!/usr/bin/env python3
import datetime
import os
import random
from collections import namedtuple
from enum import Enum
from typing import Tuple, Union

from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from pysqlcipher3 import dbapi2 as sqlite3
from telegram import Chat

import utils

load_dotenv()
sober_serenity_token = os.environ.get('SOBER_SERENITY_TOKEN')
Params = namedtuple("Params", ["name", "token"])
DB_PARAMS = Params("SoberSerenity.db", sober_serenity_token)


class Tables(Enum):
    """Table names"""
    DAILY_REFLECTION = "DAILY_REFLECTION"
    JUST_FOR_TODAY = "JUST_FOR_TODAY"
    PRAYERS = "PRAYERS"
    MOTIVATIONAL_QUOTES = "MOTIVATIONAL_QUOTES"
    USERS = "USERS"


class Columns(Enum):
    """Column names"""
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


def initialize_db(db_params: Params):
    connection = sqlite3.connect(db_params.name)
    cursor = connection.cursor()
    cursor.execute(f"PRAGMA key='{db_params.token}'")
    return connection, cursor


def query_db(query) -> Union[list, None]:
    conn, cur = initialize_db(DB_PARAMS)
    cur.execute(query)
    result = cur.fetchall()
    conn.commit()
    conn.close()
    return result if bool(result) else None


def get_record(table_name: Tables, primary_key: Columns, primary_value: Union[int, str]) -> list:
    """
    Get record based on a column key and value.

    :param table_name: Table name
    :param primary_key: Column name
    :param primary_value: Column value
    :return: Return records as list of tuples or empty list if no record is found
    """
    q = get_quotes(primary_value)
    query = f"SELECT * FROM {table_name.value} WHERE {primary_key.value} = {q}{primary_value}{q}"
    return query_db(query)


def update_record(table_name: Tables, anchor_key: Columns, anchor_value: Union[int, str], update_key: Columns,
                  update_value: Union[int, str]) -> None:
    """
    Update record

    :param table_name: Table name
    :param anchor_key: Anchor column name
    :param anchor_value: Anchor column value
    :param update_key: Update column name
    :param update_value: Update column value
    """
    q1 = get_quotes(update_value)
    q2 = get_quotes(anchor_value)
    query = f"UPDATE {table_name.value} SET {update_key.value} = {q1}{update_value}{q1} " \
            f"WHERE {anchor_key.value} = {q2}{anchor_value}{q2}"
    return query_db(query)


def insert_record(table_name: Tables, values: Tuple) -> None:
    """
    Insert record

    :param table_name: Table name
    :param values: Column values
    """
    query = f"INSERT INTO {table_name.value} VALUES ("
    for value in values:
        q = get_quotes(value)
        query += f"{q}{value}{q}, "
    query = query[:-2]
    query += ")"
    return query_db(query)


def delete_record(table_name: Tables, key: Columns, value: Union[int, str]) -> None:
    """
    Delete record

    :param table_name: Table name
    :param key: Primary key column name
    :param value: Primary key column value
    """
    q = get_quotes(value)
    query = f"DELETE FROM {table_name.value} WHERE {key.value} = {q}{value}{q}"
    return query_db(query)


def get_count(table_name: Tables, key: Columns):
    """Get count of rows"""
    query = f"SELECT COUNT({key.value}) FROM {table_name.value}"
    return query_db(query)


def get_quotes(value):
    """Get quotes to be added in SQL query if the instance is not of instance INT"""
    return "" if isinstance(value, int) else "'"


def convert_tuple_to_user_dict(tuple_data: tuple) -> dict:
    """Convert tuple record from DB to user dictionary"""
    addictions = tuple_data[4].split(", ")
    if addictions[0] == "":
        addictions = []
    user = {"UserID": tuple_data[0],
            "UserName": tuple_data[1],
            "FirstName": tuple_data[2],
            "LastName": tuple_data[3],
            "Addictions": addictions,
            "CleanDateTime": tuple_data[5],
            "UTCOffset": tuple_data[6]}
    return user


def convert_tuple_to_reading_dict(tuple_data: tuple) -> dict:
    """Convert tuple record from DB to reading dictionary"""
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


def convert_tuple_to_prayer_dict(tuple_data: tuple) -> dict:
    """Convert tuple record from DB to prayer dictionary"""
    prayer = {"Title": tuple_data[0],
              "Name": tuple_data[1],
              "Prayer": tuple_data[2]}
    return prayer


def check_user_exists(user_id: int):
    """
    Check if user already exists

    :param user_id: User ID
    :return: boolean
    """
    result = get_record(Tables.USERS, Columns.USER_ID, user_id)
    return bool(result)


def get_user(user_id: int) -> dict:
    """
    Get user profile

    :param user_id: User ID
    :return: User profile
    """
    if check_user_exists(user_id):
        result = get_record(Tables.USERS, Columns.USER_ID, user_id)
        user = convert_tuple_to_user_dict(result[0])
    else:
        user = None
    return user


def create_user(chat: Chat) -> dict:
    """Create new user profile and store in USERS table in DB. Return user if user exists"""
    if check_user_exists(chat.id):
        return get_user(chat.id)
    new_user = (chat.id, chat.username, chat.first_name, chat.last_name, "", "", "")
    insert_record(Tables.USERS, new_user)
    return convert_tuple_to_user_dict(new_user)


def get_user_profile(user: dict, user_job):
    user_profile_str = f"Name: {user['FirstName']} {user['LastName']}"
    if user['Addictions']:
        user_profile_str += f"\nAddictions: {', '.join(user['Addictions'])}"
    if user['CleanDateTime']:
        user_profile_str += f"\nClean Date: {user['CleanDateTime']}"
    if user['UTCOffset']:
        user_profile_str += f"\nUTC Offset: {user['UTCOffset']}"
    if user_job:
        notification_time = utils.convert_utc_time_to_local_time(user_job[0].job.next_run_time,
                                                                 get_time_offset(user['UserID']))
        user_profile_str += f"\nDaily Notification Time: {notification_time.time()}"
    return user_profile_str


def get_time_offset(user_id: int) -> relativedelta:
    """
    Get UTC offset for user

    :param user_id: User chat
    :return:
    """
    result = get_record(Tables.USERS, Columns.USER_ID, user_id)
    offset_str = convert_tuple_to_user_dict(result[0])['UTCOffset']
    if offset_str:
        hr = int(offset_str[1:].split(':')[0])
        mn = int(offset_str[1:].split(':')[1])
        offset = relativedelta(hours=hr, minutes=mn, seconds=0)
    else:
        offset = relativedelta(hours=0, minute=0, seconds=0)
    return offset


def update_user_utc_time_offset(user_id: int, utc_offset: str) -> bool:
    """
    Update user's UTC time offset

    :param user_id: User chat ID
    :param utc_offset: UTC offset string
    :return: True if UTC offset was updated, otherwise False
    """
    if check_user_exists(user_id):
        if utils.check_offset_format_is_correct(utc_offset):
            update_record(Tables.USERS, Columns.USER_ID, user_id, Columns.UTC_OFFSET, utc_offset)
            return True
    return False


def get_user_local_time(user_id: int) -> datetime.datetime:
    user = get_user(user_id)
    if user:
        offset = get_time_offset(user_id)
        return utils.convert_utc_time_to_local_time(datetime.datetime.utcnow(), offset)
    else:
        return datetime.datetime.utcnow()


def get_clean_time(clean_date_time: datetime.datetime, user_id: int) -> str:
    """
    Get clean time based on user specified clean date

    :param clean_date_time: datetime.datetime object specifying the clean date
    :param user_id: User ID
    :return: Clean time string
    """
    local_dt = get_user_local_time(user_id)
    date_time_delta = relativedelta(local_dt, clean_date_time)
    clean_time_str = utils.build_clean_time_str(date_time_delta)
    days_since = (local_dt - clean_date_time).days
    return f'Yaay!!! 👏👏👏, you have {clean_time_str} or {days_since} days of clean time.'


def get_reading(book_name: str, date: datetime.datetime = datetime.datetime.today()) -> str:
    """
    Get reading for a day to user

    :param book_name: Name of the book (Alcoholic Anonymous or Narcotics Anonymous)
    :param date: Date for the reading (default is current date). Date will be modified to have the year 2020 to support
    leap year
    :return Reading for the day
    """
    date = datetime.datetime(2020, date.month, date.day)
    book = Tables.DAILY_REFLECTION if book_name == "DailyReflection" else Tables.JUST_FOR_TODAY
    reading = get_record(book, Columns.DATE, str(date.date()))
    return utils.format_reading(book_name, convert_tuple_to_reading_dict(reading[0]))


def get_prayer(prayer_name: str) -> str:
    """
    Get prayer

    :param prayer_name: Name of the Prayer
    :return Prayer
    """
    prayer = get_record(Tables.PRAYERS, Columns.TITLE, prayer_name)
    return utils.format_prayer(convert_tuple_to_prayer_dict(prayer[0]))


def get_random_motivational_str() -> str:
    """Get a random quote from the list of quotes"""
    rand_int = random.randrange(get_count(Tables.MOTIVATIONAL_QUOTES, Columns.SL_NO)[0][0])
    quote = get_record(Tables.MOTIVATIONAL_QUOTES, Columns.SL_NO, rand_int)
    return quote[0][1]
