# Thunar Custom Actions Manager GUI

A simple graphical tool to backup, restore, and import Thunar custom actions using ZIP files.
After restoring or importing, Thunar is automatically restarted so your changes take effect immediately.

---

## Features

- Backup your Thunar custom actions (uca.xml and uca.d/) to a ZIP file.
- Restore custom actions from a ZIP backup.
- Import custom actions from another ZIP archive (merges with your current actions).
- Automatic Thunar restart after restore/import.
- User-friendly GUI (Python + Tkinter).

---

## Requirements

- Python 3.x
- Tkinter (usually included with Python)
- Thunar (XFCE file manager)
```
sudo apt update
sudo apt install -y thunar python3 python3-tk
```
# additional optional thunar packages
```
sudo apt install -y gir1.2-thunarx-3.0 libthunarx-3-0 thunar-archive-plugin thunar-font-manager thunar-gtkhash thunar-media-tags-plugin thunar-vcs-plugin thunar-volman thunarx-python
```
---

## How to Use
```
git clone https://github.com/thetechstoner/thunar-actions-manager.git
cd thunar-actions-manager

chmod +x thunar_actions_manager.py
./thunar_actions_manager.py
```
---

## License

MIT License
