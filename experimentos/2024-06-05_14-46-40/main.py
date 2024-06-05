from crewai import Crew, Task, Agent
import os
from langchain_groq import ChatGroq

### LLM
llm=ChatGroq(temperature=0,
             model_name="llama3-70b-8192",
             api_key=os.environ.get("GROQ_API_KEY"))


### AGENTS
planner = Agent(
    llm=llm,
    role="Planejador de Conteúdo",
    goal="Planejar conteúdo envolvente e factualmente preciso sobre {tópico}. Gerar texto em português BR.",
    backstory="Você está trabalhando no planejamento de um artigo de blog "
              "sobre o tópico: {tópico}."
              "Você coleta informações que ajudam o público a aprender algo "
              "e tomar decisões informadas. "
              "Seu trabalho é a base para "
              "o Escritor de Conteúdo escrever um artigo sobre este tópico.",
    allow_delegation=False,
    verbose=True
)

writer = Agent(
    llm=llm,
    role="Escritor de Conteúdo",
    goal="Escrever um artigo de opinião perspicaz e factualmente preciso"
         "sobre o tópico: {tópico}. Gerar texto em português BR.",
    backstory="Você está trabalhando em escrever "
              "um novo artigo de opinião sobre o tópico: {tópico}. "
              "Você baseia sua escrita no trabalho do "
              "Planejador de Conteúdo, que fornece um esboço "
              "e contexto relevante sobre o tópico. "
              "Você segue os principais objetivos e "
              "direção do esboço, "
              "como fornecido pelo Planejador de Conteúdo. "
              "Você também fornece insights objetivos e imparciais "
              "e os fundamenta com informações "
              "fornecidas pelo Planejador de Conteúdo. "
              "Você reconhece em seu artigo de opinião "
              "quando suas declarações são opiniões "
              "em vez de declarações objetivas.",
    allow_delegation=False,
    verbose=True
)

editor = Agent(
    llm=llm,    
    role="Editor",
    goal="Editar um post de blog dado para alinhar com "
         "o estilo de escrita da organização. Gerar texto em português BR.",
    backstory="Você é um editor que recebe um post de blog "
              "do Escritor de Conteúdo. "
              "Seu objetivo é revisar o post de blog "
              "para garantir que ele siga as melhores práticas jornalísticas, "
              "forneça pontos de vista equilibrados "
              "ao fornecer opiniões ou afirmações, "
              "e também evite tópicos ou opiniões controversas principais "
              "quando possível.",
    allow_delegation=False,
    verbose=True
)


### TAREFAS
plan = Task(
    description=(
        "1. Priorize as últimas tendências, principais players, "
            "e notícias importantes sobre {tópico}.\n"
        "2. Identifique o público-alvo, considerando "
            "seus interesses e pontos problemáticos.\n"
        "3. Desenvolva um esboço de conteúdo detalhado incluindo "
            "uma introdução, pontos-chave e uma chamada para ação.\n"
        "4. Inclua palavras-chave de SEO e dados ou fontes relevantes."
    ),
    expected_output="Um documento de plano de conteúdo abrangente "
        "com um esboço, análise de público-alvo, "
        "palavras-chave de SEO e recursos.",
    agent=planner,
)

write = Task(
    description=(
        "1. Use o plano de conteúdo para elaborar um post de blog envolvente "
            "sobre {tópico}.\n"
        "2. Incorpore palavras-chave de SEO naturalmente.\n"
  "3. As Seções/Subtítulos estão nomeadas corretamente "
            "de maneira envolvente.\n"
        "4. Garanta que o post esteja estruturado com uma "
            "introdução envolvente, corpo perspicaz, "
            "e uma conclusão resumida.\n"
        "5. Prova para erros gramaticais e "
            "alinhamento com a voz da marca.\n"
    ),
    expected_output="Um post de blog bem escrito "
        "em formato markdown, pronto para publicação, "
        "cada seção deve ter 2 ou 3 parágrafos.",
    agent=writer,
)

edit = Task(
    description=("Revisar o post de blog fornecido para "
                 "erros gramaticais e "
                 "alinhamento com a voz da marca."),
    expected_output="Um post de blog bem escrito em formato markdown, "
                    "pronto para publicação, "
                    "cada seção deve ter 2 ou 3 parágrafos e 64 caracteres",
    agent=editor
)


### EQUIPE 
crew = Crew(
    agents=[planner, writer, editor],
    tasks=[plan, write, edit],
    verbose=2
)

### INICIAR O FLUXO DE TRABALHO
result = crew.kickoff(inputs={"tópico": "Inteligência Artificial"})
