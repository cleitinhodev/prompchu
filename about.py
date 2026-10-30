"""Application identity and explicitly requested official links."""
from pathlib import Path
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QPixmap, QDesktopServices
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QDialogButtonBox
from i18n import tr
from visual import STYLE

LINKS=(('Repositório','https://github.com/cleitinhodev/prompchu'),
       ('Site','https://www.bugzinho.com/'),
       ('Donate','https://www.bugzinho.com/donate'))

class AboutDialog(QDialog):
    def __init__(self,parent,version):
        super().__init__(parent)
        self.setWindowTitle(tr('Sobre')+' · Prompchu')
        self.setStyleSheet(STYLE)
        self.setMinimumWidth(420)
        layout=QVBoxLayout(self);layout.setContentsMargins(30,24,30,24);layout.setSpacing(12)
        logo=QLabel();logo.setAlignment(Qt.AlignCenter)
        pix=QPixmap(str(Path(__file__).parent/'assets/prompchu-corujinha.png'))
        logo.setPixmap(pix.scaled(132,132,Qt.KeepAspectRatio,Qt.SmoothTransformation));layout.addWidget(logo)
        title=QLabel('Prompchu');title.setObjectName('brand');title.setAlignment(Qt.AlignCenter);layout.addWidget(title)
        version_label=QLabel(tr('Versão')+' '+version+' · Owl Studio');version_label.setObjectName('muted');version_label.setAlignment(Qt.AlignCenter);layout.addWidget(version_label)
        info=QLabel(tr('Seu banco de prompts local. Organize ideias, tags e favoritos em um só lugar.'))
        info.setWordWrap(True);info.setAlignment(Qt.AlignCenter);layout.addWidget(info)
        credit=QLabel('Bugzinho · CleitinhoDEV\nPython · PySide6 · SQLite');credit.setObjectName('muted');credit.setAlignment(Qt.AlignCenter);layout.addWidget(credit)
        self.link_buttons={}
        for label,url in LINKS:
            button=QPushButton(tr(label));button.setToolTip(url);button.setCursor(Qt.PointingHandCursor)
            if label=='Donate':button.setObjectName('primary')
            button.clicked.connect(lambda checked=False,target=url:QDesktopServices.openUrl(QUrl(target)))
            layout.addWidget(button);self.link_buttons[url]=button
        buttons=QDialogButtonBox(QDialogButtonBox.Close);buttons.button(QDialogButtonBox.Close).setText(tr('Fechar'));buttons.rejected.connect(self.reject);layout.addWidget(buttons)
