from tkinter import *
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import ctypes
from PIL import Image
import random
import zipfile 

# Set Application User Model ID for Windows (to fix icon/taskbar grouping)
myappid = 'mycompany.myproduct.subproduct.version'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

win = Tk()

global is_on 
global valBtnToggle
global current_folder_path
global target_size_tab
global main_size
global sticker_size
global emoji_size

is_on = False
valBtnToggle = 3 # 2 for Sticker mode (2-digit name), 3 for Emoji mode (3-digit name)
current_folder_path = None

# Target sizes for LINE Creators Market
target_size_tab = (96, 74)
main_size = (240, 240)
sticker_size = (370, 320)
emoji_size = (180, 180)

def toggle_button():
    global is_on 
    global valBtnToggle
    global current_folder_path
    
    is_on = not is_on 
    
    folder_selected = current_folder_path is not None

    if is_on:
        # Sticker Mode
        btnToggle.config(text=f"Sticker Mode (xx.png | {sticker_size[0]}x{sticker_size[1]}px)") 
        valBtnToggle = 2
        
        if folder_selected:
            btnMainImage.config(state=NORMAL, bg="#00CC99", fg="white")
    else:
        # Emoji Mode
        btnToggle.config(text=f"Emoji Mode (xxx.png | {emoji_size[0]}x{emoji_size[1]}px)") 
        valBtnToggle = 3
        
        # Main Image is usually not required for Emojis
        btnMainImage.config(state=DISABLED, bg="#00CC99", fg="white")

def fileOpen():
    global current_folder_path
    global is_on
    
    selected_dir = filedialog.askdirectory()
    
    if selected_dir:
        current_folder_path = selected_dir
        
        # Enable buttons after folder selection
        btnBulkProcess.config(state=NORMAL, bg="#FF4500", fg="white") 
        btnTabImage.config(state=NORMAL, bg="#00CC99", fg="white")
        btnZipArchive.config(state=NORMAL, bg="#3399FF", fg="white") 
        
        # Check if Main Image button should be enabled based on mode
        if is_on:
             btnMainImage.config(state=NORMAL, bg="#00CC99", fg="white")
        else:
             btnMainImage.config(state=DISABLED, bg="#00CC99", fg="white")
        
        current_dir_var.set(selected_dir)
        
        list_files(selected_dir)
        
    return current_folder_path

