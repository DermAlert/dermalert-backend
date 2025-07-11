# Generated by Django 5.2 on 2025-07-02 16:15

import accounts.managers.user
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', accounts.managers.user.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='patient',
            name='other_gender',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='patient',
            name='phone_number',
            field=models.CharField(max_length=15),
        ),
        migrations.AlterField(
            model_name='user',
            name='cpf',
            field=models.CharField(error_messages={'unique': 'A user with that cpf already exists.'}, help_text='', max_length=11, unique=True, verbose_name='CPF'),
        ),
    ]
