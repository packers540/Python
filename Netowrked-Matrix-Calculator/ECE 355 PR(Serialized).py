#Main Program Libraries
import socket
import thread
import os
import pickle

#GUI Libraries
import Tkinter
from Tkinter import *
import tkMessageBox
import tkFileDialog

#Timing Library
import timeit
import time

global button
button = 0

global ping_enabled
ping_enabled = True

top = Tkinter.Tk()
top.title("Matrix Calculator!")


#----------Server Side of the Program----------

def server():
    
    while 1:
        #ping_enabled = True
    
        global sent_array_b_rows
        global sent_array_a
        global sent_array_b
        sent_array_a = []
        sent_array_b = []
        sent_array_b_rows = 0
        
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        server.bind((socket.gethostname(), 12345))
        server.listen(1)

        client, addr1 = server.accept()
        client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        #print "Connection from:", addr1[0]

        data = client.recv(1024)

        #if data received is not a ping expect 2 matricies

        if (data != 'ping'):

            ping_enabled = False
            
            try:
                #receive row element(Assume if not ping it is a row of a matrix)
                temp1 = data


                #listen for second piece of information
                server.listen(1)
                client, addr2 = server.accept()
                client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                
                #looks for connection from same host for 11 seconds, if itmeout drop connection
                timeout = time.time() + 11 
                while (addr2[0] != addr1[0]):            
                    server.listen(1)
                    client, addr2 = server.accept()
                    client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    if time.time() > timout:
                        server.close()
                        client.close()
                        break
                    
                #receive column
                temp2 = client.recv(1024)

                
                #convert serialized data back into objects
                sent_array_a = pickle.loads(temp1)
                sent_array_b = pickle.loads(temp2)

                #calculate a row by column
                sent_result = calculate_local_1by1()
            
                #send Result
                server.listen(1)                
                client, addr3 = server.accept()
                client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

                #looks for connection from same host for 11 seconds, if itmeout drop connection
                timeout = time.time() + 11
                while (addr3[0] != addr1[0]):            
                    server.listen(1)
                    client, addr2 = server.accept()
                    client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    if time.time() > timeout:
                        server.close()
                        client.close()
                        break
                        
                #Convert result to string (byte) and send    
                client.send(str(sent_result))
                
            except:
                None

        #close sockets
        client.close()        
        server.close()

    
#------------Start Server Thread On Startup----------

thread.start_new_thread(server, ())


#-----------Check Who is available on the network---------

def checkwhoisup():
    global uphosts
    global live
    live = False


    #wait here until user presses connect button
    while (not live):
        None

    temp = E1.get()
    n = 0
    while temp[-n] != '.':
        n += 1
    
    if temp[-3:] != '/24':
        print "This Program Only Accepy Subnets That are 24 Bits Long! Please Re-Enter a Correct Value!"
        checkwhoisup()
    else:
        print "Scanning for Available Hosts on " + E1.get() + "......"
        B5.config(state = "disabled")
        
    subnet = temp[:-n + 1]
      
    #Send to every Host on subnet

    localhost_ip = socket.gethostbyname(socket.gethostname())
    
    while (1):
        temp = []
        for x in range(2, 255):
            if ping_enabled:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    s.settimeout(.1)
                    addr = subnet + str(x)
                    s.connect((addr, 12345))
                    s.send('ping')
                    s.close()

                    #Exclude the local IP on the NAT
                    if (subnet + str(x) != localhost_ip):
                        temp.append(subnet + str(x))
                        uphosts = temp

                    #Allow the program to send data to localhost
                    #temp.append(subnet + str(x))
                    #uphosts = temp
                        
                except:
                    #print 'Host 192.168.0.'+ str(x), "Is not up ATM!"
                    None
        
#-------------Start Check who is up thread-----------
        
thread.start_new_thread(checkwhoisup, ())
    
#----------Start Scanning Network For Clients When Connect Button Pressed-------

def start_scan():
    global live
    live = True
    
#------------Read Files From Browse Window---------
#----------Put Files in respective Arrays----------

def get_matrix_a():
    global button
    matrix_file_a = tkFileDialog.askopenfile()
    global array_a
    global res_row
    res_row = 0
    array_a = []
    for line in matrix_file_a.readlines():
        array_a.append([int(x) for x in line.split()])
        res_row += 1
    button += 1
    #If two files selected enabled buttons
    if button == 2:
        B1.config(state = "normal")
        B4.config(state = "normal")
    
