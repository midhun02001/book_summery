from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
import requests
from .models import Book, Chapter, BookForm, ChapterForm
from django.contrib import messages
from .summarize import Summarizer
import json
from datetime import datetime, timedelta
from .models import Book, Chapter, BookForm, ChapterForm  # Ensure this is correct
import pickle, random
import os


def get_random_quote():
    module_dir = os.path.dirname(__file__)  # get current directory
    file_path = os.path.join(module_dir, 'quotes_dump.pckl')
    with open(file_path, 'rb') as file:
        obj = pickle.load(file)
        quote = random.choice(obj)
        return quote

def homepage(request):
    books = Book.objects.filter(added_by_user=request.user).order_by('book_read_on')
    form_error = False
    last_month = datetime.today() - timedelta(days=30)
    last_month_books_count = Book.objects.filter(
        added_by_user=request.user,
        book_read_on__gt=last_month
    ).count()
    
    total_chapters = Chapter.objects.filter(book__added_by_user=request.user).count()
    quote = get_random_quote()
    
    # Prepare data for reading progress visualization
    books_per_month = [0] * 12  # List to hold the count of books for each month
    for month in range(1, 13):  # 1 to 12 for each month
        count = Book.objects.filter(
            added_by_user=request.user,
            book_read_on__month=month
        ).count()
        books_per_month[month - 1] = count  # month - 1 because list index starts at 0

    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.added_by_user = request.user
            form.save()
            form = BookForm()
            messages.success(request, 'Book added successfully!')
        else:
            form_error = True
    else:
        form = BookForm()

    context = {
        'quote': quote,
        'books': books,
        'add_book_form': form,
        'form_error': form_error,
        'last_month_books_count': last_month_books_count,
        'total_chapters': total_chapters,
        'total_books': len(books),
        'books_per_month': books_per_month,  # Add the books_per_month data
    }
    return render(request, 'books.html', context)

def get_book_details(request, slug):
    book = get_object_or_404(Book, slug=slug)

    # Check if the user has permission to view this book
    if book.added_by_user != request.user:
        messages.error(request, 'You are not authenticated to perform this action')
        return redirect('books')

    try:
        chapters = Chapter.objects.filter(book=book).order_by('chapter_number')
    except Chapter.DoesNotExist:
        chapters = None

    # Calculate summary if chapters exist
    if chapters:
        text = ''
        for chap in chapters:
            text += chap.description
        
        summarizer = Summarizer(text)
        summary = summarizer.get_summary(int(summarizer.get_length() * 0.4))
    else:
        summary = ''

    # Get user books
    books = Book.objects.filter(added_by_user=request.user).order_by('book_read_on')
    
    # Initialize forms
    add_book_form = BookForm()
    add_chapter_form = ChapterForm()  # No need to pass 'initial' here, as we will set the book in the hidden input

    # Prepare chapter data for visualization
    chapter_data = []
    for chapter in chapters:
        chapter_data.append({
            'chapter': chapter,
            'average_rating': chapter.rating,  # Average rating for the chapter
            'rating_count': chapter.rating_count  # Count of ratings for the chapter
        })

    context = {
        'books': books,
        'chapters': chapter_data,  # Pass chapter data instead of chapter directly
        'book_detail': book,
        'add_book_form': add_book_form,
        'add_chapter_form': add_chapter_form,
        'summary': summary,
    }
    return render(request, 'book_detail.html', context)


