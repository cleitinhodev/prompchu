## Prateleiras personalizadas — 1.3.0-beta.3

Pré-release da branch `teste-biblioteca`; main preservada.

- Botão **Criar prateleira** no topo da lista à esquerda da Biblioteca.
- Janela para nomear e salvar; nomes vazios, repetidos ou com mais de 80 caracteres são recusados.
- Prateleiras ficam no banco aberto e permanecem disponíveis mesmo vazias.
- Disponíveis no cadastro/edição e nos filtros da Biblioteca.
- Backup e união dos bancos preservam também as prateleiras vazias.

### Downloads

- Windows 10/11 AMD64: extraia o ZIP inteiro e abra `Prompchu/Prompchu.exe`.
- Linux x86_64: extraia o tar.gz e execute `./Prompchu/Prompchu`. Compilado no Ubuntu 22.04, requer ambiente gráfico e bibliotecas Qt/X11/OpenGL de sistema. Não é AppImage.
- macOS Apple Silicon: extraia e abra `Prompchu.app`; alvo macOS 15+. Não é para Intel.

Python já está incluído. Builds sem certificado Authenticode ou notarização Apple.

### Dados e compatibilidade

Faça **Arquivo → Backup do banco** antes de testar com sua coleção. O esquema recebe uma coluna de prateleira e uma tabela de miniaturas, sem apagar os prompts existentes. O backup SQLite inclui as imagens. O programa continua local, sem envio dos prompts ou miniaturas à internet.

A importação aceita JSON v1 e v2. As novas exportações usam v2 e incluem prateleira e miniatura; o Prompchu 1.2.0 não importa esse formato novo. A data de adição em importações corresponde à data da importação. O banco demo conserva as datas fictícias dos exemplos.

`SHA256SUMS.txt` permite comparar a integridade de cada download; não é assinatura digital de autoria. Todos os pacotes passam por testes automatizados e abertura offscreen. A validação manual nos desktops ainda é importante nesta beta.
