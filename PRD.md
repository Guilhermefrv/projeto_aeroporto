# PRD - Sky Bridge

Documento de estado atual e planejamento funcional do projeto Sky Bridge.

Data de referencia: 2026-06-02

## Visao Geral

O Sky Bridge e um sistema academico de aeroporto/companhia aerea desenvolvido em Django. O projeto ja possui uma base funcional para autenticacao, cadastro de usuarios por tipo, landing page, busca real de voos nacionais, dashboards iniciais e populacao de dados de exemplo.

O objetivo daqui em diante e transformar essa base em um fluxo completo e apresentavel para uma demonstracao de faculdade:

1. Buscar voos nacionais.
2. Selecionar um voo.
3. Fazer login ou cadastro.
4. Criar uma reserva.
5. Simular pagamento.
6. Emitir bilhete/comprovante.
7. Consultar a viagem em "Minha conta".
8. Fazer check-in simples.
9. Consultar status de voo.
10. Operar alteracoes basicas pelo painel de funcionario/admin.

O escopo deve permanecer simples, sem copiar a complexidade de sites reais como LATAM, TAP ou outros portais de companhias aereas. Essas referencias servem como guia de jornada: busca, selecao, reserva, pagamento, bilhete, minhas viagens, check-in e status de voo.

## Estrutura Atual do Projeto

```txt
projeto_aeroporto/
  manage.py
  README.md
  requirements.txt
  sistema_aeroporto/
    settings.py
    urls.py
    asgi.py
    wsgi.py
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
        seed.py
        popular_banco.py
    migrations/
      0001_initial.py
      0002_aeroporto_companhiaaerea_contamilhas_pagamento_and_more.py
      0003_reserva_pagamento.py
    templates/
      auth_home.html
      buscar_voos.html
      cadastro.html
      dashboard.html
      home.html
      login.html
      pagamento.html
      painel_admin.html
      painel_funcionario.html
      painel_passageiro.html
      reserva_sucesso.html
    static/
      css/
        auth_home.css
        cadastro.css
        home.css
        login.css
        paineis.css
        theme.css
      js/
        main.js
```

## Tecnologias Identificadas

- Python
- Django
- Django Templates
- HTML
- CSS
- JavaScript simples
- Bootstrap via CDN
- Font Awesome via CDN
- PostgreSQL
- Django TestCase/SimpleTestCase

Nao ha `package.json`, build frontend, React, Vite, TypeScript, Tailwind, ESLint ou Vitest no projeto atual.

## Rotas Atuais

| Rota | View | Template | Estado |
| --- | --- | --- | --- |
| `/` | `home` | `home.html` | Landing page principal funcional |
| `/acesso/` | `auth_home` | `auth_home.html` | Pagina intermediaria para login/cadastro |
| `/voos/buscar/` | `buscar_voos` | `buscar_voos.html` | Busca/listagem real de voos nacionais |
| `/voos/<int:voo_id>/` | `detalhe_voo` | `detalhe_voo.html` | Detalhe real do voo selecionado |
| `/voos/<int:voo_id>/selecionar/` | `selecionar_voo` | - | Exige login e volta ao detalhe do voo |
| `/voos/<int:voo_id>/reservar/` | `criar_reserva` | - | Cria reserva real e redireciona para pagamento |
| `/reservas/<int:reserva_id>/pagamento/` | `pagamento_reserva` | `pagamento.html` | Pagamento simulado de reserva |
| `/reservas/<int:reserva_id>/sucesso/` | `reserva_sucesso` | `reserva_sucesso.html` | Tela final da reserva confirmada |
| `/cadastro/` | `cadastro` | `cadastro.html` | Cadastro real com modais Bootstrap |
| `/login/` | `SkyBridgeLoginView` | `login.html` | Login real usando Django |
| `/logout/` | `SkyBridgeLogoutView` | - | Logout real usando Django |
| `/dashboard/` | `dashboard_router` | - | Redireciona conforme tipo de usuario |
| `/dashboard/passageiro/` | `dashboard_passageiro` | `painel_passageiro.html` | Painel protegido do passageiro |
| `/dashboard/funcionario/` | `dashboard_funcionario` | `painel_funcionario.html` | Painel protegido do funcionario |
| `/dashboard/administrador/` | `dashboard_administrador` | `painel_admin.html` | Painel protegido do administrador |
| `/admin/` | Django Admin | Django Admin | Admin padrao do Django |

# [Já Desenvolvido]

