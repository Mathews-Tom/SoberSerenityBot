#!/usr/bin/env python3
import os
from collections import namedtuple
from enum import Enum
from uuid import uuid4

from dotenv import load_dotenv
from telegram import (
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

import bot_helper
import database
import utils
from utils import MenuElements


class SoberSerenity:
    Bot_UCM = namedtuple('Bot_UCM', 'update context message')

    def __init__(self, token):
        self.updater = Updater(token=token)
        self.dispatcher = self.updater.dispatcher

    def clean_time(self, update: Update, context: CallbackContext) -> None:
        """Reply with calculated clean time."""
        user = get_user(update, context)
        if user['CleanDateTime']:
            clean_date_time = utils.convert_str_to_datetime(user['CleanDateTime'])
            msg = f'{database.get_random_motivational_str()}\n\n' \
                  f'{database.get_clean_time(clean_date_time, user["UserID"])}'
        else:
            msg = f'{user["FirstName"]}, you haven\'t set your profile yet. Please set user profile with clean date' \
                  f' to get clean time data.'
        send_message(self.Bot_UCM(update, context, msg), reply_markup=bot_helper.main_menu_keyboard())

    def readings(self, update: Update, context: CallbackContext) -> None:
        """Get reading for today [default] or a specific date [user input]."""
        update_context_with_user_data(update, context)
        if hasattr(update.message, 'text'):
            inp = update.message.text.split()
            reading = MenuElements[inp[0][1:].upper()].value.name
        else:
            ch = update.callback_query.data
            reading = utils.get_menu_element_from_chr(ch).value.name
        user = get_user(update, context)
        local_dt = database.get_user_local_time(user['UserID'])
        msg = database.get_reading(reading, local_dt)
        send_message(self.Bot_UCM(update, context, msg), reply_markup=bot_helper.readings_menu_keyboard())

    def prayers(self, update: Update, context: CallbackContext) -> None:
        """Get prayer"""
        update_context_with_user_data(update, context)
        if hasattr(update.message, 'text'):
            prayer = MenuElements[update.message.text[1:].upper()]
        else:
            ch = update.callback_query.data
            prayer = utils.get_menu_element_from_chr(ch)
        msg = database.get_prayer(prayer.value.name)
        send_message(self.Bot_UCM(update, context, msg), reply_markup=bot_helper.prayers_menu_keyboard())

    def profile(self, update: Update, context: CallbackContext) -> None:
        """Get user profile"""
        user = get_user(update, context)
        user_job = get_daily_notification(context, user['UserID'])
        msg = f'{user["FirstName"]}, I know the following about you\n{database.get_user_profile(user, user_job)}'
        send_message(self.Bot_UCM(update, context, msg), reply_markup=bot_helper.main_menu_keyboard())

    def set_utc_offset(self, update: Update, context: CallbackContext) -> None:
        """Set UTC offset"""
        user = get_user(update, context)
        inp = update.message.text.split()
        msg = f'Sorry {user["FirstName"]}, Please include offset in the format "+/-HH:MM" after the command'
        if len(inp) == 2 and database.update_user_utc_time_offset(user['UserID'], inp[1]):
            msg = f'User time offset set to: {inp[1]}'
        send_message(self.Bot_UCM(update, context, msg))

    def enable_daily_notification(self, update: Update, context: CallbackContext):
        """Enable daily notifications for clean time at user specified time"""
        user = get_user(update, context)
        user_job = get_daily_notification(context, user['UserID'])
        if user_job:
            notification_time = utils.convert_utc_time_to_local_time(user_job[0].job.next_run_time,
                                                                     database.get_time_offset(user['UserID']))
            msg = f'{user["FirstName"]}, your daily notification is already enabled for user for: ' \
                  f'{notification_time.time()}.\n<i>To update notification time, first disable and then enable ' \
                  f'daily notification with updated time.</i>'
        else:
            inp = update.message.text.split()
            if len(inp) == 3:
                inp = update.message.text.split()
                inp = f'{inp[1]} {inp[2]}'
                time_local = utils.convert_str_to_datetime(inp)
                offset = database.get_time_offset(user['UserID'])
                time_utc = utils.convert_local_time_to_utc_time(time_local, offset)
                user = get_user(update, context)
                context.job_queue.run_daily(notification_callback, days=tuple(range(7)), time=time_utc,
                                            context=user['UserID'], name=str(user['UserID']))
                msg = f'Great {user["FirstName"]}, I have enabled daily notifications for: {time_local.time()}'
            else:
                msg = f'{user["FirstName"]}, to enable daily notifications, please provide date time in format ' \
                      f'"YYYY-MM-DD HH:MM:SS" with current date after the command'
        send_message(self.Bot_UCM(update, context, msg), reply_markup=bot_helper.main_menu_keyboard())

    def disable_daily_notification(self, update: Update, context: CallbackContext):
        """Disable daily notifications for clean time"""
        user = get_user(update, context)
        user_job = get_daily_notification(context, user['UserID'])
        if user_job:
            notification_time = utils.convert_utc_time_to_local_time(user_job[0].job.next_run_time,
                                                                     database.get_time_offset(user['UserID']))
            user_job[0].schedule_removal()
            msg = f'{user["FirstName"]}, your daily notification for {notification_time.time()} has been disabled'
        else:
            msg = f'{user["FirstName"]}, you don\'t have daily notification enabled yet. Use ' \
                  f'"/enable_daily_notification" to enable daily notifications'
        send_message(self.Bot_UCM(update, context, msg), reply_markup=bot_helper.main_menu_keyboard())

    def help_command(self, update: Update, context: CallbackContext) -> None:
        """Displays info on how to use the bot."""
        # update.message.reply_text("Use /start or /menu to use this bot.")
        msg = "Use /start or /menu to use this bot."
        send_message(self.Bot_UCM(update, context, msg))

    def error_handler(self, update: Update, context: CallbackContext) -> None:
        """Error handler"""
        msg = "Sorry, something went wrong!!!😟😟😟"
        send_message(self.Bot_UCM(update, context, msg))
        print(f'Update {update} caused error {context.error}')

    def run(self):
        def get_command_handlers():
            """
            Command Handlers

            :return: Command handlers as an enum in the format KEY_WORD -> CommandHandler(command, callback)
            """
            Command_Handler = namedtuple('CommandHandler', 'command callback')
            command_keys = ["START", "MENU", "PROFILE", "CLEAN_TIME", "DAILY_REFLECTION", "JUST_FOR_TODAY",
                            "LORDS_PRAYER", "SERENITY_PRAYER", "ST_JOSEPHS_PRAYER", "TENDER_AND_COMPASSIONATE_GOD",
                            "THIRD_STEP_PRAYER", "SEVENTH_STEP_PRAYER", "ELEVENTH_STEP_PRAYER",
                            "ENABLE_DAILY_NOTIFICATION", "DISABLE_DAILY_NOTIFICATION", "SET_UTC_OFFSET", "HELP"]
            commands_name = ['start', 'menu', 'profile', 'clean_time', 'daily_reflection', 'just_for_today',
                             'lords_prayer', 'serenity_prayer', 'st_josephs_prayer', 'tender_and_compassionate_god',
                             'third_step_prayer', 'seventh_step_prayer', 'eleventh_step_prayer',
                             'enable_daily_notification', 'disable_daily_notification', 'set_utc_offset', 'help']
            command_callbacks = [start, start, self.profile, self.clean_time, self.readings, self.readings,
                                 self.prayers, self.prayers, self.prayers, self.prayers, self.prayers, self.prayers,
                                 self.prayers, self.enable_daily_notification, self.disable_daily_notification,
                                 self.set_utc_offset, self.help_command]
            return Enum('Commands', {k: Command_Handler(command=v1, callback=v2)
                                     for k, v1, v2 in zip(command_keys, commands_name, command_callbacks)})

        def get_callback_query_handler():
            """
            Callback Query Handlers

            :return: Callback query handlers as an enum in the format
                     KEY_WORD -> CallbackQueryHandler(callback, pattern)
            """
            Callback_Query_Handler = namedtuple('CallbackQueryHandler', 'callback pattern')
            callback_keys = ["MAIN_MENU", "PROFILE", "CLEAN_TIME", "READINGS_MENU", "PRAYERS_MENU", "READINGS",
                             "PRAYERS"]
            callback_name = [main_menu, self.profile, self.clean_time, readings_menu, prayers_menu,
                             self.readings, self.prayers]
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
            callback_pattern = [MenuElements.MAIN_MENU.value.data, MenuElements.PROFILE.value.data,
                                MenuElements.CLEAN_TIME.value.data, MenuElements.READINGS.value.data,
                                MenuElements.PRAYERS.value.data, readings_pattern, prayers_pattern]

            return Enum('CallbackQueries', {k: Callback_Query_Handler(callback=v1, pattern=v2)
                                            for k, v1, v2 in zip(callback_keys, callback_name, callback_pattern)})

        # Command Handlers
        commands = get_command_handlers()
        for cmd in commands:
            self.dispatcher.add_handler(CommandHandler(command=cmd.value.command, callback=cmd.value.callback))

        # Callback Query Handlers
        callback_queries = get_callback_query_handler()
        for cbk in callback_queries:
            self.dispatcher.add_handler(CallbackQueryHandler(callback=cbk.value.callback, pattern=cbk.value.pattern))

        # MessageHandler
        self.dispatcher.add_handler(MessageHandler(Filters.command, unknown_command))

        # ErrorHandler
        self.dispatcher.add_error_handler(self.error_handler)

        # Start the Bot
        self.updater.start_polling()

        # Run the bot until the user presses Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
        self.updater.idle()
        return


def update_context_with_user_data(update: Update, context: CallbackContext) -> None:
    """Update context.user_data with UserProfile data"""
    # Update needed only when context.user_data is empty
    if context.user_data:
        return
    if hasattr(update.callback_query, 'message'):
        chat = update.callback_query.message.chat
    else:
        chat = update.message.chat
    user = database.create_user(chat)
    key = str(uuid4())
    context.user_data[key] = user


def get_user(update: Update, context: CallbackContext) -> dict:
    """Get user from user_data in context"""
    update_context_with_user_data(update, context)
    key = list(context.user_data.keys())[0] if context.user_data else 'KeyNotFound'
    return context.user_data.get(key, {})


def start(update: Update, context: CallbackContext) -> None:
    """Sends a message with three inline buttons attached."""
    update_context_with_user_data(update, context)
    update.message.reply_text(bot_helper.main_menu_message(), reply_markup=bot_helper.main_menu_keyboard())


def menu(update: Update, context: CallbackContext, message, keyboard) -> None:
    update_context_with_user_data(update, context)
    query = update.callback_query
    query.answer()
    query.message.reply_text(message, reply_markup=keyboard)


def main_menu(update: Update, context: CallbackContext) -> None:
    menu(update, context, bot_helper.main_menu_message(), bot_helper.main_menu_keyboard())


def readings_menu(update: Update, context: CallbackContext):
    menu(update, context, bot_helper.readings_menu_message(), bot_helper.readings_menu_keyboard())


def prayers_menu(update: Update, context: CallbackContext) -> None:
    menu(update, context, bot_helper.prayers_menu_message(), bot_helper.prayers_menu_keyboard())


def send_message(bot_ucm: SoberSerenity.Bot_UCM, reply_markup: ReplyMarkup = None) -> None:
    answer_callback_query(bot_ucm.update)
    user = get_user(bot_ucm.update, bot_ucm.context)
    bot_ucm.context.bot.sendMessage(chat_id=user['UserID'],
                                    text=bot_ucm.message,
                                    parse_mode=ParseMode.HTML,
                                    reply_markup=reply_markup)


def notification_callback(context: CallbackContext) -> None:
    """Notification callback"""
    user_chat_id = int(str(context.job.context))
    user = database.get_user(user_chat_id)
    if user['CleanDateTime']:
        quote = database.get_random_motivational_str()
        clean_date_time = utils.convert_str_to_datetime(str(user['CleanDateTime']))
        msg = database.get_clean_time(clean_date_time, user['UserID'])
        context.bot.send_message(chat_id=user['UserID'], text=f'{quote}\n\n{msg}')


def get_daily_notification(context: CallbackContext, user_id) -> tuple:
    """Get enabled daily notification jobs for user"""
    user_job = context.job_queue.get_jobs_by_name(str(user_id))
    return user_job


def answer_callback_query(update: Update) -> None:
    if hasattr(update.callback_query, "answer"):
        update.callback_query.answer()


def unknown_command(update: Update, context: CallbackContext) -> None:
    msg = "Sorry, I didn't understand that command. Please try \"\\start\" \"\\menu\" to interact with the bot"
    context.bot.sendMessage(chat_id=update.message.chat_id, text=msg)


if __name__ == '__main__':
    load_dotenv()
    sober_serenity_token = os.environ.get('SOBER_SERENITY_TOKEN')
    bot = SoberSerenity(sober_serenity_token)
    bot.run()
