# Generated by Django 5.1.7 on 2025-04-16 11:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0007_matchcomment_matchmvpvote'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='matchcomment',
            options={'verbose_name': 'Commento Partita', 'verbose_name_plural': 'Commenti Partita'},
        ),
        migrations.AlterModelOptions(
            name='matchmvpvote',
            options={'verbose_name': 'Voto MVP', 'verbose_name_plural': 'Voti MVP'},
        ),
    ]
