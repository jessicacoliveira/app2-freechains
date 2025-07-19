import func3 as fc
import subprocess

canal = "#Burgo66"
key_pub = ""
key_pvt = ""
arquivo = "arq1.txt"

# Inicia servidor
fc.inicializa()

def clear():
    subprocess.call("clear", shell=True)

def menuPrincipal():
    print("""
=======================================
            Menu do Usuário
=======================================
1 - Criar Anúncio
2 - Buscar Objetos Disponíveis
3 - Meus Anúncios
4 - Minhas Solicitações
5 - Minhas Transações
6 - Sincronizar com a Rede
7 - Consultar Reputação
0 - Sair
""")

# Referente à opção 1 do menuPrincipal 
def menuCriarAnuncios():
        print("""
=======================================
            Menu de Anúncios
=======================================
1 - Criar pelo Terminal
2 - Ler por Arquivo
0 - Voltar
""")

# Referente à opção 2 do menuPrincipal 
def menuBusca():
    print("""
=======================================
            Menu de Busca
=======================================
1 - Exibir Anúncios Disponíveis (Consenso)
2 - Buscar Anúncio por palavra-chave no Título
3 - Exibir Anúncios Disponíveis por Reputação do Autor (filtro)
4 - Realizar Solicitação
5 - Curtir Anúncio
6 - Denunciar Anúncio
0 - Voltar
""")

# Referente à opção 3 do menuMeusAnúncios
def menuMeusAnuncios():
    print("""
=======================================
            Meus Anúncios
=======================================
1 - Ver Meus Anúncios Disponíveis
2 - Ver Solicitações para Meus Anúncios
3 - Aceitar Solicitação para Empréstimo (por consenso)
4 - Escolher Solicitação para Troca (manual)
0 - Voltar
""")

# Referente à opção 4 do menuPrincipal
def menuMinhasSolicitacoes():
    print("""
=======================================
          Minhas Solicitações
=======================================
1 - Ver Solicitações Ativas
2 - Ver Solicitações Aceitas
3 - Ver Solicitações Rejeitadas
0 - Voltar
""")

# Referente à opção 5 do menuPrincipal
def menuMinhasTransacoes():
    print("""
=======================================
           Minhas Transações
=======================================
1 - Registrar Retirada
2 - Registrar Devolução
3 - Exibir Recibos da Cadeia
4 - Registrar uma Avaliacao
0 - Voltar
""")

# Opção 6 não tem menu

# Referente à opção 7 do menuPrincipal
def menuReputacao():
    print("""
=======================================
       Consultar Reputação
=======================================
1 - Ver Reputação de Outro Usuário 
2 - Ver Reputação de Um Bloco 
0 - Voltar
""")

# Geração inicial de chave
nickname = ""
while nickname == '':
    nickname = input("Digite seu nickname: ").strip()
    if nickname:
        key_pub, key_pvt = fc.criarPubpvt(nickname)
        print("Chave pública:", key_pub)
        print("Chave privada:", key_pvt)
        print("Chave criada com sucesso. ")
    else:
        print("Nickname inválido.")

fc.joinCanal(key_pub, canal)
fc.getKeys (key_pvt, key_pub)
#input("Pressione Enter para continuar...")

