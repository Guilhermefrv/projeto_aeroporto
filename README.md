# Sky Bridge Airport

Aplicacao web em Django para um sistema academico de aeroporto/companhia aerea. O projeto combina uma landing page de ofertas nacionais com fluxo real de cadastro, login, busca de voos, reserva, pagamento simulado, bilhete, check-in, dashboards por tipo de usuario e administracao simples.

O escopo foi mantido propositalmente simples para apresentacao de faculdade: o sistema trabalha com voos nacionais no Brasil, dados populados por comando de gerenciamento e funcionalidades demonstraveis sem integracoes externas.

## Preview

![Preview do projeto](./docs/preview.png)

## Funcionalidades atuais

- Landing page responsiva com header, ofertas nacionais, busca de voos, beneficios e footer.
- Cadastro real com Bootstrap Modal para passageiro, funcionario e administrador.
- Login, logout, redefinicao e alteracao de senha usando recursos nativos do Django.
- Header dinamico para usuario autenticado com dropdown de conta.
- Busca real de voos nacionais usando dados do banco.
- Faixa de datas proximas com precos e sugestoes quando nao ha voo na data escolhida.
- Fluxo simples de ida e volta: seleciona ida, escolhe volta, revisa resumo e cria uma viagem agrupada.
- Pagina de detalhe do voo com origem, destino, horarios, cabine, passageiros e preco real.
- Escolha real de assento no detalhe do voo, bloqueando assentos ja ocupados.
- Reserva real associada ao passageiro logado com assento escolhido.
- Pagamento simulado por Pix, cartao, boleto ou milhas, incluindo pagamento unico para ida e volta.
- Emissao automatica de bilhete/comprovante apos pagamento aprovado.
- Area do passageiro com reservas, bilhetes, check-in, notificacoes e milhas.
- Historico de transacoes de milhas e regra academica de conversao.
- Check-in online simples para reservas confirmadas de voos futuros.
- Status de voo publico por numero do voo.
- Painel do funcionario para lista de voos do dia, alteracao de status/portao e notificacao de passageiros.
- Painel administrativo visual com indicadores, ultimas reservas, receita simulada e links para Django Admin.
- Promocoes vindas do banco, com fallback visual quando nao existem promocoes ativas.
- Paginas 404/500 personalizadas.

## Funcionalidades futuras

- Filtros comerciais mais avancados.
- Cancelamento com regras por horario/status.
- Uso de milhas mais detalhado por tarifa.
- Dashboards por perfil com mais acoes operacionais.
- Paginas de erro adicionais e monitoramento.
- Variaveis de ambiente obrigatorias em ambiente publicado.
- Possivel migracao futura de `Voo.origem`/`Voo.destino` para `ForeignKey(Aeroporto)`.
- Possivel migracao futura de `Aeronave.companhia_aerea` para `ForeignKey(CompanhiaAerea)`.

## Tecnologias utilizadas

- Python
- Django 5.2.13
- PostgreSQL via `psycopg2-binary`
- Django Templates
- HTML
- CSS
- JavaScript simples
- Bootstrap via CDN
- Font Awesome via CDN

Nao ha `package.json`; portanto o projeto nao usa React, Vite, TypeScript, Tailwind, ESLint, Vitest ou scripts `npm`.

## Estrutura de pastas

```txt
projeto_aeroporto/
  manage.py
  README.md
  PRD.md
  requirements.txt
  sistema_aeroporto/
    settings.py
    urls.py
    wsgi.py
    asgi.py
  skybridgeapp/
    admin.py
    apps.py
    context_processors.py
    forms.py
    models.py
    tests.py
    urls.py
    views.py
    management/
      commands/
        popular_banco.py
        seed.py
    migrations/
    static/
      css/
      img/
      js/
    templates/
```

## Principais rotas

| Rota | Descricao |
| --- | --- |
| `/` | Landing page principal e busca de voos. |
| `/acesso/` | Pagina intermediaria para login/cadastro. |
| `/cadastro/` | Cadastro real com modais para tipos de usuario. |
| `/login/` | Login real com suporte a `next`. |
| `/logout/` | Logout real. |
| `/senha/redefinir/` | Fluxo de redefinicao de senha. |
| `/senha/alterar/` | Alteracao de senha para usuario logado. |
| `/voos/buscar/` | Resultados da busca de voos. |
| `/voos/<id>/` | Detalhe do voo. |
| `/voos/<id>/selecionar/` | Entrada protegida para selecionar voo. |
| `/voos/<id>/volta/` | Seleciona o voo de volta de uma busca ida e volta. |
| `/voos/<ida_id>/volta/<volta_id>/resumo/` | Resumo da viagem ida e volta com assentos. |
| `/voos/<id>/reservar/` | Cria reserva real. |
| `/voos/<ida_id>/volta/<volta_id>/reservar/` | Cria uma viagem agrupada com reservas de ida e volta. |
| `/reservas/<id>/pagamento/` | Pagamento simulado de reserva ou viagem agrupada. |
| `/reservas/<id>/sucesso/` | Sucesso da reserva apos pagamento. |
| `/reservas/<id>/bilhete/` | Bilhete/comprovante. |
| `/reservas/<id>/check-in/` | Faz check-in online. |
| `/reservas/<id>/cartao-embarque/` | Cartao de embarque simples. |
| `/minhas-viagens/` | Lista de reservas do passageiro. |
| `/notificacoes/` | Notificacoes do passageiro. |
| `/status-voo/` | Consulta publica de status de voo. |
| `/dashboard/passageiro/` | Painel do passageiro. |
| `/dashboard/funcionario/` | Painel operacional do funcionario. |
| `/dashboard/administrador/` | Painel administrativo visual. |
| `/admin/` | Django Admin. |

