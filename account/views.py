import imp
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from account.forms import ProfileEditForm

from autostop.models import Autostop
from .models import Account
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse, reverse_lazy
from .utils import token_generator
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
import threading
from django.views.generic import View
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.db.models import Q
from .telegram_view import go_to_telegram
import re
from django.utils.translation import get_language

def user_login(request):
    if request.user.is_authenticated:
        return redirect('autostop:start')
    else:
        if request.method == 'POST':

            if request.is_ajax():
                data=''
                email_check = request.POST.get('email_login', None)

                if email_check:
                    if Account.objects.filter(email=email_check.lower()).exists():
                        if Account.objects.get(email=email_check.lower()).is_active == False:
                            data='not_active'
                        if Account.objects.get(email=email_check.lower()).is_blocked == True:
                            data='blocked'
                    elif Account.objects.filter(phone_number=email_check).exists():
                        if Account.objects.get(phone_number=email_check).is_active == False:
                            data='not_active'
                        if Account.objects.get(phone_number=email_check).is_blocked == True:
                            data='blocked'
                    else:
                        data='not_exists'

                return JsonResponse(data, safe=False)

            email = request.POST.get('email').lower()
            password = request.POST.get('password')

            try:
                # номер телефона
                user = authenticate(email=Account.objects.get(phone_number=email).email, password=password)
            except:
                # email
                user = authenticate(email=email, password=password)

                

            if user is not None:
                if user.is_blocked:
                    return redirect('account:logout')
                login(request, user)
                if 'next' in request.POST:
                    return redirect(request.POST.get('next'))
                return redirect('autostop:start')
            else:  
                return render(request, 'account/login.html', {'current_lang':get_language()})
        else:  
            return render(request, 'account/login.html', {'current_lang':get_language()})

def user_logout(request):
    logout(request)
    return redirect('autostop:start')


# view для того, чтобы быстрее отправлять email
class EmailThreading(threading.Thread):
    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()

def registration(request):
    if request.method == 'GET' and request.is_ajax():
        print('ajax')
        email_check = request.GET.get('email_check', None)
        if Account.objects.filter(email=email_check).exists():
            email_check = 'email_exists'
        return JsonResponse(email_check, safe=False)
        
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')

        # if request.is_ajax():
        #     data=''
        #     email_check = request.POST.get('email', None)
        #     phone_number_check = request.POST.get('phone_num', None)

        #     if email_check:
        #         if Account.objects.filter(email=email_check.lower()).exists():
        #             data='email_taken'
        #         else:
        #             data='emil_free'
        #     elif phone_number_check:
        #         if Account.objects.filter(phone_number=phone_number_check).exists():
        #             data='phone_taken'
        #         else:
        #             data='phone_free'

        #     return JsonResponse(data, safe=False)


        if Account.objects.filter(email=email).exists() or Account.objects.filter(phone_number=phone_number).exists():
            return redirect('account:registration')


        user = Account.objects.create_user(password=password, email=email.lower(), phone_number=phone_number)
        user.is_active = False # Меняем на True после регистрации
        user.save()

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        domain = get_current_site(request).domain
        link = reverse('account:activate', kwargs={'uidb64':uidb64,'token':token_generator.make_token(user)})

        activate_url='http://' + domain + link


        mail_title = "Активация"
        variables = {
            'activate_url': activate_url,
        }
        html = get_template('account/email.html').render(variables)
        text = f'Натисніть кнопку підтвердження адреси електронної пошти нижче:\nКоли Ви підтвердите свою пошту, перейдіть до розділу "Коротке введення" https://pidvezu.com.ua/brief_intro/ - там Ви дізнаєтеся, як налаштувати повідомлення, додати маршрут, подати на нього заявку та багато іншого.\nПідтвердити\n{activate_url}\nPidvezu - це безкоштовна площадка, де водії публікують свій маршрут, а інші люди можуть передати речі, їжу, тварин, або бути пасажиром для доставки в/з гарячих точок України'
        
        msg = EmailMultiAlternatives(
            mail_title,
            text,
            settings.EMAIL_HOST_USER,
            [email])
        msg.attach_alternative(html, "text/html")
        # msg.send(fail_silently=False) 
        EmailThreading(msg).start()
        

        return render(request, 'account/registration_success.html', {'email':email, 'current_lang':get_language()})
    else:
        return render(request, 'account/registration.html', {'current_lang':get_language()})

