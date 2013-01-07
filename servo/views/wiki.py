#coding=utf-8

from django.shortcuts import redirect
from django import forms
from django.views.generic import TemplateView, ListView, DetailView
from servo.models.common import Article

class ArticleListView(ListView):
    model = Article
    template = 'articles/index.html'

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title', 'content')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input-xxlarge'}),
            'content': forms.Textarea(attrs={'class': 'input-xxlarge', 'rows': 30})
        }

class ArticleEditView(TemplateView):
    template_name = 'articles/form.html'

    def get_context_data(self, **kwargs):
        form = ArticleForm()

        if kwargs.get('pk'):
            article = Article.objects.get(pk=kwargs['pk'])
            form = ArticleForm(instance=article)
        
        context = super(ArticleEditView, self).get_context_data(**kwargs)
        context['form'] = form
        return context

    def post(self, *args, **kwargs):

        if kwargs.get('pk'):
            article = Article.objects.get(pk=kwargs['pk'])
        else:
            article = Article()

        article.updated_by = self.request.user
        form = ArticleForm(self.request.POST, instance=article)
        
        if form.is_valid():
            article = form.save()
            return redirect(article)

        print form.erorrs

class ArticleDetailView(DetailView):

    template_name = 'articles/view.html'
    model = Article
    queryset = Article.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super(ArticleDetailView, self).get_context_data(**kwargs)
        context['object_list'] = Article.objects.all()
        return context
