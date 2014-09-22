# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0003_yeardata_average'),
    ]

    operations = [
        migrations.AlterField(
            model_name='yeardata',
            name='average',
            field=models.DecimalField(default=0, max_digits=5, decimal_places=2),
        ),
    ]
