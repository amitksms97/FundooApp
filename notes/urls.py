from django.urls import path
from . import views

urlpatterns = [
    path('view/', views.ListNoteView.as_view(), name='note-list'),
    path('label/', views.LabelCreateView.as_view(), name='create_label'),
    path('', views.NoteCreateView.as_view(), name='create_note'),
    path('label/', views.LabelCreateView.as_view(), name='create_label'),
    path('note/', views.NoteCreateView.as_view(), name='create_note'),
    path('noteupdate/<int:id>/', views.NoteUpdateView.as_view(), name='note_update'),
]
