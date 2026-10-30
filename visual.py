"""Owl theme and persistent appearance preferences."""
from PySide6.QtCore import QSettings, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect

STYLE = '''
QWidget {background:#151020;color:#f4eaff;font-family:"Segoe UI";font-size:13px;}
QMainWindow {background:#151020;}
QLabel {background:transparent;}
QLineEdit,QPlainTextEdit,QListWidget,QComboBox {background:#21182f;border:1px solid #453257;border-radius:12px;padding:12px;selection-background-color:#7041aa;}
QLineEdit:focus,QPlainTextEdit:focus,QComboBox:focus {border:1px solid #c292ff;}
QPushButton {background:#322242;border:1px solid #634383;border-radius:10px;padding:11px 16px;font-weight:600;}
QPushButton:hover {background:#50316d;border-color:#c292ff;}
QPushButton:pressed {background:#7041aa;}
QPushButton#primary {background:#ffab89;color:#24152e;border:0;font-weight:700;}
QPushButton#primary:hover {background:#ffd19e;}
QListWidget::item {padding:17px;border-bottom:1px solid #362544; margin:3px;border-radius:9px;}
QListWidget::item:selected {background:#513071;color:#fff1db;}
QListWidget::item:hover {background:#30203f;}
QCheckBox {spacing:8px;padding:5px;color:#e8ccff;}
QCheckBox::indicator {width:17px;height:17px;border:1px solid #8963ad;border-radius:5px;background:#21182f;}
QCheckBox::indicator:checked {background:#ba83ee;border:2px solid #ffd19e;}
QSplitter::handle {background:#453257;width:3px;}
QStatusBar {color:#bba4d0;font-size:11px;}
QScrollBar:vertical {background:#21182f;width:10px;}
QScrollBar::handle:vertical {background:#775092;border-radius:5px;min-height:30px;}
QToolTip {background:#322242;color:#fff1db;border:1px solid #ba83ee;}
'''

def preferences():
    return QSettings('Bugzinho','PrompchuAppearance')

def glow(widget, enabled):
    effect = QGraphicsDropShadowEffect(widget)
    effect.setOffset(0,0)
    effect.setBlurRadius(26)
    effect.setColor(QColor('#b16aff'))
    effect.setEnabled(enabled)
    widget.setGraphicsEffect(effect)
    return effect

def animate(window):
    if not window.motion.isChecked(): return
    window.animation.stop()
    window.animation.setStartValue(8.0)
    window.animation.setEndValue(26.0)
    window.animation.start()
