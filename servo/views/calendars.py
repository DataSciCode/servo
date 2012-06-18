from django.shortcuts import render
from django.http import HttpResponse

from datetime import datetime, timedelta
from servo.models import Calendar, CalendarEvent

def edit(req, id):
	pass

def index(req):
	calendars = Calendar.objects.filter(user = req.session.get("user"))
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
	id = req.POST.get("id")
	calendar = Calendar.objects(id = ObjectId(req.POST.get("calendar"))).first()

	if id:
		event = CalendarEvent.objects(id = ObjectId(id))
	else:
		event = CalendarEvent(calendar = calendar)

	event.description = req.POST.get("description")
	started = req.POST.getlist("started_at")
	finished = req.POST.getlist("finished_at")

	fmt = "%d.%m.%y %H:%M" # @fixme - date format should be locale-specific
	event.started_at = datetime.strptime(" ".join(started), fmt)
	event.finished_at = datetime.strptime(" ".join(finished), fmt)
	delta = event.finished_at - event.started_at
	event.hours = int(delta.seconds/3600)

	calendar.hours += event.hours
	calendar.events.append(event)
	calendar.save()

	return HttpResponse("Tapahtuma tallennettu")

def event(req, calendar_id):
	calendar = Calendar.objects(id = ObjectId(calendar_id)).first()
	event = CalendarEvent(calendar = calendar)
	event.finished_at = event.started_at + timedelta(hours = event.hours)
	return render(req, "calendars/event_form.html", {"event": event})

def remove(req, id = None):
	if req.method == "POST":
		Calendar.objects(id = ObjectId(req.POST['id'])).delete()
		return HttpResponse("Kalenteri poistettu")
	else:
		calendar = Calendar.objects(id = ObjectId(id)).first()
		return render(req, "calendars/remove.html", calendar)

def events(req, id):
	cal = Calendar.objects(id = ObjectId(id)).first()
	calendars = Calendar.objects(user = req.session.get("user"))
	return render(req, "calendars/events.html", {"calendar": cal,
		"calendars": calendars})
