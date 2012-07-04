# coding=utf-8
from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from servo.models import Issue, Message, Order

class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue

def edit(req, id=None, order_id=None, kind='symptom'):
    if req.method == 'POST':
        if 'id' in req.POST:
            issue = Issue.objects.get(pk=req.POST['id'])
        else:
            issue = Issue(created_by=req.user,
                order_id=req.POST.get('order_id'))

        if req.POST.get('symptom'):
            issue.symptom = req.POST.get('symptom')

        if req.POST.get('diagnosis'):
            issue.diagnosis = req.POST.get('diagnosis')

        if req.POST.get('solution'):
            issue.solution = req.POST.get('solution')

        issue.save()
        return HttpResponse('Tehtävä tallennettu')
    else:
        if id:
            issue = Issue.objects.get(pk=id)
        else:
            issue = Issue(order_id=order_id)

        form = IssueForm()
        description = getattr(issue, kind)
        templates = Message.objects.filter(is_template=True)

        return render(req, 'issues/form.html', {'issue': issue,
            'templates': templates, 'form': form,
            'kind': kind,
            'description': description})

def remove(req, id=None):
    if 'id' in req.POST:
        issue = Issue.objects.get(pk=req.POST['id'])
        issue.delete()
        return HttpResponse('Tehtävä poistettu')
    else:
        issue = Issue.objects.get(pk=id)
        return render(req, 'issues/remove.html', {'issue': issue})