def get_matrix_b():
    global button
    matrix_file_b = tkFileDialog.askopenfile()
    global array_b
    global array_b_rows
    array_b_rows = 0
    array_b = []
    for line in matrix_file_b.readlines():
        array_b.append([int(x) for x in line.split()])
        array_b_rows += 1
    button += 1
    #If two files selected enable buttons
    if button == 2:
        B1.config(state = "normal")
        B4.config(state = "normal")
    
    
#---------Calculating The Result Localy(No Network Only CPU)-----------

def calculate_local():
    global result
    result = []
    global res_col
    res_col = len(array_b[0])

    #Time calculation Time
    start = timeit.default_timer()

    for z in range(0, res_row):
        temp_array = []
        for y in range(0, res_col):
            temp = 0
            for x in range(0, array_b_rows):
                temp += ((array_a[z][x]) * (array_b[x][y]))
            temp_array.append(temp)
        result.append(temp_array)

    print result

    stop = timeit.default_timer()

    print stop - start, "Seconds to Compute!"


#----------Caclulate 1 Row By 1 Column-----------

def calculate_local_1by1():
    temp = 0
    for x in range(0, len(sent_array_b)):
        temp += ((sent_array_a[x]) * (sent_array_b[x]))
    return temp
        
#--------Calculate The Result With P2P computing---------

def calculate_p2p():
    global all_remaining_calcs
    all_remaining_calcs = []


    #If there are no available hosts give warning and wait for a host to become available
    if len(uphosts) == 0:
        tkMessageBox.showinfo("Program Failure", "There are NO Available Hosts. Please Try Again Later!")
        return 0

    #Check to make sure the matricies can be multiplied
    if len(array_a[0]) != len(array_b):
        tkMessageBox.showinfo("Program Failure", "Demension of Matrcies Can't Be Multiplied!")
        return 0

    #Time the P2P Calculation
    global p2p_start
    p2p_start = timeit.default_timer()

    ping_enabled = False

    global result
    result = [[None for x in xrange(len(array_b[0]))] for x in xrange(len(array_a))] 

    #Number of calculations needed to be sent out
    global calcnum
    calcnum = len(array_a) * len(array_b[0])
    
    threadcount = [None] * len(uphosts)

    #Determine how many times a thread will run(number of jobs per host)

    for x in range (0, len(uphosts)):
        threadcount[x] = (calcnum - (calcnum % len(uphosts)))/len(uphosts)

    remaining = calcnum % len(uphosts)

    while remaining > 0:
        threadcount[remaining - 1] += 1
        remaining += -1

    #Calculate what rows and columns each host is going to get
    host_calcs = [[None for x in xrange(threadcount[0])] for x in xrange(len(uphosts))] 
    
    N = 0
    Z = 0

    for x in range (0, len(array_a)):
        for y in range (0, len(array_b[0])):
            if N == (len(uphosts)):
                N = 0
                Z += 1
            host_calcs[N][Z] = (x, y)
            N += 1


    #10 seconds till timeout        
    global W
    W = 10

    #Variable to keep track of how many jobs were dropped
    global check
    check = 0

    #Create a tread for each available host
    for x in range (0, len(uphosts)):
        thread.start_new_thread(p2pcalc, (x, host_calcs[x], threadcount[x]))

    #wait till done then resend dropped jobs
    check_done()
    
#----------Send each part of the matrix to host and what for result--------                

def p2pcalc(hostnum, host_calcs, threadcount): #host number, rows/column needed, times to repeat

    delete = 0
    remaining_calcs = []
    temp1 = 0

    
    global check
    for x in range(0, threadcount):                     

        #attempt to send data to a host on available host list
        try:
            A1 = pickle.dumps(array_a[host_calcs[x][0]])
            B1 = pickle.dumps(column(array_b, host_calcs[x][1]))

            #Send Row
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            client.settimeout(W)
            client.connect((uphosts[hostnum], 12345))
            client.send(A1)
            client.close()

            #Send Column
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            client.settimeout(W)
            client.connect((uphosts[hostnum], 12345))
            client.send(B1)
            client.close()

            #Connection for recieving result
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            client.settimeout(W)
            client.connect((uphosts[hostnum], 12345))       
            data = client.recv(1024)
            client.close()

            result[host_calcs[x][0]][host_calcs[x][1]] = int(data)

        #if unable to send to a host save job and increment check    
        except:
            #incremenmt number of failed jobs
            print "Failed To Receive Data"
            check += 1
            temp1 += 1
        
            remaining_calcs.append((host_calcs[x][0], host_calcs[x][1]))
            all_remaining_calcs.append(remaining_calcs)
            
        print "-"

    
    #if number of dropped jobs > x, delete the host from uphosts list

    if temp1 == threadcount:
        print "Deleted Host"
        #try:
            #uphosts[hostnum] = None
        #except:
         #   None
    
