import os,sys,tempfile,sqlite3,unittest
from pathlib import Path
from unittest.mock import patch
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication,QDialog
from PySide6.QtCore import Qt
from main import Window,Editor
from storage import Store
from databases import merge_databases

class ShelfTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def test_empty_shelves_persist_backup_merge_and_isolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            a,b,out,backup=[Path(tmp)/n for n in ('a.db','b.db','merged.db','backup.db')]
            s=Store(a);s.add_shelf('Meus projetos')
            for name in (' ', 'meus projetos','IMAGENS','x'*81):
                with self.assertRaises(ValueError):s.add_shelf(name)
            with sqlite3.connect(backup) as dest:s.db.backup(dest)
            s.db.close();s=Store(a);self.assertIn('Meus projetos',s.shelf_names());s.db.close()
            t=Store(b);self.assertNotIn('Meus projetos',t.shelf_names());t.add_shelf('Vazia');t.db.close()
            self.assertEqual(merge_databases(a,b,out),0)
            for path,names in [(backup,['Meus projetos']),(out,['Meus projetos','Vazia'])]:
                t=Store(path)
                for name in names:self.assertIn(name,t.shelf_names())
                t.db.close()
    def test_create_dialog_editor_and_filter(self):
        w=Window(':memory:')
        try:
            with patch('library_view.QInputDialog') as dialog:
                dialog.return_value.exec.return_value=QDialog.Accepted
                dialog.return_value.textValue.return_value='Minha coleção'
                w.library.create_shelf_button.click()
            self.assertEqual(w.library.shelves.currentItem().data(Qt.UserRole),'Minha coleção')
            editor=Editor(w);self.assertGreaterEqual(editor.inputs['shelf'].findData('Minha coleção'),0);editor.close()
            with w.store.db:
                identifier=w.store.save(dict(name='Teste',prompt='Olá',shelf='Minha coleção'))
                w.store.save(dict(name='Outro',prompt='Outro',shelf='Imagens'))
            w.library.refresh();self.assertEqual(len(w.library.cards),1)
            with w.store.db:w.store.db.execute('DELETE FROM prompts WHERE id=?',(identifier,))
            w.reload();self.assertIn('Minha coleção',w.store.shelf_names())
            with patch('library_view.QInputDialog') as dialog:
                dialog.return_value.exec.return_value=QDialog.Rejected
                w.library.create_shelf()
            self.assertEqual(w.store.options('shelf'),['Imagens','Minha coleção'])
        finally:w.close()
