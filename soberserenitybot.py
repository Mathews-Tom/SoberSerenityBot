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
from strings import Strings
from utils import MenuElements


class SoberSerenity:
    Bot_UCM = namedtuple('Bot_UCM', 'update context message')

    def __init__(self, token) -> None:
        self.updater = Updater(token=token)
        self.dispatcher = self.updater.dispatcher

    def profile(self, update: Update, context: CallbackContext) -> None:
        """Get user profile."""
        user = get_user(update, context)
        msg = Strings.PROFILE.format(user["FirstName"], utils.get_user_profile_str(user))
        send_message(self.Bot_UCM(update, context, msg), reply_markup=bot_helper.main_menu_keyboard())

    def clean_time(self, update: Update, context: CallbackContext) -> None:
        """Reply with calculated clean time."""
        user = get_user(update, context)
        if user['CleanDateTime']:
            clean_date_time = utils.convert_str_to_datetime(user['CleanDateTime'])
            clean_time_str = database.get_clean_time_str(clean_date_time, user['UserID'])
            msg = f'{database.get_random_motivational_str()}\n\n' \
                  f'{Strings.CLEAN_TIME.format(clean_time_str[0], clean_time_str[1])}'
        else:
            msg = Strings.CLEAN_TIME_CLEAN_DATE_NOT_SET.format(user["FirstName"])
        send_message(self.Bot_UCM(update, context, msg), reply_markup=bot_helper.main_menu_keyboard())

    def readings(self, update: Update, context: CallbackContext) -> None:
        """Get reading for today."""
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
        """Get prayer."""
        update_context_with_user_data(update, context)
        if hasattr(update.message, 'text'):
            prayer = MenuElements[update.message.text[1:].upper()]
        else:
            ch = update.callback_query.data
            prayer = utils.get_menu_element_from_chr(ch)
        msg = database.get_prayer(prayer.value.name)
        send_message(self.Bot_UCM(update, context, msg), reply_markup=bot_helper.prayers_menu_keyboard())

    def set_utc_offset(self, update: Update, context: CallbackContext) -> None:
        """Set UTC offset."""
        user = get_user(update, context)
        inp = update.message.text.split()
        msg = Strings.UTC_OFFSET_FAILURE.format(user["FirstName"])
        if len(inp) == 2 and database.update_user_utc_time_offset(user['UserID'], inp[1]):
            msg = Strings.UTC_OFFSET_SUCCESS.format(inp[1])
        send_message(self.Bot_UCM(update, context, msg))

    def enable_daily_notification(self, update: Update, context: CallbackContext) -> None:
        """Enable daily notifications for clean time at user specified time."""
        user = get_user(update, context)
        user_job = get_daily_notification(context, user['UserID'])
        if user_job:
            notification_time = utils.convert_utc_time_to_local_time(user_job[0].job.next_run_time,
                                                                     database.get_time_offset(user["UserID"]))
            msg = Strings.ENABLE_NOTIFICATION_NOTIFICATION_ALREADY_SET.format(user["FirstName"],
                                                                              notification_time.time())
        else:
            msg = self.enable_daily_notification_set(update, context, user)
        send_message(self.Bot_UCM(update, context, msg), reply_markup=bot_helper.main_menu_keyboard())

    @staticmethod
    def enable_daily_notification_set(update: Update, context: CallbackContext, user: dict) -> str:
        inp = update.message.text.split()
        msg = Strings.ENABLE_NOTIFICATION_FAILURE.format(user["FirstName"])
        if len(inp) == 3:
            inp = update.message.text.split()
            inp = f'{inp[1]} {inp[2]}'
            time_local = utils.convert_str_to_datetime(inp)
            if time_local:
                offset = database.get_time_offset(user['UserID'])
                time_utc = utils.convert_local_time_to_utc_time(time_local, offset)
                user = get_user(update, context)
                context.job_queue.run_daily(notification_callback, days=tuple(range(7)), time=time_utc.time(),
                                            context=user['UserID'], name=str(user['UserID']))
                user["DailyNotification"] = str(time_local.time())
                database.update_daily_notification(user["UserID"], user["DailyNotification"])
                update_user(context, user)
                msg = Strings.ENABLE_NOTIFICATION_SUCCESS.format(user["FirstName"], time_local.time())
        return msg

    def disable_daily_notification(self, update: Update, context: CallbackContext) -> None:
        """Disable daily notifications for clean time."""
        user = get_user(update, context)
        user_job = get_daily_notification(context, user['UserID'])
        if user_job:
            notification_time = utils.convert_utc_time_to_local_time(user_job[0].job.next_run_time,
                                                                     database.get_time_offset(user['UserID']))
            user_job[0].schedule_removal()
            user["DailyNotification"] = ""
            database.update_daily_notification(user["UserID"], user["DailyNotification"])
            update_user(context, user)
            msg = Strings.DISABLE_NOTIFICATION_SUCCESS.format(user["FirstName"], notification_time.time())
        else:
            user["DailyNotification"] = ""
            database.update_daily_notification(user["UserID"], user["DailyNotification"])
            update_user(context, user)
            msg = Strings.DISABLE_NOTIFICATION_NOTIFICATION_NOT_SET.format(user["FirstName"])
        send_message(self.Bot_UCM(update, context, msg), reply_markup=bot_helper.main_menu_keyboard())

    def help_command(self, update: Update, context: CallbackContext) -> None:
        """Displays info on how to use the bot."""
        # update.message.reply_text("Use /start or /menu to use this bot.")
        msg = Strings.HELP
        send_message(self.Bot_UCM(update, context, msg))

    def error_handler(self, update: Update, context: CallbackContext) -> None:
        """Error handler."""
        msg = Strings.ERROR_MESSAGE
        send_message(self.Bot_UCM(update, context, msg))
        print(f'Update {update} caused error {context.error}')

    def run(self) -> None:
        def get_command_handlers() -> Enum:
            """Command Handlers.

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

        def get_callback_query_handler() -> Enum:
            """Callback Query Handlers.

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
    """Update context.user_data with UserProfile data."""
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
    """Get user from user_data in context."""
    update_context_with_user_data(update, context)
    key = list(context.user_data.keys())[0] if context.user_data else 'KeyNotFound'
    return context.user_data.get(key, {})


