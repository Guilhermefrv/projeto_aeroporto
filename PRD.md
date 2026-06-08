# PRD - Sky Bridge

Documento de estado atual e planejamento funcional do projeto Sky Bridge.

Data de referencia: 2026-06-08

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
      404.html
      500.html
      bilhete.html
      buscar_voos.html
      cadastro.html
      cartao_embarque.html
      dashboard.html
      detalhe_reserva.html
      home.html
      login.html
      minhas_viagens.html
      notificacoes_passageiro.html
      pagamento.html
      painel_admin.html
      painel_funcionario.html
      painel_passageiro.html
      password_change_done.html
      password_change_form.html
      password_reset_complete.html
      password_reset_confirm.html
      password_reset_done.html
      password_reset_email.html
      password_reset_form.html
      password_reset_subject.txt
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
| `/status-voo/` | `status_voo` | `status_voo.html` | Consulta pública de status de voo por código |
| `/voos/buscar/` | `buscar_voos` | `buscar_voos.html` | Busca/listagem real de voos nacionais |
| `/voos/<int:voo_id>/` | `detalhe_voo` | `detalhe_voo.html` | Detalhe real do voo selecionado |
| `/voos/<int:voo_id>/selecionar/` | `selecionar_voo` | - | Exige login e volta ao detalhe do voo |
| `/voos/<int:voo_id>/reservar/` | `criar_reserva` | - | Cria reserva real e redireciona para pagamento |
| `/reservas/<int:reserva_id>/pagamento/` | `pagamento_reserva` | `pagamento.html` | Pagamento simulado de reserva |
| `/reservas/<int:reserva_id>/sucesso/` | `reserva_sucesso` | `reserva_sucesso.html` | Tela final da reserva confirmada |
| `/reservas/<int:reserva_id>/bilhete/` | `bilhete_reserva` | `bilhete.html` | Tela dedicada de bilhete/comprovante |
| `/reservas/<int:reserva_id>/check-in/` | `realizar_checkin` | - | Cria check-in por POST para reserva confirmada futura |
| `/reservas/<int:reserva_id>/cartao-embarque/` | `cartao_embarque` | `cartao_embarque.html` | Cartao de embarque simples |
| `/minhas-viagens/` | `minhas_viagens` | `minhas_viagens.html` | Lista completa de reservas do passageiro |
| `/reservas/<int:reserva_id>/` | `detalhe_reserva` | `detalhe_reserva.html` | Detalhe protegido da reserva |
| `/reservas/<int:reserva_id>/cancelar/` | `cancelar_reserva` | - | Cancela reserva do passageiro por POST |
| `/notificacoes/` | `notificacoes_passageiro` | `notificacoes_passageiro.html` | Central de notificacoes do passageiro |
| `/cadastro/` | `cadastro` | `cadastro.html` | Cadastro real com modais Bootstrap |
| `/login/` | `SkyBridgeLoginView` | `login.html` | Login real usando Django |
| `/logout/` | `SkyBridgeLogoutView` | - | Logout real usando Django |
| `/senha/redefinir/` | `SkyBridgePasswordResetView` | `password_reset_form.html` | Solicita link de redefinicao de senha |
| `/senha/redefinir/enviado/` | `SkyBridgePasswordResetDoneView` | `password_reset_done.html` | Confirma envio das instrucoes |
| `/senha/redefinir/<uidb64>/<token>/` | `SkyBridgePasswordResetConfirmView` | `password_reset_confirm.html` | Define nova senha com token |
| `/senha/redefinir/concluido/` | `SkyBridgePasswordResetCompleteView` | `password_reset_complete.html` | Confirma senha redefinida |
| `/senha/alterar/` | `SkyBridgePasswordChangeView` | `password_change_form.html` | Altera senha de usuario autenticado |
| `/senha/alterar/concluido/` | `SkyBridgePasswordChangeDoneView` | `password_change_done.html` | Confirma troca de senha |
| `/dashboard/` | `dashboard_router` | - | Redireciona conforme tipo de usuario |
| `/dashboard/passageiro/` | `dashboard_passageiro` | `painel_passageiro.html` | Painel protegido do passageiro |
| `/dashboard/funcionario/` | `dashboard_funcionario` | `painel_funcionario.html` | Painel protegido do funcionario |
| `/dashboard/funcionario/voos/<int:voo_id>/atualizar/` | `atualizar_voo_operacional` | - | Atualiza status/portao de voo e notifica passageiros |
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

Observacao: algumas models ja existem para etapas futuras, mas ainda nao possuem fluxo completo de interface. `Reserva`, `Pagamento`, `Bilhete`, `CheckIn`, `ContaMilhas` e `TransacaoMilhas` ja participam do fluxo basico de reserva/pagamento/check-in. `Bagagem` ainda nao possui fluxo completo pela interface.

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

Observacao: quando nao ha promocoes ativas no banco, a Home usa `LANDING_CONTEXT` apenas como fallback visual.

## 5. Autenticacao

