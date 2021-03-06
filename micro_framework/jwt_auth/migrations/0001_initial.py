# Generated by Django 3.0.1 on 2020-01-01 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Policy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('rules', models.TextField()),
                ('notes', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Policy',
                'verbose_name_plural': 'Policies',
                'db_table': 'policies',
            },
        ),
    ]
