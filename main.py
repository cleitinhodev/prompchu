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
    QFileDialog, QDialog, QDialogButtonBox)

APP_NAME = 'Prompchu'
VERSION = '1.0.0'
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
        self.setWindowTitle('Editar prompt' if data else 'Novo prompt')
        self.resize(740, 780)
        outer = QVBoxLayout(self)
        form = QFormLayout()
        self.inputs = {}
        labels = {'name':'Nome *', 'tags':'Tags (separadas por vírgula)', 'genres':'Gêneros (separados por vírgula)', 'category':'Categoria', 'model':'Modelo / ferramenta', 'prompt':'Prompt *', 'negative':'Prompt negativo', 'notes':'Notas', 'favorite':'Favorito'}
        for key in FIELDS:
            if key == 'favorite':
                field = QCheckBox('Marcar como favorito')
                field.setChecked(bool((data or {}).get(key, False)))
            elif key in ('prompt', 'negative', 'notes'):
                field = QPlainTextEdit()
                field.setPlainText((data or {}).get(key, ''))
                field.setMinimumHeight(150 if key == 'prompt' else 65)
            else:
                field = QLineEdit((data or {}).get(key, ''))
            self.inputs[key] = field
            form.addRow(labels[key], field)
        self.inputs['category'].setPlaceholderText('Imagem, Texto, Vídeo, Código…')
        self.inputs['genres'].setPlaceholderText('Fantasia, Romance, Ficção científica…')
        outer.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setText('Salvar')
        buttons.button(QDialogButtonBox.Cancel).setText('Cancelar')
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
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(str(ASSETS / 'prompchu-cabeca.ico')))
        self.resize(1180, 760)
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        brand = QHBoxLayout()
        logo = QLabel()
        logo.setPixmap(QPixmap(str(ASSETS / 'prompchu-corujinha.png')).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        brand.addWidget(logo)
        heading = QLabel('Prompchu · Seu banco de prompts')
        heading.setStyleSheet('font-size:24px; font-weight:700; color:#a6c8ff; padding:8px')
        brand.addWidget(heading, 1)
        layout.addLayout(brand)
        bar = QHBoxLayout()
        for label, callback in [('Novo', self.new), ('Editar', self.edit), ('Duplicar', self.duplicate), ('Excluir', self.delete), ('Importar JSON', self.import_json), ('Exportar JSON', self.export_json), ('Backup do banco', self.backup)]:
            button = QPushButton(label)
            button.clicked.connect(callback)
            bar.addWidget(button)
        layout.addLayout(bar)
        filters = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText('Buscar por nome, texto, tags, gêneros, notas…')
        filters.addWidget(self.search, 3)
        self.category = QComboBox()
        self.genre = QComboBox()
        self.tag = QComboBox()
        for box in (self.category, self.genre, self.tag):
            filters.addWidget(box, 1)
            box.currentIndexChanged.connect(self.refresh)
        self.favorites = QCheckBox('Favoritos')
        filters.addWidget(self.favorites)
        layout.addLayout(filters)
        self.search.textChanged.connect(self.refresh)
        self.favorites.toggled.connect(self.refresh)
        split = QSplitter()
        self.items = QListWidget()
        self.items.currentItemChanged.connect(self.detail)
        self.items.itemDoubleClicked.connect(self.edit)
        split.addWidget(self.items)
        panel = QWidget()
        right = QVBoxLayout(panel)
        self.title = QLabel('Selecione um prompt ou clique em Novo')
        self.title.setWordWrap(True)
        self.title.setStyleSheet('font-size:20px; font-weight:600')
        self.meta = QLabel()
        self.meta.setWordWrap(True)
        right.addWidget(self.title)
        right.addWidget(self.meta)
        self.prompt = QPlainTextEdit()
        self.prompt.setReadOnly(True)
        right.addWidget(QLabel('Prompt'))
        right.addWidget(self.prompt, 3)
        self.extra = QPlainTextEdit()
        self.extra.setReadOnly(True)
        right.addWidget(QLabel('Prompt negativo e notas'))
        right.addWidget(self.extra, 1)
        actions = QHBoxLayout()
        for label, callback in [('Copiar prompt', self.copy), ('Alternar favorito', self.favorite)]:
            button = QPushButton(label)
            button.clicked.connect(callback)
            actions.addWidget(button)
        right.addLayout(actions)
        split.addWidget(panel)
        split.setSizes([360, 780])
        layout.addWidget(split, 1)
        self.statusBar().showMessage(str(path))
        for shortcut, callback in [('Ctrl+N', self.new), ('Ctrl+E', self.edit), ('Ctrl+F', self.search.setFocus)]:
            action = QAction(self)
            action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(callback)
            self.addAction(action)
        self.reload()
    def selected(self):
        item = self.items.currentItem()
        return item.data(Qt.UserRole) if item else None
    def reload(self, select=None):
        self.rows = self.store.all()
        for box, key, label in [(self.category,'category','Todas as categorias'), (self.genre,'genres','Todos os gêneros'), (self.tag,'tags','Todas as tags')]:
            old = box.currentData()
            box.blockSignals(True)
            box.clear()
            box.addItem(label, None)
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
            item = QListWidgetItem(('★ ' if row['favorite'] else '') + row['name'] + '\n' + (row['category'] or 'Sem categoria') + (' · '+row['tags'] if row['tags'] else ''))
            item.setData(Qt.UserRole, row)
            self.items.addItem(item)
            if row['id'] == identifier:
                self.items.setCurrentItem(item)
        if not self.items.currentItem() and self.items.count():
            self.items.setCurrentRow(0)
        self.detail()
        self.statusBar().showMessage(f'{self.items.count()} exibidos / {len(self.rows)} prompts • Banco: {DB_PATH}')
    def detail(self, *_):
        row = self.selected()
        self.title.setText(row['name'] if row else 'Selecione um prompt ou clique em Novo')
        self.title.setTextFormat(Qt.PlainText)
        self.meta.setTextFormat(Qt.PlainText)
        self.meta.setText(('Categoria: '+row['category']+' | Modelo: '+row['model']+'\nGêneros: '+row['genres']+'\nTags: '+row['tags']+'\nAtualizado: '+row['updated']) if row else '')
        self.prompt.setPlainText(row['prompt'] if row else '')
        self.extra.setPlainText(('NEGATIVO\n'+row['negative']+'\n\nNOTAS\n'+row['notes']) if row else '')
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
            self.statusBar().showMessage('Prompt copiado!', 3000)
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
                if Path(path).resolve() == DB_PATH.resolve(): raise ValueError('Escolha um arquivo diferente do banco em uso.')
                with sqlite3.connect(path) as target: self.store.db.backup(target)
                QMessageBox.information(self, 'Backup concluído', 'Cópia completa do banco salva.')
            except (OSError, ValueError, sqlite3.Error) as e: QMessageBox.critical(self, 'Erro', str(e))
    def closeEvent(self, event):
        self.store.db.close()
        event.accept()

STYLE = '''
QWidget { background:#171c28; color:#e5ebf5; font-family:"Segoe UI"; font-size:13px; }
QLineEdit, QPlainTextEdit, QListWidget, QComboBox {background:#202839; border:1px solid #36435b; border-radius:5px; padding:8px; selection-background-color:#365d96;}
QPushButton {background:#2c4263; border:1px solid #45638c; border-radius:5px; padding:9px 12px;}
QPushButton:hover {background:#3a5983;} QPushButton:pressed {background:#213550;}
QListWidget::item {padding:12px; border-bottom:1px solid #303c51;}
QListWidget::item:selected {background:#304d75;} QLabel {background:transparent;}
QSplitter::handle {background:#303c51;} QStatusBar {color:#9dafca;}
'''

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
    app.setStyleSheet(STYLE)
    try:
        DB_PATH = data_path()
        window = Window(DB_PATH)
        window.show()
        sys.exit(app.exec())
    except (OSError, sqlite3.Error) as error:
        QMessageBox.critical(None, 'Não foi possível abrir o banco', str(error))
        sys.exit(1)
