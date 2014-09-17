# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_matchup'),
    ]

    operations = [
        migrations.AddField(
            model_name='matchup',
            name='away_team',
            field=models.ForeignKey(related_name=b'away_team', to='game.Team', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='matchup',
            name='home_team',
            field=models.ForeignKey(related_name=b'home_team', to='game.Team'),
        ),
    ]
