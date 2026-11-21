"""Deterministic, fictional examples. Never opens the user's database."""
import json
import sys
from datetime import datetime,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from storage import Store

TOPICS={
'Imagens':[
('Cidade flutuante','fantasia, cenário','Descreva uma cidade flutuante ao amanhecer, com jardins suspensos, pontes de pedra e nuvens iluminadas. Use composição panorâmica, luz dourada suave e sombras lilás. Inclua pequenos personagens para sugerir escala.'),
('Retrato de uma exploradora','personagem, retrato','Crie o retrato de uma exploradora adulta com casaco de viagem e mochila. Expressão curiosa, cenário de floresta desfocado, iluminação lateral natural e cores terrosas. Mantenha anatomia coerente e mãos proporcionais.'),
('Cafeteria na chuva','ambiente, aconchego','Crie uma pequena cafeteria vista da rua em uma noite chuvosa. Mostre reflexos das luzes nas poças, plantas na entrada e vapor saindo das xícaras. Use tons âmbar e azul, perspectiva natural e uma atmosfera acolhedora.'),
('Produto minimalista','produto, publicidade','Componha uma fotografia de estúdio de uma garrafa reutilizável sem marca sobre pedra clara. Fundo neutro, luz difusa, sombra suave e textura realista. Deixe espaço negativo para inserir uma legenda posteriormente.'),
('Biblioteca encantada','fantasia, interior','Ilustre uma biblioteca circular antiga, com estantes altas, escada de madeira e pequenas luzes mágicas. Enquadre a sala por uma porta aberta. Use detalhes legíveis, luz quente e uma sensação de descoberta.'),
('Jardim japonês','paisagem, natureza','Crie uma paisagem de jardim japonês no outono com lago, pedras e folhas avermelhadas. Organize o enquadramento em primeiro plano, plano médio e fundo. Use luz da manhã e reflexos sutis sem saturação excessiva.')],
'Vídeos':[
('Passeio pela floresta','natureza, câmera','Planeje um vídeo de 15 segundos atravessando uma trilha na floresta. Divida em três planos de cinco segundos e detalhe movimento da câmera, iluminação, som ambiente e transições suaves.'),
('Apresentação de produto','produto, roteiro','Escreva um roteiro de 30 segundos para apresentar uma garrafa reutilizável. Inclua abertura visual, três benefícios demonstráveis, planos de detalhe e encerramento. Evite promessas não comprovadas.'),
('Cidade ao entardecer','urbano, câmera','Descreva um plano contínuo de dez segundos em uma rua ao entardecer. A câmera avança lentamente na altura dos olhos. Especifique continuidade de luz, direção dos pedestres e sons urbanos discretos.'),
('Receita em um minuto','receita, tutorial','Monte um roteiro de um minuto para uma salada simples. Liste ingredientes, etapas, enquadramentos e textos curtos na tela. Use utensílios comuns e inclua uma alternativa de ingrediente.'),
('Antes e depois','transição, edição','Proponha cinco transições para comparar imagens de antes e depois. Para cada uma, descreva duração, movimento e como manter o mesmo alinhamento entre as imagens. Priorize clareza da transformação.'),
('Abertura de canal','identidade, animação','Crie três conceitos de abertura de cinco segundos para um canal educativo. Descreva composição, animação do título e som. As aberturas devem funcionar sem depender de marcas ou personagens existentes.')],
'Músicas':[
('Piano para estudar','instrumental, estudo','Descreva uma composição instrumental de piano para estudo, andamento lento e dinâmica suave. Defina instrumentos de apoio, estrutura e atmosfera. Evite mudanças bruscas de volume e melodias de músicas existentes.'),
('Tema de aventura','trilha, fantasia','Planeje uma trilha original de aventura com cordas, flauta e percussão leve. Divida em introdução, desenvolvimento e encerramento. Explique como a instrumentação sugere curiosidade e descoberta.'),
('Lo-fi na chuva','lo-fi, ambiente','Crie um briefing musical para uma faixa lo-fi original com chuva ambiente. Especifique andamento, timbres, progressão sugerida e transições. A chuva deve ficar abaixo dos instrumentos principais.'),
('Canção sobre recomeçar','letra, composição','Escreva uma letra original em português sobre recomeçar depois de um período difícil. Use duas estrofes, refrão e ponte, com imagens cotidianas e linguagem direta. Evite clichês e imitação de artistas.'),
('Som de menu','jogo, interface','Proponha uma trilha curta e cíclica para o menu de um jogo de exploração. Descreva duração, instrumentos, densidade e como fechar o ciclo sem uma quebra perceptível.'),
('Paisagem sonora','ambiente, natureza','Planeje uma paisagem sonora de floresta ao amanhecer. Liste camadas de pássaros, vento, água e passos distantes. Indique posição estéreo e variações para evitar repetição mecânica.')],
'Documentos':[
('Ata de reunião','reunião, organização','Crie um modelo de ata de reunião com data, participantes, pauta, decisões, responsáveis e prazos. Explique brevemente o que preencher em cada seção e inclua um exemplo fictício curto.'),
('Proposta de projeto','projeto, planejamento','Monte uma estrutura de proposta para desenvolver um aplicativo simples. Inclua problema, público, escopo, entregas, cronograma, riscos e critérios de aceite. Diferencie estimativas de compromissos firmados.'),
('Relatório de atividades','relatório, trabalho','Elabore um modelo de relatório semanal com atividades concluídas, pendências, dificuldades e próximos passos. Use linguagem profissional clara e uma tabela simples de acompanhamento.'),
('Manual rápido','manual, tutorial','Crie um guia de início rápido para um aplicativo de anotações. Cubra instalação, primeira nota, organização, busca e backup. Escreva passos numerados com ações curtas.'),
('Currículo inicial','carreira, currículo','Sugira uma estrutura de currículo para uma pessoa buscando seu primeiro emprego em tecnologia. Inclua estudos e projetos pessoais sem inventar experiências. Mostre exemplos de descrições objetivas.'),
('Checklist de entrega','checklist, qualidade','Prepare um checklist para entregar um projeto de software pequeno. Inclua funcionamento, documentação, dados de exemplo, instalação e limitações conhecidas. Agrupe por etapa e indique como conferir cada item.')],
'Programação':[
('Revisão de Python','python, revisão','Atue como revisor de código Python. Ao receber o código, identifique erros de lógica, tratamento de exceções e pontos de manutenção. Explique cada problema, proponha a menor correção adequada e sugira testes úteis.'),
('Consulta SQL','sql, banco de dados','Explique como consultar uma tabela de produtos usando SELECT, WHERE, ORDER BY e LIMIT. Crie uma tabela fictícia pequena e mostre consultas com os resultados esperados, inclusive valores nulos.'),
('Formulário acessível','html, acessibilidade','Crie um exemplo de formulário HTML acessível para contato, com rótulos, campos obrigatórios, validação e mensagens claras. Inclua CSS simples e explique navegação por teclado.'),
('Testes de função','testes, python','Mostre como testar uma função de cálculo de desconto em Python. Inclua casos normais, limites e entradas inválidas. Explique a regra de arredondamento e evite testes que só repetem o código da função.'),
('Organização de projeto','arquitetura, python','Proponha uma estrutura simples de pastas para um aplicativo Python com interface e SQLite. Separe responsabilidades e explique onde colocar validação, persistência e testes. Evite abstrações desnecessárias.'),
('Depuração guiada','debug, lógica','Ajude a investigar um erro passo a passo. Peça a mensagem completa, um exemplo mínimo e o resultado esperado. Formule hipóteses testáveis e explique o que cada verificação pode confirmar ou descartar.')],
'Escrita':[
('Cena de reencontro','ficção, diálogo','Escreva uma cena original de reencontro entre dois amigos após dez anos. Mostre a tensão por gestos e diálogo, sem explicar todos os sentimentos. Termine com uma decisão pequena, mas significativa.'),
('Mundo de fantasia','worldbuilding, fantasia','Crie três cidades fictícias para um mundo de fantasia. Para cada uma, descreva geografia, economia, costume local e um conflito cotidiano. Mostre relações comerciais e culturais entre elas.'),
('Personagem com conflito','personagem, narrativa','Crie um personagem adulto com objetivo claro, medo, habilidade e contradição interna. Dê exemplos de decisões que revelem esses traços. Evite resumir sua personalidade em adjetivos.'),
('Revisão de texto','revisão, clareza','Revise o texto que eu enviar preservando minha voz e intenção. Corrija gramática e repetições, sugira melhorias de clareza e explique apenas as alterações relevantes. Não acrescente fatos novos.'),
('Mistério curto','mistério, conto','Planeje um conto de mistério em uma pequena estação de trem. Inclua três pistas, duas interpretações enganosas e uma solução coerente. Garanta que o leitor tenha acesso às pistas necessárias.'),
('Diálogo natural','diálogo, roteiro','Escreva uma conversa entre colegas que discordam sobre um projeto. Dê a cada um uma preocupação legítima. Use subtexto, interrupções moderadas e uma conclusão que não resolva tudo imediatamente.')],
'Estudos':[
('Plano de estudo semanal','estudo, planejamento','Monte um plano semanal para estudar programação com uma hora por dia. Alterne explicação, prática e revisão. Inclua um projeto pequeno, pausas e uma forma simples de verificar progresso.'),
('Explicação com analogia','didática, lógica','Explique variáveis, condições e laços usando a analogia de um jogo de RPG. Depois apresente exemplos curtos em Python e exercícios com respostas comentadas.'),
('Perguntas de revisão','revisão, exercícios','Crie dez perguntas de revisão sobre introdução a banco de dados, com dificuldade crescente. Inclua respostas explicadas e exemplos de erros comuns. Diferencie tabela, registro, coluna e chave.'),
('Resumo estruturado','resumo, leitura','Quando eu enviar um texto, organize um resumo com ideia central, argumentos, exemplos e dúvidas. Diferencie o que o autor afirma das suas interpretações e não invente informações ausentes.'),
('Matemática cotidiana','matemática, porcentagem','Explique porcentagens usando descontos, aumentos e comparação de preços. Mostre o cálculo passo a passo e três exercícios. Destaque a diferença entre porcentagem e pontos percentuais.'),
('Revisão espaçada','memória, estudo','Crie um calendário de revisão espaçada para um assunto estudado hoje. Sugira atividades de recuperação ativa em cada revisão e uma forma de ajustar o intervalo conforme os erros.')],
'Marketing':[
('Apresentação de aplicativo','produto, divulgação','Escreva uma apresentação curta para um aplicativo que organiza notas localmente. Explique para quem serve, três usos práticos e como começar. Use linguagem humana e evite promessas exageradas.'),
('Calendário de conteúdo','conteúdo, planejamento','Monte um calendário de duas semanas para divulgar um projeto independente. Alterne bastidores, dicas, demonstrações e pedidos de feedback. Indique objetivo e formato de cada publicação.'),
('Descrição de tutorial','youtube, tutorial','Crie uma descrição de vídeo para um tutorial de organização de arquivos. Inclua um resumo claro, tópicos abordados e espaço identificado para links reais. Não invente capítulos ou endereços.'),
('Texto de lançamento','lançamento, software','Escreva um post de lançamento de software com problema atendido, recursos principais e convite para testar. Mantenha tom simples e transparente sobre limitações. Termine com espaço para o link oficial.'),
('Perguntas frequentes','faq, suporte','Prepare uma FAQ para um aplicativo local de produtividade. Cubra instalação, dados, backup, exportação e suporte. Quando faltar informação, indique que precisa ser confirmada.'),
('Pesquisa com usuários','pesquisa, produto','Crie oito perguntas abertas para entender como pessoas organizam seus prompts. Evite perguntas que induzam respostas. Inclua hábitos atuais, dificuldades, contexto de uso e critérios de escolha.')],
'Outros':[
('Organizar a semana','rotina, organização','Ajude a organizar uma semana com trabalho, estudos e descanso. Comece listando compromissos fixos, tarefas prioritárias e tempo disponível. Proponha um plano realista com margem para imprevistos.'),
('Ideias de projeto','ideias, criatividade','Sugira cinco projetos pequenos que resolvam problemas cotidianos. Para cada um, descreva público, função principal e uma versão mínima que possa ser demonstrada em uma semana.'),
('Comparar alternativas','decisão, análise','Ao receber duas alternativas, organize uma comparação por custo, esforço, benefícios e limitações. Separe fatos de suposições e destaque quais informações faltam para decidir.'),
('Checklist de viagem','viagem, checklist','Crie uma lista de preparação para uma viagem curta. Separe documentos, roupas, higiene, eletrônicos e tarefas antes de sair. Indique itens que dependem do destino e do meio de transporte.'),
('Organização de arquivos','arquivos, produtividade','Sugira uma estrutura de pastas para documentos pessoais e projetos. Defina uma convenção simples de nomes, rotina de backup e um processo para lidar com arquivos duplicados sem apagá-los automaticamente.'),
('Brainstorm de nomes','nomes, criatividade','Proponha vinte nomes curtos e pronunciáveis para um aplicativo de criatividade. Explique a ideia de cada nome. Não afirme que os nomes estão disponíveis ou livres de marcas sem pesquisa.')]
}

def generate():
    rows=[]
    for shelf,items in TOPICS.items():
        for name,tags,prompt in items:
            stamp=(datetime(2026,9,1,12)+timedelta(days=len(rows))).isoformat(timespec='seconds')
            rows.append(dict(name=name,tags=tags,genres='Geral',category=shelf,model='Livre',prompt=prompt,negative='',notes='Exemplo fictício. Adapte livremente ao seu objetivo.',favorite=len(rows)%11==0,shelf=shelf,created=stamp,updated=stamp))
    return rows
if __name__=='__main__':
    rows=generate();target=ROOT/'assets/demo-prompts.json'
    target.write_text(json.dumps(dict(format='banco-de-prompts',version=2,prompts=rows),ensure_ascii=False,indent=2),encoding='utf-8')
    destination=ROOT/'examples/prompts-demo.sqlite3';destination.parent.mkdir(exist_ok=True)
    if destination.exists():destination.unlink()
    store=Store(destination)
    with store.db:
        for row in rows:
            ident=store.save(row);store.db.execute('UPDATE prompts SET created=?,updated=? WHERE id=?',(row['created'],row['updated'],ident))
    store.db.close();print(f'{len(rows)} examples written.')
