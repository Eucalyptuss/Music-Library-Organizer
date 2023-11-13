import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import pygame
from PIL import Image, ImageTk

pygame.mixer.init()

def parse_filename(filename):
    parts = filename.split('-', 1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip('.mp3').strip()
    else:
        return 'Unknown', filename

def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(reverse=reverse)

    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))

class MusicLibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Library Organizer")
        self.music_list = []
        self.duplicates = []
        self.original_file_list = []
        self.setup_ui()
        self.current_folder = ''

    def setup_ui(self):

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=3)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(3, weight=1)
        self.root.rowconfigure(4, weight=1)
        self.root.rowconfigure(5, weight=1)

        self.directory_frame = tk.Frame(self.root)
        self.directory_frame.grid(row=0, column=0, sticky="ew")

        self.folder_button = tk.Button(self.directory_frame, text="Select Folder", command=self.select_folder)
        self.folder_button.pack(side=tk.TOP, fill=tk.X)

        self.refresh_button = tk.Button(self.directory_frame, text="Refresh", command=self.refresh_list)
        self.refresh_button.pack(side=tk.TOP, fill=tk.X)

        label_music_list = tk.Label(self.root, text="Music List", bg="black", fg="white", anchor="center")
        label_music_list.grid(row=1, column=0, sticky="ew")

        self.music_table = ttk.Treeview(self.root, columns=('Folder', 'Title', 'Artist'), show='headings')
        self.music_table.heading('Folder', text='Folder',
                                 command=lambda: treeview_sort_column(self.music_table, 'Folder', False))
        self.music_table.heading('Title', text='Title',
                                 command=lambda: treeview_sort_column(self.music_table, 'Title', False))
        self.music_table.heading('Artist', text='Artist',
                                 command=lambda: treeview_sort_column(self.music_table, 'Artist', False))
        self.music_table.grid(row=2, column=0, sticky="nsew")
        self.music_table.bind("<Double-1>", self.play_selected_music)

        label_duplicate_tracks = tk.Label(self.root, text="Duplicate Tracks", bg="black", fg="white", anchor="center")
        label_duplicate_tracks.grid(row=3, column=0, sticky="ew")

        self.duplicate_table = ttk.Treeview(self.root, columns=('Folder', 'Title', 'Artist'), show='headings')
        self.duplicate_table.heading('Folder', text='Folder',
                                     command=lambda: treeview_sort_column(self.duplicate_table, 'Folder', False))
        self.duplicate_table.heading('Title', text='Title',
                                     command=lambda: treeview_sort_column(self.duplicate_table, 'Title', False))
        self.duplicate_table.heading('Artist', text='Artist',
                                     command=lambda: treeview_sort_column(self.duplicate_table, 'Artist', False))
        self.duplicate_table.grid(row=4, column=0, sticky="nsew")
        self.duplicate_table.bind("<Double-1>", self.play_selected_music)

        label_search_results = tk.Label(self.root, text="Search Results", bg="black", fg="white", anchor="center")
        label_search_results.grid(row=1, column=1, columnspan=2, sticky="ew")

        self.search_frame = tk.Frame(self.root)
        self.search_frame.grid(row=0, column=1, columnspan=2, sticky="ew")

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.search_entry.bind("<Return>", self.search_music)

        self.search_button = tk.Button(self.search_frame, text="Search", command=self.search_music)
        self.search_button.pack(side=tk.LEFT)

        self.search_results_table = ttk.Treeview(self.root, columns=('Folder', 'Title', 'Artist'), show='headings')
        self.search_results_table.heading('Folder', text='Folder',
                                          command=lambda: treeview_sort_column(self.search_results_table, 'Folder',
                                                                               False))
        self.search_results_table.heading('Title', text='Title',
                                          command=lambda: treeview_sort_column(self.search_results_table, 'Title',
                                                                               False))
        self.search_results_table.heading('Artist', text='Artist',
                                          command=lambda: treeview_sort_column(self.search_results_table, 'Artist',
                                                                               False))
        self.search_results_table.grid(row=2, column=1, rowspan=1, columnspan=2, sticky="nsew")
        self.search_results_table.bind("<Double-1>", self.play_selected_music)

        label_play_title = tk.Label(self.root, text="Play", bg="black", fg="white", anchor="center")
        label_play_title.grid(row=3, column=1, sticky="ew")

        self.play_frame = tk.Frame(self.root)
        self.play_frame.grid(row=4, column=1, rowspan=3, columnspan=2, sticky="nsew")

        self.button_frame = tk.Frame(self.play_frame)
        self.button_frame.pack(anchor='center')

        button_size = (100, 100)
        self.play_image = Image.open("./images/play.png")
        self.play_image = self.play_image.resize(button_size, Image.LANCZOS)
        self.play_image = ImageTk.PhotoImage(self.play_image)

        self.stop_image = Image.open("./images/stop.png")
        self.stop_image = self.stop_image.resize(button_size, Image.LANCZOS)
        self.stop_image = ImageTk.PhotoImage(self.stop_image)

        self.forward_image = Image.open("./images/forward.png")
        self.forward_image = self.forward_image.resize(button_size, Image.LANCZOS)
        self.forward_image = ImageTk.PhotoImage(self.forward_image)

        self.backward_image = Image.open("./images/backward.png")
        self.backward_image = self.backward_image.resize(button_size, Image.LANCZOS)
        self.backward_image = ImageTk.PhotoImage(self.backward_image)

        self.backward_button = tk.Button(self.button_frame, image=self.backward_image, command=lambda: self.skip_music(-10))
        self.backward_button.pack(side=tk.LEFT)

        self.play_button = tk.Button(self.button_frame, image=self.play_image, command=self.toggle_play_pause)
        self.play_button.pack(side=tk.LEFT)

        self.stop_button = tk.Button(self.button_frame, image=self.stop_image, command=self.stop_music)
        self.stop_button.pack(side=tk.LEFT)

        self.forward_button = tk.Button(self.button_frame, image=self.forward_image, command=lambda: self.skip_music(10))
        self.forward_button.pack(side=tk.LEFT)

        self.player_frame = tk.Frame(self.root)
        self.player_frame.grid(row=4, column=1, columnspan=2, sticky="ew")

        self.volume_slider = tk.Scale(self.play_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=self.adjust_volume)
        self.volume_slider.set(30)  # 초기 음량 값 설정
        self.volume_slider.pack(side=tk.BOTTOM, fill=tk.X, expand=True)

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.current_folder = folder_path
            self.refresh_list()

    def refresh_list(self):
        if not self.current_folder:
            messagebox.showerror("Error", "Please select a folder first.")
            return

        self.music_list.clear()
        self.duplicates.clear()
        self.original_file_list.clear()
        for root, dirs, files in os.walk(self.current_folder):
            for file in files:
                if file.endswith('.mp3'):
                    artist, title = parse_filename(file)
                    full_path = os.path.join(root, file)
                    self.original_file_list.append((full_path, title, artist))
                    self.music_list.append((root, title, artist))

        self.update_music_table()
        self.find_duplicates()

    def update_music_table(self):
        for i in self.music_table.get_children():
            self.music_table.delete(i)
        for folder, title, artist in self.music_list:
            self.music_table.insert('', 'end', values=(folder, title, artist))

    def find_duplicates(self):
        seen = {}
        for folder, title, artist in self.music_list:
            key = (title, artist)
            if key in seen:
                self.duplicates.append((folder, title, artist))
                self.duplicates.append(seen[key])
            else:
                seen[key] = (folder, title, artist)

        self.duplicates = list(dict.fromkeys(self.duplicates))
        for i in self.duplicate_table.get_children():
            self.duplicate_table.delete(i)
        for folder, title, artist in self.duplicates:
            self.duplicate_table.insert('', 'end', values=(folder, title, artist))

    def search_music(self, event=None):
        search_term = self.search_var.get().lower()
        if not search_term:
            messagebox.showerror("Error", "Please enter a search term.")
            return

        results = [(folder, title, artist) for folder, title, artist in self.music_list if
                   search_term in title.lower() or search_term in artist.lower()]

        for i in self.search_results_table.get_children():
            self.search_results_table.delete(i)
        for folder, title, artist in results:
            self.search_results_table.insert('', 'end', values=(folder, title, artist))

    def toggle_play_pause(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()

    def stop_music(self):
        pygame.mixer.music.stop()

    def skip_music(self, seconds):
        if pygame.mixer.music.get_busy():
            current_pos = pygame.mixer.music.get_pos() // 1000
            new_pos = max(0, current_pos + seconds)
            pygame.mixer.music.play(start=new_pos)

    def play_selected_music(self, event):
        selected_table = event.widget
        selected_item = selected_table.selection()

        if selected_item:
            item_data = selected_table.item(selected_item, 'values')
            file_path = None
            for path, title, artist in self.original_file_list:
                if title == item_data[1] and artist == item_data[2]:
                    file_path = path
                    break

            if file_path and os.path.isfile(file_path):
                try:
                    pygame.mixer.music.load(file_path)
                    pygame.mixer.music.play()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to play the file: {file_path}\n{e}")
            else:
                messagebox.showerror("Error", "File not found or invalid file path.")

    def adjust_volume(self, volume):
        pygame.mixer.music.set_volume(int(volume) / 100.0)

root = tk.Tk()
app = MusicLibraryApp(root)
root.mainloop()

