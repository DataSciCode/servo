from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib import auth
from django import forms
from django.contrib import messages as msgs
from django.utils.translation import ugettext as _

from servo.models import Location, UserProfile, Order, Note

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile

def logout(request):
    auth.logout(request)
    msgs.add_message(request, msgs.INFO, _(u'Kirjauduit ulos'))
    return redirect('/user/login/')
  
def login(request):
    if 'username' in request.POST:
        user = auth.authenticate(username=request.POST['username'],
            password=request.POST['password'])
        
        if user is not None and user.is_active:
            auth.login(request, user)
            msgs.add_message(request, msgs.INFO, _('Moi, %s!' % user.username))
            return redirect('/orders/index/user/%s/' % user.username)
        else:
            print 'authentication failed'
      
    return render(request, 'users/login.html')

def settings(request):
    if request.method == 'POST':
        (profile, created) = UserProfile.objects.get_or_create(user=request.user)
        location_id = request.POST.get('location')
        if location_id:
            loc = Location.objects.get(pk=location_id)
            profile.location = loc

        profile.phone = request.POST.get('phone')
        profile.tech_id = request.POST.get('tech_id')
        profile.locale = request.POST.get('locale')
        profile.save()
        
        if request.POST.get('password'):
            request.user.set_password(request.POST['password'])

        profile.save()
        request.session['user_profile'] = profile

        msgs.add_message(request, msgs.INFO, _(u'Asetukset tallennettu'))
        return redirect('/home/settings/')
    else:
        form = ProfileForm(instance=request.session.get('user_profile'))
        return render(request, 'users/settings.html', {'form': form})

def home(request):
    data = dict()
    data['orders'] = Order.objects.filter(user=request.user)
    return render(request, 'users/home.html', data)

def messages(request, message_id=None, flags='01'):
    messages = Note.objects.filter(recipient=request.user)

    if message_id:
        message = Note.objects.get(pk=message_id)
        return render(request, 'users/view_message.html', {
            'msgs': messages, 'msg': message
            })

    return render(request, 'users/messages.html', {'msgs': messages})
