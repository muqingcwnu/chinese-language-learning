from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm

# Create your views here.

def login_view(request):
    if request.user.is_authenticated:
        return redirect('main_core:home')
        
    if request.method == 'POST':
        username = request.POST.get('login')
        password = request.POST.get('password')
        remember = request.POST.get('remember')
        
        from django.contrib.auth import authenticate
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            if not remember:
                request.session.set_expiry(0)
            next_url = request.POST.get('next', 'main_core:home')
            messages.success(request, _('Welcome back, {}!').format(user.username))
            return redirect(next_url)
        else:
            messages.error(request, _('Invalid username or password.'))
    
    return render(request, 'registration/login.html')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('main_core:home')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _('Account created successfully! Welcome to China\'s Legacy!'))
            return redirect('main_core:home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, _('You have been logged out successfully.'))
    return redirect('main_core:home')
