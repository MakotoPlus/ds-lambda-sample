from django.shortcuts import render
import logging
import json
import uuid
import boto3
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, TemplateView
import botocore 
import botocore.session 
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig 

# シークレットマネージャのID
SERCRET_ID = 'arn:aws:secretsmanager:ap-northeast-1:847754671288:secret:dev/test/sercret-mIeZux'

# Create your views here.
class MessageView(TemplateView):
    '''
    MessageView
    '''
    template_name = "sqs_message/index.html"

    success_url = reverse_lazy("sqs_message:index")

    #変数
    def get_context_data(self, **kwargs):
        #print(kwargs)
        context = super().get_context_data(**kwargs)
        context['sqs'] = 'sqs_event'
        #
        # secretsmanager
        #
        #client = boto3.client('secretsmanager')
        #response = client.get_secret_value(SecretId=SERCRET_ID)
        #print("SERCRED-RESPONSE------------")
        #print(response)
        #params = json.loads(response['SecretString'])
        
        client = botocore.session.get_session().create_client('secretsmanager')
        cache_config = SecretCacheConfig()
        cache = SecretCache(config = cache_config, client = client)
        response = cache.get_secret_string(secret_id=SERCRET_ID)
        print(response)
        params = json.loads(response)
        context["message"] = params['sercretid']
        return context

    #get処理
    def get(self, request, *args, **kwargs):
        print(kwargs)
        return super().get(request, *args, **kwargs)

    #post処理
    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context)
        context["message"] = request.POST.get('message')
        context["sqs"] = request.POST.get('sqs')
        sqs_client = boto3.client('sqs')
        send_sqs = sqs_client.get_queue_url(QueueName=request.POST.get('sqs'))['QueueUrl']
        print(f'SQS=[{send_sqs}]')
        print("BOTO3 send_message")
        print(context["message"])
        sqs_message = {
            "id": str(uuid.uuid4()),
            "SendMessage": str(context["message"])
        }
        response = sqs_client.send_message(
            QueueUrl=send_sqs,
            DelaySeconds=0,
            MessageBody=(json.dumps(sqs_message)))
        print("BOTO3 send_message-----------end")
        responsed_feiled = response.get('Failed')
        if responsed_feiled:
          context["message"]="send_messages ERROR"
          print(responsed_feiled)
        else:
          context["message"]="send_messages SUCCESS"
        return render(request, self.template_name, context=context)
    