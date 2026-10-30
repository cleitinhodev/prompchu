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
ROWS += "\n" + 'Biblioteca|Library|Biblioteca|Bibliothèque|Bibliothek|Biblioteca|ライブラリ|라이브러리|资料库|Библиотека\nLimpar filtros|Clear filters|Limpiar filtros|Effacer les filtres|Filter löschen|Cancella filtri|フィルター解除|필터 초기화|清除筛选|Сбросить фильтры\nGêneros|Genres|Géneros|Genres|Genres|Generi|ジャンル|장르|类型|Жанры\nTags|Tags|Etiquetas|Étiquettes|Tags|Tag|タグ|태그|标签|Теги\nESPAÇO DE CRIAÇÃO|CREATIVE SPACE|ESPACIO CREATIVO|ESPACE CRÉATIF|KREATIVBEREICH|SPAZIO CREATIVO|クリエイティブスペース|창작 공간|创作空间|ТВОРЧЕСКОЕ ПРОСТРАНСТВО\nSalvo neste computador|Saved on this computer|Guardado en este equipo|Enregistré sur cet ordinateur|Auf diesem Computer gespeichert|Salvato su questo computer|この端末に保存|이 컴퓨터에 저장|保存在此电脑|Сохранено на этом компьютере\ncaracteres|characters|caracteres|caractères|Zeichen|caratteri|文字|자|字符|символов\npalavras|words|palabras|mots|Wörter|parole|単語|단어|词|слов\nNenhum resultado. Ajuste os filtros ou crie um prompt.|No results. Adjust filters or create a prompt.|Sin resultados. Ajusta los filtros o crea un prompt.|Aucun résultat. Modifiez les filtres ou créez un prompt.|Keine Ergebnisse. Filter ändern oder Prompt erstellen.|Nessun risultato. Modifica i filtri o crea un prompt.|結果なし。条件を変更するか作成してください。|결과가 없습니다. 필터를 바꾸거나 새로 만드세요.|无结果。请调整筛选或新建提示词。|Нет результатов. Измените фильтры или создайте промпт.\nSeu próximo resultado começa com uma boa ideia.|Your next result starts with a good idea.|Tu próximo resultado empieza con una buena idea.|Votre prochain résultat commence par une bonne idée.|Dein nächstes Ergebnis beginnt mit einer guten Idee.|Il tuo prossimo risultato inizia con una buona idea.|次の成果は、よいアイデアから。|다음 결과는 좋은 아이디어에서 시작됩니다.|下一个成果，从好点子开始。|Следующий результат начинается с хорошей идеи.'
ROWS += "\n" + 'Sobre|About|Acerca de|À propos|Über|Informazioni|このアプリについて|정보|关于|О программе\nVersão|Version|Versión|Version|Version|Versione|バージョン|버전|版本|Версия\nRepositório|Repository|Repositorio|Dépôt|Repository|Repository|リポジトリ|저장소|代码仓库|Репозиторий\nSite|Website|Sitio web|Site web|Website|Sito web|ウェブサイト|웹사이트|网站|Сайт\nDonate|Donate|Donar|Faire un don|Spenden|Dona|寄付|후원|捐赠|Поддержать\nFechar|Close|Cerrar|Fermer|Schließen|Chiudi|閉じる|닫기|关闭|Закрыть\nSeu banco de prompts local. Organize ideias, tags e favoritos em um só lugar.|Your local prompt library. Organize ideas, tags and favorites in one place.|Tu biblioteca local de prompts. Organiza ideas, etiquetas y favoritos en un solo lugar.|Votre bibliothèque locale de prompts. Organisez idées, étiquettes et favoris au même endroit.|Deine lokale Prompt-Bibliothek. Ideen, Tags und Favoriten an einem Ort.|La tua libreria locale di prompt. Organizza idee, tag e preferiti in un unico posto.|ローカルのプロンプト集。アイデア、タグ、お気に入りをまとめて管理。|로컬 프롬프트 라이브러리. 아이디어, 태그, 즐겨찾기를 한곳에서 관리하세요.|本地提示词库。在一处整理创意、标签和收藏。|Локальная библиотека промптов. Идеи, теги и избранное в одном месте.'
CATALOG={}
for row in ROWS.splitlines():
    values=row.split('|')
    assert len(values)==len(LANGUAGES), row
    CATALOG[values[0]]=dict(zip(LANGUAGES,values))

def tr(text):
    code=preferences().value('language','pt')
    return CATALOG.get(text,{}).get(code,text)
