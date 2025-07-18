import subprocess, json, random, time, sys
HASH_CONSENSUS = []
ANUNCIOS = []
ANUNCIOS_DISPONIVEIS = []
SOLICITACOES = []
SOLICITACOES_DISPONIVEIS = []
SOLICITACOES_INDISPONIVEIS = []
SOLICITACOES_REJEITADAS = []

#PORTA = random.randint(5000, 6000)
PORTA = 5000

# Chamar sempre que lista de anuncios precisar ser atualizada
def atualizarEstadoAnuncios(canal):
    global HASH_CONSENSUS, ANUNCIOS, ANUNCIOS_DISPONIVEIS
    
    HASH_CONSENSUS = getConsensus(canal)
    ANUNCIOS_DISPONIVEIS = atualizaAnunciosDisponiveis(canal)

# Atualiza lista de Anúncios Disponíveis
def atualizaAnunciosDisponiveis(canal):
    global HASH_CONSENSUS
    lista = []
    for hash_post in HASH_CONSENSUS:
        if int(isLikeOrDislike(canal, hash_post)) == 0: #Identifica se eh bloco de conteudo
            if int(getTypeBloco(canal, hash_post)) == 1:  # Identifica se eh bloco de Anúncio
                status = definirDisponibilidadeAnuncio(canal, hash_post)
                if status == "disponivel":
                    lista.append(hash_post)
     return lista

def atualizarEstadoSolicitacoes(canal, chave):
    global HASH_CONSENSUS, SOLICITACOES, SOLICITACOES_DISPONIVEIS
    global SOLICITACOES_INDISPONIVEIS, SOLICITACOES_REJEITADAS

    HASH_CONSENSUS = getConsensus(canal)
    SOLICITACOES = []
    SOLICITACOES_DISPONIVEIS = []
    SOLICITACOES_INDISPONIVEIS = []
    SOLICITACOES_REJEITADAS = []

    for hash_post in HASH_CONSENSUS:
        if int(isLikeOrDislike(canal, hash_post)) == 0:  # é bloco de conteúdo
            if int(getTypeBloco(canal, hash_post)) == 2:  # é solicitação
                SOLICITACOES.append(hash_post)
                autor_bloco = getAutor(canal, hash_post)
                if autor_bloco == chave:
                    status = definirStatusSolicitacao(canal, hash_post)
                    if status == "disponivel":
                        SOLICITACOES_DISPONIVEIS.append(hash_post)
                    elif status == "aceita":
                        SOLICITACOES_INDISPONIVEIS.append(hash_post)
                    elif status == "rejeitada":
                        SOLICITACOES_REJEITADAS.append(hash_post)

# Inicia o servidor na porta aleatória escolhida
def inicializa():
    comando = f"./freechains-host --port={PORTA} start /tmp/freechains/host0{PORTA}"
    subprocess.Popen(["gnome-terminal", "--tab", "--", "bash", "-c", f"{comando}; exec bash"])
    time.sleep(2)
    print(f"Host iniciado na porta {PORTA}")
    
    # Lista de peers que será usada na simulacao
    with open("contatos.txt", "a") as arquivo:
        arquivo.write(f"{PORTA}\n")

# Sincroniza com os demais peers da lista de contatos     
def sincronize(canal):
    with open("contatos.txt", "r") as arquivo:
        contatos = [int(linha.strip()) for linha in arquivo]
    for peer in contatos:
        if peer != PORTA:
            subprocess.run(["./freechains", f"--host=localhost:{PORTA}", "peer", f"localhost:{peer}", "send", f"{canal}"])
    
# Gera um par de chaves pública e privada a partir de uma palavra-chave
def criarPubpvt(keyword):
    resultado = subprocess.run(["./freechains", f"--host=localhost:{PORTA}", "keys", "pubpvt", keyword], stdout=subprocess.PIPE, text=True)
    saidas = resultado.stdout.strip().split()
    chave_pub = saidas[0]
    chave_pvt = saidas[1]
    return chave_pub, chave_pvt

# Entra em um canal especificado com a chave do pioneiro (só aceita 1 pioneiro)
def joinCanal(key, canal):
    subprocess.run(["./freechains", f"--host=localhost:{PORTA}", "chains", "join", canal, key], stdout=subprocess.PIPE, text=True)

