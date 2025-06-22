import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog, QMessageBox)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt


class ImageDekupe(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dekupe App")  # Pencere başlığını belirliyoruz
        self.setGeometry(200, 200, 600, 600)  # Pencerenin konumu ve boyutu

        # Görselin gösterileceği QLabel oluşturuluyor
        self.label = QLabel("Görsel seçiniz", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("border: 2px dashed #999; padding: 20px;")  # Dashed çerçeve ve iç padding

        #İki temel buton oluşturuyoruz:görsel seçmek, diğeri arka planı kaldırmak için
        self.btn_select = QPushButton("Görsel Seç")
        self.btn_process = QPushButton("Arka Planı Kaldır")
        self.btn_process.setEnabled(False) # Görsel seçilmeden arka plan kaldırma butonu aktif olmasın

        # Butonlara sade ve hoş bir mavi stil veriyoruz
        button_style = """
        QPushButton {
            background-color: #007ACC;
            color: white;
            border-radius: 6px;
            padding: 10px;
        }
        QPushButton:hover {
            background-color: #005999;
        }
        """
        self.btn_select.setStyleSheet(button_style)
        self.btn_process.setStyleSheet(button_style)

        # Dikey olarak arayüz elemanlarını yerleştiriyoruz
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.btn_select)
        layout.addWidget(self.btn_process)
        self.setLayout(layout)

        # Butonlara tıklanınca ne olacağı tanımlanıyor
        self.btn_select.clicked.connect(self.select_image)
        self.btn_process.clicked.connect(self.remove_background)

        # Seçilen görselin yolu ve OpenCV formatında hali saklanacak
        self.image_path = None
        self.cv_image = None

    def select_image(self):
        # Kullanıcıdan görsel seçmesini istiyoruz
        file_path, _ = QFileDialog.getOpenFileName(self, "Görsel Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg)")
        if file_path:
            self.image_path = file_path
            self.cv_image = cv2.imread(file_path)  # Görseli OpenCV ile BGR olarak okuyoruz

            # BGR formatını RGB'ye çeviriyoruz
            image = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2RGB)
            h, w, ch = image.shape

            # QImage ile PyQt tarafına uygun hale getiriyoruz
            qt_image = QImage(image.data, w, h, ch * w, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image).scaled(400, 400, Qt.KeepAspectRatio)  # Oranı koruyarak yeniden boyutlandır
            self.label.setPixmap(pixmap)

            self.btn_process.setEnabled(True) # Görsel seçildiği için işleme butonunu aktif hale getiriyoruz

    def remove_background(self):
        if self.cv_image is None:
            return # görsel yoksa işlem yapılmasın

        try:
            img = self.cv_image.copy()
            h, w = img.shape[:2]

            rect = (50, 50, w - 100, h - 100) # GrabCut algoritması için sabit bir dikdörtgen seçiyoruz

            # Gerekli boş maskeler ve modeller başlatılıyor
            mask = np.zeros(img.shape[:2], np.uint8)  # Başlangıçta tüm pikseller arka plan kabul ediliyor
            bgModel = np.zeros((1, 65), np.float64)
            fgModel = np.zeros((1, 65), np.float64)

            cv2.grabCut(img, mask, rect, bgModel, fgModel, 10, cv2.GC_INIT_WITH_RECT) # GrabCut algoritmasını 10 iterasyonla uyguluyoruz

            mask1 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8") # Sadece ön plan (1 ve 3) pikselleri tutularak binary maske oluşturuluyor

            # Maskeyi temizlemek ve kenarları düzeltmek için morfolojik işlemler uygulanıyor
            kernel = np.ones((3, 3), np.uint8)
            mask2 = cv2.morphologyEx(mask1, cv2.MORPH_OPEN, kernel, iterations=2)
            mask2 = cv2.morphologyEx(mask2, cv2.MORPH_CLOSE, kernel, iterations=2)

            mask2 = cv2.erode(mask2, np.ones((2, 2), np.uint8), iterations=1) # Hafif erozyon ile kenarlarda kalan ince hataları azaltıyoruz

            # Konturları tespit edip maskeye yeniden doldurarak boşlukları kapatıyoruz
            contours, _ = cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(mask2, contours, -1, 1, thickness=cv2.FILLED)

            # Maske üzerinden şeffaflık (alpha kanalı) oluşturuluyor
            alpha = mask2 * 255
            result = cv2.bitwise_and(img, img, mask=mask2)  # Sadece ön plan kalacak şekilde kesiliyor
            b, g, r = cv2.split(result)
            rgba = cv2.merge((b, g, r, alpha))  # Alpha kanalı eklenerek RGBA oluşturuluyor

            # Kullanıcıdan sonucu PNG olarak nereye kaydetmek istediği soruluyor
            save_path, _ = QFileDialog.getSaveFileName(
                self, "PNG olarak kaydet", os.path.splitext(self.image_path)[0] + "_dekupe.png", "PNG Files (*.png)"
            )
            if save_path:
                cv2.imwrite(save_path, rgba)
                QMessageBox.information(self, "Başarılı", "Dekupe Görsel kaydedildi!")

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Hata oluştu:\n{str(e)}") # Hata yakalanırsa kullanıcıya mesaj gösteriyoruz


# Uygulama başlatılıyor
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageDekupe()
    window.show()
    sys.exit(app.exec_()) 
