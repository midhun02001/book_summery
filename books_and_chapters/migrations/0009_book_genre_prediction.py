# Generated by Django 5.1.1 on 2024-09-28 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books_and_chapters', '0008_remove_chapter_created_at_chapter_rating_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='genre_prediction',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
