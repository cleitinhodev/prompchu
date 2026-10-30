"""Bundled Fredoka wordmark with infrequent, per-letter neon faults."""
import random
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QEvent, QSize
from PySide6.QtGui import QFont, QFontDatabase, QFontMetricsF, QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

class Wordmark(QWidget):
    _family = None
    def __init__(self, parent=None):
        super().__init__(parent)
        if Wordmark._family is None:
            font_id=QFontDatabase.addApplicationFont(str(Path(__file__).parent/'assets/fonts/Fredoka.ttf'))
            families=QFontDatabase.applicationFontFamilies(font_id)
            Wordmark._family=families[0] if families else 'Segoe UI'
        self.face=QFont(Wordmark._family);self.face.setPixelSize(38);self.face.setWeight(QFont.DemiBold)
        self.text='Prompchu';self.rng=random.Random();self.dim_letter=None
        self.enabled=True;self.neon=True;self.phase=0
        self.timer=QTimer(self);self.timer.setSingleShot(True);self.timer.timeout.connect(self.step)
        self.setAccessibleName('Prompchu');self.setMinimumSize(self.sizeHint())
        self.window().installEventFilter(self)
    def sizeHint(self):
        fm=QFontMetricsF(self.face)
        return QSize(int(fm.horizontalAdvance(self.text))+20,58)
    def configure(self, neon, motion):
        self.neon=neon;self.enabled=motion
        self.reset();self.sync()
    def reset(self):
        self.timer.stop();self.dim_letter=None;self.phase=0;self.update()
    def sync(self):
        w=self.window()
        if self.enabled and self.neon and w.isVisible() and w.isActiveWindow() and not w.isMinimized():
            if not self.timer.isActive():self.timer.start(self.rng.randint(2400,6500))
        else:self.reset()
    def eventFilter(self,obj,event):
        if event.type() in (QEvent.Show,QEvent.Hide,QEvent.WindowActivate,QEvent.WindowDeactivate,QEvent.WindowStateChange):
            QTimer.singleShot(0,self.sync)
        return False
    def step(self):
        # One letter drops out, briefly recovers, drops again, then stays lit.
        if self.phase==0:
            self.fault=self.rng.randrange(len(self.text));self.dim_letter=self.fault;self.phase=1;delay=180
        elif self.phase==1:self.dim_letter=None;self.phase=2;delay=240
        elif self.phase==2:self.dim_letter=self.fault;self.phase=3;delay=130
        else:self.dim_letter=None;self.phase=0;delay=self.rng.randint(2400,6500)
        self.update();self.timer.start(delay)
    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing)
        fm=QFontMetricsF(self.face);x=8;baseline=(self.height()-fm.height())/2+fm.ascent()
        for i,char in enumerate(self.text):
            path=QPainterPath();path.addText(x,baseline,self.face,char)
            dim=i==self.dim_letter
            if self.neon and not dim:
                for width,alpha in ((7,18),(3,35)):
                    c=QColor('#f3af9f');c.setAlpha(alpha)
                    p.setPen(QPen(c,width));p.setBrush(Qt.NoBrush);p.drawPath(path)
            p.setPen(Qt.NoPen);p.setBrush(QColor('#80627c' if dim else '#ffe0b3'));p.drawPath(path)
            x+=fm.horizontalAdvance(char)
        p.end()
