import tkinter
import tkinter.messagebox

class MyGUI:
    def __init__(self):
        # Create the main window widget.
        self.main_window = tkinter.Tk()

        self.top_frame = tkinter.Frame()
        self.bottom_frame = tkinter.Frame()
        
        self.prompt_label = tkinter.Label(self.top_frame, text='Digital Identity')
        self.prompt_label.pack(side='top')
        
        self.register_button = tkinter.Button(self.bottom_frame, text='Register', command=self.registerPage)
        '''self.share_button = tkinter.Button(self.main_window,text='Share', command=self.do_something)
        self.store_button = tkinter.Button(self.main_window,text='Store/Update', command=self.do_something)
        self.manage_button = tkinter.Button(self.main_window,text='Manage', command=self.do_something)
        '''
        self.register_button.pack()

        self.top_frame.pack()
        self.bottom_frame.pack()

        self.main_window.title('Our BlockChain')
        # Enter the tkinter main loop.
        tkinter.mainloop()


    def registerPage(self):
            # Display an info dialog box.
            tkinter.messagebox.showinfo('Response', 'Creating your private key\
                                        \n\nBefore we get started, we will provide you with mnemonic phrase that can be used to recover your private key.\
                                        \nYour private key will be used to store, update, or retrieve your personal information\
                                        \n\nYou MUST secure the mnemonic phrase and safe guard it in some place private, same as your private key')\

            #Creates new window 
            self.register_window = tkinter.Toplevel(self.main_window)
            #changes the size of the window
            #self.register_window.attributes('-fullscreen', True)
            self.register_window.geometry('1920x1080')
            #exit the page with the exit button
            #self.register_window.bind("<Escape>", self.end_fullscreen)

            top_frame = tkinter.Frame(self.register_window)
            mid_frame = tkinter.Frame(self.register_window)
            bottom_frame = tkinter.Frame(self.register_window)
            prompt_label = tkinter.Label(top_frame, text='Mnemonic Phrase')
            prompt_label.pack(side='top')


            top_frame.pack()
            self.register_window.title('Register')
            tkinter.mainloop()
    def end_fullscreen(self, event=None):
        self.register_window.destroy
        return "break"
# Create an instance of the MyGUI class.
if __name__ == '__main__':
    my_gui = MyGUI()
