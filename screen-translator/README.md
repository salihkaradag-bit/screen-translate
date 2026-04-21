# Screen Translator (Windows)

Bu uygulama ekrandan secilen bir bolgeyi goruntu olarak alir, Tesseract ile metni okur (OCR) ve metni secilen dile cevirir.

## Neler Yapar?

- Ekrandan fare ile alan secimi
- Secilen bolgede OCR (metin tanima)
- Kaynak dili otomatik (`auto`) veya manuel secme
- Hedef dile ceviri (ornek: `tr`, `en`, `de`)
- Sonucu ayri pencerede gosterme
- `Ceviriyi Kopyala` butonuyla panoya kopyalama

## Gereksinimler

- Windows 10/11
- Python 3.10 veya ustu
- Internet baglantisi (ceviri servisi icin)
- Tesseract OCR (sisteme kurulu olmali)

## Kurulum (Adim Adim)

### 1) Python kurulu mu kontrol et

CMD veya PowerShell:

```bash
python --version
```

Calismiyorsa once Python kur.

### 2) Proje klasorune gir

```bash
cd "C:\Users\Asus\OneDrive - ogr.dpu.edu.tr\Masaüstü\screen-translator"
```

### 3) Python paketlerini yukle

Projede kullanilan paketler:

- mss
- Pillow
- pytesseract
- deep-translator
- pyperclip

Kurulum:

```bash
pip install -r requirements.txt
```

### 4) Tesseract OCR kur

Windows icin onerilen kaynak:

- [UB Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

Kurulumdan sonra su yolu kontrol et:

- `C:\Program Files\Tesseract-OCR\tesseract.exe`

Uygulama bu yolu ve PATH'i otomatik deniyor. Bulamazsa acilista hata verir.

### 5) Uygulamayi calistir

```bash
python main.py
```

## Kullanim

1. Uygulamada kaynak dili gir:
   - Otomatik algi icin: `auto`
   - Manuel ornekler: `en`, `tr`, `de`, `fr`
2. Hedef dili gir (ornek: `tr`).
3. `Alan Sec ve Cevir` butonuna tikla.
4. Ekranda cevrilecek bolgeyi fare ile sec.
5. Sonuc penceresinde:
   - `OCR Metni` (okunan ham metin)
   - `Ceviri` (cevrilmis metin)
6. `Ceviriyi Kopyala` ile metni panoya al.

## Sik Karsilasilan Sorunlar

- **Tesseract bulunamadi**
  - Tesseract'i kur.
  - Kurulum dizinini kontrol et: `C:\Program Files\Tesseract-OCR\tesseract.exe`

- **Metin algilanamadi**
  - Daha net ve buyuk bir alan sec.
  - Dusuk kontrastli veya bulanik goruntu yerine net metin sec.

- **Ceviri hatasi**
  - Internet baglantisini kontrol et.
  - Kaynak/hedef dil kodlarinin dogru oldugunu kontrol et.

- **OCR timeout**
  - Cok buyuk alan secme; daha kucuk bolge sec.

## EXE Olarak Paketleme

Projedeki `build_exe.bat` dosyasi ile tek dosya EXE uretebilirsin.

1. `build_exe.bat` dosyasina cift tikla (veya terminalden calistir).
2. Script gerekirse `pyinstaller` kurar.
3. Build bitince su dosya olusur:
   - `dist\ScreenTranslator.exe`
4. Bu EXE dosyasina kisayol olusturup uygulama gibi kullanabilirsin.

Not: Kod degisikliklerinden sonra yeni EXE almak icin `build_exe.bat` tekrar calistirilmalidir.
