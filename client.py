import socket
import sys
import threading
import json
import time

PORT_SERVICE = 5000
PORT_CHAT = None
SERVER = "10.0.1.10"
NICKNAME = None
ID_SALA = None
ID_MSG = 1
ENTROU_SALA = False



udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def service_receiver():
    global ENTROU_SALA
    global ID_MSG
    global ID_SALA
    global PORT_CHAT

    orig = ("", PORT_SERVICE)
    udp.bind(orig)
    
    while True:
        msg, cliente = udp.recvfrom(1024)
        msg_decoded = msg.decode('utf-8')
        string_dict = json.loads(msg_decoded)
        if string_dict["acao"] == 1:
            if string_dict["id_sala"] == ID_SALA:
                if string_dict["status"] == 1:
                    ENTROU_SALA = True
                    PORT_CHAT = PORT_SERVICE+ID_SALA
                    t1.start()

        elif string_dict["acao"] == 2:
            if string_dict["status"] == 1:
                    ENTROU_SALA = False
                    ID_SALA = None
                    PORT_CHAT = None
                    udp2.close()
                    
        elif string_dict["acao"] == 3:
            pass


def chat_receiver(porta_chat):
    orig = ("", PORT_CHAT)
    udp2.bind(orig)
    while ENTROU_SALA:
        msg, client = udp2.recvfrom(1024)
        msg_dec = msg.decode("utf-8")
        msg_dic = json.loads(msg_dec)
        user = msg_dic["nome"]
        mensagem = msg_dic["msg"]
        print(f"#{user} - {mensagem}")


t1 = threading.Thread(target=chat_receiver)
t2 = threading.Thread(target=service_receiver)

def client():
    global ID_SALA
    global ID_MSG
    global NICKNAME
    print("Start Chat")
    t2.start()
    print("Type q to exit")
    message = None
    dest = (SERVER, PORT_SERVICE)
    NICKNAME = input("Informe o seu nickname-> ")
    try:
        sala = int(input("Informe o ID da sala que deseja entrar-> "))
        ID_SALA = sala
        entrar_sala = { 
            "acao": 1, 
            "nome": NICKNAME,
            "id_sala": sala
        }
        string_json = json.dumps(entrar_sala)
        udp.sendto(string_json.encode('utf-8'), dest)
    except Exception as ex:
        sys.exit(0)
    
    count = 0
    print("Aguardando confirmacao.")
    while True:
        if not ENTROU_SALA:
            count += 1
        else:
            break
        if count == 10:
            sys.exit(0)
        time.sleep(1)

    while message != "q":
        message = input("-> ")
        
        if message == "q":
            msg = {
                "acao": 2,
                "nome": NICKNAME,
                "id_sala": ID_SALA
            }
        else:
            msg = {
                "acao": 3,
                "nome": NICKNAME,
                "id_sala": ID_SALA,
                "id_msg": ID_MSG,
                "msg": message
            }
        
        string_json = json.dumps(msg)
        udp.sendto(string_json.encode('utf-8'), dest)
        ID_MSG += 1
            
    udp.close()

if __name__ == "__main__":
    client()
