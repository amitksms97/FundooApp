# Generated by Django 3.1.6 on 2021-03-01 05:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0002_auto_20210226_1219'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notes',
            name='collaborator',
        ),
        migrations.RemoveField(
            model_name='notes',
            name='color',
        ),
        migrations.RemoveField(
            model_name='notes',
            name='label',
        ),
        migrations.DeleteModel(
            name='Label',
        ),
    ]
