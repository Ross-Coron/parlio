# Generated by Django 4.1.5 on 2023-03-25 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parlio', '0003_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='uin',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]