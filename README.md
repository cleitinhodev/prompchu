<p align="center"><img src="assets/prompchu-corujinha.png" width="180" alt="Corujinha do Prompchu"></p>
<h1 align="center">Prompchu 🦉</h1>
<p align="center">Seu banco de prompts — local, organizado e fácil de consultar.</p>

Aplicativo desktop em **Python + PySide6 + SQLite**. Versão estável **1.3.0**, disponível para Windows, Linux e macOS Apple Silicon em [Releases](https://github.com/cleitinhodev/prompchu/releases/latest).

## Recursos

- Cadastro, edição, duplicação, exclusão, favoritos e cópia de prompts.
- Nome, tags, gêneros, categoria, modelo, prompt negativo, notas e miniatura JPG/PNG.
- Biblioteca em cartões com busca, filtros combináveis, datas, ordenação e prateleiras.
- Botão **Criar prateleira** acima da lista à esquerda: nomeie e salve. Prateleiras pertencem ao banco e permanecem mesmo vazias.
- Dez idiomas para navegação e editor, neon e animações opcionais. Algumas mensagens técnicas permanecem em português.
- Fonte Fredoka no título animado, ícones da corujinha e janela Sobre.

O Prompchu organiza textos. Não gera conteúdo com IA nem chama APIs de geração.

## Bancos e transferência

No menu **Arquivo**:

| Opção | Funcionamento |
| --- | --- |
| Criar banco | Cria uma coleção vazia em um arquivo novo. |
| Abrir banco | Troca de banco na mesma janela, salvando antes as alterações pendentes. |
| Backup do banco | Copia todo o banco, incluindo miniaturas e prateleiras vazias. |
| Juntar bancos | Une dois bancos em um terceiro arquivo, preservando os originais, datas e duplicatas. |
| Importar prompt | Adiciona JSON ao banco atual; aceita também coleções antigas. |
| Exportar prompt | Exporta somente o selecionado, com metadados e miniatura. |

O nome do banco aparece abaixo do cabeçalho; passe o mouse para ver o caminho. O último banco aberto é lembrado. Filtros são limpos na troca de banco; suas opções vêm da coleção aberta.

As alterações são gravadas ao salvar uma edição, adicionar, excluir ou alterar favoritos. Não é necessário um comando de salvar banco.

## Exemplos úteis opcionais

Baixe **Prompchu-Bancos-Uteis-1.3.0.zip** no release. A pasta contém 9 bancos, com 60 prompts cada: **Imagens, Vídeos, Documentos, Programação, Músicas, Estudos, Marketing, Escrita e Produtividade**.

São **540 modelos**: 20 tarefas por área, cada uma com versões para criar, revisar e adaptar. Substitua os campos entre colchetes. Extraia e abra um .sqlite3 por **Arquivo → Abrir banco**. O pacote inclui instruções e catálogo.

Os exemplos são um download separado: não são importados ou abertos automaticamente. Para transferir um item, exporte o prompt e importe no seu banco. Para combinar coleções completas, use Juntar bancos. As respostas das ferramentas precisam de revisão.

## Usar

1. Clique em **Novo prompt** e preencha nome e prompt.
2. Separe tags e gêneros por vírgulas e escolha uma prateleira.
3. Opcionalmente, escolha uma miniatura no editor.
4. Use a Biblioteca e os filtros; clique em um cartão para abrir o texto na tela inicial.
5. Clique em **Copiar prompt**.

A lista inicial carrega 100 registros por página e a Biblioteca, 24 cartões. Busca e filtros consultam todo o banco. Miniaturas têm entrada limitada a 20 MB e 40 megapixels e são reduzidas para até 640 × 400 no SQLite. A busca textual ainda examina conteúdo e não promete tempo constante em coleções enormes.

| Atalho | Ação |
| --- | --- |
| Ctrl+N | Novo prompt |
| Ctrl+E | Editar selecionado |
| Ctrl+F | Focar busca |
| Ctrl+Shift+C | Copiar prompt |

## Dados e privacidade

Os dados ficam no computador e não são criptografados. O banco padrão no Windows costuma ficar em `%APPDATA%\Bugzinho\BancoDePrompts\prompts.sqlite3`; o identificador interno antigo preserva dados existentes. Bancos criados pelo usuário ficam onde ele escolher.

Use backups antes de atualizar e guarde cópias em outro dispositivo. Abra um backup pelo menu Abrir banco. Importar JSON adiciona registros; repetir a importação cria cópias. A exportação v2 inclui prateleira e miniatura; a versão 1.2.0 não importa v2. `BANCO_PROMPTS_DIR` permite definir a pasta do banco padrão.

A instalação pelo código pode baixar dependências; o uso do aplicativo não envia prompts ou imagens a serviços externos.

## Executar e compilar

Use Python 3.12 de 64 bits. No Windows, `Iniciar.bat` prepara o ambiente. Ou crie um ambiente virtual, ative-o e execute:

```sh
python -m pip install -r requirements.txt
python main.py
```

Para gerar o pacote no sistema de destino:

```sh
python -m pip install -r requirements-build.txt
python scripts/build_release.py
```

Distribua a pasta completa, não apenas o executável. `Gerar-EXE.bat` também está disponível para Windows. Consulte requisitos e instruções de cada sistema nas notas do release.

## Testes e coleções

```sh
python -m unittest discover -s tests -v
python tests/smoke_ui.py
python scripts/make_useful_banks.py
```

O último comando gera os bancos úteis e o ZIP em `examples/`, sem ler ou modificar dados do usuário. Os testes de interface usam Qt offscreen.

## Desenvolvimento e releases

- **main:** versão estável 1.3.0.
- **legado:** main anterior, versão 1.2.0.
- **teste-biblioteca:** histórico da versão de testes aprovada.

O workflow Release desktop compila em Windows, Ubuntu 22.04 e macOS 15 Apple Silicon, testa os pacotes e publica quando todas as builds passam. Atualizar VERSION na main inicia uma publicação. O release inclui SHA256SUMS.txt para verificar integridade; os pacotes não possuem assinatura Authenticode ou notarização Apple.

A aparência foi inspirada no Renemya, com implementação própria. A fonte Fredoka inclui sua licença SIL OFL em `assets/fonts/OFL.txt`. PySide6/Qt têm licenças próprias. As imagens da corujinha foram criadas com auxílio de IA. O projeto ainda não declara uma licença de distribuição para seu código e arte.

Não envie bancos privados nas Issues. Links: [Repositório](https://github.com/cleitinhodev/prompchu), [Site](https://www.bugzinho.com/), [Doações](https://www.bugzinho.com/donate).
