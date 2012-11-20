# coding=utf-8

from django import forms
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from orders.models import Order
from servo.models import Property, Tag
from customers.models import Customer, ContactInfo

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer

def index(request, *args, **kwargs):
    if request.method == "POST":
        q = request.POST.get('query')
        try:
            (key, value) = q.split('=')
            # allow searching customers by arbitrary key/values
            customer_list = Customer.objects.filter(**{key: value.strip()})
        except Exception, e:
            customer_list = Customer.objects.filter(name__icontains=q)
    else:
        if 'tag' in kwargs:
            customer_list = Customer.objects.filter(tags__pk=kwargs['tag'])
        else:
            customer_list = Customer.objects.all()

    page = request.GET.get('page')
    paginator = Paginator(customer_list, 50)

    try:
        customers = paginator.page(page)
    except PageNotAnInteger:
        customers = paginator.page(1)
    except EmptyPage:
        customers = paginator.page(paginator.num_pages)

    tags = Tag.objects.filter(type='customer')
    return render(request, 'customers/index.html', {
        'customers': customers, 'tags': tags})

def create_order(request, customer_id):
    order = Order.objects.create(customer_id=customer_id,
        created_by=request.user)
    return redirect(order)

def add_order(request, customer_id, order_id):
    order = Order.objects.get(pk=order_id)
    customer = Customer.objects.get(pk=customer_id)
    order.customer = customer
    order.save()

    messages.add_message(request, messages.INFO, _(u'Asiakas lisätty'))
    return redirect(order)

def notes(request, customer_id, note_id=None):
    from notes.forms import NoteForm
    customer = Customer.objects.get(pk=customer_id)
    form = NoteForm(initial={'recipient': customer.name})

    return render(request, "notes/form.html", {'form': form})

def view(request, id):
    c = Customer.objects.get(pk=id)
    
    customers = Customer.objects.all()
    paginator = Paginator(customers, 25)
    customers = paginator.page(1)
    orders = Order.objects.filter(customer__tree_id=c.tree_id)
    tags = Tag.objects.filter(type='customer')

    return render(request, 'customers/view.html', {
        'customer': c,
        'customers': customers,
        'tags': tags,
        'orders': orders
        })

def edit(request, customer_id=0, parent_id=0):
    form = CustomerForm()
    fields = Property.objects.filter(type='customer')
    customer = Customer()

    if int(customer_id) > 0:
        customer = Customer.objects.get(pk=customer_id)
        form = CustomerForm(instance=customer)

    if parent_id:
        customer.parent = Customer.objects.get(pk=parent_id)
        form = CustomerForm(initial={'parent': parent_id})

    return render(request, 'customers/form.html', {
        'id': customer_id,
        'form': form,
        'fields' : fields,
        'customer': customer
        })

def save(request, customer_id):
    keys = request.POST.getlist("keys")
    values = request.POST.getlist("values")
    props = dict()

    form = CustomerForm(request.POST, request.FILES)

    if not form.is_valid():
        return render(request, "customers/form.html", {'form': form})

    for k, v in enumerate(values):
        if v != '':
            key = keys[k]
            props[key] = v
    
    if int(customer_id) > 0:
        c = Customer.objects.get(pk=customer_id)
        # clear out old contact info
        ContactInfo.objects.filter(customer=c).delete()
        form = CustomerForm(request.POST, instance=c)
    
    if form.is_valid():
        c = form.save()
        for k, v in props.items():
            if v != '':
                ContactInfo.objects.create(key=k, value=v, customer=c)
                
        messages.add_message(request, messages.INFO, _(u'Asiakas tallennettu'))
        return redirect(c)

def delete(request, customer_id=None):
    if request.method == "POST":
        c = Customer.objects.filter(pk=customer_id).delete()
        messages.add_message(request, messages.INFO, _(u'Asiakas poistettu'))
        return redirect('/customers/')
    else:
        c = Customer.objects.get(pk=customer_id)
        return render(request, 'customers/remove.html', {'customer': c})

def move(request, id=None, target=None):
    """
    Move a customer under another customer
    """
    if id and target:
        customer = Customer.objects.get(pk=id)
        target = Customer.objects.get(pk=target)
        customer.move_to(target)
        messages.add_message(request, messages.INFO, _(u'Asiakas siirretty'))

        return redirect(customer)

    if id:
        customer = Customer.objects.get(pk=id)

    return render(request, 'customers/move.html', {'customer': customer})

def search(request):
    import json
    from django.http import HttpResponse
    results = list()
    query = request.GET.get("query")
    customers = Customer.objects.filter(name__icontains=query)

    for c in customers:
        results.append("%s <%s>" %(c.name, c.email))
        results.append("%s <%s>" %(c.name, c.phone))

    return HttpResponse(json.dumps(results), content_type="application/json")
