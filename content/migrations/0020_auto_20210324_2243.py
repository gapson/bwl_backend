# Generated by Django 3.1.6 on 2021-03-25 02:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0019_auto_20210324_2239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='credit',
            name='balance',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name='Balance'),
        ),
    ]
