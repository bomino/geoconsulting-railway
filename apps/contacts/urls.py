from django.urls import path

from apps.contacts.views import ContactView

urlpatterns = [
    path("", ContactView.as_view(), name="contact"),
]
