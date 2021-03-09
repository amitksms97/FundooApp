from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Label, Notes
from ..serializers import NotesSerializer, LabelSerializer
import json


class NoteViewAPITest(TestCase):
    """ Test module for notes view API's """

    def setUp(self):
        self.client = Client()

        self.user1 = User.objects.create(username='king',
                                         email='king@gmail.com',
                                         password='pbkdf2_sha256$216000$aGGxmJs7k0Fw$ynwJewbvSZ+ATnenRDxizv4m00SlXvsogxxAX1guUxY=')
        self.user2 = User.objects.create(username='Queen',
                                         email='Queen@gmail.com',
                                         password='pbkdf2_sha256$216000$GatG7mLf52Ee$A/WyFsrsLBsruyPhXB8aY+OM3St+ODojLTa4Br6UYpM=')
        self.note_for_user1 = Notes.objects.create(title='title 1', note='note1', user=self.user1)
        self.note_for_user2 = Notes.objects.create(title='title 2', note='note2', user=self.user2)
        self.label_for_user1 = Label.objects.create(labelname='label1', user=self.user1)
        self.label_for_user2 = Label.objects.create(labelname='label2', user=self.user2)

        self.user1_credentials = {
            "username": "King",
            "password": "king123"
        }

        self.valid_payload = {
            "title": "Birthday Message",
            "note": "Test note"
        }

        self.invalid_payload = {
            "title": "Message",
            "note": ""
        }

        self.invalid_credentials = {
            'email': 'amit@gmail.com',
            'password': 'amit123'
        }

        self.valid_label_payload = {
            "label_name": "Greetings"
        }

        self.invalid_label_payload = {
            "label_name": ""
        }

    def test_get_all_notes_without_login(self):
        notes = Notes.objects.filter(user=self.user1)
        response = self.client.get(reverse('note-list'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_get_all_notes_if_login_with_invalid_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.invalid_credentials), content_type='json')
        response = self.client.get(reverse('create_note'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_get_all_notes_after_login(self):
        self.client.post(reverse('login'), data=json.dumps(self.user1_credentials), content_type='json')
        notes = Notes.objects.filter(user=self.user1)
        response = self.client.get(reverse('create_note'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_notes_of_with_is_archive_value_true_after_login(self):
        self.client.post(reverse('login'), data=json.dumps(self.user1_credentials), content_type='json')
        notes = Notes.objects.filter(user=self.user1)
        serializer = NotesSerializer(notes, many=True)
        response = self.client.get(reverse('create_note'))
        self.assertNotEqual(response.data, serializer.data)

    def test_create_notes_with_valid_payload_without_login(self):
        response = self.client.post(reverse('create_note'), data=json.dumps(self.valid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_create_notes_with_valid_payload_after_login(self):
        self.client.post(reverse('login'), data=json.dumps(self.user1_credentials), content_type='json')
        response = self.client.post(reverse('create_note'), data=json.dumps(self.valid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_notes_with_invalid_payload_after_login(self):
        self.client.post(reverse('login'), data=json.dumps(self.user1_credentials), content_type='json')
        response = self.client.post(reverse('create_note'), data=json.dumps(self.invalid_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    ### Test cases for update, delete note

    def test_get_notes_by_id_without_login(self):
        response = self.client.get(reverse('note_update', kwargs={'id': self.note_for_user1.id}))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_get_notes_by_id_after_login_with_invalid_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.invalid_credentials), content_type='json')
        response = self.client.get(reverse('note_update', kwargs={'id': self.note_for_user1.id}))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_get_notes_by_id_after_login(self):
        self.client.post(reverse('login'), data=json.dumps(self.user1_credentials), content_type='json')
        notes = Notes.objects.get(id=self.note_for_user1.id)
        serializer = NotesSerializer(notes)
        response = self.client.get(reverse('note_update', kwargs={'id': self.note_for_user1.id}))
        # self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_notes_by_id_of_other_user_after_login(self):
        self.client.post(reverse('login'), data=json.dumps(self.user1_credentials), content_type='json')
        response = self.client.get(reverse('note_update', kwargs={'id': self.note_for_user2.id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_notes_with_valid_payload_after_login(self):
        self.client.post(reverse('login'), data=json.dumps(self.user1_credentials), content_type='json')
        response = self.client.put(reverse('note_update', kwargs={'id': self.note_for_user1.id}),
                                   data=json.dumps(self.valid_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_notes_with_invalid_payload_after_login(self):
        self.client.post(reverse('login'), data=json.dumps(self.user1_credentials), content_type='json')
        response = self.client.put(reverse('note_update', kwargs={'id': self.note_for_user1.id}),
                                   data=json.dumps(self.invalid_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_notes_with_id_of_other_user_after_login(self):
        self.client.post(reverse('login'), data=json.dumps(self.user1_credentials), content_type='json')
        response = self.client.put(reverse('note_update', kwargs={'id': self.note_for_user2.id}),
                                   data=json.dumps(self.invalid_payload), content_type='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_note_without_login(self):
        response = self.client.delete(reverse('note_update', kwargs={'id': self.note_for_user1.id}),
                                      content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_delete_note_after_login(self):
        self.client.post(reverse('login'), data=json.dumps(self.user1_credentials), content_type='json')
        response = self.client.delete(reverse('note_update', kwargs={'id': self.note_for_user1.id}),
                                      content_type='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_note_with_id_of_other_user_after_login(self):
        self.client.post(reverse('login'), data=json.dumps(self.user1_credentials), content_type='application/json')
        response = self.client.delete(reverse('note_update', kwargs={'id': self.note_for_user2.id}),
                                      content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    ### Test cases for list and create label

    def test_get_all_labels_if_login_with_invalid_credentials(self):
        self.client.post(reverse('login'), data=json.dumps(self.invalid_credentials), content_type='application/json')
        response = self.client.get(reverse('create_label'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_get_all_labels_after_login(self):
        self.client.post(reverse('login'), data=json.dumps(self.user1_credentials), content_type='application/json')
        labels = Label.objects.filter(user=self.user1)
        serializer = LabelSerializer(labels, many=True)
        response = self.client.get(reverse('create_label'))
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_labels_without_login(self):
        labels = Label.objects.filter(user=self.user1)
        response = self.client.get(reverse('create_label'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_get_all_labels_of_other_user_after_login(self):
        self.client.post(reverse('login'), data=json.dumps(self.user1_credentials), content_type='application/json')
        labels = Label.objects.filter(user=self.user2)
        serializer = LabelSerializer(labels, many=True)
        response = self.client.get(reverse('create_label'))
        self.assertNotEqual(response.data, serializer.data)

    def test_create_label_with_valid_payload_without_login(self):
        response = self.client.post(reverse('create_label'), data=json.dumps(self.valid_label_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_create_label_with_valid_label_payload_after_login(self):
        self.client.post(reverse('login'), data=json.dumps(self.user1_credentials), content_type='application/json')
        response = self.client.post(reverse('create_label'), data=json.dumps(self.valid_label_payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_label_with_invalid_label_payload_after_login(self):
        self.client.post(reverse('login'), data=json.dumps(self.user1_credentials), content_type='json')
        response = self.client.post(reverse('create_label'), data=json.dumps(self.invalid_label_payload),
                                    content_type='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    ### Test Cases for Retriew, Update and Delete

    def test_get_labels_by_id_without_login(self):
        response = self.client.get(reverse('label_update', kwargs={'id': self.label_for_user1.id}))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_get_labels_by_id_after_login(self):
        self.client.post(reverse('login'), data=json.dumps(self.user1_credentials), content_type='json')
        labels = Label.objects.get(id=self.label_for_user1.id)
        serializer = LabelSerializer(labels)
        response = self.client.get(reverse('label_update', kwargs={'id': self.label_for_user1.id}))
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_label_with_valid_payload_without_login(self):
        response = self.client.put(reverse('label_update', kwargs={'id': self.label_for_user1.id}),
                                   data=json.dumps(self.valid_label_payload), content_type='json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_update_label_with_valid_payload_after_login(self):
        self.client.post(reverse('login'), data=json.dumps(self.user1_credentials), content_type='json')
        response = self.client.put(reverse('label_update', kwargs={'id': self.label_for_user1.id}),
                                   data=json.dumps(self.valid_label_payload), content_type='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


#TODO write test cases for 404