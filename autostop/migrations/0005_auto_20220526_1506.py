# Generated by Django 3.2.10 on 2022-05-26 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autostop', '0004_passengerautostop_og_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='passengerautostop',
            name='og_image',
        ),
        migrations.AddField(
            model_name='pidvezublog',
            name='og_image',
            field=models.CharField(default='', max_length=200, verbose_name='og:image ссылка на фото'),
        ),
    ]
