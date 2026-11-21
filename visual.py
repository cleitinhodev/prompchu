"""Owl palette and shared, optional border lighting (original implementation)."""
import math
from PySide6.QtCore import QSettings, Qt, QTimer, QElapsedTimer, QEvent, QObject, QRectF
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

def preferences():
    return QSettings('Bugzinho', 'PrompchuAppearance')

STYLE = '''
QWidget {color:#eee8fa;font-family:"Segoe UI";font-size:13px;}
QMainWindow,QDialog {background:#100e1b;}
QWidget#canvas {background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #151020,stop:1 #181326);}
QFrame#card {background:#211a30;border:1px solid #3b2e50;border-radius:16px;}
QFrame#header {background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #302043,stop:0.55 #49305b,stop:1 #292039);border:1px solid #614578;border-radius:18px;}
QLabel {background:transparent;border:0;}
QLabel#brand {font-size:27px;font-weight:800;color:#ffe0b3;}
QLabel#title {font-size:23px;font-weight:700;color:#fff1dc;}
QLabel#section {font-size:14px;font-weight:700;color:#d7b8ff;}
QLabel#muted {color:#ad9ebf;font-size:12px;}
QLabel#chip {background:#382746;color:#ffd4b4;border:1px solid #644362;border-radius:9px;padding:4px 9px;}
QLineEdit,QPlainTextEdit,QComboBox {background:#171321;border:1px solid #463650;border-radius:9px;padding:9px;selection-background-color:#65458c;selection-color:#fff;}
QLineEdit:hover,QComboBox:hover {border-color:#8965a9;}
QLineEdit:focus,QPlainTextEdit:focus,QComboBox:focus {border-color:#f4b58d;}
QComboBox {padding-right:22px;min-height:20px;}
QComboBox QAbstractItemView {background:#261c35;color:#f4eaff;selection-background-color:#563975;padding:5px;}
QPushButton {background:#332640;border:1px solid #574164;border-radius:9px;padding:9px 13px;font-weight:600;}
QPushButton:hover {background:#483254;border-color:#b78be0;}
QPushButton:pressed {background:#5a3e70;}
QPushButton:focus {border-color:#f4b58d;}
QPushButton#primary {background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #ffc69a,stop:1 #ed9cad);color:#281a30;border:0;font-weight:700;}
QPushButton#primary:hover {background:#ffdbb2;}
QPushButton#danger {background:#38202e;color:#ffa9b8;border-color:#694050;}
QPushButton#danger:hover {background:#63303f;}
QPushButton:disabled {background:#241f2d;color:#73677e;border-color:#352b40;}
QListWidget {background:transparent;border:0;outline:0;}
QListWidget::item {background:#272033;border:1px solid #382c46;border-radius:11px;padding:15px 12px;margin:4px 0;color:#d8cbe7;}
QListWidget::item:hover {background:#342740;border-color:#72528d;}
QListWidget::item:selected {background:#49325e;border:1px solid #ba8de7;color:#fff3e0;}
QCheckBox {spacing:7px;background:transparent;}
QCheckBox::indicator {width:16px;height:16px;border:1px solid #8e6b9f;border-radius:5px;background:#21182f;}
QCheckBox::indicator:checked {background:#edb58e;border:3px solid #60466f;}
QSplitter::handle {background:transparent;width:12px;}
QSplitter::handle:hover {background:#714d8e;border-radius:4px;}
QTabWidget::pane {border:0;background:transparent;}
QTabBar::tab {background:#241c30;color:#bca8ce;padding:9px 18px;border-bottom:2px solid transparent;}
QTabBar::tab:selected {color:#ffdbb2;border-bottom:2px solid #eeb18e;background:#33253e;}
QTabBar::tab:hover {background:#3c2c49;}
QScrollArea {border:0;background:transparent;}
QScrollBar:vertical {background:transparent;width:9px;margin:0;}
QScrollBar::handle:vertical {background:#664a7d;border-radius:4px;min-height:30px;}
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical {height:0;}
QScrollBar::add-page:vertical,QScrollBar::sub-page:vertical {background:transparent;}
QStatusBar {background:#100e1b;color:#ac9aba;font-size:12px;}
QMenu {background:#261c35;border:1px solid #624778;padding:6px;}
QMenu::item {padding:8px 24px;border-radius:6px;}
QMenu::item:selected {background:#543869;}
QToolTip {background:#382744;color:#ffdfbe;border:1px solid #b78be0;padding:7px;}
'''

class BorderLight(QWidget):
    def __init__(self, target, controller, radius=16):
        super().__init__(target)
        self.target, self.controller, self.radius = target, controller, radius
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setFocusPolicy(Qt.NoFocus)
        target.installEventFilter(self)
        self.setGeometry(target.rect())
        self.raise_()
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            self.setGeometry(self.target.rect())
        return False
    def paintEvent(self, event):
        c = self.controller
        if not c.enabled: return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()).adjusted(2,2,-2,-2),self.radius,self.radius)
        if not c.motion:
            p.setPen(QPen(QColor('#a779bc'),1.2));p.drawPath(path);return
        length = path.length()
        if length < 1: return
        for offset in (0, .5):
            head = (c.seconds * 100 / length + offset) % 1
            for step in range(28):
                a = (head - (28-step)*3/length) % 1
                b = (a + 3/length) % 1
                pa = path.pointAtPercent(path.percentAtLength(a*length))
                pb = path.pointAtPercent(path.percentAtLength(b*length))
                alpha = (step/28)**1.7
                for width, strength in ((7,.14),(3,.35),(1.5,.95)):
                    color=QColor('#ffd4a5');color.setAlphaF(alpha*strength)
                    p.setPen(QPen(color,width,Qt.SolidLine,Qt.FlatCap));p.drawLine(pa,pb)
        p.end()

class Lights(QObject):
    def __init__(self, window):
        super().__init__(window)
        self.window=window;self.layers=[];self.seconds=0;self.enabled=True;self.motion=True
        self.timer=QTimer(self);self.timer.setInterval(33);self.timer.timeout.connect(self.tick)
        self.elapsed=QElapsedTimer();window.installEventFilter(self)
    def add(self, target, radius=16):
        layer=BorderLight(target,self,radius);self.layers.append(layer);return layer
    def configure(self, enabled, motion):
        self.enabled,self.motion=enabled,motion
        for layer in self.layers: layer.setVisible(enabled);layer.update()
        self.sync()
    def sync(self):
        active=self.enabled and self.motion and self.window.isVisible() and self.window.isActiveWindow() and not self.window.isMinimized()
        if active and not self.timer.isActive(): self.elapsed.start();self.timer.start()
        elif not active: self.timer.stop()
    def eventFilter(self,obj,event):
        if event.type() in (QEvent.Show,QEvent.Hide,QEvent.WindowActivate,QEvent.WindowDeactivate,QEvent.WindowStateChange):
            QTimer.singleShot(0,self.sync)
        return False
    def tick(self):
        self.seconds += min(self.elapsed.restart()/1000,.1)
        for layer in self.layers:
            if layer.isVisible(): layer.update()

STYLE += '''
QWidget#libraryCanvas {background:#171321;}
QToolButton#libraryCard {background:#251d33;border:1px solid #4b365e;border-radius:14px;padding:10px;color:#eaddf5;font-size:13px;}
QToolButton#libraryCard:hover {background:#3a294c;border-color:#efbc9e;}
QToolButton#libraryCard:focus {border:2px solid #efbc9e;}
QDateEdit {background:#211a30;border:1px solid #4b365e;border-radius:8px;padding:6px;color:#eaddf5;}
'''
