# Generated by Django 3.2.4 on 2021-11-27 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspace', '0004_alter_image_project_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='project_id',
            field=models.IntegerField(default=0),
        ),
    ]