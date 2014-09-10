# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CareerData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DataPoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('passC', models.IntegerField(null=True)),
                ('passA', models.IntegerField(null=True)),
                ('passYds', models.IntegerField(null=True)),
                ('passTDs', models.IntegerField(null=True)),
                ('passInt', models.IntegerField(null=True)),
                ('rush', models.IntegerField(null=True)),
                ('rushYds', models.IntegerField(null=True)),
                ('rushTDs', models.IntegerField(null=True)),
                ('rec', models.IntegerField(null=True)),
                ('recYds', models.IntegerField(null=True)),
                ('recTDs', models.IntegerField(null=True)),
                ('recTar', models.IntegerField(null=True)),
                ('misc2pc', models.IntegerField(null=True)),
                ('miscFuml', models.IntegerField(null=True)),
                ('miscTDs', models.IntegerField(null=True)),
                ('points', models.IntegerField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GameData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('espn_game_id', models.IntegerField(null=True)),
                ('year', models.IntegerField()),
                ('date', models.DateField(null=True)),
                ('week_number', models.IntegerField()),
                ('bye', models.BooleanField(default=None)),
                ('home_game', models.BooleanField(default=None)),
                ('win', models.BooleanField(default=None)),
                ('pointsFor', models.IntegerField(null=True)),
                ('pointsAgainst', models.IntegerField(null=True)),
                ('projection', models.DecimalField(null=True, max_digits=5, decimal_places=1)),
                ('espn_projection', models.DecimalField(null=True, max_digits=5, decimal_places=1)),
                ('yahoo_projection', models.DecimalField(null=True, max_digits=5, decimal_places=1)),
                ('cbs_projection', models.DecimalField(null=True, max_digits=5, decimal_places=1)),
                ('data', models.ForeignKey(to='data.DataPoint')),
                ('opponent', models.ForeignKey(to='game.Team', null=True)),
                ('player', models.ForeignKey(to='game.Player')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='YearData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField()),
                ('data', models.ForeignKey(to='data.DataPoint')),
                ('player', models.ForeignKey(to='game.Player')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='careerdata',
            name='data',
            field=models.ForeignKey(to='data.DataPoint'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='careerdata',
            name='player',
            field=models.ForeignKey(to='game.Player'),
            preserve_default=True,
        ),
    ]
