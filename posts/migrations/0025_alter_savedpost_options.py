# Generated by Django 5.1.4 on 2025-07-06 14:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0024_alter_post_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='savedpost',
            options={'ordering': ['-created'], 'verbose_name': ' سیو پست', 'verbose_name_plural': ' سیو پست ها'},
        ),
    ]