def update_user(context: CallbackContext, user: dict) -> None:
    key = list(context.user_data.keys())[0] if context.user_data else 'KeyNotFound'
    context.user_data[key] = user


def start(update: Update, context: CallbackContext) -> None:
    """Sends a message with three inline buttons attached."""
    update_context_with_user_data(update, context)
    update.message.reply_text(bot_helper.main_menu_message(), reply_markup=bot_helper.main_menu_keyboard())


def menu(update: Update, context: CallbackContext, message, keyboard) -> None:
    """General menu control."""
    update_context_with_user_data(update, context)
    query = update.callback_query
    query.answer()
    query.message.reply_text(message, reply_markup=keyboard)


def main_menu(update: Update, context: CallbackContext) -> None:
    """Main menu."""
    menu(update, context, bot_helper.main_menu_message(), bot_helper.main_menu_keyboard())


def readings_menu(update: Update, context: CallbackContext) -> None:
    """Readings menu."""
    menu(update, context, bot_helper.readings_menu_message(), bot_helper.readings_menu_keyboard())


def prayers_menu(update: Update, context: CallbackContext) -> None:
    """Prayers menu."""
    menu(update, context, bot_helper.prayers_menu_message(), bot_helper.prayers_menu_keyboard())


def send_message(bot_ucm: SoberSerenity.Bot_UCM, reply_markup: ReplyMarkup = None) -> None:
    """Send message."""
    answer_callback_query(bot_ucm.update)
    user = get_user(bot_ucm.update, bot_ucm.context)
    bot_ucm.context.bot.sendMessage(chat_id=user['UserID'],
                                    text=bot_ucm.message,
                                    parse_mode=ParseMode.HTML,
                                    reply_markup=reply_markup)


def notification_callback(context: CallbackContext) -> None:
    """Notification callback."""
    user_chat_id = int(str(context.job.context))
    user = database.get_user(user_chat_id)
    if user['CleanDateTime']:
        quote = database.get_random_motivational_str()
        clean_date_time = utils.convert_str_to_datetime(str(user['CleanDateTime']))
        clean_time_str = database.get_clean_time_str(clean_date_time, user['UserID'])
        msg = Strings.CLEAN_TIME.format(clean_time_str[0], clean_time_str[1])
        context.bot.send_message(chat_id=user['UserID'], text=f'{quote}\n\n{msg}')


def get_daily_notification(context: CallbackContext, user_id) -> tuple:
    """Get enabled daily notification jobs for user."""
    user_job = context.job_queue.get_jobs_by_name(str(user_id))
    return user_job


def answer_callback_query(update: Update) -> None:
    """Answer Callback Query."""
    if hasattr(update.callback_query, "answer"):
        update.callback_query.answer()


def unknown_command(update: Update, context: CallbackContext) -> None:
    """Unknown command handler."""
    msg = Strings.UNKNOWN_COMMAND
    context.bot.sendMessage(chat_id=update.message.chat_id, text=msg)


if __name__ == '__main__':
    load_dotenv()
    sober_serenity_token = os.environ.get('SOBER_SERENITY_TOKEN')
    bot = SoberSerenity(sober_serenity_token)
    bot.run()
