"""Offline UI catalogs. Stored prompts and taxonomy are never translated."""
from visual import preferences
LANGUAGES={'pt':'Português','en':'English','es':'Español','fr':'Français','de':'Deutsch','it':'Italiano','ja':'日本語','ko':'한국어','zh':'简体中文','ru':'Русский'}
ROWS='''Novo|New|Nuevo|Nouveau|Neu|Nuovo|新規|새로 만들기|新建|Создать
Editar|Edit|Editar|Modifier|Bearbeiten|Modifica|編集|편집|编辑|Изменить
Duplicar|Duplicate|Duplicar|Dupliquer|Duplizieren|Duplica|複製|복제|复制|Дублировать
Excluir|Delete|Eliminar|Supprimer|Löschen|Elimina|削除|삭제|删除|Удалить
Importar JSON|Import JSON|Importar JSON|Importer JSON|JSON importieren|Importa JSON|JSONを読み込む|JSON 가져오기|导入JSON|Импорт JSON
Exportar JSON|Export JSON|Exportar JSON|Exporter JSON|JSON exportieren|Esporta JSON|JSONを書き出す|JSON 내보내기|导出JSON|Экспорт JSON
Backup do banco|Database backup|Copia de seguridad|Sauvegarde|Datensicherung|Backup database|バックアップ|데이터 백업|数据库备份|Резервная копия
Favoritos|Favorites|Favoritos|Favoris|Favoriten|Preferiti|お気に入り|즐겨찾기|收藏|Избранное
Copiar prompt|Copy prompt|Copiar prompt|Copier le prompt|Prompt kopieren|Copia prompt|プロンプトをコピー|프롬프트 복사|复制提示词|Копировать промпт
Alternar favorito|Toggle favorite|Cambiar favorito|Basculer favori|Favorit umschalten|Cambia preferito|お気に入り切替|즐겨찾기 전환|切换收藏|Избранное вкл./выкл.
Todas as categorias|All categories|Todas las categorías|Toutes catégories|Alle Kategorien|Tutte le categorie|すべてのカテゴリ|모든 카테고리|所有类别|Все категории
Todos os gêneros|All genres|Todos los géneros|Tous les genres|Alle Genres|Tutti i generi|すべてのジャンル|모든 장르|所有类型|Все жанры
Todas as tags|All tags|Todas las etiquetas|Toutes les étiquettes|Alle Tags|Tutti i tag|すべてのタグ|모든 태그|所有标签|Все теги
Sem categoria|Uncategorized|Sin categoría|Sans catégorie|Ohne Kategorie|Senza categoria|未分類|미분류|未分类|Без категории
Selecione um prompt ou clique em Novo|Select a prompt or create one|Selecciona un prompt o crea uno|Sélectionnez ou créez un prompt|Prompt auswählen oder erstellen|Seleziona o crea un prompt|プロンプトを選択または新規作成|프롬프트를 선택하거나 만드세요|选择或新建提示词|Выберите или создайте промпт
Buscar por nome, texto, tags, gêneros, notas…|Search your prompt collection…|Buscar en tus prompts…|Rechercher dans vos prompts…|Prompts durchsuchen…|Cerca nei tuoi prompt…|プロンプトを検索…|프롬프트 검색…|搜索提示词…|Поиск промптов…
Prompchu · Seu banco de prompts|Prompchu · Your prompt library|Prompchu · Tu biblioteca de prompts|Prompchu · Votre bibliothèque|Prompchu · Deine Prompt-Bibliothek|Prompchu · La tua libreria|Prompchu · プロンプトライブラリ|Prompchu · 프롬프트 라이브러리|Prompchu · 提示词库|Prompchu · Библиотека промптов
Prompt negativo e notas|Negative prompt & notes|Prompt negativo y notas|Prompt négatif et notes|Negativer Prompt und Notizen|Prompt negativo e note|ネガティブとメモ|네거티브 및 메모|负面提示词与备注|Негативный промпт и заметки
Editar prompt|Edit prompt|Editar prompt|Modifier le prompt|Prompt bearbeiten|Modifica prompt|プロンプトを編集|프롬프트 편집|编辑提示词|Изменить промпт
Novo prompt|New prompt|Nuevo prompt|Nouveau prompt|Neuer Prompt|Nuovo prompt|新しいプロンプト|새 프롬프트|新提示词|Новый промпт
Nome *|Name *|Nombre *|Nom *|Name *|Nome *|名前 *|이름 *|名称 *|Название *
Tags (separadas por vírgula)|Tags (comma separated)|Etiquetas (con comas)|Étiquettes (virgules)|Tags (Kommas)|Tag (virgole)|タグ（カンマ区切り）|태그 (쉼표 구분)|标签（逗号分隔）|Теги (через запятую)
Gêneros (separados por vírgula)|Genres (comma separated)|Géneros (con comas)|Genres (virgules)|Genres (Kommas)|Generi (virgole)|ジャンル（カンマ区切り）|장르 (쉼표 구분)|类型（逗号分隔）|Жанры (через запятую)
Categoria|Category|Categoría|Catégorie|Kategorie|Categoria|カテゴリ|카테고리|类别|Категория
Modelo / ferramenta|Model / tool|Modelo / herramienta|Modèle / outil|Modell / Werkzeug|Modello / strumento|モデル / ツール|모델 / 도구|模型 / 工具|Модель / инструмент
Prompt negativo|Negative prompt|Prompt negativo|Prompt négatif|Negativer Prompt|Prompt negativo|ネガティブプロンプト|네거티브 프롬프트|负面提示词|Негативный промпт
Notas|Notes|Notas|Notes|Notizen|Note|メモ|메모|备注|Заметки
Favorito|Favorite|Favorito|Favori|Favorit|Preferito|お気に入り|즐겨찾기|收藏|Избранное
Marcar como favorito|Mark as favorite|Marcar favorito|Marquer favori|Als Favorit markieren|Segna preferito|お気に入りに追加|즐겨찾기에 추가|标记收藏|В избранное
Salvar|Save|Guardar|Enregistrer|Speichern|Salva|保存|저장|保存|Сохранить
Cancelar|Cancel|Cancelar|Annuler|Abbrechen|Annulla|キャンセル|취소|取消|Отмена
Animações|Animations|Animaciones|Animations|Animationen|Animazioni|アニメーション|애니메이션|动画|Анимации
Neon|Neon|Neón|Néon|Neon|Neon|ネオン|네온|霓虹|Неон
Idioma|Language|Idioma|Langue|Sprache|Lingua|言語|언어|语言|Язык
Prompt copiado!|Prompt copied!|¡Prompt copiado!|Prompt copié !|Prompt kopiert!|Prompt copiato!|コピーしました！|복사되었습니다!|已复制！|Промпт скопирован!'''
CATALOG={}
for row in ROWS.splitlines():
    values=row.split('|')
    assert len(values)==len(LANGUAGES), row
    CATALOG[values[0]]=dict(zip(LANGUAGES,values))

def tr(text):
    code=preferences().value('language','pt')
    return CATALOG.get(text,{}).get(code,text)
