# Auto Touch Keyboard (`auto-touch-keyboard`)

[![Organization](https://img.shields.io/badge/Org-uhcal--oss-blue.svg)](https://github.com/uhcal-oss)
[![License](https://img.shields.io/badge/License-GPLv3-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-GNOME%20Wayland%20%2F%20X11-orange.svg)](https://www.gnome.org)
[![Target](https://img.shields.io/badge/Target-Faz%201%20%2F%20Faz%202%20Smart%20Boards-red.svg)](https://github.com/uhcal-oss)

Akıllı tahtalar ve dokunmatik Linux cihazları için **fiziksel klavye takılı olmadığında ekran klavyesini otomatik olarak açan**, fiziksel klavye takıldığında ise ekran klavyesini otomatik kapatan hafif ve güvenilir arka plan yöneticisi.

---

## 📌 Özellikler (Features)

- **Akıllı Donanım Tespiti**:
  - Standart sistemlerde güç tuşu (power button), video bus veya fare alıcıları klavye gibi algılanıp ekran klavyesinin açılmasını engelleyebilir.
  - `auto-touch-keyboard`, Linux çekirdeğinin tuş yetenek haritasını (bitmaps: `KEY_A` ve `KEY_SPACE`) analiz ederek **yalnızca gerçek yazı klavyelerini** fiziksel klavye olarak kabul eder.
- **Anlık Udev Dinleme (Zero CPU Overhead)**:
  - Polling (sürekli döngü) yapmaz; Linux kernel netlink soketi üzerinden udev olaylarını dinler. Klavye takıldığı veya çıkarıldığı anda mikrosaniyeler içinde tetiklenir.
- **Masaüstü Bildirimleri**:
  - Klavye çıkarıldığında veya takıldığında masaüstünde anlık bilgilendirme bildirimi gösterir.
- **Masaüstü ve Üst Panel Kısayolları**:
  - İstenildiği zaman tek dokunuşla açıp kapatmak için masaüstü kısayolu (`Ekran Klavyesi Aç/Kapat`) ve GNOME üst panel erişilebilirlik entegrasyonu sunar.

---

## 🚀 Kurulum (Installation)

```bash
git clone https://github.com/uhcal-oss/auto-touch-keyboard.git
cd auto-touch-keyboard
./install.sh
```

Kurulum betiği otomatik olarak:
1. Gerekli Python bağımlılıklarını kontrol eder (`python3-pyudev`, `python3-gobject`).
2. `auto-touch-keyboard` komutunu sistem yoluna ekler (`~/.local/bin/auto-touch-keyboard`).
3. Sistem açılışında otomatik çalışacak `auto-touch-keyboard.service` kullanıcı servisini kurar ve başlatır.
4. Masaüstü ve uygulama menüsüne dokunmatik aç/kapat simgesini ekler.

---

## 🛠️ Kullanım (Usage)

Servis arka planda otomatik çalışır, manuel bir işlem gerekmez. Ancak terminalden kontrol etmek isterseniz:

```bash
# Mevcut klavye ve durum bilgisini gösterir
auto-touch-keyboard status

# Klavyeleri anlık tarayıp ekran klavyesini duruma göre ayarlar
auto-touch-keyboard check

# Ekran klavyesini manuel aç/kapat (toggle)
auto-touch-keyboard toggle

# Manuel olarak aç
auto-touch-keyboard enable

# Manuel olarak kapat
auto-touch-keyboard disable
```

### Servis Durumunu Kontrol Etme
```bash
systemctl --user status auto-touch-keyboard.service
journalctl --user -u auto-touch-keyboard.service -f
```

---

## 📄 Lisans

Bu proje GNU General Public License v3.0 (GPLv3) ile lisanslanmıştır.  
Urla Hakan Çeken Anadolu Lisesi Açık Kaynak Topluluğu ([@uhcal-oss](https://github.com/uhcal-oss)) tarafından geliştirilmiştir.
