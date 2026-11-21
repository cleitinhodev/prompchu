## Bancos independentes — 1.3.0-beta.2

Pré-release da branch `teste-biblioteca`. A main permanece inalterada.

- **Criar banco** e **Abrir banco**: coleções independentes, com seus próprios prompts, tags e categorias.
- A troca salva as alterações do banco anterior e acontece na mesma janela. O nome do banco fica visível e o último arquivo aberto é lembrado.
- **Juntar bancos** reúne dois bancos em um terceiro arquivo novo, sem modificar os originais. Preserva datas, favoritos, miniaturas e prompts repetidos.
- **Backup do banco** mantém a cópia completa SQLite.
- **Importar prompt / Exportar prompt**: transferência JSON; a exportação agora inclui somente o prompt selecionado, com metadados e miniatura.
- Removido **Abrir demonstração**. Para experimentar os 54 exemplos, baixe `prompts-demo.sqlite3` e abra por **Arquivo → Abrir banco**. Alterações nele são salvas normalmente.
- Biblioteca com cartões, prateleiras, filtros e paginação preservada.

### Downloads

- Windows 10/11 AMD64: extraia o ZIP inteiro e abra `Prompchu/Prompchu.exe`.
- Linux x86_64: extraia o tar.gz e execute `./Prompchu/Prompchu`. Compilado no Ubuntu 22.04, requer ambiente gráfico e bibliotecas Qt/X11/OpenGL de sistema. Não é AppImage.
- macOS Apple Silicon: extraia e abra `Prompchu.app`; alvo macOS 15+. Não é para Intel.

Python já está incluído. Builds sem certificado Authenticode ou notarização Apple.

### Dados e compatibilidade

Faça **Arquivo → Backup do banco** antes de testar com sua coleção. O esquema recebe uma coluna de prateleira e uma tabela de miniaturas, sem apagar os prompts existentes. O backup SQLite inclui as imagens. O programa continua local, sem envio dos prompts ou miniaturas à internet.

A importação aceita JSON v1 e v2. As novas exportações usam v2 e incluem prateleira e miniatura; o Prompchu 1.2.0 não importa esse formato novo. A data de adição em importações corresponde à data da importação. O banco demo conserva as datas fictícias dos exemplos.

`SHA256SUMS.txt` permite comparar a integridade de cada download; não é assinatura digital de autoria. Todos os pacotes passam por testes automatizados e abertura offscreen. A validação manual nos desktops ainda é importante nesta beta.
