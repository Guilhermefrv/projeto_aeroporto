from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(ALLOWED_HOSTS=['testserver'])
class AuthFlowTests(TestCase):
    def test_home_page_renders_with_login_link(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'href="{reverse("auth_home")}"')

    def test_auth_home_links_to_login_and_registration(self):
        response = self.client.get(reverse('auth_home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'href="{reverse("login")}"')
        self.assertContains(response, f'href="{reverse("cadastro")}"')

    def test_cadastro_page_renders(self):
        response = self.client.get(reverse('cadastro'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Criar Conta')
        self.assertContains(response, 'name="tipo"')
        self.assertContains(response, 'name="nome"')
        self.assertContains(response, 'name="email"')

    def test_login_page_renders(self):
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')

    def test_logout_redirects_to_home(self):
        response = self.client.post(reverse('logout'))

        self.assertRedirects(response, reverse('home'))

    def test_dashboard_redirects_anonymous_user_to_login(self):
        response = self.client.get(reverse('dashboard'))

        expected_url = f"{reverse('login')}?next={reverse('dashboard')}"
        self.assertRedirects(response, expected_url)

    def test_authenticated_user_can_access_dashboard(self):
        user = get_user_model().objects.create_user(
            username='usuario_teste',
            password='senha-segura-123',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'usuario_teste')
