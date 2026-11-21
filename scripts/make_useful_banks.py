"""Build optional, reusable Portuguese prompt collections; never load user data."""
import sys,json,zipfile,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from storage import Store
from databases import read_database
# Each task has its own concrete deliverable; modes target different work stages.
AREAS={
'Imagens':('01_imagens', '''Fotografia de produto|Crie uma fotografia comercial de [PRODUTO] com materiais fiéis, fundo [FUNDO], luz [LUZ] e espaço para composição em [FORMATO].
Retrato profissional|Crie um retrato de [PESSOA/PERSONAGEM], expressão [EXPRESSÃO], enquadramento [PLANO], fundo discreto e iluminação coerente.
Cenário de jogo|Desenvolva um cenário de [AMBIENTE] para [GÊNERO DE JOGO], com áreas de navegação legíveis e pontos de interesse bem separados.
Personagem completo|Desenhe [PERSONAGEM], corpo inteiro sem cortes, com roupa [ROUPA], pose [POSE] e silhueta reconhecível.
Folha de personagem|Prepare vistas frontal, lateral e traseira de [PERSONAGEM], mantendo proporções, roupa e cores consistentes entre as vistas.
Ícone de aplicativo|Desenvolva um ícone para [APLICATIVO], usando [SÍMBOLO] e [PALETA], reconhecível em tamanho pequeno e sem detalhes excessivos.
Padrão repetível|Crie uma textura contínua de [ELEMENTOS], com repetição sem emendas visíveis, escala uniforme e distribuição equilibrada.
Capa de livro|Crie a arte de capa para [TEMA DO LIVRO], com foco em [ELEMENTO] e espaço reservado para título e autor adicionados depois.
Miniatura de vídeo|Crie uma composição para miniatura sobre [TEMA], com um foco principal, contraste claro e leitura em tela pequena.
Cartaz de evento|Crie a arte-base de um cartaz de [EVENTO], respeitando [IDENTIDADE] e reservando áreas limpas para data e local.
Ilustração editorial|Ilustre a ideia [IDEIA], usando uma metáfora visual compreensível para [PÚBLICO], sem depender de texto na imagem.
Diagrama ilustrado|Planeje uma ilustração explicativa de [PROCESSO], com etapas identificáveis e setas claras; forneça as legendas separadas para revisão.
Arquitetura interior|Visualize [CÔMODO] com estilo [ESTILO], materiais [MATERIAIS] e circulação plausível, respeitando as medidas fornecidas.
Paisagem natural|Crie [PAISAGEM] em [ESTAÇÃO], com profundidade entre primeiro plano e fundo, clima [CLIMA] e iluminação consistente.
Arte para adesivo|Desenhe [TEMA] com contorno fechado, silhueta simples e separação clara do fundo, adequado para um adesivo.
Estampa de camiseta|Crie uma estampa de [TEMA] com [NÚMERO] cores, formas legíveis e composição que funcione na área [ÁREA DE IMPRESSÃO].
Relevo ornamental|Desenvolva uma referência visual de baixo-relevo de [TEMA], com planos de profundidade claros e detalhes compatíveis com [TAMANHO].
Storyboard visual|Planeje [NÚMERO] quadros para [CENA], mantendo personagens e cenário consistentes e indicando ação e enquadramento.
Restauração de foto|A partir da foto anexada, restaure danos e contraste preservando identidade, textura e detalhes originais, sem inventar elementos ausentes.
Mockup de embalagem|Crie um mockup de [EMBALAGEM] para [PRODUTO], respeitando dimensões e arte fornecidas, com iluminação de estúdio.'''),
'Vídeos':('02_videos','''Roteiro de tutorial|Escreva um roteiro que ensine [TAREFA] a [PÚBLICO], mostrando pré-requisitos, etapas, demonstração e resultado verificável.
Vídeo curto educativo|Prepare um vídeo de [DURAÇÃO] sobre [TEMA], com gancho honesto, uma ideia central, exemplo e conclusão prática.
Demonstração de aplicativo|Planeje uma gravação de tela de [APLICATIVO], mostrando o problema, o fluxo principal e o resultado sem expor dados pessoais.
Vídeo de produto|Crie um roteiro de apresentação de [PRODUTO], demonstrando usos reais e limitações sem prometer resultados não comprovados.
Entrevista|Organize perguntas para entrevistar [PERFIL] sobre [TEMA], com abertura, aprofundamento, perguntas de acompanhamento e encerramento.
Documentário curto|Estruture um documentário sobre [TEMA], separando fatos confirmados, hipóteses, fontes necessárias e imagens de apoio.
Vídeo institucional|Planeje um vídeo de [ORGANIZAÇÃO] para [PÚBLICO], mostrando propósito, atividades e evidências fornecidas.
Roteiro de animação|Escreva uma cena animada sobre [SITUAÇÃO], com ações visuais, falas curtas, ritmo e transições realizáveis.
Lista de planos|Converta [ROTEIRO] em lista de planos com duração estimada, enquadramento, movimento, ação e áudio.
Plano de filmagem|Organize a gravação de [PROJETO] por locação, equipamento, pessoas, horários e dependências, considerando [RESTRIÇÕES].
B-roll|Sugira imagens de apoio para [NARRAÇÃO], ligando cada trecho a uma ação visual específica e viável de filmar.
Narração|Escreva uma narração sobre [TEMA] para [DURAÇÃO], com frases naturais para fala e pausas marcadas.
Legendas|Revise [TRANSCRIÇÃO] para legendas, preservando sentido e nomes, segmentando por unidades de leitura e sem inventar timestamps.
Descrição acessível|Elabore uma descrição das informações visuais relevantes de [CENA] sem repetir desnecessariamente o áudio.
Transições de edição|Proponha transições entre os trechos de [ROTEIRO], justificando como cada corte mantém continuidade e ritmo.
Vídeo sem rosto|Planeje um vídeo sobre [TEMA] usando narração, gráficos e gravações de tela, com referências de recursos a produzir.
Vídeo de comparação|Compare [OPÇÕES] em roteiro usando [CRITÉRIOS] e apenas os dados fornecidos, declarando lacunas.
Abertura e encerramento|Escreva três aberturas e três encerramentos para [VÍDEO], evitando clickbait e conectando a promessa ao conteúdo.
Reaproveitamento de vídeo|Transforme [TRANSCRIÇÃO LONGA] em propostas de cortes independentes, cada um com contexto, ideia central e fechamento.
Prompt de geração de vídeo|Descreva um plano de [CENA] com sujeito, ação, duração, movimento de câmera, luz e continuidade, evitando ações incompatíveis.'''),
'Documentos':('03_documentos','''Resumo executivo|Resuma [MATERIAL] para [DECISOR], destacando objetivo, fatos, decisão necessária, riscos e próximos passos.
Ata de reunião|Converta [ANOTAÇÕES] em ata com decisões, pendências, responsáveis e prazos; marque informações ausentes em vez de inventá-las.
Procedimento operacional|Documente [PROCESSO] com objetivo, pré-requisitos, etapas, critérios de conclusão e tratamento de exceções.
Relatório de progresso|Elabore um relatório de [PROJETO] com entregas concluídas, trabalho em andamento, bloqueios e próximos marcos.
Proposta de projeto|Estruture uma proposta para [OBJETIVO], com escopo, entregas, exclusões, dependências e critérios de aceitação.
Briefing|Monte um briefing para [TRABALHO], cobrindo objetivo, público, referências, restrições, materiais necessários e aprovação.
Checklist|Crie uma lista de verificação para [TAREFA], em ordem de execução, com critérios observáveis e itens obrigatórios separados dos opcionais.
Guia de uso|Escreva um guia de [FERRAMENTA] para [PÚBLICO], com instalação, primeiro uso, exemplos e resolução dos problemas informados.
FAQ|Crie perguntas frequentes sobre [SERVIÇO] usando apenas [INFORMAÇÕES], com respostas diretas e indicação das lacunas.
E-mail profissional|Redija um e-mail para [DESTINATÁRIO] com [OBJETIVO], contexto suficiente e pedido claro, em tom [TOM].
Comunicado de mudança|Explique a alteração [MUDANÇA], quem é afetado, quando acontece, ações necessárias e canal de suporte.
Plano de ação|Transforme [OBJETIVO] em ações com responsável sugerido, prazo proposto, dependência e evidência de conclusão.
Registro de decisões|Documente a decisão [DECISÃO], contexto, alternativas, critérios, justificativa e condições para revisão.
Especificação de requisitos|Organize [NECESSIDADE] em requisitos funcionais e não funcionais verificáveis, com prioridades e critérios de aceitação.
Relatório de incidente|Organize [FATOS] em linha do tempo, impacto, medidas tomadas, causas confirmadas e investigação pendente, sem atribuir culpa sem evidência.
Plano de testes|Prepare um plano para validar [SISTEMA], com escopo, cenários, entradas, resultados esperados e critérios de saída.
Glossário|Extraia os termos técnicos de [TEXTO] e defina cada um no contexto, com exemplo curto e ambiguidades sinalizadas.
Modelo de formulário|Desenhe um formulário para [FINALIDADE] com apenas os campos necessários, exemplos de preenchimento e validações claras.
Apresentação|Estruture [TEMA] em [NÚMERO] slides, com uma ideia central por slide, apoio visual sugerido e notas do apresentador.
Relatório comparativo|Compare [ALTERNATIVAS] segundo [CRITÉRIOS], distinguindo fatos, avaliações e informações ainda necessárias.'''),
'Programação':('04_programacao','''Investigar erro|Analise [ERRO], [CÓDIGO] e [AMBIENTE]; proponha causas ordenadas por evidência, passos de reprodução e correção mínima.
Revisar código|Revise [CÓDIGO] quanto a correção, legibilidade e casos extremos; explique cada achado e evite mudanças sem benefício concreto.
Refatorar função|Refatore [FUNÇÃO] em [LINGUAGEM] preservando comportamento e API pública; explique os ganhos e casos a testar.
Criar testes|Escreva testes para [COMPORTAMENTO] com casos normais, limites e falhas, verificando resultados observáveis sem espelhar a implementação.
Documentar API|Documente [ENDPOINTS] com entradas, saídas, autenticação existente, erros e exemplos consistentes com o código fornecido.
Consulta SQL|Escreva uma consulta para [OBJETIVO] usando [ESQUEMA] e [DIALETO], explicando joins, duplicatas e tratamento de valores nulos.
Migração de dados|Planeje uma migração de [ESQUEMA ATUAL] para [ESQUEMA NOVO], com backup, validação, transação e estratégia de recuperação.
Paginação|Implemente paginação para [CONSULTA] com ordenação estável, limites e comportamento definido quando registros mudam entre páginas.
Validar entrada|Implemente validação de [DADOS] usando [REGRAS], com mensagens úteis e testes de dados incompletos ou inesperados.
Ler arquivo JSON|Implemente leitura de [FORMATO JSON], validando esquema, tamanho, tipos e erros sem sobrescrever os dados atuais em caso de falha.
Exportar CSV|Implemente exportação de [DADOS] em CSV com codificação e separadores explícitos, escapando campos e documentando compatibilidade.
Interface desktop|Planeje uma interface para [TAREFA] em [FRAMEWORK], com estados vazio, carregando, sucesso e erro, acessível por teclado.
Processamento em segundo plano|Mova [TAREFA LENTA] para execução em segundo plano sem bloquear a interface, com cancelamento e comunicação segura de resultados.
Cache|Proponha cache para [OPERAÇÃO], definindo chave, invalidação, limite de memória e situações em que o cache não deve ser usado.
Logging|Adicione logs úteis a [FLUXO], distinguindo níveis e contexto, sem registrar segredos ou conteúdo privado desnecessário.
Configurações|Implemente persistência de [PREFERÊNCIAS], com valores padrão, validação, compatibilidade de versões e recuperação de arquivo inválido.
Empacotamento|Planeje a distribuição de [APLICATIVO] em [SISTEMA], incluindo recursos, dependências, teste de abertura e instruções de instalação.
Acessibilidade web|Revise [HTML/CSS] para teclado, foco, rótulos e contraste; proponha correções concretas sem afirmar conformidade não testada.
Diagnóstico de desempenho|Analise [MEDIÇÕES] e [CÓDIGO], identifique gargalos prováveis e proponha um experimento mensurável antes de otimizar.
Explicação de algoritmo|Explique [ALGORITMO] com exemplo executado passo a passo, casos extremos e custo de tempo e memória.'''),
'Músicas':('05_musicas','''Trilha de estudo|Descreva uma trilha instrumental para concentração em [ATIVIDADE], com dinâmica estável, instrumentação suave e sem mudanças bruscas.
Tema de personagem|Planeje um tema para [PERSONAGEM], relacionando personalidade e arco narrativo a ritmo, timbre e motivo melódico original.
Trilha de cenário|Descreva música ambiente para [CENÁRIO], com textura, andamento e espaço sonoro coerentes com [CLIMA].
Vinheta|Proponha uma vinheta original de [DURAÇÃO] para [PROJETO], com início reconhecível, desenvolvimento breve e final limpo.
Loop de jogo|Planeje um loop instrumental para [SITUAÇÃO DE JOGO], com transição contínua entre fim e início e baixa fadiga auditiva.
Trilha de suspense|Descreva uma trilha para [CENA] com tensão gradual, controle de dinâmica e pontos de silêncio intencionais.
Trilha alegre|Planeje uma faixa de clima positivo para [USO], com ritmo [RITMO], instrumentos [INSTRUMENTOS] e energia [NÍVEL].
Canção narrativa|Escreva letra original sobre [HISTÓRIA], com versos que avancem a narrativa e refrão ligado ao conflito central.
Refrão|Crie três refrões originais sobre [TEMA], com linguagem [TOM], métrica aproximada [MÉTRICA] e gancho memorável.
Estrutura de faixa|Organize [IDEIA MUSICAL] em seções com duração, função, evolução de energia e transições sugeridas.
Arranjo acústico|Proponha um arranjo acústico de [COMPOSIÇÃO PRÓPRIA], distribuindo melodia, harmonia e ritmo entre [INSTRUMENTOS].
Percussão|Descreva um padrão rítmico para [ESTILO] em [COMPASSO], indicando acentos, variações e espaço para a melodia.
Paisagem sonora|Planeje uma paisagem de sons de [AMBIENTE], com camadas próximas e distantes e evolução temporal discreta.
Trilha de apresentação|Descreva música de fundo para [APRESENTAÇÃO], preservando inteligibilidade da fala e evitando competir com a narração.
Trilha de relaxamento|Planeje uma faixa ambiente de [DURAÇÃO] com transições suaves, sem prometer efeitos terapêuticos.
Transição musical|Proponha uma passagem entre [SEÇÃO A] e [SEÇÃO B], considerando andamento, tonalidade e continuidade de energia.
Briefing para compositor|Escreva um briefing para música de [PROJETO], com função narrativa, duração, entregáveis e restrições de uso.
Mapa de intensidade|Divida [CENA/ROTEIRO] em momentos musicais, indicando intensidade, entradas, saídas e pontos onde o silêncio funciona melhor.
Descrição de instrumentos|Escolha instrumentos para representar [ATMOSFERA], explicando função e registro de cada um sem sobrecarregar o arranjo.
Revisão de letra|Avalie [LETRA PRÓPRIA] quanto a clareza, coerência, ritmo e clichês, propondo alternativas originais que preservem a intenção.'''),
'Estudos':('06_estudos','''Explicação inicial|Explique [CONCEITO] para [NÍVEL], começando pelos pré-requisitos e usando um exemplo concreto antes da definição formal.
Plano de estudo|Monte um plano para aprender [TEMA] em [TEMPO DISPONÍVEL], com etapas, exercícios e critérios de domínio.
Exercícios graduais|Crie exercícios sobre [TEMA] em dificuldade crescente, com soluções separadas e explicação dos erros mais prováveis.
Quiz diagnóstico|Prepare perguntas para identificar lacunas em [TEMA], associando cada resposta incorreta a um assunto para revisar.
Flashcards|Converta [MATERIAL] em cartões de pergunta e resposta com uma ideia por cartão, sem pistas involuntárias.
Resumo de capítulo|Resuma [CAPÍTULO] em conceitos centrais, relações, exemplos e pontos que exigem leitura mais cuidadosa.
Analogias|Explique [CONCEITO] por uma analogia cotidiana, indicando explicitamente onde a comparação deixa de funcionar.
Exemplo resolvido|Resolva [PROBLEMA] passo a passo, justificando cada transformação e verificando o resultado ao final.
Correção de exercício|Analise [MINHA RESOLUÇÃO], encontre a primeira etapa incorreta e dê uma pista antes de mostrar a solução completa.
Revisão espaçada|Planeje revisões de [CONTEÚDO] a partir de [DATA], com perguntas de recuperação ativa e ajuste segundo dificuldades.
Mapa conceitual|Organize [TEMA] em conceitos e relações nomeadas, distinguindo hierarquia, causa e exemplo.
Comparar conceitos|Compare [CONCEITO A] e [CONCEITO B] por definição, aplicação, limitações e exemplos que evidenciem a diferença.
Perguntas socráticas|Conduza uma sequência de perguntas sobre [TEMA], uma por vez, adaptando a dificuldade às minhas respostas.
Preparação de apresentação|Ajude a explicar [TEMA] em [DURAÇÃO], com sequência lógica, exemplos e possíveis perguntas do público.
Prática de idioma|Crie uma conversa em [IDIOMA] para [SITUAÇÃO], no nível [NÍVEL], corrigindo erros com explicações curtas.
Vocabulário contextual|Ensine palavras de [TEMA] em [IDIOMA], com frases naturais, significado no contexto e exercício de uso.
Leitura crítica|Analise [TEXTO] separando tese, evidências, pressupostos e conclusões que não são sustentadas pelo material.
Revisão de redação|Revise [REDAÇÃO] quanto a estrutura, argumentação e clareza, explicando as alterações para que eu aprenda.
Projeto prático|Proponha um projeto para praticar [HABILIDADE], com escopo realista, etapas, resultado esperado e critérios de avaliação.
Autoavaliação|Crie uma rubrica para avaliar meu domínio de [TEMA], com indicadores observáveis e próximos passos por nível.'''),
'Marketing':('07_marketing','''Descrição de produto|Escreva uma descrição de [PRODUTO] para [PÚBLICO], usando apenas características fornecidas e ligando cada benefício a uma função real.
Página de apresentação|Estruture uma página para [SERVIÇO], com proposta de valor, funcionamento, evidências disponíveis, dúvidas e chamada para ação.
Calendário editorial|Monte um calendário de [PERÍODO] para [MARCA], equilibrando conteúdo educativo, demonstrações e interação com [PÚBLICO].
Post educativo|Escreva um post que ensine [TEMA] a [PÚBLICO], com exemplo concreto e uma ação útil ao final.
Carrossel|Divida [TEMA] em [NÚMERO] telas de carrossel, com progressão clara, pouco texto e fechamento prático.
Anúncio|Crie três variações de anúncio para [OFERTA], respeitando [LIMITES] e evitando promessas, urgência ou depoimentos inventados.
Newsletter|Escreva uma newsletter sobre [NOVIDADES], priorizando relevância para [PÚBLICO] e uma chamada para ação clara.
Lançamento|Planeje a comunicação de [LANÇAMENTO], com mensagens antes, durante e depois e materiais necessários por canal.
Posicionamento|Organize o posicionamento de [MARCA] a partir de [DADOS], distinguindo público, problema, solução e diferencial demonstrável.
Tom de voz|Crie um guia de voz para [MARCA] com princípios, exemplos de frases e adaptações para suporte, anúncio e conteúdo educativo.
Pesquisa de público|Prepare perguntas abertas para entender [PÚBLICO] e [PROBLEMA], evitando induzir respostas ou pedir dados desnecessários.
FAQ comercial|Responda às dúvidas [DÚVIDAS] sobre [OFERTA] de forma transparente, incluindo limites e condições informadas.
Resposta a comentário|Elabore respostas a [COMENTÁRIOS] com tom [TOM], reconhecendo críticas e evitando prometer soluções não autorizadas.
Descrição de portfólio|Apresente [PROJETO] mostrando problema, participação, processo e resultado, sem atribuir métricas não fornecidas.
Biografia profissional|Escreva uma bio de [PERFIL] para [CANAL], com experiência verificável, foco de atuação e convite adequado.
Título e descrição de vídeo|Crie títulos e descrições para [VÍDEO] alinhados ao conteúdo real, sem exagerar a promessa.
Pesquisa de palavras-chave|Proponha hipóteses de termos de busca para [TEMA] agrupadas por intenção; não invente volumes ou dificuldade.
Teste de mensagem|Planeje um teste A/B entre [MENSAGENS], definindo hipótese, público, métrica e critérios de interpretação.
Reaproveitar conteúdo|Converta [CONTEÚDO] em formatos para [CANAIS], preservando os fatos e adaptando extensão e linguagem.
Apresentação de serviço|Crie uma apresentação curta de [SERVIÇO] com problema atendido, processo, entregáveis e próximo passo.'''),
'Escrita':('08_escrita','''Premissa de história|Crie uma premissa sobre [TEMA] com protagonista, objetivo, obstáculo e consequência de fracassar.
Perfil de personagem|Desenvolva [PERSONAGEM] com desejo, necessidade, contradição, histórico relevante e comportamento observável.
Arco narrativo|Planeje a transformação de [PERSONAGEM] entre [ESTADO INICIAL] e [ESTADO FINAL], com decisões que causem a mudança.
Construção de mundo|Desenvolva [MUNDO] a partir de [REGRA CENTRAL], mostrando efeitos na vida cotidiana, economia e conflitos.
Cena de diálogo|Escreva um diálogo entre [PERSONAGENS] com objetivos diferentes, subtexto e vozes distinguíveis.
Cena de ação|Escreva [CENA] com geografia clara, causa e efeito e consequências, evitando descrições confusas.
Descrição sensorial|Descreva [AMBIENTE] pelo ponto de vista de [PERSONAGEM], escolhendo detalhes sensoriais relevantes à emoção da cena.
Abertura de capítulo|Crie uma abertura para [CAPÍTULO] que situe o leitor, apresente tensão e se conecte ao contexto fornecido.
Encerramento de capítulo|Escreva um encerramento para [CAPÍTULO] que resolva algo local e abra uma questão coerente para a continuação.
Sinopse|Resuma [HISTÓRIA] em [EXTENSÃO], mantendo conflito central, progressão e desfecho quando solicitado.
Outline|Organize [IDEIA] em capítulos com objetivo de cena, conflito, mudança e ligação causal com o próximo capítulo.
Conflito|Proponha conflitos para [PERSONAGEM] que surjam de seus objetivos e valores, evitando obstáculos arbitrários.
Reviravolta|Planeje uma reviravolta para [TRAMA], com pistas anteriores e consequências que façam sentido ao reler.
Revisão de continuidade|Analise [TRECHOS] em busca de inconsistências de tempo, local, motivação e regras do mundo, citando evidências.
Revisão de ritmo|Avalie [CENA] quanto a repetição, exposição e progressão, propondo cortes e expansões justificados.
Voz narrativa|Reescreva [TRECHO] com voz [CARACTERÍSTICAS], preservando acontecimentos e evitando imitar um autor específico.
Poema original|Crie um poema sobre [TEMA], com imagens concretas, extensão [EXTENSÃO] e forma [FORMA].
Microconto|Escreva um microconto de até [LIMITE] palavras sobre [TEMA], com situação, mudança e final significativo.
Roteiro de visual novel|Transforme [CENA] em falas, narração, indicações visuais e escolhas com consequências claras.
Localização de texto|Adapte [TEXTO] para [IDIOMA/PÚBLICO], preservando intenção, humor e terminologia; explique escolhas ambíguas.'''),
'Produtividade':('09_produtividade','''Planejamento semanal|Organize [TAREFAS] em uma semana com [HORÁRIOS DISPONÍVEIS], reservando pausas e margem para imprevistos.
Priorização|Priorize [LISTA] por impacto, urgência e esforço, explicando os critérios e destacando dependências.
Dividir tarefa|Divida [TAREFA GRANDE] em passos que caibam em [TEMPO POR SESSÃO], cada um com resultado verificável.
Preparar reunião|Monte uma pauta para [REUNIÃO] com objetivo, decisões esperadas, materiais prévios e tempo por tópico.
Organizar notas|Agrupe [ANOTAÇÕES] por tema, extraindo ações e perguntas pendentes sem perder informações importantes.
Planejar projeto pessoal|Estruture [PROJETO] em uma primeira versão viável, etapas, recursos disponíveis e critérios para encerrar cada fase.
Checklist de viagem|Crie uma lista para [VIAGEM] considerando duração, atividades e bagagem; sinalize informações que precisam de confirmação.
Organizar arquivos|Proponha uma estrutura de pastas e nomes para [ARQUIVOS], com regras simples para busca, versões e arquivamento.
Revisão mensal|Prepare uma revisão de [MÊS] baseada em [REGISTROS], separando conquistas, dificuldades, aprendizados e ajustes.
Rotina de aprendizado|Encaixe [ESTUDO] em [ROTINA] com sessões realistas, revisão e critérios para reduzir carga quando necessário.
Plano de foco|Organize uma sessão de [DURAÇÃO] para concluir [TAREFA], com preparação, blocos de trabalho e definição de pronto.
Delegar tarefa|Escreva uma orientação para delegar [TAREFA], com contexto, entregável, limites, prazo e critério de revisão.
Inventário doméstico|Crie um modelo de inventário para [ITENS], com categoria, localização, quantidade e data de revisão.
Planejar evento|Organize [EVENTO] com [RECURSOS], incluindo cronograma, responsáveis, materiais e plano para imprevistos.
Registro de hábitos|Crie um registro simples de [HÁBITOS], definindo o que conta como realizado e uma revisão sem julgamentos.
Comparar ferramentas|Compare [FERRAMENTAS] usando [REQUISITOS] e informações fornecidas; separe necessidades essenciais de preferências.
Preparar feedback|Estruture feedback sobre [SITUAÇÃO] com observação concreta, impacto, escuta e pedido de mudança realizável.
Retrospectiva|Conduza uma retrospectiva de [PROJETO], identificando o que manter, mudar e experimentar com base em evidências.
Plano de organização|Crie um plano para organizar [ESPAÇO], dividindo triagem, agrupamento, armazenamento e manutenção em etapas curtas.
Registrar processo pessoal|Transforme [ROTINA] em um procedimento simples com gatilho, sequência, materiais e revisão periódica.''')}
MODES=[
('Criar','produção','Execute a tarefa a seguir. Antes, faça até três perguntas apenas se faltarem dados indispensáveis; caso contrário, declare as suposições e prossiga.','Entregue um resultado pronto para adaptar ao contexto, seguido de uma lista curta do que preciso confirmar.'),
('Revisar','revisão','Avalie [MATERIAL EXISTENTE] segundo o objetivo a seguir. Primeiro identifique problemas concretos; depois proponha uma versão revisada preservando o que já funciona.','Entregue: diagnóstico priorizado, versão revisada e justificativa das principais mudanças. Não invente defeitos para preencher a lista.'),
('Adaptar','adaptação','Adapte [MATERIAL EXISTENTE] para [NOVO PÚBLICO/CONTEXTO] e [NOVAS RESTRIÇÕES], seguindo o objetivo abaixo. Preserve as informações essenciais e explicite o que muda.','Entregue a versão adaptada e uma tabela curta com elemento original, alteração e motivo. Se houver incompatibilidade, proponha alternativas.')]

