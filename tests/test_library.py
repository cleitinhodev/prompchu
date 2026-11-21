import os,sys,tempfile,sqlite3,unittest
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage,QColor
from PySide6.QtCore import Qt
from main import Window,Editor
from storage import Store
from thumbnails import load_thumbnail,normalize_image

class LibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'data.sqlite3';self.w=Window(self.path)
    def tearDown(self):self.w.close();self.tmp.cleanup()
    def test_large_collection_pages_and_open_card(self):
        with self.w.store.db:
            for i in range(237):self.w.store.save(dict(name=f'Prompt {i:03}',prompt='Texto longo '+str(i),tags='teste',shelf='Imagens'))
        self.w.reload();self.assertEqual(self.w.items.count(),100)
        self.w.turn_page(1);self.assertEqual(self.w.items.count(),100)
        self.w.turn_page(1);self.assertEqual(self.w.items.count(),37)
        self.w.show_library();self.assertEqual(len(self.w.library.cards),24)
        self.w.library.query.setText('Prompt 003');self.w.library.reset()
        self.assertEqual(len(self.w.library.cards),1)
        self.w.library.cards[0].click()
        self.assertIs(self.w.pages.currentWidget(),self.w.home)
        self.assertEqual(self.w.title.text(),'Prompt 003')
        self.assertEqual(self.w.prompt.toPlainText(),'Texto longo 3')
        self.assertNotIn('prompt',self.w.items.currentItem().data(Qt.UserRole))
        self.w.search.setText('Prompt 236');self.assertEqual(self.w.items.count(),1)
    def test_combined_filters_dates_and_literal_search(self):
        with self.w.store.db:
            a=self.w.store.save(dict(name='Árvore 100%',prompt='único',tags='arte, anime',shelf='Imagens',favorite=True))
            b=self.w.store.save(dict(name='Arte',prompt='outro',tags='arte digital',shelf='Vídeos'))
            self.w.store.db.execute("UPDATE prompts SET created='2026-01-10T12:00:00' WHERE id=?",(a,))
        rows,total,_=self.w.store.page(query='arvore 100%',tags='arte,anime',shelf='Imagens',favorite=True,after='2026-01-10',before='2026-01-10')
        self.assertEqual(total,1);self.assertEqual(rows[0]['id'],a)
        self.assertEqual(self.w.store.page(tags='arte')[1],1)
        self.assertEqual(self.w.store.page(before='2026-01-09')[1],0)
    def test_thumbnail_is_embedded_and_backup_keeps_it(self):
        image=QImage(1000,600,QImage.Format_RGB32);image.fill(QColor('purple'))
        source=Path(self.tmp.name)/'source.jpg';image.save(str(source))
        data=load_thumbnail(source);source.unlink()
        with self.w.store.db:
            identifier=self.w.store.save(dict(name='Imagem',prompt='Teste'))
            self.w.store.set_thumbnail(identifier,data)
        self.w.reload(identifier)
        editor=Editor(self.w,self.w.selected());self.assertEqual(editor.thumbnail,data);editor.close()
        backup=sqlite3.connect(Path(self.tmp.name)/'backup.sqlite3');self.w.store.db.backup(backup)
        self.assertEqual(backup.execute('SELECT image FROM thumbnails').fetchone()[0],data);backup.close()
        with self.assertRaises(ValueError):normalize_image(b'not a png')
        with self.w.store.db:self.w.store.db.execute('DELETE FROM prompts WHERE id=?',(identifier,))
        self.assertIsNone(self.w.store.thumbnail(identifier))
    def test_json_roundtrip_includes_shelf_and_thumbnail(self):
        from unittest.mock import patch
        from PySide6.QtWidgets import QMessageBox
        image=QImage(80,60,QImage.Format_RGB32);image.fill(QColor('blue'))
        source=Path(self.tmp.name)/'pic.png';image.save(str(source));data=load_thumbnail(source)
        with self.w.store.db:
            identifier=self.w.store.save(dict(name='Exportar',prompt='Conteúdo',shelf='Imagens'))
            self.w.store.set_thumbnail(identifier,data)
        export=Path(self.tmp.name)/'export.json'
        with patch('main.QFileDialog.getSaveFileName',return_value=(str(export),'')),patch('main.QMessageBox.information'):
            self.w.export_json()
        with patch('main.QFileDialog.getOpenFileName',return_value=(str(export),'')),patch('main.QMessageBox.question',return_value=QMessageBox.Yes),patch('main.QMessageBox.information'):
            self.w.import_json()
        rows=self.w.store.all();self.assertEqual(len(rows),2)
        for row in rows:
            self.assertEqual(row['shelf'],'Imagens');self.assertEqual(self.w.store.thumbnail(row['id']),data)
    def test_demo_is_separate(self):
        self.w.open_demo();demo=self.w.demo_windows[-1]
        try:
            self.assertEqual(demo.store.page()[1],54)
            self.assertEqual(self.w.store.page()[1],0)
            self.assertNotEqual(demo.database_path,self.w.database_path)
        finally:demo.close()
    def test_original_schema_migration(self):
        path=Path(self.tmp.name)/'old.sqlite3';db=sqlite3.connect(path)
        db.execute('CREATE TABLE prompts (id INTEGER PRIMARY KEY,name TEXT,tags TEXT,genres TEXT,category TEXT,model TEXT,prompt TEXT,negative TEXT,notes TEXT,favorite INTEGER,created TEXT,updated TEXT)')
        db.execute("INSERT INTO prompts VALUES(1,'Antigo','','','Imagem','','Texto preservado','','',0,'2020-01-01','2020-01-01')");db.commit();db.close()
        store=Store(path)
        self.assertEqual(store.get(1)['prompt'],'Texto preservado');self.assertEqual(store.get(1)['shelf'],'Imagens')
        store.db.close()
