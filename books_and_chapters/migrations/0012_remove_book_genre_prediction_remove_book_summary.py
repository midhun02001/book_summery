# Generated by Django 5.1.1 on 2024-09-29 10:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books_and_chapters', '0011_alter_chapter_book'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='genre_prediction',
        ),
        migrations.RemoveField(
            model_name='book',
            name='summary',
        ),
    ]
