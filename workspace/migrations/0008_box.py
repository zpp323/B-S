# Generated by Django 3.2.4 on 2021-12-18 06:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workspace', '0007_project_labels'),
    ]

    operations = [
        migrations.CreateModel(
            name='Box',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('box_width', models.FloatField()),
                ('box_height', models.FloatField()),
                ('vertex_left', models.FloatField()),
                ('vertex_top', models.FloatField()),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workspace.image')),
            ],
        ),
    ]