# Início do sistema
print("Carregando possiveis dados salvos de execucao anterior. Aguarde...")
#fc.atualizaEstadoTudo (canal, key_pub)
#fc.atualizarEstadoAnuncios(canal)
while True:
    clear()
    rep = fc.getUserRep(canal, key_pub)
    print(f"Olá, {nickname}.")
    print(f"Sua reputação atual é: {rep}")
    menuPrincipal()
    opcao = input("Escolha uma opção: ").strip()

    if opcao == "1": # Criar anúncio
        while True:
            clear()
            menuCriarAnuncios()
            print("SUGESTAO: utilize o arquivo de nome arq1.txt")
            subopcao = input("Escolha uma opção: ").strip()
            if subopcao == "1":
                clear()
                titulo = input("Digite o titulo do anuncio: ").strip()
                descricao = input("Digite a descricao do anuncio: ").strip()
                tipo_transacao = int(input("Digite 1 para emprestimo e 2 para troca: ").strip())
                if tipo_transacao == 1:
                    tipo_transacao = "Emprestimo"
                    prazo = input("Digite o prazo (horas): ").strip()
                else:
                    tipo_transacao = "Troca"
                    prazo = "0"
                print("Processando...\n")
                hash_anuncio = fc.criaAnuncio (canal, titulo, descricao, tipo_transacao, prazo, key_pvt)
                print(f"\nAnúncio {hash_anuncio} criado com sucesso!\n")
                input("Pressione Enter para voltar...")
                
            elif subopcao == "2":
                clear()
                arquivo = input("Informe o arquivo de anúncios: ").strip()
                print("Lendo arquivo...\n")
                fc.readFile(canal, arquivo, key_pvt)
                #fc.atualizarEstadoAnuncios(canal)
                print("\nAnúncio(s) criado(s) com sucesso!\n")
                input("Pressione Enter para voltar...")
                clear()
            
            elif subopcao == "0":
                break
                
            else:
                print("\nOpção inválida.\n")

    elif opcao == "2": #Acessa Menu de Busca
        clear()
        while True:
            clear()
            menuBusca()
            subopcao = input("Escolha uma opção: ").strip()

            if subopcao == "1":
                clear()
                print("Processando...\n")
                fc.printAnunciosDisponiveis(canal)
                input("\nPressione Enter para continuar...")

            elif subopcao == "2":
                keyword = input("Digite a palavra-chave: ").strip()
                clear()
                print("Processando...\n")
                fc.printBuscaTitulo(canal, keyword)
                input("\nPressione Enter para continuar...")
                
            elif subopcao == "3":
                clear()
                print("Processando...\n")
                fc.printAnunciosOrdenadosRepAutor(canal)
                input("\nPressione Enter para continuar...")

            elif subopcao == "4":
                hash_post = input("Informe o hash do anúncio (ou ENTER para cancelar): ").strip()
                if not hash_post:
                    break
                mensagem = input("Digite uma proposta para o anunciante: ").strip()
                contato = input("Informe um meio de contato (email ou telefone): ").strip()
                print("Processando...\n")
                resultado = fc.placeSolicitacao(canal, hash_post, key_pvt, mensagem, contato)
                fc.atualizarEstadoSolicitacoes(canal, key_pub)
                print(f"Solicitação {resultado} registrada com sucesso!")
                input("\nPressione Enter para continuar...")

            # Registra um like simples
            elif subopcao == "5":
                hash_post = input("Informe o hash do anúncio (ou ENTER para cancelar): ").strip()
                if not hash_post:
                    break
                ID = fc.like(canal, hash_post, key_pvt)
                print("Processando...\n")
                fc.atualizarEstadoAnuncios(canal)
                print(f"Curtida em {ID} registrada!")
                input("\nPressione Enter para continuar...")
                
            # Registra um dislike com avaliação
            elif subopcao == "6":
                hash_post = input("Informe o hash do anúncio (ou ENTER para cancelar): ").strip()
                if not hash_post:
                    break
                mensagem = input("Informe o motivo da denúncia: ").strip()
                ID = fc.registrarAvaliacao (canal, hash_post, mensagem, -1, key_pvt)
                print("Processando...\n")
                fc.atualizarEstadoAnuncios(canal)
                print(f"Denúncia {ID} registrada!")
                input("\nPressione Enter para continuar...")

            elif subopcao == "0":
                break
            else:
                print("\nOpção inválida.\n")
    elif opcao == "4": #Menu Minhas Solicitações
        clear()
        while True:
            clear()
            menuMinhasSolicitacoes()
            subopcao = input("Escolha uma opção: ").strip()
            if subopcao == "1":
                fc.printSolicitacoesDisponiveis(canal)
                input("\nPressione Enter para continuar...")
                
            elif subopcao == "2":
                fc.printSolicitacoesAceitas(canal)
                input("\nPressione Enter para continuar...")
                
            elif subopcao == "3":
                fc.printSolicitacoesRejeitadas(canal)
                input("\nPressione Enter para continuar...")
            
            elif subopcao == "0":
                break
                
            else:
                print("\nOpção inválida.\n")
    
    elif opcao == "3": #Menu Meus Anúncios
        clear()

        while True:
            clear()
            menuMeusAnuncios()
            subopcao = input("Escolha uma opção: ").strip()
            if subopcao == "1":
                print("Processando...\n")
                fc.printAnunciosDisponiveisAutor(canal, key_pub)
                input("\nPressione Enter para continuar...")
                
            elif subopcao == "2":
                print("Processando...\n")
                fc.printSolicitacoesAnunciosDisponiveis (canal, key_pub)
                input("\nPressione Enter para continuar...")
                
            elif subopcao == "3":
                print("Buscando solicitacoes de emprestimo para seus anuncios. Aguarde...")
                fc.atualizarEmprestimo(canal, key_pub, key_pvt)
                
                input("\nPressione Enter para continuar...")
            
            elif subopcao == "4":
                print("Processando...\n")
                fc.printSolicitacoesTrocaAnunciosDisponiveis(canal, key_pub)
                hash_post = input("Informe o hash da solicitacao escolhida: ").strip()
                mensagem = input("Digite uma mensagem para o solicitante: ").strip()
                print("Registrando o aceite. Aguarde...")
                resultado = fc.aceitarSolicitacao(canal, hash_post, key_pvt, mensagem, 0)
                fc.atualizarEstadoAceites(canal)
                print(f"Aceite {resultado} registrado com sucesso!")
                input("\nPressione Enter para continuar...")
                
            elif subopcao == "0":
                break
                
            else:
                print("\nOpção inválida.\n")
    
    elif opcao == "5": #Menu Minhas Transacoes
        clear()
        while True: 
            menuMinhasTransacoes()
            subopcao = input("Escolha uma opção: ").strip()
            if subopcao == "1": #Registrar Retirada
                print("Carregando Aceites em Aberto...")
                fc.printAceitesDisponiveis(canal)
                hash_aceite = input("Informe o ID do aceite (ou ENTER para cancelar): ").strip()
                if not hash_aceite:
                    break
                mensagem = input("Digite uma mensagem sobre a retirada: ").strip()
                print("Essa operacao pode demorar um pouco. Por favor, aguarde...\n")
                fc.registrarRetirada(canal, key_pvt, hash_aceite, mensagem)
                input("\nPressione Enter para continuar...")
                
            elif subopcao == "2": #Registrar Devolução
                fc.printRetiradasAtivas(canal)
                hash_retirada = input("Informe o ID da retirada a ser devolvida (ou ENTER para cancelar): ").strip()
                if not hash_retirada:
                    break
                mensagem = input("Digite uma mensagem sobre a devolucao: ").strip()
                print("Essa operacao pode demorar um pouco. Por favor, aguarde...\n")
                fc.registrarDevolucao(canal, key_pvt, hash_retirada, mensagem)
                input("\nPressione Enter para continuar...")
                
            elif subopcao == "3": #Exibir recibos
                fc.printRecibosCadeia(canal)
                input("\nPressione Enter para continuar...")
                
            elif subopcao == "4":
                ava_qual = input("Digite 1 para LIKE ou 2 para DISLIKE (ou ENTER para cancelar): ").strip()
                if not ava_qual:
                    break
                hash_post = input("Informe o hash do post (ou ENTER para cancelar): ").strip()
                if not hash_post:
                    break
                mensagem = input("Informe o motivo da avaliacao: ").strip()
                if ava_qual == "1":
                    ID = fc.registrarAvaliacao (canal, hash_post, mensagem, 1, key_pvt)
                elif ava_qual == "-1":
                    ID = fc.registrarAvaliacao (canal, hash_post, mensagem, -1, key_pvt)
                print("Processando...\n")
                fc.atualizarEstadoAnuncios(canal)
                print(f"Avaliacao {ID} registrada!")
                input("\nPressione Enter para continuar...")
                clear()
            elif subopcao == "0":
                break
                
            else:
                print("\nOpção inválida.\n")
    
    elif opcao == "6":
        sincronizarRede()
        input("Pressione Enter para voltar...")

    elif opcao == "7": #Menu Consultar Reputação
        clear()
        while True:
            clear()
            menuReputacao()
            subopcao = input("Escolha uma opção: ").strip()
            if subopcao == "1":
                hash_user = input("Informe a ID do usuário: ").strip()
                rep = fc.getUserRep(canal, hash_user)
                print(f"\nReputação: {rep}\n")
                input("Pressione Enter para voltar...")
                
            elif subopcao == "2":
                hash_post = input("Informe o HASH do bloco: ").strip()
                rep = fc.getPostRep(canal, hash_post)
                print(f"\nReputação: {rep}\n")
                input("Pressione Enter para voltar...")
            
            elif subopcao == "0":
                break
                
            else:
                print("\nOpção inválida.\n")

    elif opcao == "0":
        print("\nSaindo do sistema.\n")
        break

    else:
        print("\nOpção inválida.\n")
        
fc.leaveCanal(canal)
