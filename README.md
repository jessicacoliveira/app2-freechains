# Sistema de trocas/empréstimos com Freechains

## Objetivo:
Implementação de um protótipo de aplicação que gerencia, de forma descentralizada, trocas e empréstimos de objetos entre usuários, permitindo publicar anúncios, registrar solicitações, acompanhar transações e avaliar participantes/interações.

## Instruções de uso:
* Todos os arquivos devem ser executado no diretório que contém os executáveis `freechains` e `freechains-host`;
* É necessário ter o `gnome-terminal` instalado;
* Por comodidade, utilize o arq1.txt fornecido para alimentar a aplicação com alguns anúncios;
* ### Em caso de erro durante a execução use rm -rf /tmp/freechains/host05000/ antes de executar novamente
  (Costuma funcionar. Entrar no menu principal e só sair também.)

## Simulação 1
- Inicializa 3 usuários nas portas 5001, 5002 e 5003 que postam anúncios na cadeia. Esses anúncios podem ser visualizados através do menu. Solicitações para eles também podem ser feitas normalmente através do menu.

- Observe que o protótipo normalmente permite que um usuário publique e faça transações com os próprios anúncios para facilitar os testes. Dessa forma, uma solicitação feita pelo próprio usuário também aparece na área de "Ver Solicitações para Meus Anúncios", por exemplo. *Na simulação isso não ocorre*, pois os blocos foram publicados por outros usuários e esses menus são pessoais. Isso reforça que a lógica implementada já suporta múltiplos usuários.

- Na simulação 2 que está sendo implementada, o objetivo é checar com múltiplos usuários o mecanismo de aceite do empréstimo implementado utilizando o consenso do Freechains.

## Funcionalidades:

### Implementadas
1. `Criação de anúncio:` permite ao usuário **criar um ou mais anúncios** para troca ou empréstimo, inserindo os dados pelo **terminal** ou por **arquivo**.
2. `Buscar objetos disponíveis:` oferece buscas por **anúncios disponíveis**, filtrando por **palavra-chave no título**, listando os anúncios pela **reputação do autor** ou pela **ordem do consenso**.
3. `Gerenciamento de anúncios:` exibe todos os **anúncios do usuário**, mostra as **solicitações recebidas** para cada anúncio e permite **aceitar solicitações** de empréstimo (via consenso) ou troca (escolha manual).
4. `Gerenciamento de solicitações:` **exibe as solicitações** feitas pelo usuário, separadas por status: `ativas` (sem bloco de aceite na cadeia), `aceitas` ou `rejeitadas`.
5. `Gerenciamento de transações:` permite **registrar eventos de retirada e devolução** de itens, **visualizar recibos** gerados na cadeia e **registrar avaliações** positivas ou negativas.
6. `Consultar reputação:` permite **consultar a reputação** de outro **usuário** ou a reputação atribuída a um **bloco** específico.
7. `Simulação de login:` gera e registra **chaves públicas/privadas** com base em um nickname fornecido pelo usuário.

### Falta Implementar
1. `Mecanismo de disputa:`;
2. `Testes com uso de timestamp:` punição automática pela aplicação, por exemplo;
3. `Inserção de terceiros na transação:` pontos de troca, armários etc.;
4. `Bootstrapping adequado para novos usuários`;
5. `Visualização das avaliações em forma de relatório`;
6. `Cancelamento de transação`;
7. `Sincronização entre peers`: só funcionaria em simulações;
8. `Tratamento de erros`;
9. `Simulações mais robustas`.

### Fora de Escopo
1. `Interface gráfica`;
2. `Sistema de login`.

### Ferramentas utilizadas
1. Sistema operacional `Linux`;
2. `Freechains` v.0.10.1;
3. `Python3`;
4. Bibliotecas que não precisam de instalação prévia: `subprocess`, `json` e `time`.

# Detalhes de Funcionamento (em construção)

## Menus

