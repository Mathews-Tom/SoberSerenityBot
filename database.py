import datetime
import os
import random
from typing import Tuple, Union

from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from pysqlcipher3 import dbapi2 as sqlite3
from telegram import Chat

import utils
from models import DatabaseParams, Tables, Columns, DBKeyValue

load_dotenv()
sober_serenity_token = os.environ.get('SOBER_SERENITY_TOKEN')

DB_PARAMS = DatabaseParams("SoberSerenity.db", sober_serenity_token)


def initialize_db(db_params: DatabaseParams) -> Tuple:
    """Initialize database."""
    connection = sqlite3.connect(db_params.name)
    cursor = connection.cursor()
    cursor.execute(f"PRAGMA key='{db_params.token}'")
    return connection, cursor


def query_db(query) -> Union[list, None]:
    """Query database."""
    conn, cur = initialize_db(DB_PARAMS)
    cur.execute(query)
    result = cur.fetchall()
    conn.commit()
    conn.close()
    return result if bool(result) else None


def get_record(table_name: Tables, record: DBKeyValue) -> list:
    """Get record based on a column key and value.

    :param table_name: Table name
    :param record: DBKeyValue of primary key
    :return: Return records as list of tuples or empty list if no record is found
    """
    value = utils.modify_str_int_value(record.value)
    query = f"SELECT * FROM {table_name.value} WHERE {record.key.value} = {value}"
    return query_db(query)


def get_record_not_value(table_name: Tables, record: DBKeyValue) -> list:
    """Get record based on a column key and value.

    :param table_name: Table name
    :param record: DBKeyValue of primary key
    :return: Return records as list of tuples or empty list if no record is found
    """
    value = utils.modify_str_int_value(record.value)
    query = f"SELECT * FROM {table_name.value} WHERE {record.key.value} <> {value}"
    return query_db(query)


def update_record(table_name: Tables, anchor: DBKeyValue, update: DBKeyValue) -> None:
    """Update record.

    :param table_name: Table name
    :param anchor: DBKeyValue of anchor
    :param update: DBKeyValue of update
    """
    update_value = utils.modify_str_int_value(update.value)
    anchor_value = utils.modify_str_int_value(anchor.value)
    query = f"UPDATE {table_name.value} SET {update.key.value} = {update_value} " \
            f"WHERE {anchor.key.value} = {anchor_value}"
    return query_db(query)


def insert_record(table_name: Tables, values: Tuple) -> None:
    """Insert record.

    :param table_name: Table name
    :param values: Column values
    """
    query = f"INSERT INTO {table_name.value} VALUES ("
    for value in values:
        value = utils.modify_str_int_value(value)
        query += f"{value}, "
    query = query[:-2]
    query += ")"
    return query_db(query)


def delete_record(table_name: Tables, record: DBKeyValue) -> None:
    """Delete record.

    :param table_name: Table name
    :param record: DBKeyValue of primary key
    """
    value = utils.modify_str_int_value(record.value)
    query = f"DELETE FROM {table_name.value} WHERE {record.key.value} = {value}"
    return query_db(query)


def get_count(table_name: Tables, key: Columns) -> int:
    """Get count of rows."""
    query = f"SELECT COUNT({key.value}) FROM {table_name.value}"
    result = query_db(query)
    return result[0][0] if bool(result) else 0


def check_user_exists(user_id: int) -> bool:
    """Check if user already exists.

    :param user_id: User ID
    :return: boolean
    """
    result = get_record(Tables.USERS, DBKeyValue(Columns.USER_ID, user_id))
    return bool(result)


def get_user(user_id: int) -> dict:
    """Get user profile.

    :param user_id: User ID
    :return: User profile
    """
    if check_user_exists(user_id):
        result = get_record(Tables.USERS, DBKeyValue(Columns.USER_ID, user_id))
        user = utils.convert_tuple_to_user_dict(result[0])
    else:
        user = None
    return user


def get_users_with_set_notification() -> Union[list, None]:
    results = get_record_not_value(Tables.USERS, DBKeyValue(Columns.DAILY_NOTIFICATION, ""))
    if results:
        users = []
        for result in results:
            users.append(utils.convert_tuple_to_user_dict(result))
        return users
    return None


