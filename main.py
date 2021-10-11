import pyrogram.filters
from pyrogram import Client
from pyrogram import filters
from pyrogram.handlers import MessageHandler, ChatMemberUpdatedHandler
from asyncio import sleep
import datetime
import schedule
import time
from pyrogram.types import ChatPermissions
import threading
from sqlite import sqlite_add_new_user, sqlite_update_posts, sqlite_clear_posts, sqlite_update_added_users, \
    sqlite_select_posts, sqlite_update_admin, sqlite_select_all_users_can_send_message, sqlite_add_new_user_optional, \
    sqlite_select_admins
from config import TEXT_HI, SILENCE_START, SILENCE_END, GROUP_ID
# from pyrogram.filters.service_filter_object import left_chat_member, new_chat_title, new_chat_photo, delete_chat_photo, group_chat_created, supergroup_chat_created, channel_chat_created, migrate_to_chat_id, migrate_from_chat_id, pinned_message, game_score, voice_chat_started, voice_chat_ended, voice_chat_members_invited
# pyrogram.filters.service_filter()
API_TOKEN = '1901727624:AAFhMmisKPuXG5C1e_wOm6_hqmpNLmoIRkk'
api_id = 8079740
api_hash = 'e5d7c0fad60dbdb912f4d6a00d6840dd'



IDS = sqlite_select_admins()

SILENCE = True
ALLOW_BOTS = False

bot = Client('bot', api_id, api_hash, bot_token=API_TOKEN)


async def start(client, message):
    if SILENCE:
        silencemode = 'включен'
    else:
        silencemode = 'выключен'
    if not ALLOW_BOTS:
        bots = 'включено'
    else:
        bots = 'выключено'
    await bot.send_message(chat_id=message["chat"]["id"], text='Вас приветствует бот менеджер группы.\n'
                                                               'Функции бота:\n'
                                                               f'/silence - режим тишины в группе с 22.00 до 7.00  ({silencemode})\n'
                                                               f'/allow_bots - удаление ботов, которых добавляют в группу  ({bots})\n'
                                                               '/post для создания поста, который будет отправлен в группу\n')


def get_all_users(client, message):
    members = [member for member in bot.iter_chat_members(chat_id=GROUP_ID)]
    for member in members:
        if member['status'] == 'creator' or member['status'] == 'administrator':
            admin = 1
        else:
            admin = 0
        user = {
            'id': member['user']['id'],
            'username': member['user']['username'],
            'admin': admin,
            'send_message': 1
        }
        sqlite_add_new_user_optional(user)
    print('Пользователи обновлены.')


async def say_hi_or_remove_bot(client, message):
    # print(message)
    if message["new_chat_member"]["status"] == "member":
        # await bot.delete_messages(chat_id=GROUP_ID, message_ids=message)
        if message["new_chat_member"]["user"]["is_bot"] and not ALLOW_BOTS:
            new_message = await bot.kick_chat_member(chat_id=GROUP_ID, user_id=message["new_chat_member"]["user"]["id"])
            # print(new_message)
            # await sleep(3)
            await bot.delete_messages(chat_id=GROUP_ID, message_ids=new_message["message_id"])
            # print(message["chat"]["id"])
            print(f'Бот {message["new_chat_member"]["user"]["first_name"]} удален из группы.')
        else:
            # await bot.delete_messages(chat_id=GROUP_ID, message_ids=message["message_id"])
            new_message = await bot.send_message(chat_id=message["chat"]["id"],
                                                 text=message["new_chat_member"]["user"]["first_name"] + TEXT_HI)
            await sleep(15)
            await bot.delete_messages(chat_id=GROUP_ID, message_ids=new_message["message_id"])
            print('Сообщение удалено')
            user = {
                'id': message["new_chat_member"]["user"]["id"],
                'username': message["new_chat_member"]["user"]["username"]
            }
            user2 = {
                'id': message["from_user"]["id"],
                'username': message["from_user"]["username"]
            }
            sqlite_update_added_users(user2)
            sqlite_add_new_user(user)
            await bot.restrict_chat_member(chat_id=GROUP_ID, user_id=user['id'],
                                           permissions=ChatPermissions(
                                               can_send_messages=False, can_send_media_messages=False,
                                               can_send_stickers=False,
                                               can_send_animations=False, can_send_games=False,
                                               can_use_inline_bots=False,
                                               can_add_web_page_previews=False, can_send_polls=False,
                                               can_change_info=False, can_invite_users=True,
                                               can_pin_messages=False))

            print(f'Пользователь {user["username"]} добавлен в группу.')


def delayed_message(text):
    bot.send_message(chat_id=GROUP_ID, text=text)
    return schedule.CancelJob


