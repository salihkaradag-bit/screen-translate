# Screen Translator (Windows MVP)

Ekranda bir bolge secerek OCR ile metni okur ve aninda ceviri sonucunu gosterir.

## Ozellikler

- Fare ile bolge secimi (overlay)
- OCR ile metin tanima (Tesseract)
- Otomatik veya manuel kaynak dil
- Hedef dile anlik ceviri
- Cevrilen metni tek tikla kopyalama

## Kurulum

1. Python 3.10+ kur.
2. Projeyi ac ve bagimliliklari yukle:

```powershell
pip install -r requirements.txt
```

3. Tesseract OCR kur:
   - Windows icin: [UB Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
   - Kurulumdan sonra `tesseract` komutu PATH'te olmali.

4. Uygulamayi baslat:

```powershell
python main.py
```

## Kullanim

1. `Alan Sec ve Cevir` butonuna tikla.
2. Ekranda cevirmek istedigin alani fare ile sec.
3. Sonuc penceresinde OCR metni ve ceviriyi gor.
4. `Ceviriyi Kopyala` ile panoya al.

## Uygulama gibi calistirma (CMD acmadan)

Bu proje icinde hazir bir EXE build scripti var.

1. Proje klasorunde `build_exe.bat` dosyasina cift tikla.
2. Build tamamlaninca su dosya olusur:
   - `dist\ScreenTranslator.exe`
3. Bu `.exe` dosyasina masaustunde kisayol olusturup normal uygulama gibi ac.
4. Istersen `run_app.vbs` dosyasina cift tiklayarak uygulamayi arka planda (konsolsuz) baslat.

Not: Her kod degisikliginden sonra yeni EXE almak icin `build_exe.bat` dosyasini tekrar calistir.

## Notlar

- Ilk prototipte ceviri servisi olarak `deep-translator` (Google) kullanilir.
- Internet yoksa veya servis engelliyse ceviri hatasi alabilirsin.
- Daha iyi OCR icin yuksek kontrastli ve net bolge sec.
