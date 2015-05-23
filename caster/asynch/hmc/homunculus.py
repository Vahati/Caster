import SimpleXMLRPCServer
from SimpleXMLRPCServer import *
from Tkinter import (Label, Text)
import signal
from threading import Timer

import Tkinter as tk


try: # Style C -- may be imported into Caster, or externally
    BASE_PATH = "C:/NatLink/NatLink/MacroSystem/"
    if BASE_PATH not in sys.path:
        sys.path.append(BASE_PATH)
finally:
    from caster.lib import settings  

def communicate():
    return xmlrpclib.ServerProxy("http://127.0.0.1:" + str(settings.HMC_LISTENING_PORT))

class Homunculus(tk.Tk):
    def __init__(self, htype, data=None):
        tk.Tk.__init__(self, baseName="")
        self.setup_XMLRPC_server()
        self.htype = htype
        self.completed = False
        self.max_after_completed=10
        

        self.title(settings.HOMUNCULUS_VERSION)
        self.geometry("300x200+" + str(int(self.winfo_screenwidth() / 2 - 150)) + "+" + str(int(self.winfo_screenheight() / 2 - 100)))
        self.wm_attributes("-topmost", 1)
        self.protocol("WM_DELETE_WINDOW", self.xmlrpc_kill)
 
        # 
        if self.htype == settings.QTYPE_DEFAULT:
            Label(self, text="Enter response then say 'complete'", name="pathlabel").pack()
            self.ext_box = Text(self, name="ext_box")
            self.ext_box.pack(side=tk.LEFT)
        elif self.htype == settings.QTYPE_INSTRUCTIONS:
            self.data=data.split("|")
            Label(self, text=" ".join(self.data[0].split("_")), name="pathlabel").pack()
            self.ext_box = Text(self, name="ext_box")
            self.ext_box.pack(side=tk.LEFT)
        
        
        # start server, tk main loop
        def start_server():
            while not self.server_quit:
                self.server.handle_request()  
        Timer(1, start_server).start()
        Timer(0.05, self.start_tk).start()
        # backup plan in case for whatever reason Dragon doesn't shut it down:
        Timer(300, self.xmlrpc_kill).start()
    
    def start_tk(self):
        self.mainloop()
    
    def setup_XMLRPC_server(self): 
        self.server_quit = 0
        self.server = SimpleXMLRPCServer(("127.0.0.1", settings.HMC_LISTENING_PORT), allow_none=True)
        self.server.register_function(self.xmlrpc_do_action, "do_action")
        self.server.register_function(self.xmlrpc_complete, "complete")
        self.server.register_function(self.xmlrpc_get_message, "get_message")
        self.server.register_function(self.xmlrpc_kill, "kill")
    
    def xmlrpc_kill(self):
        self.server_quit = 1
        self.destroy()
        os.kill(os.getpid(), signal.SIGTERM)
        
    def xmlrpc_complete(self):
        self.completed = True
        self.after(10, self.withdraw)
        Timer(self.max_after_completed, self.xmlrpc_kill).start()
        
    def xmlrpc_get_message(self):
        '''override this for every new child class'''
        if self.completed:
            Timer(1, self.xmlrpc_kill).start()
            return [self.ext_box.get("1.0", tk.END), self.data[1]]
        else:
            return None
    
    def xmlrpc_do_action(self, action, details=None):
        '''override'''

