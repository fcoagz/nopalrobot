import telebot
from telebot.types import ReplyKeyboardMarkup, BotCommand
from keep_alive import keep_alive
import subprocess
import json
import os

filePath = os.getcwd() + '/file/'

ffmpeg_command = 'ffmpeg -i nopalINPUT.mp4 -f avi -r 10 -s {} -b 192k -bt 64k -vcodec libxvid -deinterlace -acodec libmp3lame -ar 32000 -ab 96k -ac 2 nopalOUTPUT.avi'

with open(os.getcwd() + '/configbot.json') as archive:
    botInfo = json.load(archive)

bot = telebot.TeleBot(botInfo['TOKEN'], parse_mode='HTML')

@bot.message_handler(commands=['start'])
def sendWelcome(message):
    bot.send_message(message.chat.id, '''<i>Bienvenido a NopalRobot 🌵.</i> Recuerda apoyar el repositorio para recibir mas actualizaciones de este bot! ve a <a href="https://github.com/fcoagz">GitHub</a>''', disable_web_page_preview=True)
    bot.send_message(message.chat.id, '''Envíame el vídeo que deseas convertir para poder verlo en la consola!''')

@bot.message_handler(content_types=['video'])
def recieveFile(message):
    msg = bot.send_message(message.chat.id, '''<i>Espere un momento! 🌵</i>''')
    fileID = message.video.file_id
    fileInfo = bot.get_file(file_id=fileID)
    downloadFile = bot.download_file(file_path=fileInfo.file_path)

    with open(filePath + 'nopalINPUT.mp4', 'wb') as newFile:
        newFile.write(downloadFile)

        buttonRES = ReplyKeyboardMarkup(resize_keyboard=True,
                                         one_time_keyboard=True,
                                           row_width=1).add(
            '256x192', '256x144'
                                           )
        
        bot.delete_message(message.chat.id, msg.message_id)
        bot.send_message(message.chat.id, '''Elige la resolución de video que prefieras descargar. Puedes seleccionar la calidad del video que deseas para asegurarte de que se adapte a tus necesidades y preferencias.''', reply_markup=buttonRES)
        bot.register_next_step_handler(msg, resVideo)

def resVideo(message):
    resolution = message.text
    if resolution == '256x144' or resolution == '256x192':
        msg = bot.send_message(message.chat.id, '''Este proceso puede tomar un tiempo, dependiendo de la duración y la calidad del video original.''')

        os.chdir(filePath)
        convert = subprocess.run(ffmpeg_command.format(resolution), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if convert.returncode == 0:
            bot.edit_message_text(text='''¡Excelente! El archivo de video que has solicitado se ha convertido con éxito.''',
                                  chat_id=message.chat.id,
                                  message_id=msg.message_id)
            
            content = os.listdir(filePath)

            removeMP4 = []
            for file in content:
                if os.path.isfile(os.path.join(filePath, file)) and file.endswith('.mp4'):
                    removeMP4.append(file)
                    os.remove(removeMP4[0])

            with os.scandir() as fileVideo:
                fileVideo = [file for file in fileVideo if file.is_file()]
            with open(fileVideo[0], 'rb') as video:
                bot.send_chat_action(message.chat.id, 'upload_video')
                bot.edit_message_text(text='''🌵 Enviando el vídeo...''',
                                 chat_id= message.chat.id,
                                 message_id= msg.message_id)
                bot.send_video(message.chat.id, video)
                bot.edit_message_text(text='''🌵 Muchas Gracias por usar Nopal-viBot!''',
                                 chat_id= message.chat.id,
                                 message_id= msg.message_id)
                os.remove('nopalOUTPUT.avi')
                
        else:
            bot.edit_message_text(text='''Se produjo un error al convertir el archivo de video.''',
                             chat_id= message.chat.id,
                             message_id= msg.message_id)
    else:
        msg = bot.send_message(message.chat.id, '''Lamentablemente, la resolución de video que has seleccionado no está disponible en este momento. Te recomendamos que elijas otra resolución disponible que se adapte a tus necesidades.''')
        bot.register_next_step_handler(msg, resVideo)

if __name__ == '__main__':    
    bot.set_my_commands([BotCommand(
        command='start',
        description='Iniciar con el bot'
    )])
    keep_alive()
    bot.infinity_polling()