# Generated by Django 3.1.6 on 2021-03-20 02:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('content', '0015_auto_20210318_0017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playlist',
            name='media',
            field=models.ManyToManyField(blank=True, related_name='media_playlists', to='content.Media', verbose_name='Media'),
        ),
        migrations.CreateModel(
            name='ThemeSuggestions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='Created Date')),
                ('modified', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='Modified Dtae')),
                ('text', models.TextField(verbose_name='Message')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_theme_suggestions', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name_plural': 'Theme Suggestions',
            },
        ),
    ]
