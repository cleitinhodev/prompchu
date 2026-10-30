"""Regression checks for the redesigned interface and optional motion."""
import os
import sys
import tempfile
import unittest
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from main import Window, Editor
from visual import preferences
from i18n import LANGUAGES

class AppearanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.w=Window(Path(self.tmp.name)/'test.sqlite3')
        self.saved={key:preferences().value(key) for key in ('language','motion','neon','geometry','splitter')}
    def tearDown(self):
        self.w.close()
        for key,value in self.saved.items():
            if value is None: preferences().remove(key)
            else: preferences().setValue(key,value)
        self.tmp.cleanup()
    def test_filters_details_and_copy_preserve_text(self):
        text='Primeira linha\n\n<tag> & conteúdo'
        with self.w.store.db:
            self.w.store.save(dict(name='<b>Nome literal</b>',prompt=text,negative='negativo',notes='anotação',tags='arte',favorite=True))
        self.w.reload()
        self.assertEqual(self.w.negative.toPlainText(),'negativo')
        self.assertEqual(self.w.notes.toPlainText(),'anotação')
        self.w.copy()
        self.assertEqual(self.app.clipboard().text(),text)
        self.w.search.setText('não existe')
        self.assertEqual(self.w.items.count(),0)
        self.assertTrue(all(not b.isEnabled() for b in self.w.selection_buttons))
        self.w.clear_filters()
        self.assertEqual(self.w.items.count(),1)
    def test_neon_and_motion_are_independent(self):
        self.w.show();self.app.processEvents()
        self.w.neon.setChecked(True);self.w.motion.setChecked(False)
        self.assertTrue(self.w.lights.enabled)
        self.assertFalse(self.w.lights.timer.isActive())
        self.assertTrue(self.w.lights.layers[0].isVisible())
        self.w.neon.setChecked(False)
        self.assertTrue(all(not layer.isVisible() for layer in self.w.lights.layers))
        self.w.motion.setChecked(True);self.w.neon.setChecked(True)
        self.w.hide();self.app.processEvents()
        self.assertFalse(self.w.lights.timer.isActive())
    def test_wordmark_fault_is_per_letter_and_can_stop(self):
        sign=self.w.wordmark
        self.assertEqual(sign.face.family(),'Fredoka')
        sign.rng.seed(17)
        sign.step()
        self.assertIn(sign.dim_letter, range(8))
        sign.step()
        self.assertIsNone(sign.dim_letter)
        sign.configure(True,False)
        self.assertFalse(sign.timer.isActive())
        self.assertIsNone(sign.dim_letter)
        sign.configure(False,True)
        self.assertFalse(sign.timer.isActive())

    def test_all_languages_and_scrollable_editor(self):
        for code in LANGUAGES:
            preferences().setValue('language',code)
            w=Window(':memory:')
            w.resize(940,640);w.show();self.app.processEvents()
            self.assertFalse(w.grab().isNull())
            editor=Editor(w);editor.resize(620,480);editor.show();self.app.processEvents()
            self.assertFalse(editor.grab().isNull())
            editor.close();w.close()

if __name__=='__main__': unittest.main()