- Login real com `LoginView`.
- Logout real com `LogoutView`.
- Login exibe link para cadastro quando o usuario ainda nao tem conta.
- Cadastro iniciado a partir do login preserva o parametro `next` para retomar o fluxo protegido.
- Recuperacao de senha usa views nativas do Django com envio de link por e-mail.
- Em desenvolvimento, e-mails de redefinicao sao exibidos no terminal pelo backend console.
- Usuario autenticado consegue alterar senha informando senha atual e nova senha.
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
- Passageiro possui area "Minhas viagens" com todas as reservas reais da conta.
- Passageiro consegue abrir o detalhe protegido de uma reserva.
- Detalhe da reserva mostra voo, assento, passageiro, status da reserva, status do pagamento, valor e bilhete quando existir.
- Passageiro consegue cancelar reserva de forma simples; o status passa para `cancelada`.
- Passageiro possui pagina dedicada de notificacoes.
- Links do dropdown apontam para areas coerentes: "Minha conta", "Minhas viagens" e "Notificacoes".
- Area de viagens mostra saldo de milhas quando existe conta vinculada.
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
- Quando a rota vem de uma oferta sem data escolhida, a pagina primeiro mostra um seletor de datas navegavel e so lista voos depois que o usuario escolhe um dia.
- Setas da faixa de datas carregam novas janelas via JavaScript/JSON, sem recarregar a pagina inteira.
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

## 12. Bilhete / Comprovante

- Apos pagamento aprovado, o sistema cria automaticamente um `Bilhete`.
- Codigo do bilhete segue formato simples como `TKT-<reserva>-XXXXXX` e permanece unico pelo campo `Bilhete.codigo`.
- A tela de sucesso da reserva mostra o codigo do bilhete quando existir.
- Ha tela dedicada em `/reservas/<int:reserva_id>/bilhete/`.
- A tela dedicada mostra passageiro, voo, assento, codigo da reserva, status, codigo do bilhete, pagamento, valor e dados do trajeto.
- Apenas o passageiro dono da reserva ou staff consegue consultar o bilhete.
- A tela possui botao para voltar para "Minhas viagens".
- A tela de sucesso e o painel do passageiro exibem link "Ver bilhete" quando a reserva possui bilhete emitido.

## 13. Check-in Online

- Passageiro consegue realizar check-in por uma reserva confirmada de voo futuro.
- O sistema cria `CheckIn` com status `realizado`.
- Check-in duplicado e evitado por verificacao de passageiro e voo.
- Reserva pendente, cancelada ou de voo passado nao permite check-in.
- Ha cartao de embarque simples em `/reservas/<int:reserva_id>/cartao-embarque/`.
- O cartao mostra passageiro, documento, voo, origem, destino, partida, chegada, portao, aeronave e assento.
- "Minhas viagens", detalhe da reserva e painel do passageiro exibem acoes de "Fazer check-in" ou "Ver cartao".
- Passageiro nao consegue fazer check-in ou ver cartao de reserva de outro usuario.

## 14. Milhas Refinadas

- Passageiro criado pelo cadastro recebe uma `ContaMilhas` automaticamente.
- Regra academica clara: pagamento comum acumula 1 milha por R$ 1,00.
- Regra academica clara: pagamento por milhas consome 10 milhas por R$ 1,00 da reserva.
- Pagamento por Pix, cartao ou boleto acumula milhas ficticias.
- Pagamento por milhas verifica saldo, debita milhas e registra transacao de resgate.
- Dashboard do passageiro exibe saldo e numero do programa quando ha conta de milhas.
- Dashboard do passageiro exibe historico recente de transacoes de milhas.
- Pagina de pagamento mostra saldo atual, milhas necessarias, saldo apos resgate e milhas acumuladas em pagamento comum.
- Saldo insuficiente recebe mensagem amigavel e mantem a reserva pendente.

## 15. Populacao do Banco

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

## 16. Testes

O arquivo `skybridgeapp/tests.py` cobre:

- metadados das models;
- comando `popular_banco`;
- home e header;
- login/logout;
- cadastro a partir do login;
- redefinicao e alteracao de senha;
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
- tela dedicada de bilhete/comprovante;
- protecao do bilhete por dono da reserva;
- link "Ver bilhete" no painel do passageiro;
- unicidade do codigo do bilhete;
- lista completa de reservas em "Minhas viagens";
- detalhe protegido da reserva;
- bloqueio de acesso a reserva de outro passageiro;
- cancelamento simples de reserva;
- pagina dedicada de notificacoes do passageiro;
- check-in online para reserva confirmada futura;
- bloqueio de check-in duplicado;
- bloqueio de check-in para reserva pendente ou voo passado;
- cartao de embarque simples;
- protecao contra check-in em reserva de outro passageiro;
- links coerentes no dropdown de conta;
- tela de sucesso da reserva apos pagamento aprovado;
- exibicao de reserva no painel do passageiro;
- bloqueio amigavel para usuario sem perfil de passageiro;
- busca pública de status de voo (acessibilidade, busca bem-sucedida normalizada e busca de voo inexistente).
- painel do funcionario real com voos do dia, atualizacao operacional, notificacoes e bloqueio para passageiro.
- painel administrativo com indicadores, receita aprovada, ultimas reservas e links para admin Django.
- promocoes ativas vindas do banco na Home e fallback visual sem promocoes ativas.

