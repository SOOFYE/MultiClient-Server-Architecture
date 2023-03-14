import PySimpleGUI as sg
import socket
import threading


client = socket.socket()

sg.theme('LightGrey')

# All the stuff inside your window.
layout = [  [sg.Text('IP-Address: '),sg.InputText(size=(15,2),key='-IPADDRESS-',enable_events=True),sg.Text('Connect to Port: '),sg.InputText(size=(15,2),key='-PORT-',enable_events=True),sg.Button('Connect',key='-CONNECT-',disabled=True)],
            [sg.Text(key='-ERROR-')],
            [sg.Multiline(size=(60,10), key='-MSG_BOX-',disabled=True)],
            [sg.Multiline(key='-CLIENTINPUT-',enable_events=True), sg.Button('Send',key='-SEND-',disabled=True)],
            [sg.Button('Disconnect',key='-DISC-',disabled=True)] ]

# Create the Window
window = sg.Window('Client', layout)

#This client thread recieves messages from the server
def client_function():

    while True:

        try:
            messageFromServer = client.recv(2048).decode('utf-8')
            if not messageFromServer:
                raise ConnectionResetError #if connectionis closed this event is raised
            messages.append(messageFromServer)
            if messageFromServer == '***SERVER SHUTDOWN***':
                #client.close()
                window['-CONNECT-'].update(disabled=False)
                window['-DISC-'].update(disabled=True)

            window['-MSG_BOX-'].update('\n'.join(messages))
        except ConnectionResetError:
            window['-ERROR-'].update("Connection Error")
            break


messages = []


# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break

    if event == '-CLIENTINPUT-':
        if values['-CLIENTINPUT-'] == '' or values['-CLIENTINPUT-'] == ' ':
            window['-SEND-'].update(disabled=True)
        else:
            window['-SEND-'].update(disabled=False)
    
    if event == '-IPADDRESS-' or event=='-PORT-':
        if (values['-IPADDRESS-']==' ' or values['-IPADDRESS-']=='' or values['-PORT-']=='' or values['-PORT-']==' '):
            window['-CONNECT-'].update(disabled=True)
        else:
            window['-CONNECT-'].update(disabled=False)


    if event == '-CONNECT-':
        client = socket.socket()
        try:
            window['-ERROR-'].update("")
            if int(values['-PORT-']) >=0 and int(values['-PORT-']) <=65536:
                window['-ERROR-'].update(" ")
                client.connect((values['-IPADDRESS-'],int(values['-PORT-'])))
                client_thread = threading.Thread(target=client_function, args=())
                client_thread.start()
                
                window['-CONNECT-'].update(disabled=True)
                window['-DISC-'].update(disabled=False)
            else:
                window['-ERROR-'].update("Port Number out of Range!")
       
        except socket.error as e:
            print(client)
            window['-ERROR-'].update(e)

        

    if event == '-SEND-': #handles client sending message to the server
        
        try:
            window['-ERROR-'].update("")
            messages.append('You: '+values['-CLIENTINPUT-'])
            window['-MSG_BOX-'].update('\n'.join(messages)) #add server message on the messagebox
            window['-CLIENTINPUT-'].update('') #clear input field
            window['-SEND-'].update(disabled=True)
            client.sendall(values['-CLIENTINPUT-'].encode())

        except socket.error as e:
            window['-ERROR-'].update(e)

    if event == '-DISC-': #handles when client dissconnected from the server
        mess = 'Disconnected'
        client.sendall(mess.encode())
        #time.sleep(1)
        #client.close()
        window['-CONNECT-'].update(disabled=False)
        window['-DISC-'].update(disabled=True)
        


client.close()
window.close()