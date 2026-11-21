## Biblioteca — versão de teste 1.3.0-beta.1

Esta versão foi construída da branch `teste-biblioteca`. A main e o release estável 1.2.0 permanecem disponíveis.

- Menu **Arquivo** para importar, exportar, fazer backup e abrir a demonstração.
- Nova **Biblioteca** ocupando a área central: cartões com título, tags, data de adição e miniatura.
- Prateleiras: Imagens, Vídeos, Músicas, Documentos, Programação, Escrita, Estudos, Marketing e Outros. É possível digitar novas prateleiras no editor.
- Busca em nome, conteúdo e metadados, filtro por múltiplas tags (todas devem estar presentes), categoria, gênero, favoritos e intervalo de datas. Ordenação por nome, criação e atualização.
- Clicar no cartão volta à tela inicial com o prompt aberto.
- Lista inicial em páginas de 100; biblioteca em páginas de 24. As buscas consultam todo o banco. O conteúdo completo só é carregado para o prompt selecionado.
- Miniaturas JPG/PNG pelo editor, com remoção e substituição. São reduzidas e guardadas no próprio SQLite; o arquivo original não precisa permanecer na mesma pasta.

### Experimentar sem misturar os dados

Use **Arquivo → Abrir demonstração**: abre outra janela com 54 prompts fictícios em um banco temporário independente. As alterações nessa demonstração não são permanentes; exporte ou faça backup se quiser guardá-las.

Também estão disponíveis `prompts-demo.json`, para importar opcionalmente no seu banco, e `prompts-demo.sqlite3`, banco de teste pronto. Reimportar o JSON cria cópias. Os exemplos são textos genéricos em português e podem ser adaptados livremente.

### Downloads

- Windows 10/11 AMD64: extraia o ZIP inteiro e abra `Prompchu/Prompchu.exe`.
- Linux x86_64: extraia o tar.gz e execute `./Prompchu/Prompchu`. Compilado no Ubuntu 22.04, requer ambiente gráfico e bibliotecas Qt/X11/OpenGL de sistema. Não é AppImage.
- macOS Apple Silicon: extraia e abra `Prompchu.app`; alvo macOS 15+. Não é para Intel.

Python já está incluído. Builds sem certificado Authenticode ou notarização Apple.

### Dados e compatibilidade

Faça **Arquivo → Backup do banco** antes de testar com sua coleção. O esquema recebe uma coluna de prateleira e uma tabela de miniaturas, sem apagar os prompts existentes. O backup SQLite inclui as imagens. O programa continua local, sem envio dos prompts ou miniaturas à internet.

A importação aceita JSON v1 e v2. As novas exportações usam v2 e incluem prateleira e miniatura; o Prompchu 1.2.0 não importa esse formato novo. A data de adição em importações corresponde à data da importação. O banco demo conserva as datas fictícias dos exemplos.

`SHA256SUMS.txt` permite comparar a integridade de cada download; não é assinatura digital de autoria. Todos os pacotes passam por testes automatizados e abertura offscreen. A validação manual nos desktops ainda é importante nesta beta.
