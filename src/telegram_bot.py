import logging
import sys
import traceback
from random import choice

from jikanpy import Jikan
from telegram import ParseMode, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    Updater,
)
from telegram.utils.helpers import mention_html

from src.lib.recommender import Recommender

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

jikan = Jikan()
recommender = None

mal = {}

SET_USERNAME_1 = range(1)


def start(update, context):
    """Send a message when the command /start is issued."""
    user = update.message.from_user
    update.message.reply_text(
        f"Konichiwa {user.first_name}-san! Bem-vindo ao Majin Bot uwu"
    )
    logger.info(f"User {user.id} started the bot.")


def set_username(update, context):
    update.message.reply_text("Qual seu nome de usuário do MyAnimeList?")

    return SET_USERNAME_1


def set_username_1(update, context):
    mal_username = update.message.text.strip()
    user = update.message.from_user

    update.message.reply_text(
        "Pera aí, vou procurar seu nome de usuário, me dê um minuto..."
    )

    try:
        response = jikan.user(username=mal_username, request="animelist")
    except Exception as e:
        logger.info(e)
        update.message.reply_text(
            "Não consegui encontrar :(\n" "Tente novamente, por favor."
        )
        return ConversationHandler.END

    mal[user] = response["anime"]
    update.message.reply_text(
        f"Okay {user.first_name}, tudo certo!\n"
        "Use /recommend para receber uma recomendação especial :)"
    )

    logger.info(f"User {user.username} logged with {mal_username}.")

    return ConversationHandler.END


def recommend(update, context):
    user = update.message.from_user
    message = ""
    if user in mal:
        anime_id = recommender.recommend(mal[user])
        anime_name = recommender.get_anime_name(anime_id)

        possibilities = [
            f"{anime_name} é um bom anime! Dê uma olhada!\n",
            f"Que tal {anime_name}?\n",
            f"{anime_name} combina com seu otaku interior :3\n",
        ]
        if "aruto" in anime_name:
            possibilities = [f"Você certamente vai gostar de {anime_name}, tô certo!"]
        if "Jojo" in anime_name:
            possibilities = ["**Is That (recommendation) a JoJo Reference?**"]

        message = choice(possibilities)
    else:
        anime_id = recommender.recommend_from_top()
        anime_name = recommender.get_anime_name(anime_id)
        message = (
            "Hey! Parece que você não me disse seu nome de usuário do MyAnimeList.\n"
            "Me diga seu nome de usuário com /set_username.\n"
            "\n"
            f"Bom, mas que tal dar uma chance à {anime_name}?\n"
        )

    message += f"https://myanimelist.net/anime/{anime_id}"
    update.message.reply_text(message)


def cancel(update, context):
    user = update.message.from_user
    logger.info(f"User {user.first_name} canceled the operation.")

    update.message.reply_text("Operação cancelada!", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def stop(update, context):
    user = update.message.from_user
    if user in mal:
        del mal[user]
    update.message.reply_text("Espero te ver novamente em breve. Sayonara!")


def error(update, context):
    devs = [203939828]

    if update.effective_message:
        text = (
            "Eita! Um erro interno ocorreu enquanto eu tentava tratar sua requisição.\n"
            "Mas não se preocupe, meu desenvolvedor será notificado!"
        )
        update.effective_message.reply_text(text)

    trace = "".join(traceback.format_tb(sys.exc_info()[2]))
    payload = ""
    if update.effective_user:
        user = mention_html(update.effective_user.id, update.effective_user.first_name)
        payload += f" with the user {user}"

    if update.effective_chat:
        payload += f" within the chat <i>{update.effective_chat.title}</i>"
        if update.effective_chat.username:
            payload += f" (@{update.effective_chat.username})"

    if update.poll:
        payload += f" with the poll id {update.poll.id}."

    text = (
        f"The error <code>{context.error}</code> happened{payload}.\n"
        f"The full traceback:\n\n<code>{trace}</code>"
    )

    for dev_id in devs:
        context.bot.send_message(dev_id, text, parse_mode=ParseMode.HTML)

    raise


def main():
    global recommender
    recommender = Recommender()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("set_username", set_username)],
        states={SET_USERNAME_1: [MessageHandler(Filters.text, set_username_1)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    bot_token = input("Insert Majin Bot token = ")
    updater = Updater(bot_token, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("recommend", recommend))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_error_handler(error)

    print("Server is up.")

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
