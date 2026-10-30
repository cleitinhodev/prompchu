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
    QFileDialog, QDialog, QDialogButtonBox, QFrame, QTabWidget, QMenu, QScrollArea)

from i18n import tr, LANGUAGES
from visual import STYLE as OWL_STYLE, preferences, Lights

APP_NAME = 'Prompchu'
VERSION = '1.2.0-preview'
ASSETS = Path(__file__).resolve().parent / 'assets'

FIELDS = ('name', 'tags', 'genres', 'category', 'model', 'prompt', 'negative', 'notes', 'favorite')

def fold(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text.casefold()) if unicodedata.category(c) != 'Mn')

def terms(text):
    return list(dict.fromkeys(t.strip() for t in text.split(',') if t.strip()))

def validate(data):
    if not isinstance(data, dict):
        raise ValueError('Cada prompt precisa ser um objeto JSON.')
    result = {}
    for key in FIELDS:
        value = data.get(key, False if key == 'favorite' else '')
        if key == 'favorite':
            if type(value) is not bool:
                raise ValueError('favorite precisa ser true ou false.')
        elif not isinstance(value, str):
            raise ValueError(f'O campo {key} precisa ser texto.')
        result[key] = value
    if not result['name'].strip() or not result['prompt'].strip():
        raise ValueError('Nome e prompt são obrigatórios.')
    result['name'] = result['name'].strip()
    for key in ('tags', 'genres'):
        result[key] = ', '.join(terms(result[key]))
    return result

