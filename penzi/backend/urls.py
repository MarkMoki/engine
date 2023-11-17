from django.urls import path
from .views import MessageReceiveView, UserCreateView

urlpatterns = [
    path('receive-message/', MessageReceiveView.as_view(), name='receive_message'),
    path('create-user/', UserCreateView.as_view(), name='create_user'),
]