## Modelos principais

- `UsuarioCustomizado`
- `Passageiro`
- `Funcionario`
- `Administrador` legado
- `Aeroporto`
- `CompanhiaAerea`
- `Aeronave`
- `PortaoEmbarque`
- `Voo`
- `Tarifa`
- `Promocao`
- `Viagem`
- `Reserva`
- `Pagamento`
- `Bilhete`
- `Bagagem`
- `CheckIn`
- `Notificacao`
- `ContaMilhas`
- `TransacaoMilhas`

Observacao: `Administrador` e um model legado mantido apenas por compatibilidade historica. O novo cadastro administrativo usa `UsuarioCustomizado` com `tipo='administrador'`, `is_staff=True` e `is_superuser=True`. No Django Admin, o model legado fica isolado e nao permite criar/editar/excluir registros nem expor a senha.

## Regra academica de milhas

- Passageiro cadastrado recebe conta Sky Pass com saldo inicial de 10.000 milhas.
- Pagamentos por Pix, cartao ou boleto acumulam `1 milha` a cada `R$ 1,00` pago.
- Pagamento por milhas usa `10 milhas` a cada `R$ 1,00` da reserva ou viagem agrupada.
- Se o saldo for insuficiente, a reserva permanece pendente e o usuario recebe feedback amigavel.
- Toda movimentacao gera `TransacaoMilhas` e aparece no painel do passageiro.

## Variaveis de ambiente

O projeto le configuracoes sensiveis via variaveis de ambiente, mantendo fallbacks locais para desenvolvimento.

```powershell
$env:DJANGO_SECRET_KEY="troque-esta-chave"
$env:DJANGO_DEBUG="True"
$env:DJANGO_ALLOWED_HOSTS="127.0.0.1,localhost"
$env:POSTGRES_DB="skybridge"
$env:POSTGRES_USER="postgres"
$env:POSTGRES_PASSWORD="admin"
$env:POSTGRES_HOST="127.0.0.1"
$env:POSTGRES_PORT="5432"
```

Antes de publicar ou compartilhar ambiente real, defina `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS` e as credenciais reais do PostgreSQL fora do codigo.

## Como rodar localmente

### 1. Criar e ativar ambiente virtual

PowerShell:

```powershell
python -m venv ..\meuMundo
..\meuMundo\Scripts\Activate.ps1
```

CMD:

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

### 3. Verificar o projeto

```bash
python manage.py check
```

### 4. Aplicar migrations

```bash
python manage.py migrate
```

### 5. Popular dados de exemplo

```bash
python manage.py popular_banco
```

Para criar tambem contas de demonstracao para a banca:

```bash
python manage.py popular_banco --usuarios-demo
```

Contas criadas por essa opcao:

| Usuario | Tipo | Senha |
| --- | --- | --- |
| `passageiro.demo` | Passageiro | `SkyBridge@123` |
| `funcionario.demo` | Funcionario | `SkyBridge@123` |
| `admin.demo` | Administrador | `SkyBridge@123` |

Para limpar apenas dados de exemplo criados pelo comando:

```bash
python manage.py popular_banco --limpar
```

### 6. Criar superusuario

```bash
python manage.py createsuperuser
```

### 7. Rodar servidor

```bash
python manage.py runserver
```

Acesse:

- Home: `http://127.0.0.1:8000/`
- Cadastro: `http://127.0.0.1:8000/cadastro/`
- Login: `http://127.0.0.1:8000/login/`
- Admin: `http://127.0.0.1:8000/admin/`

## Fluxo recomendado para demonstracao

1. Rode `python manage.py popular_banco --usuarios-demo`.
2. Acesse `/`.
3. Escolha origem, destino, data de ida e, se quiser demonstrar ida e volta, data de volta.
4. Compare datas proximas.
5. Selecione o voo de ida e, quando houver data de volta, selecione tambem o voo de retorno.
6. Acesse `passageiro.demo` ou crie uma conta de passageiro.
7. Escolha assento(s) e confirme a reserva.
8. Simule pagamento.
9. Veja o bilhete.
10. Abra "Minhas viagens".
11. Faca check-in e visualize o cartao de embarque.
12. Consulte status do voo em `/status-voo/`.

## Testes

O projeto possui testes Django cobrindo:

- metadados dos models;
- comando `popular_banco`;
- home e promocoes vindas do banco;
- cadastro por tipo de usuario;
- login/logout/senhas;
- busca real de voos;
- detalhe e selecao de voo;
- reserva real;
- pagamento simulado;
- bilhete;
- area do passageiro;
- check-in;
- status de voo;
- painel do funcionario;
- painel administrativo;
- milhas refinadas;
- pagina 404 personalizada.

Para rodar:

```bash
python manage.py test
```

Para verificar se ha migrations pendentes:

```bash
python manage.py makemigrations --check --dry-run
```

## Boas praticas do projeto

- Use TDD para novas funcionalidades com comportamento ou regra de negocio.
- Rode `python manage.py check` e `python manage.py test` antes de finalizar mudancas relevantes.
- Nao implemente integracoes externas sem escopo claro.
- Nao salve senhas manualmente; use sempre o sistema de autenticacao do Django.
- Mantenha o escopo simples e demonstravel para faculdade.
- Evite copiar textos, marcas ou imagens proprietarias de companhias reais.
"# aeroporto_teste_v" 
