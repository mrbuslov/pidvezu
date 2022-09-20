from ast import Try
from enum import auto
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
import requests, json, polyline, folium
from account.models import Account
from .models import PidvezuBlog
from .forms import BlogForm

from website import settings
from . import getroute
from .forms import AutostopForm, ApplicationForm, PassengerAutostopForm
from .models import Autostop, Application, PassengerAutostop
from datetime import datetime
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q, F
from django.contrib.auth.decorators import login_required
from functools import reduce
import operator
from googletrans import Translator
from django.db.models import Case, When, Value
from django.utils.translation import get_language


def start(request):
    if 'locations_search' in request.GET:
        locations_search = request.GET['locations_search']
        return redirect(f'/drivers/?{locations_search}')

    context = {
        'current_lang':get_language(),
        'driver_publc_num': Autostop.objects.filter(status='published').count(),
        'passenger_publc_num': PassengerAutostop.objects.filter(status='published').count(),
    }
    return render(request, 'autostop/start_page.html', context)

def transliterate(string):
    try:
        # You can get about 1000 requests / hour without hitting the req/IP block limit. Also, individual requests are limited to less than 5000 characters per request
        translator = Translator()
        result = translator.translate(string, dest='uk').text
    except:
        dic = {'зк':'зьк','ск':'ськ','цк':'цьк','ск':'ськ','Ь':'Ь', 'ь':'ь', 'Ъ':'’', 'ъ':'’', 'А':'А', 'а':'а', 'Б':'Б', 'б':'б', 'В':'В', 'в':'в',
            'Г':'Г', 'г':'g', 'Д':'Д', 'д':'д', 'Є':'є', 'е':'є', 'Ё':'Йо', 'ё':'ьо', 'Ж':'Ж', 'ж':'ж',
            'З':'З', 'з':'з', 'И':'І', 'и':'і', 'Й':'Й', 'й':'й', 'К':'К', 'к':'к', 'Л':'Л', 'л':'л',
            'М':'М', 'м':'м', 'Н':'Н', 'н':'н', 'О':'О', 'о':'о', 'П':'П', 'п':'п', 'Р':'Р', 'р':'р', 
            'С':'С', 'с':'с', 'Т':'Т', 'т':'т', 'У':'У', 'у':'у', 'Ф':'Ф', 'ф':'ф', 'Х':'Х', 'х':'х',
            'Ц':'Ц', 'ц':'ц', 'Ч':'Ч', 'ч':'ч', 'Ш':'Ш', 'ш':'ш', 'Щ':'Щ', 'щ':'щ', 'Ы':'И',
            'ы':'и', 'Э':'Е', 'э':'е', 'Ю':'Ю', 'ю':'ю', 'Я':'я', 'я':'я'}
            
        alphabet = ['Ь', 'ь', 'Ъ', 'ъ', 'А', 'а', 'Б', 'б', 'В', 'в', 'Г', 'г', 'Д', 'д', 'Е', 'е', 'Ё', 'ё',
                    'Ж', 'ж', 'З', 'з', 'И', 'и', 'Й', 'й', 'К', 'к', 'Л', 'л', 'М', 'м', 'Н', 'н', 'О', 'о',
                    'П', 'п', 'Р', 'р', 'С', 'с', 'Т', 'т', 'У', 'у', 'Ф', 'ф', 'Х', 'х', 'Ц', 'ц', 'Ч', 'ч',
                    'Ш', 'ш', 'Щ', 'щ', 'Ы', 'ы', 'Э', 'э', 'Ю', 'ю', 'Я', 'я']
        

        st = string
        result = str()
        
        len_st = len(st)
        for i in range(0,len_st):
            if st[i] in alphabet:
                simb = dic[st[i]]
            else:
                simb = st[i]
            result = result + simb

    return result

