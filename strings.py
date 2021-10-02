#!/usr/bin/env python3

class Strings:
    MAIN_MENU = "Hi, I am the Sober Serenity Bot. ⚖️🕊⚖️🕊⚖️🕊️ \n\n\nI am here to help and guide you through your " \
                "process of Sobriety, be it for yourself or if you are trying to help out someone you care about. " \
                "Here are few things I can be of help to you. Please chose one"
    READINGS_MENU = "Readings help to feel comforted during our journey of recovery and sobriety and to gain " \
                    "strength. We learn that today is a gift with no guarantees. With this in mind, the " \
                    "insignificance of the past and future, and the importance of our actions today, become real " \
                    "for us. This simplifies our lives."
    PRAYERS_MENU = "On the onset of our journey towards sobriety we made a decision to turn our lives over to the " \
                   "care of a Higher Power. This surrender relieves the burden of the past and fear of the future, " \
                   "and the gift of today is now in proper perspective. We accept and enjoy life as it is right now. " \
                   "When we refuse to accept the reality of today we are denying our faith in our Higher Power, " \
                   "which can only bring more suffering. Prayer gives you a connection to something greater than " \
                   "yourself, which does wonders for your emotional well-being. It provides a greater sense of " \
                   "purpose, betters your mood, and helps you cope with and overcome the difficulties life brings " \
                   "your way. Just as it’s important to exercise your body to stay healthy and in shape, the same " \
                   "is true for your soul, you need to practice spiritual exercises to keep your soul in shape."
    MAIN_MENU_BUTTON = "〽️ Main Menu 〽️"
    PROFILE_BUTTON = "👤 Profile 👤"
    CLEAN_TIME_BUTTON = "⏳ Clean Time ⏳"
    READINGS_BUTTON = "📚 Readings 📚"
    PRAYERS_BUTTON = "🙏 Prayers 🙏"
    DAILY_REFLECTION_BUTTON = "📖 Daily Reflections 📖"
    JUST_FOR_TODAY_BUTTON = "📖 Just For Today 📖"
    LORDS_PRAYER_BUTTON = "📜 LORD's Prayer 📜"
    SERENITY_PRAYER_BUTTON = "📜 Serenity Prayer 📜"
    ST_JOSEPHS_PRAYER_BUTTON = "📜 St. Joseph's Prayer 📜"
    TENDER_AND_COMPASSIONATE_GOD_BUTTON = "📜 Tender and Compassionate GOD 📜"
    THIRD_STEP_PRAYER_BUTTON = "📜 Third Step Prayer 📜"
    SEVENTH_STEP_PRAYER_BUTTON = "📜 Seventh Step Prayer 📜"
    ELEVENTH_STEP_PRAYER_BUTTON = "📜 Eleventh Step Prayer 📜"
    PROFILE = "{}, I know the following about you:\n{}"
    PROFILE_FIRSTNAME_LASTNAME = "Name: {} {}"
    PROFILE_ADDICTIONS = "Addictions: {}"
    PROFILE_CLEAN_DATE = "Clean Date: {}"
    PROFILE_UTC_OFFSET = "UTC Offset: {}"
    PROFILE_DAILY_NOTIFICATION = "Daily Notification Time: {}"
    CLEAN_TIME = "Yaay!!! 👏👏👏, you have {} or {} days of clean time."
    CLEAN_TIME_CLEAN_DATE_NOT_SET = "{}, you haven't set your profile yet. Please update user profile with clean " \
                                    "date to get clean time data."
    UTC_OFFSET_SUCCESS = "User time offset set to: {}"
    UTC_OFFSET_FAILURE = "{}, use this format to set UTC offset:\n\n/set_utc_offset +/-HH:MM"
    ENABLE_NOTIFICATION_SUCCESS = "Great {}, I have enabled daily notifications for: {}"
    ENABLE_NOTIFICATION_NOTIFICATION_ALREADY_SET = "{}, your daily notification is already enabled for: {}.\n<i>To " \
                                                   "update notification time, first disable and then enable daily " \
                                                   "notification with updated time.</i>"
    ENABLE_NOTIFICATION_FAILURE = "{}, use this format to enable daily notifications:\n\n/enable_daily_notification " \
                                  "YYYY-MM-DD HH:MM:SS"
    DISABLE_NOTIFICATION_SUCCESS = "{}, your daily notification for {} has been disabled"
    DISABLE_NOTIFICATION_NOTIFICATION_NOT_SET = "{}, you don't have daily notification enabled yet. Use " \
                                                "command /enable_daily_notification to enable daily notifications"
    UNKNOWN_COMMAND = "Sorry, I didn't understand that command. Please try \"\\start\" \"\\menu\" to interact " \
                      "with the bot"
    ERROR_MESSAGE = "Sorry, something went wrong!!!😟😟😟"
    HELP = "Use /start or /menu to use this bot."