def process_bulk_resize_and_rename():
    global current_folder_path
    global valBtnToggle
    global sticker_size
    global emoji_size
    
    if not current_folder_path or not os.path.isdir(current_folder_path):
        messagebox.showerror("Error", "Please select a source folder first")
        return

    # Filter and sort all PNG files
    all_png_files = sorted([
        f for f in os.listdir(current_folder_path) 
        if f.lower().endswith(".png") and os.path.isfile(os.path.join(current_folder_path, f))
    ])
    
    if not all_png_files:
        messagebox.showerror("Error", "No .png files found in the selected folder")
        return

    mode = "Emoji" if valBtnToggle == 3 else "Sticker"
    current_target_size = emoji_size if valBtnToggle == 3 else sticker_size
    
    warning_message = (
        f"*** WARNING: SOURCE FILES WILL BE OVERWRITTEN ***\n\n"
        f"Current Mode: {mode}\n"
        f"File Count: {len(all_png_files)}\n"
        f"Target Size: {current_target_size[0]}x{current_target_size[1]}px\n\n"
        f"All PNG files in this folder will be resized and renamed sequentially, "
        f"and will be saved over the original files! (with compression)\n"
        f"Have you backed up your source files?"
    )
    if messagebox.askyesno("CONFIRM: IN-PLACE OVERWRITE", warning_message, icon='warning') == False:
        return
        
    i = 1 
    processed_count = 0
    processed_images = [] 

    try:
        # 1. Process images (Resize and queue for saving)
        for file_name in all_png_files:
            source_path = os.path.join(current_folder_path, file_name)
            
            with Image.open(source_path) as img:
                resized_img = img.resize(current_target_size, Image.Resampling.LANCZOS)
                
                # Determine new file name (01.png or 001.png)
                new_file_name = str(i).zfill(valBtnToggle) + ".png"
                
                processed_images.append((resized_img, new_file_name))
                
                i += 1
                processed_count += 1
        
        # 2. Delete existing files (excluding reserved names)
        deleted_count = 0
        failed_deletes = []
        # Reserved files are often tab.png, main.png, main@2x.png (we only care about main and tab here)
        reserved_names = ('tab.png', 'main.png', 'main@2x.png') 
        files_to_delete = [f for f in all_png_files if not f.lower() in reserved_names]
        
        for file_name in files_to_delete:
             full_path = os.path.join(current_folder_path, file_name)
             if os.path.exists(full_path):
                 try:
                     os.remove(full_path)
                     deleted_count += 1
                 except Exception as del_e:
                     failed_deletes.append(file_name)


        # 3. Save the processed and renamed images
        for img, new_file_name in processed_images:
            output_path = os.path.join(current_folder_path, new_file_name) 
            # Save with optimization and high compression
            img.save(output_path, 'PNG', optimize=True, compress_level=9)
            
        if failed_deletes:
             messagebox.showwarning("Deletion Warning", 
                                    f"Could not delete some source files ({len(failed_deletes)} files):\n"
                                    f"{', '.join(failed_deletes)}\n\n"
                                    f"Please check that these files are not open or locked by another program.")
        
        list_files(current_folder_path)
        messagebox.showinfo("Success", 
                            f"Success! Processed and renamed {processed_count} files (IN-PLACE)\n"
                            f"Mode: {mode} ({current_target_size[0]}x{current_target_size[1]}px)\n"
                            f"Source files have been overwritten and reordered.")
             
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during processing: {e}")

def _create_single_image(target_size, new_file_name, dialog_title):
    global current_folder_path
    
    # Ask user where to save the single output file
    output_dir = filedialog.askdirectory(title=dialog_title)
    if not output_dir:
        return

    # Find all PNG files in the source folder
    all_png_files = [
        f for f in os.listdir(current_folder_path) 
        if f.lower().endswith(".png") and os.path.isfile(os.path.join(current_folder_path, f))
    ]
    
    if not all_png_files:
        messagebox.showerror("Error", "No .png files found in the selected folder")
        return

    # Pick one file randomly for the Tab/Main image
    selected_file_name = random.choice(all_png_files)
    
    if messagebox.askyesno("Confirm Process", 
                           f"The randomly selected file is:\n{selected_file_name}\n\n"
                           f"Do you want to proceed with resizing to {target_size[0]}x{target_size[1]}px "
                           f"and saving as {new_file_name}?") == False:
        return
        
    try:
        source_path = os.path.join(current_folder_path, selected_file_name)
        output_path = os.path.join(output_dir, new_file_name)
        
        with Image.open(source_path) as img:
            resized_img = img.resize(target_size, Image.Resampling.LANCZOS)
            
            # Save with optimization and high compression
            resized_img.save(output_path, 'PNG', optimize=True, compress_level=9)
        
        messagebox.showinfo("Success", 
                            f"Success! Processed and copied random file:\n{selected_file_name}\n"
                            f"to\n{new_file_name}\nin:\n{output_dir}")
             
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during processing: {e}")

def create_tab_image():
    global target_size_tab
    _create_single_image(target_size_tab, "tab.png", "Select folder to save Tab Image (tab.png)")

def create_main_image():
    global main_size
    _create_single_image(main_size, "main.png", "Select folder to save Main Image (main.png)")


