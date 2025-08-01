import sys
import subprocess
import os
import stat
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QPushButton, QSpinBox, QLabel, QTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt


class NitroSenseGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NitroSense Fan Kontrol - SD")
        self.setGeometry(100, 100, 600, 400)
        self.ec_path = "/dev/ec"
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        power_layout = QHBoxLayout()
        power_label = QLabel("Güç Modu:")
        self.power_combo = QComboBox()
        self.power_combo.addItems(["Quiet", "Default", "Performance"])
        power_layout.addWidget(power_label)
        power_layout.addWidget(self.power_combo)
        main_layout.addLayout(power_layout)

        fan_layout = QHBoxLayout()
        fan_label = QLabel("Fan Modu:")
        self.fan_combo = QComboBox()
        self.fan_combo.addItems(["Auto", "Custom", "Max"])
        self.fan_spin = QSpinBox()
        self.fan_spin.setRange(0, 100)
        self.fan_spin.setValue(50)
        self.fan_spin.setSuffix("%")
        self.fan_spin.setEnabled(False)
        fan_layout.addWidget(fan_label)
        fan_layout.addWidget(self.fan_combo)
        fan_layout.addWidget(self.fan_spin)
        main_layout.addLayout(fan_layout)

        self.fan_combo.currentTextChanged.connect(self.toggle_fan_spin)

        apply_button = QPushButton("Ayarları Uygula")
        apply_button.clicked.connect(self.apply_settings)
        main_layout.addWidget(apply_button)

        debug_layout = QHBoxLayout()
        debug_label = QLabel("Hata Ayıklama:")
        self.read_ec_button = QPushButton("EC Oku")
        self.energy_button = QPushButton("Enerji Verileri")
        self.nvidia_button = QPushButton("Nvidia-Powerd Yeniden Başlat")
        self.read_ec_button.clicked.connect(self.read_ec)
        self.energy_button.clicked.connect(self.read_energy)
        self.nvidia_button.clicked.connect(self.restart_nvidia)
        debug_layout.addWidget(debug_label)
        debug_layout.addWidget(self.read_ec_button)
        debug_layout.addWidget(self.energy_button)
        debug_layout.addWidget(self.nvidia_button)
        main_layout.addLayout(debug_layout)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        main_layout.addWidget(self.output_text)

    def toggle_fan_spin(self):
        self.fan_spin.setEnabled(self.fan_combo.currentText() == "Custom")

    def check_ec(self):
        self.output_text.append(f"Kontrol ediliyor: {self.ec_path}")
        if not os.path.exists(self.ec_path):
            self.output_text.append(f"Hata: {self.ec_path} dosyası bulunamadı!")
            QMessageBox.critical(self, "Hata",
                f"EC dosyası {self.ec_path} bulunamadı!\n"
                "Lütfen 'acpi_ec' kernel modülünü yükleyin ve sistemi yeniden başlatın.\n"
                "Detaylar için: https://github.com/MusiKid/acpi_ec")
            return False
        try:
            mode = os.stat(self.ec_path).st_mode
            self.output_text.append(f"Dosya izinleri: {oct(mode & 0o777)}")
            if not (mode & stat.S_IRUSR and mode & stat.S_IWUSR):
                self.output_text.append(f"Hata: {self.ec_path} için okuma/yazma izni yok!")
                QMessageBox.critical(self, "Hata",
                    f"{self.ec_path} dosyasına okuma/yazma izni yok!\n"
                    "Komutla izinleri düzeltin: 'sudo chmod 660 /dev/ec'\n"
                    "Veya script'i 'sudo' ile çalıştırın.")
                return False
            # Cihaz dosyası olduğunu doğrula
            if not stat.S_ISCHR(mode):
                self.output_text.append(f"Hata: {self.ec_path} bir karakter cihaz dosyası değil!")
                QMessageBox.critical(self, "Hata",
                    f"{self.ec_path} bir karakter cihaz dosyası değil!\n"
                    "Lütfen 'acpi_ec' modülünün doğru yüklendiğinden emin olun.")
                return False
        except PermissionError:
            self.output_text.append(f"Hata: {self.ec_path} dosyasına erişim izni yok!")
            QMessageBox.critical(self, "Hata",
                f"{self.ec_path} dosyasına erişim izni yok!\n"
                "Script'i 'sudo' ile çalıştırın veya dosya izinlerini kontrol edin: 'sudo chmod 660 /dev/ec'")
            return False
        self.output_text.append(f"{self.ec_path} erişilebilir.")
        return True

    def ec_write(self, offset, value):
        try:
            cmd = ["sudo", "dd", f"of={self.ec_path}", "bs=1", f"seek={offset}", "count=1", "conv=notrunc"]
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            _, stderr = process.communicate(input=value)
            if process.returncode != 0:
                self.output_text.append(f"EC yazma hatası (offset {offset}): {stderr}")
                return False
        except subprocess.SubprocessError as e:
            self.output_text.append(f"EC yazma hatası: {str(e)}")
            return False
        self.output_text.append(f"EC yazma başarılı (offset {offset})")
        return True

    def apply_settings(self):
        if not self.check_ec():
            return

        if not self.ec_write(0x03, '\x11'):
            return

        power_mode = self.power_combo.currentText()
        fan_mode = self.fan_combo.currentText()
        fan_percent = self.fan_spin.value()

        if power_mode == "Quiet":
            self.output_text.append("PWR - Quiet")
            self.ec_write(0x2c, '\x00')
            self.ec_write(0x2d, '\x04')
        elif power_mode == "Default":
            self.output_text.append("PWR - Default")
            self.ec_write(0x2c, '\x01')
            self.ec_write(0x2d, '\x04')
        elif power_mode == "Performance":
            self.output_text.append("PWR - Performance")
            self.ec_write(0x2c, '\x04')
            self.ec_write(0x2d, '\x04')

        if fan_mode == "Auto":
            self.output_text.append("FAN - Auto")
            self.ec_write(0x21, '\x10')
            self.ec_write(0x22, '\x04')
        elif fan_mode == "Max":
            self.output_text.append("FAN - Max")
            self.ec_write(0x21, '\x20')
            self.ec_write(0x22, '\x08')
        elif fan_mode == "Custom":
            self.output_text.append(f"FAN - Custom ({fan_percent}%)")
            self.ec_write(0x21, '\x30')
            self.ec_write(0x22, '\x0c')
            hex_pct = f"\\x{fan_percent:02x}"
            self.ec_write(0x37, hex_pct)
            self.ec_write(0x3a, hex_pct)

    def read_ec(self):
        if not self.check_ec():
            return
        try:
            result = subprocess.run(["sudo", "xxd", "-g1", self.ec_path], check=True,
                                   capture_output=True, text=True)
            self.output_text.append("EC Okuma:\n" + result.stdout)
        except subprocess.CalledProcessError as e:
            self.output_text.append(f"EC okuma hatası: {e.stderr}")

    def read_energy(self):
        try:
            result = subprocess.run(
                ["sudo", "find", "/sys/devices/virtual/powercap", "-type", "f", "-iname", "energy_uj",
                 "-print", "-exec", "cat", "{}", ";"],
                check=True, capture_output=True, text=True)
            self.output_text.append("Enerji Verileri:\n" + result.stdout)
        except subprocess.CalledProcessError as e:
            self.output_text.append(f"Enerji verisi okuma hatası: {e.stderr}")

    def restart_nvidia(self):
        try:
            result = subprocess.run(["sudo", "systemctl", "restart", "nvidia-powerd"], check=True,
                                   capture_output=True, text=True)
            self.output_text.append("Nvidia-Powerd yeniden başlatıldı.")
        except subprocess.CalledProcessError as e:
            self.output_text.append(f"Nvidia-Powerd yeniden başlatma hatası: {e.stderr}")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Hata: Bu uygulama root yetkileri gerektirir.")
        print("Lütfen 'sudo python3 main.py' ile çalıştırın.")
        sys.exit(1)
    app = QApplication(sys.argv)
    window = NitroSenseGUI()
    window.show()
    sys.exit(app.exec_())