# Sai de um canal
def leaveCanal(canal):
    subprocess.run(["./freechains", f"--host=localhost:{PORTA}", "chains", "leave", canal], stdout=subprocess.PIPE, text=True)

# Dá like em um post, assinando com a chave privada
def like(canal, hash_post, chave):
    resultado = subprocess.run(["./freechains", "chain", f"{canal}", f"--port={PORTA}", "like", hash_post, f"--sign={chave}"], stdout=subprocess.PIPE, text=True)
    
    return resultado.stdout.strip()

# Dá dislike em um post, assinando com a chave privada
def dislike(canal, hash_post, chave):
    resultado = subprocess.run(["./freechains", "chain", f"{canal}", f"--port={PORTA}", "dislike", f"{hash_post}", f"--sign={chave}"], stdout=subprocess.PIPE, text=True)
    
    return resultado.stdout.strip()

# Recupera o conteúdo (payload) de um post a partir do seu hash
def getPayload(hash_post, canal):   
    resultado = subprocess.run (["./freechains", f"--host=localhost:{PORTA}", "chain", canal, "get", "payload", hash_post], stdout=subprocess.PIPE, text=True)
    payload = resultado.stdout.strip()

    if payload == "": #tirar isso depois
        return {}  # (like ou dislike)
    else:
        return json.loads(payload)

# Obtém a reputação de um usuário 
def getUserRep(canal, chave):
    resultado = subprocess.run (["./freechains", f"--host=localhost:{PORTA}", "chain", canal, "reps", chave], stdout=subprocess.PIPE, text=True)
    return resultado.stdout.strip()

# Obtém a reputação de um post 
def getPostRep(canal, hash_post):
    resultado = subprocess.run (["./freechains", f"--host=localhost:{PORTA}", "chain", canal, "reps", hash_post], stdout=subprocess.PIPE, text=True)
    return resultado.stdout.strip()

def getConsensus(canal):
    resultado = subprocess.run(["./freechains", f"--host=localhost:{PORTA}", "chain", canal, "consensus"], stdout=subprocess.PIPE, text=True)
    saidas = resultado.stdout.strip().split()
    return saidas

