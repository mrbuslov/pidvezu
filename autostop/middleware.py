from django.shortcuts import redirect, render
# from django.utils.translation import get_language
from loguru import logger
import requests
from random import randint
import traceback

from website import settings
from django.utils.translation import get_language


class MyMiddleware:
    def __init__(self, get_response):
        self._get_response = get_response
    
    def __call__(self, request):
        response = self._get_response(request)
        return response

    def process_exception(self, request, exception):
        logger.add("logging/debug.log", format=' Time: {time}\nMsg:{message}\n', #  Filename:{file} ({file.name} --- {file.path})\n Function:{function}\n Level:{level}\n Line:{line}\n 
                    level='DEBUG', rotation='10 KB', compression='zip', ) # serialize=True
        logger.debug(exception)
        
        BOT_TOKEN = settings.TOKEN
        traceback_extract_tb = str(traceback.extract_tb(exception.__traceback__)[-1])
        traceback_extract_tb = traceback_extract_tb.replace('<', '').replace('>','')
        text = f'ERROR: <strong>{exception}</strong>\n\n{traceback_extract_tb}' # берём последнюю строку в ошибке ( с линией, где произошла ошибка)
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={505309520}&text={text}&parse_mode=HTML")

        return render(request, 'others/exception.html', {'current_lang':get_language()}) # , context