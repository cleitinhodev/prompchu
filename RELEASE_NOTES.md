Owl Studio agora é a versão principal do Prompchu! 🦉

Biblioteca de prompts local com busca, filtros, favoritos, edição, importação/exportação JSON e backup SQLite. Interface nas cores da corujinha, abas de leitura, dez idiomas de navegação e efeitos opcionais. O novo letreiro Fredoka apresenta pequenas falhas aleatórias de luz por letra. O botão Sobre reúne informações do programa e links para repositório, site e doações. Desligue Animações para deixá-lo estável; desligue Neon para remover o brilho.

## Downloads

- **Windows AMD64**: extraia o ZIP inteiro e abra `Prompchu/Prompchu.exe`. Windows 10/11 de 64 bits.
- **Linux x86_64**: extraia o `.tar.gz` e execute `./Prompchu/Prompchu`. Compilado em Ubuntu 22.04; requer desktop gráfico e bibliotecas de sistema Qt/X11/OpenGL. Não é AppImage. Python está incluído.
- **macOS arm64**: extraia o ZIP e abra `Prompchu.app`. Para Apple Silicon (M1 ou posterior), alvo macOS 14+. Não é uma build para Intel.

As builds não exigem instalar Python. Cada pacote passa por testes de banco/interface e teste automático de abertura do executável em modo offscreen. Esse teste não substitui a validação manual em cada desktop.

## Conferir o download

`SHA256SUMS.txt` contém o hash SHA-256 de cada pacote. Compare-o com o arquivo baixado:

Windows PowerShell: `Get-FileHash .\Prompchu-1.2.0-Windows-AMD64.zip -Algorithm SHA256`

Linux: `sha256sum -c SHA256SUMS.txt --ignore-missing`

macOS: `shasum -a 256 Prompchu-1.2.0-Darwin-arm64.zip`

O hash verifica a integridade em relação à lista publicada; não é uma assinatura digital que certifica o autor. Os executáveis não têm certificado Authenticode nem notarização Apple; o sistema pode exibir avisos de desenvolvedor não identificado.

## Dados existentes

O banco e o formato JSON continuam compatíveis. Faça um backup antes de atualizar. Não apague a pasta de dados `Bugzinho/BancoDePrompts`. Parte das mensagens técnicas e diálogos de importação/backup ainda aparece em português.
