from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.ListNoteView.as_view(), name='note-list'),
    path('', views.NoteCreateView.as_view(), name='create_note'),
    path('note/', views.NoteCreateView.as_view(), name='create_note'),
]
