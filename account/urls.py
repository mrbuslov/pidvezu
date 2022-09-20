from django.shortcuts import render
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from account import views

app_name='account'

urlpatterns = [
    path('login/', views.user_login ,name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'), # мой профиль
    # path('account/', views.account, name='account'), # профиль пользователя
    path('account/<int:pk>/', views.account, name='account'),
    path('telegram_bot/', views.get_unique_code, name='get_unique_code'),

    path('registration/', views.registration, name='registration'),
    path('activate/<uidb64>/<token>', views.VerificationView.as_view(), name = 'activate'),

    path('reset_email/', views.RequestResetEmailView.as_view(), name = 'reset_email'), # эти 2 связаны - из одной выходит другая
    path('set_new_pswrd/<uidb64>/<token>', views.SetNewPswrdView.as_view(), name = 'set_new_pswrd'),

]