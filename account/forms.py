import imp
from django.forms import ModelForm
from account.models import Account
from django import forms
from django.utils.translation import gettext_lazy as _

class ProfileEditForm(ModelForm):
    class Meta:
        model = Account
        fields=('image','first_name', 'last_name', 'phone_number', 'car_description', 'telegram')    

        widgets = {
            # 'first_name':forms.TextInput(attrs={'placeholder':'Имя'}),
            # 'last_name':forms.TextInput(attrs={'placeholder':'Фамилия'}),
            # 'phone_number':forms.TextInput(attrs={'placeholder':'Номер телефона'}),
            'car_description':forms.Textarea(attrs={'placeholder':_('Опишите Ваше транспортное средство...')}),
            'telegram': forms.CheckboxInput(),
        } 
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

