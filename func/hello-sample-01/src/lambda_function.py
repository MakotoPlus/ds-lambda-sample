import sys

def handler(event, context):
    print('handler ----------start')
    print(event)
    print(context)
    print('handler ----------end')
    return 'Hello from AWS Lambda using Python' + sys.version + '!'

def output_context(context):
    print('context')
    print(context)
    return 0

def output_event(event):
    print('event')
    print(event)
    return 0