## 1. Base Django e Configuracao

- Projeto Django organizado em `sistema_aeroporto` e app principal `skybridgeapp`.
- Configuracao para PostgreSQL em `settings.py`.
- `AUTH_USER_MODEL` configurado para `skybridgeapp.UsuarioCustomizado`.
- Apps, middlewares e context processors de auth/session/messages configurados.
- Context processor proprio para notificacoes nao lidas.
- Arquivos estaticos organizados em CSS e JavaScript.

## 2. Models Principais

Models existentes:

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
- `Reserva`
- `Pagamento`
- `Bilhete`
- `Bagagem`
- `CheckIn`
- `Notificacao`
- `ContaMilhas`
- `TransacaoMilhas`

Observacao: algumas models ja existem para etapas futuras, mas ainda nao possuem fluxo completo de interface. `Reserva`, `Pagamento`, `Bilhete`, `ContaMilhas` e `TransacaoMilhas` ja participam do fluxo basico de reserva/pagamento. `CheckIn` e `Bagagem` ainda nao possuem fluxo completo pela interface.

## 3. Admin Django

- Models registradas em `skybridgeapp/admin.py`.
- `UsuarioCustomizado` usa `UserAdmin`.
- Filtros e buscas basicas configurados para varias entidades.
- Admin ja permite cadastrar/visualizar aeroportos, voos, tarifas, promocoes, reservas, pagamentos e demais entidades.

## 4. Landing Page Principal

- Home em `/`.
- Visual inspirado em experiencia de companhias aereas.
- Header com logo, navegacao, login ou menu de conta.
- Hero promocional.
- Busca visual e funcional de voos nacionais.
- Cards de ofertas nacionais.
- Secoes de beneficios.
- Footer.
- Escopo de voos ajustado para Brasil.

Ponto pendente: parte das ofertas ainda vem de `LANDING_CONTEXT` em `views.py`, nao diretamente de `Promocao` no banco.

## 5. Autenticacao

- Login real com `LoginView`.
- Logout real com `LogoutView`.
- Mensagens de login/logout exibidas como Bootstrap Toast.
- Redirecionamento por tipo:
  - passageiro vai para `/`;
  - funcionario vai para `/dashboard/funcionario/`;
  - administrador vai para `/dashboard/administrador/`.
- Usuario anonimo ve botao "Fazer login".
- Usuario logado ve menu de conta no header.

## 6. Cadastro de Usuarios

- Cadastro real em `/cadastro/`.
- Interface com tres cards e modais Bootstrap:
  - Passageiro;
  - Funcionario;
  - Administrador.
- Forms separados:
  - `CadastroPassageiroForm`;
  - `CadastroFuncionarioForm`;
  - `CadastroAdministradorForm`.
- Senhas salvas com hash seguro via Django.
- Passageiro cria `UsuarioCustomizado` + perfil `Passageiro`.
- Funcionario cria `UsuarioCustomizado` + perfil `Funcionario`.
- Administrador cria `UsuarioCustomizado` com `is_staff=True`.
- Model legado `Administrador` nao e usado para novo cadastro.

## 7. Dashboards por Tipo

- Dashboard roteador em `/dashboard/`.
- Painel do passageiro protegido.
- Painel do funcionario protegido.
- Painel do administrador protegido.
- Cada tipo de usuario e redirecionado para sua area.
- Dashboards de tipo errado sao bloqueados por verificacoes simples em `request.user.tipo`.

Estado atual:

- Passageiro ve dados basicos, reservas recentes, notificacoes e atalhos.
- Funcionario ve voos, portoes e bagagens em formato inicial.
- Administrador ve cards de contagem basica.

## 8. Busca Real de Voos Nacionais

- Formulario `BuscaVooForm` em `forms.py`.
- Busca publica por GET em `/voos/buscar/`.
- Campos:
  - origem;
  - destino;
  - data de ida;
  - data de volta visual/preservada;
  - passageiros;
  - cabine/classe;
  - codigo promocional visual.
- Origem e destino usam aeroportos reais do banco.
- JavaScript em `static/js/main.js` ajuda a filtrar destinos conforme origem.
- Busca consulta `Voo` e `Tarifa`.
- Filtra por:
  - origem;
  - destino;
  - data de partida;
  - status `programado`;
  - classe/tarifa ativa, quando selecionada.
