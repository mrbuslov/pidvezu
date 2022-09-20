import os
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

# python-telegram-bot
# python manage.py telegram_bot 
from django.core.management.base import BaseCommand
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from website import settings

from asgiref.sync import sync_to_async
import logging
from account.models import Account
import aiohttp
from aiogram.utils.markdown import bold, code, italic, text
from aiogram.types import ParseMode
from aiogram.utils.emoji import emojize
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

@sync_to_async
def extract_unique_code(text):
    return text.split()[1] if len(text.split()) > 1 else None

@sync_to_async
def get_account(unique_code):
    if Account.objects.filter(unique_code=unique_code).exists():
        return Account.objects.get(unique_code=unique_code)
    else:
        return None


bot = Bot(token=settings.TOKEN)
dp = Dispatcher(bot)

button1 = KeyboardButton('Що може робити Бот?')
button2 = InlineKeyboardButton('Перейти до профілю', url="https://pidvezu.com.ua/profile/")

markup = ReplyKeyboardMarkup(resize_keyboard=True).add(button1).add(button2)

# how to register_next_step_handler aiogram python


# class Form(StatesGroup):
#     state = State() # Задаем состояние

# @dp.message_handler(commands=['start'])
# async def start(message: types.Message):
#     await bot.send_message(message.chat.id, 'Отправь свое сообщение:')
#     await Form.state.set() # Устанавливаем состояние

# @dp.message_handler(state=Form.state) # Принимаем состояние
# async def start(message: types.Message, state: FSMContext):
#     async with state.proxy() as proxy: # Устанавливаем состояние ожидания
#         state['state'] = message.text
#         await state.finish() # Выключаем состояние

class Command(BaseCommand):
    help = 'Телеграм Бот'

    def handle(self, *args, **options):

        @dp.message_handler(commands=['start'])
        async def process_start_command(message: types.Message):
            await types.ChatActions.typing() # "Бот печатает ..."

            unique_code = await extract_unique_code(message.text)
            if unique_code and await get_account(unique_code):
                account_obj = await get_account(unique_code)
                account_obj.chat_id = message.chat.id
                account_obj.save()

                first_name = message.from_user.first_name
                account_first_name = account_obj.first_name
                username = message.from_user.username
                try:
                    if first_name:
                        reply = "Здрастуйте {0}!".format(first_name)
                    elif account_first_name:
                        reply = "Здрастуйте {0}!".format(account_first_name)
                    elif username:
                        reply = "Здрастуйте {0}!".format(username)
                    else:
                        reply = "Здрастуйте!"
                except:
                    reply = "Здрастуйте!"

                if account_obj.telegram == False:
                    reply += ' Я надсилатиму Вам повідомлення про зміну статусу Ваших зявок.\nТакож, коли Ви складете маршрут, я відправлю посилання на нього в Google Картах.\nУвімкніть повідомлення, перетягнувши кружечок у поле Telegram.'

                    keyboard_markup = types.InlineKeyboardMarkup()
                    press_btn = types.InlineKeyboardButton('Увімкнути повідомлення', url="https://pidvezu.com.ua/profile/")
                    keyboard_markup.row(press_btn)
                    
                    await bot.send_message(message.from_user.id, reply, reply_markup=keyboard_markup)
                else:
                    await bot.send_message(message.from_user.id, reply, reply_markup=markup)

            else:
                reply = "Щоб ми могли надсилати повідомлення про Ваші заявки, зайдіть через сайт."
                
                keyboard_markup = types.InlineKeyboardMarkup()
                press_btn = types.InlineKeyboardButton('Зайти на сайт', url="https://pidvezu.com.ua/telegram_bot/")
                keyboard_markup.row(press_btn)
                    
                await bot.send_message(message.from_user.id, reply, reply_markup=keyboard_markup)



        @dp.message_handler(commands=['help'])
        async def what_bot_can_do(message: types.Message):
            await types.ChatActions.typing() # "Бот печатает ..."

            msg = []
            msg.append(text("З радістю розповімо!)\nКоли Ви хочете перевезти вантаж, або ж хочете проїхати, Ви подаєте ", italic("заявку")," водієві. Коли йому прийде сповіщення про це, ми відправимо Вам повідомлення, схвалив чи відхилив він її :relaxed: \n"))
            msg.append(text("Якщо Ви водій, після складання ", italic("маршрута")," і прийому заявок, Ви видаляєте оголошення. Після чого ми Вам відправимо посилання на Google Карти з повністю побудованим маршрутом.🌍")) # &#1F30D;	

            keyboard_markup = types.InlineKeyboardMarkup()
            press_btn = types.InlineKeyboardButton('Побудувати маршрут', url="https://pidvezu.com.ua/add/")
            keyboard_markup.row(press_btn)
            
            await bot.send_message(message.chat.id, emojize(text(*msg, sep='\n')), parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard_markup)


        @dp.message_handler()
        async def send_back(message: types.Message):
            if str(message.text).lower() == 'привет' or str(message.text).lower() == 'привіт':
                await bot.send_message(message.chat.id, 'Привіт!) У мене є багато команд, із чого почнемо?', reply_markup=markup)
            if str(message.text).lower() == 'що може робити бот?':
                await what_bot_can_do(message)
            if str(message.text).lower() == 'перейти до профілю':
                keyboard_markup = types.InlineKeyboardMarkup()
                press_btn = types.InlineKeyboardButton('Перейти до профілю', url="https://pidvezu.com.ua/profile/")
                keyboard_markup.row(press_btn)
                
                await bot.send_message(message.chat.id, 'Давайте змінимо Ваші дані', reply_markup=keyboard_markup)
   





        executor.start_polling(dp)