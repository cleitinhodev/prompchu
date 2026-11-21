"""Prompchu — seu banco de prompts local em PySide6."""
import json
import os
import sqlite3
import sys
import unicodedata
from pathlib import Path
from datetime import datetime
from PySide6.QtCore import Qt, QStandardPaths
from PySide6.QtGui import QAction, QKeySequence, QIcon, QPixmap
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QFormLayout, QLineEdit, QPlainTextEdit, QComboBox, QCheckBox,
    QPushButton, QListWidget, QListWidgetItem, QSplitter, QLabel, QMessageBox,
    QFileDialog, QDialog, QDialogButtonBox, QFrame, QTabWidget, QMenu, QScrollArea, QStackedWidget)

from about import AboutDialog
from wordmark import Wordmark
from i18n import tr, LANGUAGES
from visual import STYLE as OWL_STYLE, preferences, Lights

APP_NAME = 'Prompchu'
VERSION = '1.3.0-beta.1'
ASSETS = Path(__file__).resolve().parent / 'assets'

from storage import Store, FIELDS, SHELVES, fold, terms, validate
from thumbnails import load_thumbnail, normalize_image
from library_view import LibraryView
import base64

class Editor(QDialog):
    def __init__(self, parent, data=None):
        super().__init__(parent)
        self.setWindowTitle(tr('Editar prompt') if data else tr('Novo prompt'))
        self.resize(800, 680)
        self.setMinimumSize(620, 480)
        self.setStyleSheet(OWL_STYLE)
        outer = QVBoxLayout(self)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        body = QWidget(); form = QFormLayout(body)
        form.setSpacing(12)
        scroll.setWidget(body)
        self.inputs = {}
        labels = {'name':tr('Nome *'), 'tags':tr('Tags (separadas por vírgula)'), 'genres':tr('Gêneros (separados por vírgula)'), 'category':tr('Categoria'), 'model':tr('Modelo / ferramenta'), 'prompt':'Prompt *', 'negative':tr('Prompt negativo'), 'notes':tr('Notas'), 'favorite':tr('Favorito'), 'shelf':tr('Prateleira')}
        for key in FIELDS:
            if key == 'shelf':
                field=QComboBox();field.setEditable(True)
                field.addItems([tr(v) for v in SHELVES])
                for i,v in enumerate(SHELVES):field.setItemData(i,v)
                value=(data or {}).get('shelf') or 'Outros'
                index=field.findData(value)
                if index>=0:field.setCurrentIndex(index)
                else:field.setEditText(value)
            elif key == 'favorite':
                field = QCheckBox(tr('Marcar como favorito'))
                field.setChecked(bool((data or {}).get(key, False)))
            elif key in ('prompt', 'negative', 'notes'):
                field = QPlainTextEdit()
                field.setPlainText((data or {}).get(key, ''))
                field.setMinimumHeight(150 if key == 'prompt' else 65)
            else:
                field = QLineEdit((data or {}).get(key, ''))
            self.inputs[key] = field
            form.addRow(tr(labels[key]), field)
        self.inputs['category'].setPlaceholderText('Imagem, Texto, Vídeo, Código…')
        self.inputs['genres'].setPlaceholderText('Fantasia, Romance, Ficção científica…')
        self.thumbnail=parent.store.thumbnail(data['id']) if data and data.get('id') else None
        self.thumb_preview=QLabel();self.thumb_preview.setFixedHeight(88)
        self.update_thumbnail()
        thumb_actions=QHBoxLayout()
        upload=QPushButton(tr('Escolher miniatura'));upload.clicked.connect(self.choose_thumbnail)
        remove=QPushButton(tr('Remover miniatura'));remove.clicked.connect(self.remove_thumbnail)
        thumb_actions.addWidget(upload);thumb_actions.addWidget(remove)
        form.addRow(tr('Miniatura JPG / PNG'),self.thumb_preview);form.addRow(thumb_actions)
        outer.addWidget(scroll, 1)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setText(tr('Salvar'))
        buttons.button(QDialogButtonBox.Save).setObjectName('primary')
        buttons.button(QDialogButtonBox.Cancel).setText(tr('Cancelar'))
        buttons.accepted.connect(self.check)
        buttons.rejected.connect(self.reject)
        outer.addWidget(buttons)
    def update_thumbnail(self):
        self.thumb_preview.clear()
        if self.thumbnail:
            pix=QPixmap();pix.loadFromData(self.thumbnail)
            self.thumb_preview.setPixmap(pix.scaled(180,88,Qt.KeepAspectRatio,Qt.SmoothTransformation))
        else:self.thumb_preview.setText(tr('Sem miniatura'))
    def choose_thumbnail(self):
        path,_=QFileDialog.getOpenFileName(self,tr('Escolher miniatura'),'','Imagens (*.jpg *.jpeg *.png)')
        if path:
            try:self.thumbnail=load_thumbnail(path);self.update_thumbnail()
            except (ValueError,OSError) as e:QMessageBox.warning(self,tr('Miniatura'),str(e))
    def remove_thumbnail(self):self.thumbnail=None;self.update_thumbnail()
    def values(self):
        return {k: (w.isChecked() if k == 'favorite' else (w.currentData() if w.currentIndex()>=0 and w.currentText()==w.itemText(w.currentIndex()) else w.currentText()) if isinstance(w,QComboBox) else w.toPlainText() if isinstance(w, QPlainTextEdit) else w.text()) for k,w in self.inputs.items()}
    def check(self):
        try:
            validate(self.values())
        except ValueError as e:
            QMessageBox.warning(self, 'Confira os campos', str(e))
            return
        self.accept()

