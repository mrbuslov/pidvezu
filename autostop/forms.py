from django.forms import ModelForm
from django import forms
from .models import Application, Autostop, PassengerAutostop, PidvezuBlog
from django.utils.translation import gettext_lazy as _

class AutostopForm(ModelForm):
    class Meta:
        model = Autostop
        fields=('content','rubric','seats_left')     # 'locations','locations_addresses',

        widgets = {
            'content':forms.Textarea(attrs={'placeholder':_('Напишите Ваши условия и дополнительную информацию...')}), # 'onkeyup':"charCount()", 
        } 
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ApplicationForm(ModelForm):
    class Meta:
        model = Application
        fields=('comment','rubric')

        widgets = {
            'comment':forms.Textarea(attrs={'placeholder':_('Напишите дополнительную информацию...')}), # 'onkeyup':"charCount()", 
        } 
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    
class PassengerAutostopForm(ModelForm):
    class Meta:
        model = PassengerAutostop
        fields=('content','rubric')     # 'locations','locations_addresses',

        widgets = {
            'content':forms.Textarea(attrs={'placeholder':_('Напишите Вашу дополнительную информацию, чтобы водители увидели её...')}), # 'onkeyup':"charCount()", 
        } 
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        

class BlogForm(ModelForm):
    class Meta:
        model = PidvezuBlog
        fields=('title_ru','title_uk','post_content_ru','post_content_uk')

        widgets = {
            'title_ru':forms.TextInput(attrs={'placeholder':'Название публикации...'}), 
            'title_uk':forms.TextInput(attrs={'placeholder':_('Название публикации...')}), 
            'post_content_ru':forms.Textarea(attrs={'placeholder':'Описание публикации...'}), 
            'post_content_uk':forms.Textarea(attrs={'placeholder':_('Описание публикации...')}), 
        } 
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)