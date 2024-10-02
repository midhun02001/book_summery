from django.db import models
from django import forms
from django.utils.text import slugify
from django.contrib.auth.models import User

def generate_unique_slug(_class, field):
    """
    Return a unique slug if the original slug exists.
    eg: foo-bar => foo-bar-1
    """
    origin_slug = slugify(field)
    unique_slug = origin_slug
    numb = 1
    while _class.objects.filter(slug=unique_slug).exists():
        unique_slug = f'{origin_slug}-{numb}'
        numb += 1
    return unique_slug

class Book(models.Model):
    added_by_user = models.ForeignKey(User, on_delete=models.CASCADE)
    book_name = models.CharField(max_length=200)
    author_name = models.CharField(max_length=200)
    book_read_on = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=200, unique=True)
    # genre_prediction = models.CharField(max_length=100, blank=True, null=True)  # New field for genre prediction
    # summary = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.book_name

    def save(self, *args, **kwargs):
        if not self.slug or slugify(self.book_name) != self.slug:
            self.slug = generate_unique_slug(Book, self.book_name)
        super(Book, self).save(*args, **kwargs)

class Chapter(models.Model):
    book = models.ForeignKey(Book, related_name='chapters', on_delete=models.CASCADE)
    chapter_number = models.IntegerField()
    description = models.TextField()
    rating = models.FloatField(default=0.0)  # Average rating
    rating_count = models.IntegerField(default=0)  # Number of ratings

    def __str__(self):
        return f"{self.book.book_name}: Chapter {self.chapter_number}"

class DateInput(forms.DateInput):
    input_type = 'date'

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'
        exclude = ('slug', 'added_by_user')
        widgets = {
            'book_read_on': DateInput(),
        }

class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ['chapter_number', 'description']
