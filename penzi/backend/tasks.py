from celery import shared_task
from .helpers import send_response_function  # Import your function for sending responses

@shared_task
def send_multiple_responses(response1, response2):
    # Call your function to send responses asynchronously
    send_response_function(response1)
    send_response_function(response2)