def get_index_page(request,model):
    time_now1 = str(datetime.today().date().day).zfill(2) + '.' + str(datetime.today().date().month).zfill(2) + '.' + str(datetime.today().date().year).zfill(2)
    time_now2 = str(datetime.today().date().day+1).zfill(2) + '.' + str(datetime.today().date().month).zfill(2) + '.' + str(datetime.today().date().year).zfill(2)

    
    locations_search = ''
    if 'locations_search' in request.GET: # filter
        locations_search = request.GET['locations_search']
        value1 = request.GET['locations_search'].replace(',',' ').replace(';', ' ').split(' ') # заменяем всякие знаки препинания
        value2 = transliterate(request.GET['locations_search']).replace(',',' ').replace(';', ' ').split(' ') # заменяем всякие знаки препинания
        autostop_obj1 = model.objects.filter(reduce(operator.and_, (Q(locations_addresses__icontains=location) for location in value1)))
        autostop_obj2 = model.objects.filter(reduce(operator.and_, (Q(locations_addresses__icontains=location) for location in value2)))
        autostop_obj = (autostop_obj1 | autostop_obj2).distinct()
    else:
        autostop_obj = model.objects.filter(status='published')
   
    paginator = Paginator(autostop_obj,20)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    response = paginator.page(page_num)


    context = {
        'response':response,
        'page':page,
        'locations_query':locations_search,
        'time_now1':time_now1, # сегодня
        'time_now2':time_now2, # завра
        'current_lang':get_language(),

        'driver_publc_num': Autostop.objects.filter(status='published').count(),
        'passenger_publc_num': PassengerAutostop.objects.filter(status='published').count(),
    }
    return context


def index(request):
    context = get_index_page(request,Autostop)
    return render(request, 'autostop/index.html', context)

def passenger_index(request):
    context = get_index_page(request,PassengerAutostop)
    return render(request, 'autostop/index_passenger.html', context)


@login_required(login_url='/login/')
def add(request):
    if request.method =='POST':
        form = AutostopForm(data=request.POST)
        if form.is_valid():
            departure_point = request.POST.get('departure_point', None)
            departure_address = request.POST.get('departure_address', None)
            arrival_point = request.POST.get('arrival_point', None)
            arrival_address = request.POST.get('arrival_address', None)
            departure_time = request.POST.get('departure_time', None)

            if departure_point == None or departure_address == None or arrival_point == None or arrival_address == None or departure_time == None:
                return redirect('autostop:add')

            post = form.save(commit=False)
            post.locations = departure_point + ';' + arrival_point
            post.locations_addresses = departure_address + ';' + arrival_address
            post.departure_time = datetime.strptime(departure_time, '%d-%m-%Y %H:%M')
            post.author = request.user
            post.status = 'draft'
            post.save()

            return redirect('autostop:my_routes')
        else:
            return redirect('autostop:add')
    else:
        form = AutostopForm()
        context={
            'form':form,
            'current_lang':get_language(),
        }       
        return render(request, 'autostop/add.html', context) 
    
@login_required(login_url='/login/')
def passenger_add(request):
    if request.method =='POST':
        form = PassengerAutostopForm(data=request.POST)
        if form.is_valid():
            departure_point = request.POST.get('departure_point', None)
            departure_address = request.POST.get('departure_address', None)
            arrival_point = request.POST.get('arrival_point', None)
            arrival_address = request.POST.get('arrival_address', None)
            departure_time = request.POST.get('departure_time', None)

            if departure_point == None or departure_address == None or arrival_point == None or arrival_address == None or departure_time == None:
                return redirect('autostop:passenger_add')

            post = form.save(commit=False)
            post.locations = departure_point + ';' + arrival_point
            post.locations_addresses = departure_address + ';' + arrival_address
            post.departure_time = datetime.strptime(departure_time, '%d-%m-%Y %H:%M')
            post.author = request.user
            post.status = 'draft'
            post.save()

            return redirect('autostop:my_routes')
        else:
            return redirect('autostop:passenger_add')
    else:
        form = PassengerAutostopForm()
        context={
            'form':form,
            'current_lang':get_language(),
        }       
        return render(request, 'autostop/add_passenger.html', context) 


