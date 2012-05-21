from servo3.models import Calendar, CalendarEvent
from django.shortcuts import render
from django.http import HttpResponse

from bson import ObjectId
from datetime import datetime

def index(req):
  calendars = Calendar.objects(user = req.session.get("user"))
  return render(req, "calendars/index.html", {"calendars": calendars})
  
def create(req):
	calendar = Calendar()
	return render(req, "calendars/form.html", {"calendar": calendar})

def save(req):
	if "id" in req.POST:
		cal = Calendar.objects(id = ObjectId(req.POST['id']))
	else:
		cal = Calendar()

	cal.title = req.POST.get("title")
	cal.user = req.session.get("user")
	cal.save()

	return HttpResponse("Kalenteri tallennettu")

def save_event(req):

	if data.get("id"):
		event = CalendarEvent.objects(id = ObjectId(data.get("id")))
	else:
		calendar = Calendar.objects(id = ObjectId(data.get("calendar")))
		event = CalendarEvent(calendar = calendar)

	cal = Calendar.objects(id = ObjectId(req.POST['id'])).first()
	event.calendar = cal
	started = req.POST.getlist("started_at")
	finished = req.POST.getlist("finished_at")
	event.started_at = datetime.strptime(" ")
	event.finished_at = ""
	event.save()

	return HttpResponse("Tapahtuma tallennettu")

def event(req, calendar_id):
	calendar = Calendar.objects(id = ObjectId(calendar_id)).first()
	event = CalendarEvent()
	return render(req, "calendars/event_form.html", {
		"calendar": calendar, "event": event
	})

def remove(req, id = None):
	if req.method == "POST":
		Calendar.objects(id = ObjectId(req.POST['id'])).delete()
		return HttpResponse("Kalenteri poistettu")
	else:
		calendar = Calendar.objects(id = ObjectId(id)).first()
		return render(req, "calendars/remove.html", calendar)

def events(req, id):
	cal = Calendar.objects(id = ObjectId(id)).first()
	return render(req, "calendars/events.html", {"calendar": cal})
