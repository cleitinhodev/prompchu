"""SQLite queries with bounded pages; additive schema and embedded thumbnails."""
import sqlite3
import unicodedata
from datetime import datetime

FIELDS=('name','tags','genres','category','model','prompt','negative','notes','favorite','shelf')
SHELVES=('Imagens','Vídeos','Músicas','Documentos','Programação','Escrita','Estudos','Marketing','Outros')

def fold(text):
    return ''.join(c for c in unicodedata.normalize('NFD',str(text).casefold()) if unicodedata.category(c)!='Mn')

def terms(text):
    return list(dict.fromkeys(t.strip() for t in text.split(',') if t.strip()))

def validate(data):
    if not isinstance(data,dict):raise ValueError('Cada prompt precisa ser um objeto JSON.')
    result={}
    for key in FIELDS:
        value=data.get(key,False if key=='favorite' else '')
        if key=='favorite':
            if type(value) is not bool:raise ValueError('favorite precisa ser true ou false.')
        elif not isinstance(value,str):raise ValueError(f'O campo {key} precisa ser texto.')
        result[key]=value
    if not result['name'].strip() or not result['prompt'].strip():raise ValueError('Nome e prompt são obrigatórios.')
    result['name']=result['name'].strip()
    for key in ('tags','genres'):result[key]=', '.join(terms(result[key]))
    return result

class Store:
    def __init__(self,path):
        self.db=sqlite3.connect(path)
        self.db.row_factory=sqlite3.Row
        self.db.create_function('fold',1,fold,deterministic=True)
        self.db.create_function('has_term',2,lambda text,term:int(fold(term) in {fold(t) for t in terms(text)}),deterministic=True)
        self.db.execute('PRAGMA foreign_keys=ON')
        with self.db:
            self.db.execute('''CREATE TABLE IF NOT EXISTS prompts (
                id INTEGER PRIMARY KEY, name TEXT NOT NULL, tags TEXT NOT NULL,
                genres TEXT NOT NULL, category TEXT NOT NULL, model TEXT NOT NULL,
                prompt TEXT NOT NULL, negative TEXT NOT NULL, notes TEXT NOT NULL,
                favorite INTEGER NOT NULL DEFAULT 0, created TEXT NOT NULL, updated TEXT NOT NULL)''')
            cols={r['name'] for r in self.db.execute('PRAGMA table_info(prompts)')}
            if 'shelf' not in cols:
                self.db.execute("ALTER TABLE prompts ADD COLUMN shelf TEXT NOT NULL DEFAULT ''")
                for shelf,names in {'Imagens':['imagem','imagens','image'],'Vídeos':['video','videos'],'Músicas':['musica','musicas','audio'],'Documentos':['documento','documentos'],'Programação':['codigo','programacao','code'],'Escrita':['texto','escrita'],'Estudos':['estudos','educacao'],'Marketing':['marketing']}.items():
                    for name in names:self.db.execute('UPDATE prompts SET shelf=? WHERE fold(category)=?',(shelf,name))
            self.db.execute('CREATE TABLE IF NOT EXISTS thumbnails (prompt_id INTEGER PRIMARY KEY REFERENCES prompts(id) ON DELETE CASCADE, image BLOB NOT NULL)')
            self.db.execute('CREATE INDEX IF NOT EXISTS prompt_created ON prompts(created DESC,id DESC)')
            self.db.execute('CREATE INDEX IF NOT EXISTS prompt_recent ON prompts(favorite DESC,updated DESC,id DESC)')
            self.db.execute('CREATE INDEX IF NOT EXISTS prompt_shelf ON prompts(shelf)')
    def all(self):
        return [dict(r) for r in self.db.execute('SELECT * FROM prompts ORDER BY favorite DESC,updated DESC,id DESC')]
    def get(self,identifier):
        row=self.db.execute('SELECT * FROM prompts WHERE id=?',(identifier,)).fetchone()
        return dict(row) if row else None
    def thumbnail(self,identifier):
        row=self.db.execute('SELECT image FROM thumbnails WHERE prompt_id=?',(identifier,)).fetchone()
        return bytes(row[0]) if row else None
    def save(self,data,identifier=None):
        data=validate(data);now=datetime.now().isoformat(timespec='seconds');values=[data[k] for k in FIELDS]
        if identifier is None:
            cur=self.db.execute('INSERT INTO prompts ('+','.join(FIELDS)+',created,updated) VALUES ('+','.join('?' for _ in range(len(FIELDS)+2))+')',values+[now,now]);return cur.lastrowid
        self.db.execute('UPDATE prompts SET '+','.join(k+'=?' for k in FIELDS)+',updated=? WHERE id=?',values+[now,identifier]);return identifier
    def set_thumbnail(self,identifier,image):
        if image is None:self.db.execute('DELETE FROM thumbnails WHERE prompt_id=?',(identifier,))
        else:self.db.execute('INSERT OR REPLACE INTO thumbnails(prompt_id,image) VALUES (?,?)',(identifier,image))
    def options(self,key):
        if key not in ('tags','genres','category','shelf'):raise ValueError(key)
        options=set()
        for row in self.db.execute(f'SELECT DISTINCT {key} FROM prompts'):
            options.update(terms(row[0]) if key in ('tags','genres') else ([row[0]] if row[0] else []))
        return sorted(options,key=fold)
    def where(self,query='',tags='',genre='',category='',shelf='',favorite=False,after='',before='',**_):
        clauses=[];params=[]
        haystack="fold(name||' '||tags||' '||genres||' '||category||' '||model||' '||prompt||' '||negative||' '||notes||' '||shelf)"
        for token in fold(query).split():clauses.append(f'instr({haystack},?)>0');params.append(token)
        for tag in terms(tags):clauses.append('has_term(tags,?)=1');params.append(tag)
        if genre:clauses.append('has_term(genres,?)=1');params.append(genre)
        for field,value in [('category',category),('shelf',shelf)]:
            if value:
                if field=='shelf' and value=='Outros':clauses.append("(shelf='Outros' OR shelf='')")
                else:clauses.append(f'{field}=?');params.append(value)
        if favorite:clauses.append('favorite=1')
        if after:clauses.append('created>=?');params.append(after)
        if before:clauses.append('created<?');params.append(before+'T99')
        return (' WHERE '+' AND '.join(clauses) if clauses else ''),params
    def page(self,offset=0,limit=100,sort='recent',**filters):
        limit=max(1,min(int(limit),100));where,params=self.where(**filters)
        order={'recent':'favorite DESC,updated DESC,id DESC','new':'created DESC,id DESC','old':'created ASC,id ASC','name':'fold(name),id'}.get(sort,'created DESC,id DESC')
        total=self.db.execute('SELECT COUNT(*) FROM prompts'+where,params).fetchone()[0]
        offset=max(0,min(int(offset),((max(total,1)-1)//limit)*limit))
        cols='id,name,tags,genres,category,model,favorite,shelf,created,updated'
        rows=[dict(r) for r in self.db.execute('SELECT '+cols+' FROM prompts'+where+' ORDER BY '+order+' LIMIT ? OFFSET ?',params+[limit,offset])]
        return rows,total,offset
    def offset_for(self,identifier,limit=100,**filters):
        where,params=self.where(**filters)
        row=self.db.execute('WITH ranked AS (SELECT id,row_number() OVER (ORDER BY favorite DESC,updated DESC,id DESC)-1 AS position FROM prompts'+where+') SELECT position FROM ranked WHERE id=?',params+[identifier]).fetchone()
        return (row[0]//limit)*limit if row else 0
