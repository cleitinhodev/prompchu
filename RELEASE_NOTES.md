# Prompchu 1.3.0 — Estável

A versão aprovada da Biblioteca e dos bancos independentes agora é a principal. A main anterior (1.2.0) foi preservada na branch `legado`. As versões beta anteriores permanecem no histórico.

## Novidades

- Biblioteca em cartões, miniaturas JPG/PNG, datas, tags e filtros combináveis.
- Prateleiras padrão e criação de prateleiras personalizadas, persistentes mesmo vazias.
- Criar e abrir bancos independentes na mesma janela, lembrando o último banco utilizado.
- União de dois bancos em um terceiro, sem apagar os originais; preserva datas, miniaturas e prateleiras vazias.
- Exportação de um prompt selecionado em JSON e importação no banco escolhido.
- Backup completo SQLite e gravação após salvar cada alteração.
- Dez idiomas, neon e animações opcionais, identidade da corujinha e janela Sobre.

## Bancos úteis — download opcional

`Prompchu-Bancos-Uteis-1.3.0.zip` contém uma pasta com **9 bancos e 540 modelos de prompts em português**. Áreas: Imagens, Vídeos, Documentos, Programação, Músicas, Estudos, Marketing, Escrita e Produtividade.

Cada área inclui 20 tarefas com versões para **Criar, Revisar e Adaptar** (60 registros por banco). Os campos entre colchetes permitem reutilizar os textos. O pacote traz instruções e catálogo. Não contém miniaturas.

Extraia o ZIP e use **Arquivo → Abrir banco**. Os exemplos não são instalados, abertos ou importados automaticamente. O programa não executa prompts: copie o texto para a ferramenta desejada. Revise o resultado gerado.

## Downloads do aplicativo

- **Windows 10/11 AMD64:** extraia o ZIP inteiro e execute `Prompchu/Prompchu.exe`, mantendo todos os arquivos juntos.
- **Linux x86_64:** extraia o tar.gz e execute `./Prompchu/Prompchu`. Build Ubuntu 22.04; requer ambiente gráfico e bibliotecas Qt/X11/OpenGL. Não é AppImage.
- **macOS Apple Silicon:** extraia e abra `Prompchu.app`. Alvo macOS 15+; não é build Intel.

Python incluído. Sem certificado Authenticode ou notarização Apple. `SHA256SUMS.txt` permite verificar integridade dos downloads; não é assinatura digital de autoria.

## Dados e compatibilidade

Faça backup antes de atualizar seu banco. A migração adiciona prateleiras e miniaturas sem apagar prompts. Os dados continuam locais, sem envio automático à internet. JSON v1 e v2 são aceitos; a exportação usa v2, que não é importado pela versão 1.2.0. A importação cria novas datas de adição; a união dos bancos preserva as datas originais.

A interface e os pacotes passam por testes automatizados em Windows, Linux e macOS. A promoção para estável incorpora a versão testada e aprovada pelo usuário.
