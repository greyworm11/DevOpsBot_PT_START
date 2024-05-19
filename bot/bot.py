import logging
import re
import paramiko
import psycopg2
import subprocess
import os
from dotenv import load_dotenv, find_dotenv

from telegram import Update, ForceReply, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler


MAX_MESSAGE_LENGTH = 4096 # макс. размер сообщения телеграм
CHOOSING_PHONE = 1
CHOOSING_EMAIL = 1
		
# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# ENV variables
load_dotenv()

TOKEN = os.getenv('TOKEN')
HOST = os.getenv('RM_HOST')
PORT = os.getenv('RM_PORT')
USER = os.getenv('RM_USER')
PASSWD = os.getenv('RM_PASSWORD')
DB_DATABASE = os.getenv('DB_DATABASE')
DB_USER = os.getenv('DB_USER')
DB_PASSWD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')

def helpCommand(update: Update, context):
    update.message.reply_text('Help!')

def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'find_phone_number'

def findEmailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска email адреса(адресов): ')
    return 'find_email'

def verifyPasswordCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки')
    return 'verify_password'

# ssh 

def getReleaseCommand(update: Update, context):
    update.message.reply_text('Введите ip-адрес хоста, имя пользователя и пароль через пробел')
    return 'get_release'

def getUnameCommand(update: Update, context):
    update.message.reply_text('Введите ip-адрес хоста, имя пользователя и пароль через пробел')
    return 'get_uname'

def getUptimeCommand(update: Update, context):
    update.message.reply_text('Введите ip-адрес хоста, имя пользователя и пароль через пробел')
    return 'get_uptime'

def getDfCommand(update: Update, context):
    update.message.reply_text('Введите ip-адрес хоста, имя пользователя и пароль через пробел')
    return 'get_df'

def getFreeCommand(update: Update, context):
    update.message.reply_text('Введите ip-адрес хоста, имя пользователя и пароль через пробел')
    return 'get_free'

def getMpstatCommand(update: Update, context):
    update.message.reply_text('Введите ip-адрес хоста, имя пользователя и пароль через пробел')
    return 'get_mpstat'

def getWCommand(update: Update, context):
    update.message.reply_text('Введите ip-адрес хоста, имя пользователя и пароль через пробел')
    return 'get_w'

def getAuthsCommand(update: Update, context):
    update.message.reply_text('Введите ip-адрес хоста, имя пользователя и пароль через пробел')
    return 'get_auths'

def getCriticalCommand(update: Update, context):
    update.message.reply_text('Введите ip-адрес хоста, имя пользователя и пароль через пробел')
    return 'get_critical'

def getPsCommand(update: Update, context):
    update.message.reply_text('Введите ip-адрес хоста, имя пользователя и пароль через пробел')
    return 'get_ps'

def getSsCommand(update: Update, context):
    update.message.reply_text('Введите ip-адрес хоста, имя пользователя и пароль через пробел')
    return 'get_ss'

def getServicesCommand(update: Update, context):
    update.message.reply_text('Введите ip-адрес хоста, имя пользователя и пароль через пробел')
    return 'get_services'

def getAptListCommand(update: Update, context):
    update.message.reply_text('Пожалуйста, введите пакет для проверки (название или all - для вывода информации о всех пакетах)')
    return 'get_apt_list'


def saveToDb(val_list, table_name, row_name):
    try:
        conn = psycopg2.connect(
            dbname=DB_DATABASE,
            user=DB_USER,
            password=DB_PASSWD,
            host=DB_HOST,
            port=DB_PORT
        )
    
        cur = conn.cursor()
        for val in val_list:
            insert_query = f"INSERT INTO {table_name} ({row_name}) VALUES (%s) ON CONFLICT DO NOTHING"
            cur.execute(insert_query, (val,))

        conn.commit()
        cur.close()
        conn.close()
        return "Найденные данные успешно сохранены в базе данных."
    except Exception as e:
        return "Ошибка при добавлении записей: " + str(e)


def saveToDbPhoneNumbers(update: Update, context):
    # получаем данные из контекста (номера телефонов)
    phone_numbers_list = context.user_data.get('phone_numbers', [])
    choice = update.message.text
    if (choice == 'Да'):
        update.message.reply_text('Начинаем сохранение найденных номеров телефонов в БД')
        status = saveToDb(phone_numbers_list, 'phone_numbers', 'phone_number')
        update.message.reply_text(status)
    else:
        update.message.reply_text('Сохранение в БД не выполняем')
    return ConversationHandler.END


def saveToDbEmails(update: Update, context):
    # получаем данные из контекста (email адреса)
    email_list = context.user_data.get('email_list', [])
    choice = update.message.text
    if (choice == 'Да'):
        update.message.reply_text('Начинаем сохранение найденных email-адресов в БД')
        status = saveToDb(email_list, 'emails', 'email')
        update.message.reply_text(status)
    else:
        update.message.reply_text('Сохранение в БД не выполняем')
    return ConversationHandler.END


