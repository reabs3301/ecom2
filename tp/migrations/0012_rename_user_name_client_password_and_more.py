# Generated by Django 5.1.6 on 2025-03-19 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tp', '0011_delete_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='client',
            old_name='user_name',
            new_name='password',
        ),
        migrations.RemoveField(
            model_name='client',
            name='user_password',
        ),
        migrations.AddField(
            model_name='client',
            name='username',
            field=models.CharField(default='client', max_length=50, unique=True),
            preserve_default=False,
        ),
    ]
