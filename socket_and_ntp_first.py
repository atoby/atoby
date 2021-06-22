import socket  # Import socket modulesssssasdasdasd
import threading
import time
import RPi.GPIO as GPIO
import signal
codeset='UTF-8'  # or 'Latin-1' or 'UTF-8'

#BCM Library
GPIO.setmode(GPIO.BCM)

led=3
GPIO.setup(led, GPIO.OUT)
GPIO.output(led, False)
synced = False

#https://www.youtube.com/watch?v=A97QLHAqNuw&list=PL0Llpc8Y6FSOgMo1PGMOfJRKPGJD2DM2-&index=9
exit_event = threading.Event()

def handle_connection(connection,client_address):
    try:
        
        print('Got connection from %s' % str(client_address))
        
        connection.sendall(("1").encode(codeset))
        

        while True:
            
            byte_data = connection.recv(300)
            data = byte_data.decode(codeset)
            print('%s received: "%s"' % (str(client_address), data))

            if exit_event.is_set():
                break

            if data == "I am synced!":
                synced = True               

            if synced:
                synced = False
                break
        i = 0

        while i < 20: # 10 sek flashen
            zeit = int(time.time()*1000.0) #milliseconds! 
            milliseconds = abs(zeit) % 1000 

            if exit_event.is_set():
                break
        
            if (milliseconds >= 0 and milliseconds < 10) or (milliseconds >= 150 and milliseconds < 160):
                #GPIO.output(led, True)
                pass
            if (milliseconds == 0 ) or (milliseconds == 150):   
                i = i+1
                print("Blinkiblink")
            else:
                #GPIO.output(led, False)
                pass
            
                
        connection.sendall(("2").encode(codeset))
        print("sent 2 to shutdown")

    finally:
        # Clean up the connection
        connection.close()
        #GPIO.cleanup()	

def signal_handler(signum, frame):
    exit_event.set()


signal.signal(signal.SIGINT, signal_handler)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket object
host = '10.79.114.254'  # wlan0 NIC
port = 54111  # Reserve a port for your service. Allowed Ports 49152-65535 - HEX+DEC

##following steps  to use port again: https://subscription.packtpub.com/book/networking_and_servers/9781849513463/1/ch01lvl1sec18/reusing-socket-addresses
# Get the old state of the SO_REUSEADDR option
old_state = s.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR )
print "Old socket state: %s" %old_state
# Enable the SO_REUSEADDR option
s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
new_state = s.getsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR )
print "New socket state: %s" %new_state

##
skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
skt.bind((host, port))  # Bind to the port

skt.listen(1)  # Now wait for client connection.
print ("Listening on port: %s " %port)

#list of all threads:
threads = []
while True:
    if exit_event.is_set():
        break
    connection, client_address = skt.accept()  # Establish / get one connection with client.
#    handle_connection(connection,client_address)   # handle connections one by one
    # or start new thread for each connection
    t=threading.Thread(target=handle_connection,args=(connection,client_address))
    t.start()
    threads.append(t)
    # and continue with loop accepting next connection
    print(threads)
    
#s.close()