@login_required(login_url='/login/')
def edit(request, slug):
    route = Autostop.objects.get(slug=slug)
    form = AutostopForm(request.POST, instance=route) # instance - исправляемая запись
    if request.user == route.author:
        if Application.objects.filter(route=route).count() > 0:
            return render(request, 'autostop/u_cant_edit.html', {'current_lang':get_language()})
        if request.method == 'POST':
            if form.is_valid():
                departure_point = request.POST.get('departure_point', None)
                departure_address = request.POST.get('departure_address', None)
                arrival_point = request.POST.get('arrival_point', None)
                arrival_address = request.POST.get('arrival_address', None)

                if departure_point == None or departure_address == None or arrival_point == None or arrival_address == None:
                    return HttpResponseRedirect(request.request.path_info)

                post = form.save(commit=False)
                post.locations = departure_point + ';' + arrival_point
                post.locations_addresses = departure_address + ';' + arrival_address
                post.status = 'edited'
                post = form.save()

                return redirect('autostop:my_routes')
            else:
                print(form.errors.as_data())
        
        form = AutostopForm(instance=route)
        # checkboxes check
        people_checkbox = ''
        animals_checkbox = ''
        good_checkbox = ''
        food_checkbox = ''
        others_checkbox = ''
        for rubric in route.rubric:
            if rubric == 'people':
                people_checkbox = 'checked'
            elif rubric == 'animals':
                animals_checkbox = 'checked'
            elif rubric == 'good':
                good_checkbox = 'checked'
            elif rubric == 'food':
                food_checkbox = 'checked'
            elif rubric == 'others':
                others_checkbox = 'checked'
                
        context = {
            'route_slug':route.slug,
            'form':form,
            'departure_point': route.locations.split(';')[0],
            'departure_address': route.locations_addresses.split(';')[0],
            'arrival_point': route.locations.split(';')[1],
            'arrival_address': route.locations_addresses.split(';')[1],

            'departure_time': route.departure_time,

            'people_checkbox':people_checkbox,
            'animals_checkbox':animals_checkbox,
            'good_checkbox':good_checkbox,
            'food_checkbox':food_checkbox,
            'others_checkbox':others_checkbox,

            'current_lang':get_language(),
        }
        return render(request, 'autostop/edit.html', context)
    else:
        return redirect('autostop:my_routes')

@login_required(login_url='/login/')
def delete(request, slug):
    route = Autostop.objects.get(slug=slug)
    if request.user == route.author:
        Account.objects.filter(email=request.user.email).update(rides=F('rides')+1)
        route.delete()
        if request.user.telegram == True and request.user.chat_id != None:
            text = 'Ви видалили маршрут "' + route.first_last_location()[0] + ' --- ' + route.first_last_location()[1] +'"\n\n<strong>Маршрут в Google Картах:</strong>\n' + route.get_google_routing()
            requests.get(f"https://api.telegram.org/bot{settings.TOKEN}/sendMessage?chat_id={request.user.chat_id}&parse_mode=HTML&text={text}")

        return redirect('autostop:my_routes')
    else:
        return redirect('autostop:index')
@login_required(login_url='/login/')
def delete_passenger_route(request, slug):
    route = PassengerAutostop.objects.get(slug=slug)
    if request.user == route.author:
        route.delete()

        return redirect('autostop:my_routes')
    else:
        return redirect('autostop:index')


@login_required(login_url='/login/')
def update_addresses_info(request):
    if request.is_ajax():
        addresses = request.POST.getlist('addresses[]')
        locations = request.POST.getlist('locations[]')
        slug = request.POST.get('slug', None)

        route = Autostop.objects.filter(slug=slug)
        _addresses = ''
        _locations = ''

        for i, val in enumerate(addresses):
            _addresses += val + ';'
            _locations += locations[i] + ';'

        route.update(locations_addresses=_addresses[:-1])# удаляем последнюю ';'
        route.update(locations=_locations[:-1])

        
        routes = showroute(route[0].locations)
        return JsonResponse(data={
            'map_script':routes.script.render(),
            'map_html':routes.html.render(),
        })
    else:
        return redirect('autostop:index')

@login_required(login_url='/login/')
def apply(request, slug):
    if Application.objects.filter(Q(author=request.user), route=Autostop.objects.get(slug=slug)).exists():
        return redirect('autostop:i_applied')
    if Autostop.objects.get(slug=slug).author != request.user:
        if request.method =='POST':
            form = ApplicationForm(data=request.POST)
            if form.is_valid():
                departure_point = request.POST.get('departure_point', None)
                departure_address = request.POST.get('departure_address', None)
                arrival_point = request.POST.get('arrival_point', None)
                arrival_address = request.POST.get('arrival_address', None)

                post = form.save(commit=False)
                post.route = Autostop.objects.get(slug=slug)
                post.locations = departure_point + ';' + arrival_point
                post.locations_addresses = departure_address + ';' + arrival_address
                post.author = request.user
                post.save()

                return redirect('autostop:i_applied')
            else:
                return redirect('autostop:apply')
        else:
            form = ApplicationForm()
            route = Autostop.objects.get(slug=slug)
            addresses = route.locations_addresses.split(';')
            context={
                'form':form,
                'route': route,
                'departure_address': addresses[0],
                'arrival_address': addresses[1],
                'current_lang':get_language(),
            }       
            return render(request, 'autostop/apply.html', context) 
    else:
        return redirect('autostop:index')