def edit_book_details(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if book.added_by_user != request.user:
        messages.error(request, 'You are not authenticated to perform this action')
        return redirect('books')

    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book details updated successfully!')
            return redirect('book_detail', slug=book.slug)
    else:
        form = BookForm(instance=book)

    return render(request, 'modals/book_detail_edit_modal.html', {'form': form,'book': book})


def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if book.added_by_user != request.user:
        messages.error(request, 'You are not authenticated to perform this action')
        return redirect('books')
    book.delete()
    return redirect('books')

def add_chapter(request, slug):
    # Retrieve the book using the slug
    book = get_object_or_404(Book, slug=slug)

    # Check if the user is authenticated to add a chapter to the book
    if book.added_by_user != request.user:
        messages.error(request, 'You are not authenticated to perform this action')
        return redirect('book_detail', slug=book.slug)

    if request.method == 'POST':
        form = ChapterForm(request.POST)
        if form.is_valid():
            new_chapter = form.save(commit=False)
            new_chapter.book = book  # Associate the chapter with the book
            new_chapter.save()
            messages.success(request, 'Chapter added successfully!')
            return redirect('book_detail', slug=book.slug)
        else:
            messages.error(request, 'Failed to add chapter. Please correct the errors.')
    else:
        form = ChapterForm()

    context = {
        'add_chapter_form': form,
        'book': book,
    }
    return render(request, 'book_detail_chapteradd.html', context)







def edit_chapter(request, pk):
    chapter = get_object_or_404(Chapter, pk=pk)
    if chapter.book.added_by_user != request.user:
        messages.error(request, 'You are not authenticated to perform this action')
        return redirect('books')
    
    if request.method == 'POST':
        form = ChapterForm(request.POST, instance=chapter)
        if form.is_valid():
            form.save()
            messages.success(request, 'Chapter updated successfully!')
            return redirect('book_detail', slug=chapter.book.slug)

    form = ChapterForm(instance=chapter)
    return render(request, 'modals/chapter_edit_modal.html', {'form': form})

def edit_fromchapter(request, pk):
    chapter = get_object_or_404(Chapter, pk=pk)
    if chapter.book.added_by_user != request.user:
        messages.error(request, 'You are not authenticated to perform this action')
        return redirect('books')
    
    if request.method == 'POST':
        form = ChapterForm(request.POST, instance=chapter)
        if form.is_valid():
            form.save()
            messages.success(request, 'Chapter updated successfully!')
            return redirect('book_detail', slug=chapter.book.slug)
    else:
        form = ChapterForm(instance=chapter)
    book = chapter.book  # Assuming a ForeignKey relationship

    return render(request, 'modals/book_detail_chapteradd.html', {'form': form, 'chapter': chapter,'book':book})

def delete_chapter(request, pk):
    chapter = get_object_or_404(Chapter, pk=pk)
    if chapter.book.added_by_user != request.user:
        messages.error(request, 'You are not authenticated to perform this action')
        return redirect('books')
    
    chapter.delete()
    messages.success(request, 'Chapter deleted successfully!')
    return redirect('book_detail', slug=chapter.book.slug)


def search_book(request):
    if request.is_ajax():
        q = request.GET.get('term')
        books = Book.objects.filter(
                book_name__icontains=q,
                added_by_user=request.user
            )[:10]
        results = []
        for book in books:
            book_json = {}
            book_json['slug'] = book.slug
            book_json['label'] = book.book_name
            book_json['value'] = book.book_name
            results.append(book_json)
        data = json.dumps(results)
    else:
        book_json = {}
        book_json['slug'] = None
        book_json['label'] = None
        book_json['value'] = None
        data = json.dumps(book_json)
    return HttpResponse(data)

from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .models import Book, Chapter
import google.generativeai as genai

# Configure Gemini API with your API key
genai.configure(api_key="AIzaSyAEpxEaoSLL6Z6gBM3Ha0edMAECjW6h61g")

from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def genre_prediction(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    genre_prediction = None
    summary = ''

    if request.method == "POST":
        # Calculate the summary as you did in get_book_details
        chapters = Chapter.objects.filter(book=book).order_by('chapter_number')
        summary = ''.join(chap.description for chap in chapters)  # Efficient way to concatenate

        if summary:
            user_input = f"Please classify the genre of the following book summary in a safe and respectful manner:\n\n{summary}"

            try:
                # Call the Gemini model
                model = genai.GenerativeModel(model_name="gemini-1.5-flash")
                chat_session = model.start_chat(history=[])
                response = chat_session.send_message(user_input)
                
                # Check if response is valid and safe
                if response and hasattr(response, 'text'):
                    genre_prediction = response.text
                else:
                    messages.error(request, 'The response from the API was not valid.')
            
            except Exception as e:
                # Handle cases where response is flagged as unsafe or other exceptions occur
                messages.error(request, f'The content could not be processed: {str(e)}')
        
        else:
            messages.error(request, 'The book has no summary to analyze.')
            return redirect('book_detail', slug=book.slug)

        # Generate word cloud
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(summary)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')

        # Save the word cloud image to a BytesIO object
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()

        # Encode the image to base64 string
        wordcloud_image = base64.b64encode(image_png).decode('utf-8')

        # Redirect to the genre prediction result page
        return render(request, 'genre_prediction_result.html', {
            'book_id': book_id,
            'summary': summary,
            'genre_prediction': genre_prediction,
            'wordcloud_image': wordcloud_image,
        })

    # If method is not POST, redirect back to the book details
    return redirect('book_detail', slug=book.slug)

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def download_report(request):
    if request.method == 'POST':
        summary = request.POST.get('summary', '')
        genre_prediction = request.POST.get('genre_prediction', '')
        wordcloud_image = request.POST.get('wordcloud_image', '')

        context = {
            'summary': summary,
            'genre_prediction': genre_prediction,
            'wordcloud_image': wordcloud_image,
        }
        return render_to_pdf('genre_prediction_report.html', context)
    return HttpResponse("Invalid request", status=400)

# Replace with your API key and URL
API_KEY = 'AIzaSyDBUzgtJ2Jvt1ztpgUwZc5r_VAWClZGfxU'
API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent'

# Define predefined responses for the chatbot
PREDEFINED_RESPONSES = {
    'hello': 'Hi there! How can I assist you today?',
    'bye': 'Goodbye! Have a great day!',
    # Add more predefined responses as needed
}

def chatbot(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')
        conversation_history = request.session.get('conversation_history', [])

        # Append user message to the conversation history
        conversation_history.append(f"input: {user_message}")
        bot_reply = PREDEFINED_RESPONSES.get(user_message.lower(), None)  # Case insensitive match

        if not bot_reply:
            # Make a request to the Google API if the message is not predefined
            headers = {'Content-Type': 'application/json'}
            messages = [{'text': message} for message in conversation_history]

            data = {'contents': [{'parts': messages}]}

            try:
                response = requests.post(f'{API_URL}?key={API_KEY}', headers=headers, json=data)
                response.raise_for_status()
                api_response = response.json()
                bot_reply = api_response['candidates'][0]['content']['parts'][0]['text']
                bot_reply = '. '.join(bot_reply.split('. ')[:3])  # Limit response to 3 sentences
            except requests.RequestException as e:
                print(f"API request error: {e}")
                bot_reply = 'Sorry, there was an error processing your request.'

        # Append bot reply to conversation history
        conversation_history.append(f"output: {bot_reply}")
        request.session['conversation_history'] = conversation_history

        # Return the bot reply as a JSON response
        return JsonResponse({'reply': bot_reply})

    return render(request,'chatbot.html')
