import func3 as fc
import subprocess, json, time

user1_pvt = "CD1499F6E4E766064A4EA7562B95C9E07C787F188D26E5D6D4485A083CDB6080E968215E8F3FFE7289B71E039A18274375187F6BA2B0B5A386BF479151171C5F"
user1_pub = "E968215E8F3FFE7289B71E039A18274375187F6BA2B0B5A386BF479151171C5F"

user2_pvt = "8BD8EC8806030C6EC00830AEC27BD640C3560FDA78C3D2CEB81319808E31ABB482F15FFC4FBB82B8FC86ED45E722AA2440040C7AD0150323DE012A8FD517777A"
user2_pub = "82F15FFC4FBB82B8FC86ED45E722AA2440040C7AD0150323DE012A8FD517777A"

user3_pvt = "622B1B946383244FDBCDBA01A3E5028395944757C23DBDD05E196523F7835951C54B5065536D62B0E4B65A856DA7BDCFC81D8072882DC1D10D6A0C86ECB23F4C"
user3_pub = "C54B5065536D62B0E4B65A856DA7BDCFC81D8072882DC1D10D6A0C86ECB23F4C"

def simulHosts(canal, chave_pub):
    global user1_pub, user1_pvt, user2_pub, user2_pvt, user3_pub, user3_pvt
    
    for porta in [5001, 5002, 5003]:
        comando = f"./freechains-host --port={porta} start /tmp/freechains/host0{porta}"
        subprocess.Popen(["gnome-terminal", "--tab", "--", "bash", "-c", f"{comando}; exec bash"])
        time.sleep(2)
    
    subprocess.run(["./freechains", f"--host=localhost:{5001}", "chains", "join", canal, chave_pub], stdout=subprocess.PIPE, text=True)
    subprocess.run(["./freechains", f"--host=localhost:{5002}", "chains", "join", canal, chave_pub], stdout=subprocess.PIPE, text=True)
    subprocess.run(["./freechains", f"--host=localhost:{5003}", "chains", "join", canal, chave_pub], stdout=subprocess.PIPE, text=True)

    hash_anuncio1 = criaAnuncio (canal, "Troco furadeira", "Seminova, sem detalhes", "Troca", "0", user1_pvt, 5001)
    hash_anuncio2 = criaAnuncio (canal, "Empresto escada", "reforcada, 5 degraus", "Emprestimo", "15", user2_pvt, 5002)
    hash_anuncio3 = criaAnuncio (canal, "Troco figurinhas da Copa", "soh quero brilhantes", "Troca", "0", user3_pvt, 5003)
    
    for porta in [5001, 5002, 5003]:
        subprocess.run(["./freechains", f"--host=localhost:{porta}", "peer", "localhost:5000", "send", canal])
        subprocess.run(["./freechains", f"--host=localhost:5000", "peer", f"localhost:{porta}", "recv", canal])
    
    #transferindo rep
    fc.likeHosts (canal, hash_anuncio1)
    fc.likeHosts (canal, hash_anuncio1)
    fc.likeHosts (canal, hash_anuncio1)
    fc.likeHosts (canal, hash_anuncio1) 
    fc.likeHosts (canal, hash_anuncio2)
    fc.likeHosts (canal, hash_anuncio2)
    fc.likeHosts (canal, hash_anuncio2) 
    fc.likeHosts (canal, hash_anuncio3) 
    fc.likeHosts (canal, hash_anuncio3) 
    
    subprocess.run(["./freechains", f"--host=localhost:{5001}", "chains", "leave", canal], stdout=subprocess.PIPE, text=True)
    subprocess.run(["./freechains", f"--host=localhost:{5002}", "chains", "leave", canal], stdout=subprocess.PIPE, text=True)
    subprocess.run(["./freechains", f"--host=localhost:{5003}", "chains", "leave", canal], stdout=subprocess.PIPE, text=True)
    
def criaAnuncio (canal, titulo, descricao, tipo_transacao, prazo, chave_pvt, porta):
    item = {
        "Tipo_bloco": 1,
        "Titulo": titulo,
        "Descricao": descricao,
        "Tipo_transacao": tipo_transacao,
        "Prazo": prazo
    }
    json_item = json.dumps(item, ensure_ascii=False)
    hash_anuncio = postBloco(json_item, chave_pvt, canal, porta)
    return hash_anuncio
    
def placeSolicitacao(canal, hash_post, chave_pvt, mensagem, contato, porta):
    
    item = {
        "Tipo_bloco": 2,
        "Solicitando": hash_post,
        "Proposta": mensagem,
        "Contato": contato
    }

    json_item = json.dumps(item, ensure_ascii=False)
    hash_solicitacao = postBloco(json_item, chave_pvt, canal, porta)
    return hash_solicitacao

def postBloco(dados, chave_pvt, canal, porta):
    resultado = subprocess.run (["./freechains", f"--host=localhost:{porta}", "chain", canal, "post", "inline", dados, f"--sign={chave_pvt}"], stdout=subprocess.PIPE, text=True)
    return resultado.stdout.strip()  # retorna o hash do post
    
    

