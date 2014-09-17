# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_auto_20140916_1439'),
    ]

    operations = [
        migrations.CreateModel(
            name='Matchup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('espn_game_id', models.IntegerField(null=True)),
                ('year', models.IntegerField()),
                ('date', models.DateField(null=True)),
                ('week_number', models.IntegerField()),
                ('bye', models.BooleanField(default=None)),
                ('win', models.BooleanField(default=None)),
                ('pointsFor', models.IntegerField(null=True)),
                ('pointsAgainst', models.IntegerField(null=True)),
                ('home_team', models.ForeignKey(to='game.Team')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