# html draggable --- https://css-tricks.com/draggable-elements-push-others-way/
# google maps построение маршрута (первые 3 - путь, последний с @ - какую часть карты показать и z масштаб) --- https://www.google.com.ua/maps/dir/50.4572194,30.5086202/50.4593158,30.4911548/50.4626926,30.4903405/@50.4623922,30.4965738,15z
def route(request, slug):
    if not Autostop.objects.filter(slug=slug).exists():
        return render(request, "others/404.html", {'current_lang': get_language()})
    route = Autostop.objects.get(slug=slug)
    routes = showroute(route.locations)
    addresses = route.locations_addresses.split(';')

    rubrics = []
    rubric_names = str(route.rubric).split(',')
    emojis_array = ['🧍','🐕','👖','🥕']
    for i, rubric in enumerate(route.rubric):
        if rubric == 'people':
            rubrics.append(emojis_array[0] + ' ' + rubric_names[i])
        elif rubric == 'animals':
            rubrics.append(emojis_array[1] + ' ' + rubric_names[i])
        elif rubric == 'good':
            rubrics.append(emojis_array[2] + ' ' + rubric_names[i])
        elif rubric == 'food':
            rubrics.append(emojis_array[3] + ' ' + rubric_names[i])
        elif rubric == 'others':
            rubrics.append(rubric_names[i])

    i = 0
    addresses_array = []
    for point in route.locations.split(';'):
        addresses_array.append(
            {
                addresses[i]:point
            }
        )
        i += 1

    time_now1 = str(datetime.today().date().day).zfill(2) + '.' + str(datetime.today().date().month).zfill(2) + '.' + str(datetime.today().date().year).zfill(2)
    time_now2 = str(datetime.today().date().day-1).zfill(2) + '.' + str(datetime.today().date().month).zfill(2) + '.' + str(datetime.today().date().year).zfill(2)

    user_applied = False
    if request.user.is_authenticated:
        if Application.objects.filter(Q(author=request.user), route=Autostop.objects.get(slug=slug)).exists():
            user_applied = True
    context={
        'route': route,
        'map':routes,  
        'rubrics':rubrics,
        'author': route.author,
        'addresses_array':addresses_array,

        'fist_address':addresses[0],
        'addresses':addresses[1:len(addresses)-1], # выбрасываем первый и последний адреса
        'last_address':addresses[-1],
        'time_now1':time_now1,
        'time_now2':time_now2,

        'user_applied':user_applied,
        'current_lang':get_language(),
    }       
    return render(request, 'autostop/route.html', context) 

def route_passenger(request, slug):
    if not PassengerAutostop.objects.filter(slug=slug).exists():
        return render(request, "others/404.html", {'current_lang': get_language()})
    route = PassengerAutostop.objects.get(slug=slug)
    routes = showroute(route.locations)
    addresses = route.locations_addresses.split(';')

    rubrics = []
    rubric_names = str(route.rubric).split(',')
    emojis_array = ['🧍','🐕','👖','🥕']
    for i, rubric in enumerate(route.rubric):
        if rubric == 'people':
            rubrics.append(emojis_array[0] + ' ' + rubric_names[i])
        elif rubric == 'animals':
            rubrics.append(emojis_array[1] + ' ' + rubric_names[i])
        elif rubric == 'good':
            rubrics.append(emojis_array[2] + ' ' + rubric_names[i])
        elif rubric == 'food':
            rubrics.append(emojis_array[3] + ' ' + rubric_names[i])
        elif rubric == 'others':
            rubrics.append(rubric_names[i])

    i = 0
    addresses_array = []
    for point in route.locations.split(';'):
        addresses_array.append(
            {
                addresses[i]:point
            }
        )
        i += 1

    time_now1 = str(datetime.today().date().day).zfill(2) + '.' + str(datetime.today().date().month).zfill(2) + '.' + str(datetime.today().date().year).zfill(2)
    time_now2 = str(datetime.today().date().day-1).zfill(2) + '.' + str(datetime.today().date().month).zfill(2) + '.' + str(datetime.today().date().year).zfill(2)

    context={
        'route': route,
        'map':routes,  
        'rubrics':rubrics,
        'author': route.author,
        'addresses_array':addresses_array,

        'fist_address':addresses[0],
        'last_address':addresses[-1],
        'time_now1':time_now1,
        'time_now2':time_now2,

        'current_lang':get_language(),
    }       
    return render(request, 'autostop/route_passenger.html', context) 