class VerificationView(View):
    def get(self,request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Account.objects.get(pk=uid)
        except Exception as e:
            user = None
        
        if user is not None:
            if not token_generator.check_token(user,token):
                return redirect('account:login')

            if user.is_active:
                return redirect('account:profile')
            user.is_active = True
            user.save()

            return redirect('account:profile')
        else:
            raise Exception


class RequestResetEmailView(View):
    def get(self, request):
        return render(request, 'account/reset_email.html', {'current_lang':get_language()})
    
    def post(self, request):
        email = request.POST.get('email', None)
        
        if email is None:
            return render(request, 'account/reset_email.html', {'current_lang':get_language()})

        user = Account.objects.filter(email=email)
        if user.exists():
            uidb64 =urlsafe_base64_encode(force_bytes(user[0].pk))

            domain = get_current_site(request).domain
            link = reverse('account:set_new_pswrd', kwargs={'uidb64':uidb64,'token':token_generator.make_token(user[0])})

            renew_password_url='http://' + domain + link

            mail_title = "Оновлення пароля"
            variables = {
                'activate_url': renew_password_url,
            }
            html = get_template('account/email_reset_password.html').render(variables)
            text = f'Щоб скинути пароль, натисніть кнопку нижче.\nСкинути пароль\n{renew_password_url}\nPidvezu - це безкоштовна площадка, де водії публікують свій маршрут, а інші люди можуть передати речі, їжу, тварин, або бути пасажиром для доставки в/з гарячих точок України'
            
            msg = EmailMultiAlternatives(
                mail_title,
                text,
                settings.EMAIL_HOST_USER,
                [email])
            msg.attach_alternative(html, "text/html")
            EmailThreading(msg).start() # мы быстрее отправляем email

            return render(request, 'account/reset_email_success.html', {'current_lang':get_language()})
        else:
            return redirect('account:registration')

class SetNewPswrdView(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64':uidb64,
            'token':token,
            'current_lang':get_language(),
        }

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = Account.objects.get(pk=user_id)

            if PasswordResetTokenGenerator().check_token(user, token):
                return render(request, 'account/reset_email.html', {'current_lang':get_language()}) # Пароль кликают 2-ой раз, так нельзя. Отошлём на повторную отправку
        except DjangoUnicodeDecodeError as identifier:
            return render(request, 'account/reset_email.html', {'current_lang':get_language()})
        return render(request, 'account/set_new_pswrd.html', context)
    
    def post(self, request, uidb64, token):
        context = {
            'uidb64':uidb64,
            'token':token,
            'current_lang':get_language(),
        }

        password = request.POST.get('password', None)
        if password is None or len(password) < 4 or len(password) > 20:
            return render(request, 'account/set_new_pswrd.html', context)

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))

            user = Account.objects.get(pk=user_id)
            user.set_password(password)
            user.is_active = True
            user.save()

            return redirect('/login/')
        except DjangoUnicodeDecodeError as identifier:
            return render(request, 'account/set_new_pswrd.html', context)


@login_required(login_url='/login/')
def profile(request):
    account = Account.objects.get(pk=request.user.pk) 
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=account)
        if form.is_valid():
            post = form.save(commit=False)

            if request.FILES.get('img'):
                post.image = request.FILES.get('img')
                
            # if post.phone_number == None or not re.match(r'^\+?3?8?(0\d{9})$', post.phone_number):
            #     return redirect('account:profile')
            if request.POST.get('telegram') == 'on':
                post.telegram = True
            else:
                post.telegram = False
            post.save()
        return redirect('account:profile')

    
    form = ProfileEditForm(instance=account)
    checked = ''
    if account.telegram == True:
        checked = 'checked'
    return render(request, 'account/profile.html', {'form':form, 'account':account,'checked':checked, 'current_lang':get_language()})
    

def account(request, pk):
    if Account.objects.filter(pk=pk).exists():
        autostop_obj = Autostop.objects.filter(Q(author=Account.objects.get(pk=pk).pk), Q(status='published'))
        user=Account.objects.get(pk=pk)
        time_now1 = str(datetime.today().date().day).zfill(2) + '.' + str(datetime.today().date().month).zfill(2) + '.' + str(datetime.today().date().year).zfill(2)
        time_now2 = str(datetime.today().date().day-1).zfill(2) + '.' + str(datetime.today().date().month).zfill(2) + '.' + str(datetime.today().date().year).zfill(2)

        context={
            'autostop_obj':autostop_obj,
            'requested_user':user,
            'time_now1':time_now1,
            'time_now2':time_now2,
            'current_lang':get_language(),
        }

        if user == request.user:
            return redirect('account:profile')


        return render(request, 'account/account.html', context)
    else:
        return HttpResponse('Такий Юзер зник о_о')


# --------------------------------- Telegram -------------------------------------
def get_unique_code(request):
    return go_to_telegram(request)