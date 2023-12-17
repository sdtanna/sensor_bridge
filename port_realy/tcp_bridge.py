import serial
import socket
import threading

# Configuration for your serial ports
cliCom = '/dev/ttyS1'  # Change to your first serial port
dataCom = '/dev/ttyS2'  # Change to your second serial port
baud_rate = 9600  # Modify as per your requirement

# TCP server configuration
tcp_ip = '0.0.0.0'  # Listening on all interfaces
tcp_port = 5000  # TCP port

# Initialize serial connections
ser1 = serial.Serial(cliCom, 115200,parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=0.6)
ser2 = serial.Serial(dataCom, 921600,parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=0.6)

# TCP server setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((tcp_ip, tcp_port))
server_socket.listen(1)
print(f"TCP Server listening on {tcp_ip}:{tcp_port}")

# Client handler function
def client_handler(client_socket):
    while True:
        # Read data from serial ports
        data1 = ser1.read(ser1.in_waiting or 1)
        data2 = ser2.read(ser2.in_waiting or 1)

        # Send data to TCP client
        if data1:
            client_socket.sendall(data1)
        if data2:
            client_socket.sendall(data2)

        # Receive data from TCP client
        try:
            client_data = client_socket.recv(1024)
            if client_data:
                # Write data to serial ports
                ser1.write(client_data)
                ser2.write(client_data)
        except:
            break

# Accepting clients
while True:
    client_sock, addr = server_socket.accept()
    print(f"Connection from {addr}")
    client_thread = threading.Thread(target=client_handler, args=(client_sock,))
    client_thread.start()