def create_zip_archive():
    global current_folder_path
    
    if not current_folder_path or not os.path.isdir(current_folder_path):
        messagebox.showerror("Error", "Please select a folder containing processed files first")
        return

    # Get all PNG files for zipping
    all_png_files = sorted([
        f for f in os.listdir(current_folder_path) 
        if f.lower().endswith(".png") and os.path.isfile(os.path.join(current_folder_path, f))
    ])
    
    if not all_png_files:
        messagebox.showerror("Error", "No .png files found in the selected folder to create ZIP")
        return

    zip_path = filedialog.asksaveasfilename(
        initialdir=current_folder_path,
        defaultextension=".zip",
        filetypes=[("Zip files", "*.zip")],
        title="Save ZIP file for LINE Creators Market submission"
    )

    if not zip_path:
        return

    try:
        # Create ZIP file containing all relevant PNGs in the folder
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_name in all_png_files:
                full_path = os.path.join(current_folder_path, file_name)
                # Write file into the zip archive using only the filename as arcname
                zf.write(full_path, arcname=file_name)
        
        messagebox.showinfo("Success", 
                            f"Success! Created ZIP file at:\n{zip_path}\n"
                            f"Total {len(all_png_files)} files, ready for LINE Creators Market submission")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while creating ZIP file: {e}")


def list_files(folder_path):
    # Clear existing list
    for item in tree_view.get_children():
        tree_view.delete(item)
    
    try:
        # Populate list with files from the folder
        for filename in os.listdir(folder_path):
            if os.path.isfile(os.path.join(folder_path, filename)):
                tree_view.insert("", "end", values=(filename,))
    except Exception:
        pass


# --- UI Setup ---

# Calculate window position to center it
width = 700
height = 710 
x = (win.winfo_screenwidth() // 2) - (width // 2)
y = (win.winfo_screenheight() // 2) - (height // 2)
win.geometry('{}x{}+{}+{}' .format(width,height,x,y))
win.title("LINE Creators Market Preparation Tool")
current_dir_var = StringVar()


# Mode Toggle Button (initial state set at the end)
btnToggle = tk.Button(win, text="Mode Toggle", command=toggle_button) 
btnToggle.pack(pady=10)


btnOpenFile = Button(win, text="1. Select Source Folder", width=30, pady=5, command=fileOpen)
btnOpenFile.pack(pady=5)

btnBulkProcess = tk.Button(win, text=f"2. Resize and Rename All Files IN-PLACE", 
                         width=55, pady=5, command=process_bulk_resize_and_rename, 
                         state=DISABLED, bg="#FF4500", fg="white")
btnBulkProcess.pack(pady=5)

btnTabImage = tk.Button(win, text=f"3. Pick 1 Random File & Create Tab Image (tab.png | {target_size_tab[0]}x{target_size_tab[1]}px)", 
                         width=55, pady=5, command=create_tab_image, 
                         state=DISABLED, bg="#00CC99", fg="white")
btnTabImage.pack(pady=5)

btnMainImage = tk.Button(win, text=f"4. Pick 1 Random File & Create Main Image (main.png | {main_size[0]}x{main_size[1]}px)",
                         width=55, pady=5, command=create_main_image, 
                         state=DISABLED, bg="#00CC99", fg="white")
btnMainImage.pack(pady=5)

btnZipArchive = tk.Button(win, text="5. Create ZIP Archive from All PNG Files in Folder",
                         width=55, pady=5, command=create_zip_archive, 
                         state=DISABLED, bg="#3399FF", fg="white")
btnZipArchive.pack(pady=5)


folder_label = tk.Label(win, textvariable=current_dir_var, fg="#0077b6")
folder_label.pack(pady=5)

# File List Treeview
frame_file_list = Frame(win)
frame_file_list.pack(padx=20, pady=10, fill="both", expand=True)

tree_view = ttk.Treeview(frame_file_list, columns=("Files",), show="headings", selectmode="browse")
tree_view.heading("Files", text="Files in Current Folder")
tree_view.column("Files", width=300, anchor="w")
tree_view.grid(row=0, column=0, sticky='nsew')

vsb = ttk.Scrollbar(frame_file_list, orient="vertical", command=tree_view.yview)
vsb.grid(row=0, column=1, sticky='ns')
tree_view.configure(yscrollcommand=vsb.set)

frame_file_list.grid_columnconfigure(0, weight=1)
frame_file_list.grid_rowconfigure(0, weight=1)

# Initialize the toggle button state and text
toggle_button()

win.mainloop()
