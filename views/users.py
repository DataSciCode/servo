import hashlib
from servo3.models import User, Location
from django.shortcuts import redirect, render
from django.http import HttpResponse

def logout(req):
  if "confirm" in req.POST:
    return redirect("/user/login")
    
  return render(req, "users/logout.html")
  
def login(req):
  if "email" in req.POST:
    pw = hashlib.sha1(req.POST['password']).hexdigest()
    user = User.objects(email = req.POST['email'], password = pw).first()
    
    if user:
      req.session['user'] = user
      return redirect("/orders/index/user/%s" %(user.username))
      
  return render(req, "users/login.html")
  
def settings(req):
  if req.method == "POST":
    req.session['user'].phone = req.POST['phone']
    loc = Location.objects(id = req.POST['location']).first()
    req.session['user'].location = loc
    req.session['user'].save()
    return HttpResponse('Asetukset tallennettu')
  else:
    user = req.session.get("user")
    locations = Location.objects.all()
    return render(req, 'users/settings.html', {'user': user, 'locations': locations})
    