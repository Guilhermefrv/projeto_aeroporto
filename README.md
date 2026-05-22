# Sky Bridge Airport Landing Page

Aplicacao web em Django para um sistema aeroportuario chamado Sky Bridge. O projeto combina uma landing page responsiva, inspirada em experiencias de compra de passagens aereas, com uma base de modelos para gerenciamento de passageiros, voos, reservas, bilhetes, bagagens, check-in, portoes de embarque e notificacoes.

A Home atual apresenta ofertas, busca visual, filtros, beneficios e navegacao preparada para futuras funcionalidades. A antiga Home foi preservada como uma pagina de acesso, mantendo o fluxo visual de login/cadastro sem implementar autenticacao real neste momento.

## Preview

![Preview do projeto](./docs/preview.png)

> A imagem acima e um placeholder para uma captura futura da interface.

## Funcionalidades atuais

- Landing page responsiva como Home principal.
- Header com logo, navegacao e botao "Fazer login".
- Botao "Fazer login" da landing levando para a antiga Home preservada em `/acesso/`.
- Pagina de acesso com cards para login e cadastro visual.
- Tela de login visual com formulario, CSRF token, campos obrigatorios e botao de voltar.
- Modulo visual de busca de voos e servicos.
- Abas, filtros, campos e botoes clicaveis como placeholders, sem regra real ainda.
- Cards de ofertas com destinos e precos ficticios.
- Secao de beneficios.
- Footer com colunas de links e redes sociais.
- Modelos Django registrados no admin para entidades do dominio aeroportuario.
- Estrutura preparada para futuras integracoes de busca, autenticacao e reservas.

## Funcionalidades futuras

- Busca real de voos.
- Login e autenticacao com usuarios reais.
- Area do usuario para reservas e viagens.
- Chat/FAQ de ajuda com IA.
- Integracao com APIs externas.
- Sistema de reservas.
- Filtros funcionais para ofertas.
- Check-in online funcional.
- Testes automatizados seguindo TDD para novas regras de negocio e comportamentos.

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
  manage.py
  requirements.txt
  sistema_aeroporto/
    settings.py
    urls.py
    asgi.py
    wsgi.py
  skybridgeapp/
    admin.py
    apps.py
    models.py
    tests.py
    urls.py
    views.py
    migrations/
      0001_initial.py
    templates/
      home.html
      auth_home.html
      login.html
    static/
      css/
        home.css
        auth_home.css
        login.css
```

## Paginas e rotas

| Rota | View | Template | Descricao |
| --- | --- | --- | --- |
| `/` | `home` | `home.html` | Nova landing page principal com ofertas e busca visual. |
| `/acesso/` | `auth_home` | `auth_home.html` | Antiga Home preservada como pagina de acesso. |
| `/login/` | `login_view` | `login.html` | Tela visual de login. |
| `/admin/` | Django Admin | Django Admin | Painel administrativo do Django. |

Fluxo principal:

1. O usuario acessa `/`.
2. Clica em "Fazer login".
3. E direcionado para `/acesso/`.
4. Clica em "Fazer Login".
5. E direcionado para `/login/`.

## Dados e dominio

O app `skybridgeapp` possui modelos para:

- `Passageiro`
- `Funcionario`
- `Administrador`
- `Aeronave`
- `Voo`
- `Reserva`
- `Bilhete`
- `Bagagem`
- `CheckIn`
- `PortaoEmbarque`
- `Notificacao`

Esses modelos estao registrados no Django Admin em `skybridgeapp/admin.py`.

## Banco de dados

O projeto esta configurado atualmente para usar PostgreSQL em `sistema_aeroporto/settings.py`.

Antes de rodar migrations ou o servidor Django com `runserver`, garanta que:

- o PostgreSQL esteja instalado;
- o servico esteja rodando em `127.0.0.1:5432`;
- o banco configurado exista;
- as credenciais locais estejam corretas no arquivo de configuracao.

> Observacao: as credenciais estao hoje diretamente em `settings.py`. Antes de usar este projeto em producao ou publicar o repositorio, mova segredos para variaveis de ambiente ou um arquivo `.env` nao versionado.

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
- Login visual: `http://127.0.0.1:8000/login/`
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

O arquivo `skybridgeapp/tests.py` existe, mas ainda nao ha testes implementados.

Para rodar os testes Django:

```bash
python manage.py test
```

Para novas funcionalidades com comportamento ou regra de negocio, use TDD:

1. Entenda o comportamento esperado.
2. Crie testes que falhem primeiro.
3. Implemente o minimo necessario para passar.
4. Refatore mantendo os testes passando.

Priorize testes orientados ao comportamento do usuario para navegacao, formularios, validacoes, filtros, estado, chat/FAQ, integracao entre componentes e regras de negocio. Evite testes frageis baseados em classes CSS ou detalhes internos.

## Desenvolvimento frontend

O frontend atual usa Django Templates e CSS estatico.

Arquivos principais:

- `skybridgeapp/templates/home.html`: landing page principal.
- `skybridgeapp/templates/auth_home.html`: antiga Home preservada como pagina de acesso.
- `skybridgeapp/templates/login.html`: tela visual de login.
- `skybridgeapp/static/css/home.css`: estilos da landing page.
- `skybridgeapp/static/css/auth_home.css`: estilos da pagina de acesso.
- `skybridgeapp/static/css/login.css`: estilos da tela de login.

Os botoes, filtros e abas da landing page sao placeholders visuais neste momento. Eles devem permanecer sem comportamento real ate que uma funcionalidade seja definida e implementada com testes quando aplicavel.

## Boas praticas para contribuir

- Antes de alterar comportamento, escreva ou atualize testes relevantes.
- Rode `python manage.py check` antes de finalizar mudancas.
- Rode `python manage.py test` quando houver testes ou alteracoes de comportamento.
- Nao altere a configuracao de banco sem necessidade clara.
- Nao implemente autenticacao, busca real ou APIs externas sem escopo definido.
- Mantenha textos, assets e imagens sem copiar material proprietario de outras empresas.
- Prefira codigo simples e legivel a abstracoes desnecessarias.

## Observacoes conhecidas

- O servidor Django padrao depende do PostgreSQL configurado em `settings.py`.
- Sem PostgreSQL rodando localmente, `runserver`, `migrate` e comandos que consultem migrations podem falhar ao conectar no banco.
- A tela de login ainda e apenas visual; nao autentica usuarios.
- A busca e os filtros ainda sao placeholders.
- Nao ha pipeline de build frontend separado.
