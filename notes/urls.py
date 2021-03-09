from django.urls import path
from .views import NoteOperationsView, LabelOperationsView, AddCollaboratorForNotes, ListCollaboratorAPIView, \
    TrashNotes, SearchAPIView, ArchiveNotes, AddReminderToNotes, SendReminderEmail

urlpatterns = [
    path('', NoteOperationsView.as_view(), name='note-list'),
    path('label/', LabelOperationsView.as_view(), name='label-list'),
    path('collab/', AddCollaboratorForNotes.as_view(), name='collab'),
    path('list-collaborator/', ListCollaboratorAPIView.as_view(), name='list-collab'),
    path('trash/', TrashNotes.as_view()),
    path('search/', SearchAPIView.as_view()),
    path('archive/', ArchiveNotes.as_view()),
    path('remmail/', SendReminderEmail.as_view()),
    path('reminder/', AddReminderToNotes.as_view(), name='reminder'),

]
