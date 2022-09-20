from django.shortcuts import render
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name='autostop'

urlpatterns = [
    path('', views.start, name='start'),
    path('load_main_map/', views.load_main_map, name='load_main_map'),
    path('load_main_map_marker_info/', views.load_main_map_marker_info, name='load_main_map_marker_info'),

    path('drivers/', views.index, name='index'),
    path('add/', views.add, name='add'),
    path('edit/<str:slug>', views.edit, name='edit'),
    path('delete/<str:slug>', views.delete, name='delete'),
    path('apply/<str:slug>', views.apply, name='apply'),
    path('route/<str:slug>', views.route, name='route'),
    path('my_routes/', views.my_routes, name='my_routes'),
    path('i_applied/', views.i_applied, name='i_applied'),
    path('cancel_application/<int:pk>', views.cancel_application, name='cancel_application'),
    path('applied_to_me/', views.applied_to_me, name='applied_to_me'),
    path('confirm_application/<int:pk>', views.confirm_application, name='confirm_application'),
    path('reject_application/<int:pk>', views.reject_application, name='reject_application'),
    path('update_addresses_info/', views.update_addresses_info, name='update_addresses_info'),
    path('others/', views.others, name='others'),
    
    #passenger
    path('passengers/', views.passenger_index, name='passenger_index'),
    path('passenger_add/', views.passenger_add, name='passenger_add'),
    path('route_passenger/<str:slug>', views.route_passenger, name='route_passenger'),
    path('delete_passenger_route/<str:slug>', views.delete_passenger_route, name='delete_passenger_route'),
    
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    path('pidvezu_rules/', views.pidvezu_rules, name='pidvezu_rules'),
    path('brief_intro/', views.brief_intro, name='brief_intro'),
    path('blog/<str:slug>/', views.blog_post, name='blog_post'),
    path('add_blog_post/', views.add_blog_post, name='add_blog_post'),
    path('blog/', views.blog, name='blog'),
    
    path('error_to_admin/', views.error_to_admin, name='error_to_admin'),

    # path('map/',views.showmap,name='showmap'),
    # path('map/<str:path>',views.showroute,name='showroute'),
]
#+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)