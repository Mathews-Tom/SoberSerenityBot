#!/usr/bin/env python3
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from utils import MenuElements


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("👤 Profile 👤", callback_data=str(MenuElements.PROFILE.value.data)),
            InlineKeyboardButton("⏳ Clean Time ⏳", callback_data=str(MenuElements.CLEAN_TIME.value.data))
        ],
        [
            InlineKeyboardButton("📚 Readings 📚", callback_data=str(MenuElements.READINGS.value.data)),
            InlineKeyboardButton("🙏 Prayers 🙏", callback_data=str(MenuElements.PRAYERS.value.data)),
        ],
    ]
    return InlineKeyboardMarkup(keyboard, resize_keyboard=True)


def readings_menu_keyboard() -> InlineKeyboardMarkup:
    """Readings menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("📖 Daily Reflections 📖",
                                 callback_data=str(MenuElements.DAILY_REFLECTION.value.data)),
            InlineKeyboardButton("📖 Just For Today 📖", callback_data=str(MenuElements.JUST_FOR_TODAY.value.data)),
        ],
        [InlineKeyboardButton("〽️ Main Menu 〽️", callback_data=str(MenuElements.MAIN_MENU.value.data))],
    ]
    return InlineKeyboardMarkup(keyboard, resize_keyboard=True)


def prayers_menu_keyboard() -> InlineKeyboardMarkup:
    """Prayers menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("📜 LORD's Prayer 📜", callback_data=str(MenuElements.LORDS_PRAYER.value.data)),
            InlineKeyboardButton("📜 Serenity Prayer 📜",
                                 callback_data=str(MenuElements.SERENITY_PRAYER.value.data)),
        ],
        [
            InlineKeyboardButton("📜 St. Joseph's Prayer 📜",
                                 callback_data=str(MenuElements.ST_JOSEPHS_PRAYER.value.data)),
            InlineKeyboardButton("📜 Tender and Compassionate GOD 📜",
                                 callback_data=str(MenuElements.TENDER_AND_COMPASSIONATE_GOD.value.data)),
        ],
        [
            InlineKeyboardButton("📜 Third Step Prayer 📜",
                                 callback_data=str(MenuElements.THIRD_STEP_PRAYER.value.data)),
            InlineKeyboardButton("📜 Seventh Step Prayer 📜",
                                 callback_data=str(MenuElements.SEVENTH_STEP_PRAYER.value.data)),
        ],
        [
            InlineKeyboardButton("📜 Eleventh Step Prayer 📜",
                                 callback_data=str(MenuElements.ELEVENTH_STEP_PRAYER.value.data)),
            InlineKeyboardButton("〽️ Main Menu 〽️", callback_data=str(MenuElements.MAIN_MENU.value.data)),
        ],
    ]
    return InlineKeyboardMarkup(keyboard, resize_keyboard=True)


def main_menu_message() -> str:
    """Main menu message"""
    return 'Hi, I am the Sober Serenity Bot. ⚖️🕊⚖️🕊⚖️🕊️ \n\n\nI am here to help and guide you through your ' \
           'process of Sobriety, be it for yourself or if you are trying to help out someone you care about. ' \
           'Here are few things I can be of help to you. Please chose :: '


def readings_menu_message() -> str:
    """Reading menu message"""
    return 'Readings help to feel comforted during our journey of recovery and sobriety and to gain strength. ' \
           'We learn that today is a gift with no guarantees. With this in mind, the insignificance of the past ' \
           'and future, and the importance of our actions today, become real for us. This simplifies our lives.'


def prayers_menu_message() -> str:
    """Prayers menu message"""
    return 'On the onset of our journey towards sobriety we made a decision to turn our lives over to the care ' \
           'of a Higher Power. This surrender relieves the burden of the past and fear of the future, and the ' \
           'gift of today is now in proper perspective. We accept and enjoy life as it is right now. When we ' \
           'refuse to accept the reality of today we are denying our faith in our Higher Power, which can only ' \
           'bring more suffering. Prayer gives you a connection to something greater than yourself, which does ' \
           'wonders for your emotional well-being. It provides a greater sense of purpose, betters your mood, ' \
           'and helps you cope with and overcome the difficulties life brings your way. Just as it’s important ' \
           'to exercise your body to stay healthy and in shape, the same is true for your soul, you need to ' \
           'practice spiritual exercises to keep your soul in shape.'
