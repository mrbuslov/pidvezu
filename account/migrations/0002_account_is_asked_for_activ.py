# Generated by Django 3.2.10 on 2022-04-17 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='is_asked_for_activ',
            field=models.BooleanField(default=False),
        ),
    ]