class Store:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.execute('''CREATE TABLE IF NOT EXISTS prompts (
            id INTEGER PRIMARY KEY, name TEXT NOT NULL, tags TEXT NOT NULL,
            genres TEXT NOT NULL, category TEXT NOT NULL, model TEXT NOT NULL,
            prompt TEXT NOT NULL, negative TEXT NOT NULL, notes TEXT NOT NULL,
            favorite INTEGER NOT NULL DEFAULT 0, created TEXT NOT NULL, updated TEXT NOT NULL)''')
        self.db.commit()
    def all(self):
        return [dict(r) for r in self.db.execute('SELECT * FROM prompts ORDER BY favorite DESC, updated DESC, id DESC')]
    def save(self, data, identifier=None):
        data = validate(data)
        now = datetime.now().isoformat(timespec='seconds')
        values = [data[k] for k in FIELDS]
        if identifier is None:
            cur = self.db.execute('INSERT INTO prompts (' + ','.join(FIELDS) + ',created,updated) VALUES (' + ','.join('?' for _ in range(11)) + ')', values + [now, now])
            return cur.lastrowid
        self.db.execute('UPDATE prompts SET ' + ','.join(k+'=?' for k in FIELDS) + ',updated=? WHERE id=?', values+[now, identifier])
        return identifier

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
        labels = {'name':tr('Nome *'), 'tags':tr('Tags (separadas por vírgula)'), 'genres':tr('Gêneros (separados por vírgula)'), 'category':tr('Categoria'), 'model':tr('Modelo / ferramenta'), 'prompt':'Prompt *', 'negative':tr('Prompt negativo'), 'notes':tr('Notas'), 'favorite':tr('Favorito')}
        for key in FIELDS:
            if key == 'favorite':
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
        outer.addWidget(scroll, 1)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setText(tr('Salvar'))
        buttons.button(QDialogButtonBox.Save).setObjectName('primary')
        buttons.button(QDialogButtonBox.Cancel).setText(tr('Cancelar'))
        buttons.accepted.connect(self.check)
        buttons.rejected.connect(self.reject)
        outer.addWidget(buttons)
    def values(self):
        return {k: (w.isChecked() if k == 'favorite' else w.toPlainText() if isinstance(w, QPlainTextEdit) else w.text()) for k,w in self.inputs.items()}
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
        heading = QLabel('Prompchu'); heading.setObjectName('brand')
        subtitle = QLabel(tr('Seu próximo resultado começa com uma boa ideia.')); subtitle.setObjectName('muted')
        titles.addWidget(heading);titles.addWidget(subtitle);brand.addLayout(titles,1)
        self.new_button = QPushButton('+  '+tr('Novo prompt'));self.new_button.setObjectName('primary')
        self.new_button.clicked.connect(self.new);brand.addWidget(self.new_button)
        menu_button=QPushButton(tr('Biblioteca'))
        menu=QMenu(menu_button)
        for label, callback in [('Importar JSON',self.import_json),('Exportar JSON',self.export_json),('Backup do banco',self.backup)]:
            menu.addAction(tr(label),callback)
        menu_button.setMenu(menu);brand.addWidget(menu_button)
        layout.addWidget(header)
        settings=preferences()
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
        controls.addWidget(self.neon);controls.addWidget(self.motion);layout.addLayout(controls)
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
        layout.addWidget(split,1)
        self.lights=Lights(self);self.lights.add(header,18);self.lights.add(self.new_button,9)
        self.panel_light=self.lights.add(panel,16)
        QApplication.instance().focusChanged.connect(self.focus_light)
        self.neon.toggled.connect(self.effects);self.motion.toggled.connect(self.effects)
        self.language.currentIndexChanged.connect(self.change_language)
        self.search.textChanged.connect(self.refresh);self.favorites.toggled.connect(self.refresh)
        for shortcut,callback in [('Ctrl+N',self.new),('Ctrl+E',self.edit),('Ctrl+F',self.search.setFocus),('Ctrl+Shift+C',self.copy)]:
            action=QAction(self);action.setShortcut(QKeySequence(shortcut));action.triggered.connect(callback);self.addAction(action)
        self.effects();self.reload()
        geometry=settings.value('geometry')
        if geometry is not None: self.restoreGeometry(geometry)
        splitter_state=settings.value('splitter')
        if splitter_state is not None: self.split.restoreState(splitter_state)
        self.statusBar().setToolTip(str(self.database_path))

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
        self.focus_light(None,QApplication.focusWidget())

    def change_language(self):
        preferences().setValue('language', self.language.currentData())
        replacement = Window(self.database_path)
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
        item = self.items.currentItem()
        return item.data(Qt.UserRole) if item else None
    def reload(self, select=None):
        self.rows = self.store.all()
        for box, key, label in [(self.category,'category',tr('Todas as categorias')), (self.genre,'genres',tr('Todos os gêneros')), (self.tag,'tags',tr('Todas as tags'))]:
            old = box.currentData()
            box.blockSignals(True)
            box.clear()
            box.addItem(tr(label), None)
            options = set()
            for row in self.rows:
                options.update(terms(row[key]) if key != 'category' else [row[key]] if row[key] else [])
            for option in sorted(options, key=fold):
                box.addItem(option, option)
            index = box.findData(old)
            box.setCurrentIndex(max(index, 0))
            box.blockSignals(False)
        self.refresh(select=select)
    def refresh(self, *_args, select=None):
        current = self.selected()
        identifier = select if select is not None else current['id'] if current else None
        self.items.clear()
        query = fold(self.search.text()).split()
        for row in self.rows:
            text = fold(' '.join(str(row[k]) for k in FIELDS))
            if not all(word in text for word in query):
                continue
            if self.favorites.isChecked() and not row['favorite']:
                continue
            if self.category.currentData() and row['category'] != self.category.currentData():
                continue
            if any(box.currentData() and box.currentData() not in terms(row[key]) for box,key in [(self.genre,'genres'),(self.tag,'tags')]):
                continue
            item = QListWidgetItem(('★ ' if row['favorite'] else '') + row['name'] + '\n' + (row['category'] or tr('Sem categoria')) + (' · '+row['tags'] if row['tags'] else ''))
            item.setData(Qt.UserRole, row)
            self.items.addItem(item)
            if row['id'] == identifier:
                self.items.setCurrentItem(item)
        if not self.items.currentItem() and self.items.count():
            self.items.setCurrentRow(0)
        self.detail()
        self.collection.setText(tr('Biblioteca') + f'  ·  {self.items.count()} / {len(self.rows)}')
        self.empty.setVisible(self.items.count() == 0)
        self.statusBar().showMessage(tr('Salvo neste computador') + '  ·  Ctrl+N / Ctrl+E / Ctrl+Shift+C')
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
                self.reload(identifier)
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
                Path(path).write_text(json.dumps({'format':'banco-de-prompts', 'version':1, 'prompts':rows}, ensure_ascii=False, indent=2), encoding='utf-8')
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
                if content.get('format') != 'banco-de-prompts' or content.get('version') != 1:
                    raise ValueError('Formato ou versão desconhecidos.')
                content = content.get('prompts')
            if not isinstance(content, list): raise ValueError('Esperada uma lista de prompts.')
            rows = [validate(row) for row in content]
            if QMessageBox.question(self, 'Importar', f'Adicionar {len(rows)} prompts? Os atuais serão mantidos. Reimportações criam cópias.', QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes: return
            with self.store.db:
                for row in rows: self.store.save(row)
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
        DB_PATH = data_path()
        window = Window(DB_PATH)
        window.show()
        sys.exit(app.exec())
    except (OSError, sqlite3.Error) as error:
        QMessageBox.critical(None, 'Não foi possível abrir o banco', str(error))
        sys.exit(1)
