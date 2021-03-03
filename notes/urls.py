from django.urls import path
from .views import NoteOperationsView

urlpatterns = [
    path('', NoteOperationsView.as_view(), name='note-list'),
]
