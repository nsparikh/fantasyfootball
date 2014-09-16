# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_team_division'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='dob',
            field=models.DateField(null=True, verbose_name=b'Date of Birth'),
        ),
    ]