- Exibe menor tarifa ativa como "preco a partir de".
- Mostra sugestoes proximas quando nao ha voo na data exata.
- Mostra faixa de datas flexiveis.
- Mostra rotas disponiveis quando a combinacao nao existe.

## 9. Fluxo Selecionar Voo

- Botao "Selecionar voo" da listagem agora aponta para uma rota real.
- Rota protegida `selecionar_voo` exige login antes de seguir.
- Usuario anonimo e redirecionado para `/login/` com `next`.
- Usuario logado volta para o detalhe do voo selecionado.
- Pagina de detalhe do voo exibe origem, destino, data, horarios, status, aeronave, portao, classe e preco.
- Detalhe do voo permite ajustar quantidade simples de passageiros.
- Preco exibido usa a tarifa ativa da classe selecionada ou a menor tarifa ativa disponivel.
- Total estimado e calculado com base na quantidade de passageiros.

## 10. Reserva Real

- Botao "Continuar para reserva" no detalhe do voo cria uma `Reserva` real.
- Reserva e associada ao `Passageiro` logado.
- Assento simples e gerado automaticamente em formato como `1A`, `1B`, `2A`.
- Status inicial da reserva e `pendente`, pois a confirmacao final depende do pagamento simulado.
- Apos criar a reserva, o usuario e redirecionado para a pagina de pagamento.
- Reserva criada aparece no painel do passageiro em "Minhas viagens".
- Usuarios autenticados sem perfil de passageiro recebem mensagem amigavel e nao criam reserva.

## 11. Pagamento Simulado

- Pagina de pagamento em `/reservas/<int:reserva_id>/pagamento/`.
- Acesso protegido por login.
- Apenas o passageiro dono da reserva ou staff pode acessar o pagamento.
- Exibe resumo da reserva, voo, passageiro, cabine, quantidade, assento e valor total.
- Metodos visuais disponiveis:
  - Pix;
  - Cartao;
  - Boleto;
  - Milhas.
- Confirmacao do formulario cria ou atualiza `Pagamento`.
- Pagamento aprovado altera a reserva para `confirmada`.
- Reserva sem pagamento aprovado nao acessa a tela final de sucesso.
- Valor total usa a tarifa ativa da classe escolhida ou a menor tarifa ativa disponivel.

## 12. Bilhete Automatico Inicial

- Apos pagamento aprovado, o sistema cria automaticamente um `Bilhete`.
- Codigo do bilhete segue formato simples como `TKT-<reserva>-XXXXXX`.
- A tela de sucesso da reserva mostra o codigo do bilhete quando existir.

Ponto pendente: ainda falta uma tela dedicada de bilhete/comprovante para consulta posterior.

## 13. Milhas Basicas

- Passageiro criado pelo cadastro recebe uma `ContaMilhas` automaticamente.
- Pagamento por Pix, cartao ou boleto acumula milhas ficticias.
- Pagamento por milhas verifica saldo, debita milhas e registra transacao de resgate.
- Dashboard do passageiro exibe saldo e numero do programa quando ha conta de milhas.

Ponto pendente: a experiencia de milhas ainda e simples e pode ser refinada em etapas futuras.

## 14. Populacao do Banco

- Comando principal: `python manage.py popular_banco`.
- Comando delega para `seed`.
- Cria aeroportos brasileiros, companhias, aeronaves, portoes, voos, tarifas e promocoes.
- Cria malha nacional ate o fim do ano atual.
- Usa `update_or_create` e estrategia idempotente.
- Possui opcao `--limpar` para remover dados de exemplo sem apagar usuarios reais.

Aeroportos principais:

- GRU - Sao Paulo
- GIG - Rio de Janeiro
- BSB - Brasilia
- REC - Recife
- SSA - Salvador
- MAO - Manaus
- BEL - Belem
- CWB - Curitiba
- POA - Porto Alegre
- CGB - Cuiaba

## 15. Testes

O arquivo `skybridgeapp/tests.py` cobre:

- metadados das models;
- comando `popular_banco`;
- home e header;
- login/logout;
- cadastro por tipo;
- dashboards protegidos;
- busca de voos;
- filtros de origem/destino/data/classe;
- sugestoes de datas proximas;
- preservacao dos filtros GET.
- detalhe de voo;
- selecao de voo com login obrigatorio e `next`;
- exibicao de tarifa real no detalhe.
- criacao real de reserva;
- pagamento simulado por Pix;
- pagamento com milhas;
- bloqueio de pagamento com saldo insuficiente;
- acumulo de milhas em pagamento comum;
- geracao automatica de bilhete;
- tela de sucesso da reserva apos pagamento aprovado;
- exibicao de reserva no painel do passageiro;
- bloqueio amigavel para usuario sem perfil de passageiro.

