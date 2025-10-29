from tkinter import *
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import ctypes
from PIL import Image
import random
import zipfile 

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
valBtnToggle = 3
current_folder_path = None

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
        btnToggle.config(text=f"Sticker Mode (xx.png | {sticker_size[0]}x{sticker_size[1]}px)") 
        valBtnToggle = 2
        
        if folder_selected:
            btnMainImage.config(state=NORMAL, bg="#00CC99", fg="white")
    else:
        btnToggle.config(text=f"Emoji Mode (xxx.png | {emoji_size[0]}x{emoji_size[1]}px)") 
        valBtnToggle = 3
        
        btnMainImage.config(state=DISABLED, bg="#00CC99", fg="white")

def fileOpen():
    global current_folder_path
    global is_on
    
    selected_dir = filedialog.askdirectory()
    
    if selected_dir:
        current_folder_path = selected_dir
        
        btnBulkProcess.config(state=NORMAL, bg="#FF4500", fg="white") 
        btnTabImage.config(state=NORMAL, bg="#00CC99", fg="white")
        btnZipArchive.config(state=NORMAL, bg="#3399FF", fg="white") 
        
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
        messagebox.showerror("Error", "โปรดเลือกโฟลเดอร์ต้นทางก่อน")
        return

    all_png_files = sorted([
        f for f in os.listdir(current_folder_path) 
        if f.lower().endswith(".png") and os.path.isfile(os.path.join(current_folder_path, f))
    ])
    
    if not all_png_files:
        messagebox.showerror("Error", "ไม่พบไฟล์ .png ในโฟลเดอร์ที่เลือก")
        return

    mode = "Emoji" if valBtnToggle == 3 else "Sticker"
    current_target_size = emoji_size if valBtnToggle == 3 else sticker_size
    
    warning_message = (
        f"*** คำเตือน: ไฟล์ต้นฉบับจะถูกเขียนทับ ***\n\n"
        f"โหมดปัจจุบัน: {mode}\n"
        f"จำนวนไฟล์: {len(all_png_files)}\n"
        f"ขนาดเป้าหมาย: {current_target_size[0]}x{current_target_size[1]}px\n\n"
        f"ไฟล์ PNG ทั้งหมดในโฟลเดอร์นี้จะถูกลดขนาดและเปลี่ยนชื่อตามลำดับ "
        f"และจะบันทึกทับไฟล์เดิมทันที! (พร้อมบีบอัดไฟล์)\n"
        f"คุณได้สำรองไฟล์ต้นฉบับไว้แล้วใช่หรือไม่?"
    )
    if messagebox.askyesno("CONFIRM: IN-PLACE OVERWRITE", warning_message, icon='warning') == False:
        return
        
    i = 1 
    processed_count = 0
    processed_images = [] 

    try:
        for file_name in all_png_files:
            source_path = os.path.join(current_folder_path, file_name)
            
            with Image.open(source_path) as img:
                resized_img = img.resize(current_target_size, Image.Resampling.LANCZOS)
                
                new_file_name = str(i).zfill(valBtnToggle) + ".png"
                
                processed_images.append((resized_img, new_file_name))
                
                i += 1
                processed_count += 1
        
        deleted_count = 0
        failed_deletes = []
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


        for img, new_file_name in processed_images:
            output_path = os.path.join(current_folder_path, new_file_name) 
            img.save(output_path, 'PNG', optimize=True, compress_level=9)
            
        if failed_deletes:
             messagebox.showwarning("Deletion Warning", 
                                    f"ไม่สามารถลบไฟล์ต้นฉบับบางไฟล์ได้ ({len(failed_deletes)} ไฟล์):\n"
                                    f"{', '.join(failed_deletes)}\n\n"
                                    f"โปรดตรวจสอบว่าไฟล์เหล่านี้ไม่ได้ถูกเปิดหรือถูกล็อกโดยโปรแกรมอื่น.")
        
        list_files(current_folder_path)
        messagebox.showinfo("Success", f"สำเร็จ! ประมวลผลและตั้งชื่อ {processed_count} ไฟล์ (IN-PLACE)\nโหมด: {mode} ({current_target_size[0]}x{current_target_size[1]}px)\nไฟล์ต้นฉบับถูกเขียนทับและเรียงลำดับใหม่แล้ว")
            
    except Exception as e:
        messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการประมวลผล: {e}")

def _create_single_image(target_size, new_file_name, dialog_title):
    global current_folder_path
    
    output_dir = filedialog.askdirectory(title=dialog_title)
    if not output_dir:
        return

    all_png_files = [
        f for f in os.listdir(current_folder_path) 
        if f.lower().endswith(".png") and os.path.isfile(os.path.join(current_folder_path, f))
    ]
    
    if not all_png_files:
        messagebox.showerror("Error", "ไม่พบไฟล์ .png ในโฟลเดอร์ที่เลือก")
        return

    selected_file_name = random.choice(all_png_files)
    
    if messagebox.askyesno("Confirm Process", 
                          f"ไฟล์ที่ถูกสุ่มเลือกคือ:\n{selected_file_name}\n\nต้องการดำเนินการลดขนาดเป็น {target_size[0]}x{target_size[1]}px และบันทึกเป็น {new_file_name} หรือไม่?") == False:
        return
        
    try:
        source_path = os.path.join(current_folder_path, selected_file_name)
        output_path = os.path.join(output_dir, new_file_name)
        
        with Image.open(source_path) as img:
            resized_img = img.resize(target_size, Image.Resampling.LANCZOS)
            
            resized_img.save(output_path, 'PNG', optimize=True, compress_level=9)
        
        messagebox.showinfo("Success", f"สำเร็จ! ประมวลผลและคัดลอกไฟล์สุ่ม:\n{selected_file_name}\nเป็น\n{new_file_name}\nไปยัง:\n{output_dir}")
            
    except Exception as e:
        messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการประมวลผล: {e}")

