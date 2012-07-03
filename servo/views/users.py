import hashlib
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib import auth
from django import forms

from servo.models import Location, UserProfile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile

def logout(request):
    if 'confirm' in request.POST:
        auth.logout(request)
        return redirect('/user/login')
    
    return render(request, "users/logout.html")
  
def login(request):
    if 'username' in request.POST:
        user = auth.authenticate(username=request.POST['username'],
            password=request.POST['password'])
    
        if user is not None and user.is_active:
            auth.login(request, user)
            return redirect('/orders/index/user/%s' %(user.username))
        else:
            print 'authentication failed'
      
    return render(request, 'users/login.html')

def settings(request):
    if request.method == 'POST':
        loc = Location.objects.get(pk=request.POST.get('location'))
        profile = UserProfile.objects.get_or_create(user=request.user,
            location=loc)[0]
        profile.phone = request.POST.get('phone')
        profile.tech_id = request.POST.get('tech_id')
        profile.locale = request.POST.get('locale')
        profile.save()

        if request.POST.get('password'):
            request.user.set_password(request.POST['password'])

        profile.save()
        request.session['user_profile'] = profile

        return HttpResponse('Asetukset tallennettu')
    else:
        form = ProfileForm(instance=request.session.get('user_profile'))
        return render(request, 'users/settings.html', {'form': form})
