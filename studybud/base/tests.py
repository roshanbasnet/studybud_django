from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from base.forms import UserForm

class UpdateUserViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.url = reverse('update-user')
        self.image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")

    def test_update_user_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/update-user.html')
        self.assertIsInstance(response.context['form'], UserForm)

    def test_update_user_view_post_valid(self):
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'profile_picture': self.image,
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('user-profile', kwargs={'pk': self.user.id}))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.email, 'testuser@example.com')
        self.assertIsNotNone(self.user.profile_picture)

    def test_update_user_view_post_invalid(self):
        data = {
            'first_name': '',
            'last_name': '',
            'email': 'invalidemail',
            'profile_picture': self.image,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/update-user.html')
        self.assertIsInstance(response.context['form'], UserForm)
        self.assertContains(response, 'This field is required.')
        self.assertContains(response, 'Enter a valid email address.')