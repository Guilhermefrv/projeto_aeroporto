from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from .models import Funcionario, Passageiro


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
    def criar_usuario_passageiro(self):
        user = get_user_model().objects.create_user(
            username='usuario_teste',
            password='senha-segura-123',
            first_name='Usuario',
            last_name='Teste',
            tipo='passageiro',
        )
        Passageiro.objects.create(
            usuario=user,
            nome='Usuario Teste',
            cpf_passaporte='TST123456',
            data_nascimento='1990-01-01',
            contato='(11) 90000-0000',
            nacionalidade='Brasileira',
        )
        return user

    def test_home_page_renders_with_login_link(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'href="{reverse("auth_home")}"')
        self.assertContains(response, 'Fazer login')

    def test_home_login_link_shows_full_name_for_authenticated_user(self):
        user = get_user_model().objects.create_user(
            username='guilherme',
            password='senha-segura-123',
            first_name='Guilherme',
            last_name='Silva',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Guilherme Silva')
        self.assertNotContains(response, 'Fazer login')

    def test_home_login_link_falls_back_to_username_for_authenticated_user(self):
        user = get_user_model().objects.create_user(
            username='guilherme',
            password='senha-segura-123',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'guilherme')
        self.assertNotContains(response, 'Fazer login')

    def test_auth_home_links_to_login_and_registration(self):
        response = self.client.get(reverse('auth_home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'href="{reverse("login")}"')
        self.assertContains(response, f'href="{reverse("cadastro")}"')

    def test_cadastro_page_renders(self):
        response = self.client.get(reverse('cadastro'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Criar Conta')
        self.assertContains(response, 'data-bs-toggle="modal"')
        self.assertContains(response, 'data-bs-target="#modalPassageiro"')
        self.assertContains(response, 'data-bs-target="#modalFuncionario"')
        self.assertContains(response, 'data-bs-target="#modalAdministrador"')
        self.assertContains(response, 'class="modal fade"')
        self.assertContains(response, 'name="tipo_usuario" value="passageiro"')
        self.assertContains(response, 'name="tipo_usuario" value="funcionario"')
        self.assertContains(response, 'name="tipo_usuario" value="administrador"')
        self.assertContains(response, 'class="btn btn-outline-secondary modal-cancel-btn"')
        self.assertContains(response, 'data-bs-dismiss="modal"')
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="nome"')
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'name="cpf_passaporte"')
        self.assertContains(response, '<select id="id_passageiro_nacionalidade"', html=False)
        self.assertContains(response, 'Selecione sua nacionalidade')
        self.assertContains(response, 'value="Italiana"')
        self.assertContains(response, 'name="cargo"')
        self.assertContains(response, 'name="matricula"')
        self.assertContains(response, 'name="password1"')
        self.assertContains(response, 'name="password2"')

    def test_login_page_renders(self):
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')

    def test_login_page_preserves_next_parameter(self):
        response = self.client.get(f'{reverse("login")}?next={reverse("dashboard")}')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'name="next" value="{reverse("dashboard")}"')

    def test_valid_user_can_login_and_redirect_to_dashboard(self):
        self.criar_usuario_passageiro()

        response = self.client.post(reverse('login'), {
            'username': 'usuario_teste',
            'password': 'senha-segura-123',
        })

        self.assertRedirects(response, reverse('dashboard'))
        self.assertIn('_auth_user_id', self.client.session)

    def test_valid_user_can_login_with_next_redirect(self):
        self.criar_usuario_passageiro()

        response = self.client.post(reverse('login'), {
            'username': 'usuario_teste',
            'password': 'senha-segura-123',
            'next': reverse('dashboard'),
        })

        self.assertRedirects(response, reverse('dashboard'))
        self.assertIn('_auth_user_id', self.client.session)

    def test_invalid_user_cannot_login(self):
        self.criar_usuario_passageiro()

        response = self.client.post(reverse('login'), {
            'username': 'usuario_teste',
            'password': 'senha-incorreta',
        })

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertTrue(response.context['form'].non_field_errors())

    def test_logout_redirects_to_home(self):
        response = self.client.post(reverse('logout'))

        self.assertRedirects(response, reverse('home'))

    def test_authenticated_user_can_logout_to_home(self):
        user = self.criar_usuario_passageiro()
        self.client.force_login(user)

        response = self.client.post(reverse('logout'))

        self.assertRedirects(response, reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_dashboard_redirects_anonymous_user_to_login(self):
        response = self.client.get(reverse('dashboard'))

        expected_url = f"{reverse('login')}?next={reverse('dashboard')}"
        self.assertRedirects(response, expected_url)

    def test_authenticated_user_can_access_dashboard(self):
        user = self.criar_usuario_passageiro()
        self.client.force_login(user)

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'usuario_teste')
        self.assertContains(response, 'Passageiro')
        self.assertContains(response, 'Nome do passageiro')
        self.assertContains(response, 'Usuario Teste')


@override_settings(ALLOWED_HOSTS=['testserver'])
class CadastroUsuarioTests(TestCase):
    def setUp(self):
        self.cadastro_url = reverse('cadastro')
        self.login_url = reverse('login')
        self.form_data = self.dados_passageiro()

    def dados_passageiro(self):
        return {
            'tipo_usuario': 'passageiro',
            'username': 'maria.silva',
            'nome': 'Maria Silva',
            'email': 'maria@example.com',
            'cpf_passaporte': '12345678900',
            'data_nascimento': '1995-05-12',
            'contato': '(11) 99999-0000',
            'nacionalidade': 'Brasileira',
            'password1': 'SenhaForte123',
            'password2': 'SenhaForte123',
        }

    def dados_funcionario(self):
        return {
            'tipo_usuario': 'funcionario',
            'username': 'joao.funcionario',
            'nome': 'Joao Funcionario',
            'email': 'joao.funcionario@example.com',
            'contato': '(11) 98888-0000',
            'cargo': 'atendente',
            'matricula': 'MAT123',
            'password1': 'SenhaForte123',
            'password2': 'SenhaForte123',
        }

    def dados_administrador(self):
        return {
            'tipo_usuario': 'administrador',
            'username': 'ana.admin',
            'nome': 'Ana Admin',
            'email': 'ana.admin@example.com',
            'password1': 'SenhaForte123',
            'password2': 'SenhaForte123',
        }

    def test_cadastro_cria_usuario_passageiro(self):
        response = self.client.post(self.cadastro_url, self.form_data)

        self.assertRedirects(response, self.login_url)

        usuario = get_user_model().objects.get(username='maria.silva')
        self.assertEqual(usuario.tipo, 'passageiro')
        self.assertEqual(usuario.email, 'maria@example.com')
        self.assertEqual(usuario.first_name, 'Maria Silva')

    def test_cadastro_cria_perfil_passageiro_vinculado(self):
        data = self.form_data.copy()
        data['nacionalidade'] = 'Italiana'

        self.client.post(self.cadastro_url, data)

        usuario = get_user_model().objects.get(username='maria.silva')
        passageiro = Passageiro.objects.get(usuario=usuario)

        self.assertEqual(passageiro.nome, 'Maria Silva')
        self.assertEqual(passageiro.cpf_passaporte, '12345678900')
        self.assertEqual(passageiro.contato, '(11) 99999-0000')
        self.assertEqual(passageiro.nacionalidade, 'Italiana')

    def test_cadastro_cria_usuario_funcionario(self):
        response = self.client.post(self.cadastro_url, self.dados_funcionario())

        self.assertRedirects(response, self.login_url)

        usuario = get_user_model().objects.get(username='joao.funcionario')
        self.assertEqual(usuario.tipo, 'funcionario')
        self.assertEqual(usuario.email, 'joao.funcionario@example.com')
        self.assertEqual(usuario.first_name, 'Joao Funcionario')

    def test_cadastro_cria_perfil_funcionario_vinculado(self):
        self.client.post(self.cadastro_url, self.dados_funcionario())

        usuario = get_user_model().objects.get(username='joao.funcionario')
        funcionario = Funcionario.objects.get(usuario=usuario)

        self.assertEqual(funcionario.nome, 'Joao Funcionario')
        self.assertEqual(funcionario.cargo, 'atendente')
        self.assertEqual(funcionario.matricula, 'MAT123')
        self.assertEqual(funcionario.contato, '(11) 98888-0000')

    def test_cadastro_cria_usuario_administrador_sem_model_legado(self):
        response = self.client.post(self.cadastro_url, self.dados_administrador())

        self.assertRedirects(response, self.login_url)

        usuario = get_user_model().objects.get(username='ana.admin')
        self.assertEqual(usuario.tipo, 'administrador')
        self.assertTrue(usuario.is_staff)
        self.assertFalse(usuario.is_superuser)
        self.assertFalse(Passageiro.objects.filter(usuario=usuario).exists())
        self.assertFalse(Funcionario.objects.filter(usuario=usuario).exists())

    def test_cadastro_passageiro_nao_exige_cargo_ou_matricula(self):
        data = self.dados_passageiro()
        data.pop('cargo', None)
        data.pop('matricula', None)

        response = self.client.post(self.cadastro_url, data)

        self.assertRedirects(response, self.login_url)

    def test_cadastro_funcionario_exige_cargo_e_matricula(self):
        data = self.dados_funcionario()
        data.pop('cargo')
        data.pop('matricula')

        response = self.client.post(self.cadastro_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['modal_aberto'], 'funcionario')
        self.assertFalse(get_user_model().objects.filter(username='joao.funcionario').exists())
        self.assertTrue(response.context['funcionario_form'].errors['cargo'])
        self.assertTrue(response.context['funcionario_form'].errors['matricula'])

    def test_cadastro_administrador_nao_exige_campos_de_perfis(self):
        data = self.dados_administrador()

        response = self.client.post(self.cadastro_url, data)

        self.assertRedirects(response, self.login_url)

    def test_cadastro_nao_salva_senha_em_texto_puro(self):
        self.client.post(self.cadastro_url, self.form_data)

        usuario = get_user_model().objects.get(username='maria.silva')

        self.assertNotEqual(usuario.password, 'SenhaForte123')
        self.assertTrue(usuario.check_password('SenhaForte123'))

    def test_usuario_cadastrado_consegue_fazer_login(self):
        self.client.post(self.cadastro_url, self.dados_funcionario())

        response = self.client.post(reverse('login'), {
            'username': 'joao.funcionario',
            'password': 'SenhaForte123',
        })

        self.assertRedirects(response, reverse('dashboard'))
