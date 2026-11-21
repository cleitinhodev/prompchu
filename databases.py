"""Independent database files and a non-destructive, transactional merge."""
import os
import sqlite3
import tempfile
from pathlib import Path
from storage import Store, FIELDS, validate, fold

REQUIRED={'id','name','tags','genres','category','model','prompt','negative','notes','favorite','created','updated'}

def same_file(a,b):
    a,b=Path(a),Path(b)
    return a.resolve()==b.resolve() or (a.exists() and b.exists() and os.path.samefile(a,b))

def read_database(path):
    path=Path(path).resolve()
    if not path.is_file():raise ValueError('O banco selecionado não existe.')
    db=sqlite3.connect(path.as_uri()+'?mode=ro',uri=True)
    db.row_factory=sqlite3.Row
    try:
        db.execute('PRAGMA query_only=ON')
        if db.execute('PRAGMA quick_check').fetchone()[0]!='ok':raise ValueError('O banco está danificado.')
        tables={r['name']:r['type'] for r in db.execute("SELECT name,type FROM sqlite_master WHERE name IN ('prompts','thumbnails','shelves')")}
        if tables.get('prompts')!='table':raise ValueError('Este arquivo não é um banco do Prompchu.')
        if not REQUIRED.issubset({r['name'] for r in db.execute('PRAGMA table_info(prompts)')}):raise ValueError('O banco não tem os campos necessários do Prompchu.')
        if db.execute("SELECT 1 FROM sqlite_master WHERE type='trigger' AND tbl_name IN ('prompts','thumbnails','shelves')").fetchone():raise ValueError('Banco com gatilhos não suportados.')
        columns={r['name'] for r in db.execute('PRAGMA table_info(prompts)')}
        text_columns=(REQUIRED-{'id','favorite'})|({'shelf'} if 'shelf' in columns else set())
        invalid=' OR '.join(f"typeof({key})!='text'" for key in sorted(text_columns))
        if db.execute("SELECT 1 FROM prompts WHERE "+invalid+" OR typeof(id)!='integer' OR favorite NOT IN (0,1) OR favorite IS NULL LIMIT 1").fetchone():raise ValueError('O banco contém registros inválidos.')
        if 'thumbnails' in tables:
            if tables['thumbnails']!='table' or not {'prompt_id','image'}.issubset({r['name'] for r in db.execute('PRAGMA table_info(thumbnails)')}):raise ValueError('Tabela de miniaturas inválida.')
        if 'shelves' in tables:
            if tables['shelves']!='table' or 'name' not in {r['name'] for r in db.execute('PRAGMA table_info(shelves)')}:raise ValueError('Tabela de prateleiras inválida.')
            if db.execute("SELECT 1 FROM shelves WHERE typeof(name)!='text' LIMIT 1").fetchone():raise ValueError('Prateleira inválida.')
        return db
    except Exception:
        db.close();raise

def create_database(path):
    path=Path(path)
    # Exclusive creation: never truncate an existing bank, including aliases.
    with path.open('xb'):pass
    try:return Store(path)
    except Exception:
        path.unlink(missing_ok=True);raise

def open_database(path):
    db=read_database(path);db.close()
    return Store(path)

def merge_databases(first,second,destination):
    sources=[Path(first).resolve(),Path(second).resolve()];destination=Path(destination).resolve()
    if same_file(*sources):raise ValueError('Escolha dois bancos diferentes.')
    if destination.exists() or any(same_file(p,destination) for p in sources):raise ValueError('Escolha um arquivo novo para o banco unido. Os originais não serão substituídos.')
    readers=[];output=None;temporary=None
    try:
        for path in sources:
            db=read_database(path);db.execute('BEGIN');readers.append(db)
        fd,name=tempfile.mkstemp(prefix='.prompchu-merge-',suffix='.sqlite3',dir=destination.parent);os.close(fd);temporary=Path(name)
        output=Store(temporary);count=0
        with output.db:
            for source in readers:
                if source.execute("SELECT 1 FROM sqlite_master WHERE name='shelves' AND type='table'").fetchone():
                    for shelf in source.execute('SELECT name FROM shelves'):
                        output.db.execute('INSERT OR IGNORE INTO shelves(name) VALUES (?)',(shelf[0],))
                has_images=source.execute("SELECT 1 FROM sqlite_master WHERE name='thumbnails' AND type='table'").fetchone()
                for original in source.execute('SELECT * FROM prompts ORDER BY id'):
                    row=dict(original)
                    if row['favorite'] not in (0,1):raise ValueError('Favorito inválido no banco de origem.')
                    row['favorite']=bool(row['favorite'])
                    for key in ('created','updated'):
                        if not isinstance(row[key],str):raise ValueError('Data inválida no banco de origem.')
                    if 'shelf' not in row:row['shelf']=legacy_shelf(row['category'])
                    identifier=output.save(validate(row))
                    output.db.execute('UPDATE prompts SET created=?,updated=? WHERE id=?',(row['created'],row['updated'],identifier))
                    if has_images:
                        image=source.execute('SELECT image FROM thumbnails WHERE prompt_id=?',(row['id'],)).fetchone()
                        if image:
                            if not isinstance(image[0],bytes):raise ValueError('Miniatura inválida no banco de origem.')
                            output.set_thumbnail(identifier,image[0])
                    count+=1
        output.db.close();output=None
        # Publish the completed database atomically and refuse concurrent overwrites.
        os.link(temporary,destination)
        return count
    finally:
        if output is not None:output.db.close()
        for db in readers:db.close()
        if temporary is not None:temporary.unlink(missing_ok=True)

def legacy_shelf(category):
    return {'imagem':'Imagens','imagens':'Imagens','video':'Vídeos','videos':'Vídeos','musica':'Músicas','musicas':'Músicas','codigo':'Programação','programacao':'Programação','texto':'Escrita','documentos':'Documentos','estudos':'Estudos','marketing':'Marketing'}.get(fold(category),'Outros')