async def check_users_posts(client, message):
    print('функция check_users')
    # print(type(message))
    id = int(message["from_user"]["id"])
    username = message["from_user"]["username"]
    user = {
        'id': id,
        'username': username
    }
    count = sqlite_select_posts(user)
    # print(count)
    # if message.get('service') == None:
    if count < 2:
        sqlite_update_posts(user)
    else:
        await bot.delete_messages(GROUP_ID, message["message_id"])
        new_message = await bot.send_message(chat_id=message["chat"]["id"],
                                             text=message["from_user"][
                                                      "first_name"] + ' , вы не можете отправлять более двух сообщений в сутки.\nОбратите внимание на правила группы.')
        await sleep(5)
        await bot.delete_messages(chat_id=GROUP_ID, message_ids=new_message["message_id"])
        try:
            await bot.restrict_chat_member(chat_id=GROUP_ID, user_id=id,
                                           permissions=ChatPermissions(
                                               can_send_messages=False, can_send_media_messages=False,
                                               can_send_stickers=False,
                                               can_send_animations=False, can_send_games=False,
                                               can_use_inline_bots=False,
                                               can_add_web_page_previews=False, can_send_polls=False,
                                               can_change_info=False, can_invite_users=True,
                                               can_pin_messages=False))
        except:
            print('error')
    # else:
    #     await bot.delete_messages(chat_id=GROUP_ID, message_ids=message["message_id"])
    await silence(client, message)
    # print(USERS_POST)


async def post_message(client, message):
    # schedule_date (unix)
    answer = ''
    while answer != 'q' and answer != '1' and answer != '2' and '/' not in answer and '1' not in answer and '2' not in answer and 'q' not in answer:
        message = await bot.send_message(chat_id=message["chat"]["id"],
                                         text='1 - отправить сообщение сейчас\n2 - отправить отложенное сообщение\nq - выйти')
        # print(message["message_id"])
        await sleep(1)
        raw_answer = await bot.get_messages(chat_id=message["chat"]["id"], message_ids=(int(message["message_id"]) + 1))
        while raw_answer["empty"]:
            await sleep(1)
            raw_answer = await bot.get_messages(chat_id=message["chat"]["id"],
                                                message_ids=(int(message["message_id"]) + 1))
        answer = raw_answer["text"]
    if '1' in answer:
        message = await bot.send_message(chat_id=message["chat"]["id"],
                                         text='Напишите текст, который я перешлю в группу.')
        print(f'Пользователь {message["chat"]["id"]} выбрал вариант 1. Сообщение отправлено.')
        await sleep(30)
        text = ''
        while text == '':
            try:
                raw_text = await bot.get_messages(chat_id=message["chat"]["id"],
                                                  message_ids=int(message["message_id"]) + 1)
                while raw_text["empty"] or raw_text["text"] == ' ' or raw_text["text"] == '':
                    raw_text = await bot.get_messages(chat_id=message["chat"]["id"],
                                                      message_ids=int(message["message_id"]) + 1)
                text = raw_text["text"]
                if '/' in text:
                    return
            except:
                await sleep(10)
        await bot.send_message(chat_id=GROUP_ID, text=text)
        await bot.send_message(chat_id=message["chat"]["id"],
                               text='Ваше сообщение успешно отправлено в группу.')
    elif '2' in answer:
        message = await bot.send_message(chat_id=message["chat"]["id"],
                                         text='Напишите первым сообщением текст, который я перешлю в группу\n'
                                              'Вторым сообщением укажите время в формате часы:минуты')
        print(f'Пользователь {message["chat"]["id"]} выбрал вариант 2. Сообщение отправлено.')
        await sleep(10)
        text = ''
        time = ''
        while text == '' or time == '':
            try:
                raw_text = await bot.get_messages(chat_id=message["chat"]["id"],
                                                  message_ids=int(message["message_id"]) + 1)
                while raw_text["empty"] or raw_text["text"] == ' ' or raw_text["text"] == '':
                    raw_text = await bot.get_messages(chat_id=message["chat"]["id"],
                                                      message_ids=int(message["message_id"]) + 1)
                    await sleep(2)
                text = raw_text["text"]
                if '/' in text:
                    return
                raw_time = await bot.get_messages(chat_id=message["chat"]["id"],
                                                  message_ids=int(message["message_id"]) + 2)
                while raw_time["empty"] or raw_time["text"] == ' ' or raw_time["text"] == '':
                    raw_time = await bot.get_messages(chat_id=message["chat"]["id"],
                                                      message_ids=int(message["message_id"]) + 2)
                time = raw_time["text"]
                if '/' in time:
                    return
            except:
                await sleep(10)
        try:
            schedule.every().day.at(time).do(delayed_message, text)
            await bot.send_message(chat_id=message["chat"]["id"],
                                   text=f'Отправка сообщения запланированна на {time}.')
        except:
            await bot.send_message(chat_id=message["chat"]["id"],
                                   text='Ошибка при отправке сообщения.')
    elif answer == 'q' or '/' in answer or 'q' in answer:
        pass
    else:
        await bot.send_message(chat_id=message["chat"]["id"],
                               text='Используйте 1 или 2 для выбора опции(введите /post ещё раз)')


