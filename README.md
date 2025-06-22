# Dekupe App - PyQt5 & OpenCV ile Arka Plan Kaldırma

Bu proje, kullanıcıların seçtikleri bir görselin arka planını otomatik olarak kaldırmalarını sağlayan basit bir masaüstü uygulamasıdır. Görsel işleme için OpenCV, kullanıcı arayüzü için PyQt5 kullanılmıştır. 
Fatma Sena YÜKSEL - Bensu ÖZTÜRK


## Özellikler

- Görsel seçme ve ön izleme
- GrabCut algoritması ile arka plan kaldırma
- Şeffaf PNG olarak çıktı alma
- Temiz, kullanıcı dostu arayüz

## Kullanılan Teknolojiler

- Python 3.10.11
- OpenCV
- PyQt5
- NumPy

## Kurulum ve Çalıştırma

### Gerekli kütüphaneleri kurun

```bash
pip install opencv-python numpy pyqt5
```

### Uygulamayı başlatın:
```bash
python dekupe_app.py
```
### Kullanım
"Görsel Seç" butonuna tıklayarak bir .jpg, .png veya .jpeg dosyası seçin.
Görsel yüklendikten sonra "Arka Planı Kaldır" butonu aktifleşir.
Arka plan kaldırıldıktan sonra çıktıyı .png formatında kaydedin.


