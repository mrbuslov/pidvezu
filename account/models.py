from distutils.command.upload import upload
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid

from io import BytesIO
from PIL import ExifTags, Image as PIL_Image
from django.core.files.base import ContentFile

class MyAccountManager(BaseUserManager):
	def create_user(self, email, password=None, phone_number=None):
		if not email:
			raise ValueError('Введите email')

		user = self.model(
			email=self.normalize_email(email),
			phone_number=phone_number,
		)

		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, password):
		user = self.create_user(
			email=self.normalize_email(email),
			password=password,
		)
		user.is_admin = True
		user.is_staff = True
		user.is_superuser = True
		user.save(using=self._db)
		return user


from django.contrib.auth.models import PermissionsMixin
class Account(AbstractBaseUser, PermissionsMixin):
	image 					= models.ImageField(null=True, blank=True)
	email 					= models.EmailField(verbose_name="email", max_length=60, unique=True)
	phone_number			= models.CharField(max_length=20, verbose_name='Номер телефона', blank=True, unique=True, null=True)
	first_name				= models.CharField(max_length=30, default='', blank=True)
	last_name				= models.CharField(max_length=30, default='', blank=True)
	car_description 		= models.TextField(max_length=1000, default='', blank=True, null=True)
	rides 					= models.PositiveIntegerField(default=0, verbose_name='Кол-во поездок')
	is_asked_for_activ		= models.BooleanField(default=False)

	telegram = models.BooleanField(null=True, default=False, verbose_name='Telegram')
	chat_id = models.BigIntegerField(null=True, blank=True, verbose_name='chat id', editable=False)

	
	date_joined				= models.DateTimeField(verbose_name='Дата регистрации', auto_now_add=True)
	last_login				= models.DateTimeField(verbose_name='Последний вход', auto_now=True)
	is_admin				= models.BooleanField(default=False)
	is_active				= models.BooleanField(default=True)
	is_staff				= models.BooleanField(default=False)
	is_superuser			= models.BooleanField(default=False)
	is_blocked				= models.BooleanField(default=False)
	unique_code				= models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

	USERNAME_FIELD = 'email'

	objects = MyAccountManager()

	def __str__(self):
		return self.email
	
	def get_first_part_email(self): # использовано в base.html
		return self.email.split('@')[0]

	def save(self, *args, **kwargs):
		if self.image:
			related_img = Account.objects.get(id=self.id)
			if related_img.image != self.image:
				filename = translate("%s.jpg" % self.image.name[:self.image.name.rfind('.')])
			
				image = PIL_Image.open(self.image)
				try:
					if image.mode != "RGB":
						image = image.convert("RGB")
				except:
					pass

				try:
					for orientation in ExifTags.TAGS.keys():
						if ExifTags.TAGS[orientation] == 'Orientation':
							break
					exif = dict(image._getexif().items())

					if exif[orientation] == 3:
						image = image.rotate(180, expand=True)
					elif exif[orientation] == 6:
						image = image.rotate(270, expand=True)
					elif exif[orientation] == 8:
						image = image.rotate(90, expand=True)
				except:
					pass
				image_io = BytesIO()
				image.save(image_io, format='JPEG', quality=70)

				# change the image field value to be the newly modified image value
				self.image.save(f'images/users/{self.email.split("@")[0]}_{str(uuid.uuid4())}.jpg', ContentFile(image_io.getvalue()), save=False)
			
		super(Account, self).save(*args, **kwargs)

def translate(string):
	dic = {'Ь':'', 'ь':'', 'Ъ':'', 'ъ':'', 'А':'A', 'а':'a', 'Б':'B', 'б':'b', 'В':'V', 'в':'v',
		'Г':'G', 'г':'g', 'Д':'D', 'д':'d', 'Е':'E', 'е':'e', 'Ё':'E', 'ё':'e', 'Ж':'Zh', 'ж':'zh',
		'З':'Z', 'з':'z', 'И':'I', 'и':'i', 'Й':'I', 'й':'i', 'К':'K', 'к':'k', 'Л':'L', 'л':'l',
		'М':'M', 'м':'m', 'Н':'N', 'н':'n', 'О':'O', 'о':'o', 'П':'P', 'п':'p', 'Р':'R', 'р':'r', 
		'С':'S', 'с':'s', 'Т':'T', 'т':'t', 'У':'U', 'у':'u', 'Ф':'F', 'ф':'f', 'Х':'Kh', 'х':'kh',
		'Ц':'Tc', 'ц':'tc', 'Ч':'Ch', 'ч':'ch', 'Ш':'Sh', 'ш':'sh', 'Щ':'Shch', 'щ':'shch', 'Ы':'Y',
		'ы':'y', 'Э':'E', 'э':'e', 'Ю':'Iu', 'ю':'iu', 'Я':'Ia', 'я':'ia'}
		
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

	return result.replace(' ','_').lower()