# Retorna o bloco completo de um post em formato JSON
def getBloco(canal, hash_post):
    resultado = subprocess.run(["./freechains", f"--host=localhost:{PORTA}", "chain", canal, "get", "block", hash_post], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    saida = resultado.stdout.strip()
    
    return json.loads(saida)
    
def getAutor(canal, hash_post):
    bloco = getBloco(canal, hash_post)
    
    sign_info = bloco.get("sign", {})
    return sign_info.get("pub", None)

# Retorna o hash do bloco gênesis da cadeia
def getGenesis(canal):
    resultado = subprocess.run(["./freechains", f"--host=localhost:{PORTA}", "chain", canal, "genesis"], stdout=subprocess.PIPE, text=True)
    return resultado.stdout.strip()
    
def isLikeOrDislike(canal, hash_post):
    bloco = getBloco(canal, hash_post)

    like_info = bloco.get("like") or {}
    return like_info.get("n", 0) # 1 para like, -1 para dislike, 0 para conteudo

# Posta bloco no canal especificado, assinando com a chave privada
def postBloco(dados, chave, canal):
    resultado = subprocess.run (["./freechains", f"--host=localhost:{PORTA}", "chain", canal, "post", "inline", dados, f"--sign={chave}"], stdout=subprocess.PIPE, text=True)
    return resultado.stdout.strip()  # retorna o hash do post

# Identifica o tipo de bloco a partir do conteudo guardado no payload
def getTypeBloco (canal, hash_post):
    bloco = getPayload(hash_post, canal)
    return bloco.get("Tipo_bloco", 0)

def readFile (canal, arquivo, chave):
    with open(arquivo, "r", encoding="utf-8") as file:
        for linha in file:
            linha = linha.strip()
            if not linha:
                continue  # ignora linhas vazias

            partes = linha.split("/")

            item = {
                "Tipo_bloco": partes[0].strip(),
                "Titulo": partes[1].strip(),
                "Descricao": partes[2].strip(),
                "Tipo_transacao": partes[3].strip(),
                "Prazo": partes[4].strip()
            }
            json_item = json.dumps(item, ensure_ascii=False)
            postBloco(json_item, chave, canal)

# Exibe na tela o conteudo de um bloco do tipo anuncio
def printAnuncio (canal, hash_post):
    bloco = getPayload(hash_post, canal)
    
    tipo_bloco = bloco.get("Tipo_bloco", "Nao especificado")
    titulo = bloco.get("Titulo", "Sem título")
    descricao = bloco.get("Descricao", "Sem descricao")
    tipo_trans = bloco.get("Tipo_transacao", "Nao especificado")
    prazo = bloco.get("Prazo", "Nao aplicavel")
    
    print("=== Anúncio ===")
    print(f"ID do bloco: {hash_post}")
    print(f"Tipo do bloco: {tipo_bloco}")
    print(f"Título: {titulo}")
    print(f"Descricao: {descricao}")
    print(f"Tipo de transação: {tipo_trans}")
    if tipo_trans == "Emprestimo":
        print(f"Prazo: {prazo}")
    print("================\n")

# Exibe na tela todos os anúncios de uma lista genérica
def printListaAnuncios (canal, lista):
    if not lista:
        print("Nenhum anúncio para exibir.")
        return
    for hash_post in lista:
        printAnuncio(canal, hash_post)

#Exibe todos os anuncios da cadeia        
def printAllAnuncios (canal):
    printListaAnuncios (canal, getListaAnuncios(canal))
                
#Exibe todos os anúncios disponíveis (sem bloco de aceite associado) da cadeia
def printAnunciosDisponiveis(canal):
    global ANUNCIOS_DISPONIVEIS 
    printListaAnuncios (canal, ANUNCIOS_DISPONIVEIS)

# Exibe os Anúncios Disponíveis para uma dada pub_key
def printAnunciosDisponiveisAutor(canal, chave):
    lista = getAnunciosDisponiveisAutor (canal, chave)
    printListaAnuncios (canal, lista)
    
# Exibe anúncios disponíveis ordenados pela rep do autor
def printAnunciosOrdenadosRepAutor(canal):
    lista = ordenaAnunciosRepAutor(canal)
    printListaAnuncios (canal, lista)
    
#Exibe resultados da busca de dada keyword no título de anúncios disponíveis
def printBuscaTitulo(canal, keyword):
    lista = buscaTitulo(canal, keyword)
    printListaAnuncios (canal, lista)

# Devolve uma lista com os Anúncios Disponíveis para uma dada pub_key 
def getAnunciosDisponiveisAutor(canal, chave):
    global ANUNCIOS_DISPONIVEIS
    anunciosDisponiveisAutor = []
    for hash_post in ANUNCIOS_DISPONIVEIS:
        if getAutor(canal, hash_post) == chave:
            anunciosDisponiveisAutor.append(hash_post)
    return anunciosDisponiveisAutor 
    
# Devolve a lista completa de Anúncios a partir do CONSENSUS
# Nao eh global pq eh pouco usada     
def getListaAnuncios(canal):
    global HASH_CONSENSUS
    lista = []
    for hash_post in HASH_CONSENSUS:
        if int(isLikeOrDislike(canal, hash_post)) == 0: #Identifica se eh bloco de conteudo
            if int(getTypeBloco(canal, hash_post)) == 1:  # Identifica se eh bloco de Anúncio
                lista.append(hash_post)
    return lista

# Devolve lista de anúncios disponíveis ordenados pela rep do autor
def ordenaAnunciosRepAutor(canal):
    global ANUNCIOS_DISPONIVEIS
    lista_reps = []
    for hash_post in ANUNCIOS_DISPONIVEIS:
        autor = getAutor(canal, hash_post)
        rep = float(getUserRep(canal, autor))
        lista_reps.append((hash_post, rep))

    lista_reps.sort(key=lambda x: x[1], reverse=True)
    
    return [h for h, _ in lista_reps]

# Retorna lista de anúncios disponíveis que possuem dada keyword no título
def buscaTitulo (canal, keyword):
    global ANUNCIOS_DISPONIVEIS
    keyword = keyword.strip().lower()
    resultados = []
    
    for hash_post in ANUNCIOS_DISPONIVEIS:
        bloco = getPayload(hash_post, canal)
        titulo = bloco.get("Titulo", "").strip().lower()
        if keyword in titulo:
            resultados.append(hash_post)
    return resultados

# Cria um bloco de Solicitacao na cadeia
def placeSolicitacao(canal, hash_post, chave, mensagem, contato):
    
    item = {
        "Tipo_bloco": 2,
        "Solicitando": hash_post,
        "Proposta": mensagem,
        "Contato": contato
    }

    json_item = json.dumps(item, ensure_ascii=False)
    resultado = postBloco(json_item, chave, canal)
    
    return resultado
    
# Exibe na tela o conteudo de um bloco do tipo solicitacao    
def printSolicitacao (canal, hash_post):
    bloco = getPayload(hash_post, canal)
    
    tipo_bloco = bloco.get("Tipo_bloco", "Nao especificado")
    solicitando = bloco.get("Solicitando", "Nao especificado")
    proposta = bloco.get("Proposta", "Sem descricao")
    contato = bloco.get("Contato", "Nao especificado")
    
    print("=== Solicitacao ===")
    print(f"ID do bloco: {hash_post}")
    #print(f"Tipo do bloco: {tipo_bloco}")
    print(f"Solicitando: {solicitando}")
    print(f"Proposta: {proposta}")
    print(f"Contato: {contato}")
    print("================\n")

# Exibe na tela todos os anúncios de uma lista genérica
def printListaSolicitacoes (canal, lista):
    if not lista:
        print("Nenhuma solicitacao para exibir.")
        return
    for hash_post in lista:
        printSolicitacao(canal, hash_post)

def printSolicitacoesDisponiveis(canal):
    global SOLICITACOES_DISPONIVEIS
    lista = SOLICITACOES_DISPONIVEIS
    printListaSolicitacoes (canal, lista)
    
def printSolicitacoesIndisponiveis(canal):
    global SOLICITACOES_INDISPONIVEIS
    lista = SOLICITACOES_INDISPONIVEIS
    printListaSolicitacoes (canal, lista)
    
def printSolicitacoesRejeitadas(canal):
    global SOLICITACOES_REJEITADAS
    lista = SOLICITACOES_REJEITADAS
    printListaSolicitacoes (canal, lista)

#Exibe todas as solicitacoes da cadeia
def printAllSolicitacoes(canal):
    lista = getListaSolicitacoes(canal)
    printListaSolicitacoes (canal, lista)
    
#Exibe as solicitações feitas por autor especifico
def printBuscaSolicitacoesChave(canal, chave):
    lista = buscaSolicitacoesChave (canal, chave)
    printListaSolicitacoes (canal, lista)

#Exibe as solicitações encontradas na busca
def printBuscaSolicitacoesAnuncio(canal, hash_anuncio):
    lista = buscaSolicitacoesAnuncio (canal, hash_anuncio)
    if not resultados:
        print(f"Nenhuma solicitacao registrada para o anúncio {hash_anuncio}")
        return
    printListaSolicitacoes (canal, lista)

# Exibe solicitações para anúncios disponíveis de um dado autor
def printSolicitacoesAnunciosDisponiveis (canal, chave):
    lista = getAnunciosDisponiveisAutor(canal, chave)
    if not lista:
        print(f"Nenhuma solicitacao registrada para meus anúncios.")
        return
    for hash_post in lista:
        printBuscaSolicitacoesAnuncio(canal, hash_post)

#Busca solicitações postadas por um autor específico
def buscaSolicitacoesChave (canal, chave):
    global SOLICITACOES
    resultados = []
    
    for hash_post in SOLICITACOES:
        bloco = getBloco(canal, hash_post)
        autor_bloco = getAutor(canal, hash_post)
        if autor_bloco == chave:
            resultados.append(hash_post)
    return resultados

#Busca solicitações associadas a um anuncio especifico
def buscaSolicitacoesAnuncio (canal, hash_anuncio):
    global SOLICITACOES
    resultados = []
    
    for hash_post in SOLICITACOES:
        bloco = getPayload(hash_post, canal)
        solicitando = bloco.get("Solicitando", "Erro")           
        if solicitando == hash_anuncio:
            resultados.append(hash_post)
    return resultados

# Devolve listas de solicitacoes disponiveis, aceitas e rejeitadas de autor específico
def getSolicitacoes(canal, chave):
    hash_list = buscaSolicitacoesChave (canal, chave)
    sol_disponiveis = []
    sol_aceitas = []
    sol_rejeitadas = []
    for hash_post in hash_list:
        status = definirStatusSolicitacao(canal, hash_post)
        if status == "disponivel":
            sol_disponiveis.append(hash_post)
        elif status == "aceita":
            sol_aceitas.append(hash_post)
        else:
            sol_rejeitadas.append(hash_post)
    return sol_disponiveis, sol_aceitas, sol_rejeitadas
    
# Classifica as solicitacoes em disponivel, aceita e rejeitada
def definirStatusSolicitacao(canal, hash_solicitacao):
    global HASH_CONSENSUS
    bloco = getPayload(hash_solicitacao, canal)
    hash_anuncio = bloco.get("Solicitando", "")
    indice = HASH_CONSENSUS.index(hash_anuncio)
    
    for i in range(indice + 1, len(HASH_CONSENSUS)):
        bloco = getPayload(HASH_CONSENSUS[i], canal)
        if int(getTypeBloco(canal, HASH_CONSENSUS[i])) == 3 and bloco.get("Anuncio") == hash_anuncio:
            if bloco.get("Solicitacao") == hash_solicitacao:
                return "aceita"
            else:
                return "rejeitada"
    return "disponivel"
    
# Devolve o hash do anuncio ao qual a solicitacao se refere
def getAnuncioSolicitacao(hash_post, canal):
    bloco = getPayload(hash_post, canal)
    return bloco.get("Solicitando", "")

# Classifica os anuncios em disponivel e indisponivel
def definirDisponibilidadeAnuncio(canal, hash_anuncio):
    global HASH_CONSENSUS
    indice = HASH_CONSENSUS.index(hash_anuncio)
    
    for i in range(indice + 1, len(HASH_CONSENSUS)):
        bloco = getPayload(HASH_CONSENSUS[i], canal)
        if int(getTypeBloco(canal, HASH_CONSENSUS[i])) == 3 and bloco.get("Anuncio") == hash_anuncio:
            return "indisponivel" 
    return "disponivel"

# Devolve a lista completa de Solicitacoes a partir do CONSENSUS    
def getListaSolicitacoes(canal):
    global HASH_CONSENSUS
    lista = []
    for hash_post in HASH_CONSENSUS:
        if int(isLikeOrDislike(canal, hash_post)) == 0: #Identifica se eh bloco de conteudo
            if int(getTypeBloco(canal, hash_post)) == 2:  # Identifica se eh bloco de Anúncio
                lista.append(hash_post)
    return lista
  
'''
def getAnunciosDisponiveis(canal):
    hash_list = getConsensus(canal)
    resultado = []
    for hash_post in hash_list:
        if int(isLikeOrDislike(canal, hash_post)) == 0: #Identifica se eh bloco de conteudo
            if int(getTypeBloco(canal, hash_post)) == 1:  # Identifica se eh bloco de Anúncio
                status = definirDisponibilidadeAnuncio(canal, hash_post)
                if status == "disponivel":
                    resultado.append(hash_post)
    return resultado'''
   
def escolhaEmprestimo(canal, hash_anuncio):
    hash_list = getConsensus(canal)
    indice = hash_list.index(hash_anuncio)
    aux = 0
    retorno = "vazio"
    for i in range(indice + 1, len(hash_list)):
        bloco = getPayload(hash_list[i], canal)
        tipo = int(getTypeBloco(canal, hash_list[i]))
        
        if tipo == 3 and bloco.get("Anuncio") == hash_anuncio:
            return "indisponivel"
        elif tipo == 2 and bloco.get("Solicitando") == hash_anuncio and aux == 0:
            retorno = hash_list[i]
            aux=1
            
    return retorno
    
def atualizarEmprestimo(canal, chave_pub, chave_pvt):
    lista = getAnunciosDisponiveisAutor(canal, chave_pub)
    if not lista:
        print("Nenhuma nova solicitacao para emprestimo.")
    for hash_anuncio in lista:
        bloco = getPayload(hash_anuncio, canal)
        if bloco.get("Tipo_transacao") == "Emprestimo":
            printEscolhaEmprestimo(canal, hash_anuncio, chave_pvt, bloco.get("Descricao"), bloco.get("Prazo"))

def printEscolhaEmprestimo(canal, hash_anuncio, chave, mensagem, prazo):
    retorno = escolhaEmprestimo(canal, hash_anuncio)
    if retorno == "vazio":
        print(f"Nenhuma nova solicitacao para {hash_anuncio} foi encontrada.")
    elif retorno == "indisponivel":
        print("ERRO: bloco de aceite encontrado. Anuncio nao esta mais disponivel.")
    else:
        aceitarSolicitacao(canal, retorno, chave, mensagem, prazo)
        print(f"Solicitacao {retorno} escolhida para {hash_anuncio}. Bloco de aceite gerado com sucesso!")

# Exibe a lista de anúncios de troca disponíveis para a escolha de um usuário específico
def printAnunciosTrocaDisponiveis(canal, chave):
    lista = getAnunciosDisponiveisAutor(canal, chave_pub)
    if not lista:
        print("Nenhuma solicitacao de troca disponivel.")
    for hash_anuncio in lista:
        bloco = getPayload(hash_anuncio, canal)
        if bloco.get("Tipo_transacao") == "Troca":
            printAnuncio(canal, hash_anuncio)
            
def printSolicitacoesTrocaAnunciosDisponiveis (canal, chave):
    disponiveis = getAnunciosDisponiveis(canal)
    disponiveisAutor = getAnunciosAutor(canal, disponiveis, chave)
    
    if not disponiveisAutor:
        print(f"Nenhum anúncio próprio disponível.")
        return
        
    for hash_anuncio in disponiveisAutor:
        bloco = getPayload(hash_anuncio, canal)
        if bloco.get("Tipo_transacao") == "Troca":
            resultados = buscaSolicitacoesAnuncio (canal, hash_anuncio)
            for hash_post in resultados:
                printSolicitacao (canal, hash_post)


# Cria o bloco de aceite
def aceitarSolicitacao(canal, hash_post, chave, mensagem, prazo):
    ref_anuncio = getAnuncioSolicitacao(hash_post, canal)
    item = {
        "Tipo_bloco": 3,
        "Solicitacao": hash_post,
        "Anuncio": ref_anuncio,
        "Mensagem": mensagem,
        "Prazo": prazo
    }

    json_item = json.dumps(item, ensure_ascii=False)
    resultado = postBloco(json_item, chave, canal)
    
    return resultado

def printAceite (canal, hash_post):
    bloco = getPayload(hash_post, canal)
    
    tipo_bloco = bloco.get("Tipo_bloco", "Nao especificado")
    solicitacao = bloco.get("Solicitacao", "Nao especificado")
    anuncio = bloco.get("Anuncio", "Sem descricao")
    msg = bloco.get("Mensagem", "Nao especificado")
    prazo = bloco.get("Prazo", "Nao especificado")
    
    print("=== Solicitacao ===")
    print(f"ID do bloco: {hash_post}")
    print(f"Tipo do bloco: {tipo_bloco}")
    print(f"Solicitacao: {solicitacao}")
    print(f"Anuncio: {anuncio}")
    print(f"Mensagem: {msg}")
    print(f"Prazo: {prazo}")
    print("================\n")

#Exibe todos os blocos de aceite da cadeia
def printAllAceite(canal):
    hash_list = getConsensus(canal)
    for hash_post in hash_list:
        tipo1 = int(isLikeOrDislike(canal, hash_post))
        if tipo1 == 0:
            tipo2 = int(getTypeBloco(canal, hash_post))
            if tipo2 == 3:
                printAceite(canal, hash_post)
  
 # Cria bloco de avaliação
def registrarAvaliacao (canal, hash_post, mensagem, tipo_interacao, chave):
    if tipo_interacao == 1:
        ref_interacao = like(canal, hash_post, chave)
    elif tipo_interacao == -1:
        ref_interacao = dislike(canal, hash_post, chave)
    autor = getAutor(canal, hash_post)
    item = {
        "Tipo_bloco": 0,
        "Ref_interacao": ref_interacao, #hash do bloco de like/dislike
        "Ref_bloco": hash_post,         #hash do bloco avaliado
        "Ref_autor": autor,              #hash do autor do bloco que foi avaliado
        "Mensagem": mensagem            #motivo da avaliação
    }

    json_item = json.dumps(item, ensure_ascii=False)
    resultado = postBloco(json_item, chave, canal)
    
    return resultado
 
