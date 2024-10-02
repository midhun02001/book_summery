# forms.py
from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['book_name', 'author_name', 'book_read_on']  # Add other fields as necessary


from .models import Chapter

class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ['chapter_number', 'description']  # Fields from the Chapter model

        # Adding widgets for better control of form fields appearance
        widgets = {
            'chapter_number': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter chapter number',
                'min': 1  # Example: Setting minimum value for chapter number
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter chapter description',
                'rows': 4,  # Set number of rows for the textarea
            }),
        }

        # Adding labels for the form fields
        labels = {
            'chapter_number': 'Chapter Number',
            'description': 'Chapter Description',
        }
