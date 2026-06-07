from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.shortcuts import render
from django.shortcuts import redirect

def login_view(request):

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:

            login(request, user)

            return redirect('dashboard')

    return render(
        request,
        'login.html'
    )