# coding=utf-8

from django.contrib import auth
from django.contrib import messages as msgs
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _

from servo.models.note import Note
from servo.models.order import Order
from servo.models.common import Location
from servo.models.account import UserProfile
from servo.forms.account import ProfileForm
  
def login(request):
    if 'username' in request.POST:
        user = auth.authenticate(username=request.POST['username'],
            password=request.POST['password'])
        
        if user is not None and user.is_active:
            auth.login(request, user)
            msgs.add_message(request, msgs.INFO, _('Moi, %s!' % user.username))
            return redirect('/orders/')
        else:
            msgs.add_message(request, msgs.INFO,
            	_(u'Väärä käyttäjätunnus tai salasana'))
    
    return render(request, 'accounts/login.html')

def logout(request):
    auth.logout(request)
    msgs.add_message(request, msgs.INFO, _(u'Kirjauduit ulos'))
    return redirect('/accounts/login/')

def settings(request):
    if request.method == 'POST':
    	data = request.POST.copy()
    	data['user'] = request.user.id
        profile = request.user.get_profile()
        form = ProfileForm(data, instance=profile)

        if form.is_valid():
        	profile = form.save()
        else:
        	print form.errors
        	return render(request, 'accounts/settings.html', {'form': form})
        
        if request.POST.get('password'):
            request.user.set_password(request.POST['password'])

        request.session['user_profile'] = profile
        msgs.add_message(request, msgs.INFO, _(u'Asetukset tallennettu'))
        return redirect('servo.views.account.settings')
    else:
        form = ProfileForm(instance=request.user.get_profile())
        return render(request, 'accounts/settings.html', {'form': form})

def home(request):
    data = dict()
    data['orders'] = Order.objects.filter(user=request.user)
    return render(request, 'accounts/home.html', data)

def messages(request, message_id=None, flags='01'):
    messages = Note.objects.filter(recipient=request.user)

    if message_id:
        message = Note.objects.get(pk=message_id)
        return render(request, 'accounts/view_message.html', {
            'msgs': messages, 'msg': message
            })

    return render(request, 'accounts/messages.html', {'msgs': messages})
