import socket
import threading
import json
import queue


PORT = 5000  # Porta que o Servidor esta
USERS = []
MESSAGES = queue.Queue()
CHAT = queue.Queue()

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.bind("", PORT)

def receive():
    while True:
        try:
            msg, client = udp.recvfrom(1024)
            MESSAGES.put((msg, client))
        except:
            pass

def controll():
    while True:
        while not MESSAGES.empty():
            msg, client = MESSAGES.get()
            msg_json =  msg.decode('utf-8')
            msg_dic = json.loads(msg_json)
            
            if msg_dic["acao"] == 1:
                entrar_sala(msg_dic, client)
            elif msg_dic["acao"] == 2:
                sair_sala(msg_dic, client)
            elif msg_dic["acao"] == 3:
                chat_room(msg_dic, client)
            


def entrar_sala(msg_dic, client):
    adicionar_usuario(msg_dic, client)
    msg = {
        "acao": 1,
        "nome": msg_dic["nome"],
        "id_sala": msg_dic["id_sala"],
        "status": 1
    }
    msg_json = json.dumps(msg)
    udp.sendto(msg_json.encode("utf-8"), client)


def adicionar_usuario(usuario, cliente):
    ip_client, port_client = cliente
    port_client = port_client+usuario["id_sala"]
    cliente_sala = (ip_client, port_client)
    
    novo_usuario = {}
    novo_usuario["nome"] = usuario["nome"]
    novo_usuario["conexao"] = cliente_sala
    novo_usuario["id_sala"] = usuario["id_sala"]
    USERS.append(novo_usuario)

def sair_sala(msg_dic, client):
    remove_usuario(msg_dic, client)
    msg = {
        "acao": 2,
        "nome": msg_dic["nome"],
        "id_sala": msg_dic["id_sala"],
        "status": 1
    }
    msg_json = json.dumps(msg)
    udp.sendto(msg_json.encode("utf-8"), client)

def remove_usuario(usuario, cliente):
    novo_usuario = {}
    novo_usuario["nome"] = usuario["nome"]
    novo_usuario["conexao"] = cliente
    novo_usuario["id_sala"] = usuario["id_sala"]
    USERS.remove(novo_usuario)



def chat_room(msg_dic, client):
    msg_chat = {
        "id_sala": msg_dic["id_sala"],
        "nome": msg_dic["nome"],
        "msg": msg_dic["message"] 
    }
    CHAT.put(msg_chat)
    msg = {
        "acao": 3,
        "nome": msg_dic["nome"],
        "id_sala": msg_dic["id_sala"],
        "id_msg": msg_dic["id_msg"],
        "status": 1
    }
    msg_json = json.dumps(msg)
    udp.sendto(msg_json.encode("utf-8"), client)

def broadcast():
    while True:
        while not CHAT.empty():
            msg_chat = CHAT.get()
            msg_json = json.dumps(msg_chat)

            for user in USERS:
                if user["id_sala"] == msg_chat["id_sala"]:
                    udp.sendto(msg_json.encode("utf-8"), user["conexao"])



t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=controll)
t3 = threading.Thread(target=broadcast)

t1.start()
t2.start()
t3.start()


