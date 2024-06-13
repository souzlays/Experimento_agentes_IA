from crewai import Crew, Task, Agent
from crewai_tools import BaseTool
import os
from PyPDF2 import PdfReader
from langchain_groq import ChatGroq

### LLM
llm=ChatGroq(temperature=0,
             model_name="llama3-70b-8192",
             api_key=os.environ.get("GROQ_API_KEY"))


def extrair_texto_pdf(file_path: str):
    paginas_texto = []
    with open(file_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            paginas_texto.append(f"Texto da página {page_num + 1}: {page_text}")
    
    return paginas_texto

file_path = "/home/pge/lays/teste_basetools/artigo.pdf"
texto_paginas = extrair_texto_pdf(file_path)
texto_paginas_str = "".join(texto_paginas)


### AGENTS
agente_resumidor_por_pagina = Agent(
    llm=llm,
    role="Resumir textos",
    goal="Gerar resumos precisos e concisos de cada página do arquivo PDF.",
    backstory="Como agente resumidor de páginas, gerar resumos claros e informativos para facilitar a compreensão e revisão dos documentos."
    "Gerar um resumo por página do arquivo PDF",
    allow_delegation=False,
    verbose=False,
)

agente_de_resumo_global = Agent(
    llm=llm,
    role="Resumidor Global",
    goal="Gerar um resumo global conciso e preciso a partir dos resumos das páginas de arquivos PDF.",
    backstory="Como agente de resumo global, compilar resumos individuais das páginas em um único resumo que capture a essência do documento.",
    allow_delegation=False,
    verbose=True,
)


agente_revisor_do_resumo_global = Agent(
    llm=llm,    
    role="Revisor de Resumos",
    goal="Garantir que os resumos globais atendam aos critérios de qualidade especificados.",
    backstory="Como agente revisor de resumos, assegurar que os resumos sejam coerentes, precisos e informativos para facilitar a compreensão dos documentos resumidos.",
    allow_delegation=False,
    verbose=True
)

## Tarefas
tarefa_resumo_paginas = Task(
    description=(
        "Resumir o texto: {texto_paginas}"
        "Gerar um resumo de cada página do arquivo PDF"
        "Utilizar técnicas para gerar resumos concisos, porém informativos. "
        "Capturar com precisão pontos-chave, ideias principais e detalhes importantes. "
        "Os resumos devem ser claros, coerentes e fáceis de entender."
    ),
    expected_output="Resumo bem elaborado de cada página, destacando pontos principais, descobertas-chave e informações essenciais.",
    agent=agente_resumidor_por_pagina,
)

# tarefa_de_aprimoramento_de_resumo = Task(
#     description=(
#         "Aprimorar resumos de cada página do arquivo. "
#         "Analisar e identificar áreas que podem ser expandidas, clarificadas ou melhoradas. "
#         "Adicionar detalhes relevantes para uma cobertura mais abrangente das informações."
#     ),
#     expected_output="Resumo aprimorado que incorpora melhorias identificadas, mais abrangente e informativo.",
#     agent=agente_resumidor_por_pagina,
# )


tarefa_de_resumo_global = Task(
    description=(
        "Gerar um resumo global a partir dos resumos de cada página do {texto_paginas}. "
        "Síntese abrangente e concisa, capturando pontos-chave de todas as seções e páginas."
    ),
    expected_output=(
        "Resumo global que condensa informações importantes de todas as seções e páginas do documento, "
        "coeso, claro e refletindo com precisão o conteúdo original."
    ),
    agent=agente_de_resumo_global,
)


tarefa_de_revisão_de_resumo_global = Task(
    description=(
        "Revisar resumo global para incluir título, introdução, conclusão e seção de referências."
    ),
    expected_output=(
        "Resumo revisado que incorpora todas as melhorias especificadas, "
        "com título claro, introdução contextualizada, conclusão com insights finais e seção de referências."
    ),
    agent=agente_revisor_do_resumo_global,
)


### EQUIPE 
crew = Crew(
    agents=[agente_resumidor_por_pagina, agente_de_resumo_global, agente_revisor_do_resumo_global],
    tasks=[tarefa_resumo_paginas, tarefa_de_resumo_global, tarefa_de_revisão_de_resumo_global],
    verbose=1
)

inputs = {"texto_paginas": texto_paginas_str}

### INICIAR O FLUXO DE TRABALHO
result = crew.kickoff(inputs=inputs)
