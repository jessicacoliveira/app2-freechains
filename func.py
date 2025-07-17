import subprocess, json, random, time, sys

#PORTA = random.randint(5000, 6000)
PORTA = 5000

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

#Exibe todos os anuncios da cadeia
def printAllAnuncios (canal):
    hash_list = getConsensus(canal)
    
    for hash_post in hash_list:
        tipo1 = int(isLikeOrDislike(canal, hash_post))
        if tipo1 == 0:
            tipo2 = int(getTypeBloco(canal, hash_post))
            if tipo2 == 1:
                printAnuncio(canal, hash_post)
                  
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

def printSolicitacao (canal, hash_post):
    bloco = getPayload(hash_post, canal)
    
    tipo_bloco = bloco.get("Tipo_bloco", "Nao especificado")
    solicitando = bloco.get("Solicitando", "Nao especificado")
    proposta = bloco.get("Proposta", "Sem descricao")
    contato = bloco.get("Contato", "Nao especificado")
    
    print("=== Solicitacao ===")
    print(f"ID do bloco: {hash_post}")
    print(f"Tipo do bloco: {tipo_bloco}")
    print(f"Solicitando: {solicitando}")
    print(f"Proposta: {proposta}")
    print(f"Contato: {contato}")
    print("================\n")

#Exibe todas as solicitacoes da cadeia
def printAllSolicitacoes(canal):
    hash_list = getConsensus(canal)
    
    if len(hash_list) == 1:
        print("Não há anúncios a serem exibidos.")
    else:
        for hash_post in hash_list:
            tipo1 = int(isLikeOrDislike(canal, hash_post))
            if tipo1 == 0:
                tipo2 = int(getTypeBloco(canal, hash_post))
                if tipo2 == 2:
                    printSolicitacao(canal, hash_post)

#Busca solicitações postadas por um autor específico
def buscaSolicitacoesChave (canal, chave):
    hash_list = getConsensus(canal)
    resultados = []
    
    for hash_post in hash_list:
        tipo1 = int(isLikeOrDislike(canal, hash_post))
        if tipo1 == 0:
            tipo2 = int(getTypeBloco(canal, hash_post))
            if tipo2 == 2:
                bloco = getBloco(canal, hash_post)
                autor_bloco = getAutor(canal, hash_post)
            
                if autor_bloco == chave:
                    resultados.append(hash_post)
    return resultados
    
#Exibe as solicitações encontradas na busca
def printBuscaSolicitacoesChave(canal, chave):
    resultados = buscaSolicitacoesChave (canal, chave)
    if not resultados:
        print(f"Nenhuma solicitacao registrada com essa chave.")
    for hash_post in resultados:
        printSolicitacao (canal, hash_post)
    
#Busca solicitações associadas a um anúncio específico
def buscaSolicitacoesAnuncio (canal, hash_anuncio):
    hash_list = getConsensus(canal)
    resultados = []
    
    for hash_post in hash_list:
        tipo1 = int(isLikeOrDislike(canal, hash_post))
        if tipo1 == 0:
            tipo2 = int(getTypeBloco(canal, hash_post))
            if tipo2 == 2:
                bloco = getPayload(hash_post, canal)
                solicitando = bloco.get("Solicitando", "Erro")           
                if solicitando == hash_anuncio:
                    resultados.append(hash_post)
    return resultados

def printSolicitacoesAnunciosDisponiveis (canal, chave):
    disponiveis = getAnunciosDisponiveis(canal)
    disponiveisAutor = getAnunciosAutor(canal, disponiveis, chave)
    if not disponiveisAutor:
        print(f"Nenhuma solicitacao registrada para meus anúncios.")
    for hash_post in disponiveisAutor:
        printBuscaSolicitacoesAnuncio(canal, hash_post)
    

#Exibe as solicitações encontradas na busca
def printBuscaSolicitacoesAnuncio(canal, hash_anuncio):
    resultados = buscaSolicitacoesAnuncio (canal, hash_anuncio)
    if not resultados:
        print(f"Nenhuma solicitacao registrada para o anúncio {hash_anuncio}")
    for hash_post in resultados:
        printSolicitacao (canal, hash_post)

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

def printListaSolicitacoes(canal, hash_list):
    if not hash_list:
        print("Nenhuma solicitacao a ser exibida.")
        return
    for hash_post in hash_list:
        printSolicitacao (canal, hash_post)

