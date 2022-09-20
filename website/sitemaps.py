from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from autostop.models import *
from django.db.models import Q



class AutostopSitemap(Sitemap):
    i18n = True 
    alternates = True 
    x_default = True 
    changefreq = 'always'
    
    def items(self):
        return Autostop.objects.filter(status='published')

class PassengerAutostopSitemap(Sitemap):
    i18n = True 
    alternates = True 
    x_default = True 
    changefreq = 'always'
    
    def items(self):
        return PassengerAutostop.objects.filter(status='published')


class PidvezuBlogSitemap(Sitemap):
    i18n = True 
    alternates = True 
    x_default = True 
    changefreq = 'always'
    
    def items(self):
        return PidvezuBlog.objects.filter(status='published')