## 16. Frontend e UX

- CSS proprio em `home.css`, `cadastro.css`, `login.css`, `paineis.css`, `auth_home.css` e `theme.css`.
- Bootstrap usado em modais, dropdown e toasts.
- Font Awesome usado para icones.
- JavaScript simples usado para Bootstrap Toast e apoio da busca.

# [A Desenvolver]

## Prioridade Recomendada

1. Bilhete/comprovante dedicado.
2. Minha conta/minhas viagens.
3. Check-in online.
4. Status de voo publico.
5. Painel do funcionario real.
6. Painel administrativo mais apresentavel.
7. Promocoes vindas do banco.
8. Milhas refinadas.
9. Melhorias tecnicas finais.

## 1. Bilhete / Comprovante

Prioridade: alta.

Estado atual: a model `Bilhete` ja e gerada automaticamente apos pagamento aprovado, e o codigo aparece na tela de sucesso da reserva. Ainda falta uma tela propria de bilhete/recibo.

Implementar:

- Tela de bilhete/recibo.
- Mostrar passageiro, voo, assento, codigo da reserva e status.
- Botao para voltar para "Minhas viagens".

Criterios de aceite:

- Bilhete pode ser consultado pelo passageiro dono da reserva.
- Codigo do bilhete e unico.

## 2. Minha Conta / Minhas Viagens

Prioridade: alta.

Estado atual: o passageiro ja possui dashboard, mas ele ainda precisa virar uma area util de jornada.

Implementar:

- Listar reservas do passageiro.
- Ver detalhe da reserva.
- Ver bilhete.
- Ver status do pagamento.
- Cancelar reserva de forma simples.
- Mostrar notificacoes.
- Mostrar saldo de milhas, se existir.

Criterios de aceite:

- Passageiro visualiza suas reservas reais.
- Passageiro nao acessa reservas de outro usuario.
- Cancelamento altera status da reserva.
- Links do dropdown "Minha conta", "Minhas viagens" e "Notificacoes" apontam para areas coerentes.

## 3. Check-in Online

Prioridade: media/alta.

Estado atual: a model `CheckIn` existe e ha botao visual no painel, mas sem fluxo real.

Implementar:

- Botao "Fazer check-in" em reserva confirmada.
- Permitir check-in apenas para voo futuro.
- Criar `CheckIn`.
- Gerar cartao de embarque simples.
- Atualizar dashboard do passageiro.

Criterios de aceite:

- Reserva confirmada de voo futuro permite check-in.
- Check-in duplicado e evitado.
- Cartao de embarque exibe passageiro, voo, horario, portao e assento.

## 4. Status de Voo Publico

Prioridade: media.

Estado atual: o header possui "Status de voo", mas ainda e placeholder.

Implementar:

- Pagina publica `/status-voo/`.
- Buscar por numero do voo.
- Mostrar origem, destino, horarios, portao e status.
- Funcionario/admin podem alterar status.

Criterios de aceite:

- Usuario anonimo consegue consultar status por numero de voo.
- Voos inexistentes exibem mensagem amigavel.
- Alteracao de status feita por funcionario/admin aparece na consulta publica.

## 5. Painel do Funcionario Real

Prioridade: media.

Estado atual: o painel do funcionario mostra dados iniciais, mas ainda nao executa operacoes reais.

Implementar:

- Lista de voos do dia.
- Alterar status: programado, atrasado, em andamento, cancelado.
- Alterar portao.
- Ver bagagens.
- Criar notificacao para passageiros afetados.

Criterios de aceite:

- Funcionario altera status/portao de voo.
- Passageiros com reserva no voo recebem notificacao.
- Funcionario nao acessa painel administrativo.

## 6. Painel Administrativo Mais Apresentavel

Prioridade: media.

Estado atual: admin Django resolve a administracao tecnica, e o painel visual possui estatisticas basicas.

Implementar:

- Cards com total de voos, reservas, passageiros e pagamentos.
- Links rapidos para admin Django.
- Lista de ultimas reservas.
- Receita simulada por pagamentos aprovados.

Criterios de aceite:

- Administrador ve indicadores importantes para apresentacao.
- Links levam para rotas/admin corretos.
- Receita usa pagamentos aprovados.

