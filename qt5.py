import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
import cv2
import tkinter as tk
from tkinter import ttk

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create layout for the central widget
        layout = QGridLayout(central_widget)

        # Add a button
        button = QPushButton("Click me", self)
        button.clicked.connect(self.onButtonClick)
        layout.addWidget(button, 0, 0)

        # Embed the Tkinter window
        self.embedTkinterWindow(layout, 0, 1)

        # Embed the OpenCV imshow window
        self.embedOpenCVImshow(layout, 1, 0, 1, 2)

        self.setWindowTitle("Qt Window")
        self.setGeometry(100, 100, 800, 600)
        self.show()

    def embedTkinterWindow(self, layout, row, col):
        # Create a Tkinter window
        tkinter_window = tk.Tk()
        tkinter_window.title("Tkinter Window")

        # Add buttons or widgets to the Tkinter window
        button = ttk.Button(tkinter_window, text="Tkinter Button")
        button.pack()

        # Embed the Tkinter window in the Qt layout
        window_id = tkinter_window.winfo_id()
        embed_frame = QWidget(self)
        embed_frame.setGeometry(0, 0, 300, 200)
        embed_frame.createWindowContainer(window_id)
        layout.addWidget(embed_frame, row, col)

    def embedOpenCVImshow(self, layout, row, col, rowspan, colspan):
        # Create a blank image for demonstration
        img = QImage(640, 480, QImage.Format_RGB32)
        img.fill(Qt.green)

        # Convert QImage to QPixmap
        pixmap = QPixmap.fromImage(img)

        # Create a QLabel to display the image
        label = QLabel(self)
        label.setPixmap(pixmap)

        # Embed the QLabel in the Qt layout
        layout.addWidget(label, row, col, rowspan, colspan)

    def onButtonClick(self):
        print("Button clicked!")


def main():
    try:
        app = QApplication(sys.argv)
        window = MyMainWindow()
    except KeyboardInterrupt:
        sys.exit(app.exec_())

if __name__ == '__main__':
    main()