async def silence(client, message):
    if SILENCE:
        time = int(datetime.datetime.now().hour)
        if time < 7 or time >= 22:
            await bot.delete_messages(chat_id=message["chat"]["id"], message_ids=message["message_id"])
    text_len = len(message['text'])
    # print(text_len)
    if text_len > 300:
        await bot.delete_messages(chat_id=message["chat"]["id"], message_ids=message["message_id"])
        new_message = await bot.send_message(chat_id=GROUP_ID,
                                             text=f'{message["from_user"]["first_name"]}, вы не можете отправлять сообщение больше 300 знаков.\nОбратите внимание на правила группы.')
        await sleep(5)
        await bot.delete_messages(chat_id=GROUP_ID, message_ids=new_message["message_id"])
        print(f'Сообщение удалено, больше 300 знаков.')


def silence_on():
    if SILENCE:
        members = sqlite_select_all_users_can_send_message()
        for member in members:
            try:
                bot.restrict_chat_member(chat_id=GROUP_ID, user_id=member["username"],
                                         permissions=ChatPermissions(
                                             can_send_messages=False, can_send_media_messages=False,
                                             can_send_stickers=False,
                                             can_send_animations=False, can_send_games=False,
                                             can_use_inline_bots=False,
                                             can_add_web_page_previews=False, can_send_polls=False,
                                             can_change_info=False, can_invite_users=True,
                                             can_pin_messages=False))
            except:
                continue
        message = bot.send_message(chat_id=GROUP_ID,
                                   text='Решим тишины включен. Запрещено отправлять сообщения с 22.00 до 7.00')
        print('Режим тишины включен.')


async def delete_service(client, message):
    print('функция delete_service')
    await bot.delete_messages(chat_id=GROUP_ID, message_ids=message["message_id"])


def silence_off():
    members = sqlite_select_all_users_can_send_message()
    for member in members:
        try:
            bot.restrict_chat_member(chat_id=GROUP_ID, user_id=member["username"], permissions=ChatPermissions(
                can_send_messages=True, can_send_media_messages=True, can_send_stickers=False,
                can_send_animations=False, can_send_games=False, can_use_inline_bots=False,
                can_add_web_page_previews=False, can_send_polls=False, can_change_info=False, can_invite_users=True,
                can_pin_messages=False))
        except:
            continue
    bot.send_message(chat_id=GROUP_ID,
                     text='Решим тишины выключен. Сообщения снова можно отправлять.')
    sqlite_clear_posts()
    print('Режим тишины выключен. Количество постов в день сброшено.')


async def mode_silence(client, message):
    global SILENCE
    if SILENCE:
        SILENCE = False
        await bot.send_message(chat_id=message["chat"]["id"],
                               text='Решим тишины выключен.')
    else:
        SILENCE = True
        await bot.send_message(chat_id=message["chat"]["id"],
                               text='Решим тишины включен.')


async def mode_bots(client, message):
    global ALLOW_BOTS
    if not ALLOW_BOTS:
        ALLOW_BOTS = True
        await bot.send_message(chat_id=message["chat"]["id"],
                               text='Решим удаления ботов выключен.')
    else:
        ALLOW_BOTS = False
        await bot.send_message(chat_id=message["chat"]["id"],
                               text='Решим удаления ботов включен.')


schedule.every().day.at(SILENCE_START).do(silence_on)
schedule.every().day.at(SILENCE_END).do(silence_off)
schedstop = threading.Event()


def timer():
    while not schedstop.is_set():
        schedule.run_pending()
        time.sleep(3)


schedthread = threading.Thread(target=timer)
schedthread.start()

bot.add_handler(MessageHandler(mode_silence, filters.chat(IDS) & filters.command(["silence"])))
bot.add_handler(MessageHandler(mode_bots, filters.chat(IDS) & filters.command(["allow_bots"])))
bot.add_handler(MessageHandler(start, filters.chat(IDS) & filters.command(["start", "help", "info"])))
bot.add_handler(MessageHandler(post_message, filters.chat(IDS) & filters.command(["post"])))
bot.add_handler(MessageHandler(check_users_posts, filters.chat(GROUP_ID) & ~filters.service))
bot.add_handler(MessageHandler(delete_service, filters.chat(GROUP_ID) & filters.service))
bot.add_handler(ChatMemberUpdatedHandler(say_hi_or_remove_bot, filters.group & filters.chat(GROUP_ID)))
bot.add_handler(MessageHandler(get_all_users, filters.chat(IDS) & filters.command(["get_all_users"])))
print('Бот запущен.')
bot.run()
