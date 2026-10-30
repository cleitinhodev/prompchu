<p align="center">
  <img src="assets/prompchu-corujinha.png" width="180" alt="Corujinha do Prompchu">
</p>

<h1 align="center">Prompchu 🦉</h1>
<p align="center">Seu banco de prompts — local, organizado e fácil de consultar.</p>

Aplicativo desktop em **Python + PySide6**, com interface em português e armazenamento local em **SQLite**. Guarde prompts para imagens, textos, programação e outros usos com informações que ajudam a encontrá-los depois.

## Recursos

- Cadastro, edição, duplicação e exclusão com confirmação.
- Nome, tags, gêneros, categoria, modelo/ferramenta, prompt negativo e notas.
- Favoritos e cópia do prompt com um clique.
- Busca em todos os campos, sem diferenciar maiúsculas nem acentos.
- Filtros combináveis por categoria, gênero, tag e favoritos.
- Importação e exportação JSON e backup completo SQLite.
- Corujinha inteira na identidade do programa e no ícone do executável; cabeça no ícone da janela.

O Prompchu organiza seus textos; não gera conteúdo com IA nem chama APIs externas.

## Executar pelo código-fonte

Recomendado: **Python 3.12 de 64 bits**. Dependência fixada em PySide6 6.8.3; use Python 3.10–3.13 compatível com essa versão do Qt.

No Windows, extraia/clone o projeto e abra `Iniciar.bat`. Ele cria um ambiente virtual e instala as dependências na primeira execução (requer internet e Python instalado).

Ou use o terminal:

```sh
python -m venv .venv
```

Ative o ambiente:

```bat
:: Windows
.venv\Scripts\activate
```

```sh
# Linux/macOS
source .venv/bin/activate
```

Depois:

```sh
python -m pip install -r requirements.txt
python main.py
```

O código usa recursos multiplataforma do Qt. A distribuição executável tem como alvo Windows 10/11 de 64 bits; suporte em outros sistemas depende dos requisitos do Qt.

## Gerar executável no Windows

Abra `Gerar-EXE.bat` no Windows com Python instalado. A build usa PyInstaller e inclui as bibliotecas necessárias, sem exigir Python no computador que receber o resultado.

Saída: `dist/Prompchu/Prompchu.exe`. **Distribua toda a pasta `dist/Prompchu`**, mantendo `_internal` e os demais arquivos juntos.

O workflow `.github/workflows/windows-build.yml` também testa e compila a versão Windows. No GitHub, abra **Actions → Build Windows → Run workflow**. Após sucesso, baixe o artefato `Prompchu-Windows64` e extraia-o antes de abrir o EXE. Artefatos de Actions podem exigir login e têm prazo de retenção.

## Usar

1. Clique em **Novo** e preencha nome e prompt (obrigatórios).
2. Separe tags e gêneros por vírgula. Categorias e nomes de modelos são livres.
3. Use a busca e os filtros para encontrar seus registros.
4. Clique em **Copiar prompt** para usar o texto em outra ferramenta.

| Atalho | Ação |
| --- | --- |
| Ctrl+N | Novo prompt |
| Ctrl+E | Editar selecionado |
| Ctrl+F | Focar busca |
| Duplo clique | Editar selecionado |

## Dados, privacidade e backups

Os dados ficam no seu computador. O caminho do banco aparece no rodapé. O identificador interno `BancoDePrompts` foi mantido para **continuar usando os dados da versão anterior**; o nome exibido é Prompchu.

No Windows, a localização usual é `%APPDATA%\Bugzinho\BancoDePrompts\prompts.sqlite3`.

- Atualizar o código ou a build não exige apagar esse arquivo.
- Os dados **não são criptografados**.
- Use **Backup do banco** e guarde uma cópia em outro dispositivo.
- Para restaurar SQLite, feche o aplicativo e substitua o banco pela cópia de backup.
- Para levar registros a outro PC, exporte JSON e importe no destino.
- A exportação inclui **todos** os prompts, mesmo com filtros ativos.
- Importar adiciona registros e mantém os existentes; repetir a importação cria cópias.
- `BANCO_PROMPTS_DIR` permite escolher outra pasta de dados com permissão de escrita.

A instalação e a build podem usar internet para baixar pacotes. O uso do aplicativo não envia prompts a serviços externos.

## Estrutura

```text
main.py                     Aplicativo e persistência SQLite
assets/                     PNGs transparentes e ICOs da corujinha
scripts/build_windows.py    Build PyInstaller com ícone e assets
Iniciar.bat                 Execução com ambiente virtual
Gerar-EXE.bat               Build local Windows
requirements.txt           Dependência de execução
requirements-build.txt     Dependências de build
tests/                      Testes de persistência e interface
.github/workflows/          Build Windows no GitHub Actions
```

## Testes

```sh
python -m unittest discover -s tests -v
python tests/smoke_ui.py
```

O teste de interface usa a plataforma Qt `offscreen`. Os testes automatizados não substituem a conferência de abertura em Windows real.

## Identidade visual

- `assets/prompchu-corujinha.png`: mascote completo em PNG transparente.
- `assets/prompchu-corujinha.ico`: ícone do executável.
- `assets/prompchu-cabeca.png`: cabeça em PNG transparente.
- `assets/prompchu-cabeca.ico`: ícone da janela e favicon para eventual site.

Os ICOs contêm resoluções de 16 a 256 pixels. As imagens foram criadas com auxílio de IA para este projeto.

## Desenvolvimento

Esta é a base inicial do Prompchu, versão **1.0.0**. Sugestões e problemas podem ser registrados nas Issues. Não envie bancos ou exports contendo informações privadas.

PySide6/Qt são dependências de terceiros com licenças próprias: consulte a [documentação do Qt for Python](https://doc.qt.io/qtforpython-6/). Este projeto ainda não declara uma licença de distribuição para seu código e arte.
