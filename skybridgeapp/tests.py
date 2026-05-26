from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse


class AirportDomainModelMetadataTests(SimpleTestCase):
    def test_airport_and_airline_models_have_core_fields(self):
        from .models import Aeroporto, CompanhiaAerea

        self.assertEqual(Aeroporto._meta.get_field('codigo_iata').max_length, 3)
        self.assertTrue(Aeroporto._meta.get_field('codigo_iata').unique)
        self.assertTrue(Aeroporto._meta.get_field('estado').blank)
        self.assertEqual(str(Aeroporto(codigo_iata='GRU', nome='Guarulhos', cidade='Sao Paulo', pais='Brasil')), 'GRU - Guarulhos')

        self.assertEqual(CompanhiaAerea._meta.get_field('codigo_iata').max_length, 3)
        self.assertTrue(CompanhiaAerea._meta.get_field('codigo_iata').unique)
        self.assertEqual(str(CompanhiaAerea(nome='Sky Bridge Air', codigo_iata='SBA', pais='Brasil')), 'Sky Bridge Air (SBA)')

    def test_commercial_models_have_simple_choices_and_relations(self):
        from .models import Pagamento, Promocao, Tarifa

        self.assertEqual(Tarifa._meta.get_field('voo').remote_field.model.__name__, 'Voo')
        self.assertIn(('economy', 'Economy'), Tarifa.CLASSES)
        self.assertIn(('executiva', 'Executiva'), Tarifa.CLASSES)

        self.assertEqual(Promocao._meta.get_field('origem').remote_field.model.__name__, 'Aeroporto')
        self.assertTrue(Promocao._meta.get_field('descricao').blank)
        self.assertTrue(Promocao._meta.get_field('origem').null)
        self.assertTrue(Promocao._meta.get_field('destino').null)

        self.assertEqual(Pagamento._meta.get_field('reserva').remote_field.model.__name__, 'Reserva')
        self.assertIn(('pix', 'Pix'), Pagamento.METODOS)
        self.assertIn(('aprovado', 'Aprovado'), Pagamento.STATUS)

    def test_mileage_models_have_account_and_transaction_fields(self):
        from .models import ContaMilhas, TransacaoMilhas

        self.assertEqual(ContaMilhas._meta.get_field('passageiro').remote_field.model.__name__, 'Passageiro')
        self.assertEqual(ContaMilhas._meta.get_field('saldo').default, 0)
        self.assertTrue(ContaMilhas._meta.get_field('numero_programa').unique)

        self.assertEqual(TransacaoMilhas._meta.get_field('conta').remote_field.model.__name__, 'ContaMilhas')
        self.assertIn(('acumulo', 'Acumulo'), TransacaoMilhas.TIPOS)
        self.assertIn(('resgate', 'Resgate'), TransacaoMilhas.TIPOS)


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
