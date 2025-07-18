# Generated by Django 5.1.4 on 2025-07-12 18:52

import accounts.models
import imagekit.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_alter_follow_followed_alter_follow_follower'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', accounts.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='banner',
            field=imagekit.models.fields.ProcessedImageField(blank=True, null=True, upload_to='banners/%Y/%m'),
        ),
    ]
