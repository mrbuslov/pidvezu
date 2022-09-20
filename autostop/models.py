from django.db import models
from pytils.translit import slugify 
from io import BytesIO
from django.core.files.base import ContentFile
import datetime
from django.urls import reverse
from django.contrib.sitemaps import ping_google
import uuid
# from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from multiselectfield import MultiSelectField
from django.utils.translation import get_language



class Autostop(models.Model):
    slug = models.SlugField(null=True, blank=True, max_length=150, unique = True,verbose_name='Ссылка')
    content = models.TextField(max_length=5500, null=True, blank=True, verbose_name='Описание') 
    published = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано') 
    departure_time = models.DateTimeField(verbose_name='Дата и время отправления', null=True, blank=True)
    locations = models.TextField(max_length=2000, null=True, blank=True, verbose_name='Точки') 
    locations_addresses = models.TextField(max_length=2000, null=True, blank=True, verbose_name='Адреса точек') 

    
    RUBRIC_CHOICES = (
        ('people', _('Люди')),
        ('animals', _('Животные')),
        ('good', _('Вещи')), # отображение, обозначение
        ('food', _('Продукты')),
        ('others', _('Другое')),
    )
    rubric = MultiSelectField(choices=RUBRIC_CHOICES, max_length=100,null=True,verbose_name='Рубрика')
    seats_left = models.IntegerField(null=True, blank=True, verbose_name='Кол-во свободных мест')

    author = models.ForeignKey('account.Account',null=True, on_delete=models.CASCADE, verbose_name='Автор', blank=True)

    views = models.PositiveIntegerField(default=0, verbose_name='Просмотры')

    #User
    favourites = models.ManyToManyField('account.Account', related_name="favourite", default=None, blank=True, verbose_name = "Понравившиеся публикации")

    STATUS_CHOICES = (
        ('published', 'Опубликовано'),
        ('draft', 'На рассмотрении'),
        ('rejected', 'Отклонено'),
        ('edited', 'Изменено'),
        ('archive', 'В архиве'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Изменение нашей модели для админ-панели
    class Meta:
        verbose_name_plural='Объявления' # verbose - подробный
        verbose_name= 'Объявление'
        ordering=['-published']
    


    def save(self,  *args, **kwargs):
        if not self.pk:
            if Autostop.objects.filter(slug=self.slug).exists():
                self.slug = str(uuid.uuid4()).replace('-','')
            else:
                self.slug = str(uuid.uuid4()).replace('-','')
            super(Autostop, self).save(*args, **kwargs)
        else:
            super(Autostop, self).save(*args, **kwargs)

        try:
            ping_google() # Вы можете захотеть «пинговать» Google, когда ваша карта сайта изменится, чтобы он знал, что нужно переиндексировать ваш сайт
        except Exception:
            pass


    def locations_as_list(self): # использовано в my_routes.html
        return self.locations_addresses.split(';')
    def first_last_location(self): # использовано в my_routes.html
        return [self.locations_addresses.split(';')[0],self.locations_addresses.split(';')[-1]]
    # https://www.google.com.ua/maps/dir/50.4572194,30.5086202/50.4593158,30.4911548/50.4626926,30.4903405/@50.4623922,30.4965738,15z
    def get_google_routing(self): # использовано в my_routes.html
        return f"https://www.google.com.ua/maps/dir/{self.locations.replace(';','/')}/@{self.locations.split(';')[-1]},15z"

    def __str__(self):
        return self.author.email
        
    
    def get_absolute_url(self): # sitemap
        if get_language() == 'ru':
            return f'/ru/route/{self.slug}/'
        else:
            return f'/route/{self.slug}/'


class Application(models.Model):
    route = models.ForeignKey('Autostop',null=True, on_delete=models.CASCADE,verbose_name='Заявка')  
    comment = models.TextField(max_length=5500, null=True, blank=True, verbose_name='Комментарий') 
    published = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано') 
    locations = models.TextField(max_length=2000, null=True, blank=True, verbose_name='Точки') 
    locations_addresses = models.TextField(max_length=2000, null=True, blank=True, verbose_name='Адреса точек') 

    STATUS_CHOICES = (
        ('considering', _('На рассмотрении')),
        ('justified', _('Подтверждена')),
        ('rejected', _('Отклонена')),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='considering')


    RUBRIC_CHOICES = (
        ('people', _('Люди')),
        ('animals', _('Животные')),
        ('good', _('Вещи')),
        ('food', _('Продукты')),
        ('others', _('Другое')),
    )
    rubric = MultiSelectField(choices=RUBRIC_CHOICES, max_length=100,null=True,verbose_name='Рубрика')
    author = models.ForeignKey('account.Account',null=True, on_delete=models.CASCADE, verbose_name='Автор', blank=True)

    unique_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        verbose_name_plural='Заявки' # verbose - подробный
        verbose_name= 'Заявка'
        ordering=['-published']

        
    def locations_as_list(self): # использовано в applied_to_me.html
        return self.locations_addresses.split(';')
    def first_last_location(self): # использовано в telegram_view.py
        return [self.locations_addresses.split(';')[0],self.locations_addresses.split(';')[-1]]

    def __str__(self):
        return f'{self.pk}'




class PassengerAutostop(models.Model):
    slug = models.SlugField(null=True, blank=True, max_length=150, unique = True,verbose_name='Ссылка')
    content = models.TextField(max_length=5500, null=True, blank=True, verbose_name='Описание') 
    published = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано') 
    departure_time = models.DateTimeField(verbose_name='Дата и время отправления', null=True, blank=True)
    locations = models.TextField(max_length=2000, null=True, blank=True, verbose_name='Точки') 
    locations_addresses = models.TextField(max_length=2000, null=True, blank=True, verbose_name='Адреса точек') 
    
    RUBRIC_CHOICES = (
        ('people', _('Люди')),
        ('animals', _('Животные')),
        ('good', _('Вещи')),
        ('food', _('Продукты')),
        ('others', _('Другое')),
    )
    rubric = MultiSelectField(choices=RUBRIC_CHOICES, max_length=100,null=True,verbose_name='Рубрика')

    author = models.ForeignKey('account.Account',null=True, on_delete=models.CASCADE, verbose_name='Автор', blank=True)
    views = models.PositiveIntegerField(default=0, verbose_name='Просмотры')

    STATUS_CHOICES = (
        ('published', 'Опубликовано'),
        ('draft', 'На рассмотрении'),
        ('rejected', 'Отклонено'),
        ('edited', 'Изменено'),
        ('archive', 'В архиве'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Изменение нашей модели для админ-панели
    class Meta:
        verbose_name_plural='Пассажир. объявления' # verbose - подробный
        verbose_name= 'Пассажир. объявление'
        ordering=['-published']
    


    def save(self,  *args, **kwargs):
        if not self.pk:
            if PassengerAutostop.objects.filter(slug=self.slug).exists():
                self.slug = str(uuid.uuid4()).replace('-','')
            else:
                self.slug = str(uuid.uuid4()).replace('-','')
            super(PassengerAutostop, self).save(*args, **kwargs)
        else:
            super(PassengerAutostop, self).save(*args, **kwargs)

        try:
            ping_google() # Вы можете захотеть «пинговать» Google, когда ваша карта сайта изменится, чтобы он знал, что нужно переиндексировать ваш сайт
        except Exception:
            pass


    def locations_as_list(self): # использовано в 
        return self.locations_addresses.split(';')
    def first_last_location(self): # использовано в 
        return [self.locations_addresses.split(';')[0],self.locations_addresses.split(';')[-1]]
    def get_google_routing(self): # использовано в 
        return f"https://www.google.com.ua/maps/dir/{self.locations.replace(';','/')}/@{self.locations.split(';')[-1]},15z"

    def __str__(self):
        return self.author.email
        
    
    def get_absolute_url(self): # sitemap
        if get_language() == 'ru':
            return f'/ru/route_passenger/{self.slug}/'
        else:
            return f'/route_passenger/{self.slug}/'



from slugify import slugify
from ckeditor_uploader.fields import RichTextUploadingField
class PidvezuBlog(models.Model):
    title_ru = models.CharField(verbose_name='Название', max_length=200)
    title_uk = models.CharField(verbose_name='Назва (uk)', max_length=200, blank=True, null=True)
    slug = models.SlugField(max_length=150, unique = True,verbose_name='Ссылка', blank=True, null=True)
    post_content_ru = RichTextUploadingField(verbose_name='Содержание post\'a', blank=True, null = True)
    post_content_uk = RichTextUploadingField(verbose_name='Змiст post\'a (uk)', blank=True, null=True) 
    published = models.DateTimeField(auto_now_add=True,verbose_name='Опубликовано') 
    views = models.PositiveIntegerField(default=0, verbose_name='Просмотры')
    author = models.ForeignKey('account.Account',null=True, on_delete=models.CASCADE, verbose_name='Автор', blank=True)
    
    og_image = models.CharField(verbose_name='og:image ссылка на фото', max_length=200, default='')

    
    STATUS_CHOICES = (
        ('published', 'Published'),
        ('draft', 'Draft'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
	
    class Meta:
        verbose_name_plural='Публикации блога' # verbose - подробный
        verbose_name= 'Публикация'	
        ordering=['-published']



    def __str__(self):
        return self.title_ru


    def save(self,  *args, **kwargs):
        if not self.pk:
            if PidvezuBlog.objects.filter(title_ru=self.title_ru).exists():
                self.slug = slugify(self.title_ru) + "-" + str(uuid.uuid4())
            else:
                self.slug = slugify(self.title_ru)
            super(PidvezuBlog, self).save(*args, **kwargs)
        else:
            super(PidvezuBlog, self).save(*args, **kwargs)
            
        try:
            ping_google() # Вы можете захотеть «пинговать» Google, когда ваша карта сайта изменится, чтобы он знал, что нужно переиндексировать ваш сайт
        except Exception:
            pass
        
    
    def get_absolute_url(self): # sitemap
        if get_language() == 'ru':
            return f'/ru/blog/{self.slug}/'
        else:
            return f'/blog/{self.slug}/'



