import time
import socket


# 서버의 주소입니다. hostname 또는 ip address를 사용할 수 있습니다.
# HOST = '127.0.0.1'  
HOST = '165.132.105.40'  
# 서버에서 지정해 놓은 포트 번호입니다. 
PORT = 10036



# 소켓 객체를 생성합니다. 
# 주소 체계(address family)로 IPv4, 소켓 타입으로 TCP 사용합니다.  
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 지정한 HOST와 PORT를 사용하여 서버에 접속합니다. 
client_socket.connect((HOST, PORT))
print("connected")

# a = [1, 1, 1, 1]
# b = [1, 2, 1, 2]

# temp1 = list(map(str, a))
# temp1 = '\t'.join(temp1)
# temp1 = temp1 + '\n'

# temp2 = list(map(str, b))
# temp2 = '\t'.join(temp2)
# temp2 = temp2 + '\n'

temp1 = "a"
temp1 = temp1 + '\n'

try :
    while True :
        print("data send : ", temp1)
        client_socket.sendall(temp1.encode())
        time.sleep(1)
except :
    client_socket.close()


# 메시지를 전송합니다. 
# for i in range(20) :
#     client_socket.sendall(temp_str.encode())
#     print("send data :", i)
#     time.sleep(1)


# # 메시지를 수신합니다. 
# data = client_socket.recv(1024)
# print('Received', repr(data.decode()))

# 소켓을 닫습니다.
