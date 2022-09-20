from django.contrib import admin
from account.models import Account
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms
from django.contrib.auth.admin import UserAdmin

class HidePassword(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Account
        fields = ('password',)



from django.db.models import Q
class is_user_active(admin.SimpleListFilter):
    title = 'Неактивные пользователи'
    parameter_name = 'is_active'

    def lookups(self, request, model_admin):
        return (
            ('activated', 'Активный'), 
            ('not_activated', 'Не активный'),
            ('not_activated_and_not_asked', 'Не активный и не спрошенный'),
            ('staff', 'Персонал'), 
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        if self.value().lower() == 'activated':
            return queryset.filter(is_active = True)
        if self.value().lower() == 'not_activated':
            return queryset.filter(is_active = False)
        if self.value().lower() == 'not_activated_and_not_asked':
            return queryset.filter(Q(is_active = False), Q(is_asked_for_activ = False))
        if self.value().lower() == 'staff':
            return queryset.filter(is_staff = True)



class AccountAdmin(UserAdmin): 
    form = HidePassword # скрываем пароль

    list_display = ('email',)
    list_filter = (is_user_active,)
    search_fields = ('email',)
    ordering=('email',)
    fieldsets = (
        (None, {'fields': ('image','email', 'password', 'phone_number', 'first_name', 'last_name', 'car_description', 'rides')}),
        ('Личная информация', {'fields': ( 'unique_code', 'telegram','chat_id', 'date_joined','last_login', 'is_asked_for_activ')}),
        ('Разрешения', {'fields': ('is_admin','is_active', 'is_blocked', 'is_staff', 'is_superuser', 'groups', 'user_permissions',)}),
    )
    
    # если захотим добавить аккаунт со страницы admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password',),
        }),
    )

    readonly_fields = ( 'unique_code', 'chat_id', 'date_joined','last_login')

    class Meta:
        model = Account




admin.site.register(Account, AccountAdmin)