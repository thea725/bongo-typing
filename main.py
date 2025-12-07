import sys
import threading
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from pynput import keyboard


class FloatingImageWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.img_untyping = QPixmap("./assets/bongo_normal.png")
        self.img_typing = QPixmap("./assets/bongo_typing.png")

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
        self.set_typing(True)

    def on_key_release(self, key):
        self.set_typing(False)

    def set_typing(self, typing):
        if typing:
            self.label.setPixmap(self.img_typing)
            self.resize(self.img_typing.size())
        else:
            self.label.setPixmap(self.img_untyping)
            self.resize(self.img_untyping.size())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.drag_pos:
            delta = event.globalPosition().toPoint() - self.drag_pos
            self.move(self.pos() + delta)
            self.drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = FloatingImageWindow()
    w.show()
    sys.exit(app.exec())
