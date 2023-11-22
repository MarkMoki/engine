from django.urls import path
from .views import MessageReceiveView, UserCreateView, TwilioResponseView

urlpatterns = [
    path('receive-message/', MessageReceiveView.as_view(), name='receive_message'),
    path('create-user/', UserCreateView.as_view(), name='create_user'),
    path('twilio-webhook/', TwilioResponseView.as_view(), name='twilio-webhook'),
]