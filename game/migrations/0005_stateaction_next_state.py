# Generated by Django 2.0.3 on 2019-05-02 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_stateaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='stateaction',
            name='next_state',
            field=models.CharField(default='[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]', max_length=100),
        ),
    ]
