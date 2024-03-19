from config import TELEGRAM_TOKEN
import telebot
import requests

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Definir el teclado de opciones
markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
markup.add('buscar anime', 'recomendar lista de 10 anime')

@bot.message_handler(commands=["start"])
def cmd_start(message):
    commands_list = "\n".join([
        "/start - Inicia la conversación",
        "comando: buscar anime",
        "comando: recomendar lista de 10 anime"
    ])
    bot.send_message(message.chat.id, f'Hola! ¿Qué deseas hacer?\n\nAquí tienes una lista de comandos disponibles:\n{commands_list}', reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if 'buscar anime' in message.text.lower():
        bot.reply_to(message, 'Por favor, envía una palabra clave para buscar anime.')
        bot.register_next_step_handler(message, buscar_anime)
    elif 'recomendar lista de 10 anime' in message.text.lower():
        recomendar_lista_anime(message)
    else:
        bot.reply_to(message, 'No entendí tu respuesta. Por favor, elige una opción válida.')

def buscar_anime(message):
    busqueda = message.text.lower()
    if not busqueda:
        bot.reply_to(message, 'Por favor, envía una palabra clave para buscar anime.')
        return

    url = f"https://api.jikan.moe/v4/anime?q={busqueda}&sfw"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanza una excepción si la respuesta es un error HTTP
        data = response.json()
        if "data" in data and data["data"]:
            anime = data["data"][0]
            respuesta = f"Título: {anime['title']}\n"
            if anime['genres']:
                respuesta += f"Género: {anime['genres'][0]['name']}\n"
            else:
                respuesta += "Género: Desconocido\n"
            respuesta += f"Sinopsis: {anime['synopsis']}"
            if "images" in anime and "jpg" in anime["images"]:
                image_url = anime["images"]["jpg"]["image_url"]
                bot.send_photo(message.chat.id, image_url)
            else:
                respuesta += "\n\nNo se pudo cargar la imagen del anime."
        else:
            respuesta = "No se encontraron resultados para la búsqueda."
    except requests.exceptions.HTTPError as err:
        print(err)
        respuesta = "Ocurrió un error al buscar el anime."

    bot.reply_to(message, respuesta)
    # Preguntar qué desea hacer después de mostrar la información del anime
    bot.send_message(message.chat.id, '¿Qué deseas hacer ahora?', reply_markup=markup)

def recomendar_lista_anime(message):
    try:
        url = "https://api.jikan.moe/v4/anime"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if "data" in data and data["data"]:
            top_animes = sorted(data["data"], key=lambda x: x["popularity"], reverse=True)[:10]  # Ordenar por popularidad y tomar los primeros 10 anime
            respuesta = "Aquí tienes una lista de 10 anime recomendados:\n"
            for anime in top_animes:
                respuesta += f"{anime['title']}\n"
        else:
            respuesta = "No se encontraron resultados para la búsqueda."
    except requests.exceptions.HTTPError as err:
        print(err)
        respuesta = "Ocurrió un error al buscar los anime."

    bot.reply_to(message, respuesta)
    # Preguntar qué desea hacer después de mostrar la lista de 10 anime
    bot.send_message(message.chat.id, '¿Qué deseas hacer ahora?', reply_markup=markup)


if __name__ == '__main__':
    print('Bot iniciado')
    bot.infinity_polling()
    print('Fin')