## 17. Frontend e UX

- CSS proprio em `home.css`, `cadastro.css`, `login.css`, `paineis.css`, `auth_home.css` e `theme.css`.
- Bootstrap usado em modais, dropdown e toasts.
- Font Awesome usado para icones.
- JavaScript simples usado para Bootstrap Toast e apoio da busca.

## 18. Status de Voo Público

- Rota pública em `/status-voo/`.
- Busca inteligente e robusta por número de voo (desconsiderando maiúsculas/minúsculas, espaços extras e hifens).
- Exibição de origem, destino, horários, portão e status atual com design responsivo e badges coloridos para os diferentes status.
- Mensagem amigável quando o voo não é encontrado.

## 19. Painel do Funcionario Real

- Painel do funcionario lista os voos do dia em `/dashboard/funcionario/`.
- Funcionario altera status do voo entre programado, atrasado, em andamento e cancelado.
- Funcionario altera portao de embarque pela propria interface do painel.
- Portao anterior e liberado e novo portao e marcado como ocupado quando ha troca.
- Passageiros com reservas ativas no voo recebem notificacao automatica.
- Bagagens recentes sao exibidas no painel operacional com passageiro, voo, peso e status.
- Passageiros e outros tipos sem permissao nao conseguem executar a rota operacional.

## 20. Painel Administrativo Mais Apresentavel

- Painel administrativo visual em `/dashboard/administrador/`.
- Administrador ve cards com totais de voos, reservas, passageiros e pagamentos.
- Receita simulada soma apenas pagamentos aprovados.
- Painel exibe quantidade de pagamentos aprovados usada no calculo da receita.
- Links rapidos levam para Django Admin, usuarios, passageiros, funcionarios, voos, reservas, pagamentos, aeroportos, aeronaves e promocoes.
- Ultimas reservas aparecem em tabela com passageiro, voo, assento, status, pagamento e valor.
- Funcionarios continuam bloqueados de acessar o painel administrativo.

## 21. Promocoes Vindas do Banco

- Home busca `Promocao.objects.filter(ativa=True)` para montar cards reais de ofertas.
- Promocoes cadastradas no Django Admin aparecem na landing page.
- Cards exibem rota, titulo, descricao, preco formatado e imagem coerente com o destino.
- Imagens nacionais ja cadastradas para Sao Paulo, Brasilia, Cuiaba, Curitiba, Manaus e Porto Alegre sao reaproveitadas.
- Botao "Ver oferta" dos cards reais leva para a busca de voos com origem e destino da promocao.
- Promocoes repetidas para a mesma origem/destino sao deduplicadas na Home, priorizando o menor preco.
- Quando nao ha promocoes ativas, a Home usa os cards estaticos como fallback visual.
- Dados criados pelo comando `popular_banco` sao compativeis com os cards da Home.

## 22. Melhorias Tecnicas Importantes

- `README.md` atualizado para refletir cadastro, busca, reserva, pagamento, bilhete, check-in, dashboards, promocoes e milhas reais.
- Busca por textos quebrados foi revisada nos arquivos vivos do projeto.
- Model legado `Administrador` foi isolado no Django Admin: nao permite adicionar, editar ou excluir e nao expoe o campo `senha`.
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` e credenciais do PostgreSQL passaram a aceitar variaveis de ambiente com fallback local de desenvolvimento.
- Paginas 404 e 500 personalizadas foram criadas com visual coerente com a landing page.
- Pontos arquiteturais futuros documentados: avaliar `Voo.origem`/`Voo.destino` como `ForeignKey(Aeroporto)` e `Aeronave.companhia_aerea` como `ForeignKey(CompanhiaAerea)`.


# [A Desenvolver]

## Prioridade Recomendada

1. Revisao visual final para apresentacao.
2. Revisao dos dados de demonstracao no banco antes da banca.
3. Opcional: escolha real de assentos.
4. Opcional: fluxo completo de ida e volta.
5. Opcional futuro: migrar campos de texto de voo/aeronave para relacionamentos mais fortes.


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

Fazer uma revisao final de apresentacao: conferir dados do `popular_banco`, criar usuarios de demonstracao, validar o fluxo completo de passageiro, funcionario e administrador, e ajustar apenas polimentos visuais pontuais.

Sugestao de entrega:

1. Rodar `python manage.py popular_banco --limpar` e `python manage.py popular_banco`.
2. Validar busca, reserva, pagamento, bilhete e check-in com um passageiro.
3. Validar alteracao de status/portao com um funcionario.
4. Validar indicadores e links rapidos com um administrador.