def create_user(chat: Chat) -> dict:
    """Create new user profile and store in USERS table in DB. Return user if user exists."""
    if check_user_exists(chat.id):
        return get_user(chat.id)
    new_user = (chat.id, chat.username, chat.first_name, chat.last_name, "", "", "", "")
    insert_record(Tables.USERS, new_user)
    return utils.convert_tuple_to_user_dict(new_user)


def get_time_offset(user_id: int) -> relativedelta:
    """Get UTC offset for user.

    :param user_id: User chat
    :return:
    """
    result = get_record(Tables.USERS, DBKeyValue(Columns.USER_ID, user_id))
    offset_str = utils.convert_tuple_to_user_dict(result[0])['UTCOffset']
    return utils.convert_utc_offset_str_relative_delta(offset_str)


def update_daily_notification(user_id: int, notification_time: str) -> bool:
    """Update daily notification time.

    :param user_id: User chat ID
    :param notification_time: Notification time
    :return: True if Daily notification was updated, otherwise False
    """
    if check_user_exists(user_id):
        update_record(Tables.USERS, DBKeyValue(Columns.USER_ID, user_id),
                      DBKeyValue(Columns.DAILY_NOTIFICATION, notification_time))
        return True
    return False


def update_user_utc_time_offset(user_id: int, utc_offset: str) -> bool:
    """Update user's UTC time offset.

    :param user_id: User chat ID
    :param utc_offset: UTC offset string
    :return: True if UTC offset was updated, otherwise False
    """
    if check_user_exists(user_id):
        if utils.check_offset_format_is_correct(utc_offset):
            update_record(Tables.USERS, DBKeyValue(Columns.USER_ID, user_id),
                          DBKeyValue(Columns.UTC_OFFSET, utc_offset))
            return True
    return False


def get_user_local_time(user_id: int) -> datetime.datetime:
    """Get user local time."""
    user = get_user(user_id)
    if user:
        offset = get_time_offset(user_id)
        return utils.convert_utc_time_to_local_time(datetime.datetime.utcnow(), offset)
    else:
        return datetime.datetime.utcnow()


def get_clean_time_str(clean_date_time: datetime.datetime, user_id: int) -> Tuple:
    """Get clean time based on user specified clean date.

    :param clean_date_time: datetime.datetime object specifying the clean date
    :param user_id: User ID
    :return: Clean time string
    """
    local_dt = get_user_local_time(user_id)
    date_time_delta = relativedelta(local_dt, clean_date_time)
    clean_time_str = utils.build_clean_time_str(date_time_delta)
    days_since = (local_dt - clean_date_time).days
    return clean_time_str, days_since


def get_reading(book_name: str, date: datetime.datetime = datetime.datetime.today()) -> str:
    """Get reading for a day to user.

    :param book_name: Name of the book (Alcoholic Anonymous or Narcotics Anonymous)
    :param date: Date for the reading (default is current date). Date will be modified to have the year 2020 to support
    leap year
    :return Reading for the day
    """
    date = datetime.datetime(2020, date.month, date.day)
    book = Tables.DAILY_REFLECTION if book_name == "DailyReflection" else Tables.JUST_FOR_TODAY
    reading = get_record(book, DBKeyValue(Columns.DATE, str(date.date())))
    return utils.format_reading(book_name, utils.convert_tuple_to_reading_dict(reading[0]))


def get_prayer(prayer_name: str) -> str:
    """Get prayer.

    :param prayer_name: Name of the Prayer
    :return Prayer
    """
    prayer = get_record(Tables.PRAYERS, DBKeyValue(Columns.TITLE, prayer_name))
    return utils.format_prayer(utils.convert_tuple_to_prayer_dict(prayer[0]))


def get_random_motivational_str() -> str:
    """Get a random quote from the list of quotes."""
    rand_int = random.randrange(get_count(Tables.MOTIVATIONAL_QUOTES, Columns.SL_NO))
    quote = get_record(Tables.MOTIVATIONAL_QUOTES, DBKeyValue(Columns.SL_NO, rand_int))
    return quote[0][1]
