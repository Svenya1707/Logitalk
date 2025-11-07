import base64
import io
import threading
from socket import socket, AF_INET, SOCK_STREAM
from customtkinter import *
from tkinter import filedialog
from PIL import Image
import os 

class MainWindow(CTk):
    def __init__(self):
        super().__init__()
    
        set_appearance_mode("Dark")
        set_default_color_theme("blue")
        
        self.geometry("800x600")
        self.minsize(400, 300)
        self.title("Chat client")
        self.username = ""
        
        self.adaptive_ui_after_id = None

        self.menu_frame = CTkFrame(self, width=200, height=600, fg_color="#2b2b2b", corner_radius=0)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)
        
        self.is_show_menu = True
        self.speed_animate_menu = 20
        
        self.btn = CTkButton(self, text='✖', command=self.toggle_show_menu, width=30, height=30, 
                             fg_color="transparent", hover_color="#3E3E3E", text_color="#FFFFFF")
        self.btn.place(x=0, y=0)

        self.label = None
        self.entry_pack = None
        self.save_button = None
        self.setup_menu_content()


        self.chat_field = CTkScrollableFrame(self, fg_color="#1e1e1e", corner_radius=0)

        self.input_frame = CTkFrame(self, height=60, fg_color="#2b2b2b", corner_radius=0)
        
        self.message_entry = CTkEntry(self.input_frame, placeholder_text="Введіть повідомлення...", height=40, 
                                      border_width=0, corner_radius=10)
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)

        self.open_img_button = CTkButton(self.input_frame, text='🖼', width=50, height=40, command=self.open_image, 
                                         corner_radius=10, fg_color="#4a4a4a", hover_color="#5a5a5a")
        self.open_img_button.pack(side="left", padx=5, pady=10)

        self.send_button = CTkButton(self.input_frame, text='▶', width=50, height=40, command=self.send_message, 
                                     corner_radius=10, fg_color="#1fa53c", hover_color="#16517a")
        self.send_button.pack(side="left", padx=(0, 10), pady=10)

        self.adaptive_ui()
        self.bind('<Configure>', self._on_configure_safe) 

        img_demo = None
        try:
            img_demo = CTkImage(Image.open('images.png').resize((300, 300)), size=(300, 300))
        except FileNotFoundError:
             pass
             
        self.add_message("Демонстрація відображення зображення (моє повідомлення):", img=img_demo, author=self.username)
        self.add_message("Це повідомлення від іншого користувача:", author="ІншийКористувач")
        self.add_message(f"[SYSTEM] {self.username} приєднався (лась) до чату!", author="[SYSTEM]")

        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('127.0.0.1', 5000)) 
            hello = f"TXT@{self.username}@[SYSTEM] {self.username} приєднався (лась) до чату!\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except ConnectionRefusedError:
            self.add_message(f"Не вдалося підключитися: Сервер не запущений або порт 5000 не слухається.", author="[SYSTEM]")
        except Exception as e:
            self.add_message(f"Не вдалося підключитися до сервера: {type(e).__name__}: {e}", author="[SYSTEM]")

    def _on_configure_safe(self, event):
        if event.widget == self:
            if self.adaptive_ui_after_id:
                self.after_cancel(self.adaptive_ui_after_id)

            self.adaptive_ui_after_id = self.after(10, self.adaptive_ui)

    def setup_menu_content(self):
        self.remove_menu_content()
        
        CTkLabel(self.menu_frame, text="НАЛАШТУВАННЯ", font=("Arial", 16, "bold")).pack(pady=(40, 5))
        CTkLabel(self.menu_frame, text="Ім'я користувача", text_color="#AAAAAA").pack(pady=(5, 5))

        self.entry_pack = CTkEntry(self.menu_frame, placeholder_text="Ваше нове ім'я...", corner_radius=10)
        self.entry_pack.insert(0, self.username)
        self.entry_pack.pack(padx=20, fill="x")

        self.save_button = CTkButton(self.menu_frame, text="Зберегти Нік", command=self.save_name, 
                                     corner_radius=10, fg_color="#1fa54c", hover_color="#16517a")
        self.save_button.pack(pady=(10, 20), padx=20, fill="x")

    def remove_menu_content(self):
        for widget in self.menu_frame.winfo_children():
            widget.destroy()

    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.speed_animate_menu = -20
            self.btn.configure(text='⚙')
            self.show_menu()
        else:
            self.is_show_menu = True
            self.speed_animate_menu = 20
            self.btn.configure(text='✖')
            self.setup_menu_content()
            self.show_menu()

    def show_menu(self):
        current_width = self.menu_frame.winfo_width()
        
        if not self.is_show_menu and current_width > 30:
            new_width = max(30, current_width + self.speed_animate_menu)
            self.menu_frame.configure(width=new_width)
            self.adaptive_ui()
            self.after(10, self.show_menu)

        elif self.is_show_menu and current_width < 200:
            new_width = min(200, current_width + self.speed_animate_menu)
            self.menu_frame.configure(width=new_width)
            self.adaptive_ui()
            self.after(10, self.show_menu)

    def save_name(self):
        new_name = self.entry_pack.get().strip()
        if new_name and new_name != self.username:
            self.add_message(f"Нік змінено: {self.username} -> {new_name}", author="[SYSTEM]")
            self.username = new_name
            self.setup_menu_content()
        else:
            self.add_message("Ім'я не змінилося або поле порожнє.", author="[SYSTEM]")

    def adaptive_ui(self):
        
        if self.adaptive_ui_after_id:
            self.after_cancel(self.adaptive_ui_after_id)
            self.adaptive_ui_after_id = None
            
        menu_width = self.menu_frame.winfo_width()
        window_height = self.winfo_height()
        window_width = self.winfo_width()
        input_height = 60
        
        self.menu_frame.configure(height=window_height)

        self.input_frame.place(x=menu_width, y=window_height - input_height)
        self.input_frame.configure(width=window_width - menu_width)

        self.chat_field.place(x=menu_width, y=30)
        self.chat_field.configure(width=window_width - menu_width, height=window_height - input_height - 30)


    def add_message(self, message, img=None, author=None):
        
        is_mine = author == self.username
        is_system = author == "[SYSTEM]"
        
        if is_system:
            anchor_pos = 'center'
            bg_color = '#333333'
            text_color = '#AAAAAA'
        elif is_mine:
            anchor_pos = 'e'
            bg_color = '#1f6aa5'
            text_color = 'white'
        else:
            anchor_pos = 'w'
            bg_color = '#3E3E3E'
            text_color = 'white'

        message_frame = CTkFrame(self.chat_field, fg_color=bg_color, corner_radius=10)
        message_frame.pack(pady=5, padx=10, anchor=anchor_pos)
        
        
        menu_width = self.menu_frame.winfo_width()
        
        chat_field_width = self.winfo_width() - menu_width
        wrapleng_size = max(200, chat_field_width * 0.7)

        label_kwargs = {
            "text": message, 
            "wraplength": wrapleng_size, 
            "text_color": text_color, 
            "justify": 'left'
        }

        if img:
            label_kwargs['image'] = img
            label_kwargs['compound'] = 'top'
            
        CTkLabel(message_frame, **label_kwargs).pack(padx=10, pady=5)
        
        self.chat_field._parent_canvas.yview_moveto(1.0) 

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.add_message(f"[{self.username}]: {message}", author=self.username)
            data = f"TXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                pass
            self.message_entry.delete(0, END)

    def recv_message(self):
        buffer = ''
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk: break
                buffer += chunk.decode('utf-8', errors='ignore')
                while "\n" in buffer:
                    line, buffer = buffer.split('\n', 1)
                    self.handle_line(line.strip())
            except:
                break
        try:
            self.sock.close()
        except:
             pass

    def handle_line(self, line):
        if not line: return
        parts = line.split('@', 2)
        msg_type = parts[0]
        
        if msg_type == 'TXT':
            if len(parts) == 3:
                author = parts[1]
                message = parts[2]
                self.add_message(f"[{author}]: {message}", author=author)
                
        elif msg_type == 'IMGG':
            if len(parts) >= 4:
                author = parts[1]
                filename = parts[2]
                bed_data = parts[3]
                try:
                    img_data = base64.b64decode(bed_data.encode())
                    pil_img = Image.open(io.BytesIO(img_data))
                    ctk_img = CTkImage(pil_img.resize((300, 300)), size=(300, 300))
                    self.add_message(f"[{author}] надіслав зображення: {filename}", ctk_img, author=author)
                except Exception as e:
                    self.add_message(f"Помилка відображення зображення: {e}", author="[SYSTEM]")
        else:
            self.add_message(line, author="[SYSTEM]")

    def open_image(self):
        file_name = filedialog.askopenfilename(title="Виберіть зображення", 
                                               filetypes=(("Image files", "*.png;*.jpg;*.jpeg;*.gif"), ("all files", "*.*")))
        if not file_name:
            return
        
        try:
            with open(file_name, "rb") as f:
                raw = f.read()
            bed_data = base64.b64encode(raw).decode()
            short_name = os.path.basename(file_name)
            data = f"IMGG@{self.username}@{short_name}@{bed_data}\n"
            
            self.sock.sendall(data.encode())
            
            sent_img = CTkImage(Image.open(file_name).resize((300, 300)), size=(300, 300))
            self.add_message(f"[{self.username}] надіслав зображення: {short_name}", sent_img, author=self.username)
            
        except Exception as e:
            self.add_message(f"Не вдалося надіслати зображення: {e}", author="[SYSTEM]")

if __name__ == "__main__":
    win = MainWindow()
    win.mainloop()