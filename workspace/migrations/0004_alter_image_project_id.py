# Generated by Django 3.2.4 on 2021-11-27 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspace', '0003_auto_20211127_2012'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='project_id',
            field=models.IntegerField(),
        ),
    ]