## 7. Promocoes Vindas do Banco

Prioridade: media.

Estado atual: a landing page ainda usa muitos dados estaticos em `LANDING_CONTEXT`.

Implementar:

- Buscar `Promocao.objects.filter(ativa=True)` na Home.
- Montar cards de promocao reais.
- Criar fallback visual caso nao existam promocoes ativas.
- Reaproveitar dados criados pelo `popular_banco`.

Criterios de aceite:

- Promocoes cadastradas no admin aparecem na Home.
- Home nao quebra quando nao ha promocoes.
- Cards continuam nacionais e visualmente consistentes.

## 8. Milhas Refinadas

Prioridade: baixa/media.

Estado atual: conta de milhas, acumulo e resgate ja existem de forma simples no fluxo de cadastro/pagamento.

Implementar simples:

- Melhorar mensagens e visual do uso de milhas.
- Mostrar historico de transacoes no dashboard.
- Definir regra academica clara de conversao entre reais e milhas.
- Manter feedback amigavel quando o saldo for insuficiente.

Criterios de aceite:

- Passageiro entende saldo, historico e impacto do pagamento com milhas.
- Transacoes aparecem no painel.
- Regras ficam simples e demonstraveis.

## 9. Melhorias Tecnicas Importantes

Prioridade: media antes da apresentacao final.

Implementar ou revisar:

- Atualizar `README.md`, pois esta desatualizado e ainda diz que cadastro/busca sao visuais.
- Corrigir textos com caracteres quebrados no codigo/templates, como `FuncionÃ¡rio`.
- Remover, aposentar ou isolar a model legada `Administrador`, pois ela guarda senha em texto puro.
- Avaliar migrar `Voo.origem` e `Voo.destino` de texto para `ForeignKey(Aeroporto)` futuramente.
- Avaliar migrar `Aeronave.companhia_aerea` de texto para `ForeignKey(CompanhiaAerea)` futuramente.
- Mover `SECRET_KEY` e credenciais do banco para variaveis de ambiente antes de publicar.
- Criar paginas 404/erro simples e bonitas.

Criterios de aceite:

- Documentacao reflete o estado real do projeto.
- Projeto nao exibe textos quebrados.
- Dados sensiveis nao ficam expostos em codigo antes de publicacao.
- Erros comuns possuem tela apresentavel.

## Fluxo MVP Para Apresentacao

Fluxo recomendado para demonstrar o sistema inteiro:

1. Abrir a Home.
2. Buscar um voo nacional.
3. Comparar datas proximas.
4. Selecionar voo.
5. Fazer login ou criar conta de passageiro.
6. Confirmar reserva.
7. Simular pagamento.
8. Emitir bilhete.
9. Abrir "Minhas viagens".
10. Fazer check-in.
11. Consultar status do voo.
12. Entrar como funcionario e alterar status/portao.
13. Mostrar notificacao no painel do passageiro.
14. Entrar como administrador e mostrar indicadores gerais.

## Regras de Escopo

Manter simples:

- Somente voos nacionais no Brasil.
- Sem integracao real com pagamento.
- Sem reserva de assentos complexa.
- Sem API externa.
- Sem IA obrigatoria.
- Sem carrinho ou pedido complexo.
- Sem pacote/hotel/carro real nesta fase.
- Sem permissao avancada alem de verificacoes por tipo de usuario.

## Estrategia de Implementacao

Para funcionalidades com comportamento ou regra de negocio, seguir TDD:

1. Definir comportamento esperado.
2. Criar teste que falha.
3. Implementar o minimo para passar.
4. Refatorar mantendo testes passando.

Priorizar testes de comportamento do usuario:

- navegacao;
- formularios;
- validacoes;
- filtros;
- login/logout;
- reserva;
- pagamento;
- check-in;
- protecao por tipo de usuario.

## Proximo Passo Recomendado

Implementar a tela dedicada de bilhete/comprovante, porque pagamento e bilhete automatico ja existem, mas o usuario ainda nao tem uma pagina propria para consultar o comprovante depois.

Sugestao de primeira entrega:

1. Criar rota para visualizar bilhete por reserva ou por codigo.
2. Exigir login e garantir que apenas o dono da reserva ou staff acesse.
3. Mostrar dados do passageiro, voo, assento, status, pagamento e codigo do bilhete.
4. Adicionar link "Ver bilhete" no painel do passageiro e na tela de sucesso.
5. Manter o layout simples e apresentavel para demonstracao.
