import PySimpleGUI as sg
import socket
import threading


server = socket.socket()

sg.theme('DefaultNoMoreNagging')

# All the stuff inside your window.
layout = [  [sg.Text('Port Number: '),sg.InputText(size=(30,2),key='-PORT-'),sg.Button('Start Listening',key='-LISTEN-', disabled=False)],
            [sg.Text(key='-ERROR-')],
            [sg.Multiline(size=(60,10), key='-MSG_BOX-',disabled=True)],
            [sg.Multiline(key='-SERVERINPUT-',enable_events=True), sg.Button('Send',key='-SEND-',disabled=True)],
            [sg.Button('Close Server',disabled=True,key='-CLOSE-')] 
            ]



# Create the Window
window = sg.Window('Server', layout,finalize=True)

messages = [] #for appending messages on the console.
clients = [] #saving all connected clients.




#This thread is responsible for retriving data from a client and passing it down to other connected clients.
def new_client(clientSocket,clientAddress):
    while True:
        
        try:
            clientData = clientSocket.recv(2048).decode('utf-8')

            
        except socket.error as e:
            window['-ERROR-'].update("Client_Thread: "+str(e))
            clientSocket.close()
            clients.remove(clientSocket)
            break

# if dissconected message recived from the client, then close that socket.
        if clientData == 'Disconnected':
            message = "Client: "+str(clientAddress)+"Disconnected!"
            messages.append(message)
            window['-MSG_BOX-'].update('\n'.join(messages))
            clients.remove(clientSocket)
            #clientSocket.close()


        clientData = str(clientAddress) + ': ' + clientData

        message = "MESSAGE:"+clientData
        messages.append(message)
        window['-MSG_BOX-'].update('\n'.join(messages))

        
#all other clients except the sending client is being sent the message
        for otherclients in clients:
            if otherclients != clientSocket:
                otherclients.sendall(clientData.encode())


#Server Thread is responsible for accepting connections from the client and creates a client thread for each connected client.        
def server_thread():

    while True:
        try:
            server.listen(10) 
                
            clientSocket,clientAddress = server.accept()
            clients.append(clientSocket)

            message = "Client: "+str(clientAddress)+"Connected!"
            messages.append(message)
            window['-MSG_BOX-'].update('\n'.join(messages))

            serverToClientMessage = "***You are Connected to the server**"  
            clientSocket.sendall(serverToClientMessage.encode())

            client_thread = threading.Thread(target=new_client, args=(clientSocket,clientAddress)) #client thread being created
            client_thread.start()

        except socket.error as e:
            window['-ERROR-'].update("Server_Thread: "+str(e))
            break

    
        


# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break



    if event=='-SERVERINPUT-':
        if values['-SERVERINPUT-'] == '' or values['-SERVERINPUT-'] == ' ' or None:
            window['-SEND-'].update(disabled=True)
        else:
           window['-SEND-'].update(disabled=False)


    if event == '-LISTEN-':  
        
        if len(clients)!=0:
            clients = []
        
        try:
            server = socket.socket()
            if int(values['-PORT-']) >=0 and int(values['-PORT-']) <=65536:
                window['-ERROR-'].update(" ")
                server.bind(('localhost',int(values['-PORT-']))) #SERVER BIND
                print(server)
                serverThread = threading.Thread(target=server_thread, args=())
                serverThread.start()
                message = "Server is now listening on Port: "+values['-PORT-']
                messages.append(message)
                window['-MSG_BOX-'].update('\n'.join(messages))

                window['-LISTEN-'].update(disabled=True)
                window['-CLOSE-'].update(disabled=False)
            else:
                window['-ERROR-'].update("Port Number out of Range!")



        except socket.error as e:
            #new_client.join()
            window['-ERROR-'].update('LISTEN: '+str(e))




    if event == '-SEND-': #when server sends message, it is sent to all clients.

        try:
            messages.append('You: '+values['-SERVERINPUT-'])
            window['-MSG_BOX-'].update('\n'.join(messages)) 
            window['-SERVERINPUT-'].update('')
            window['-SEND-'].update(disabled=True)
            for c in clients:
                data = 'Server: ' + ' ' + values['-SERVERINPUT-']
                c.sendall(data.encode())
            
        except socket.error as e:
            window['-ERROR-'].update("-SEND-: "+str(e))

    if event == '-CLOSE-': #When server closes the sever, it alerts all clients and disconnects all clients.

        try:
            window['-LISTEN-'].update(disabled=False)
            window['-CLOSE-'].update(disabled=True)
            messages.append('Server Shutdown.')
            window['-MSG_BOX-'].update('\n'.join(messages)) #add server message on the messagebox
            for c in clients:
                data = '***SERVER SHUTDOWN***'
                c.sendall(data.encode())
                c.close()
                
            server.close()
        except socket.error as e:
            window['-MSG_BOX-'].update('CLOSE: '+str(e)) #add server message on the messagebox
            #server.close()
        



   
    





server.close()
window.close()