@login_required(login_url='/login/')
def my_routes(request):
    all_routes = Autostop.objects.filter(author=request.user)
    all_passenger_routes = PassengerAutostop.objects.filter(author=request.user)
    return render(request, 'autostop/my_routes.html', {'all_routes':all_routes,'all_passenger_routes':all_passenger_routes,'current_lang':get_language(),}) 


def remove_address_from_textfield(application, route):
    application_address1 = application.locations_addresses.split(';')[0]
    application_address2 = application.locations_addresses.split(';')[1]

    # ВАРИАНТ 1

    # # проверяем наличие 1-го адреса в маршруте
    # if ';' + application_address1 in route.locations_addresses:
    #     route.locations_addresses = route.locations_addresses.replace(';' + application_address1, '')
    # else:
    #     route.locations_addresses = route.locations_addresses.replace(application_address1, '')
    
    # # проверяем наличие 2-го адреса в маршруте
    # if ';' + application_address2 in route.locations_addresses:
    #     route.locations_addresses = route.locations_addresses.replace(';' + application_address2, '')
    # else:
    #     route.locations_addresses = route.locations_addresses.replace(application_address2, '')

    # # на всякий случа проверяем наличие ';' на начале и конце всего маршрута
    # route_is_not_clear = True
    # while route_is_not_clear:
    #     if route.locations_addresses[0] != ';' and route.locations_addresses[-1] != ';':
    #         route_is_not_clear = False
    #     else:
    #         if route.locations_addresses[0] == ';':
    #             route.locations_addresses = route.locations_addresses.replace(route.locations_addresses[0], '')
    #         if route.locations_addresses[-1] == ';':
    #             route.locations_addresses = route.locations_addresses.replace(route.locations_addresses[-1], '')
    #     print(route_is_not_clear)


    # ВАРИАНТ 2
    routes = []
    for path in route.locations_addresses.split(';'):
        if path == application_address1:
            continue
        elif path == application_address2:
            continue
        else:
            routes.append(path)
    
    route.locations_addresses = ';'.join([str(item) for item in routes])
    route.save()
def remove_ip_from_textfield(application, route):
    application_ip1 = application.locations.split(';')[0]
    application_ip2 = application.locations.split(';')[1]

    # ВАРИАНТ 1

    # # проверяем наличие 1-го адреса в маршруте
    # if ';' + application_ip1 in route.locations:
    #     route.locations = route.locations_addresses.replace(';' + application_ip1, '')
    # else:
    #     route.locations = route.locations.replace(application_ip1, '')
    
    # # проверяем наличие 2-го адреса в маршруте
    # if ';' + application_ip2 in route.locations:
    #     route.locations = route.locations.replace(';' + application_ip2, '')
    # else:
    #     route.locations = route.locations.replace(application_ip2, '')

    # # на всякий случа проверяем наличие ';' на начале и конце всего маршрута
    # route_is_not_clear = True
    # while route_is_not_clear:
    #     if route.locations[0] != ';' and route.locations[-1] != ';':
    #         route_is_not_clear = False
    #     else:
    #         if route.locations[0] == ';':
    #             route.locations = route.locations.replace(route.locations[0], '')
    #         if route.locations[-1] == ';':
    #             route.locations = route.locations.replace(route.locations[-1], '')
    #     print(route_is_not_clear)


    # ВАРИАНТ 2
    ips = []
    for path in route.locations.split(';'):
        if path == application_ip1:
            continue
        elif path == application_ip2:
            continue
        else:
            ips.append(path)

    route.locations = ';'.join([str(item) for item in ips])
    route.save()




