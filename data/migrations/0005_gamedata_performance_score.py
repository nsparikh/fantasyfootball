# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0004_auto_20140922_1256'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamedata',
            name='performance_score',
            field=models.DecimalField(null=True, max_digits=5, decimal_places=2),
            preserve_default=True,
        ),
    ]
