#!/usr/bin/env python3

import os
from collections import namedtuple
from enum import Enum
from uuid import uuid4

from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    ParseMode, ReplyMarkup,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    MessageHandler,
    Filters
)

import utils
from utils import MenuElements


class SoberSerenity:
    Bot_UCM = namedtuple('Bot_UCM', 'update context message')

    def __init__(self, token):
        self.updater = Updater(token=token)
        self.dispatcher = self.updater.dispatcher

    @staticmethod
    def main_menu_keyboard():
        """Main menu keyboard"""
        keyboard = [
            [InlineKeyboardButton("⏳ Clean Time ⏳", callback_data=str(MenuElements.CLEAN_TIME.value.data))],
            [
                InlineKeyboardButton("📚 Readings 📚", callback_data=str(MenuElements.READINGS.value.data)),
                InlineKeyboardButton("🙏 Prayers 🙏", callback_data=str(MenuElements.PRAYERS.value.data)),
            ],
        ]
        return InlineKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def readings_menu_keyboard():
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

    @staticmethod
    def prayers_menu_keyboard():
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

    @staticmethod
    def main_menu_message():
        """Main menu message"""
        return 'Hi, I am the Sober Serenity Bot. ⚖️🕊⚖️🕊⚖️🕊️ \n\n\nI am here to help and guide you through your ' \
               'process of Sobriety, be it for yourself or if you are trying to help out someone you care about. ' \
               'Here are few things I can be of help to you. Please chose :: '

    @staticmethod
    def readings_menu_message():
        """Reading menu message"""
        return 'Readings help to feel comforted during our journey of recovery and sobriety and to gain strength. ' \
               'We learn that today is a gift with no guarantees. With this in mind, the insignificance of the past ' \
               'and future, and the importance of our actions today, become real for us. This simplifies our lives.'

    @staticmethod
    def prayers_menu_message():
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

    @staticmethod
    def update_context_with_user_data(update: Update, context: CallbackContext) -> None:
        """Update context.user_data with UserProfile data"""
        # Update needed only when context.user_data is empty
        if context.user_data:
            return

        if hasattr(update.callback_query, 'message'):
            chat = update.callback_query.message.chat
        else:
            chat = update.message.chat

        user = utils.create_user(chat)
        key = str(uuid4())
        context.user_data[key] = user

    def start(self, update: Update, context: CallbackContext) -> None:
        """Sends a message with three inline buttons attached."""
        self.update_context_with_user_data(update, context)
        update.message.reply_text(self.main_menu_message(), reply_markup=self.main_menu_keyboard())

    def main_menu(self, update: Update, context: CallbackContext) -> None:
        self.update_context_with_user_data(update, context)
        query = update.callback_query
        query.answer()
        query.message.reply_text(self.main_menu_message(), reply_markup=self.main_menu_keyboard())

    def readings_menu(self, update: Update, context: CallbackContext):
        self.update_context_with_user_data(update, context)
        query = update.callback_query
        query.message.reply_text(self.readings_menu_message(), reply_markup=self.readings_menu_keyboard())
        query.answer()

    def prayers_menu(self, update: Update, context: CallbackContext) -> None:
        self.update_context_with_user_data(update, context)
        query = update.callback_query
        query.answer()
        query.message.reply_text(self.prayers_menu_message(), reply_markup=self.prayers_menu_keyboard())

    def clean_time(self, update: Update, context: CallbackContext) -> None:
        """Reply with calculated clean time."""
        user = self.__get_user(update, context)
        if user['CleanDateTime']:
            clean_date_time = utils.convert_str_to_datetime(user['CleanDateTime'])
            msg = f'{utils.get_random_motivational_str()}\n\n{utils.get_clean_time(clean_date_time)}'
        else:
            msg = f'{user["FirstName"]}, you haven\'t set your profile yet. Please set user profile with clean date' \
                  f' to get clean time data.'
        self.__answer_callback_query(update)
        self.__send_message(self.Bot_UCM(update, context, msg), reply_markup=self.main_menu_keyboard())

    def readings(self, update: Update, context: CallbackContext) -> None:
        """Get reading for today [default] or a specific date [user input]."""
        self.update_context_with_user_data(update, context)
        if hasattr(update.message, 'text'):
            inp = update.message.text.split()
            reading = MenuElements[inp[0][1:].upper()].value.name
            dt = utils.convert_str_to_datetime(inp[1])
            if not dt:
                user = self.__get_user(update, context)
                msg = f'Sorry {user["FirstName"]}, I don\'t understand that date time format. Please provide date ' \
                      f'time in format "YYYY-MM-DD HH:MM:SS" or "YYY-MM-DD"'
            else:
                msg = utils.get_reading(reading, dt)
        else:
            ch = update.callback_query.data
            reading = utils.get_menu_element_from_chr(ch).value.name
            msg = utils.get_reading(reading)
        self.__answer_callback_query(update)
        self.__send_message(self.Bot_UCM(update, context, msg), reply_markup=self.main_menu_keyboard())

    def prayers(self, update: Update, context: CallbackContext) -> None:
        """Get prayer"""
        self.update_context_with_user_data(update, context)
        if hasattr(update.message, 'text'):
            prayer = MenuElements[update.message.text[1:].upper()]
        else:
            ch = update.callback_query.data
            prayer = utils.get_menu_element_from_chr(ch)
        msg = utils.get_prayer(prayer.value.name)
        self.__answer_callback_query(update)
        self.__send_message(self.Bot_UCM(update, context, msg), reply_markup=self.main_menu_keyboard())

    def profile(self, update: Update, context: CallbackContext):
        """Get user profile"""
        user = self.__get_user(update, context)
        user_job = self.__get_daily_notification(context, user['UserID'])
        msg = f'{user["FirstName"]}, I know the following about you\n{utils.get_user_profile(user, user_job)}'
        self.__send_message(self.Bot_UCM(update, context, msg))

    def set_utc_offset(self, update: Update, context: CallbackContext) -> None:
        """Set UTC offset"""
        user = self.__get_user(update, context)
        inp = update.message.text.split()
        if len(inp) == 2:
            if utils.update_user_utc_time_offset(user['UserID'], inp[1]):
                msg = f'User time offset set to: {inp[1]}'
                self.__send_message(self.Bot_UCM(update, context, msg))
            else:
                msg = f'Sorry {user["FirstName"]}, I don\'t understand that offset format. Please provide offset ' \
                      f'in the format "+/-HH:MM"'
                self.__send_message(self.Bot_UCM(update, context, msg))

    def enable_daily_notification(self, update: Update, context: CallbackContext):
        """Enable daily notifications for clean time at user specified time"""
        user = self.__get_user(update, context)
        user_job = self.__get_daily_notification(context, user['UserID'])
        if user_job:
            notification_time = utils.convert_utc_time_to_local_time(user_job[0].job.next_run_time,
                                                                     utils.get_time_offset(user['UserID']))
            msg = f'{user["FirstName"]}, your daily notification is already enabled for user for: ' \
                  f'{notification_time.time()}.\n<i>To update notification time, first disable and then enable ' \
                  f'daily notification with updated time.</i>'
            self.__send_message(self.Bot_UCM(update, context, msg))
        else:
            inp = update.message.text.split()
            if len(inp) == 3:
                inp = update.message.text.split()
                inp = f'{inp[1]} {inp[2]}'
                time_local = utils.convert_str_to_datetime(inp)
                offset = utils.get_time_offset(user['UserID'])
                time_utc = utils.convert_local_time_to_utc_time(time_local, offset)
                user = self.__get_user(update, context)
                context.job_queue.run_daily(self.notification_callback, days=tuple(range(7)), time=time_utc,
                                            context=user['UserID'], name=str(user['UserID']))
                msg = f'Great {user["FirstName"]}, I have enabled daily notifications for: {time_local.time()}'
                self.__send_message(self.Bot_UCM(update, context, msg))
            else:
                msg = f'Sorry {user["FirstName"]}, I don\'t understand that date time format. Please provide date ' \
                      f'time in format "YYYY-MM-DD HH:MM:SS" with current date'
                self.__send_message(self.Bot_UCM(update, context, msg))

    def disable_daily_notification(self, update: Update, context: CallbackContext):
        """Disable daily notifications for clean time"""
        user = self.__get_user(update, context)
        user_job = self.__get_daily_notification(context, user['UserID'])
        if user_job:
            notification_time = utils.convert_utc_time_to_local_time(user_job[0].job.next_run_time,
                                                                     utils.get_time_offset(user['UserID']))
            user_job[0].schedule_removal()
            msg = f'{user["FirstName"]}, your daily notification for {notification_time.time()} has been disabled'
            self.__send_message(self.Bot_UCM(update, context, msg))
        else:
            msg = f'{user["FirstName"]}, you don\'t have daily notification enabled yet. Use ' \
                  f'"/enable_daily_notification" to enable daily notifications'
            self.__send_message(self.Bot_UCM(update, context, msg))

    def __get_user(self, update: Update, context: CallbackContext) -> dict:
        """Get user from user_data in context"""
        self.update_context_with_user_data(update, context)
        key = list(context.user_data.keys())[0] if context.user_data else 'KeyNotFound'
        return context.user_data.get(key, {})

    @staticmethod
    def __get_daily_notification(context: CallbackContext, user_id) -> tuple:
        """Get enabled daily notification jobs for user"""
        user_job = context.job_queue.get_jobs_by_name(str(user_id))
        return user_job

    @staticmethod
    def notification_callback(context: CallbackContext) -> None:
        """Notification callback"""
        user_chat_id = int(context.job.context)
        user = utils.get_user(user_chat_id)
        if user['CleanDateTime']:
            quote = utils.get_random_motivational_str()
            clean_date_time = utils.convert_str_to_datetime(str(user['CleanDateTime']))
            msg = utils.get_clean_time(clean_date_time)
            context.bot.send_message(chat_id=user['UserID'], text=f'{quote}\n\n{msg}')

    def help_command(self, update: Update, context: CallbackContext) -> None:
        """Displays info on how to use the bot."""
        # update.message.reply_text("Use /start or /menu to use this bot.")
        msg = "Use /start or /menu to use this bot."
        self.__send_message(self.Bot_UCM(update, context, msg))

    @staticmethod
    def unknown_command(update: Update, context: CallbackContext) -> None:
        msg = "Sorry, I didn't understand that command. Please try \"\\start\" \"\\menu\" to interact with the bot"
        context.bot.sendMessage(chat_id=update.message.chat_id, text=msg)

    def error_handler(self, update: Update, context: CallbackContext) -> None:
        msg = "Sorry, something went wrong!!!😟😟😟"
        try:
            self.__send_message(self.Bot_UCM(update, context, msg))
            print(f'Update {update} caused error {context.error}')
        except AttributeError:
            print(msg)

    @staticmethod
    def __answer_callback_query(update: Update) -> None:
        try:
            update.callback_query.answer()
        except AttributeError:
            pass

    def __send_message(self, bot_ucm: Bot_UCM, reply_markup: ReplyMarkup = None) -> None:
        user = self.__get_user(bot_ucm.update, bot_ucm.context)
        bot_ucm.context.bot.sendMessage(chat_id=user['UserID'],
                                        text=bot_ucm.message,
                                        parse_mode=ParseMode.HTML,
                                        reply_markup=reply_markup)

    def run(self):
        def create_command_handlers():
            """
            Command Handlers

            :return: Command handlers as an enum in the format KEY_WORD -> CommandHandler(command, callback)
            """
            Command_Handler = namedtuple('CommandHandler', 'command callback')
            command_keys = ["START", "MENU", "CLEAN_TIME", "READINGS", "PRAYERS", "DAILY_REFLECTION", "JUST_FOR_TODAY",
                            "LORDS_PRAYER", "SERENITY_PRAYER", "ST_JOSEPHS_PRAYER", "TENDER_AND_COMPASSIONATE_GOD",
                            "THIRD_STEP_PRAYER", "SEVENTH_STEP_PRAYER", "ELEVENTH_STEP_PRAYER", "PROFILE",
                            "ENABLE_DAILY_NOTIFICATION", "DISABLE_DAILY_NOTIFICATION", "SET_UTC_OFFSET", "HELP"]
            commands_name = ['start', 'menu', 'clean_time', 'daily_reflection', 'just_for_today', 'lords_prayer',
                             'serenity_prayer', 'st_josephs_prayer', 'tender_and_compassionate_god',
                             'third_step_prayer',
                             'seventh_step_prayer', 'eleventh_step_prayer', 'profile', 'enable_daily_notification',
                             'disable_daily_notification', 'set_utc_offset', 'help']
            command_callbacks = [self.start, self.start, self.clean_time, self.readings, self.readings, self.prayers,
                                 self.prayers, self.prayers, self.prayers, self.prayers, self.prayers, self.prayers,
                                 self.profile, self.enable_daily_notification, self.disable_daily_notification,
                                 self.set_utc_offset, self.help_command]
            return Enum('Commands', {k: Command_Handler(command=v1, callback=v2)
                                     for k, v1, v2 in zip(command_keys, commands_name, command_callbacks)})

        def create_callback_query_handler():
            """
            Callback Query Handlers

            :return: Callback query handlers as an enum in the format
                     KEY_WORD -> CallbackQueryHandler(callback, pattern)
            """
            Callback_Query_Handler = namedtuple('CallbackQueryHandler', 'callback pattern')
            callback_keys = ["MAIN_MENU", "CLEAN_TIME", "READINGS_MENU", "PRAYERS_MENU", "READINGS", "PRAYERS"]
            callback_name = [self.main_menu, self.clean_time, self.readings_menu, self.prayers_menu, self.readings,
                             self.prayers]
            # Reading patterns
            readings_pattern = f'({MenuElements.DAILY_REFLECTION.value.data}' \
                               f'|{MenuElements.JUST_FOR_TODAY.value.data})'
            # Prayer patterns
            prayers_pattern = f'({MenuElements.LORDS_PRAYER.value.data}' \
                              f'|{MenuElements.SERENITY_PRAYER.value.data}' \
                              f'|{MenuElements.ST_JOSEPHS_PRAYER.value.data}' \
                              f'|{MenuElements.TENDER_AND_COMPASSIONATE_GOD.value.data}' \
                              f'|{MenuElements.THIRD_STEP_PRAYER.value.data}' \
                              f'|{MenuElements.SEVENTH_STEP_PRAYER.value.data}' \
                              f'|{MenuElements.ELEVENTH_STEP_PRAYER.value.data})'
            callback_pattern = [MenuElements.MAIN_MENU.value.data, MenuElements.CLEAN_TIME.value.data,
                                MenuElements.READINGS.value.data, MenuElements.PRAYERS.value.data, readings_pattern,
                                prayers_pattern]

            return Enum('CallbackQueries', {k: Callback_Query_Handler(callback=v1, pattern=v2)
                                            for k, v1, v2 in zip(callback_keys, callback_name, callback_pattern)})

        # Command Handlers
        commands = create_command_handlers()
        for cmd in commands:
            self.dispatcher.add_handler(CommandHandler(command=cmd.value.command, callback=cmd.value.callback))

        # Callback Query Handlers
        callback_queries = create_callback_query_handler()
        for cbk in callback_queries:
            self.dispatcher.add_handler(CallbackQueryHandler(callback=cbk.value.callback, pattern=cbk.value.pattern))

        # MessageHandler
        self.dispatcher.add_handler(MessageHandler(Filters.command, self.unknown_command))

        # ErrorHandler
        self.dispatcher.add_error_handler(self.error_handler)

        # Start the Bot
        self.updater.start_polling()

        # Run the bot until the user presses Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
        self.updater.idle()
        return


if __name__ == '__main__':
    load_dotenv()
    SOBER_SERENITY_TOKEN = os.environ.get('SOBER_SERENITY_TOKEN')
    bot = SoberSerenity(SOBER_SERENITY_TOKEN)
    bot.run()
