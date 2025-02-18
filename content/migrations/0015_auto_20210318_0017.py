# Generated by Django 3.1.6 on 2021-03-18 04:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('content', '0014_auto_20210308_2103'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='currency',
            options={'ordering': ('name',), 'verbose_name_plural': 'currencies/Region'},
        ),
        migrations.AlterModelOptions(
            name='media',
            options={'ordering': ('published_date',)},
        ),
        migrations.RemoveField(
            model_name='credit',
            name='currency',
        ),
        migrations.AddField(
            model_name='currency',
            name='region_name',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='Region Name'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='amount_paid',
            field=models.FloatField(default=0, verbose_name='Amount Paid'),
        ),
        migrations.AlterField(
            model_name='appsetting',
            name='name',
            field=models.CharField(default='Default Setting', editable=False, max_length=100, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='credit',
            name='balance',
            field=models.FloatField(verbose_name='Balance'),
        ),
        migrations.AlterField(
            model_name='credit',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_credits', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AlterField(
            model_name='playlist',
            name='media',
            field=models.ManyToManyField(blank=True, null=True, related_name='media_playlists', to='content.Media', verbose_name='Media'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='date_end',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Date End'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='payment_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Payment Date'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='deposit',
            field=models.FloatField(verbose_name='Deposit credit'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_transactions', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='withdraw',
            field=models.FloatField(verbose_name='Withdrawal credit'),
        ),
        migrations.AlterUniqueTogether(
            name='appsetting',
            unique_together={('name',)},
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='Created Date')),
                ('modified', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='Modified Dtae')),
                ('credit', models.FloatField(verbose_name='Number of credit')),
                ('is_active', models.BooleanField(default=True, help_text='UnCheck this box if this price is not available anymore', verbose_name='Is active?')),
                ('date_start', models.DateTimeField(blank=True, null=True, verbose_name='Date Start')),
                ('date_end', models.DateTimeField(blank=True, null=True, verbose_name='Date End')),
                ('media', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='media_prices', to='content.media', verbose_name='Media')),
                ('offer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='offer_prices', to='content.offer', verbose_name='Offer')),
            ],
            options={
                'verbose_name_plural': 'Prices',
                'ordering': ('date_start',),
            },
        ),
        migrations.CreateModel(
            name='CreditSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='Created Date')),
                ('modified', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='Modified Dtae')),
                ('value_in_currency', models.FloatField(default=1, verbose_name='Value In Currency')),
                ('credit', models.FloatField(verbose_name='Number of Credit')),
                ('is_active', models.BooleanField(default=True, help_text='UnCheck this box if this credit setting is not available anymore', verbose_name='Is active?')),
                ('date_start', models.DateTimeField(blank=True, null=True, verbose_name='Date Start')),
                ('date_end', models.DateTimeField(blank=True, null=True, verbose_name='Date End')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='currency_credits_setting', to='content.currency', verbose_name='Region/Currency')),
            ],
            options={
                'ordering': ('created',),
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='transaction',
            name='credit_setting',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='crdit_setting_transactions', to='content.creditsetting', verbose_name='Credit Setting'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='offer_price',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='content.price', verbose_name='Offer Price'),
        ),
        migrations.DeleteModel(
            name='OfferPrice',
        ),
    ]