def create_tab_image():
    global target_size_tab
    _create_single_image(target_size_tab, "tab.png", "เลือกโฟลเดอร์สำหรับบันทึกภาพ Tab Image (tab.png)")

def create_main_image():
    global main_size
    _create_single_image(main_size, "main.png", "เลือกโฟลเดอร์สำหรับบันทึกภาพ Main Image (main.png)")


def create_zip_archive():
    global current_folder_path
    
    if not current_folder_path or not os.path.isdir(current_folder_path):
        messagebox.showerror("Error", "โปรดเลือกโฟลเดอร์ที่มีไฟล์ที่ประมวลผลแล้วก่อน")
        return

    all_png_files = sorted([
        f for f in os.listdir(current_folder_path) 
        if f.lower().endswith(".png") and os.path.isfile(os.path.join(current_folder_path, f))
    ])
    
    if not all_png_files:
        messagebox.showerror("Error", "ไม่พบไฟล์ .png ในโฟลเดอร์ที่เลือกเพื่อสร้าง ZIP")
        return

    zip_path = filedialog.asksaveasfilename(
        initialdir=current_folder_path,
        defaultextension=".zip",
        filetypes=[("Zip files", "*.zip")],
        title="บันทึกไฟล์ ZIP สำหรับส่ง LINE Creators Market"
    )

    if not zip_path:
        return

    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_name in all_png_files:
                full_path = os.path.join(current_folder_path, file_name)
                zf.write(full_path, arcname=file_name)
        
        messagebox.showinfo("Success", f"สำเร็จ! สร้างไฟล์ ZIP ที่:\n{zip_path}\nมีทั้งหมด {len(all_png_files)} ไฟล์ พร้อมส่ง LINE Creators Market")

    except Exception as e:
        messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการสร้างไฟล์ ZIP: {e}")


def list_files(folder_path):
    for item in tree_view.get_children():
        tree_view.delete(item)
    
    try:
        for filename in os.listdir(folder_path):
            if os.path.isfile(os.path.join(folder_path, filename)):
                tree_view.insert("", "end", values=(filename,))
    except Exception:
        pass


width = 700
height = 710 
x = (win.winfo_screenwidth() // 2) - (width // 2)
y = (win.winfo_screenheight() // 2) - (height // 2)
win.geometry('{}x{}+{}+{}' .format(width,height,x,y))
win.title("LINE Creators Market Preparation Tool")
current_dir_var = StringVar()


btnToggle = tk.Button(win, text="Mode Toggle", command=toggle_button) 
btnToggle.pack(pady=10)


btnOpenFile = Button(win, text="1. เลือกโฟลเดอร์ต้นทาง", width=30, pady=5, command=fileOpen)
btnOpenFile.pack(pady=5)

btnBulkProcess = tk.Button(win, text=f"2. ลดขนาดและเปลี่ยนชื่อไฟล์ทั้งหมด IN-PLACE", 
                       width=55, pady=5, command=process_bulk_resize_and_rename, state=DISABLED, bg="#FF4500", fg="white")
btnBulkProcess.pack(pady=5)

btnTabImage = tk.Button(win, text=f"3. สุ่ม 1 ไฟล์ & สร้าง Tab Image (tab.png | {target_size_tab[0]}x{target_size_tab[1]}px)", 
                       width=55, pady=5, command=create_tab_image, state=DISABLED, bg="#00CC99", fg="white")
btnTabImage.pack(pady=5)

btnMainImage = tk.Button(win, text=f"4. สุ่ม 1 ไฟล์ & สร้าง Main Image (main.png | {main_size[0]}x{main_size[1]}px)",
                         width=55, pady=5, command=create_main_image, state=DISABLED, bg="#00CC99", fg="white")
btnMainImage.pack(pady=5)

btnZipArchive = tk.Button(win, text="5. สร้างไฟล์ Zip จากไฟล์ PNG ทั้งหมดในโฟลเดอร์",
                         width=55, pady=5, command=create_zip_archive, state=DISABLED, bg="#3399FF", fg="white")
btnZipArchive.pack(pady=5)


folder_label = tk.Label(win, textvariable=current_dir_var, fg="#0077b6")
folder_label.pack(pady=5)

frame_file_list = Frame(win)
frame_file_list.pack(padx=20, pady=10, fill="both", expand=True)

tree_view = ttk.Treeview(frame_file_list, columns=("Files",), show="headings", selectmode="browse")
tree_view.heading("Files", text="ไฟล์ในโฟลเดอร์ปัจจุบัน")
tree_view.column("Files", width=300, anchor="w")
tree_view.grid(row=0, column=0, sticky='nsew')

vsb = ttk.Scrollbar(frame_file_list, orient="vertical", command=tree_view.yview)
vsb.grid(row=0, column=1, sticky='ns')
tree_view.configure(yscrollcommand=vsb.set)

frame_file_list.grid_columnconfigure(0, weight=1)
frame_file_list.grid_rowconfigure(0, weight=1)

toggle_button()

win.mainloop()
