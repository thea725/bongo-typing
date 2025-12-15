import sys
import threading
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from pynput import keyboard
import configparser as cp

config = cp.ConfigParser()

VK_Q = 0x51
scale_factor = 0.7

class BongoWindow(QWidget):
    
    quitRequested = pyqtSignal()

    def __init__(self):
        super().__init__()

        # Config Position Loading
        if not config.read("config.ini"):
            # Calculating Position
            screen = QApplication.primaryScreen()
            geom = screen.availableGeometry()
            pos_x = geom.right() - self.width()
            pos_y = geom.bottom() - self.height()

            # Move and Save
            self.move(QPoint(pos_x, pos_y))
            config["app"] = {
                "posx": pos_x,
                "posy": pos_y
            }
            self.saveConfig()
        else:
            self.move(
                QPoint(
                    int(config["app"]["posx"]),
                    int(config["app"]["posy"])
                )
            )

        self.img_untyping = QPixmap("./assets/normal.png")
        self.img_untyping = self.img_untyping.scaled(
            self.img_untyping.width() * scale_factor,
            self.img_untyping.height() * scale_factor
        )
        self.img_typing = QPixmap("./assets/typing.png")
        self.img_typing = self.img_typing.scaled(
            self.img_typing.width() * scale_factor,
            self.img_typing.height() * scale_factor
        )

        self.label = QLabel(self)
        self.label.setPixmap(self.img_untyping)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.resize(self.img_untyping.size())

        self.drag_pos = None
        self.start_keyboard_listener()

        self.quitRequested.connect(QApplication.quit)

        self.keys = set()
        
    def start_keyboard_listener(self):
        t = threading.Thread(target=self._keyboard_listener_thread, daemon=True)
        t.start()

    def _keyboard_listener_thread(self):
        with keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        ) as listener:
            listener.join()

    def on_key_press(self, key):
        self.keys.add(key)
        if self.is_ctrl_q():
            self.quitRequested.emit()
        self.set_typing(True)

    def on_key_release(self, key):
        self.keys.discard(key)
        self.set_typing(False)

    def set_typing(self, typing):
        if typing:
            self.label.setPixmap(self.img_typing)
            self.resize(self.img_typing.size())
        else:
            self.label.setPixmap(self.img_untyping)
            self.resize(self.img_untyping.size())

    def is_ctrl_q(self):
        ctrl = keyboard.Key.ctrl_l in self.keys or keyboard.Key.ctrl_r in self.keys
        q = any(
            isinstance(k, keyboard.KeyCode) and k.vk == VK_Q
            for k in self.keys
        )
        return ctrl and q

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.drag_pos:
            delta = event.globalPosition().toPoint() - self.drag_pos
            pos = self.pos() + delta
            self.move(pos)
            self.drag_pos = event.globalPosition().toPoint()

            # save to config.ini
            config["app"] = {
                "posx": pos.x(),
                "posy": pos.y()
            }
            self.saveConfig() 

    def mouseReleaseEvent(self, event):
        self.drag_pos = None
    
    def saveConfig(self):
        with open("config.ini", "w") as f:
            config.write(f)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = BongoWindow()
    w.show()
    sys.exit(app.exec())