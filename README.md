# Anime Recommender

A telegram bot anime recommender based on myanimelist.net data

## Usage

Send a message to `@ods1_bot` on telegram! If it does not respond, the server is probably down. You can't rise it yourself (would need my API key), but you can create your own bot from this repo. See the section below.

### Running your own bot

First, download both [myanimelist datasets](https://www.kaggle.com/CooperUnion/anime-recommendations-database) and put them under `data/raw_anime.csv` and `data/raw_rating.csv`.

Next, run `pipenv install` to install dependencies. Learn how to install pipenv [here](https://github.com/pypa/pipenv).

Last, `pipenv run main.py` will prompt your bot API key. You can read more about making your own telegram bot [here](https://core.telegram.org/bots).

Obs: I've configured the telegram bot to notify me of errors on `src/telegram_bot.py` under `error` function. I suggest you to change it to your own telegram ID ([how to  get your telegram user ID](https://bigone.zendesk.com/hc/en-us/articles/360008014894-How-to-get-the-Telegram-user-ID-)), so you can receive error notifications directly.

## Contributing

You can just leave an issue, but if you really want to contribute directly, just make sure to run `pre-commit install` and follow the code style.
