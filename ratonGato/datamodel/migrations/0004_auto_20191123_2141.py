# Generated by Django 2.2.6 on 2019-11-23 21:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datamodel', '0003_auto_20191123_2140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='move',
            name='game',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name='moves', to='datamodel.Game'),
        ),
    ]
