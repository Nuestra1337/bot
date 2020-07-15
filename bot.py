from pyowm import OWM
from pyowm.utils.config import get_default_config
import telebot
import tokens
import COVID19Py

# Подключение и настройка библиотеки с API OpenWeatherMap
config_dict = get_default_config()
config_dict['language'] = 'ru'
owm = OWM(tokens.owm_token, config_dict)

# Подключение библиотеки Telebot
bot = telebot.TeleBot(tokens.bot_token)

# Подключение библиотеки COVID19py
# На случай, если сайт, с которого берутся данные, упадет
try:
    covid19 = COVID19Py.COVID19()
except:
    pass

# 
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}!\n'
                                      f'Я буду показывать для Вас погоду в любом городе.')


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, f'Чтобы узнать погоду, всего лишь отправьте название города.\n'
                                      f'Так же, если Вы хотите посмотреть статистику по COVID-19\n'
                                      f'наберите команды:\n '
                                      f'/covid - для статистики во всем мире\n'
                                      f'/covidru - для статистики в России')


@bot.message_handler(commands=['covid'])
def covid_message(message):
    # На случай, если сайт, с которого берутся данные, упадет
    try:
        world_statistic = covid19.getLatest()
        bot.send_message(message.chat.id,
                         f"Данные по всему миру:\n"
                         f"Заболевших: {world_statistic['confirmed']:,}\n"
                         f"Смертей: {world_statistic['deaths']:,}")
    except:
        bot.send_message(message.chat.id,"Ошибка подключения к серверу. Попробуйте позже")


@bot.message_handler(commands=['covidru'])
def covidru_message(message):
    try:
        russia_statistic = covid19.getLocationByCountryCode("RU")
        date = russia_statistic[0]['last_updated'].split("T")
        time = date[1].split(".")
        bot.send_message(message.chat.id, f"Данные по России:\n"
                                          f"Последнее обновление: {date[0]} {time[0]} (UTC +0)\n"
                                          f"Заболевших: {russia_statistic[0]['latest']['confirmed']:,}\n"
                                          f"Смертей: {russia_statistic[0]['latest']['deaths']:,}")
    except:
        bot.send_message(message.chat.id,"Ошибка подключения к серверу. Попробуйте позже")


@bot.message_handler(content_types=['text'])
def send_echo(message):
    mgr = owm.weather_manager()
    # Чтобы бот не ложился при неккоретном вводе города или некорректных данных
    try:
        observation = mgr.weather_at_place(message.text)
        w = observation.weather.detailed_status
        temp_dict_celsius = observation.weather.temperature('celsius')['temp']
        wind_dict_in_meters_per_sec = observation.weather.wind()['speed']
        message_from_bot = f'🏙: {message.text.title()}\n 🌤: {w}\n' \
                           f'🌡: {str(round(temp_dict_celsius))}°\n' \
                           f'🌬: {str(wind_dict_in_meters_per_sec)} м/c.\n'
        bot.send_message(message.chat.id, message_from_bot)
    except:
        bot.send_message(message.chat.id, "Ошибка! Попробуйте заново")


bot.polling(none_stop=True)
