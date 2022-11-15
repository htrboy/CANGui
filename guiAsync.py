from tkinter import *
#import time
#import os
import threading
import random
import queue
import can
import signal
import sys

root = Tk()


from can import message
from can.interface import Bus

can.rc['interface'] = 'kvaser'
can.rc['channel'] = '0'
can.rc['bitrate'] = 100000
can.rc['receive_own_messages'] = True

bus = Bus()
reader = can.BufferedReader()
#notifier = can.Notifier(bus, [reader])
#listener = can.Listener()

def sigint_handler(signal, frame):
    print("keyboard interrupt")
    sys.exit(0)

def send_one():
    msg = can.Message(arbitration_id=0x01A00000, data=[0, 0, 0, 0, 0, 0, 0, 0],
                      is_extended_id=True)
    bus.send(msg)

def receiveMessages():
    inMsg = reader.get_message()
    if inMsg is not None:
        #msg = bus.recv()       
        mesgID= inMsg.arbitration_id
        mesgData = inMsg.data
        incomingMessage = ("ID: " + mesgID, "Data: " + mesgData)
        return incomingMessage

    '''
    #mesg = []
    #while mesg is not None:
    #while True:
    #pd = reader.get_message(3)
    if pd is None:
        #break
        mesg.append(pd)
     
    try:
        df=pd.DataFrame(index=range(1),columns=range(10))
        df[0][0]=pd.timestamp
        df[1][0]=pd.arbitration_id
        candavec=list(pd.data)
        lengthdata=len(candavec)
        for i in range(0,lengthdata):
            df[i+2][0]=candavec[i]
        dfcan=dfcan.append(df)

    except Exception as sigint_handler:
        dfcan.rename(columns={0:'Timestamp',  1:'Id',  2:'D1',  3:'D2',  4:'D3',  5:'D4',  6:'D5',  7:'D6',  8:'D7',  9:'D8'}, inplace=True)
        dfcan.set_index(pd.to_datetime(dfcan[0], unit='s'), inplace=True)
        dfcan.to_csv('dfcan.csv')
          
        
            
    return mesg
    '''

class GuiPart:
    def __init__(self, master, queue, endCommand, root):
        self.queue = queue

        self.root = root
        self.root.title('TEST GUI')
        self.frame1 = Frame(self.root)
        # Set up the GUI
        # Add more GUI stuff here depending on your specific needs
        self.window_width = 600
        self.window_height = 400

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.center_x = int(self.screen_width/2 - self.window_width / 2)
        self.center_y = int(self.screen_height/2 - self.window_height / 2)

        self.root.geometry(f'{self.window_width}x{self.window_height}+{self.center_x}+{self.center_y}')
        self.root.resizable(1, 1) #x,y resizable
        #root.minsize(600, 400) 
        #root.maxsize(1000, 800) 

        self.root.attributes('-topmost', 1)

        '''
        Construct the first frame, frame1
        '''
        self.frame1 = LabelFrame(root, text="Serial", bg="green", fg="white", padx=5, pady=5)
        
        # Displaying the frame1 in row 0 and column 0
        self.frame1.grid(row=0, column=0)
        
        # Constructing the button b1 in frame1
        self.b1 = Button(self.frame1, text="Setup")
        
        # Displaying the button b1
        self.b1.pack()
        
        # Constructing the second frame, frame2
        self.frame2 = LabelFrame(self.root, text="Test", bg="yellow", padx=5, pady=5)
        self.frame2.grid(row=0, column=1)
        self.b2 = Button(self.frame2, text="Send", command=send_one)
        self.b2.pack()

        # Construct Message frame for received messages
        self.frame3 = LabelFrame(self.root, text="Messages", bg="light cyan", fg="black", padx=15, pady=15)
        self.frame3.grid(row=1, column=0, columnspan=4, padx=5, pady=5)
        self.txtbx1 = Text(self.frame3, height=10, width=70 )
        self.text = self.processIncoming()
        #if text is not None:
        #txtbx1.insert(END, text)
        self.txtbx1.pack()

    def processIncoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.queue.qsize(  ):
            try:
                msg = self.queue.get(0)
                # Check contents of message and do whatever is needed. As a
                # simple test, print it (in real life, you would
                # suitably update the GUI's display in a richer fashion).
                if msg is not None:
                    print(msg)
                    self.txtbx1.insert(END, msg)
                    return msg
                
                #text = msg
                #return text
            except queue.Empty:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                pass
        

class ThreadedClient:
    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """
    def __init__(self, master):
        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI as well. We spawn a new thread for the worker (I/O).
        """
        self.master = master

        # Create the queue
        self.queue = queue.Queue(  )

        # Set up the GUI part
        self.gui = GuiPart(master, self.queue, self.endApplication, root)

        # Set up the thread to do asynchronous I/O
        # More threads can also be created and used, if necessary
        self.running = 1
        self.thread1 = threading.Thread(target=self.workerThread1)
        self.thread1.start(  )

        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.periodicCall(  )

    def periodicCall(self):
        """
        Check every 200 ms if there is something new in the queue.
        """
        self.gui.processIncoming(  )
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            import sys
            sys.exit(1)
        self.master.after(200, self.periodicCall)

    def workerThread1(self):
        """
        This is where we handle the asynchronous I/O. For example, it may be
        a 'select(  )'. One important thing to remember is that the thread has
        to yield control pretty regularly, by select or otherwise.
        """
        while self.running:
            # To simulate asynchronous I/O, we create a random number at
            # random intervals. Replace the following two lines with the real
            # thing.
            #time.sleep(rand.random(  ) * 1.5)
            #msg = rand.random(  )
            inMsg = bus.recv()
            #inMsg = reader.on_message_received
            #inMsg = reader.get_message()
            if inMsg is not None:
        #msg = bus.recv()       
                mesgID = inMsg.arbitration_id
                mesgData = inMsg.data
                incomingMessage = ("ID: " + str(mesgID), "Data: " + str(mesgData))
                #return incomingMessage
                #msg = receiveMessages()
                #self.queue.put(msg)
                self.queue.put(incomingMessage)

    def endApplication(self):
        self.running = 0

rand = random.Random(  )


client = ThreadedClient(root)
root.mainloop(  )