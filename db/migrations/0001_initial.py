# Generated by Django 2.2.5 on 2019-09-10 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('u_id', models.CharField(max_length=255, primary_key=True, serialize=False, verbose_name='User id, slack')),
                ('categories', models.CharField(default=None, max_length=1024, verbose_name='personal categories')),
                ('filter_list', models.CharField(default=None, max_length=1024, verbose_name='personal filter list')),
            ],
        ),
    ]