#return the column of matrix
def column(matrix, i):
    return [row[i] for row in matrix]


#wait until all hosts have either sent back results or dropped
def check_done():
    global check
    global p2p_stop
    done = False
    comp_done = False
    while (not comp_done):
     
        while(not done):
            temp = check

            #Check to see if entire result array is filled
            for x in range(0, len(array_a)):
                for y in range(0, len(array_b[0])):
                    if result[x][y] != None:
                            temp += 1
                            
            #If entire array is filled done with calculation
            if temp == len(array_a) * len(array_b[0]):
                done = True
            
        #Need to wait for cpu to append remaining jobs and delete bad hosts
                
        time.sleep(.1)       #BAD but works 
         
        #if there were no dropped jobs end program and print result 
        if check == 0:
            #ping_enabled = True
            p2p_stop = timeit.default_timer()
            print result
            print p2p_stop - p2p_start, "Seconds to Cumpute"
            comp_done = True

        #If there were dropped jobs split up jobs and resend    
        else:
            print "RESENDING!!!"
            done = False
            calcnum = check
            check = 0

            #clean up delete hosts
            for x in range(0, len(uphosts)):
                if uphosts[x] == None:
                    uphosts.remove(None)

            #Split up remaining jobs same as before
            remaining_threadcount = [None] * len(uphosts)
                    
            for x in range (0, len(uphosts)):
                remaining_threadcount[x] = (calcnum - (calcnum % len(uphosts)))/len(uphosts)

            remaining = calcnum % len(uphosts)

            while remaining > 0:
                remaining_threadcount[remaining - 1] += 1
                remaining += -1

            #Send remaining jobs remaining jobs
            for x in range (0, len(uphosts)):
                try:
                    thread.start_new_thread(p2pcalc, (x, all_remaining_calcs[x], remaining_threadcount[x]))
                except:
                    None
    
#-------------------------------------------------------------------------

#---------Background--------
C = Tkinter.Canvas(top, bg="green", height = 300, width = 400)

#----------Directions Message--------
var = StringVar()
directions = Message(top, textvariable=var, relief=RAISED)
var.set("Welcome to the p2p matrix calculator.  To use the program select two files containing matrix A and matrix B respectfully.  Then click on the calculate button for the calculation you wish to perform.")

#--------Entry Fields-------
v = StringVar()
v.set("192.168.0.0/24")
E1 = Entry(top, textvariable = v)


#---------Buttons---------
B1 = Tkinter.Button(top, text = "Calculate P2P", command = calculate_p2p)
B2 = Tkinter.Button(top, text = "Browse", command = get_matrix_a)
B3 = Tkinter.Button(top, text = "Browse", command = get_matrix_b)
B4 = Tkinter.Button(top, text = "Calculate Locally", command = calculate_local)
B5 = Tkinter.Button(top, text = "Connect to Network", command = start_scan)
B1.config(state = "disabled")
B4.config(state = "disabled")

#---------Labels---------
L1 = Label(top, text = "Matrix P2P Calculator")
L2 = Label(top, text = "Matrix A")
L3 = Label(top, text = "Matrix B")
    
#--------PLACING ELEMENTS ON WIDGET------
L1.place(x=150,y=10)
L2.place(x=10, y=50)
L3.place(x=220, y=50)
directions.place(x=220, y=90)

C.pack()

E1.place(x=30, y=150)

B1.place(x=200, y=220)
B2.place(x=100, y=50)
B3.place(x=310, y=50)
B4.place(x=300, y=220)
B5.place(x=40, y=180)

top.mainloop()
#---------End of GUI----------
os._exit(0)
