# Generated by Django 3.0.5 on 2021-05-24 17:11

import datetime
from django.db import migrations, models
import djongo.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StoryGroup',
            fields=[
                ('group_id', djongo.models.fields.ObjectIdField(auto_created=True, primary_key=True, serialize=False)),
                ('group_name', models.CharField(max_length=255)),
                ('date_created', models.DateTimeField(default=datetime.datetime(2021, 5, 24, 17, 11, 59, 570612))),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('status', models.IntegerField(choices=[(0, 'Ongoing'), (1, 'Finished')])),
                ('vote_duration', models.DurationField()),
                ('vote_threshold', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