class Window(QMainWindow):
    def __init__(self, path):
        super().__init__()
        self.store = Store(path)
        self.database_path = path
        self.offset=0
        self.page_size=100
        self.setStyleSheet(OWL_STYLE)
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(str(ASSETS / 'prompchu-cabeca.ico')))
        self.resize(1280, 820)
        self.setMinimumSize(940, 640)
        root = QWidget(); root.setObjectName('canvas')
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(22, 18, 22, 10); layout.setSpacing(16)
        header = QFrame(); header.setObjectName('header')
        brand = QHBoxLayout(header); brand.setContentsMargins(20, 14, 20, 14)
        logo = QLabel()
        logo.setPixmap(QPixmap(str(ASSETS / 'prompchu-corujinha.png')).scaled(76,76,Qt.KeepAspectRatio,Qt.SmoothTransformation))
        brand.addWidget(logo)
        titles = QVBoxLayout()
        heading = Wordmark(self); self.wordmark=heading
        subtitle = QLabel(tr('Seu próximo resultado começa com uma boa ideia.')); subtitle.setObjectName('muted')
        titles.addWidget(heading);titles.addWidget(subtitle);brand.addLayout(titles,1)
        self.new_button = QPushButton('+  '+tr('Novo prompt'));self.new_button.setObjectName('primary')
        self.new_button.clicked.connect(self.new);brand.addWidget(self.new_button)
        menu_button=QPushButton(tr('Arquivo'))
        menu=QMenu(menu_button)
        for label, callback in [('Importar JSON',self.import_json),('Exportar JSON',self.export_json),('Backup do banco',self.backup),('Abrir demonstração',self.open_demo)]:
            menu.addAction(tr(label),callback)
        menu_button.setMenu(menu);brand.addWidget(menu_button)
        self.library_button=QPushButton(tr('Biblioteca'));self.library_button.clicked.connect(self.show_library);brand.addWidget(self.library_button)
        about_button=QPushButton(tr('Sobre'));about_button.clicked.connect(self.show_about);brand.addWidget(about_button)
        layout.addWidget(header)
        settings=preferences()
        self.pages=QStackedWidget();layout.addWidget(self.pages,1)
        self.home=QWidget();self.pages.addWidget(self.home)
        home_layout=QVBoxLayout(self.home);home_layout.setContentsMargins(0,0,0,0);home_layout.setSpacing(14)
        controls=QHBoxLayout()
        self.search=QLineEdit();self.search.setClearButtonEnabled(True)
        self.search.setPlaceholderText(tr('Buscar por nome, texto, tags, gêneros, notas…')+'  ·  Ctrl+F')
        controls.addWidget(self.search,1)
        self.language=QComboBox()
        for code,name in LANGUAGES.items(): self.language.addItem(name,code)
        self.language.setCurrentIndex(max(0,self.language.findData(settings.value('language','pt'))))
        self.language.setToolTip(tr('Idioma'));controls.addWidget(self.language)
        self.neon=QCheckBox(tr('Neon'));self.motion=QCheckBox(tr('Animações'))
        self.neon.setChecked(settings.value('neon',True,type=bool));self.motion.setChecked(settings.value('motion',True,type=bool))
        controls.addWidget(self.neon);controls.addWidget(self.motion);home_layout.addLayout(controls)
        split=QSplitter();split.setHandleWidth(14);self.split=split
        library=QFrame();library.setObjectName('card')
        left=QVBoxLayout(library);left.setContentsMargins(16,18,16,16);left.setSpacing(12)
        self.collection=QLabel(tr('Biblioteca'));self.collection.setObjectName('section');left.addWidget(self.collection)
        self.favorites=QCheckBox('★  '+tr('Favoritos'));left.addWidget(self.favorites)
        self.category=QComboBox();self.genre=QComboBox();self.tag=QComboBox()
        for box,label in [(self.category,'Categoria'),(self.genre,'Gêneros'),(self.tag,'Tags')]:
            box.setToolTip(tr(label));left.addWidget(box);box.currentIndexChanged.connect(self.refresh)
        clear=QPushButton(tr('Limpar filtros'));clear.clicked.connect(self.clear_filters);left.addWidget(clear)
        self.items=QListWidget();self.items.setWordWrap(True)
        self.items.currentItemChanged.connect(self.detail);self.items.itemDoubleClicked.connect(self.edit)
        left.addWidget(self.items,1)
        self.empty=QLabel(tr('Nenhum resultado. Ajuste os filtros ou crie um prompt.'))
        self.empty.setWordWrap(True);self.empty.setObjectName('muted');left.addWidget(self.empty)
        pager=QHBoxLayout();self.prev_page=QPushButton('‹');self.next_page=QPushButton('›');self.page_label=QLabel()
        self.prev_page.setToolTip(tr('Anterior'));self.next_page.setToolTip(tr('Próxima'))
        self.prev_page.clicked.connect(lambda:self.turn_page(-1));self.next_page.clicked.connect(lambda:self.turn_page(1))
        pager.addWidget(self.prev_page);pager.addWidget(self.page_label,1);pager.addWidget(self.next_page);left.addLayout(pager)
        split.addWidget(library)
        panel=QFrame();panel.setObjectName('card')
        right=QVBoxLayout(panel);right.setContentsMargins(22,20,22,20);right.setSpacing(12)
        eyebrow=QLabel(tr('ESPAÇO DE CRIAÇÃO'));eyebrow.setObjectName('section');right.addWidget(eyebrow)
        self.title=QLabel();self.title.setObjectName('title');self.title.setWordWrap(True);right.addWidget(self.title)
        self.meta=QLabel();self.meta.setObjectName('muted');self.meta.setWordWrap(True);right.addWidget(self.meta)
        self.chips=QLabel();self.chips.setWordWrap(True);self.chips.setObjectName('chip');right.addWidget(self.chips)
        self.tabs=QTabWidget()
        self.prompt=QPlainTextEdit();self.prompt.setReadOnly(True)
        self.negative=QPlainTextEdit();self.negative.setReadOnly(True)
        self.notes=QPlainTextEdit();self.notes.setReadOnly(True)
        self.extra=QPlainTextEdit();self.extra.setReadOnly(True);self.extra.hide()
        self.tabs.addTab(self.prompt,'Prompt');self.tabs.addTab(self.negative,tr('Prompt negativo'));self.tabs.addTab(self.notes,tr('Notas'))
        right.addWidget(self.tabs,1)
        self.word_count=QLabel();self.word_count.setObjectName('muted');right.addWidget(self.word_count)
        actions=QHBoxLayout();self.selection_buttons=[]
        for label,callback,style in [('Copiar prompt',self.copy,'primary'),('Editar',self.edit,''),('Duplicar',self.duplicate,''),('Alternar favorito',self.favorite,''),('Excluir',self.delete,'danger')]:
            button=QPushButton(tr(label));button.setObjectName(style);button.clicked.connect(callback)
            actions.addWidget(button);self.selection_buttons.append(button)
        right.addLayout(actions)
        split.addWidget(panel);split.setSizes([340,880]);split.setStretchFactor(1,1)
        home_layout.addWidget(split,1)
        self.library=LibraryView(self.store);self.pages.addWidget(self.library)
        self.library.chosen.connect(self.open_prompt);self.library.back.connect(lambda:self.pages.setCurrentWidget(self.home))
        self.lights=Lights(self);self.lights.add(header,18);self.lights.add(self.new_button,9)
        self.panel_light=self.lights.add(panel,16)
        QApplication.instance().focusChanged.connect(self.focus_light)
        self.neon.toggled.connect(self.effects);self.motion.toggled.connect(self.effects)
        self.language.currentIndexChanged.connect(self.change_language)
        self.search.textChanged.connect(self.refresh);self.favorites.toggled.connect(self.refresh)
        for shortcut,callback in [('Ctrl+N',self.new),('Ctrl+E',self.edit),('Ctrl+F',self.focus_search),('Ctrl+Shift+C',self.copy)]:
            action=QAction(self);action.setShortcut(QKeySequence(shortcut));action.triggered.connect(callback);self.addAction(action)
        self.effects();self.reload()
        geometry=settings.value('geometry')
        if geometry is not None: self.restoreGeometry(geometry)
        splitter_state=settings.value('splitter')
        if splitter_state is not None: self.split.restoreState(splitter_state)
        self.statusBar().setToolTip(str(self.database_path))

    def focus_search(self):
        (self.library.query if self.pages.currentWidget() is self.library else self.search).setFocus()
    def show_library(self):
        self.library.refresh_options();self.library.refresh();self.pages.setCurrentWidget(self.library)
    def open_prompt(self,identifier):
        self.clear_filters();self.refresh(select=identifier)
        self.pages.setCurrentWidget(self.home);self.tabs.setCurrentIndex(0)
    def turn_page(self,direction):
        self.offset+=direction*self.page_size;self.refresh(keep_page=True)
    def open_demo(self):
        import tempfile
        folder=tempfile.TemporaryDirectory(prefix='prompchu-demo-')
        window=Window(Path(folder.name)/'demo.sqlite3');window.demo_folder=folder
        rows=json.loads((ASSETS/'demo-prompts.json').read_text(encoding='utf-8'))['prompts']
        with window.store.db:
            for row in rows:
                identifier=window.store.save(row)
                window.store.db.execute('UPDATE prompts SET created=?,updated=? WHERE id=?',(row['created'],row['updated'],identifier))
        window.setWindowTitle(APP_NAME+' · '+tr('Demonstração'))
        window.reload();window.show_library();window.show()
        if not hasattr(self,'demo_windows'):self.demo_windows=[]
        self.demo_windows.append(window)
    def show_about(self):
        AboutDialog(self, VERSION).exec()

    def clear_filters(self):
        self.search.clear();self.favorites.setChecked(False)
        for box in (self.category,self.genre,self.tag): box.setCurrentIndex(0)

    def focus_light(self, old, new):
        if hasattr(self,'panel_light'):
            target=self.panel_light.target
            self.panel_light.setVisible(self.neon.isChecked() and new is not None and (new is target or target.isAncestorOf(new)))

    def effects(self):
        settings=preferences()
        settings.setValue('neon',self.neon.isChecked());settings.setValue('motion',self.motion.isChecked())
        self.lights.configure(self.neon.isChecked(),self.motion.isChecked())
        self.wordmark.configure(self.neon.isChecked(),self.motion.isChecked())
        self.focus_light(None,QApplication.focusWidget())

    def change_language(self):
        preferences().setValue('language', self.language.currentData())
        replacement = Window(self.database_path)
        if hasattr(self,'demo_folder'):
            replacement.demo_folder=self.demo_folder
            replacement.setWindowTitle(self.windowTitle())
        replacement.setGeometry(self.geometry())
        for source,target in [(self.category,replacement.category),(self.genre,replacement.genre),(self.tag,replacement.tag)]:
            target.setCurrentIndex(max(0,target.findData(source.currentData())))
        replacement.search.setText(self.search.text())
        replacement.favorites.setChecked(self.favorites.isChecked())
        row=self.selected()
        replacement.refresh(select=row['id'] if row else None)
        replacement.tabs.setCurrentIndex(self.tabs.currentIndex())
        replacement.split.restoreState(self.split.saveState())
        QApplication.instance().prompchu_window = replacement
        replacement.show()
        self.close()

    def selected(self):
        item=self.items.currentItem()
        return self.store.get(item.data(Qt.UserRole)['id']) if item else None
    def reload(self, select=None):
        for box,key,label in [(self.category,'category','Todas as categorias'),(self.genre,'genres','Todos os gêneros'),(self.tag,'tags','Todas as tags')]:
            old=box.currentData();box.blockSignals(True);box.clear();box.addItem(tr(label),None)
            for option in self.store.options(key):box.addItem(option,option)
            box.setCurrentIndex(max(0,box.findData(old)));box.blockSignals(False)
        self.refresh(select=select,keep_page=True)
        self.library.refresh_options()
    def home_filters(self):
        return dict(query=self.search.text(),category=self.category.currentData() or '',genre=self.genre.currentData() or '',tags=self.tag.currentData() or '',favorite=self.favorites.isChecked())
    def refresh(self,*_args,select=None,keep_page=False):
        current=self.selected();identifier=select if select is not None else current['id'] if current else None
        if not keep_page:self.offset=0
        filters=self.home_filters()
        if select is not None:self.offset=self.store.offset_for(select,self.page_size,**filters)
        rows,total,self.offset=self.store.page(offset=self.offset,limit=self.page_size,**filters)
        self.items.blockSignals(True);self.items.clear()
        for row in rows:
            item=QListWidgetItem(('★ ' if row['favorite'] else '')+row['name']+'\n'+(row['category'] or tr('Sem categoria'))+(' · '+row['tags'] if row['tags'] else ''))
            item.setData(Qt.UserRole,row);self.items.addItem(item)
            if row['id']==identifier:self.items.setCurrentItem(item)
        if not self.items.currentItem() and self.items.count():self.items.setCurrentRow(0)
        self.items.blockSignals(False);self.detail()
        self.collection.setText(tr('Biblioteca')+f' · {total}')
        self.empty.setVisible(not rows)
        self.page_label.setText(f'{self.offset//self.page_size+1} / {max(1,(total+self.page_size-1)//self.page_size)}')
        self.prev_page.setEnabled(self.offset>0);self.next_page.setEnabled(self.offset+len(rows)<total)
        self.statusBar().showMessage(tr('Salvo neste computador')+' · Ctrl+N / Ctrl+E / Ctrl+Shift+C')
    def detail(self, *_):
        row = self.selected()
        self.title.setText(row['name'] if row else tr('Selecione um prompt ou clique em Novo'))
        self.title.setTextFormat(Qt.PlainText)
        self.meta.setTextFormat(Qt.PlainText)
        self.meta.setText((row['category'] or tr('Sem categoria')) + ('  ·  '+row['model'] if row['model'] else '') + '  ·  '+row['updated'].replace('T',' ') if row else tr('Selecione um prompt ou clique em Novo'))
        self.chips.setTextFormat(Qt.PlainText)
        self.chips.setText('   ·   '.join(terms(row['tags']) + terms(row['genres'])) if row else '')
        self.chips.setVisible(bool(self.chips.text()))
        self.prompt.setPlainText(row['prompt'] if row else '')
        self.negative.setPlainText(row['negative'] if row else '')
        self.notes.setPlainText(row['notes'] if row else '')
        self.extra.setPlainText((row['negative']+'\n'+row['notes']) if row else '')
        text=row['prompt'] if row else ''
        self.word_count.setText(f"{len(text):,} " + tr('caracteres') + '  ·  ' + f"{len(text.split()):,} " + tr('palavras'))
        for button in self.selection_buttons: button.setEnabled(row is not None)
        self.selection_buttons[3].setText(('★  ' if row and row['favorite'] else '☆  ') + tr('Favorito'))

    def editor(self, row=None, duplicate=False):
        dialog = Editor(self, row)
        if dialog.exec() == QDialog.Accepted:
            try:
                with self.store.db:
                    identifier = self.store.save(dialog.values(), None if duplicate or not row else row['id'])
                    self.store.set_thumbnail(identifier,dialog.thumbnail)
                self.reload(identifier)
                self.open_prompt(identifier)
            except (sqlite3.Error, ValueError) as e:
                QMessageBox.critical(self, 'Erro ao salvar', str(e))
    def new(self): self.editor()
    def edit(self, *_):
        if self.selected(): self.editor(self.selected())
    def duplicate(self):
        if self.selected():
            row = dict(self.selected())
            row['name'] += ' (cópia)'
            self.editor(row, True)
    def delete(self):
        row = self.selected()
        if row and QMessageBox.question(self, 'Excluir prompt', f'Excluir “{row["name"]}”?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            with self.store.db:
                self.store.db.execute('DELETE FROM prompts WHERE id=?', (row['id'],))
            self.reload()
    def favorite(self):
        row = self.selected()
        if row:
            row['favorite'] = not bool(row['favorite'])
            with self.store.db: self.store.save(row, row['id'])
            self.reload(row['id'])
    def copy(self):
        if self.selected():
            QApplication.clipboard().setText(self.selected()['prompt'])
            self.statusBar().showMessage(tr('Prompt copiado!'), 3000)
    def export_json(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Exportar todos os prompts', 'prompts.json', 'JSON (*.json)')
        if path:
            try:
                rows = [{k: bool(r[k]) if k == 'favorite' else r[k] for k in FIELDS} for r in self.store.all()]
                for data,row in zip(rows,self.store.all()):
                    image=self.store.thumbnail(row['id'])
                    if image:data['thumbnail_png']=base64.b64encode(image).decode('ascii')
                Path(path).write_text(json.dumps({'format':'banco-de-prompts', 'version':2, 'prompts':rows}, ensure_ascii=False, indent=2), encoding='utf-8')
                QMessageBox.information(self, 'Exportado', f'{len(rows)} prompts exportados.')
            except OSError as e: QMessageBox.critical(self, 'Erro', str(e))
    def import_json(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Importar prompts', '', 'JSON (*.json)')
        if not path: return
        try:
            if Path(path).stat().st_size > 25*1024*1024:
                raise ValueError('O arquivo excede 25 MB.')
            content = json.loads(Path(path).read_text(encoding='utf-8-sig'))
            if isinstance(content, dict):
                if content.get('format') != 'banco-de-prompts' or content.get('version') not in (1,2):
                    raise ValueError('Formato ou versão desconhecidos.')
                content = content.get('prompts')
            if not isinstance(content, list): raise ValueError('Esperada uma lista de prompts.')
            rows = [validate(row) for row in content]
            images=[]
            for row in content:
                raw=row.get('thumbnail_png')
                if raw is not None and not isinstance(raw,str):raise ValueError('Miniatura inválida.')
                images.append(normalize_image(base64.b64decode(raw,validate=True)) if raw else None)
            if QMessageBox.question(self, 'Importar', f'Adicionar {len(rows)} prompts? Os atuais serão mantidos. Reimportações criam cópias.', QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes: return
            with self.store.db:
                for row,image in zip(rows,images):
                    identifier=self.store.save(row)
                    self.store.set_thumbnail(identifier,image)
            self.reload()
            QMessageBox.information(self, 'Importado', f'{len(rows)} prompts adicionados.')
        except (OSError, ValueError, sqlite3.Error) as e:
            QMessageBox.critical(self, 'Importação cancelada', str(e))
    def backup(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Backup completo', 'prompts-backup.sqlite3', 'SQLite (*.sqlite3)')
        if path:
            try:
                if Path(path).resolve() == Path(self.database_path).resolve(): raise ValueError('Escolha um arquivo diferente do banco em uso.')
                with sqlite3.connect(path) as target: self.store.db.backup(target)
                QMessageBox.information(self, 'Backup concluído', 'Cópia completa do banco salva.')
            except (OSError, ValueError, sqlite3.Error) as e: QMessageBox.critical(self, 'Erro', str(e))
    def closeEvent(self, event):
        preferences().setValue('geometry',self.saveGeometry())
        preferences().setValue('splitter',self.split.saveState())
        self.library.timer.stop()
        self.wordmark.reset()
        self.lights.timer.stop()
        QApplication.instance().focusChanged.disconnect(self.focus_light)
        self.store.db.close()
        event.accept()

def data_path():
    override = os.environ.get('BANCO_PROMPTS_DIR')
    folder = Path(override) if override else Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation))
    folder.mkdir(parents=True, exist_ok=True)
    return folder / 'prompts.sqlite3'

DB_PATH = Path('prompts.sqlite3')
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Identificador de armazenamento estável: preserva o banco da versão anterior.
    app.setApplicationName('BancoDePrompts')
    app.setApplicationDisplayName(APP_NAME)
    app.setApplicationVersion(VERSION)
    app.setWindowIcon(QIcon(str(ASSETS / 'prompchu-cabeca.ico')))
    app.setOrganizationName('Bugzinho')
    app.setStyle('Fusion')
    app.setStyleSheet(OWL_STYLE)
    try:
        if '--smoke-test' in sys.argv:
            import tempfile
            from PySide6.QtCore import QTimer
            smoke_folder = tempfile.TemporaryDirectory()
            DB_PATH = Path(smoke_folder.name) / 'smoke.sqlite3'
        else:
            DB_PATH = data_path()
        window = Window(DB_PATH)
        window.show()
        if '--smoke-test' in sys.argv:
            QTimer.singleShot(500, window.close)
        sys.exit(app.exec())
    except (OSError, sqlite3.Error) as error:
        QMessageBox.critical(None, 'Não foi possível abrir o banco', str(error))
        sys.exit(1)
