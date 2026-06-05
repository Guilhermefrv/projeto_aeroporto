from datetime import date, timedelta
from decimal import Decimal
from io import StringIO
from urllib.parse import quote, unquote

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils import timezone

from .models import Aeroporto, Aeronave, Bagagem, Bilhete, CheckIn, ContaMilhas, Funcionario, Notificacao, Pagamento, Passageiro, PortaoEmbarque, Reserva, Tarifa, Voo


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
        from .models import Pagamento, Promocao, Reserva, Tarifa

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
        self.assertIn(('pendente', 'Pendente'), Reserva.STATUS)
        self.assertEqual(Reserva._meta.get_field('quantidade_passageiros').default, 1)

    def test_mileage_models_have_account_and_transaction_fields(self):
        from .models import ContaMilhas, TransacaoMilhas

        self.assertEqual(ContaMilhas._meta.get_field('passageiro').remote_field.model.__name__, 'Passageiro')
        self.assertEqual(ContaMilhas._meta.get_field('saldo').default, 0)
        self.assertTrue(ContaMilhas._meta.get_field('numero_programa').unique)

        self.assertEqual(TransacaoMilhas._meta.get_field('conta').remote_field.model.__name__, 'ContaMilhas')
        self.assertIn(('acumulo', 'Acumulo'), TransacaoMilhas.TIPOS)
        self.assertIn(('resgate', 'Resgate'), TransacaoMilhas.TIPOS)


