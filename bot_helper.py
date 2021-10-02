#!/usr/bin/env python3
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from strings import Strings
from utils import MenuElements


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(Strings.PROFILE_BUTTON, callback_data=str(MenuElements.PROFILE.value.data)),
            InlineKeyboardButton(Strings.CLEAN_TIME_BUTTON, callback_data=str(MenuElements.CLEAN_TIME.value.data))
        ],
        [
            InlineKeyboardButton(Strings.READINGS_BUTTON, callback_data=str(MenuElements.READINGS.value.data)),
            InlineKeyboardButton(Strings.PRAYERS_BUTTON, callback_data=str(MenuElements.PRAYERS.value.data)),
        ],
    ]
    return InlineKeyboardMarkup(keyboard, resize_keyboard=True)


def readings_menu_keyboard() -> InlineKeyboardMarkup:
    """Readings menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(Strings.DAILY_REFLECTION_BUTTON,
                                 callback_data=str(MenuElements.DAILY_REFLECTION.value.data)),
            InlineKeyboardButton(Strings.JUST_FOR_TODAY_BUTTON,
                                 callback_data=str(MenuElements.JUST_FOR_TODAY.value.data)),
        ],
        [InlineKeyboardButton(Strings.MAIN_MENU_BUTTON, callback_data=str(MenuElements.MAIN_MENU.value.data))],
    ]
    return InlineKeyboardMarkup(keyboard, resize_keyboard=True)


def prayers_menu_keyboard() -> InlineKeyboardMarkup:
    """Prayers menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(Strings.LORDS_PRAYER_BUTTON, callback_data=str(MenuElements.LORDS_PRAYER.value.data)),
            InlineKeyboardButton(Strings.SERENITY_PRAYER_BUTTON,
                                 callback_data=str(MenuElements.SERENITY_PRAYER.value.data)),
        ],
        [
            InlineKeyboardButton(Strings.ST_JOSEPHS_PRAYER_BUTTON,
                                 callback_data=str(MenuElements.ST_JOSEPHS_PRAYER.value.data)),
            InlineKeyboardButton(Strings.TENDER_AND_COMPASSIONATE_GOD_BUTTON,
                                 callback_data=str(MenuElements.TENDER_AND_COMPASSIONATE_GOD.value.data)),
        ],
        [
            InlineKeyboardButton(Strings.THIRD_STEP_PRAYER_BUTTON,
                                 callback_data=str(MenuElements.THIRD_STEP_PRAYER.value.data)),
            InlineKeyboardButton(Strings.SEVENTH_STEP_PRAYER_BUTTON,
                                 callback_data=str(MenuElements.SEVENTH_STEP_PRAYER.value.data)),
        ],
        [
            InlineKeyboardButton(Strings.ELEVENTH_STEP_PRAYER_BUTTON,
                                 callback_data=str(MenuElements.ELEVENTH_STEP_PRAYER.value.data)),
            InlineKeyboardButton(Strings.MAIN_MENU_BUTTON, callback_data=str(MenuElements.MAIN_MENU.value.data)),
        ],
    ]
    return InlineKeyboardMarkup(keyboard, resize_keyboard=True)


def main_menu_message() -> str:
    """Main menu message"""
    return Strings.MAIN_MENU


def readings_menu_message() -> str:
    """Reading menu message"""
    return Strings.READINGS_MENU


def prayers_menu_message() -> str:
    """Prayers menu message"""
    return Strings.PRAYERS_MENU