@login_required(login_url='/login/')
def i_applied(request):
    applications = Application.objects.filter(author=request.user)
    return render(request, 'autostop/i_applied.html', {'applications':applications,'current_lang':get_language()})
def cancel_application(request,pk):
    application = Application.objects.get(pk=pk)
    route = Autostop.objects.get(pk=application.route.pk)
    
    remove_address_from_textfield(application, route)
    remove_ip_from_textfield(application, route)

    if application.author == request.user:
        application.delete()
    return redirect('autostop:i_applied')

@login_required(login_url='/login/')
def applied_to_me(request):
    routes = Autostop.objects.filter(author=request.user)
    paths = {}
    for route in routes: 
        applications = Application.objects.filter(route=route).order_by('status')
        if applications.count() > 0:
            paths[route]=applications
    return render(request, 'autostop/applied_to_me.html', {'routes':paths,'current_lang':get_language()})

@login_required(login_url='/login/')
def confirm_application(request, pk):
    application = Application.objects.get(pk=pk)
    if application.status == 'justified':
        return redirect('autostop:applied_to_me')
    application.status = 'justified'
    application.save()
    route = Autostop.objects.get(pk=application.route.pk)

    route.locations_addresses += ';' + application.locations_addresses.split(';')[0]
    route.locations_addresses += ';' + application.locations_addresses.split(';')[1]
    route.locations += ';' + application.locations.split(';')[0]
    route.locations += ';' + application.locations.split(';')[1]
    route.save()
    return redirect('autostop:applied_to_me')

@login_required(login_url='/login/')
def reject_application(request, pk):
    application = Application.objects.get(pk=pk)
    if application.status == 'rejected':
        return redirect('autostop:applied_to_me')
    application.status = 'rejected'
    application.save()
    route = Autostop.objects.get(pk=application.route.pk)
    
    remove_address_from_textfield(application, route)
    remove_ip_from_textfield(application, route)
    
    return redirect('autostop:applied_to_me')

def others(request):
    return render(request,'others/others.html', {'current_lang':get_language()})


def privacy_policy(request):
    return render(request, 'others/privacy_policy.html', {'current_lang':get_language()})
def pidvezu_rules(request):
    return render(request, 'others/pidvezu_rules.html', {'current_lang':get_language()})
def brief_intro(request):
    return render(request, 'others/brief_intro.html', {'current_lang':get_language()})

def error_to_admin(request):
    a=1/0
    return render(request, 'others/exception.html', {'current_lang':get_language()})

def handler404_error(request, *args, **argv):
    return render(request, "others/404.html", {'current_lang': get_language()})
def handler500_error(request, *args, **argv):
    return render(request, "others/500.html", {'current_lang': get_language()})



def load_main_map(request):
    if request.is_ajax():
        what_search_on_map = request.GET.get('what_search_on_map', None)

        if what_search_on_map == 'search_drivers':
            points = Autostop.objects.filter(status='published')
            points_list = []
            slugs_list = []
            
            for point in points:
                add_point = point.locations.split(';')[0]
                points_list.append(add_point)
                slugs_list.append(point.slug)
            return JsonResponse(data={'points_list':points_list, 'slugs_list':slugs_list})
        elif what_search_on_map == 'search_passengers':    
            points = PassengerAutostop.objects.filter(status='published')
            points_list = []
            slugs_list = []
            
            for point in points:
                add_point = point.locations.split(';')[0]
                points_list.append(add_point)
                slugs_list.append(point.slug)
            return JsonResponse(data={'points_list':points_list, 'slugs_list':slugs_list})
        else:
            raise Exception('main_map_exception')
    else:
        return redirect('autostop:start')