class PopularBancoCommandTests(TestCase):
    def test_popular_banco_command_popula_dados_iniciais(self):
        output = StringIO()

        call_command('popular_banco', stdout=output)

        self.assertTrue(Aeroporto.objects.filter(codigo_iata='GRU').exists())
        self.assertTrue(Aeroporto.objects.filter(codigo_iata='GIG').exists())
        self.assertTrue(Aeroporto.objects.filter(codigo_iata='SSA').exists())
        self.assertTrue(Aeroporto.objects.filter(codigo_iata='CWB').exists())
        self.assertTrue(Aeroporto.objects.filter(codigo_iata='BEL').exists())
        self.assertTrue(Aeroporto.objects.filter(codigo_iata='CGB').exists())
        self.assertTrue(Voo.objects.filter(numero_voo__startswith='SB').exists())
        self.assertTrue(Voo.objects.filter(origem__icontains='POA', destino__icontains='GRU', status='programado').exists())
        self.assertTrue(Voo.objects.filter(origem__icontains='CWB', destino__icontains='GRU', status='programado').exists())
        self.assertTrue(
            Voo.objects.filter(
                numero_voo__startswith='SB',
                partida__date=date(timezone.localdate().year, 12, 31),
            ).exists()
        )

        total_voos = Voo.objects.filter(numero_voo__startswith='SB').count()
        total_voos_com_tarifa = Voo.objects.filter(
            numero_voo__startswith='SB',
            tarifas__ativa=True,
        ).distinct().count()
        self.assertEqual(total_voos, total_voos_com_tarifa)
        self.assertEqual(get_user_model().objects.count(), 0)
        self.assertIn('Banco populado com sucesso', output.getvalue())

    def test_popular_banco_command_e_idempotente_e_limpa_dados_de_exemplo(self):
        call_command('popular_banco')
        total_voos = Voo.objects.filter(numero_voo__startswith='SB').count()
        total_tarifas = Tarifa.objects.filter(voo__numero_voo__startswith='SB').count()

        call_command('popular_banco')

        self.assertEqual(Voo.objects.filter(numero_voo__startswith='SB').count(), total_voos)
        self.assertEqual(Tarifa.objects.filter(voo__numero_voo__startswith='SB').count(), total_tarifas)

        call_command('popular_banco', '--limpar')

        self.assertFalse(Voo.objects.filter(numero_voo__startswith='SB').exists())
        self.assertFalse(Tarifa.objects.filter(voo__numero_voo__startswith='SB').exists())

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

    def criar_usuario_funcionario(self):
        user = get_user_model().objects.create_user(
            username='funcionario_teste',
            password='senha-segura-123',
            first_name='Funcionario',
            last_name='Teste',
            tipo='funcionario',
        )
        Funcionario.objects.create(
            usuario=user,
            nome='Funcionario Teste',
            cargo='atendente',
            matricula='MAT999',
            contato='(11) 91111-0000',
        )
        return user

    def criar_usuario_administrador(self):
        return get_user_model().objects.create_user(
            username='admin_teste',
            password='senha-segura-123',
            first_name='Admin',
            last_name='Teste',
            tipo='administrador',
            is_staff=True,
        )

    def criar_voo_admin(self, numero_voo='SBADM1'):
        aeronave = Aeronave.objects.create(
            modelo=f'Airbus {numero_voo}',
            capacidade=180,
            companhia_aerea='Sky Bridge Air',
        )
        portao = PortaoEmbarque.objects.create(
            numero_portao=f'A{numero_voo[-1]}',
            localizacao='Terminal Admin',
            status='livre',
        )
        partida = timezone.now() + timedelta(days=3)
        return Voo.objects.create(
            numero_voo=numero_voo,
            origem='GRU - Sao Paulo',
            destino='REC - Recife',
            partida=partida,
            chegada=partida + timedelta(hours=3),
            status='programado',
            aeronave=aeronave,
            portao=portao,
        )

    def criar_reserva_admin(self, passageiro, voo, assento='1A', status='confirmada'):
        return Reserva.objects.create(
            passageiro=passageiro,
            voo=voo,
            classe_tarifa='economy',
            quantidade_passageiros=1,
            assento=assento,
            status=status,
        )

    def test_home_page_renders_with_login_link(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'href="{reverse("auth_home")}"')
        self.assertContains(response, 'Fazer login')
        self.assertContains(response, 'bootstrap@5.3.3/dist/css/bootstrap.min.css')
        self.assertContains(response, 'bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js')
        self.assertContains(response, '/static/js/main.js')
        self.assertNotContains(response, 'class="dropdown account-menu"')

    def test_home_uses_only_brazilian_flight_scope(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Destinos selecionados pelo Brasil')
        self.assertContains(response, 'GRU - São Paulo')
        self.assertContains(response, 'CWB')
        self.assertContains(response, 'REC')
        self.assertContains(response, 'MAO')
        self.assertContains(response, 'BSB')
        self.assertContains(response, 'São Paulo → Manaus')
        self.assertContains(response, 'São Paulo → Curitiba')
        self.assertContains(response, 'São Paulo → Brasília')
        self.assertNotContains(response, 'Internacionais')
        self.assertNotContains(response, 'Buenos Aires')
        self.assertNotContains(response, 'Santiago')
        self.assertNotContains(response, 'Lisboa')

    def test_home_account_menu_greets_authenticated_user_by_first_name(self):
        user = get_user_model().objects.create_user(
            username='guilherme',
            password='senha-segura-123',
            first_name='Guilherme',
            last_name='Silva',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="dropdown account-menu"')
        self.assertContains(response, 'data-bs-toggle="dropdown"')
        self.assertContains(response, 'class="dropdown-menu dropdown-menu-end account-dropdown"')
        self.assertContains(response, 'class="dropdown-item account-dropdown-item"')
        self.assertContains(response, 'class="account-avatar"')
        self.assertContains(response, 'GS')
        self.assertContains(response, 'Olá, Guilherme')
        self.assertContains(response, 'Minha conta')
        self.assertContains(response, 'Notificações')
        self.assertContains(response, 'action="{0}"'.format(reverse('logout')))
        self.assertContains(response, f'href="{reverse("dashboard_passageiro")}"')
        self.assertContains(response, f'href="{reverse("minhas_viagens")}"')
        self.assertContains(response, f'href="{reverse("notificacoes_passageiro")}"')
        self.assertContains(response, f'href="{reverse("password_change")}"')
        self.assertContains(response, 'Alterar senha')
        self.assertNotContains(response, 'Fazer login')

        html = response.content.decode()
        self.assertRegex(html, rf'href="{reverse("dashboard_passageiro")}"[\s\S]*?Minha conta')
        self.assertRegex(html, rf'href="{reverse("minhas_viagens")}"[\s\S]*?Minhas viagens')
        self.assertRegex(html, rf'href="{reverse("notificacoes_passageiro")}"[\s\S]*?Notifica')

    def test_home_account_menu_falls_back_to_generic_label(self):
        user = get_user_model().objects.create_user(
            username='guilherme',
            password='senha-segura-123',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Minha conta')
        self.assertContains(response, f'href="{reverse("dashboard_passageiro")}"')
        self.assertNotContains(response, 'Fazer login')

    def test_home_account_link_points_to_employee_dashboard(self):
        user = self.criar_usuario_funcionario()
        self.client.force_login(user)

        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Olá, Funcionario')
        self.assertContains(response, f'href="{reverse("dashboard_funcionario")}"')
        self.assertNotContains(response, 'Fazer login')

    def test_home_account_link_points_to_admin_dashboard(self):
        user = self.criar_usuario_administrador()
        self.client.force_login(user)

        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Olá, Admin')
        self.assertContains(response, f'href="{reverse("dashboard_administrador")}"')
        self.assertNotContains(response, 'Fazer login')

    def test_auth_home_links_to_login_and_registration(self):
        response = self.client.get(reverse('auth_home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'href="{reverse("login")}"')
        self.assertContains(response, f'href="{reverse("cadastro")}"')

    def test_auth_home_redirects_authenticated_passenger_to_home(self):
        user = self.criar_usuario_passageiro()
        self.client.force_login(user)

        response = self.client.get(reverse('auth_home'))

        self.assertRedirects(response, reverse('home'))

    def test_auth_home_redirects_authenticated_employee_to_dashboard(self):
        user = self.criar_usuario_funcionario()
        self.client.force_login(user)

        response = self.client.get(reverse('auth_home'))

        self.assertRedirects(response, reverse('dashboard_funcionario'))

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
        self.assertContains(response, f'href="{reverse("cadastro")}"')
        self.assertContains(response, 'Nao tem uma conta?')
        self.assertContains(response, f'href="{reverse("password_reset")}"')
        self.assertContains(response, 'Esqueceu a senha?')
        self.assertNotContains(response, 'data-noop')

    def test_login_page_preserves_next_parameter(self):
        response = self.client.get(f'{reverse("login")}?next={reverse("dashboard")}')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'name="next" value="{reverse("dashboard")}"')
        self.assertContains(response, f'href="{reverse("cadastro")}?next={quote(reverse("dashboard"), safe="/")}"')

    def test_password_reset_page_renders(self):
        response = self.client.get(reverse('password_reset'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'Enviar instrucoes')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_password_reset_sends_email_for_existing_user(self):
        user = self.criar_usuario_passageiro()
        user.email = 'usuario@example.com'
        user.save(update_fields=['email'])

        response = self.client.post(reverse('password_reset'), {'email': user.email})

        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Sky Bridge', mail.outbox[0].subject)
        self.assertIn('/senha/redefinir/', mail.outbox[0].body)

    def test_password_reset_confirm_changes_password(self):
        user = self.criar_usuario_passageiro()
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        response = self.client.get(reverse('password_reset_confirm', args=[uidb64, token]))
        reset_url = response['Location']

        response = self.client.post(reset_url, {
            'new_password1': 'NovaSenhaForte123',
            'new_password2': 'NovaSenhaForte123',
        })

        user.refresh_from_db()
        self.assertRedirects(response, reverse('password_reset_complete'))
        self.assertTrue(user.check_password('NovaSenhaForte123'))

    def test_authenticated_user_can_change_password(self):
        user = self.criar_usuario_passageiro()
        self.client.force_login(user)

        response = self.client.post(reverse('password_change'), {
            'old_password': 'senha-segura-123',
            'new_password1': 'SenhaAlterada123',
            'new_password2': 'SenhaAlterada123',
        })

        user.refresh_from_db()
        self.assertRedirects(response, reverse('password_change_done'))
        self.assertTrue(user.check_password('SenhaAlterada123'))

    def test_anonymous_password_change_redirects_to_login(self):
        response = self.client.get(reverse('password_change'))

        self.assertRedirects(response, f'{reverse("login")}?next={reverse("password_change")}')

    def test_passenger_login_redirects_to_home(self):
        self.criar_usuario_passageiro()

        response = self.client.post(reverse('login'), {
            'username': 'usuario_teste',
            'password': 'senha-segura-123',
        })

        self.assertRedirects(response, reverse('home'))
        self.assertIn('_auth_user_id', self.client.session)

    def test_passenger_login_shows_success_message_on_home(self):
        self.criar_usuario_passageiro()

        response = self.client.post(reverse('login'), {
            'username': 'usuario_teste',
            'password': 'senha-segura-123',
        }, follow=True)

        self.assertContains(response, 'class="toast-container position-fixed top-0 end-0 p-3 sky-toast-container"')
        self.assertContains(response, 'class="toast sky-toast success"')
        self.assertContains(response, 'data-bs-delay="4200"')
        self.assertContains(response, 'Login realizado com sucesso.')

    def test_employee_login_redirects_to_employee_dashboard(self):
        self.criar_usuario_funcionario()

        response = self.client.post(reverse('login'), {
            'username': 'funcionario_teste',
            'password': 'senha-segura-123',
        })

        self.assertRedirects(response, reverse('dashboard_funcionario'))
        self.assertIn('_auth_user_id', self.client.session)

    def test_admin_login_redirects_to_admin_dashboard(self):
        self.criar_usuario_administrador()

        response = self.client.post(reverse('login'), {
            'username': 'admin_teste',
            'password': 'senha-segura-123',
        })

        self.assertRedirects(response, reverse('dashboard_administrador'))
        self.assertIn('_auth_user_id', self.client.session)

    def test_valid_user_can_login_with_next_redirect(self):
        self.criar_usuario_passageiro()

        response = self.client.post(reverse('login'), {
            'username': 'usuario_teste',
            'password': 'senha-segura-123',
            'next': reverse('dashboard'),
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('dashboard'))
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

    def test_logout_shows_success_message_on_home(self):
        user = self.criar_usuario_passageiro()
        self.client.force_login(user)

        response = self.client.post(reverse('logout'), follow=True)

        self.assertContains(response, 'class="toast-container position-fixed top-0 end-0 p-3 sky-toast-container"')
        self.assertContains(response, 'class="toast sky-toast success"')
        self.assertContains(response, 'Logout realizado com sucesso.')
        self.assertContains(response, 'Fazer login')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_dashboard_redirects_anonymous_user_to_login(self):
        response = self.client.get(reverse('dashboard'))

        expected_url = f"{reverse('login')}?next={reverse('dashboard')}"
        self.assertRedirects(response, expected_url)

    def test_specific_dashboards_redirect_anonymous_user_to_login(self):
        for dashboard_name in ['dashboard_passageiro', 'dashboard_funcionario', 'dashboard_administrador']:
            with self.subTest(dashboard_name=dashboard_name):
                response = self.client.get(reverse(dashboard_name))
                expected_url = f"{reverse('login')}?next={reverse(dashboard_name)}"
                self.assertRedirects(response, expected_url)

    def test_dashboard_router_sends_passenger_to_passenger_panel(self):
        user = self.criar_usuario_passageiro()
        self.client.force_login(user)

        response = self.client.get(reverse('dashboard'))

        self.assertRedirects(response, reverse('dashboard_passageiro'))

    def test_passenger_can_access_passenger_dashboard(self):
        user = self.criar_usuario_passageiro()
        self.client.force_login(user)

        response = self.client.get(reverse('dashboard_passageiro'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Passageiro')
        self.assertContains(response, 'Nome Completo')
        self.assertContains(response, 'Usuario Teste')

    def test_passenger_cannot_access_employee_dashboard(self):
        user = self.criar_usuario_passageiro()
        self.client.force_login(user)

        response = self.client.get(reverse('dashboard_funcionario'))

        self.assertRedirects(response, reverse('dashboard_passageiro'))

    def test_employee_cannot_access_admin_dashboard(self):
        user = self.criar_usuario_funcionario()
        self.client.force_login(user)

        response = self.client.get(reverse('dashboard_administrador'))

        self.assertRedirects(response, reverse('dashboard_funcionario'))

    def test_admin_dashboard_shows_indicators_and_approved_revenue(self):
        admin_user = self.criar_usuario_administrador()
        passenger_user = self.criar_usuario_passageiro()
        passageiro = Passageiro.objects.get(usuario=passenger_user)
        voo_um = self.criar_voo_admin('SBAD1')
        voo_dois = self.criar_voo_admin('SBAD2')
        reserva_aprovada = self.criar_reserva_admin(passageiro, voo_um, assento='1A')
        reserva_pendente = self.criar_reserva_admin(passageiro, voo_dois, assento='1B', status='pendente')
        Pagamento.objects.create(
            reserva=reserva_aprovada,
            valor_total=Decimal('500.50'),
            metodo='pix',
            status='aprovado',
            data_pagamento=timezone.now(),
        )
        Pagamento.objects.create(
            reserva=reserva_pendente,
            valor_total=Decimal('199.90'),
            metodo='boleto',
            status='pendente',
        )
        self.client.force_login(admin_user)

        response = self.client.get(reverse('dashboard_administrador'))

        self.assertEqual(response.status_code, 200)
        stats = response.context['stats']
        self.assertEqual(stats['total_voos'], 2)
        self.assertEqual(stats['total_reservas'], 2)
        self.assertEqual(stats['total_passageiros'], 1)
        self.assertEqual(stats['total_pagamentos'], 2)
        self.assertEqual(stats['pagamentos_aprovados'], 1)
        self.assertEqual(stats['receita_aprovada'], Decimal('500.50'))
        self.assertContains(response, 'Receita aprovada')
        self.assertContains(response, 'R$ 500,50')
        self.assertContains(response, 'Pagamentos')

    def test_admin_dashboard_lists_latest_reservations(self):
        admin_user = self.criar_usuario_administrador()
        passenger_user = self.criar_usuario_passageiro()
        passageiro = Passageiro.objects.get(usuario=passenger_user)
        voo = self.criar_voo_admin('SBAD3')
        reservas = [
            self.criar_reserva_admin(passageiro, voo, assento=f'{index}A')
            for index in range(1, 7)
        ]
        self.client.force_login(admin_user)

        response = self.client.get(reverse('dashboard_administrador'))

        ultimas_ids = [reserva.id for reserva in response.context['ultimas_reservas']]
        self.assertEqual(ultimas_ids, [reserva.id for reserva in reversed(reservas[-5:])])
        self.assertContains(response, f'Reserva #{reservas[-1].id}')
        self.assertContains(response, passageiro.nome)
        self.assertContains(response, voo.numero_voo)
        self.assertNotContains(response, f'Reserva #{reservas[0].id}')

    def test_admin_dashboard_has_quick_links_to_django_admin_models(self):
        admin_user = self.criar_usuario_administrador()
        self.client.force_login(admin_user)

        response = self.client.get(reverse('dashboard_administrador'))

        self.assertContains(response, 'href="/admin/"')
        self.assertContains(response, 'href="/admin/skybridgeapp/voo/"')
        self.assertContains(response, 'href="/admin/skybridgeapp/reserva/"')
        self.assertContains(response, 'href="/admin/skybridgeapp/passageiro/"')
        self.assertContains(response, 'href="/admin/skybridgeapp/pagamento/"')


@override_settings(ALLOWED_HOSTS=['testserver'])
class BuscaVoosTests(TestCase):
    def setUp(self):
        self.gru = Aeroporto.objects.create(
            codigo_iata='GRU',
            nome='Guarulhos',
            cidade='São Paulo',
            estado='SP',
            pais='Brasil',
        )
        self.rec = Aeroporto.objects.create(
            codigo_iata='REC',
            nome='Guararapes',
            cidade='Recife',
            estado='PE',
            pais='Brasil',
        )
        self.cwb = Aeroporto.objects.create(
            codigo_iata='CWB',
            nome='Afonso Pena',
            cidade='Curitiba',
            estado='PR',
            pais='Brasil',
        )
        self.cnf = Aeroporto.objects.create(
            codigo_iata='CNF',
            nome='Confins',
            cidade='Belo Horizonte',
            estado='MG',
            pais='Brasil',
        )
        self.aeronave = Aeronave.objects.create(
            modelo='Airbus A320',
            capacidade=180,
            companhia_aerea='Sky Bridge Air',
        )
        self.portao = PortaoEmbarque.objects.create(
            numero_portao='A1',
            localizacao='Terminal 1',
            status='livre',
        )
        self.partida_base = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=10)
        self.voo_gru_rec = Voo.objects.create(
            numero_voo='SB123',
            origem='GRU - São Paulo',
            destino='REC - Recife',
            partida=self.partida_base,
            chegada=self.partida_base + timedelta(hours=3),
            status='programado',
            aeronave=self.aeronave,
            portao=self.portao,
        )
        self.voo_gru_cwb = Voo.objects.create(
            numero_voo='SB124',
            origem='GRU - São Paulo',
            destino='CWB - Curitiba',
            partida=self.partida_base + timedelta(days=1),
            chegada=self.partida_base + timedelta(days=1, hours=2),
            status='programado',
            aeronave=self.aeronave,
            portao=self.portao,
        )
        self.voo_rec_gru = Voo.objects.create(
            numero_voo='SB125',
            origem='REC - Recife',
            destino='GRU - São Paulo',
            partida=self.partida_base + timedelta(days=2),
            chegada=self.partida_base + timedelta(days=2, hours=3),
            status='programado',
            aeronave=self.aeronave,
            portao=self.portao,
        )
        self.voo_gru_rec_proximo = Voo.objects.create(
            numero_voo='SB127',
            origem='GRU - São Paulo',
            destino='REC - Recife',
            partida=self.partida_base + timedelta(days=2, hours=5),
            chegada=self.partida_base + timedelta(days=2, hours=8),
            status='programado',
            aeronave=self.aeronave,
            portao=self.portao,
        )
        self.voo_em_andamento = Voo.objects.create(
            numero_voo='SB126',
            origem='GRU - SÃ£o Paulo',
            destino='REC - Recife',
            partida=self.partida_base + timedelta(days=4),
            chegada=self.partida_base + timedelta(days=4, hours=3),
            status='em_andamento',
            aeronave=self.aeronave,
            portao=self.portao,
        )
        self.voo_cancelado = Voo.objects.create(
            numero_voo='SB999',
            origem='GRU - São Paulo',
            destino='REC - Recife',
            partida=self.partida_base + timedelta(days=3),
            chegada=self.partida_base + timedelta(days=3, hours=3),
            status='cancelado',
            aeronave=self.aeronave,
            portao=self.portao,
        )

        Tarifa.objects.create(
            voo=self.voo_gru_rec,
            classe='economy',
            preco_base=Decimal('250.00'),
            taxas=Decimal('20.00'),
            ativa=True,
        )
        Tarifa.objects.create(
            voo=self.voo_gru_rec,
            classe='premium_economy',
            preco_base=Decimal('260.00'),
            taxas=Decimal('25.00'),
            ativa=True,
        )
        Tarifa.objects.create(
            voo=self.voo_gru_rec,
            classe='executiva',
            preco_base=Decimal('10.00'),
            taxas=Decimal('5.00'),
            ativa=False,
        )
        Tarifa.objects.create(
            voo=self.voo_gru_cwb,
            classe='economy',
            preco_base=Decimal('300.00'),
            taxas=Decimal('30.00'),
            ativa=True,
        )
        Tarifa.objects.create(
            voo=self.voo_rec_gru,
            classe='economy',
            preco_base=Decimal('400.00'),
            taxas=Decimal('40.00'),
            ativa=False,
        )
        Tarifa.objects.create(
            voo=self.voo_gru_rec_proximo,
            classe='economy',
            preco_base=Decimal('350.00'),
            taxas=Decimal('35.00'),
            ativa=True,
        )

    def criar_usuario_passageiro_com_perfil(self, username='comprador', cpf_passaporte='COMP123456', nome='Comprador Teste'):
        user = get_user_model().objects.create_user(
            username=username,
            password='senha-segura-123',
            first_name=nome.split()[0],
            tipo='passageiro',
        )
        passageiro = Passageiro.objects.create(
            usuario=user,
            nome=nome,
            cpf_passaporte=cpf_passaporte,
            data_nascimento='1990-01-01',
            contato='(11) 90000-0000',
            nacionalidade='Brasileira',
        )
        return user, passageiro

    def criar_usuario_funcionario_com_perfil(self):
        user = get_user_model().objects.create_user(
            username='operador',
            password='senha-segura-123',
            first_name='Operador',
            tipo='funcionario',
        )
        funcionario = Funcionario.objects.create(
            usuario=user,
            nome='Operador Teste',
            cargo='atendente',
            matricula='OP123',
            contato='(11) 98888-0000',
        )
        return user, funcionario

    def criar_reserva_confirmada_com_bilhete(self, passageiro, codigo='TKT-TESTE-001'):
        reserva = Reserva.objects.create(
            passageiro=passageiro,
            voo=self.voo_gru_rec,
            classe_tarifa='economy',
            quantidade_passageiros=1,
            assento='12A',
            status='confirmada',
        )
        Pagamento.objects.create(
            reserva=reserva,
            valor_total=Decimal('270.00'),
            metodo='pix',
            status='aprovado',
            data_pagamento=timezone.now(),
        )
        bilhete = Bilhete.objects.create(
            reserva=reserva,
            codigo=codigo,
        )
        return reserva, bilhete

    def test_home_renderiza_formulario_de_busca_real(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'action="{reverse("buscar_voos")}"')
        self.assertContains(response, 'method="get"')
        self.assertContains(response, 'id="homeSearchAdvanced"')
        self.assertContains(response, 'data-bs-target="#originAirportModal"')
        self.assertContains(response, 'data-bs-target="#destinationAirportModal"')
        self.assertContains(response, 'data-airport-option')
        self.assertContains(response, '/static/js/main.js?v=')
        self.assertContains(response, 'name="origem"')
        self.assertContains(response, 'name="destino"')
        self.assertContains(response, 'name="data_ida"')
        self.assertContains(response, 'name="data_volta"')
        self.assertContains(response, 'name="passageiros"')
        self.assertContains(response, 'name="classe"')
        self.assertIn('GRU', response.context['route_map'])
        self.assertIn('REC', response.context['route_map']['GRU'])
        self.assertIn('CWB', response.context['route_map']['GRU'])

    def test_rota_busca_retorna_status_200(self):
        response = self.client.get(reverse('buscar_voos'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Buscar voos nacionais')

    def test_busca_sem_filtros_lista_todos_os_voos_ativos(self):
        response = self.client.get(reverse('buscar_voos'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SB123')
        self.assertContains(response, 'SB124')
        self.assertContains(response, 'SB125')
        self.assertContains(response, 'SB127')
        self.assertNotContains(response, 'SB126')
        self.assertNotContains(response, 'SB999')
        self.assertEqual(
            [voo.numero_voo for voo in response.context['voos']],
            ['SB123', 'SB124', 'SB125', 'SB127'],
        )

    def test_busca_filtra_apenas_por_origem(self):
        response = self.client.get(reverse('buscar_voos'), {
            'origem': self.gru.pk,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SB123')
        self.assertContains(response, 'SB124')
        self.assertContains(response, 'SB127')
        self.assertNotContains(response, 'SB125')
        self.assertNotContains(response, 'SB126')
        self.assertNotContains(response, 'SB999')

    def test_busca_filtra_apenas_por_destino(self):
        response = self.client.get(reverse('buscar_voos'), {
            'destino': self.rec.pk,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SB123')
        self.assertContains(response, 'SB127')
        self.assertNotContains(response, 'SB124')
        self.assertNotContains(response, 'SB125')
        self.assertNotContains(response, 'SB126')
        self.assertNotContains(response, 'SB999')

    def test_busca_filtra_origem_e_destino_simultaneamente(self):
        response = self.client.get(reverse('buscar_voos'), {
            'origem': self.gru.pk,
            'destino': self.rec.pk,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SB123')
        self.assertContains(response, 'SB127')
        self.assertNotContains(response, 'SB124')
        self.assertNotContains(response, 'SB125')
        self.assertNotContains(response, 'SB126')
        self.assertNotContains(response, 'SB999')

    def test_busca_filtra_por_data_de_partida(self):
        response = self.client.get(reverse('buscar_voos'), {
            'data_ida': self.partida_base.date().isoformat(),
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SB123')
        self.assertNotContains(response, 'SB124')
        self.assertNotContains(response, 'SB125')
        self.assertNotContains(response, 'SB126')
        self.assertNotContains(response, 'SB999')

    def test_busca_retorna_menor_tarifa_ativa_e_tarifa_indisponivel_quando_necessario(self):
        response_com_tarifa = self.client.get(reverse('buscar_voos'), {
            'origem': self.gru.pk,
            'destino': self.rec.pk,
            'data_ida': self.partida_base.date().isoformat(),
        })

        self.assertEqual(response_com_tarifa.status_code, 200)
        self.assertContains(response_com_tarifa, 'SB123')
        self.assertContains(response_com_tarifa, 'R$ 270,00')
        self.assertNotContains(response_com_tarifa, 'R$ 15,00')

        response_sem_tarifa = self.client.get(reverse('buscar_voos'), {
            'origem': self.rec.pk,
            'destino': self.gru.pk,
            'data_ida': (self.partida_base + timedelta(days=2)).date().isoformat(),
        })

        self.assertEqual(response_sem_tarifa.status_code, 200)
        self.assertContains(response_sem_tarifa, 'SB125')
        self.assertContains(response_sem_tarifa, 'Tarifa indisponível')


    def test_busca_com_todas_as_classes_nao_filtra_por_cabine(self):
        response = self.client.get(reverse('buscar_voos'), {
            'origem': self.gru.pk,
            'classe': '',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SB123')
        self.assertContains(response, 'SB124')
        self.assertContains(response, 'SB127')

    def test_busca_com_classe_especifica_filtra_por_tarifa_ativa(self):
        response = self.client.get(reverse('buscar_voos'), {
            'origem': self.gru.pk,
            'classe': 'premium_economy',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SB123')
        self.assertNotContains(response, 'SB124')

    def test_busca_com_data_inexistente_mostra_mensagem_e_sugestoes(self):
        response = self.client.get(reverse('buscar_voos'), {
            'origem': self.gru.pk,
            'destino': self.rec.pk,
            'data_ida': (self.partida_base + timedelta(days=30)).date().isoformat(),
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nenhum voo encontrado para os filtros informados.')
        self.assertContains(response, 'Rotas disponiveis')

    def test_busca_com_rota_sem_malha_mostra_sugestoes_da_origem(self):
        response = self.client.get(reverse('buscar_voos'), {
            'origem': self.gru.pk,
            'destino': self.cnf.pk,
            'data_ida': (self.partida_base + timedelta(days=30)).date().isoformat(),
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ainda nao temos voos cadastrados para essa rota.')
        self.assertContains(response, 'Rotas disponiveis a partir de GRU')
        self.assertContains(response, 'REC - Recife')

    def test_busca_sem_resultado_exato_mostra_opcoes_proximas(self):
        response = self.client.get(reverse('buscar_voos'), {
            'origem': self.gru.pk,
            'destino': self.rec.pk,
            'data_ida': (self.partida_base + timedelta(days=1)).date().isoformat(),
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nao encontramos voos nessa data')
        self.assertContains(response, 'SB123')
        self.assertContains(response, 'SB127')
        self.assertContains(response, 'Ver opcao')
        self.assertEqual(response.context['resultado_tipo'], 'proximo')

    def test_faixa_de_datas_flexiveis_mostra_menor_preco_e_link(self):
        data_sem_voo = (self.partida_base + timedelta(days=1)).date().isoformat()

        response = self.client.get(reverse('buscar_voos'), {
            'origem': self.gru.pk,
            'destino': self.rec.pk,
            'data_ida': data_sem_voo,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Datas proximas')
        self.assertContains(response, 'R$ 270,00')
        self.assertContains(response, 'R$ 385,00')
        self.assertContains(response, 'Sem voo')
        self.assertContains(response, f'data_ida={self.partida_base.date().isoformat()}')
        self.assertContains(response, f'data_ida={data_sem_voo}')

    def test_resultados_preservam_filtros_get_incluindo_volta(self):
        data_volta = (self.partida_base + timedelta(days=7)).date().isoformat()
        response = self.client.get(reverse('buscar_voos'), {
            'origem': self.gru.pk,
            'destino': self.rec.pk,
            'data_ida': self.partida_base.date().isoformat(),
            'data_volta': data_volta,
            'classe': 'economy',
        })

        form = response.context['search_form']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(form['origem'].value()), str(self.gru.pk))
        self.assertEqual(str(form['destino'].value()), str(self.rec.pk))
        self.assertEqual(form['data_ida'].value(), self.partida_base.date().isoformat())
        self.assertEqual(form['data_volta'].value(), data_volta)
        self.assertEqual(form['classe'].value(), 'economy')

    def test_resultados_linkam_selecionar_voo_com_classe_e_passageiros(self):
        response = self.client.get(reverse('buscar_voos'), {
            'origem': self.gru.pk,
            'destino': self.rec.pk,
            'data_ida': self.partida_base.date().isoformat(),
            'classe': 'premium_economy',
            'passageiros': 3,
        })

        selecionar_url = reverse('selecionar_voo', args=[self.voo_gru_rec.pk])

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'href="{selecionar_url}?classe=premium_economy&passageiros=3"')
        self.assertContains(response, 'Selecionar voo')

    def test_detalhe_voo_real_exibe_resumo_e_menor_tarifa_ativa(self):
        response = self.client.get(reverse('detalhe_voo', args=[self.voo_gru_rec.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Voo SB123')
        self.assertContains(response, 'GRU')
        self.assertContains(response, 'REC - Recife')
        self.assertContains(response, 'R$ 270,00')
        self.assertContains(response, 'Economy')
        self.assertContains(response, 'name="passageiros"')
        self.assertContains(response, 'value="1"')

    def test_detalhe_voo_exibe_tarifa_da_classe_selecionada(self):
        response = self.client.get(reverse('detalhe_voo', args=[self.voo_gru_rec.pk]), {
            'classe': 'premium_economy',
            'passageiros': 3,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'R$ 285,00')
        self.assertContains(response, 'Premium economy')
        self.assertContains(response, 'value="3"')

    def test_detalhe_voo_cai_para_menor_tarifa_quando_classe_nao_tem_tarifa_ativa(self):
        response = self.client.get(reverse('detalhe_voo', args=[self.voo_gru_rec.pk]), {
            'classe': 'executiva',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'R$ 270,00')
        self.assertContains(response, 'Economy')
        self.assertNotContains(response, 'R$ 15,00')

    def test_selecionar_voo_anonimo_redireciona_para_login_com_next(self):
        selecionar_url = reverse('selecionar_voo', args=[self.voo_gru_rec.pk])

        response = self.client.get(f'{selecionar_url}?classe=economy&passageiros=2')

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith(f'{reverse("login")}?next='))
        self.assertIn(selecionar_url, unquote(response['Location']))
        self.assertIn('classe=economy', unquote(response['Location']))
        self.assertIn('passageiros=2', unquote(response['Location']))

    def test_selecionar_voo_logado_redireciona_para_detalhe_com_filtros(self):
        user = get_user_model().objects.create_user(
            username='comprador',
            password='senha-segura-123',
            first_name='Comprador',
            tipo='passageiro',
        )
        Passageiro.objects.create(
            usuario=user,
            nome='Comprador Teste',
            cpf_passaporte='COMP123456',
            data_nascimento='1990-01-01',
            contato='(11) 90000-0000',
            nacionalidade='Brasileira',
        )
        self.client.force_login(user)
        selecionar_url = reverse('selecionar_voo', args=[self.voo_gru_rec.pk])
        detalhe_url = reverse('detalhe_voo', args=[self.voo_gru_rec.pk])

        response = self.client.get(f'{selecionar_url}?classe=economy&passageiros=2')

        self.assertRedirects(response, f'{detalhe_url}?classe=economy&passageiros=2')

    def test_passageiro_logado_cria_reserva_real(self):
        user = get_user_model().objects.create_user(
            username='comprador',
            password='senha-segura-123',
            first_name='Comprador',
            tipo='passageiro',
        )
        passageiro = Passageiro.objects.create(
            usuario=user,
            nome='Comprador Teste',
            cpf_passaporte='COMP123456',
            data_nascimento='1990-01-01',
            contato='(11) 90000-0000',
            nacionalidade='Brasileira',
        )
        self.client.force_login(user)

        response = self.client.post(reverse('criar_reserva', args=[self.voo_gru_rec.pk]), {
            'classe': 'economy',
            'passageiros': 1,
        })

        reserva = Reserva.objects.get()
        self.assertRedirects(response, reverse('pagamento_reserva', args=[reserva.pk]))
        self.assertEqual(reserva.passageiro, passageiro)
        self.assertEqual(reserva.voo, self.voo_gru_rec)
        self.assertEqual(reserva.status, 'pendente')
        self.assertEqual(reserva.classe_tarifa, 'economy')
        self.assertEqual(reserva.quantidade_passageiros, 1)
        self.assertRegex(reserva.assento, r'^[0-9]{1,2}[A-F]$')

    def test_pagina_pagamento_exibe_resumo_e_metodos(self):
        user = get_user_model().objects.create_user(
            username='comprador',
            password='senha-segura-123',
            first_name='Comprador',
            tipo='passageiro',
        )
        passageiro = Passageiro.objects.create(
            usuario=user,
            nome='Comprador Teste',
            cpf_passaporte='COMP123456',
            data_nascimento='1990-01-01',
            contato='(11) 90000-0000',
            nacionalidade='Brasileira',
        )
        reserva = Reserva.objects.create(
            passageiro=passageiro,
            voo=self.voo_gru_rec,
            classe_tarifa='economy',
            quantidade_passageiros=2,
            assento='12A',
            status='pendente',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('pagamento_reserva', args=[reserva.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pix')
        self.assertContains(response, 'Cartão')
        self.assertContains(response, 'Boleto')
        self.assertContains(response, 'Milhas')
        self.assertContains(response, 'R$ 540,00')

    def test_pagamento_simulado_aprova_reserva(self):
        user = get_user_model().objects.create_user(
            username='comprador',
            password='senha-segura-123',
            first_name='Comprador',
            tipo='passageiro',
        )
        passageiro = Passageiro.objects.create(
            usuario=user,
            nome='Comprador Teste',
            cpf_passaporte='COMP123456',
            data_nascimento='1990-01-01',
            contato='(11) 90000-0000',
            nacionalidade='Brasileira',
        )
        reserva = Reserva.objects.create(
            passageiro=passageiro,
            voo=self.voo_gru_rec,
            classe_tarifa='economy',
            quantidade_passageiros=1,
            assento='12A',
            status='pendente',
        )
        self.client.force_login(user)

        response = self.client.post(reverse('pagamento_reserva', args=[reserva.pk]), {
            'metodo': 'pix',
        }, follow=True)

        reserva.refresh_from_db()
        pagamento = Pagamento.objects.get(reserva=reserva)

        self.assertEqual(pagamento.status, 'aprovado')
        self.assertEqual(pagamento.metodo, 'pix')
        self.assertEqual(pagamento.valor_total, Decimal('270.00'))
        self.assertEqual(reserva.status, 'confirmada')
        self.assertContains(response, 'Pagamento aprovado')

    def test_tela_sucesso_reserva_exibe_assento_e_status(self):
        user = get_user_model().objects.create_user(
            username='comprador',
            password='senha-segura-123',
            first_name='Comprador',
            tipo='passageiro',
        )
        passageiro = Passageiro.objects.create(
            usuario=user,
            nome='Comprador Teste',
            cpf_passaporte='COMP123456',
            data_nascimento='1990-01-01',
            contato='(11) 90000-0000',
            nacionalidade='Brasileira',
        )
        reserva = Reserva.objects.create(
            passageiro=passageiro,
            voo=self.voo_gru_rec,
            classe_tarifa='economy',
            quantidade_passageiros=1,
            assento='12A',
            status='confirmada',
        )
        Pagamento.objects.create(
            reserva=reserva,
            valor_total=Decimal('270.00'),
            metodo='pix',
            status='aprovado',
            data_pagamento=timezone.now(),
        )
        self.client.force_login(user)

        response = self.client.get(reverse('reserva_sucesso', args=[reserva.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'Reserva #{reserva.pk}')
        self.assertContains(response, 'SB123')
        self.assertContains(response, '12A')
        self.assertContains(response, 'Confirmada')
        self.assertContains(response, 'Pix')
        self.assertContains(response, 'R$ 270,00')
        self.assertContains(response, reverse('dashboard_passageiro'))

    def test_passageiro_dono_consulta_tela_de_bilhete(self):
        user, passageiro = self.criar_usuario_passageiro_com_perfil(
            username='comprador_bilhete',
            cpf_passaporte='BIL123456',
        )
        reserva, bilhete = self.criar_reserva_confirmada_com_bilhete(passageiro)
        self.client.force_login(user)

        response = self.client.get(reverse('bilhete_reserva', args=[reserva.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bilhete / Comprovante')
        self.assertContains(response, passageiro.nome)
        self.assertContains(response, self.voo_gru_rec.numero_voo)
        self.assertContains(response, reserva.assento)
        self.assertContains(response, f'Reserva #{reserva.pk}')
        self.assertContains(response, reserva.get_status_display())
        self.assertContains(response, bilhete.codigo)
        self.assertContains(response, 'Voltar para Minhas viagens')
        self.assertContains(response, reverse('dashboard_passageiro'))

    def test_passageiro_nao_acessa_bilhete_de_outra_reserva(self):
        _, passageiro_dono = self.criar_usuario_passageiro_com_perfil(
            username='dono_bilhete',
            cpf_passaporte='DONO123456',
        )
        reserva, _ = self.criar_reserva_confirmada_com_bilhete(passageiro_dono)
        outro_usuario, _ = self.criar_usuario_passageiro_com_perfil(
            username='outro_passageiro',
            cpf_passaporte='OUTRO123456',
        )
        self.client.force_login(outro_usuario)

        response = self.client.get(reverse('bilhete_reserva', args=[reserva.pk]))

        self.assertRedirects(response, reverse('dashboard_passageiro'))

    def test_painel_passageiro_exibe_link_para_bilhete_confirmado(self):
        user, passageiro = self.criar_usuario_passageiro_com_perfil(
            username='comprador_link_bilhete',
            cpf_passaporte='LINK123456',
        )
        reserva, bilhete = self.criar_reserva_confirmada_com_bilhete(passageiro)
        self.client.force_login(user)

        response = self.client.get(reverse('dashboard_passageiro'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ver bilhete')
        self.assertContains(response, bilhete.codigo)
        self.assertContains(response, reverse('bilhete_reserva', args=[reserva.pk]))

    def test_minhas_viagens_lista_todas_reservas_do_passageiro(self):
        user, passageiro = self.criar_usuario_passageiro_com_perfil(
            username='comprador_viagens',
            cpf_passaporte='VIAG123456',
        )
        ContaMilhas.objects.create(
            passageiro=passageiro,
            saldo=12345,
            numero_programa='SB-654321',
        )
        reserva_confirmada, bilhete = self.criar_reserva_confirmada_com_bilhete(
            passageiro,
            codigo='TKT-VIAGENS-001',
        )
        reserva_pendente = Reserva.objects.create(
            passageiro=passageiro,
            voo=self.voo_gru_cwb,
            classe_tarifa='economy',
            quantidade_passageiros=1,
            assento='14C',
            status='pendente',
        )
        _, outro_passageiro = self.criar_usuario_passageiro_com_perfil(
            username='outro_viagens',
            cpf_passaporte='OUTVIAG123',
        )
        Reserva.objects.create(
            passageiro=outro_passageiro,
            voo=self.voo_rec_gru,
            classe_tarifa='economy',
            quantidade_passageiros=1,
            assento='20A',
            status='confirmada',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('minhas_viagens'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Minhas viagens')
        self.assertContains(response, f'Reserva #{reserva_confirmada.pk}')
        self.assertContains(response, f'Reserva #{reserva_pendente.pk}')
        self.assertContains(response, 'SB123')
        self.assertContains(response, 'SB124')
        self.assertNotContains(response, 'SB125')
        self.assertContains(response, 'Aprovado')
        self.assertContains(response, 'Pendente')
        self.assertContains(response, 'Ver detalhes')
        self.assertContains(response, 'Finalizar pagamento')
        self.assertContains(response, 'Ver bilhete')
        self.assertContains(response, bilhete.codigo)
        self.assertContains(response, '12345 milhas')

    def test_detalhe_reserva_mostra_status_pagamento_e_bilhete(self):
        user, passageiro = self.criar_usuario_passageiro_com_perfil(
            username='comprador_detalhe',
            cpf_passaporte='DET123456',
        )
        reserva, bilhete = self.criar_reserva_confirmada_com_bilhete(
            passageiro,
            codigo='TKT-DETALHE-001',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('detalhe_reserva', args=[reserva.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'Reserva #{reserva.pk}')
        self.assertContains(response, passageiro.nome)
        self.assertContains(response, self.voo_gru_rec.numero_voo)
        self.assertContains(response, reserva.assento)
        self.assertContains(response, 'Confirmada')
        self.assertContains(response, 'Pagamento aprovado')
        self.assertContains(response, 'Pix')
        self.assertContains(response, 'R$ 270,00')
        self.assertContains(response, bilhete.codigo)
        self.assertContains(response, reverse('bilhete_reserva', args=[reserva.pk]))

    def test_passageiro_nao_acessa_detalhe_reserva_de_outro_usuario(self):
        _, passageiro_dono = self.criar_usuario_passageiro_com_perfil(
            username='dono_reserva',
            cpf_passaporte='DONORES123',
        )
        reserva, _ = self.criar_reserva_confirmada_com_bilhete(
            passageiro_dono,
            codigo='TKT-DONO-001',
        )
        outro_usuario, _ = self.criar_usuario_passageiro_com_perfil(
            username='intruso_reserva',
            cpf_passaporte='INTRUSO123',
        )
        self.client.force_login(outro_usuario)

        response = self.client.get(reverse('detalhe_reserva', args=[reserva.pk]))

        self.assertRedirects(response, reverse('dashboard_passageiro'))

    def test_cancelar_reserva_altera_status_para_cancelada(self):
        user, passageiro = self.criar_usuario_passageiro_com_perfil(
            username='comprador_cancelamento',
            cpf_passaporte='CANC123456',
        )
        reserva, _ = self.criar_reserva_confirmada_com_bilhete(
            passageiro,
            codigo='TKT-CANCEL-001',
        )
        self.client.force_login(user)

        response = self.client.post(reverse('cancelar_reserva', args=[reserva.pk]))

        reserva.refresh_from_db()
        self.assertEqual(reserva.status, 'cancelada')
        self.assertRedirects(response, reverse('detalhe_reserva', args=[reserva.pk]))

    def test_reserva_confirmada_futura_permite_checkin_e_cria_cartao(self):
        user, passageiro = self.criar_usuario_passageiro_com_perfil(
            username='comprador_checkin',
            cpf_passaporte='CHECKIN123',
        )
        reserva, _ = self.criar_reserva_confirmada_com_bilhete(
            passageiro,
            codigo='TKT-CHECKIN-001',
        )
        self.client.force_login(user)

        response = self.client.post(reverse('realizar_checkin', args=[reserva.pk]), follow=True)

        checkin = CheckIn.objects.get(passageiro=passageiro, voo=reserva.voo)
        self.assertEqual(checkin.status, 'realizado')
        self.assertRedirects(response, reverse('cartao_embarque', args=[reserva.pk]))
        self.assertContains(response, 'Cartao de embarque')
        self.assertContains(response, passageiro.nome)
        self.assertContains(response, reserva.voo.numero_voo)
        self.assertContains(response, reserva.voo.partida.strftime('%d/%m/%Y'))
        self.assertContains(response, reserva.assento)
        self.assertContains(response, reserva.voo.portao.numero_portao)

    def test_checkin_duplicado_reaproveita_registro_existente(self):
        user, passageiro = self.criar_usuario_passageiro_com_perfil(
            username='comprador_checkin_dup',
            cpf_passaporte='CHECKINDUP',
        )
        reserva, _ = self.criar_reserva_confirmada_com_bilhete(
            passageiro,
            codigo='TKT-CHECKIN-DUP',
        )
        CheckIn.objects.create(
            passageiro=passageiro,
            voo=reserva.voo,
            status='realizado',
        )
        self.client.force_login(user)

        response = self.client.post(reverse('realizar_checkin', args=[reserva.pk]))

        self.assertEqual(CheckIn.objects.filter(passageiro=passageiro, voo=reserva.voo).count(), 1)
        self.assertRedirects(response, reverse('cartao_embarque', args=[reserva.pk]))

    def test_reserva_de_voo_passado_nao_permite_checkin(self):
        user, passageiro = self.criar_usuario_passageiro_com_perfil(
            username='comprador_checkin_passado',
            cpf_passaporte='CHECKPASS',
        )
        voo_passado = Voo.objects.create(
            numero_voo='SB-PASS',
            origem='GRU - Sao Paulo',
            destino='REC - Recife',
            partida=timezone.now() - timedelta(days=1),
            chegada=timezone.now() - timedelta(days=1, hours=-3),
            status='programado',
            aeronave=self.aeronave,
            portao=self.portao,
        )
        reserva = Reserva.objects.create(
            passageiro=passageiro,
            voo=voo_passado,
            classe_tarifa='economy',
            quantidade_passageiros=1,
            assento='18A',
            status='confirmada',
        )
        self.client.force_login(user)

        response = self.client.post(reverse('realizar_checkin', args=[reserva.pk]), follow=True)

        self.assertFalse(CheckIn.objects.filter(passageiro=passageiro, voo=voo_passado).exists())
        self.assertContains(response, 'Check-in disponivel apenas para reservas confirmadas de voos futuros.')

    def test_reserva_pendente_nao_permite_checkin(self):
        user, passageiro = self.criar_usuario_passageiro_com_perfil(
            username='comprador_checkin_pendente',
            cpf_passaporte='CHECKPEND',
        )
        reserva = Reserva.objects.create(
            passageiro=passageiro,
            voo=self.voo_gru_rec,
            classe_tarifa='economy',
            quantidade_passageiros=1,
            assento='17A',
            status='pendente',
        )
        self.client.force_login(user)

        response = self.client.post(reverse('realizar_checkin', args=[reserva.pk]), follow=True)

        self.assertFalse(CheckIn.objects.filter(passageiro=passageiro, voo=reserva.voo).exists())
        self.assertContains(response, 'Check-in disponivel apenas para reservas confirmadas de voos futuros.')

    def test_painel_exibe_acao_de_checkin_para_reserva_confirmada_futura(self):
        user, passageiro = self.criar_usuario_passageiro_com_perfil(
            username='comprador_checkin_link',
            cpf_passaporte='CHECKLINK',
        )
        reserva, _ = self.criar_reserva_confirmada_com_bilhete(
            passageiro,
            codigo='TKT-CHECKIN-LINK',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('minhas_viagens'))

        self.assertContains(response, 'Fazer check-in')
        self.assertContains(response, reverse('realizar_checkin', args=[reserva.pk]))

    def test_passageiro_nao_faz_checkin_em_reserva_de_outro_usuario(self):
        _, passageiro_dono = self.criar_usuario_passageiro_com_perfil(
            username='dono_checkin',
            cpf_passaporte='DONOCHECK',
        )
        reserva, _ = self.criar_reserva_confirmada_com_bilhete(
            passageiro_dono,
            codigo='TKT-DONO-CHECK',
        )
        outro_usuario, _ = self.criar_usuario_passageiro_com_perfil(
            username='intruso_checkin',
            cpf_passaporte='INTRCHECK',
        )
        self.client.force_login(outro_usuario)

        response = self.client.post(reverse('realizar_checkin', args=[reserva.pk]))

        self.assertFalse(CheckIn.objects.filter(passageiro=passageiro_dono, voo=reserva.voo).exists())
        self.assertRedirects(response, reverse('dashboard_passageiro'))

    def test_notificacoes_passageiro_lista_apenas_do_usuario(self):
        user, passageiro = self.criar_usuario_passageiro_com_perfil(
            username='comprador_notificacoes',
            cpf_passaporte='NOTIF123',
        )
        _, outro_passageiro = self.criar_usuario_passageiro_com_perfil(
            username='outro_notificacoes',
            cpf_passaporte='NOTIFOUT123',
        )
        Notificacao.objects.create(
            passageiro=passageiro,
            mensagem='Seu voo teve o portao alterado.',
            tipo='mudanca_portao',
        )
        Notificacao.objects.create(
            passageiro=outro_passageiro,
            mensagem='Mensagem de outro passageiro.',
            tipo='geral',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('notificacoes_passageiro'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Notificações')
        self.assertContains(response, 'Seu voo teve o portao alterado.')
        self.assertNotContains(response, 'Mensagem de outro passageiro.')

    def test_reserva_aparece_no_painel_do_passageiro(self):
        user = get_user_model().objects.create_user(
            username='comprador',
            password='senha-segura-123',
            first_name='Comprador',
            tipo='passageiro',
        )
        passageiro = Passageiro.objects.create(
            usuario=user,
            nome='Comprador Teste',
            cpf_passaporte='COMP123456',
            data_nascimento='1990-01-01',
            contato='(11) 90000-0000',
            nacionalidade='Brasileira',
        )
        self.client.force_login(user)

        self.client.post(reverse('criar_reserva', args=[self.voo_gru_rec.pk]), {
            'classe': 'economy',
            'passageiros': 1,
        })
        reserva = Reserva.objects.get(passageiro=passageiro)
        response = self.client.get(reverse('dashboard_passageiro'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SB123')
        self.assertContains(response, reserva.assento)
        self.assertContains(response, 'Pendente')
        self.assertContains(response, 'Finalizar pagamento')

    def test_usuario_sem_perfil_passageiro_nao_cria_reserva(self):
        user = get_user_model().objects.create_user(
            username='usuario_sem_perfil',
            password='senha-segura-123',
            first_name='Usuario',
            tipo='passageiro',
        )
        self.client.force_login(user)

        response = self.client.post(reverse('criar_reserva', args=[self.voo_gru_rec.pk]), {
            'classe': 'economy',
            'passageiros': 1,
        }, follow=True)

        self.assertFalse(Reserva.objects.exists())
        self.assertContains(response, 'Complete seu cadastro de passageiro antes de reservar um voo.')

    def test_pagamento_milhas_sucesso(self):
        from .models import ContaMilhas, TransacaoMilhas
        user = get_user_model().objects.create_user(
            username='comprador_milhas',
            password='senha-segura-123',
            first_name='Comprador',
            tipo='passageiro',
        )
        passageiro = Passageiro.objects.create(
            usuario=user,
            nome='Comprador Teste',
            cpf_passaporte='COMP1234567',
            data_nascimento='1990-01-01',
            contato='(11) 90000-0000',
            nacionalidade='Brasileira',
        )
        # Cria conta de milhas com saldo de 5000 milhas
        conta = ContaMilhas.objects.create(
            passageiro=passageiro,
            saldo=5000,
            numero_programa='SB-123456'
        )
        reserva = Reserva.objects.create(
            passageiro=passageiro,
            voo=self.voo_gru_rec,
            classe_tarifa='economy',
            quantidade_passageiros=1, # Custa R$ 270,00 -> 2700 milhas
            assento='12A',
            status='pendente',
        )
        self.client.force_login(user)

        response = self.client.post(reverse('pagamento_reserva', args=[reserva.pk]), {
            'metodo': 'milhas',
        }, follow=True)

        reserva.refresh_from_db()
        conta.refresh_from_db()
        pagamento = Pagamento.objects.get(reserva=reserva)

        self.assertEqual(pagamento.status, 'aprovado')
        self.assertEqual(pagamento.metodo, 'milhas')
        self.assertEqual(reserva.status, 'confirmada')
        self.assertEqual(conta.saldo, 5000 - 2700) # Saldo restante: 2300
        
        # Verifica se gerou transação de resgate
        transacao = TransacaoMilhas.objects.filter(conta=conta, tipo='resgate').first()
        self.assertIsNotNone(transacao)
        self.assertEqual(transacao.quantidade, -2700)

    def test_pagamento_milhas_saldo_insuficiente(self):
        from .models import ContaMilhas
        user = get_user_model().objects.create_user(
            username='comprador_liso',
            password='senha-segura-123',
            first_name='Comprador',
            tipo='passageiro',
        )
        passageiro = Passageiro.objects.create(
            usuario=user,
            nome='Comprador Teste',
            cpf_passaporte='COMP1234568',
            data_nascimento='1990-01-01',
            contato='(11) 90000-0000',
            nacionalidade='Brasileira',
        )
        # Cria conta de milhas com saldo insuficiente (ex: 500 milhas)
        conta = ContaMilhas.objects.create(
            passageiro=passageiro,
            saldo=500,
            numero_programa='SB-123457'
        )
        reserva = Reserva.objects.create(
            passageiro=passageiro,
            voo=self.voo_gru_rec,
            classe_tarifa='economy',
            quantidade_passageiros=1, # Custa R$ 270,00 -> 2700 milhas
            assento='12A',
            status='pendente',
        )
        self.client.force_login(user)

        response = self.client.post(reverse('pagamento_reserva', args=[reserva.pk]), {
            'metodo': 'milhas',
        })

        reserva.refresh_from_db()
        conta.refresh_from_db()
        self.assertEqual(reserva.status, 'pendente') # Permanece pendente
        self.assertEqual(conta.saldo, 500) # Não altera saldo
        self.assertFormError(response.context['pagamento_form'], 'metodo', 'Saldo de milhas insuficiente. Necessário: 2700 milhas. Seu saldo: 500 milhas.')

    def test_pagamento_pix_acumula_milhas(self):
        from .models import ContaMilhas, TransacaoMilhas
        user = get_user_model().objects.create_user(
            username='comprador_rico',
            password='senha-segura-123',
            first_name='Comprador',
            tipo='passageiro',
        )
        passageiro = Passageiro.objects.create(
            usuario=user,
            nome='Comprador Teste',
            cpf_passaporte='COMP1234569',
            data_nascimento='1990-01-01',
            contato='(11) 90000-0000',
            nacionalidade='Brasileira',
        )
        conta = ContaMilhas.objects.create(
            passageiro=passageiro,
            saldo=1000,
            numero_programa='SB-123458'
        )
        reserva = Reserva.objects.create(
            passageiro=passageiro,
            voo=self.voo_gru_rec,
            classe_tarifa='economy',
            quantidade_passageiros=1, # Custa R$ 270,00
            assento='12A',
            status='pendente',
        )
        self.client.force_login(user)

        self.client.post(reverse('pagamento_reserva', args=[reserva.pk]), {
            'metodo': 'pix',
        })

        conta.refresh_from_db()
        self.assertEqual(conta.saldo, 1000 + 270) # Acumula 270 milhas (1 por real)
        
        # Verifica se gerou transação de acumulo
        transacao = TransacaoMilhas.objects.filter(conta=conta, tipo='acumulo').first()
        self.assertIsNotNone(transacao)
        self.assertEqual(transacao.quantidade, 270)

    def test_pagamento_gera_bilhete_automatico(self):
        user = get_user_model().objects.create_user(
            username='comprador_tkt',
            password='senha-segura-123',
            first_name='Comprador',
            tipo='passageiro',
        )
        passageiro = Passageiro.objects.create(
            usuario=user,
            nome='Comprador Teste',
            cpf_passaporte='COMP1234570',
            data_nascimento='1990-01-01',
            contato='(11) 90000-0000',
            nacionalidade='Brasileira',
        )
        reserva = Reserva.objects.create(
            passageiro=passageiro,
            voo=self.voo_gru_rec,
            classe_tarifa='economy',
            quantidade_passageiros=1,
            assento='12A',
            status='pendente',
        )
        self.client.force_login(user)

        self.client.post(reverse('pagamento_reserva', args=[reserva.pk]), {
            'metodo': 'pix',
        })

        reserva.refresh_from_db()
        self.assertEqual(reserva.status, 'confirmada')
        
        # Verifica se o bilhete foi criado
        bilhete = Bilhete.objects.filter(reserva=reserva).first()
        self.assertIsNotNone(bilhete)
        self.assertTrue(bilhete.codigo.startswith('TKT-'))
        self.assertTrue(Bilhete._meta.get_field('codigo').unique)

    def test_status_voo_pagina_publica_acessivel(self):
        response = self.client.get(reverse('status_voo'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Status de Voo')

    def test_status_voo_busca_com_sucesso(self):
        # Test basic search
        response = self.client.get(reverse('status_voo'), {'numero_voo': 'SB123'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SB123')
        self.assertContains(response, 'GRU - São Paulo')
        self.assertContains(response, 'REC - Recife')
        self.assertContains(response, 'Programado')
        self.assertContains(response, 'Airbus A320')
        self.assertContains(response, 'A1')

        # Test robustness (lowercase, space, hyphen)
        response_robust = self.client.get(reverse('status_voo'), {'numero_voo': '  sb-123  '})
        self.assertEqual(response_robust.status_code, 200)
        self.assertContains(response_robust, 'SB123')

    def test_status_voo_busca_voo_inexistente(self):
        response = self.client.get(reverse('status_voo'), {'numero_voo': 'SB888'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Voo não encontrado')

    def test_painel_funcionario_lista_voos_do_dia_com_form_operacional(self):
        user, _ = self.criar_usuario_funcionario_com_perfil()
        voo_hoje = Voo.objects.create(
            numero_voo='SBHOJE',
            origem='GRU - SÃ£o Paulo',
            destino='REC - Recife',
            partida=timezone.localtime().replace(hour=14, minute=0, second=0, microsecond=0),
            chegada=timezone.localtime().replace(hour=17, minute=0, second=0, microsecond=0),
            status='programado',
            aeronave=self.aeronave,
            portao=self.portao,
        )
        self.client.force_login(user)

        response = self.client.get(reverse('dashboard_funcionario'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Voos de Hoje')
        self.assertContains(response, voo_hoje.numero_voo)
        self.assertContains(response, reverse('atualizar_voo_operacional', args=[voo_hoje.pk]))
        self.assertContains(response, 'name="status"')
        self.assertContains(response, 'name="portao"')
        self.assertNotContains(response, self.voo_gru_rec.numero_voo)

    def test_funcionario_altera_status_e_portao_do_voo(self):
        user, _ = self.criar_usuario_funcionario_com_perfil()
        novo_portao = PortaoEmbarque.objects.create(
            numero_portao='B2',
            localizacao='Terminal 2',
            status='livre',
        )
        _, passageiro = self.criar_usuario_passageiro_com_perfil(
            username='afetado_operacao',
            cpf_passaporte='AFETADO123',
        )
        Reserva.objects.create(
            passageiro=passageiro,
            voo=self.voo_gru_rec,
            classe_tarifa='economy',
            quantidade_passageiros=1,
            assento='9A',
            status='confirmada',
        )
        self.client.force_login(user)

        response = self.client.post(reverse('atualizar_voo_operacional', args=[self.voo_gru_rec.pk]), {
            'status': 'atrasado',
            'portao': novo_portao.pk,
        })

        self.voo_gru_rec.refresh_from_db()
        self.assertRedirects(response, reverse('dashboard_funcionario'))
        self.assertEqual(self.voo_gru_rec.status, 'atrasado')
        self.assertEqual(self.voo_gru_rec.portao, novo_portao)

        notificacao = Notificacao.objects.get(passageiro=passageiro)
        self.assertEqual(notificacao.tipo, 'atraso')
        self.assertIn(self.voo_gru_rec.numero_voo, notificacao.mensagem)
        self.assertIn(novo_portao.numero_portao, notificacao.mensagem)

    def test_funcionario_notifica_todos_os_passageiros_com_reserva_ativa(self):
        user, _ = self.criar_usuario_funcionario_com_perfil()
        _, passageiro_um = self.criar_usuario_passageiro_com_perfil(
            username='afetado_um',
            cpf_passaporte='AFETADO1',
        )
        _, passageiro_dois = self.criar_usuario_passageiro_com_perfil(
            username='afetado_dois',
            cpf_passaporte='AFETADO2',
        )
        Reserva.objects.create(
            passageiro=passageiro_um,
            voo=self.voo_gru_rec,
            classe_tarifa='economy',
            quantidade_passageiros=1,
            assento='10A',
            status='confirmada',
        )
        Reserva.objects.create(
            passageiro=passageiro_dois,
            voo=self.voo_gru_rec,
            classe_tarifa='economy',
            quantidade_passageiros=1,
            assento='10B',
            status='pendente',
        )
        self.client.force_login(user)

        self.client.post(reverse('atualizar_voo_operacional', args=[self.voo_gru_rec.pk]), {
            'status': 'cancelado',
            'portao': self.portao.pk,
        })

        self.assertEqual(Notificacao.objects.filter(tipo='cancelamento').count(), 2)
        self.assertTrue(Notificacao.objects.filter(passageiro=passageiro_um).exists())
        self.assertTrue(Notificacao.objects.filter(passageiro=passageiro_dois).exists())

    def test_passageiro_nao_altera_status_operacional(self):
        user, _ = self.criar_usuario_passageiro_com_perfil(
            username='passageiro_operacao',
            cpf_passaporte='PASSOP',
        )
        self.client.force_login(user)

        response = self.client.post(reverse('atualizar_voo_operacional', args=[self.voo_gru_rec.pk]), {
            'status': 'cancelado',
            'portao': self.portao.pk,
        })

        self.voo_gru_rec.refresh_from_db()
        self.assertRedirects(response, reverse('dashboard_passageiro'))
        self.assertEqual(self.voo_gru_rec.status, 'programado')
        self.assertFalse(Notificacao.objects.exists())

    def test_painel_funcionario_exibe_bagagens_monitoradas(self):
        user, _ = self.criar_usuario_funcionario_com_perfil()
        _, passageiro = self.criar_usuario_passageiro_com_perfil(
            username='bagagem_operacao',
            cpf_passaporte='BAGOP',
        )
        reserva = Reserva.objects.create(
            passageiro=passageiro,
            voo=self.voo_gru_rec,
            classe_tarifa='economy',
            quantidade_passageiros=1,
            assento='11A',
            status='confirmada',
        )
        Bagagem.objects.create(
            reserva=reserva,
            peso=Decimal('18.50'),
            status='despachada',
            numero_rastreio='BAG123',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('dashboard_funcionario'))

        self.assertContains(response, 'BAG123')
        self.assertContains(response, passageiro.nome)
        self.assertContains(response, self.voo_gru_rec.numero_voo)


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

    def test_cadastro_preserva_next_ao_voltar_para_login(self):
        next_url = '/voos/10/selecionar/?classe=economy'
        data = self.dados_passageiro()
        data['next'] = next_url

        response = self.client.post(self.cadastro_url, data)

        expected_url = f'{self.login_url}?next={quote(next_url, safe="")}'
        self.assertRedirects(response, expected_url)

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

        self.assertRedirects(response, reverse('dashboard_funcionario'))

    def test_cadastro_passageiro_cria_conta_milhas_com_saldo_inicial(self):
        from .models import ContaMilhas
        response = self.client.post(self.cadastro_url, self.dados_passageiro())
        self.assertRedirects(response, self.login_url)

        usuario = get_user_model().objects.get(username='maria.silva')
        passageiro = Passageiro.objects.get(usuario=usuario)
        conta = ContaMilhas.objects.get(passageiro=passageiro)
        
        self.assertEqual(conta.saldo, 10000)
        self.assertTrue(conta.numero_programa.startswith('SB-'))
