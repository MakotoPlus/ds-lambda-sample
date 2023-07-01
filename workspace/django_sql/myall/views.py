import logging
import json
import uuid
import boto3
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, TemplateView
from myall import models
from myall.service.paypay.form_paypay import FormPaypay
from myall.service.line.form_line import FormLine
from . import sqllogic

logger = logging.getLogger(__name__)

# Create your views here.
def index(request):
    logger.info('index start-------------')
    records = sqllogic.check_01_select_related('マキマ')
    for record in records:
        print("++++++++++++++++")
        for blogTagRecord in record.blogTaglist:
            print("-----")
            print(f'tag=[{blogTagRecord.tag.name}],title=[{blogTagRecord.blog.title}]')
    print(records)
    logger.info('index end-------------')
    #for q in connection.queries:
    #    print(q)
    context = {
        "records": records,
        "abc": "test"
    }
    return render(request, 'myall/index.html', context)

class ManyToManyListView(ListView):
    template_name = 'myall/many_2_many.html'
    model = models.MTag

class MBlogListView(ListView):
    template_name = 'myall/mbloglist.html'
    model = models.MBlog
    context_object_name = 'mblogss'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mblogss'] = self.model.objects.filter(
                tags=models.MTag.objects.get(pk=self.kwargs['pk']))
        return context

class PayPayView(CreateView):
    '''
    PayPayView
    '''
    template_name = "myall/adjust/create.html"
    form_class = FormPaypay
    success_url = reverse_lazy("myall:adjustlist")

    def form_valid(self, form):
        data = form.save(commit=False)
        data.save()
        adjust = models.GenericAdjustment(content_object=data, tag="paypay")
        adjust.save()
        return super().form_valid(form)

class LineView(CreateView):
    '''
    LineView
    '''
    template_name = "myall/adjust/create.html"
    form_class = FormLine
    success_url = reverse_lazy("myall:adjustlist")

    def form_valid(self, form):
        data = form.save(commit=False)
        data.save()
        adjust = models.GenericAdjustment(content_object=data, tag="line")
        adjust.save()
        return super().form_valid(form)


class AdjustListView(ListView):
    template_name = 'myall/adjust/list.html'
    model = models.GenericAdjustment
    context_object_name = 'genericAdjustmentList'

class AdjustDetailView(TemplateView):
    template_name = 'myall/adjust/detail.html'
    #model = models.GenericAdjustment
    
    def get_context_data(self,**kwargs):
        context_object_name = 'detail'
        context = super().get_context_data(**kwargs)
        adjust = models.GenericAdjustment.objects.get(pk=self.kwargs['pk'])
        if isinstance(adjust.content_object, models.PayPay):
            context['paypay'] = adjust.content_object
            self.template_name = 'myall/adjust/paypay/detail.html'
        else:
            context['line'] = adjust.content_object
            self.template_name = 'myall/adjust/line/detail.html'
        return context
    
