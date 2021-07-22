from django.shortcuts import redirect, render
from .models import Music, Photo
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .forms import ListenForm
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm


import boto3
import uuid

S3_BASE_URL = 'http://s3.us-east-1.amazonaws.com/'
BUCKET = 'music-memories-p4'
# Create your views here.

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def music_index(request):
    music = Music.objects.all()
    return render(request, 'music/index.html', {'music': music})

def add_listen(request, music_id):
    form = ListenForm(request.POST)
    if form.is_valid():
        new_listen = form.save(commit=False)
        new_listen.music_id = music_id
        new_listen.save()
    return redirect('detail', music_id=music_id)

class MusicCreate(CreateView):
    model = Music
    fields = '__all__'
    success_url = '/music/'

class MusicUpdate(UpdateView):
    model = Music
    fields = ['artist', 'album', 'song', 'genre', 'comments']
    success_url = '/music/'

class MusicDelete(DeleteView):
    model = Music
    success_url = '/music/'

def music_detail(request, music_id):
    music = Music.objects.get(id=music_id)
    listen_form = ListenForm()
    return render(request, 'music/detail.html', {
        'music': music,
        'listen_form': listen_form,})

def add_photo(request, music_id):
    photo_file = request.FILES.get('photo-file', None)
    if photo_file:
        s3 = boto3.client('s3')
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        try:
            s3.upload_fileobj(photo_file, BUCKET, key)
            url = f"{S3_BASE_URL}{BUCKET}/{key}"
            photo = Photo(url=url, music_id=music_id)
            photo.save()
        except Exception as error:
            print('An error occured uploading file to S3')
            print(error)
    return redirect('detail', music_id=music_id)

def signup(request):
  error_message = ''
  if request.method == 'POST':
    # This is how to create a 'user' form object
    # that includes the data from the browser
    form = UserCreationForm(request.POST)
    if form.is_valid():
      # This will add the user to the database
      user = form.save()
      # This is how we log a user in via code
      login(request, user)
      return redirect('index')
    else:
      error_message = 'Invalid sign up - try again'
  # A bad POST or a GET request, so render signup.html with an empty form
  form = UserCreationForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'registration/signup.html', context)
