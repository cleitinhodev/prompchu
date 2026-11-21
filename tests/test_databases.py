import os,sys,tempfile,sqlite3,json,hashlib,unittest
from pathlib import Path
from unittest.mock import patch
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication,QMessageBox
from main import Window
from storage import Store
from databases import create_database,merge_databases,open_database
from visual import preferences

class DatabaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.last=preferences().value('last_database',None)
    def tearDown(self):
        if self.last is None:preferences().remove('last_database')
        else:preferences().setValue('last_database',self.last)
        self.temp.cleanup()
    def bank(self,name,tag):
        path=self.root/name;s=Store(path)
        with s.db:
            ident=s.save(dict(name='Mesmo nome',prompt='Conteúdo '+tag,tags=tag,shelf='Minha '+tag,favorite=True))
            s.db.execute("UPDATE prompts SET created='2020-01-01T00:00:00',updated='2020-02-01T00:00:00'")
            s.set_thumbnail(ident,b'preserve blob')
        s.db.close();return path
    def test_switch_same_window_resets_filters_and_commits(self):
        a=self.bank('a.sqlite3','a');b=self.bank('b.sqlite3','b');w=Window(a)
        try:
            identity=id(w);old=w.store.db
            w.search.setText('a');w.library.tags.setText('a');w.show_library()
            w.store.save(dict(name='Pendente',prompt='Salvar antes de trocar'))
            w.switch_database(b)
            self.assertEqual(id(w),identity);self.assertIs(w.library.store,w.store)
            self.assertEqual(w.search.text(),'');self.assertEqual(w.library.tags.text(),'')
            self.assertEqual(w.store.options('tags'),['b']);self.assertEqual(w.tag.count(),2)
            self.assertEqual(w.prompt.toPlainText(),'Conteúdo b')
            with self.assertRaises(sqlite3.ProgrammingError):old.execute('SELECT 1')
            check=Store(a);self.assertEqual(check.page()[1],2);check.db.close()
            w.switch_database(self.root/'empty.sqlite3',create=True)
            self.assertEqual(w.items.count(),0);self.assertEqual(w.tag.count(),1);self.assertEqual(len(w.library.cards),0)
        finally:w.close()
    def test_failed_open_leaves_current_bank_and_invalid_file_unchanged(self):
        a=self.bank('a.sqlite3','a');bad=self.root/'bad.sqlite3';bad.write_bytes(b'not sqlite');w=Window(a)
        try:
            with self.assertRaises(sqlite3.Error):w.switch_database(bad)
            self.assertEqual(w.store.options('tags'),['a']);self.assertEqual(bad.read_bytes(),b'not sqlite')
            with self.assertRaises(ValueError):w.switch_database(self.root/'missing.sqlite3')
            self.assertFalse((self.root/'missing.sqlite3').exists())
            with self.assertRaises(FileExistsError):w.switch_database(a,create=True)
            self.assertEqual(w.store.page()[1],1)
        finally:w.close()
    def test_merge_preserves_sources_dates_images_and_duplicate_names(self):
        a=self.bank('a.sqlite3','a');b=self.bank('b.sqlite3','b');before=[p.read_bytes() for p in (a,b)]
        destination=self.root/'merged.sqlite3';self.assertEqual(merge_databases(a,b,destination),2)
        self.assertEqual(before,[p.read_bytes() for p in (a,b)])
        result=Store(destination)
        self.assertEqual(len(result.all()),2);self.assertEqual(result.options('tags'),['a','b'])
        for row in result.all():
            self.assertEqual(row['created'],'2020-01-01T00:00:00');self.assertEqual(row['updated'],'2020-02-01T00:00:00')
            self.assertEqual(result.thumbnail(row['id']),b'preserve blob');self.assertTrue(row['favorite'])
        result.db.close()
        with self.assertRaises(ValueError):merge_databases(a,b,a)
        with self.assertRaises(ValueError):merge_databases(a,a,self.root/'same.sqlite3')
        self.assertEqual(before,[p.read_bytes() for p in (a,b)])
    def test_merge_failure_does_not_publish_partial_database(self):
        a=self.bank('a.sqlite3','a');bad=self.root/'bad.sqlite3';bad.write_text('bad')
        target=self.root/'out.sqlite3'
        with self.assertRaises(sqlite3.Error):merge_databases(a,bad,target)
        self.assertFalse(target.exists());self.assertEqual(list(self.root.glob('.prompchu-merge-*')),[])
    def test_export_only_selected_and_import_into_another_bank(self):
        a=self.root/'a.sqlite3';b=self.root/'b.sqlite3';w=Window(a)
        try:
            with w.store.db:
                keep=w.store.save(dict(name='Exportar este',prompt='Um',tags='selecionado'))
                w.store.save(dict(name='Não exportar',prompt='Dois'))
            w.reload(keep);output=self.root/'prompt.json'
            with patch('main.QFileDialog.getSaveFileName',return_value=(str(output),'')),patch('main.QMessageBox.information'):
                w.export_json()
            payload=json.loads(output.read_text());self.assertEqual(len(payload['prompts']),1);self.assertEqual(payload['prompts'][0]['name'],'Exportar este')
            w.switch_database(b,create=True)
            with patch('main.QFileDialog.getOpenFileName',return_value=(str(output),'')),patch('main.QMessageBox.question',return_value=QMessageBox.Yes),patch('main.QMessageBox.information'):
                w.import_json()
            self.assertEqual(w.store.page()[1],1);self.assertEqual(w.prompt.toPlainText(),'Um')
            old=Store(a);self.assertEqual(old.page()[1],2);old.db.close()
        finally:w.close()
