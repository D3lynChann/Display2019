import socket

localIp = '172.18.184.242'      #lab linux
#localIp = '172.18.184.163'     #lab
#localIp = '192.168.2.106'      #yj home
#localIp = '172.26.21.248'       #sf home

def initWebEnvC(ip = localIp, port = 8888):
    ip_port = (ip, port)
    sok = socket.socket()
    sok.connect(ip_port)
    sok.settimeout(20)
    return sok
    
def initWebEnvS(ip = localIp, port = 8888):
    ip_port = (ip, port)
    sok = socket.socket()
    sok.bind(ip_port)
    sok.listen(20)
    conn, address = sok.accept()
    return sok, conn, address    
