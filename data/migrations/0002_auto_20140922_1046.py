# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0007_auto_20140922_1046'),
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gamedata',
            name='bye',
        ),
        migrations.RemoveField(
            model_name='gamedata',
            name='date',
        ),
        migrations.RemoveField(
            model_name='gamedata',
            name='espn_game_id',
        ),
        migrations.RemoveField(
            model_name='gamedata',
            name='home_game',
        ),
        migrations.RemoveField(
            model_name='gamedata',
            name='opponent',
        ),
        migrations.RemoveField(
            model_name='gamedata',
            name='pointsAgainst',
        ),
        migrations.RemoveField(
            model_name='gamedata',
            name='pointsFor',
        ),
        migrations.RemoveField(
            model_name='gamedata',
            name='week_number',
        ),
        migrations.RemoveField(
            model_name='gamedata',
            name='win',
        ),
        migrations.RemoveField(
            model_name='gamedata',
            name='year',
        ),
        migrations.AddField(
            model_name='gamedata',
            name='matchup',
            field=models.ForeignKey(to='game.Matchup', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='yeardata',
            name='team',
            field=models.ForeignKey(default=33, to='game.Team'),
            preserve_default=True,
        ),
    ]