def build(destination=None):
    out=Path(destination or ROOT/'examples'/'bancos-uteis');out.mkdir(parents=True,exist_ok=True)
    counts={};texts=set()
    for area,(filename,raw) in AREAS.items():
        path=out/(filename+'.sqlite3')
        if path.exists():path.unlink()
        store=Store(path);tasks=raw.splitlines();assert len(tasks)==20
        with store.db:
            for title,goal in (line.split('|',1) for line in tasks):
                for mode,tag,intro,ending in MODES:
                    prompt=f'{intro}\n\nOBJETIVO\n{goal}\n\nCONTEXTO\nPúblico: [PÚBLICO]\nFinalidade: [FINALIDADE]\nMateriais ou referências disponíveis: [MATERIAIS]\nRestrições: [RESTRIÇÕES]\n\nENTREGA\n{ending}\nUse somente fatos fornecidos ou verificáveis; indique incertezas e não invente fontes, números ou resultados. Para tarefas visuais ou musicais, entregue um briefing ou prompt de geração se a ferramenta não produzir mídia.'
                    assert prompt not in texts;texts.add(prompt)
                    store.save(dict(name=f'{title} — {mode}',prompt=prompt,tags=f'{tag}, reutilizável, {area.lower()}',genres='Geral',category=title,model='Genérico',shelf=area,favorite=False,notes='Substitua os campos entre colchetes antes de usar. Estes modelos são pontos de partida; revise a resposta da ferramenta. As três versões têm objetivos distintos: criar, revisar e adaptar.'))
            store.db.execute("UPDATE prompts SET created='2026-11-21T12:00:00',updated='2026-11-21T12:00:00'")
        assert store.db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        assert store.page()[1]==60;store.db.close()
        check=read_database(path);check.close();counts[filename]=60
    guide='''# Bancos úteis para Prompchu 1.3.0

540 modelos em português: 9 bancos, com 20 tarefas por área e 3 versões por tarefa (Criar, Revisar e Adaptar). As versões atendem etapas diferentes do trabalho; não são 540 assuntos independentes.

## Como usar

1. Extraia este ZIP para uma pasta sua.
2. No Prompchu, use Arquivo → Abrir banco e escolha um arquivo .sqlite3.
3. Explore a Biblioteca, filtre por categoria ou pelas tags produção, revisão e adaptação.
4. Copie um prompt e substitua os campos [ENTRE COLCHETES]. Remova os campos que não se aplicam.
5. Cole na ferramenta de sua escolha. O Prompchu apenas organiza os textos; não executa os prompts nem gera mídia.

Os bancos são opcionais e não são carregados nem importados automaticamente pelo aplicativo. As alterações feitas neles são salvas normalmente. Para voltar ao original, extraia novamente o ZIP. Para levar um item ao seu banco, use Exportar prompt, abra seu banco e use Importar prompt. Juntar bancos combina coleções sem apagar os arquivos originais.

## Conteúdo

'''+''.join(f'- {area}: 60 prompts em {data[0]}.sqlite3\n' for area,data in AREAS.items())+'''
Sem dados pessoais, miniaturas ou textos de terceiros. Conteúdo genérico preparado para esta coleção, com campos editáveis. Datas representam a preparação do pacote. As respostas dependem da ferramenta utilizada e devem ser revisadas; os modelos não garantem qualidade, precisão ou resultados específicos.

## Sugestões

- Imagens: produto, personagem, cenário, ícone, textura, capa, estampa e relevo.
- Vídeos: tutorial, roteiro, entrevista, planos, narração, legendas e cortes.
- Documentos: atas, relatórios, procedimentos, briefings, requisitos e apresentações.
- Programação: depuração, testes, SQL, migração, paginação, interfaces e distribuição.
- Músicas: trilhas, loops, letras, arranjos, transições e paisagens sonoras.
- Estudos: explicações, exercícios, flashcards, planos e avaliação.
- Marketing: produto, páginas, posts, calendário, anúncios e portfólio.
- Escrita: personagens, cenas, mundos, continuidade, revisão e localização.
- Produtividade: planejamento, reuniões, notas, organização, eventos e retrospectivas.
'''
    (out/'LEIA-ME.md').write_text(guide,encoding='utf-8')
    (out/'catalogo.json').write_text(json.dumps({'version':1,'total':sum(counts.values()),'banks':counts},ensure_ascii=False,indent=2),encoding='utf-8')
    archive=out.parent/'Prompchu-Bancos-Uteis-1.3.0.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.iterdir()):z.write(p,'Bancos-Uteis/'+p.name)
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    print(f'{sum(counts.values())} prompts, {len(counts)} bancos: {archive}')
    return archive
if __name__=='__main__':build()
