from tkinter.filedialog import *

import socket, threading, requests, time, playsound, math

class GUI(Frame):

    SLEEP = 0.01
    msgdict = dict()
    missing = list()
    last_received_message = ""
    HEADER = "%++++%"
    second = 0
    sending = 0
    played = 0
    retry = 0
    again = 0
    done = 0
    greatest = 0

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.checkVar = IntVar(value = 1)
        self.ip = StringVar(value = "25.137.210.200")
        self.name = StringVar(value = "Fatih")
        self.initUI()

    def initUI(self):
        self.pack(fill = BOTH, expand = TRUE)

        self.frame1 = Frame(self)
        self.frame1.pack(fill = X)

        self.frame2 = Frame(self)
        self.frame2.pack(fill = X, pady = (20, 0))

        self.frame3 = Frame(self)
        self.frame3.pack(fill = X, pady = (30, 0))

        mainLabel = Label(self.frame1, text = "Project 1", font = "ComicSans 25 italic")
        mainLabel.pack(pady = (15,0))

        destinationLabel = Label(self.frame2, text = "Enter Destination IP:", font = "ComicSans 12")
        destinationLabel.grid(row = 0, column = 0)

        self.destinationEntry = Entry(self.frame2, textvariable = self.ip)
        self.destinationEntry.grid(row = 0, column = 1, columnspan = 2, padx = 20)

        protocolLabel = Label(self.frame2, text = "Protocol:", font = "ComicSans 12")
        protocolLabel.grid(row = 1, column = 0, pady = 10)

        self.tcp = Radiobutton(self.frame2, text = "TCP", variable = self.checkVar, value = 1)
        self.tcp.grid(row = 1, column = 1, pady = 10)

        self.udp = Radiobutton(self.frame2, text = "UDP", variable = self.checkVar, value = 2)
        self.udp.grid(row = 1, column = 2, pady = 10)

        nameLabel = Label(self.frame2, text = "Name: ", font = "ComicSans 12")
        nameLabel.grid(row = 2, column = 0, pady = 10)

        self.name_widget = Entry(self.frame2, textvariable = self.name)
        self.name_widget.grid(row = 2, column = 1, columnspan = 2, pady = 10)
        self.name_widget.bind("<Return>", lambda event: self.screen())

        connectionButton = Button(self.frame3, text = "Start Connection => ", command = self.screen)
        connectionButton.pack()

        self.connectionLabel = Label(self.frame3, text = "Waiting for connecting to partner", font = "ComicSans 12", fg = "red")
        self.connectionLabel.pack()

    def screen(self):

        self.IP = self.destinationEntry.get()
        self.PORT = 54321
        self.PROTOCOL = socket.SOCK_STREAM if self.checkVar.get() == 1 else socket.SOCK_DGRAM
        self.name = self.name_widget.get()
        self.update_pro()

        frames = [self.frame1, self.frame2, self.frame3]

        for frame in frames:
            for widget in frame.winfo_children():
                widget.destroy()

        root.title("Chat Room")
        root.geometry("670x530+250+50")

        self.txt = Text(self.frame1, state = DISABLED)
        self.txt.grid(row = 0, column = 0, columnspan = 2)

        self.text = Text(self.frame2, height = 4, width = 44)

        self.text.grid(row = 0, column = 0)
        self.text.bind("<Return>", lambda event, data = 0, check = 1: self.send_chat(data, check))
        self.text.focus()

        scroll = Scrollbar(self.frame1, command = self.txt.yview)
        scroll.grid(row = 0, column = 2, sticky = "WENS")
        self.txt['yscrollcommand'] = scroll.set

        self.send = Button(self.frame2, text = "Send", height = 4, width = 9)
        self.send.grid(row = 0, column = 1)
        self.send.bind("<Button-1>", lambda event, data=0, check=1,: self.send_chat(data, check))


        self.musicButton = Button(self.frame2, text = "♪", height = 4, width = 9, command = self.music)
        self.musicButton.grid(row = 0, column = 2)

        self.browseButton = Button(self.frame2, text ="Browse", height = 4, width = 9, command = self.browse)
        self.browseButton.grid(row = 0, column = 3)

        if self.PROTOCOL == socket.SOCK_STREAM: self.initialize_tcp()
        else: self.initialize_udp()

    def initialize_tcp(self):

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.IP, self.PORT))
        self.socket = self.client_socket
        self.connection = "TCP"

        self.joined()

        self.listen_messages(self.client_socket)

    def initialize_udp(self):

        self.serverAddressPort = ("127.0.0.1", 12345)
        self.UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.UDPClientSocket.connect((self.IP, self.PORT))
        self.socket = self.UDPClientSocket
        self.connection = "UDP"

        self.joined()

        self.listen_messages(self.UDPClientSocket)

    def joined(self):

        self.socket.send(("joined:" + str(self.name).capitalize()).encode('utf-8'))
        self.txt["state"] = NORMAL
        self.txt.insert("end", "You are connected\n\n")
        self.txt.yview(END)
        self.txt["state"] = DISABLED

    def listen_messages(self, so):

        thread = threading.Thread(target = self.receive_message, args = (so, ))
        thread.start()

    def receive_message(self, so):
        done = 0
        transfer = 0
        opened = 0
        file = None

        while True:

            buffer = so.recv(1024)
            time.sleep(self.SLEEP)

            if self.again:
                print("resending the necessary file")
                mess = buffer.decode("cp437")

                number, msg, r = mess.split(self.HEADER)

                if msg != "done":
                    self.messages[int(number)] = msg.encode("cp437")
                    self.missing.remove(int(number))
                else:
                    self.again = 0
                    file = open(self.fileName, "wb")
                    break

            elif b"transfer_is_starting" in buffer:
                print("Transfer is starting")
                self.messages = dict()
                self.greatest = 0
                transfer = 1
                continue

            elif transfer:
                message = buffer.decode("cp437")

                try:
                    number, msg, r = message.split(self.HEADER)

                except IndexError:
                    msg = None
                    number = None
                    print(f"Error: {message}")

                if msg == "transfer_is_done":
                    print("Done")
                    done = 1
                    self.greatest = int(number)

                if not opened:
                    file = open(self.fileName, "wb")
                    opened = 1

                if done: break

                else:
                    try:
                        self.messages[int(number)] = msg.encode('cp437')
                    except ValueError:
                        print(f"Number: {number}")

            else:

                message = buffer.decode('utf-8')
                if "%+number+%" in message:
                    num = message.split("%+number+%")[1]

                    if num != "done":

                        msg = self.msgdict[int(num) + 1]
                        self.socket.send(msg.encode("cp437"))
                        time.sleep(self.SLEEP)

                    else:
                        time.sleep(self.SLEEP)
                        self.socket.send("%++++%done%++++%".encode("cp437"))

                elif "joined" in message:
                    user = message.split(":")[1]
                    message = user + " has joined"
                    self.txt["state"] = NORMAL
                    self.txt.insert('end', message + '\n\n')
                    self.txt.yview(END)
                    self.txt["state"] = DISABLED

                elif "Music" in message:

                    sound = message.split(": ")[1].lower()
                    self.music_thread(sound)

                    name = message.split("/")[1].split(".")[0]
                    self.txt["state"] = NORMAL
                    self.txt.insert("end", f"Sound {name} is played\n\n")
                    self.txt.yview(END)
                    self.txt["state"] = DISABLED

                elif "Document:" in message:

                    self.fileName = message.split(":")[2].split(",")[0].strip()
                    seq = message.split(":")[3].strip()

                    self.downloadLabel = Label(self.frame1, text=f"Document: {self.fileName},     Security: {seq.capitalize()}", fg="green", relief="raised")
                    self.downloadLabel.grid(row=1, column=0, pady=(20, 0), padx=(20, 0), sticky="w")

                    self.downloadButton = Button(self.frame1, text="Download File", state = DISABLED, bg = "lawngreen", command = self.permission)
                    self.downloadButton.grid(row=1, column=1, pady=(10, 0), sticky="w")

                elif "Let" in message:

                    self.send["state"] = NORMAL
                    self.send.bind("<Button-1>", lambda event, data = 0, check = 1, : self.send_chat(data, check))
                    self.sending = 1

                elif "Cancel" in message:

                    self.downloadLabel.destroy()
                    self.downloadButton.destroy()

                elif "changed_security" in message:
                    seq = message.split(":")[1].strip()

                    txt = f"Document: {self.fileName}, {5*' '} Security: {seq.capitalize()}"

                    self.downloadLabel["text"] = txt
                    self.downloadButton["state"] = NORMAL

                else:

                    if "transferred" in message:

                        self.downloadLabel.destroy()
                        self.cancelButton.destroy()

                    self.txt["state"] = NORMAL
                    self.txt.insert('end', message + '\n')
                    self.txt.yview(END)
                    self.txt["state"] = DISABLED

        print("Writing starts")

        last = self.greatest

        for i in range(1, last):
            if i not in self.messages and i not in self.missing:
                self.missing.append(i)

        state = len(self.missing)
        print(self.missing)

        if not state:
            print("%100 Percent of the message is received. (0 files are missing)")

            for i in sorted(self.messages):
                file.write(self.messages[i])

            self.again = 0

            message = f"{self.fileName} is transferred\n"
            self.txt["state"] = NORMAL
            self.txt.insert('end', message + '\n')
            self.txt.yview(END)
            self.txt["state"] = DISABLED

            self.downloadLabel.destroy()
            self.downloadButton.destroy()

            self.socket.send(message.encode("utf-8"))
            file.close()

        else:
            percent = (len(self.missing)/last) * 100
            print(f"{round(percent, 2)}% of the files are missing. ({len(self.missing)} files are missing)")
            self.resend()

        self.listen_messages(so)
        return "break"

    def resend(self):
        self.again = 1

        for num in self.missing:
            time.sleep(self.SLEEP)
            self.socket.send(f"%+number+%{num}".encode("utf-8"))

        self.socket.send(f"%+number+%done".encode("utf-8"))

    def send_chat(self, data, check):

        if self.sending:

            self.socket.send("0%++++%transfer_is_starting%++++%".encode("utf-8"))
            self.counter = 1

            file = open(f"{self.file.name}", "rb")
            l = file.read(1000)

            while l:
                messages = self.chunks(l)

                for msg in messages:
                    self.msgdict[self.counter] = msg
                    self.socket.send(msg.encode("cp437"))
                    time.sleep(self.SLEEP)

                l = file.read(1000)

            file.close()

            self.sending = 0
            time.sleep(self.SLEEP)
            self.socket.send(f"{self.counter}%++++%transfer_is_done%++++%".encode("cp437"))
            return

        elif check:
            data = self.text.get("1.0", END)

        message = ""

        if not self.sending:

            senders_name = f"{str(self.name).strip().capitalize()}: "
            message = senders_name + data.capitalize()

        if "Music" not in message and "Document:" not in message and "Let" not in message and "Cancel" not in message:

            self.txt["state"] = NORMAL
            self.txt.insert('end', message + '\n')
            self.txt.yview(END)
            self.txt["state"] = DISABLED
            self.text.delete(1.0, 'end')

        self.socket.send(message.encode("utf-8"))
        self.text.focus()
        return 'break'

    def chunks(self, string):

        messages = []
        send = f"{self.counter}%++++%{string.decode('cp437')}%++++%"

        if len(send) <= 1024:
            msg = send + "\x00" * (1024 - len(send))
            messages.append(msg)
            self.counter += 1
            return messages

        turn = math.ceil(len(str(string))/1000)
        step = 1000

        for i in range(turn):
            msg = string.decode('cp437')[i * step: (i + 1) * step]
            msg = f"{self.counter}%++++%{msg}%++++%"
            msg += "\x00" * (1024 - len(msg))
            messages.append(msg)
            self.counter += 1

        return messages

    def browse(self):

        self.file = askopenfile(initialdir='C:\\Users\Muhammed Fatih\\Downloads', title ="Select File", filetypes = (("PDF Files", "*.pdf"), ("All Files", "*.*")))
        self.file_name = self.file.name.split("/")[-1]

        self.security = "Checking..."
        self.send_chat(f"Document: {self.file_name}, Security: {self.security.capitalize()}", 0)
        self.security_thread()

        self.downloadLabel = Label(self.frame1, text = f"Document: {self.file_name}, Security: {self.security.capitalize()}", fg ="green", relief ="raised")
        self.downloadLabel.grid(row = 1, column  = 0, pady = (20, 0), padx = (20, 0), sticky ="w")

        self.cancelButton = Button(self.frame1, text = "Cancel Upload", command = self.cancel)
        self.cancelButton.grid(row = 1, column = 1, pady = (10, 0), sticky = "w")

        self.send["state"] = DISABLED
        self.send.unbind("<Button-1>")

    def cancel(self):
        self.downloadLabel.destroy()
        self.cancelButton.destroy()
        self.send["state"] = NORMAL
        self.sending = 0
        self.send_chat("cancel", 0)

    def permission(self):
        self.download = 1
        self.send_chat("let", 0)

    def update_pro(self):
        with open("txt\change.txt", "w") as doc:
            doc.write(str(self.PROTOCOL))

    def music(self):

        window = Toplevel(root)
        window.title("Select the Sound")
        window.geometry("270x100+480+100")

        first = Button(window, text = 1, height = 5, width = 5)
        first.pack(side = LEFT)
        first.bind("<Button-1>", lambda event: self.play_sound("music/1.mp3"))

        second = Button(window, text = 2, height = 5, width = 5)
        second.pack(side = LEFT)
        second.bind("<Button-1>", lambda event: self.play_sound("music/2.mp3"))

        third = Button(window, text = 3, height = 5, width = 5)
        third.pack(side = LEFT)
        third.bind("<Button-1>", lambda event: self.play_sound("music/3.mp3"))

        fourth = Button(window, text = 4, height = 5, width = 5)
        fourth.pack(side = LEFT)
        fourth.bind("<Button-1>", lambda event: self.play_sound("music/4.mp3"))

        fifth = Button(window, text = 5, height = 5, width = 5)
        fifth.pack(side = LEFT)
        fifth.bind("<Button-1>", lambda event: self.play_sound("music/5.mp3"))

        sixth = Button(window, text = 6, height = 5, width = 5)
        sixth.pack(side = LEFT)
        sixth.bind("<Button-1>", lambda event: self.play_sound("music/6.mp3"))

    def play_sound(self, url):

        if self.second != 0:
            self.txt["state"] = NORMAL
            self.txt.insert("end", f"You can only play 1 song in 10 secs. {self.second} remaining\n\n")
            self.txt.yview(END)
            self.txt["state"] = DISABLED

        else:
            self.second = 10

            name = url.split("/")[1].split(".")[0]
            self.txt["state"] = NORMAL
            self.txt.insert("end", f"Sound {name} is played\n\n")
            self.txt.yview(END)
            self.txt["state"] = DISABLED

            self.music_thread(url)

            self.secondThread = threading.Thread(target = self.sound_time)
            self.secondThread.start()
            self.send_chat(url, 0)

    def music_thread(self, url):
        music_thread = threading.Thread(target = self.play, args = (url,))
        music_thread.start()

    def play(self, url):
        playsound.playsound(url)
        self.played += 1

    def sound_time(self):

        for sec in range(10):
            self.second -= 1
            time.sleep(1)

    def security_thread(self):
        thread = threading.Thread(target = self.secure)
        thread.start()

    def secure(self):
        url = "https://www.virustotal.com/vtapi/v2/file/scan"
        params = {"apikey": "7cb94fde8920fc0ebefb227be5fbb39db59bfd3e3d30217f7a7f2dbd6f001555"}
        files = {"file": (f"{self.file.name}", open(self.file.name, "rb"))}
        response = requests.post(url, files = files, params = params)
        resp = response.json()["response_code"]
        self.security = "Secure" if resp == 1 else "Might not be secure"

        text = f"Document: {self.file_name}, {5 * ' '} Security: {self.security.capitalize()}"
        self.downloadLabel["text"] = text

        text = f"changed_security: {self.security}"
        self.socket.send(text.encode("utf-8"))

if __name__ == '__main__':
    root = Tk()
    app = GUI(root)
    root.title("Chat App")
    root.geometry("600x300+250+50")
    root.mainloop()