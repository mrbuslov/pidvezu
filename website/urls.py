from django.contrib import admin
from django.urls import path, include, re_path
from django.utils.translation import gettext_lazy as _
from django.conf.urls.i18n import i18n_patterns
from .sitemaps import * # Sitemap
from django.contrib.sitemaps.views import sitemap, index
from . import settings


sitemaps = {
    'drivers_applications': AutostopSitemap,
    'passengers_applications': PassengerAutostopSitemap,
    'blog': PidvezuBlogSitemap,
}


urlpatterns = [
]
urlpatterns += i18n_patterns (
    path('pidvezu_admin_page/', admin.site.urls),
    path('',include('account.urls', namespace='account')),
    path('',include('autostop.urls', namespace='autostop')),
    path('ckeditor',include('ckeditor_uploader.urls')),

    # path('sitemap.xml', sitemap, {'sitemaps':sitemaps}),
    
    path('sitemap.xml', index, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.index'),
    path('sitemap-<section>.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    prefix_default_language=False # чтобы не было /uk/ в строке
)


if 'rosetta' in settings.INSTALLED_APPS: # это графический редактор переведённого текста
    urlpatterns += [
        re_path(r'^rosetta/', include('rosetta.urls'))
    ]

admin.site.index_title = "Pidvezu"
admin.site.site_header = "Pidvezu Admin"
admin.site.site_title = "Admin"

# errors handlers
# handler400 = 'autostop.views.handler400_error' # неверный запрос
# handler403 = 'autostop.views.handler403_error' # запрещён доступ к странице
handler404 = 'autostop.views.handler404_error' # неверная страница
handler500 = 'autostop.views.handler500_error' # проблема с сервером