def load_main_map_marker_info(request):
    if request.is_ajax():
        slug = request.GET.get('slug', None)
        what_search = ''
        link_to_apply = ''
        link_to_passenger_ad = ''

        try:
            route = Autostop.objects.get(slug=slug)
            what_search = 'drivers'
            link_to_apply = f'/apply/{slug}'
            phone_number = route.author.phone_number
        except:
            route = PassengerAutostop.objects.get(slug=slug)
            what_search = 'passengers'
            phone_number = route.author.phone_number
            link_to_passenger_ad = f'/route_passenger/{slug}'
        person = Account.objects.get(email=route.author.email)

        # имя
        if person.first_name:
            person_name = person.first_name
        elif person.last_name:
            person_name = person.first_name
        else:
            person_name = person.email.split('@')[0]
        print(person_name)

        # точка прибытия и отправления
        departure_point = route.locations.split(';')[0]
        arrival_point = route.locations.split(';')[-1]

        # все другие точки для построения, кроме данного отобразившегося пути
        if what_search == 'drivers':
            other_points = Autostop.objects.filter(Q(status='published'),~Q(slug=slug))
        else:
            other_points = PassengerAutostop.objects.filter(Q(status='published'),~Q(slug=slug))
        points_list = []
        slugs_list = []
            
        for point in other_points:
            add_point = point.locations.split(';')[0]
            points_list.append(add_point)
            slugs_list.append(point.slug)

        # строим маршрут (синяя линия)
        routes = []
        for p in route.locations.split(';'):
            routes.append(p.replace(' ', ''))

        figure = folium.Figure()
        lat1,long1,lat2,long2=float(routes[0].split(',')[0]),float(routes[0].split(',')[1]),float(routes[1].split(',')[0]),float(routes[1].split(',')[1])
        # если ошибка от сервера 502, куда мы отправляем запрос
        try:
            route=getroute.get_route(long1,lat1,long2,lat2)
            m = folium.Map(location=[(route['start_point'][0]), (route['start_point'][1])], zoom_start=10)
        except:
            print('except')
            route=[long1,lat1,long2,lat2]
            m = folium.Map(location=[lat1, long1], zoom_start=10)
            
        route = not route
        for i, route in enumerate(routes):
            if i < len(routes)-1: # не выходим за границы массива
                lat1,long1,lat2,long2=float(routes[i].split(',')[0]),float(routes[i].split(',')[1]),float(routes[i+1].split(',')[0]),float(routes[i+1].split(',')[1])
                route=getroute.get_route(long1,lat1,long2,lat2)
                m.add_to(figure)
                
                html="Перезавантажте карту"
                iframe = folium.IFrame(html=html, width=230, height=45)
                # test = folium.Html('<b>Hello world</b>', script=True)
                popup = folium.Popup(iframe, max_width=2650)

                try:
                    folium.PolyLine(route['route'],weight=5,color='blue',opacity=0.6).add_to(m)
                    folium.Marker(location=route['start_point'],icon=folium.Icon(icon='play', color='green'), popup=popup).add_to(m) # , tooltip=folium.Tooltip(iframe.render())  ---   при наведении окно
                    folium.Marker(location=route['end_point'],icon=folium.Icon(icon='stop', color='red')).add_to(m)
                except:
                    folium.Marker(location=[lat1, long1],icon=folium.Icon(icon='play', color='green'), popup=popup).add_to(m) # , tooltip=folium.Tooltip(iframe.render())  ---   при наведении окно
                    folium.Marker(location=[lat2, long2],icon=folium.Icon(icon='stop', color='red')).add_to(m)
                    
        # добавляем каждую точку
        for point in points_list:
            folium.Marker(location=[point.split(',')[0], point.split(',')[1]]).add_to(m)
        figure.render()
        routes = figure

        return JsonResponse(data={
            'map_script':routes.script.render(),
            'map_html':routes.html.render(),
            'map_header':routes.header.render(),

            'departure_point':departure_point,
            'arrival_point':arrival_point,
            'points_list':points_list, 
            'slugs_list':slugs_list,

            'person_name':person_name,
            'link_to_apply':link_to_apply,
            'link_to_passenger_ad':link_to_passenger_ad,
            'phone_number':phone_number,
            'what_search':what_search,
        })
    else:
        return redirect('autostop:start')



import html2text
from .models import PidvezuBlog
def blog(request):
    blog_obj = PidvezuBlog.objects.filter(status = 'published')
    paginator = Paginator(blog_obj, 20)

    page = request.GET.get('page')
    try:
        response = paginator.page(page)
    except PageNotAnInteger:
        response = paginator.page(1)
    except EmptyPage:
        response = paginator.page(paginator.num_pages)
    
    time_now1 = str(datetime.today().date().day).zfill(2) + '.' + str(datetime.today().date().month).zfill(2) + '.' + str(datetime.today().date().year).zfill(2)
    time_now2 = str(datetime.today().date().day-1).zfill(2) + '.' + str(datetime.today().date().month).zfill(2) + '.' + str(datetime.today().date().year).zfill(2) # для того, чтобы вместо дня 1 марта превратить в 01 марта

    values = []
    for val in blog_obj: 
        post_content_ru = str(html2text.html2text(val.post_content_ru)).replace('[','').replace(']','')
        post_content_uk = str(html2text.html2text(val.post_content_uk)).replace('[','').replace(']','')

        values.append({
            'slug': val.slug,
            'title_uk': val.title_uk,
            'published': val.published,
            'post_content_uk': post_content_uk,
            'title_ru': val.title_ru,
            'post_content_ru': post_content_ru,
        })


    context={
        'blog_obj':response, 
        'current_lang':get_language(),
        'time_now1': time_now1,
        'time_now2': time_now2,
        'values': values,
    }

    return render(request, 'others/blog.html', context)

