"Telegram API for summarize model."

import re
import os
import argparse
import telebot
from telebot.types import BotCommand
import yaml
from model_api import ModelAPI


def process_message(message: str):
    """
    Process message before saving it into the file. 
    Add spaces, treat each separate message as a sentence.

    """
    processed_message = ''
    if re.search(r"\w$", message):
        processed_message = message + '. '
    else:
        processed_message = message + ' '

    return processed_message

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-config',
                        dest="config",
                        default='./bot_config.yaml',
                        type=str,
                        help='')
    args = parser.parse_args()
    with open(args.config, "r", encoding='utf-8') as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.FullLoader)

    bot = telebot.TeleBot(config['BOT_TOKEN'], parse_mode=None)
    model_api = ModelAPI()

    commands = config['commands']

    @bot.message_handler(commands=[commands['change_ilanguage']['command']])
    def change_input_language(message):
        """
        Manually set language of accumulated messages to summarize.

        """
        model_api.set_input_language(message.text)
        bot.reply_to(message, commands['change_ilanguage']['reply'])

    @bot.message_handler(commands=[commands['change_mlanguage']['command']])
    def change_model_language(message):
        """
        Manually set language which model is trained on.

        """
        model_api.set_model_language(message.text)
        bot.reply_to(message, commands['change_mlanguage']['reply'])

    @bot.message_handler(commands=[commands['change_olanguage']['command']])
    def change_output_language(message):
        """
        Manually set language of output summary.

        """
        model_api.set_output_language(message.text)
        bot.reply_to(message, commands['change_olanguage']['reply'])

    @bot.message_handler(commands=[commands['check_messages']['command']])
    def check_stored_messages(message):
        """
        Print the content of file with accumulated messages.

        """
        bot.reply_to(message, commands['check_messages']['reply'])
        try:
            with open(config['fnames']['message_accumulator'], 'r',
                      encoding='utf-8') as fstream:
                content = fstream.readlines()
                bot.send_message(message.chat.id, content)
        except FileNotFoundError:
            bot.send_message(message.chat.id, config['misc_messages']['no_file_reply'])

    @bot.message_handler(commands=[commands['reset_messages']['command']])
    def delete_accumulated_messages(message):
        """
        Erase the file with accumulated messages.

        """
        try:
            os.remove(config['fnames']['message_accumulator'])
            bot.send_message(message.chat.id, commands['reset_messages']['reply'])
        except FileNotFoundError:
            bot.send_message(message.chat.id, config['misc_messages']['no_file_reply'])

    @bot.message_handler(commands=[commands['load_model']['command']])
    def load_model(message):
        """
        Load selected model, default - Remeris/BART-CNN-Convosumm

        """
        model_api.prepare_model()
        bot.send_message(message.chat.id, commands['load_model']['reply'])

    @bot.message_handler(commands=[commands['make_summary']['command']])
    def summarize(message):
        """
        Run model's inference pipeline.

        """
        bot.send_message(message.chat.id, commands['make_summary']['reply'])
        with open(config['fnames']['message_accumulator'], 'r',
                  encoding='utf-8') as fstream:
            messages = fstream.readline()
        model_answer = model_api.summarize(messages)
        bot.send_message(message.chat.id, model_answer)

    @bot.message_handler(commands=[commands['terminate_bot']['command']])
    def shutoff(message):
        """
        Disable bot, finish scipt run.

        """
        bot.send_message(message.chat.id, commands['terminate_bot']['reply'])
        bot.stop_polling()

    @bot.message_handler(commands=[commands['start']['command']])
    def show_command_menu(message):
        """
        Update bot command menu.

        """
        bot.send_message(message.chat.id, commands['start']['reply'])
        bot.set_my_commands(
            commands=[
                BotCommand(commands[key]['command'], commands[key]['description'])
                for key in commands
            ]
        )
        bot.set_chat_menu_button(message.chat.id,
                                 telebot.types.MenuButtonCommands('commands'))

    @bot.message_handler(content_types=['text'])
    def accumulate_messages(message):
        """
        Accumulate any given non-command text messages in file.

        """
        with open(config['fnames']['message_accumulator'], 'a',
                  encoding='utf-8') as fstream:
            text = process_message(message.text)
            fstream.write(text)

    bot.infinity_polling()
