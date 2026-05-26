# Sky Bridge Airport

Aplicacao web em Django para um sistema aeroportuario chamado Sky Bridge. O projeto combina uma landing page responsiva de ofertas de viagens com uma base de modelos para gerenciamento de usuarios, passageiros, funcionarios, aeroportos, voos, reservas, bilhetes, bagagens, check-in, portoes de embarque, pagamentos, milhas, promocoes e notificacoes.

A Home atual apresenta ofertas, busca visual, filtros, beneficios e navegacao preparada para futuras funcionalidades. O fluxo de acesso ja usa a autenticacao nativa do Django para login, logout e dashboard protegido, enquanto o cadastro ainda e apenas visual.

## Funcionalidades atuais

- Landing page responsiva como Home principal.
- Header com logo, navegacao e botao "Fazer login".
- Botao "Fazer login" levando para a pagina de acesso em `/acesso/`.
- Pagina de acesso com cards para login e cadastro.
- Tela de login integrada ao `LoginView` do Django.
- Logout integrado ao `LogoutView` do Django.
- Dashboard protegido por `login_required`.
- Tela de cadastro visual, ainda sem gravar usuarios no banco.
- Modulo visual de busca de voos e servicos.
- Abas, filtros, campos e botoes clicaveis como placeholders.
- Cards de ofertas com destinos e precos ficticios.
- Secoes de beneficios, milhas e footer.
- Usuario customizado com tipo de conta: passageiro, funcionario ou administrador.
- Modelos Django registrados no admin para entidades do dominio aeroportuario.
- Context processor para contar notificacoes nao lidas de passageiros autenticados.
- Testes automatizados cobrindo metadados de modelos e fluxo basico de autenticacao.

## Funcionalidades futuras

- Cadastro real de usuarios e criacao dos perfis correspondentes.
- Busca real de voos.
- Area do usuario para reservas e viagens.
- Sistema completo de reservas.
- Pagamentos e emissao de bilhetes.
- Filtros funcionais para ofertas.
- Check-in online funcional.
- Gerenciamento real de milhas.
- Chat/FAQ de ajuda com IA.
- Integracao com APIs externas.

## Tecnologias utilizadas

- Python
- Django 5.2.13
- PostgreSQL via `psycopg2-binary`
- HTML com Django Templates
- CSS
- Font Awesome via CDN

Nao foram encontrados neste projeto:

- `package.json`
- React
- Vite
- TypeScript
- Tailwind CSS
- React Router
- ESLint
- Vitest ou Testing Library

## Estrutura de pastas

```txt
projeto_aeroporto/
  .gitignore
  manage.py
  README.md
  requirements.txt
  sistema_aeroporto/
    __init__.py
    asgi.py
    settings.py
    urls.py
    wsgi.py
  skybridgeapp/
    __init__.py
    admin.py
    apps.py
    context_processors.py
    models.py
    tests.py
    urls.py
    views.py
    migrations/
      __init__.py
      0001_initial.py
      0002_aeroporto_companhiaaerea_contamilhas_pagamento_and_more.py
    static/
      css/
        auth_home.css
        cadastro.css
        home.css
        login.css
    templates/
      auth_home.html
      cadastro.html
      dashboard.html
      home.html
      login.html
```

## Paginas e rotas

| Rota | View | Template | Descricao |
| --- | --- | --- | --- |
| `/` | `home` | `home.html` | Landing page principal com ofertas, busca visual e beneficios. |
| `/acesso/` | `auth_home` | `auth_home.html` | Pagina intermediaria com opcoes de login e cadastro. |
| `/cadastro/` | `cadastro` | `cadastro.html` | Tela visual de criacao de conta, ainda sem persistencia. |
| `/login/` | `SkyBridgeLoginView` | `login.html` | Login real usando autenticacao do Django. |
| `/logout/` | `SkyBridgeLogoutView` | - | Logout real usando autenticacao do Django. |
| `/dashboard/` | `dashboard` | `dashboard.html` | Area protegida para usuarios autenticados. |
| `/admin/` | Django Admin | Django Admin | Painel administrativo do Django. |

Fluxo principal:

1. O usuario acessa `/`.
2. Clica em "Fazer login".
3. E direcionado para `/acesso/`.
4. Clica em "Fazer Login".
5. E direcionado para `/login/`.
6. Apos autenticar, e redirecionado para `/dashboard/`.
7. No dashboard, pode sair pelo formulario de logout.

## Dados e dominio

O app `skybridgeapp` possui os seguintes modelos:

- `UsuarioCustomizado`
- `Passageiro`
- `ContaMilhas`
- `TransacaoMilhas`
- `Funcionario`
- `Administrador`
- `Aeroporto`
- `CompanhiaAerea`
- `Aeronave`
- `PortaoEmbarque`
- `Voo`
- `Tarifa`
- `Promocao`
- `Reserva`
- `Pagamento`
- `Bilhete`
- `Bagagem`
- `CheckIn`
- `Notificacao`

Esses modelos estao registrados no Django Admin em `skybridgeapp/admin.py`.

### Usuario customizado

O projeto define `AUTH_USER_MODEL = 'skybridgeapp.UsuarioCustomizado'`. Esse modelo herda de `AbstractUser` e adiciona o campo `tipo`, que pode ser:

- `passageiro`
- `funcionario`
- `administrador`

Os modelos `Passageiro` e `Funcionario` funcionam como perfis complementares ligados ao usuario por `OneToOneField`.

### Notificacoes

