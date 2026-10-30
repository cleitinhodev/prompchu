import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import sys
import tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from main import Window, Editor, validate
app = QApplication([])
with tempfile.TemporaryDirectory() as folder:
    window = Window(Path(folder)/'ui.sqlite3')
    assert window.windowTitle() == 'Prompchu'
    assert not window.windowIcon().isNull()
    with window.store.db:
        window.store.save(validate({'name':'Fantasia','prompt':'Castelo de cristal','tags':'anime','genres':'Fantasia','category':'Imagem'}))
        window.store.save(validate({'name':'Código','prompt':'Função Python','category':'Código'}))
    window.reload()
    assert window.items.count() == 2
    window.search.setText('cristal')
    assert window.items.count() == 1
    window.favorite()
    window.favorites.setChecked(True)
    assert window.items.count() == 1
    window.search.setText('inexistente')
    assert window.items.count() == 0 and not window.prompt.toPlainText()
    editor = Editor(window)
    editor.inputs['name'].setText('Teste')
    editor.inputs['prompt'].setPlainText('Prompt')
    editor.check()
    assert editor.result() == 1
    window.close()
print('Interface: OK')
