from django.contrib import admin
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from autostop.models import Autostop, Application, PassengerAutostop
from account.telegram_view import send_ad_status_notification
from django.db.models import Q
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from .models import PidvezuBlog

def make_published(modeladmin, request, queryset):
    queryset.update(status='published')
make_published.short_description = "Опубликовать объявления"
def make_draft(modeladmin, request, queryset):
    queryset.update(status='draft')
make_draft.short_description = "Сделать черновиком"

class adts_expiration_date(admin.SimpleListFilter):
    title = 'Срок годности объявлений'
    parameter_name = 'status'
    
    def lookups(self, request, model_admin):
        return (
            ('normal_ads', 'Нормальные'), # если поменять название, то меняй второй параметр
            ('expired_ads', 'Просроченные'),
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        if self.value().lower() == 'normal_ads':
            return queryset.filter(Q(departure_time__gte = make_aware(datetime.today())), ~Q(status='rejected')) # make_aware - чтобы знали временной пояс и не было ошибки "DateTimeField received a naive datetime"
        if self.value() == 'expired_ads':
            return queryset.filter(Q(departure_time__lte = make_aware(datetime.today())), ~Q(status='rejected'))    



class AutostopAdmin(admin.ModelAdmin): # класс-редактор представления модели
    list_display=('id','author', 'departure_time', 'status')# последовательность имен полей, которые должны выводиться в списке записей
    list_display_links=('author',) # последовательность имен полей, которые должны быть преобразованы в гиперссылки, ведущие на страницу правки записи
    search_fields = ('author__email',) # последовательность имен полей, по которым должна выполняться фильтрация
    ordering = ['status', 'published',]
    list_filter = ('status',adts_expiration_date) # поле с фильтрами справа
    fields =( 'slug','content','departure_time','rubric','seats_left','locations','locations_addresses', 'favourites', 'published', 'author', 'views', 'status') 
    readonly_fields = ('published',)

    
    actions = [make_published, make_draft]
    change_form_template = "others/admin_autostop.html"

        # отвечает за кнопку ОПУБЛИКОВАТЬ и переход к след.публик.
    def response_change(self, request, obj):
        if "publish_btn" in request.POST:
            # не меняем status на published, потому что уже это сделали с js html admin
            self.message_user(request, f'Маршрут опубликован')
            send_ad_status_notification(obj.author.chat_id, obj, 'published')
            
            if Autostop.objects.filter(pk = (obj.pk+1)).exists():
                return redirect(f"/pidvezu_admin_page/autostop/autostop/{Autostop.objects.get(pk = (obj.pk+1)).pk}/change")
            else:
                return HttpResponseRedirect('/pidvezu_admin_page/autostop/autostop/')
        if "reject_btn" in request.POST:
            # не меняем status на rejected, потому что уже это сделали с js html admin
            self.message_user(request, f'Маршрут отклонён"')
            send_ad_status_notification(obj.author.chat_id, obj, 'rejected')
            
            if Autostop.objects.filter(pk = (obj.pk+1)).exists():
                return redirect(f"/pidvezu_admin_page/autostop/autostop/{Autostop.objects.get(pk = (obj.pk+1)).pk}/change")
            else:
                return HttpResponseRedirect('/pidvezu_admin_page/autostop/autostop/')
        elif "delete_btn" in request.POST:
            next_obj = obj.pk + 1 
            obj.delete()
            self.message_user(request, f'Маршрут удалён"')
            if Autostop.objects.filter(pk = next_obj).exists():
                return redirect(f"/pidvezu_admin_page/autostop/autostop/{Autostop.objects.get(pk = next_obj)}/change")
            else:
                return HttpResponseRedirect('/pidvezu_admin_page/autostop/autostop/')
        else:
            return HttpResponseRedirect('/pidvezu_admin_page/autostop/autostop/')


class ApplicationAdmin(admin.ModelAdmin):
    list_display=('route','rubric',)
    list_display_links=('route',) 
    search_fields = ('author__email',)
    ordering = ['published',]
    list_filter = ('published',) # поле с фильтрами справа
    fields =('route','comment','published','locations','locations_addresses','unique_code','rubric','author','status') 
    readonly_fields = ('published','unique_code')


class PassengerAutostopAdmin(admin.ModelAdmin): # класс-редактор представления модели
    list_display=('id','author','departure_time', 'status')# последовательность имен полей, которые должны выводиться в списке записей
    list_display_links=('author',) # последовательность имен полей, которые должны быть преобразованы в гиперссылки, ведущие на страницу правки записи
    search_fields = ('author__email',) # последовательность имен полей, по которым должна выполняться фильтрация
    ordering = ['status', 'published',]
    list_filter = ('status',adts_expiration_date) # поле с фильтрами справа
    fields =( 'slug','content','departure_time','rubric','locations','locations_addresses', 'published', 'author', 'views', 'status') 
    readonly_fields = ('published',)

    
    actions = [make_published, make_draft]
    change_form_template = "others/admin_autostop.html"

        # отвечает за кнопку ОПУБЛИКОВАТЬ и переход к след.публик.
    def response_change(self, request, obj):
        if "publish_btn" in request.POST:
            # не меняем status на published, потому что уже это сделали с js html admin
            self.message_user(request, f'Маршрут опубликован')
            # send_ad_status_notification(obj.author.chat_id, obj, 'published')
            
            if PassengerAutostop.objects.filter(pk = (obj.pk+1)).exists():
                return redirect(f"/pidvezu_admin_page/autostop/passengerautostop/{PassengerAutostop.objects.get(pk = (obj.pk+1)).pk}/change")
            else:
                return HttpResponseRedirect('/pidvezu_admin_page/autostop/passengerautostop/')
        if "reject_btn" in request.POST:
            # не меняем status на rejected, потому что уже это сделали с js html admin
            self.message_user(request, f'Маршрут отклонён"')
            # send_ad_status_notification(obj.author.chat_id, obj, 'rejected')
            
            if PassengerAutostop.objects.filter(pk = (obj.pk+1)).exists():
                return redirect(f"/pidvezu_admin_page/autostop/passengerautostop/{PassengerAutostop.objects.get(pk = (obj.pk+1)).pk}/change")
            else:
                return HttpResponseRedirect('/pidvezu_admin_page/autostop/passengerautostop/')
        elif "delete_btn" in request.POST:
            next_obj = obj.pk + 1 
            obj.delete()
            self.message_user(request, f'Маршрут удалён"')
            if PassengerAutostop.objects.filter(pk = next_obj).exists():
                return redirect(f"/pidvezu_admin_page/autostop/passengerautostop/{PassengerAutostop.objects.get(pk = next_obj)}/change")
            else:
                return HttpResponseRedirect('/pidvezu_admin_page/autostop/passengerautostop/')
        else:
            return HttpResponseRedirect('/pidvezu_admin_page/autostop/passengerautostop/')



class PidvezuBlogAdmin(admin.ModelAdmin): # класс-редактор представления модели
    list_display=('title_ru', 'author', 'views')
    list_display_links=('title_ru',) 
    fields = ('title_ru', 'title_uk', 'slug', 'og_image','post_content_ru', 'post_content_uk', 'published', 'views', 'status')
    search_fields=('title_ru',)
    readonly_fields = ('published',)
    prepopulated_fields = {'slug': ('title_ru',)} # slug применяет значение title

    
    change_form_template = "others/blog_admin_btns.html"

    def response_change(self, request, obj):
        if "publish_btn" in request.POST:
            if obj.status == 'published':
                self.message_user(request, 'Эта запись была уже опубликована')
                return redirect(f"/pidvezu_admin_page/autostop/pidvezublog/{obj.pk}/change")
                
            obj.status = 'published'
            obj.save()
            self.message_user(request, f'Опубликована запись "{obj.title_ru}"')
            
            return redirect(f"/pidvezu_admin_page/autostop/pidvezublog/")
        elif "delete_btn" in request.POST:
            next_obj = obj.pk + 1 
            obj_title = obj.title_ru
            obj.delete()
            self.message_user(request, f'Удалена запись "{obj_title}"')
            if PidvezuBlog.objects.filter(pk = next_obj).exists():
                return redirect(f"/pidvezu_admin_page/autostop/pidvezublog/{PidvezuBlog.objects.get(pk = (next_obj)).pk}/change")
            else:
                return HttpResponseRedirect('/pidvezu_admin_page/autostop/pidvezublog/')
        else:
            return redirect('/pidvezu_admin_page/autostop/pidvezublog/')





admin.site.register(Autostop, AutostopAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(PassengerAutostop, PassengerAutostopAdmin)
admin.site.register(PidvezuBlog, PidvezuBlogAdmin)

admin.site.unregister(Group)