O context processor `notificacoes_nao_lidas` adiciona ao contexto dos templates a quantidade de notificacoes nao lidas do passageiro autenticado. Usuarios anonimos ou sem perfil de passageiro recebem total `0`.

## Banco de dados

O projeto esta configurado para usar PostgreSQL em `sistema_aeroporto/settings.py`.

Configuracao atual:

- Banco: `skybridge`
- Usuario: `postgres`
- Host: `127.0.0.1`
- Porta: `5432`

Antes de rodar migrations ou o servidor Django com `runserver`, garanta que:

- o PostgreSQL esteja instalado;
- o servico esteja rodando em `127.0.0.1:5432`;
- o banco configurado exista;
- as credenciais locais estejam corretas no arquivo de configuracao.

> Observacao: as credenciais e a `SECRET_KEY` estao hoje diretamente em `settings.py`. Antes de usar este projeto em producao ou publicar o repositorio, mova segredos para variaveis de ambiente ou um arquivo `.env` nao versionado.

## Como rodar localmente

### 1. Criar e ativar um ambiente virtual

Windows PowerShell:

```powershell
python -m venv ..\meuMundo
..\meuMundo\Scripts\Activate.ps1
```

Windows CMD:

```bat
python -m venv ..\meuMundo
..\meuMundo\Scripts\activate.bat
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Verificar configuracao do Django

```bash
python manage.py check
```

### 4. Aplicar migrations

```bash
python manage.py migrate
```

### 5. Criar superusuario

```bash
python manage.py createsuperuser
```

### 6. Rodar servidor local

```bash
python manage.py runserver
```

Depois acesse:

- Home: `http://127.0.0.1:8000/`
- Pagina de acesso: `http://127.0.0.1:8000/acesso/`
- Cadastro visual: `http://127.0.0.1:8000/cadastro/`
- Login: `http://127.0.0.1:8000/login/`
- Dashboard: `http://127.0.0.1:8000/dashboard/`
- Admin: `http://127.0.0.1:8000/admin/`

## Scripts e comandos disponiveis

Este projeto nao possui `package.json`, portanto nao ha scripts `npm run lint`, `npm run build`, `npm test` ou `npm run typecheck`.

Comandos Django uteis:

```bash
python manage.py check
python manage.py test
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Testes

O arquivo `skybridgeapp/tests.py` possui testes implementados para:

- metadados e relacionamentos principais dos modelos de dominio;
- modelos comerciais como tarifa, promocao e pagamento;
- modelos de milhas;
- renderizacao da Home;
- links da pagina de acesso;
- renderizacao do cadastro visual;
- renderizacao do login;
- redirecionamento de logout;
- protecao do dashboard para usuario anonimo;
- acesso ao dashboard para usuario autenticado.

Para rodar os testes Django:

```bash
python manage.py test
```

Para novas funcionalidades com comportamento ou regra de negocio, use TDD:

1. Entenda o comportamento esperado.
2. Crie testes que falhem primeiro.
3. Implemente o minimo necessario para passar.
4. Refatore mantendo os testes passando.

Priorize testes orientados ao comportamento do usuario para navegacao, formularios, validacoes, filtros, estado, integracao entre componentes e regras de negocio. Evite testes frageis baseados em classes CSS ou detalhes internos.

## Desenvolvimento frontend

O frontend atual usa Django Templates e CSS estatico.

Arquivos principais:

- `skybridgeapp/templates/home.html`: landing page principal.
- `skybridgeapp/templates/auth_home.html`: pagina de acesso com login/cadastro.
- `skybridgeapp/templates/login.html`: tela de login integrada ao Django.
- `skybridgeapp/templates/cadastro.html`: tela visual de criacao de conta.
- `skybridgeapp/templates/dashboard.html`: area protegida apos login.
- `skybridgeapp/static/css/home.css`: estilos da landing page.
- `skybridgeapp/static/css/auth_home.css`: estilos da pagina de acesso e dashboard.
- `skybridgeapp/static/css/login.css`: estilos da tela de login.
- `skybridgeapp/static/css/cadastro.css`: estilos da tela de cadastro.

Os botoes, filtros e abas da landing page sao placeholders visuais neste momento. Eles devem permanecer sem comportamento real ate que uma funcionalidade seja definida e implementada com testes quando aplicavel.

O formulario de cadastro tambem e visual: ele possui campos e CSRF token, mas o envio e bloqueado no template por JavaScript e ainda nao cria usuarios.

## Boas praticas para contribuir

- Antes de alterar comportamento, escreva ou atualize testes relevantes.
- Rode `python manage.py check` antes de finalizar mudancas.
- Rode `python manage.py test` quando houver testes ou alteracoes de comportamento.
- Nao altere a configuracao de banco sem necessidade clara.
- Nao implemente busca real, APIs externas ou regras de reserva sem escopo definido.
- Mantenha textos, assets e imagens sem copiar material proprietario de outras empresas.
- Prefira codigo simples e legivel a abstracoes desnecessarias.

## Observacoes conhecidas

- O servidor Django padrao depende do PostgreSQL configurado em `settings.py`.
- Sem PostgreSQL rodando localmente, `runserver`, `migrate` e comandos que consultem migrations podem falhar ao conectar no banco.
- O login ja usa autenticacao real do Django.
- O cadastro ainda e apenas visual e nao cria usuarios.
- A busca, os filtros, as ofertas e os botoes comerciais ainda sao placeholders.
- Nao ha pipeline de build frontend separado.
