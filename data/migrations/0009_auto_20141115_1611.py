# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0008_datapoint_dstydsallowed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='yeardata',
            name='team',
            field=models.ForeignKey(default=33, to='game.Team', null=True),
        ),
    ]