- `Criar anúncios:` criação manual ou carregamento de arquivo;
- `Busca de Objetos:` visualização de anúncios, curtidas e denúncias de anúncios e *realizar solicitações*;
- `Meus Anúncios:` área de gerenciamento pessoal dos anúncios que permite a *realizar aceites*;
- `Minhas Solicitações:` área de visualização das solicitações que foram feitas (sem resposta, aceitas e rejeitadas);
- `Minhas Transações:` permite gerenciar transações de *retirada* e *devolução* de aceites em aberto, além de gerar recibos e visualizá-los;
- `Consultar Reputação:` permite checar a reputação de usuários e blocos

## Blocos internos da aplicação

Os blocos internos da aplicação são armazenados como strings no formato JSON no payload de um bloco de conteúdo padrão do Freechains. Foram definidos sete tipos de blocos, cada um representando um estágio no ciclo da transação:

### Anúncio
Início de uma transação.

1. `Tipo Bloco:` 1
2. `Título:` informado pelo usuário
3. `Descrição:` informado pelo usuário
4. `Tipo Transação:` Troca ou Empréstimo, informado pelo usuário
5. `Prazo:` 0 para Troca ou valor em horas para Empréstimo

### Solicitação
Manifestação de interesse pelo objeto

1. `Tipo Bloco:` 2
2. `Solicitando:` ID hash do anúncio ao qual se refere
3. `Proposta:` mensagem do solicitante
4. `Contato:` informado pelo solicitante

### Aceite
Confirmação por parte do anunciante.

1. `Tipo Bloco:` 3
2. `Solicitação:` ID hash da solicitação escolhida 
3. `Anúncio:` ID hash do anúncio alvo da solicitação
4. `Mensagem:` informado pelo anunciante
5. `Prazo:` o mesmo da solicitação

### Retirada
Registro da retirada do item pelo solicitante.

1. `Tipo Bloco:` 4
2. `Aceite:` ID hash do Aceite criado para essa transação
3. `Mensagem:` informada pelo usuário

### Devolução
Registro da devolução do item ao anunciante. Usado apenas nas transações de empréstimo.

1. `Tipo Bloco:` 5
2. `Aceite:` ID hash do Aceite criado para essa transação
3. `Retirada:` ID hash do bloco de retirada 
4. `Mensagem:` informada pelo usuário

### Recibo
Consolidação da transação. 

1. `Tipo Bloco:` 6
2. `Anúncio:` ID hash do bloco de anúncio da transação
3. `Solicitação:` ID hash do bloco de Aceite
4. `Aceite:` ID hash do bloco de Aceite
5. `Retirada:` ID hash do bloco de Retirada
6. `Devolução:` ID hash do bloco de Devolução

### Avaliação
Feedback sobre a interação. Sempre associado a um bloco de like/dislike.

1. `Tipo Bloco:` 0
2. `Referência Interação:` ID hash do bloco de like/dislike
3. `Referência Bloco:` ID hash do bloco avaliado
4. `Referência user:` ID hash do usuário do bloco que foi avaliado
5. `Mensagem:` motivo da avaliação

## Regras da aplicação:

* Anúncios deixam de estar disponíveis quando associados a um bloco de aceite. O mesmo para uma solicitação.
* A escolha de uma solicitação é automática (escolha do Consenso do Freechains) para anúncios de Empréstimo. Para anúncio de Troca, a escolha é feita manualmente por quem o publicou. A escolha gera um bloco de aceite.
* Um bloco de aceite fica disponível até que um bloco de recibo (que indica finalização da transação) seja associado a ele.
* A opção de retirada só fica ativa para aceites disponíveis e se não houver um bloco de retirada já associado a um aceite disponível.
* A opção de devolução só fica disponível se o anúncio de referência for de empréstimo e se houver sido registrado um bloco de retirada para ele.
* Um bloco de recibo é postado na cadeia quando uma transação é finalizada. Para trocas, o recibo é "emitido" após a retirada. Para empréstimos, após a devolução.
* Uma avaliação pode ser feita a qualquer momento, por qualquer motivo. Como é composta de 2 blocos (like/dislike + bloco textual para o motivo), custa 2 reps. Denúncias seguem o mesmo modelo e também custam 2 reps. Curtir anúncios custa 1 bloco de like/dislike normal, ou seja, 1 rep.