def findPhoneNumbers (update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) номера телефонов

    phoneNumRegex = re.compile(r'(\+7|8)[\s(\-]?(\d{3})[\s)\-]?(\d{3})[\s\-]?(\d{2})[\s\-]?(\d{2})')

    phoneNumberList = phoneNumRegex.findall(user_input) # Ищем номера телефонов

    if not phoneNumberList: # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return # Завершаем выполнение функции
    
    phonesList = []
    phoneNumbers = 'Найденные номера телефонов:\n' # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        phone_number = "".join(phoneNumberList[i])
        phonesList.append(phone_number)
        phoneNumbers += str(i + 1) + '. ' + phone_number + '\n' # Записываем очередной номер
        
    update.message.reply_text(phoneNumbers) # Отправляем сообщение пользователю
    if(len(phoneNumbers) == 0):
        return ConversationHandler.END # если нет записей, то прекращаем взаимодействие
    # сохраняем найденные адреса в контексте
    context.user_data['phone_numbers'] = phonesList
    # Спрашиваем требуется ли сохранить их в БД
    reply_keyboard = [['Да', 'Нет']]
    update.message.reply_text(
        "Хотите сохранить найденные номера телефонов в базе данных?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return CHOOSING_PHONE


def findEmail(update: Update, context):
    user_input = update.message.text # Получаем текст

    emailRegex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

    emailList = emailRegex.findall(user_input)
    if not emailList: # Обрабатываем случай, когда мейлов нет
        update.message.reply_text('Email адреса не найдены')
        return # Завершаем выполнение функции
    
    emails = "Найденные email адреса:\n"
    for i in range(len(emailList)):
        email = "".join(emailList[i])
        emails += str(i + 1) + '. ' + email + '\n' # Записываем очередной email
    
    update.message.reply_text(emails) # Отправляем сообщение пользователю с найденными email
    if(len(emailList) == 0):
        return ConversationHandler.END # если нет записей, то прекращаем взаимодействие
    # сохраняем найденные адреса в контексте
    context.user_data['email_list'] = emailList
    # Спрашиваем требуется ли сохранить их в БД
    reply_keyboard = [['Да', 'Нет']]
    update.message.reply_text(
        "Хотите сохранить найденные email адреса в базе данных?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return CHOOSING_EMAIL



def verifyPassword(update: Update, context):
    user_input = update.message.text # Получаем от пользователя пароль

    passRegex = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')

    if(re.match(passRegex, user_input)):
        update.message.reply_text("Пароль сложный")
    else:
        update.message.reply_text("Пароль простой")

    return ConversationHandler.END # Завершаем работу обработчика диалога


def executeSshCommand(hostname, username, password, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password)
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode()
    ssh.close()
    return output


def executeSsh(user_input, command):
    if(len(user_input) != 3):
        return None
    hostname, user, passwd = user_input
    command_output = executeSshCommand(hostname, user, passwd, command)
    print(command_output)
    return command_output


def sshCommand(command):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=HOST, username=USER, password=PASSWD, port=PORT)
        stdin, stdout, stderr = client.exec_command(command)
        data = stdout.read() + stderr.read()
        client.close()
        data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
        return data
    except Exception as e:
        logger.error("Ошибка при подключении по ssh: %s", str(e))


def getRelease(update: Update, context):
    update.message.reply_text('Release information:')
    data = sshCommand('lsb_release -d')
    update.message.reply_text(data)
    return ConversationHandler.END


def getUname(update: Update, context):
    update.message.reply_text('Uname information:')
    data=sshCommand('uname -a')
    update.message.reply_text(data)
    return ConversationHandler.END


def getUptime(update: Update, context):
    update.message.reply_text('Uptime information:')
    data=sshCommand('uptime')
    update.message.reply_text(data)
    return ConversationHandler.END

def getDf(update: Update, context):
    update.message.reply_text('Df information:')
    data=sshCommand('df -h')
    update.message.reply_text(data)
    return ConversationHandler.END

def getFree(update: Update, context):
    update.message.reply_text('Free information:')
    data=sshCommand('free -h')
    update.message.reply_text(data)
    return ConversationHandler.END

def getMpstat(update: Update, context):
    update.message.reply_text('Mpstat information:')
    data=sshCommand('mpstat')
    update.message.reply_text(data)
    return ConversationHandler.END

def getW(update: Update, context):
    update.message.reply_text('W information:')
    data=sshCommand('w')
    update.message.reply_text(data)
    return ConversationHandler.END

def getAuths(update: Update, context):
    update.message.reply_text('Auths information:')
    data=sshCommand('last -10')
    update.message.reply_text(data)
    return ConversationHandler.END

def getCritical(update: Update, context):
    update.message.reply_text('Critical information:')
    data=sshCommand('journalctl -p 2 -n 5')
    update.message.reply_text(data)
    return ConversationHandler.END

def getPs(update: Update, context):
    update.message.reply_text('Ps information:')
    data=sshCommand('ps -A | head -n 10')
    update.message.reply_text(data)
    return ConversationHandler.END

def getSs(update: Update, context):
    update.message.reply_text('Ss information:')
    data=sshCommand('ss -lntu')
    update.message.reply_text(data)
    return ConversationHandler.END

def getServices(update: Update, context):
    update.message.reply_text('Services information:')
    data=sshCommand('systemctl --type=service --state=running | head -n 10')
    update.message.reply_text(data)
    return ConversationHandler.END

def getAptList(update: Update, context):
    user_input = update.message.text
    if user_input == 'all':
        data=sshCommand('apt list --installed | head -n 10')
        update.message.reply_text(data)
    else:
        data=sshCommand(f'apt list --installed | grep "{user_input}" | head -n 10')
        update.message.reply_text(data) 
    return ConversationHandler.END




def get_repl_logs(update: Update, context):
    command = "cat /var/log/postgresql/postgresql.log | grep 'repl' | tail -n 40"
    res = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0 or res.stderr.decode() != "":
        logger.error("Ошибка при выводе логов репликации: %s", res.stderr.decode())
    else:
        update.message.reply_text(res.stdout.decode().strip('\n'))


def getDataFromDb(table_name):
    try:
        conn = psycopg2.connect(
            dbname="db",
            user="postgres",
            password="postgres",
            host="db",
            port="5432"
        )
    
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {table_name};")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        return None


def getEmails(update: Update, context):
    update.message.reply_text('Записи таблицы emails БД')
    rows = getDataFromDb("emails")
    output = ''
    for row in rows:
        output += str(row[0]) + '. ' + str(row[1]) + '\n'
    update.message.reply_text(output)
    return ConversationHandler.END


def getPhoneNumbers(update: Update, context):
    update.message.reply_text('Записи таблицы phone_numbers БД')
    rows = getDataFromDb("phone_numbers")
    output = ''
    for row in rows:
        output += str(row[0]) + '. ' + str(row[1]) + '\n'
    update.message.reply_text(output)
    return ConversationHandler.END


def echo(update: Update, context):
    update.message.reply_text(update.message.text)


def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчики диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            CHOOSING_PHONE: [MessageHandler(Filters.regex('^(Да|Нет)$'), saveToDbPhoneNumbers)],
        },
        fallbacks=[]
    )
    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailCommand)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, findEmail)],
            CHOOSING_EMAIL: [MessageHandler(Filters.regex('^(Да|Нет)$'), saveToDbEmails)],
        },
        fallbacks=[]
    )
    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPasswordCommand)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verifyPassword)],
        },
        fallbacks=[]
    )
    convHandlerGetAptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', getAptListCommand)],
        states={
            'check_apt_list': [MessageHandler(Filters.text & ~Filters.command, getAptList)],
        },
        fallbacks=[]
    )
    convHandlerGetEmails= ConversationHandler(
    entry_points=[CommandHandler('get_emails', getEmails)],
    states={
        'get_emails': [MessageHandler(Filters.text & ~Filters.command, getEmails)],
    },
    fallbacks=[]
    )
    convHandlerGetPhoneNumbers= ConversationHandler(
    entry_points=[CommandHandler('get_phone_numbers', getPhoneNumbers)],
    states={
        'get_phone_numbers': [MessageHandler(Filters.text & ~Filters.command, getPhoneNumbers)],
    },
    fallbacks=[]
    )

	# Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerVerifyPassword)
    # ssh
    # dp.add_handler(convHandlerGetRelease)
    dp.add_handler(CommandHandler("get_release", getRelease))
    dp.add_handler(CommandHandler("get_uname", getUname))
    dp.add_handler(CommandHandler("get_uptime", getUptime))
    dp.add_handler(CommandHandler("get_df", getDf))
    dp.add_handler(CommandHandler("get_free", getFree))
    dp.add_handler(CommandHandler("get_mpstat", getMpstat))
    dp.add_handler(CommandHandler("get_w", getW))
    dp.add_handler(CommandHandler("get_auths", getAuths))
    dp.add_handler(CommandHandler("get_critical", getCritical))
    dp.add_handler(CommandHandler("get_ps", getPs))
    dp.add_handler(CommandHandler("get_ss", getSs))
    dp.add_handler(CommandHandler("get_services", getServices))
    dp.add_handler(convHandlerGetAptList)
    # replication logs
    # dp.add_handler(convHandlerGetReplLogs)
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    # извлечение данных из БД
    dp.add_handler(convHandlerGetEmails)
    dp.add_handler(convHandlerGetPhoneNumbers)
	# Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
		
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
