import socket
import threading
import sys
import pickle
import time
from os import system, name

servers = [
    ['localhost', 10000],
    ['localhost', 10001],
    ['localhost', 10002],
    ['localhost', 10003],
]
links = [
    [0, 1],
    [1, 2],
    [1, 3],
    [2, 3],
]
routingTable = []
id = 0
numClients = 4
hash_size = 2
hash = {}


def createRoutingTable():
    for i in links:
        if (id == i[0]):
            routingTable.append([i[1], i[1] * hash_size + hash_size - 1])
        elif(id == i[1]):
            routingTable.append([i[0], i[0] * hash_size + hash_size - 1])


class Receiver(threading.Thread):

    def __init__(self, my_host, my_port):
        threading.Thread.__init__(self, name="messenger_receiver")
        self.host = my_host
        self.port = my_port

    def listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen(10)
        while True:
            connection, client_address = sock.accept()
            try:
                while True:
                    received_data = connection.recv(1024)
                    if received_data:
                        data = pickle.loads(received_data)
                        handleData(data)
                    else:
                        break
            finally:
                connection.shutdown(2)
                connection.close()

    def run(self):
        self.listen()


def sendData(to, data):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((servers[to][0], servers[to][1]))
        s.send(data)
        s.shutdown(2)
        s.close()
    except:
        print('Falha ao enviar dados')


def handleData(data):
    key_received = data[1]
    hash_key = key_received % (hash_size * numClients)
    if(data[0] == 0):  # Adicionar chave
        message_received = data[2]
        if(hash_key in hash):
            hash[hash_key][key_received] = message_received
        else:
            sendMessage(hash_key, key_received, message_received)
    elif(data[0] == 1):  # Procurar chave
        if(hash_key in hash):
            to = whereToSend(data[2] * hash_size)
            data = pickle.dumps(
                [2, key_received, data[2], hash[hash_key][key_received]])
        else:
            to = whereToSend(hash_key)
            data = pickle.dumps([data[0], data[1], data[2]])
        sendData(to, data)
    elif(data[0] == 2):  # Devolver e mostrar chave
        if(id == data[2]):
            print('A mensagem da chave ' +
                  str(key_received) + ' é ' + str(data[3]))
        else:
            to = whereToSend(data[2] * hash_size)
            data = pickle.dumps([2, data[1], data[2], data[3]])
            sendData(to, data)


def writeMessage():
    key = int(input('Qual a chave?\n'))
    hash_key = key % (hash_size * numClients)
    message = input('Qual a mensagem?\n')
    sendMessage(hash_key, key, message)


def sendMessage(hash_key, key, message):
    if(hash_key in hash):
        hash[hash_key][key] = message
    else:
        to = whereToSend(hash_key)
        try:
            data = pickle.dumps([0, key, message])
            sendData(to, data)
        except:
            print('Falha ao enviar mensagem')


def whereToSend(hash_key):
    aux_num = 123456789
    aux_id = -1
    for i in routingTable:
        if (i[1] < aux_num and hash_key <= i[1]):
            aux_num = i[1]
            aux_id = i[0]
    if(aux_id == -1):
        for i in routingTable:
            if (i[1] < aux_num and hash_key >= i[1]):
                aux_num = i[1]
                aux_id = i[0]
    return aux_id


def findKey():
    key = int(input('Qual a chave que gostaria de procurar?\n'))
    hash_key = key % (hash_size * numClients)
    if(hash_key in hash):
        print('A mensagem da chave ' + str(key) +
              ' é ' + str(hash[hash_key][key]))
    else:
        data = pickle.dumps([1, key, id])
        to = whereToSend(hash_key)
        try:
            sendData(to, data)
        except:
            print('Falha ao enviar mensagem\n')


def main():
    if len(sys.argv) > 1:
        global id
        id = int(sys.argv[1])
        my_host = servers[id][0]
        my_port = servers[id][1]
    else:
        print('Falta argumentos')
        sys.exit()
    createRoutingTable()
    receiver = Receiver(my_host, my_port)
    receiver.daemon = True
    receiver.start()
    for i in range(id * hash_size, id * hash_size + hash_size):
        hash[i] = {}
    menu()


def clear():
    if name == 'nt':
        _ = system('cls')

    else:
        _ = system('clear')


def menu():
    while True:
        clear()
        print(
            'Opções\n1 - Mandar mensagem\n2 - Procurar chave\n3 - Visualizar Hash\n4 - Mostrar tabela de roteamento\n0 - Sair')
        option = int(input())
        if(option == 1):
            writeMessage()
        elif(option == 2):
            findKey()
        elif(option == 3):
            print(hash)
        elif(option == 4):
            print(routingTable)
        elif(option == 0):
            sys.exit()
        else:
            print('Opção inexistente')
        time.sleep(1)
        input('\n\n\nPressione qualquer tecla para continuar...\n')


if __name__ == '__main__':
    main()