from django.db.models import F
def blog_post(request, slug):
    if PidvezuBlog.objects.filter(slug=slug).exists:
        blog_obj = PidvezuBlog.objects.get(slug=slug)
        PidvezuBlog.objects.filter(slug=slug).update(views=F('views')+1)
        return render(request, 'others/blog_post.html', {'blog_obj':blog_obj, 'current_lang':get_language()})
    else:
        return redirect('account:blog')


        
def add_blog_post(request):
    if request.user.is_staff:
        if request.method =='POST':
            form = BlogForm(data=request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.status = 'published'

                try:
                    get_img = post.post_content_ru
                    get_img = get_img.split('src="')[1].split('"')[0]
                    print(get_img)
                    post.og_image = 'https://pidvezu.com.ua' + get_img
                except:
                    post.og_image = 'https://pidvezu.com.ua/static/img/start_image.jpg'

                post.save()

                return redirect('autostop:blog')
            else:
                return redirect('autostop:add_blog_post')
        else:
            form = BlogForm()
            context={
                'form':form,
                'current_lang':get_language(),
            }       
            return render(request, 'others/blog_post_add.html', context) 
    else:
        return redirect('autostop:blog')






# https://realpython.com/location-based-app-with-geodjango-tutorial/
# https://python.plainenglish.io/django-webapp-for-plotting-route-between-two-points-in-a-map-6f1babfeec59

# http://127.0.0.1/map/47.902668,33.392523;47.902715,33.398885;47.898031,33.406787 
# http://127.0.0.1/map/47.902668,33.392523;47.902715,33.398885;47.898031,33.406787;48.898031,33.406787
# def showroute(request, path):
def showroute(path):
    routes = []
    for p in path.split(';'):
        routes.append(p.replace(' ', ''))

    figure = folium.Figure()
    
    lat1,long1,lat2,long2=float(routes[0].split(',')[0]),float(routes[0].split(',')[1]),float(routes[1].split(',')[0]),float(routes[1].split(',')[1])
    try:
        route=getroute.get_route(long1,lat1,long2,lat2)
        m = folium.Map(location=[(route['start_point'][0]), (route['start_point'][1])], zoom_start=10)
    except:
        route=[long1,lat1,long2,lat2]
        m = folium.Map(location=[lat1, long1], zoom_start=10)

    route = not route
    for i, route in enumerate(routes):
        if i < len(routes)-1: # не выходим за границы массива
            lat1,long1,lat2,long2=float(routes[i].split(',')[0]),float(routes[i].split(',')[1]),float(routes[i+1].split(',')[0]),float(routes[i+1].split(',')[1])
            route=getroute.get_route(long1,lat1,long2,lat2)
            m.add_to(figure)
            try:
                folium.PolyLine(route['route'],weight=5,color='blue',opacity=0.6).add_to(m)
                folium.Marker(location=route['start_point'],icon=folium.Icon(icon='play', color='green')).add_to(m) # , tooltip=folium.Tooltip(iframe.render())  ---   при наведении окно
                folium.Marker(location=route['end_point'],icon=folium.Icon(icon='stop', color='red')).add_to(m)
            except:
                folium.Marker(location=[lat1, long1],icon=folium.Icon(icon='play', color='green')).add_to(m) # , tooltip=folium.Tooltip(iframe.render())  ---   при наведении окно
                folium.Marker(location=[lat2, long2],icon=folium.Icon(icon='stop', color='red')).add_to(m)
    
    figure.render()
    # context={'map':figure}
    # return render(request, 'map/showroute.html', context)
    return figure