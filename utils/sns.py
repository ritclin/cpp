import boto3
from django.conf import settings

def subscribe_user_email_to_sns(email):
    sns = boto3.client('sns', region_name=settings.AWS_REGION)

    response = sns.subscribe(
        TopicArn=settings.AWS_SNS_TOPIC_ARN,
        Protocol='email',
        Endpoint=email,
        ReturnSubscriptionArn=False
    )
    return response
