import tkinter as tk
from tkinter import ttk, filedialog
import numpy as np
import os
import cv2
import matplotlib.pyplot as plt # type: ignore
from skimage.metrics import structural_similarity as ssim # type: ignore

class ModernSteganographyApp:
    def __init__(self):
        self.main = tk.Tk()
        self.main.title("Data Hiding Tool")
        self.main.geometry("1000x700")
        self.main.configure(bg="#f0f4f8")
        
        # Global variables
        self.filename1 = None
        self.filename2 = None
        
        self.setup_styles()
        self.create_widgets()
        
    def setup_styles(self):
        # Configure modern styles
        self.style = ttk.Style()
        self.style.configure(
            "Custom.TButton",
            padding=10,
            font=("Helvetica", 11, "bold"),
            background="#4a90e2",
            foreground="white",
            borderwidth=0,
            focusthickness=3,
            focuscolor='none',
            relief="flat",
            bordercolor="#4a90e2",
            anchor="center"
        )
        self.style.map(
            "Custom.TButton",
            background=[("active", "#357ABD")],
            foreground=[("active", "white")]
        )
        
        self.style.configure(
            "Status.TFrame",
            background="#ffffff",
            relief="flat",
            borderwidth=0
        )
        
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.main, bg="#2c3e50", height=100)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame,
            text="Data Hiding Tool",
            font=("Helvetica", 28, "bold"),
            fg="white",
            bg="#2c3e50"
        )
        title.pack(pady=30)
        
        # Main content area
        content_frame = tk.Frame(self.main, bg="#f0f4f8")
        content_frame.pack(fill="both", expand=True, padx=40)
        
        # Button container with modern grid layout
        btn_frame = tk.Frame(content_frame, bg="#f0f4f8")
        btn_frame.pack(fill="x", pady=20)
        
        # Create two rows of buttons with icons
        buttons = [
            ("📁 Upload Cover Image", self.upload_cover_image),
            ("📄 Upload Secret Image", self.upload_secret_image),
            ("🔒 Hide Secret Image", self.hide_image),
            ("🔓 Extract Secret Image", self.extract_image),
            ("📊 Calculate Metrics", self.calculate_metrics)
        ]
        
        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(
                btn_frame,
                text=text,
                command=command,
                style="Custom.TButton",
                width=25
            )
            row = i // 3
            col = i % 3
            btn.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Status area with modern styling
        status_frame = ttk.Frame(content_frame, style="Status.TFrame")
        status_frame.pack(fill="both", expand=True, pady=20)
        
        self.text_area = tk.Text(
            status_frame,
            height=15,
            width=70,
            font=("Helvetica", 11),
            bg="white",
            fg="#2c3e50",
            relief="flat",
            padx=10,
            pady=10,
            wrap=tk.WORD
        )
        self.text_area.pack(padx=20, pady=20, fill="both", expand=True)
        self.text_area.config(state=tk.DISABLED)
        
        # Add a subtle footer
        footer = tk.Label(
            self.main,
            text="Secure Data Hiding Tool",
            font=("Helvetica", 9),
            fg="#666666",
            bg="#f0f4f8"
        )
        footer.pack(pady=10)

    def upload_cover_image(self):
        self.filename1 = filedialog.askopenfilename(
            initialdir="SampleImages",
            title="Select Cover Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg")]
        )
        self.update_status(f"✅ Cover Image: {os.path.basename(self.filename1)} loaded")

    def upload_secret_image(self):
        self.filename2 = filedialog.askopenfilename(
            initialdir="SampleImages",
            title="Select Secret Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg")]
        )
        self.update_status(f"✅ Secret Image: {os.path.basename(self.filename2)} loaded")

    def get_next_filename(self, directory, base_filename):
        if not os.path.exists(directory):
            os.makedirs(directory)
        i = 1
        while os.path.exists(os.path.join(directory, f"{base_filename}_{i}.png")):
            i += 1
        return os.path.join(directory, f"{base_filename}_{i}.png")

    def hide_image(self):
        if not all([self.filename1, self.filename2]):
            self.update_status("❌ Please upload both cover and secret images first")
            return

        cover_img = cv2.imread(self.filename1)
        secret_img = cv2.imread(self.filename2)
        
        secret_img = cv2.resize(secret_img, (cover_img.shape[1], cover_img.shape[0]))
        secret_img_normalized = secret_img // 16
        
        encrypted_img = cover_img.copy()
        for i in range(cover_img.shape[0]):
            for j in range(cover_img.shape[1]):
                for k in range(cover_img.shape[2]):
                    encrypted_img[i, j, k] = (cover_img[i, j, k] & 0xF0) | (secret_img_normalized[i, j, k] & 0x0F)

        encrypted_filename = self.get_next_filename("EncryptedImages", "encrypted_image")
        cv2.imwrite(encrypted_filename, encrypted_img)
        self.update_status(f"✅ Secret image hidden and saved as: {os.path.basename(encrypted_filename)}")

        self.show_comparison(cover_img, encrypted_img, "Cover Image", "Encrypted Image")

    def extract_image(self):
        encrypted_filename = filedialog.askopenfilename(
            initialdir="EncryptedImages",
            title="Select Encrypted Image",
            filetypes=[("PNG files", "*.png")]
        )
        
        if not encrypted_filename:
            return
            
        encrypted_img = cv2.imread(encrypted_filename)
        secret_img = np.zeros_like(encrypted_img)
        
        for i in range(encrypted_img.shape[0]):
            for j in range(encrypted_img.shape[1]):
                for k in range(encrypted_img.shape[2]):
                    secret_img[i, j, k] = (encrypted_img[i, j, k] & 0x0F) * 16

        extracted_filename = self.get_next_filename("ExtractedImages", "extracted_secret")
        cv2.imwrite(extracted_filename, secret_img)
        self.update_status(f"✅ Secret image extracted and saved as: {os.path.basename(extracted_filename)}")
        
        self.show_comparison(encrypted_img, secret_img, "Encrypted Image", "Extracted Secret")

    def calculate_metrics(self):
        if not self.filename1:
            self.update_status("❌ Please upload cover image first")
            return
            
        cover_img = cv2.imread(self.filename1)
        encrypted_filename = filedialog.askopenfilename(
            initialdir="EncryptedImages",
            title="Select Encrypted Image",
            filetypes=[("PNG files", "*.png")]
        )
        
        if not encrypted_filename:
            return
            
        encrypted_img = cv2.imread(encrypted_filename)
        encrypted_img = cv2.resize(encrypted_img, (cover_img.shape[1], cover_img.shape[0]))

        cover_gray = cv2.cvtColor(cover_img, cv2.COLOR_BGR2GRAY)
        encrypted_gray = cv2.cvtColor(encrypted_img, cv2.COLOR_BGR2GRAY)

        ssim_value = ssim(cover_gray, encrypted_gray)
        mse = np.mean((cover_img - encrypted_img) ** 2)
        psnr_value = 100 if mse == 0 else 10 * np.log10((255 ** 2) / mse)

        self.update_status(
            f"📊 Image Quality Metrics:\n"
            f"   PSNR: {psnr_value:.2f} dB\n"
            f"   SSIM: {ssim_value:.4f}"
        )

    def show_comparison(self, img1, img2, title1, title2):
        plt.style.use('dark_background')
        figure, axis = plt.subplots(1, 2, figsize=(12, 6))
        figure.patch.set_facecolor('#2c3e50')
        
        axis[0].set_title(title1, color='white', pad=20)
        axis[1].set_title(title2, color='white', pad=20)
        
        axis[0].imshow(cv2.cvtColor(img1, cv2.COLOR_BGR2RGB))
        axis[1].imshow(cv2.cvtColor(img2, cv2.COLOR_BGR2RGB))
        
        for ax in axis:
            ax.set_xticks([])
            ax.set_yticks([])
        
        plt.tight_layout()
        plt.show()

    def update_status(self, message):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.config(state=tk.DISABLED)

    def run(self):
        self.main.mainloop()

if __name__ == "__main__":
    app = ModernSteganographyApp()
    app.run()
