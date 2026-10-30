import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import Store, validate, fold

class Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'test.sqlite3'
        self.store = Store(self.path)
    def tearDown(self):
        self.store.db.close()
        self.temp.cleanup()
    def row(self):
        return validate({'name':'Cena mágica', 'prompt':'Um castelo', 'tags':'anime, anime, céu'})
    def test_persistence_update(self):
        with self.store.db: identifier = self.store.save(self.row())
        self.store.db.close()
        self.store = Store(self.path)
        row = self.store.all()[0]
        self.assertEqual(row['tags'], 'anime, céu')
        row['favorite'] = True
        row['prompt'] = 'Outro castelo'
        with self.store.db: self.store.save(row, identifier)
        self.assertEqual(len(self.store.all()), 1)
        self.assertEqual(self.store.all()[0]['prompt'], 'Outro castelo')
    def test_validation(self):
        for value in ({}, {'name':'a','prompt':3}, {'name':'a','prompt':'b','favorite':'yes'}):
            with self.assertRaises(ValueError): validate(value)
        self.assertEqual(fold('FICÇÃO'), 'ficcao')
    def test_rollback(self):
        with self.assertRaises(ValueError):
            with self.store.db:
                self.store.save(self.row())
                self.store.save({})
        self.assertEqual(self.store.all(), [])

if __name__ == '__main__': unittest.main()
