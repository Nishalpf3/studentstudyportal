from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .forms import *
from django.views import generic
from youtubesearchpython import VideosSearch
import requests
# Create your views here.

def home(request):
    return render (request,'dashboard/home.html')


def notes(request):
    if request.method == "POST":
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(user=request.user,title=request.POST['title'],description=request.POST['description'])
            notes.save()
        messages.success(request,f"NOtes Added from {request.user.username} Successfully!")
    else:
        form = NotesForm()
    notes = Notes.objects.filter(user=request.user)
    context = {'notes':notes,'form':form}
    return render (request, 'dashboard/notes.html',context)


def delete_note(request, pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect("notes")

class NotesDetailView(generic.DetailView):
    model = Notes


def homework(request):
    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            homeworks = Homework(
                user = request.user,
                subject = request.POST['subject'],
                title = request.POST['title'],
                description = request.POST['description'],
                due = request.POST['due'],
                is_finished = finished
            )
            homeworks.save()
            messages.success(request,f'Homework Added from {request.user.username}!!.')
    else:
        form = HomeworkForm()
    homework = Homework.objects.filter(user=request.user)
    if len(homework) == 0:
        homework_done = True
    else:
        homework_done = False
    context = {'homeworks':homework,
               'homework_done':homework_done, 
               'form':form,
               }
    return render(request, 'dashboard/homework.html',context)


def update_homework(request, pk=None):
    homework = get_object_or_404(Homework, id=pk)
    if request.method == 'POST':
        if 'is_finished' in request.POST:
            homework.is_finished = True
        else:
            homework.is_finished = False
        homework.save()
    return redirect('homework')



def delete_homework(request, pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect("homework")


def youtube(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        video = VideosSearch(text,limit=10)
        result_list = []
        for i in video.result()['result']:
            result_dict = {
                'input':text,
                'title':i['title'],
                'duration':i['duration'],
                'thumbnail':i['thumbnails'][0]['url'],
                'channel':i['channel']['name'],
                'link':i['link'],
                'views':i['viewCount']['short'],
                'published':i['publishedTime']
            }
            desc = ''
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    desc += j['text']
            result_dict['description'] = desc
            result_list.append(result_dict)
            context={
                'form':form,
                'results':result_list
            }
        return render(request, 'dashboard/youtube.html',context)
    else:
        form = DashboardForm()
    context = {'form':form}
    return render(request, "dashboard/youtube.html", context)

def todo(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST["is_finished"]
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            todos = Todo(

                user = request.user,
                title = request.POST['title'],
                is_finished = finished
            )
            todos.save()
            messages.success(request,f"Todo Added From {request.user.username}!!..")
    else:
        form = TodoForm()
    todo = Todo.objects.filter(user=request.user)
    if len(todo) == 0:
        todos_done = True
    else:
        todos_done = False
    context = {
        'form':form,
        'todos':todo,
        'todos_done':todos_done
    }
    return render(request,"dashboard/todo.html",context)


def update_todo(request, pk=None):
    todo = get_object_or_404(Todo, id=pk)
    if request.method == 'POST':
        if 'is_finished' in request.POST:
            todo.is_finished = True
        else:
            todo.is_finished = False
        todo.save()
    return redirect('todo')


def delete_todo(request,pk=None):
    Todo.objects.get(id=pk).delete()
    return redirect("todo")



def books(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://www.googleapis.com/books/v1/volumes?q=" + text  # Use https
        try:
            r = requests.get(url)
            r.raise_for_status()  # Raise an HTTPError for bad responses
            answer = r.json()
            result_list = []
            for i in range(min(10, len(answer['items']))):
                item = answer['items'][i]
                volume_info = item.get('volumeInfo', {})
                image_links = volume_info.get('imageLinks', {})
                result_dict = {
                    'title': volume_info.get('title'),
                    'subtitle': volume_info.get('subtitle'),
                    'description': volume_info.get('description'),
                    'count': volume_info.get('pageCount'),
                    'categories': volume_info.get('categories'),
                    'rating': volume_info.get('averageRating'),
                    'thumbnail': image_links.get('thumbnail'),
                    'preview': volume_info.get('previewLink'),
                }
                result_list.append(result_dict)
            context = {
                'form': form,
                'results': result_list,
            }
            return render(request, 'dashboard/books.html', context)
        except requests.exceptions.RequestException as e:
            messages.error(request, f"An error occurred: {e}")
            context = {'form': form}
            return render(request, "dashboard/books.html", context)
    else:
        form = DashboardForm()
    context = {'form': form}
    return render(request, "dashboard/books.html", context)

def dictionary(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST.get('text')
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en_US/{text}"
        try:
            r = requests.get(url)
            r.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
            answer = r.json()
            phonetics = answer[0]['phonetics'][0].get('text', 'N/A')
            audio = answer[0]['phonetics'][0].get('audio', 'N/A')
            definition = answer[0]['meanings'][0]['definitions'][0].get('definition', 'N/A')
            example = answer[0]['meanings'][0]['definitions'][0].get('example', 'N/A')
            synonyms = answer[0]['meanings'][0]['definitions'][0].get('synonyms', [])
            context = {
                'form': form,
                'input': text,
                'phonetics': phonetics,
                'audio': audio,
                'definition': definition,
                'example': example,
                'synonyms': synonyms,
            }
        except requests.exceptions.RequestException as e:
            context = {
                'form': form,
                'input': text,
                'error': str(e),  # Pass the error message to the context
            }
        except (IndexError, KeyError) as e:
            context = {
                'form': form,
                'input': text,
                'error': 'Error parsing the dictionary API response.',
            }
        return render(request, "dashboard/dictionary.html", context)
    else:
        form = DashboardForm()
        context = {
            'form': form
        }
    return render(request, "dashboard/dictionary.html", context)
