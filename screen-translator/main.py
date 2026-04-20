import threading
import tkinter as tk
import socket
import shutil
import subprocess
import tempfile
import os
import re
from dataclasses import dataclass
from tkinter import messagebox

import mss
import pyperclip
from deep_translator import GoogleTranslator
from PIL import Image

socket.setdefaulttimeout(15)


def resolve_tesseract_path() -> str:
    candidates = [
        shutil.which("tesseract"),
        os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "Tesseract-OCR", "tesseract.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"), "Tesseract-OCR", "tesseract.exe"),
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for path in candidates:
        if path and os.path.exists(path):
            return path
    return ""


tesseract_path = resolve_tesseract_path()


@dataclass
class Selection:
    x1: int
    y1: int
    x2: int
    y2: int

    def normalize(self) -> "Selection":
        return Selection(
            min(self.x1, self.x2),
            min(self.y1, self.y2),
            max(self.x1, self.x2),
            max(self.y1, self.y2),
        )

    def size_valid(self) -> bool:
        area = (self.x2 - self.x1) * (self.y2 - self.y1)
        return area > 100


class SelectionOverlay:
    def __init__(self, on_done):
        self.on_done = on_done
        self.start_x = 0
        self.start_y = 0
        self.rect_id = None

        self.window = tk.Toplevel()
        self.window.attributes("-fullscreen", True)
        self.window.attributes("-topmost", True)
        self.window.attributes("-alpha", 0.25)
        self.window.configure(bg="black")
        self.window.title("Bir alan sec")

        self.canvas = tk.Canvas(self.window, cursor="cross", bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.window.bind("<Escape>", self.cancel)

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
            self.start_x,
            self.start_y,
            self.start_x,
            self.start_y,
            outline="#00ff7f",
            width=2,
        )

    def on_drag(self, event):
        if self.rect_id:
            self.canvas.coords(self.rect_id, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        selection = Selection(self.start_x, self.start_y, event.x, event.y).normalize()
        self.window.destroy()
        if selection.size_valid():
            self.on_done(selection)

    def cancel(self, _event):
        self.window.destroy()


class ResultWindow:
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("Anlik Ceviri")
        self.window.geometry("560x360")
        self.window.attributes("-topmost", True)
        self.window.protocol("WM_DELETE_WINDOW", self.hide)

        toolbar = tk.Frame(self.window)
        toolbar.pack(fill=tk.X, padx=8, pady=8)

        self.copy_btn = tk.Button(toolbar, text="Ceviriyi Kopyala")
        self.copy_btn.pack(side=tk.LEFT)

        self.status_var = tk.StringVar(value="Hazir")
        status_label = tk.Label(toolbar, textvariable=self.status_var, anchor="w")
        status_label.pack(side=tk.LEFT, padx=12)

        self.text = tk.Text(self.window, wrap="word")
        self.text.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

    def hide(self):
        self.window.withdraw()

    def set_status(self, status: str):
        self.status_var.set(status)

    def set_result(self, source: str, translated: str):
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, "OCR Metni:\n")
        self.text.insert(tk.END, source.strip() + "\n\n")
        self.text.insert(tk.END, "Ceviri:\n")
        self.text.insert(tk.END, translated.strip())
        self.copy_btn.config(command=lambda: pyperclip.copy(translated.strip()))


class ScreenTranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Translator")
        self.root.geometry("440x220")

        frame = tk.Frame(root, padx=16, pady=16)
        frame.pack(fill=tk.BOTH, expand=True)

        title = tk.Label(
            frame,
            text="Ekranda bir alan sec ve aninda cevir",
            font=("Segoe UI", 12, "bold"),
        )
        title.pack(pady=(0, 10))

        lang_frame = tk.Frame(frame)
        lang_frame.pack(fill=tk.X, pady=(0, 8))

        tk.Label(lang_frame, text="Kaynak dil:").pack(side=tk.LEFT)
        self.src_lang = tk.StringVar(value="auto")
        tk.Entry(lang_frame, textvariable=self.src_lang, width=8).pack(side=tk.LEFT, padx=(6, 18))

        tk.Label(lang_frame, text="Hedef dil:").pack(side=tk.LEFT)
        self.dst_lang = tk.StringVar(value="tr")
        tk.Entry(lang_frame, textvariable=self.dst_lang, width=8).pack(side=tk.LEFT, padx=6)

        note = tk.Label(
            frame,
            text="Ornek dil kodlari: auto, en, tr, de, fr",
            fg="#666666",
        )
        note.pack()

        self.select_btn = tk.Button(frame, text="Alan Sec ve Cevir", command=self.start_selection, height=2)
        self.select_btn.pack(fill=tk.X, pady=(12, 6))

        self.status_var = tk.StringVar(value="Hazir")
        tk.Label(frame, textvariable=self.status_var).pack(anchor="w")

        self.result_window = ResultWindow()
        self.result_window.window.withdraw()

    def _ensure_result_window(self):
        if not self.result_window.window.winfo_exists():
            self.result_window = ResultWindow()

    def start_selection(self):
        if not tesseract_path:
            self.show_error(
                "Tesseract bulunamadi. Lutfen kurulum yolunu kontrol et: "
                "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
            )
            return
        self.status_var.set("Alan seciliyor...")
        self.root.withdraw()
        self.root.after(150, lambda: SelectionOverlay(self.process_selection))

    def process_selection(self, selection: Selection):
        self.root.deiconify()
        src_lang = self.src_lang.get().strip() or "auto"
        dst_lang = self.dst_lang.get().strip() or "tr"
        self.select_btn.config(state=tk.DISABLED)
        self.status_var.set("Goruntu okunuyor...")
        threading.Thread(
            target=self._translate_pipeline,
            args=(selection, src_lang, dst_lang),
            daemon=True,
        ).start()

    def _set_status(self, text: str):
        self.root.after(0, lambda: self.status_var.set(text))

    def _translate_pipeline(self, selection: Selection, src_lang: str, dst_lang: str):
        try:
            self._set_status("Goruntu yakalaniyor...")
            image = self.capture_region(selection)
            self._set_status("OCR yapiliyor...")
            prepared_image = self.prepare_image_for_ocr(image)
            raw_text = self.run_ocr(prepared_image)
            extracted_text = self.normalize_ocr_text(raw_text)
            if not extracted_text:
                raise RuntimeError("Metin algilanamadi. Daha net bir alan secmeyi dene.")

            self._set_status("Ceviri yapiliyor...")
            translated = GoogleTranslator(
                source=src_lang,
                target=dst_lang,
            ).translate(extracted_text)
            self.root.after(0, lambda: self.show_result(extracted_text, translated))
        except Exception as exc:
            self.root.after(0, lambda: self.show_error(str(exc)))
        finally:
            self.root.after(0, lambda: self.select_btn.config(state=tk.NORMAL))

    @staticmethod
    def capture_region(selection: Selection) -> Image.Image:
        with mss.mss() as sct:
            monitor = {
                "top": selection.y1,
                "left": selection.x1,
                "width": selection.x2 - selection.x1,
                "height": selection.y2 - selection.y1,
            }
            shot = sct.grab(monitor)
            return Image.frombytes("RGB", shot.size, shot.rgb)

    @staticmethod
    def prepare_image_for_ocr(image: Image.Image) -> Image.Image:
        # Larger captures can make OCR very slow; keep a practical size ceiling.
        max_side = 1800
        width, height = image.size
        scale = min(1.0, max_side / max(width, height))
        if scale < 1.0:
            image = image.resize((int(width * scale), int(height * scale)), Image.LANCZOS)
        return image.convert("L")

    @staticmethod
    def run_ocr(image: Image.Image) -> str:
        if not tesseract_path:
            raise RuntimeError("Tesseract bulunamadi. Lutfen PATH ayarini kontrol et.")

        temp_path = ""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                temp_path = tmp.name
            image.save(temp_path, format="PNG")

            command = [
                tesseract_path,
                temp_path,
                "stdout",
                "--oem",
                "3",
                "--psm",
                "6",
                "-l",
                "eng+tur",
            ]
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

            if result.returncode != 0:
                stderr_lower = (result.stderr or "").lower()
                if "failed loading language" in stderr_lower or "error opening data file" in stderr_lower:
                    fallback = subprocess.run(
                        [tesseract_path, temp_path, "stdout", "--oem", "3", "--psm", "6"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        check=False,
                    )
                    if fallback.returncode == 0:
                        return (fallback.stdout or "").strip()
                    raise RuntimeError(f"OCR hatasi: {fallback.stderr.strip() or 'Bilinmeyen hata'}")
                raise RuntimeError(f"OCR hatasi: {result.stderr.strip() or 'Bilinmeyen hata'}")

            return (result.stdout or "").strip()
        except subprocess.TimeoutExpired:
            raise RuntimeError("OCR zaman asimina ugradi. Daha kucuk/temiz bir alan sec.")
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    @staticmethod
    def normalize_ocr_text(text: str) -> str:
        if not text:
            return ""

        # Normalize line endings and trim noisy spaces.
        cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
        cleaned = re.sub(r"[ \t]+", " ", cleaned).strip()
        if not cleaned:
            return ""

        lines = [line.strip() for line in cleaned.split("\n")]
        merged_lines = []
        current = ""
        punctuation = ".!?;:)]}\"'"

        for line in lines:
            if not line:
                if current:
                    merged_lines.append(current.strip())
                    current = ""
                continue

            if not current:
                current = line
                continue

            # If previous line ends with hyphen-like break, merge without extra space.
            if current.endswith("-"):
                current = current[:-1] + line
                continue

            # If sentence likely continues, join with a space.
            if current[-1] not in punctuation:
                current = f"{current} {line}"
            else:
                merged_lines.append(current.strip())
                current = line

        if current:
            merged_lines.append(current.strip())

        # Keep paragraph separation for readability.
        return "\n\n".join(part for part in merged_lines if part)

    def show_result(self, source: str, translated: str):
        self.status_var.set("Tamamlandi")
        self._ensure_result_window()
        self.result_window.window.deiconify()
        self.result_window.window.lift()
        self.result_window.window.focus_force()
        self.result_window.set_status("Hazir")
        self.result_window.set_result(source, translated)

    def show_error(self, message: str):
        self.status_var.set("Hata")
        messagebox.showerror("Screen Translator", message)


def main():
    root = tk.Tk()
    ScreenTranslatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
