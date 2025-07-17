import boto3
import json
from django.conf import settings

def send_order_event(order, event_type):
    sqs = boto3.client('sqs')

    payload = {
        "order_id": order.id,
        "user": order.user.username,
        "supplier": order.supplier.name,
        "product": order.product.name,
        "quantity": order.quantity,
        "status": event_type,
        "reference_image": order.reference_image_url
    }

    sqs.send_message(
        QueueUrl=settings.SQS_QUEUE_URL,
        MessageBody=json.dumps(payload)
    )
