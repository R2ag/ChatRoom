import socket
import _thread
import json

from client import ID_SALA

PORT = 5000  # Porta que o Servidor esta
LISTA_USUARIO = []

def adicionar_usuario(usuario, cliente):
    novo_usuario = {}
    novo_usuario["nome"] = usuario["nome"]
    novo_usuario["conexao"] = cliente
    novo_usuario["id_sala"] = usuario["id_sala"]
    LISTA_USUARIO.append(novo_usuario)

def remove_usuario(usuario, cliente):
    novo_usuario = {}
    novo_usuario["nome"] = usuario["nome"]
    novo_usuario["conexao"] = cliente
    novo_usuario["id_sala"] = usuario["id_sala"]
    LISTA_USUARIO.remove(novo_usuario)


def chat_server(udp):
    print(f"Starting UDP Server on port {PORT}")
    orig = ("", PORT)
    udp.bind(orig)
    while True:
        msg, cliente = udp.recvfrom(1024)
        msg_decoded = msg.decode('utf-8')
        try:
            string_dict = json.loads(msg_decoded)
            if string_dict["acao"] == 1:
                adicionar_usuario(string_dict, cliente)
                msg = {
                    "acao": 1,
                    "nome": string_dict["nome"],
                    "id_sala": string_dict["id_sala"],
                    "status": 1
                }
                msg_json = json.dumps(msg)
                udp.sendto(msg_json.encode("utf-8"), cliente)
            elif string_dict["acao"] == 2:
                remove_usuario(string_dict, cliente)
                msg = {
                    "acao": 2,
                    "nome": string_dict["nome"],
                    "id_sala": string_dict["id_sala"],
                    "status": 1
                }
                msg_json = json.dumps(msg)
                udp.sendto(msg_json.encode("utf-8"), cliente)
            elif string_dict["acao"] == 3:
                msg = {
                    "acao": 3,
                    "nome": string_dict["nome"],
                    "id_sala": string_dict["id_sala"],
                    "id_msg": string_dict["id_msg"],
                    "status": 1
                }
                msg_json = json.dumps(msg)
                udp.sendto(msg_json.encode("utf-8"), cliente)
                
                msg_chat = {
                    "id_sala": string_dict["id_sala"],
                    "nome": string_dict["nome"],
                    "msg": string_dict["message"] 
                }
                msg_chat_json = json.dumps(msg_chat)
                for item in LISTA_USUARIO:
                    if (item["id_sala"] == string_dict["id_sala"]) and (item["conexao"] != cliente):
                        udp.sendto(msg_json.encode("utf-8"), item["conexao"])

        except Exception as ex:
            pass
    udp.close()

def main():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    chat_server(udp)

if __name__ == "__main__":
    main()
