# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0006_auto_20140917_1213'),
    ]

    operations = [
        migrations.RenameField(
            model_name='matchup',
            old_name='pointsAgainst',
            new_name='away_team_points',
        ),
        migrations.RenameField(
            model_name='matchup',
            old_name='pointsFor',
            new_name='home_team_points',
        ),
    ]
