# python manage.py telbot

from datetime import datetime, time
from os import stat
from account.models import Account
from django.db.models.signals import post_save
from website import settings
import requests
from django.http.request import QueryDict
# from autostop.filters import OrderFilter
from .models import Account
from autostop.models import Autostop, Application, PassengerAutostop
import random
from aiogram import types
from asgiref.sync import sync_to_async

from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import threading


BOT_TOKEN = settings.TOKEN
buslov_id = settings.BUSLOV_TELEGRAM
admin_group_id = settings.ADMIN_GROUP_TELEGRAM


@login_required(login_url='/login/')
def go_to_telegram(request):
    account_obj = Account.objects.get(email=request.user)
    Account.objects.filter(email=request.user).update(telegram=True)
    unique_code = account_obj.unique_code

    return HttpResponseRedirect("https://telegram.me/pidvezu_ua_bot?start={}".format(unique_code))


def created_post(sender, instance, created, **kwargs):
    if created == True:
        sync_to_async(ad_created(admin_group_id,instance), thread_sensitive=True)

    if created==False and instance.status == 'edited':
        sync_to_async(ad_edited(admin_group_id,instance), thread_sensitive=True)

    # if created==False and instance.status == 'published' or instance.status == 'rejected':
    #     if instance.author.chat_id != None  and instance.author.telegram == True:
    #         if instance.status == 'published':
    #             send_ad_status_notification(instance.author.chat_id, instance, 'published')
    #         if instance.status == 'rejected':
    #             send_ad_status_notification(instance.author.chat_id, instance, 'rejected')


post_save.connect(created_post, sender=Autostop) # этой строкой мы получаем сигнал о том, что пост был создан


def ad_created(chat_id, instance):    
    parse_message = f"Новое объявление, проверь-ка :)"
    keyboard_markup = types.InlineKeyboardMarkup()
    press_btn = types.InlineKeyboardButton('Перейти к публикации', url=f"https://pidvezu.com.ua/pidvezu_admin_page/autostop/autostop/{instance.pk}/change/")
    keyboard_markup.row(press_btn)

    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={parse_message}&parse_mode=HTML&reply_markup={keyboard_markup}")


def ad_edited(chat_id, instance):
    parse_message = f"Изменили объявление\n"

    keyboard_markup = types.InlineKeyboardMarkup()
    press_btn = types.InlineKeyboardButton('Перейти к редактированию', url=f"https://pidvezu.com.ua/pidvezu_admin_page/autostop/autostop/{instance.pk}/change/")
    keyboard_markup.row(press_btn)

    # https://www.youtube.com/watch?v=xFoUNDRVBYM&ab_channel=%D0%9C%D1%8D%D0%BB%D1%81%D0%B8%D0%BA-%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5
    # 7:37
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={parse_message}&parse_mode=HTML&reply_markup={keyboard_markup}")

def send_ad_status_notification(chat_id, instance, status):
    if instance.author.chat_id != None and instance.author.telegram == True:
        if status == 'published':
            parse_message = f"Ваш <strong><i>маршрут</i></strong> було опубліковано 👍\n{instance.first_last_location()[0]} --- {instance.first_last_location()[1]}"
        if status == 'rejected':
            parse_message = f"Ваш <strong><i>маршрут</i></strong> було відхилено 😔\n{instance.first_last_location()[0]} --- {instance.first_last_location()[1]}"
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={parse_message}&parse_mode=HTML")
    






def created_application(sender, instance, created, **kwargs):
    if created == True and instance.route.author.chat_id != None and instance.route.author.telegram == True:
        sync_to_async(application_created(instance.route.author.chat_id,instance), thread_sensitive=True)
    if created == False and instance.author.chat_id != None  and instance.route.author.telegram == True:
        if instance.status == 'justified' or instance.status == 'rejected':
            sync_to_async(application_status(instance.author.chat_id,instance), thread_sensitive=True)

post_save.connect(created_application, sender=Application) # этой строкой мы получаем сигнал о том, что пост был создан


def application_created(chat_id, instance):
    if instance.author.first_name != '' and instance.author.last_name != '':
        author_name = instance.author.first_name + ' ' + instance.author.last_name
    elif instance.author.first_name != '':
        author_name = instance.author.first_name
    else:
        author_name = instance.author.email
    parse_message = f'''
Нова заявка!
<strong><i>Маршрут:</i></strong>
<i>Ваш шлях:</i> {instance.route.first_last_location()[0]} --- {instance.route.first_last_location()[1]}
--------------------------------------------------
<i>Заявник:</i> {author_name}
<i>Номер телефону:</i> {instance.author.phone_number}
<i>Шлях заявника:</i> {instance.first_last_location()[0]} --- {instance.first_last_location()[1]}
    '''
    keyboard_markup = types.InlineKeyboardMarkup()
    press_btn = types.InlineKeyboardButton('Перейти до розділу "Заявки"', url=f"https://pidvezu.com.ua/applied_to_me/")
    keyboard_markup.row(press_btn)
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={parse_message}&parse_mode=HTML&reply_markup={keyboard_markup}")


# emojis --- https://www.w3schools.com/charsets/ref_emoji.asp
def application_status(chat_id, instance):
    if instance.route.author.first_name != '' and instance.route.author.last_name != '':
        author_name = instance.route.author.first_name + ' ' + instance.route.author.last_name
    elif instance.route.author.first_name != '':
        author_name = instance.route.author.first_name
    else:
        author_name = instance.route.author.email
    
    if instance.status == 'justified':
        parse_message = f'{author_name} схвалив(ла) вашу заявку 👍'
    else:
        parse_message = f'{author_name} відхилив(ла) вашу заявку 😔'
    parse_message += f'''
<strong><i>Ваш маршрут:</i></strong>{instance.first_last_location()[0]} --- {instance.first_last_location()[1]}
    '''
    keyboard_markup = types.InlineKeyboardMarkup()
    press_btn = types.InlineKeyboardButton('Відкрити оголошення', url=f"https://pidvezu.com.ua/route/{instance.route.slug}/")
    keyboard_markup.row(press_btn)
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={parse_message}&parse_mode=HTML&reply_markup={keyboard_markup}")



def created_passenger_post(sender, instance, created, **kwargs):
    if created == True:
        sync_to_async(passenger_ad_created(admin_group_id,instance), thread_sensitive=True)

post_save.connect(created_passenger_post, sender=PassengerAutostop) # этой строкой мы получаем сигнал о том, что пост был создан


def passenger_ad_created(chat_id, instance):    
    parse_message = f"Новая заявка от пассажира :)"
    keyboard_markup = types.InlineKeyboardMarkup()
    press_btn = types.InlineKeyboardButton('Перейти к заявке', url=f"https://pidvezu.com.ua/ru/pidvezu_admin_page/autostop/passengerautostop/{instance.pk}/change/")
    keyboard_markup.row(press_btn)

    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={parse_message}&parse_mode=HTML&reply_markup={keyboard_markup}")
