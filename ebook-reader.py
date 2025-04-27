import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from ebooklib import epub, ITEM_DOCUMENT
from bs4 import BeautifulSoup
import os
import shutil
import json

# Ensure lib and data folders exist
os.makedirs('lib', exist_ok=True)
progress_file = 'progress.json'
if not os.path.exists(progress_file):
    with open(progress_file, 'w') as f:
        json.dump({}, f)

class EPUBReader:
    def __init__(self, root):
        self.root = root
        self.root.title("EPUB Reader")
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 14))
        self.text_area.pack(fill=tk.BOTH, expand=True)

        top_frame = tk.Frame(root)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        self.add_btn = tk.Button(top_frame, text="+", command=self.add_book)
        self.add_btn.pack(side=tk.LEFT)

        self.book_select = tk.StringVar(root)
        self.book_menu = tk.OptionMenu(top_frame, self.book_select, "")
        self.book_menu.pack(side=tk.LEFT)

        self.open_btn = tk.Button(top_frame, text="Open", command=self.select_book)
        self.open_btn.pack(side=tk.LEFT)

        self.prev_btn = tk.Button(top_frame, text="<< Prev", command=self.prev_chapter)
        self.prev_btn.pack(side=tk.LEFT)

        self.next_btn = tk.Button(top_frame, text="Next >>", command=self.next_chapter)
        self.next_btn.pack(side=tk.LEFT)

        self.book = None
        self.chapters = []
        self.current_chapter = 0
        self.current_book_path = ""

        self.update_book_list()

    def add_book(self):
        file_path = filedialog.askopenfilename(filetypes=[("EPUB files", "*.epub")])
        if not file_path:
            return
        
        filename = os.path.basename(file_path)
        lib_path = os.path.join('lib', filename)
        try:
            shutil.copy(file_path, lib_path)
            messagebox.showinfo("Success", f"Book '{filename}' added to library.")
            self.update_book_list()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add book: {e}")

    def update_book_list(self):
        files = [f for f in os.listdir('lib') if f.endswith('.epub')]
        menu = self.book_menu["menu"]
        menu.delete(0, "end")
        for file in files:
            menu.add_command(label=file, command=lambda value=file: self.book_select.set(value))
        if files:
            self.book_select.set(files[0])

    def select_book(self):
        book_name = self.book_select.get()
        if not book_name:
            messagebox.showwarning("No selection", "Please select a book to open.")
            return
        lib_path = os.path.join('lib', book_name)
        self.open_book(lib_path)

    def open_book(self, path):
        try:
            self.book = epub.read_epub(path)
            self.chapters = []
            self.current_book_path = path

            for item in self.book.get_items():
                if item.get_type() == ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    text = soup.get_text()
                    self.chapters.append(text)

            if not self.chapters:
                messagebox.showerror("Error", "No readable chapters found in this EPUB.")
                return

            self.load_progress()
            self.show_chapter()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open EPUB: {e}")

    def show_chapter(self):
        if not self.chapters:
            return
        self.text_area.delete('1.0', tk.END)
        self.text_area.insert(tk.END, self.chapters[self.current_chapter])
        self.save_progress()

    def next_chapter(self):
        if self.current_chapter < len(self.chapters) - 1:
            self.current_chapter += 1
            self.show_chapter()
        else:
            messagebox.showinfo("End", "You are at the last chapter.")

    def prev_chapter(self):
        if self.current_chapter > 0:
            self.current_chapter -= 1
            self.show_chapter()
        else:
            messagebox.showinfo("Start", "You are at the first chapter.")

    def save_progress(self):
        try:
            with open(progress_file, 'r') as f:
                data = json.load(f)
        except:
            data = {}

        data[self.current_book_path] = self.current_chapter
        with open(progress_file, 'w') as f:
            json.dump(data, f)

    def load_progress(self):
        try:
            with open(progress_file, 'r') as f:
                data = json.load(f)
            self.current_chapter = data.get(self.current_book_path, 0)
        except:
            self.current_chapter = 0

if __name__ == "__main__":
    root = tk.Tk()
    reader = EPUBReader(root)
    root.mainloop()
