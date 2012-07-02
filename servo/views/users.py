import hashlib
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib import auth

from servo.models import Location

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
        request.session['user'].phone = request.POST['phone']
        loc = Location.objects(id = request.POST['location']).first()
        request.session['user'].location = loc
        request.session['user'].save()
        return HttpResponse('Asetukset tallennettu')
    else:
        user = request.session.get("user")
        locations = Location.objects.all()
        return render(request, 'users/settings.html', {'user': user,
            'locations': locations})