def definirStatusSolicitacao(canal, hash_solicitacao):
    hash_list = getConsensus(canal)
    bloco = getPayload(hash_solicitacao, canal)
    hash_anuncio = bloco.get("Solicitando", "")
    indice = hash_list.index(hash_anuncio)
    
    for i in range(indice + 1, len(hash_list)):
        bloco = getPayload(hash_list[i], canal)
        if int(getTypeBloco(canal, hash_list[i])) == 3 and bloco.get("Anuncio") == hash_anuncio:
            if bloco.get("Solicitacao") == hash_solicitacao:
                return "aceita"
            else:
                return "rejeitada"
    return "disponivel"

# ---------------

def getAnuncioSolicitacao(hash_post, canal):
    bloco = getPayload(hash_post, canal)
    return bloco.get("Solicitando", "")

def definirDisponibilidadeAnuncio(canal, hash_anuncio):
    hash_list = getConsensus(canal)
    indice = hash_list.index(hash_anuncio)
    
    for i in range(indice + 1, len(hash_list)):
        bloco = getPayload(hash_list[i], canal)
        if int(getTypeBloco(canal, hash_list[i])) == 3 and bloco.get("Anuncio") == hash_anuncio:
            return hash_list[i]  # Retorna o hash do aceite encontrado
    return "disponivel"

def getAnunciosDisponiveis(canal):
    hash_list = getConsensus(canal)
    resultado = []
    for hash_post in hash_list:
        if int(isLikeOrDislike(canal, hash_post)) == 0: #Identifica se eh bloco de conteudo
            if int(getTypeBloco(canal, hash_post)) == 1:  # Identifica se eh bloco de Anúncio
                status = definirDisponibilidadeAnuncio(canal, hash_post)
                if status == "disponivel":
                    resultado.append(hash_post)
    return resultado
    
def getAnunciosAutor(canal, hash_list, chave):
    resultado = []
    for hash_post in hash_list:
        if getAutor(canal, hash_post) == chave:
            resultado.append(hash_post)
    return resultado

def getAnunciosDisponiveisAutor(canal, chave):
    disponiveis = getAnunciosDisponiveis(canal)
    disponiveisAutor = getAnunciosAutor(canal, disponiveis, chave)
    return disponiveisAutor


def printAnunciosDisponiveisAutor(canal, chave):
    disponiveisAutor = getAnunciosDisponiveisAutor(canal, chave)
    if not disponiveisAutor:
        print("Nenhum anúncio disponível no momento.")
        return
    for hash_post in disponiveisAutor:
        printAnuncio (canal, hash_post)
        

def printAnunciosDisponiveis(canal):
    lista = getAnunciosDisponiveis(canal)
    if not lista:
        print("Nenhum anúncio disponível no momento.")
        return
    for hash_post in lista:
        printAnuncio (canal, hash_post)
        
def printAnunciosOrdenadosRepAutor(canal):
    lista_reps = []
    lista_hash = getAnunciosDisponiveis(canal)
    for hash_post in lista_hash:
        autor = getAutor(canal, hash_post)
        rep = float(getUserRep(canal, autor))
        lista_reps.append((hash_post, rep))

    lista_reps.sort(key=lambda x: x[1], reverse=True)
    
    if not lista_reps:
        print("Nenhum anúncio disponível no momento.")
        return

    for hash_post, rep in lista_reps:
        rep = int(rep)
        print(f"[Autor com reputação: {rep}]")
        printAnuncio (canal, hash_post)
        
# Retorna lista de hashes que possuem a keyword no título do anúncio
def buscaTitulo (canal, keyword):
    hash_list = getAnunciosDisponiveis(canal)
    keyword = keyword.strip().lower()
    resultados = []
    
    for hash_post in hash_list:
        bloco = getPayload(hash_post, canal)
        titulo = bloco.get("Titulo", "").strip().lower()
        if keyword in titulo:
            resultados.append(hash_post)
    return resultados
    
def printBuscaTitulo(canal, keyword):
    resultados = buscaTitulo(canal, keyword)
    if not resultados:
        print(f"Nenhum anúncio encontrado com '{keyword}' no título.")
    for hash_post in resultados:
        printAnuncio(canal, hash_post)
    
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
 
