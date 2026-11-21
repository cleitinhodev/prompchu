import sqlite3
"""Full-window paged library. Only visible cards and thumbnails are loaded."""
from PySide6.QtCore import Qt,Signal,QSize,QDate,QTimer,QEvent
from PySide6.QtGui import QPixmap,QIcon,QPainter,QColor,QFont
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QComboBox,QCheckBox,QPushButton,QListWidget,QListWidgetItem,QScrollArea,QGridLayout,QToolButton,QDateEdit,QInputDialog,QDialog,QMessageBox)
from storage import SHELVES
from i18n import tr

class LibraryView(QWidget):
    chosen=Signal(int)
    back=Signal()
    PAGE_SIZE=24
    def __init__(self,store):
        super().__init__();self.store=store;self.offset=0;self.cards=[];self.columns=0
        root=QVBoxLayout(self);root.setContentsMargins(0,0,0,0);root.setSpacing(12)
        top=QHBoxLayout();back=QPushButton('‹  '+tr('Voltar'));back.clicked.connect(self.back);top.addWidget(back)
        title=QLabel(tr('Biblioteca'));title.setObjectName('title');top.addWidget(title,1)
        self.count=QLabel();self.count.setObjectName('muted');top.addWidget(self.count);root.addLayout(top)
        self.query=QLineEdit();self.query.setPlaceholderText(tr('Buscar por nome, texto, tags, gêneros, notas…'));self.query.setClearButtonEnabled(True);root.addWidget(self.query)
        filters=QHBoxLayout()
        self.tags=QLineEdit();self.tags.setPlaceholderText(tr('Tags: separe por vírgula'));filters.addWidget(self.tags,2)
        self.category=QComboBox();filters.addWidget(self.category)
        self.genre=QComboBox();filters.addWidget(self.genre)
        self.favorites=QCheckBox(tr('Favoritos'));filters.addWidget(self.favorites)
        self.sort=QComboBox()
        for name,value in [('Mais recentes','new'),('Mais antigos','old'),('Nome A–Z','name'),('Atualizados','recent')]:self.sort.addItem(tr(name),value)
        filters.addWidget(self.sort);root.addLayout(filters)
        dates=QHBoxLayout();self.date_enabled=QCheckBox(tr('Data de adição'));dates.addWidget(self.date_enabled)
        self.after=QDateEdit(QDate(2000,1,1));self.before=QDateEdit(QDate.currentDate())
        for d in (self.after,self.before):d.setCalendarPopup(True);d.setDisplayFormat('dd/MM/yyyy');d.setEnabled(False)
        dates.addWidget(self.after);dates.addWidget(QLabel('—'));dates.addWidget(self.before)
        clear=QPushButton(tr('Limpar filtros'));clear.clicked.connect(self.clear);dates.addStretch();dates.addWidget(clear);root.addLayout(dates)
        body=QHBoxLayout();self.shelves=QListWidget();self.shelves.setFixedWidth(175);self.shelves.setSpacing(3);sidebar=QVBoxLayout();self.create_shelf_button=QPushButton('+ '+tr('Criar prateleira'));self.create_shelf_button.setFixedWidth(175);self.create_shelf_button.clicked.connect(self.create_shelf);sidebar.addWidget(self.create_shelf_button);sidebar.addWidget(self.shelves,1);body.addLayout(sidebar)
        self.scroll=QScrollArea();self.scroll.setWidgetResizable(True);self.scroll.viewport().installEventFilter(self)
        self.canvas=QWidget();self.canvas.setObjectName("libraryCanvas");self.grid=QGridLayout(self.canvas);self.grid.setSpacing(14);self.grid.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        self.scroll.setWidget(self.canvas);body.addWidget(self.scroll,1);root.addLayout(body,1)
        self.empty=QLabel(tr('Nenhum resultado. Ajuste os filtros ou crie um prompt.'));self.empty.setObjectName('muted');root.addWidget(self.empty)
        paging=QHBoxLayout();self.prev=QPushButton('‹  '+tr('Anterior'));self.next=QPushButton(tr('Próxima')+'  ›');self.page_label=QLabel()
        paging.addWidget(self.prev);paging.addStretch();paging.addWidget(self.page_label);paging.addStretch();paging.addWidget(self.next);root.addLayout(paging)
        self.timer=QTimer(self);self.timer.setSingleShot(True);self.timer.setInterval(200);self.timer.timeout.connect(self.reset)
        self.query.textChanged.connect(lambda:self.timer.start());self.tags.textChanged.connect(lambda:self.timer.start())
        for c in (self.category,self.genre,self.sort):c.currentIndexChanged.connect(self.reset)
        self.shelves.currentRowChanged.connect(self.reset);self.favorites.toggled.connect(self.reset)
        self.date_enabled.toggled.connect(self.dates_changed)
        self.after.dateChanged.connect(self.reset);self.before.dateChanged.connect(self.reset)
        self.prev.clicked.connect(lambda:self.turn(-1));self.next.clicked.connect(lambda:self.turn(1))
        self.refresh_options()
    def create_shelf(self):
        dialog=QInputDialog(self);dialog.setWindowTitle(tr('Criar prateleira'))
        dialog.setLabelText(tr('Nome da prateleira'));dialog.setOkButtonText(tr('Salvar'));dialog.setCancelButtonText(tr('Cancelar'))
        while dialog.exec()==QDialog.Accepted:
            try:name=self.store.add_shelf(dialog.textValue())
            except ValueError as error:
                QMessageBox.warning(self,tr('Criar prateleira'),tr(str(error)));continue
            except sqlite3.Error as error:
                QMessageBox.critical(self,tr('Criar prateleira'),str(error));return
            self.refresh_options()
            for i in range(self.shelves.count()):
                if self.shelves.item(i).data(Qt.UserRole)==name:self.shelves.setCurrentRow(i);break
            self.reset();return
    def dates_changed(self):
        for d in (self.after,self.before):d.setEnabled(self.date_enabled.isChecked())
        self.reset()
    def filters(self):
        shelf=self.shelves.currentItem()
        return dict(query=self.query.text(),tags=self.tags.text(),category=self.category.currentData() or '',genre=self.genre.currentData() or '',shelf=shelf.data(Qt.UserRole) if shelf else '',favorite=self.favorites.isChecked(),sort=self.sort.currentData(),after=self.after.date().toString('yyyy-MM-dd') if self.date_enabled.isChecked() else '',before=self.before.date().toString('yyyy-MM-dd') if self.date_enabled.isChecked() else '')
    def refresh_options(self):
        for box,key,label in [(self.category,'category','Todas as categorias'),(self.genre,'genres','Todos os gêneros')]:
            value=box.currentData();box.blockSignals(True);box.clear();box.addItem(tr(label),'')
            for v in self.store.options(key):box.addItem(v,v)
            box.setCurrentIndex(max(0,box.findData(value)));box.blockSignals(False)
        item=self.shelves.currentItem();old=item.data(Qt.UserRole) if item else ''
        self.shelves.blockSignals(True);self.shelves.clear()
        for label,value in [(tr('Todas as prateleiras'),'')]+[(tr(v) if v in SHELVES else v,v) for v in self.store.shelf_names()]:
            item=QListWidgetItem(label);item.setData(Qt.UserRole,value);self.shelves.addItem(item)
            if value==old:self.shelves.setCurrentItem(item)
        self.shelves.blockSignals(False)
    def clear(self):
        self.query.clear();self.tags.clear();self.category.setCurrentIndex(0);self.genre.setCurrentIndex(0);self.shelves.setCurrentRow(0);self.favorites.setChecked(False);self.date_enabled.setChecked(False);self.sort.setCurrentIndex(0);self.reset()
    def reset(self,*_):self.offset=0;self.refresh()
    def turn(self,direction):self.offset+=direction*self.PAGE_SIZE;self.refresh()
    def refresh(self):
        self.timer.stop()
        rows,total,self.offset=self.store.page(offset=self.offset,limit=self.PAGE_SIZE,**self.filters())
        for card in self.cards:self.grid.removeWidget(card);card.deleteLater()
        self.cards=[]
        for row in rows:
            card=QToolButton();card.setObjectName('libraryCard');card.setToolButtonStyle(Qt.ToolButtonTextUnderIcon);card.setCursor(Qt.PointingHandCursor)
            pix=QPixmap();data=self.store.thumbnail(row['id'])
            if data:pix.loadFromData(data)
            if pix.isNull():
                pix=QPixmap(440,210);pix.fill(QColor('#30223f'));p=QPainter(pix);p.setPen(QColor('#d8b5fa'));p.setFont(QFont('Sans Serif',28,QFont.Bold));p.drawText(pix.rect(),Qt.AlignCenter,tr(row['shelf'] or 'Outros'));p.end()
            card.setIcon(QIcon(pix));card.setIconSize(QSize(220,105));card.setFixedSize(248,235)
            fm=card.fontMetrics()
            title=fm.elidedText(('★ ' if row['favorite'] else '')+row['name'],Qt.ElideRight,224)
            tags=fm.elidedText(row['tags'] or '—',Qt.ElideRight,224)
            card.setText(title+'\n'+tags+'\n'+tr('Adicionado')+': '+row['created'][:10]+'\n'+tr(row['shelf'] or 'Outros'))
            card.setToolTip(row['name']+'\n'+row['tags']);card.setAccessibleName(row['name'])
            card.clicked.connect(lambda checked=False,identifier=row['id']:self.chosen.emit(identifier));self.cards.append(card)
        self.columns=0;self.arrange();self.scroll.verticalScrollBar().setValue(0)
        self.empty.setVisible(not rows);self.count.setText(f'{total} prompts')
        self.page_label.setText(f'{self.offset//self.PAGE_SIZE+1} / {max(1,(total+self.PAGE_SIZE-1)//self.PAGE_SIZE)}')
        self.prev.setEnabled(self.offset>0);self.next.setEnabled(self.offset+len(rows)<total)
    def arrange(self):
        columns=max(1,(self.scroll.viewport().width()-20)//262)
        if self.columns==columns:return
        self.columns=columns
        for card in self.cards:self.grid.removeWidget(card)
        for i,card in enumerate(self.cards):self.grid.addWidget(card,i//columns,i%columns)
        self.canvas.setMinimumSize(columns*262+6,((len(self.cards)+columns-1)//columns)*249+6)
        self.grid.invalidate();self.grid.activate()
    def eventFilter(self,obj,event):
        if event.type()==QEvent.Resize and hasattr(self,'grid'):
            QTimer.singleShot(0,self.arrange)
        return False
    def resizeEvent(self,event):
        super().resizeEvent(event);QTimer.singleShot(0,self.arrange)
