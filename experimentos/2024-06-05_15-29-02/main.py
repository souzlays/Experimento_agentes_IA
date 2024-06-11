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
    goal="Gerar resumos precisos e concisos de cada página do arquivo PDF."
    "Utilizar o texto extraído das páginas do arquivo PDF para fazer um breve resumo de cada página."
    "Resumir cada página do arquivo PDF de forma clara e concisa."
    "Não exibir o conteúdo completo da página, mas sim destacar os pontos-chave e as informações essenciais."
    "Gerar texto em português BR.",
    backstory="Como um agente resumidor de páginas, sua missão é "
            "examinar cuidadosamente o texto de cada página dos arquivos PDF."
            "e gerar resumos claros e informativos."
            "facilite a compreensão e a revisão dos documentos.",
    allow_delegation=True,
    verbose=False,
    
)

agente_de_resumo_global = Agent(
    llm=llm,
    role="Resumidor Global",
    goal="Gerar um resumo global conciso e preciso a partir dos resumos das páginas de arquivos PDF. Gerar texto em português BR."
    "Não exibir o conteúdo completo da página, mas sim destacar os pontos-chave e as informações essenciais.",
    backstory="Como um agente de resumo global, sua missão é"
            "compilar os resumos individuais de cada página dos arquivos PDF "
            "e sintetizá-los em um único resumo global que captura a essência "
            "de todo o documento." 
            "assegura que o resumo global seja coerente"
            "informativo e útil para a compreensão rápida do conteúdo do PDF.",
    allow_delegation=False,
    verbose=True,
    
)

agente_revisor_do_resumo_global = Agent(
    llm=llm,    
    role="Revisor de Resumos",
    goal="Garantir que os resumos globais atendam aos critérios de qualidade especificados."
    "Não exibir o conteúdo do arquivo, exibir apenas a revisão"
    "Gerar texto em português BR.",
    backstory="Como um agente revisor de resumos, sua missão é "
            "examinar os resumos globais gerados para que atendam aos padrões "
            "de qualidade especificados. Utilizando sua atenção aos detalhes e conhecimentos "
            "em revisão, você assegura que os resumos sejam coerentes, precisos e informativos, "
            "facilitando a compreensão dos documentos resumidos.",
    allow_delegation=False,
    verbose=True
)

## Tarefas
tarefa_resumo_paginas = Task(
    description=(
        "Resuma o texto: {texto_paginas}"
        "Utilize técnicas de resumo de texto para gerar "
        "resumos concisos, porém informativos. "
        "Certifique-se de capturar com precisão os pontos-chave, "
        "ideias principais e detalhes importantes. "
        "Os resumos devem ser claros, coerentes "
        "e fácil de entender para as partes interessadas "
        "que podem não ter tempo para ler as páginas inteiras."
    ),
    expected_output="Um resumo bem elaborado das páginas"
        "destacando os principais pontos, "
        "descobertas-chave e informações essenciais. "
        "Os resumos devem fornecer uma visão geral abrangente "
        "ao mesmo tempo que serão sucintos e de fácil compreensão.",
    agent=agente_resumidor_por_pagina,
    
)

tarefa_de_aprimoramento_de_resumo = Task(
    description=(
        "Aprimore os resumos existentes das páginas"
        "Analise os resumos atuais e os documentos originais"
        "para identificar áreas que podem ser expandidas, clarificadas ou melhoradas. "
        "Adicione detalhes relevantes que possam ter sido omitidos nos resumos iniciais. "
        "Garanta que os resumos aprimorados mantenha sua concisão e clareza, "
        "mas forneça uma cobertura mais abrangente das informações essenciais."
    ),
    expected_output="resumo aprimorado das páginas do documento "
        "que incorpora as melhorias identificadas. "
        "Os resumos aprimorados devem ser mais abrangentes e informativos do que o original, "
        "incluindo detalhes adicionais relevantes para uma compreensão completa do conteúdo.",
    agent=agente_resumidor_por_pagina,
)

tarefa_de_resumo_global = Task(
    description=(
        "Gerar um resumo geral a partir dos resumos do {texto_paginas}"
        "que contenha uma síntese abrangente e concisa do conteúdo. "
        "O resumo deve capturar os pontos-chave de todas as seções "
        "e páginas do documento, destacando as informações mais relevantes. "
        "Certifique-se de manter a coesão e a fluidez no resumo, "
        "mantendo uma estrutura lógica e organizada. "
        "O resumo deve ser claro e compreensível para os leitores, "
        "refletindo com precisão o conteúdo original do arquivo PDF."
    ),
    expected_output=(
        "Um resumo global do arquivo PDF, "
        "que condensa de forma eficaz as informações mais importantes "
        "de todas as seções e páginas. O resumo deve ser conciso, "
        "coeso e refletir com precisão o conteúdo original. "
        "Deve oferecer uma visão geral compreensível do documento "
        "e destacar os pontos-chave para os leitores."
    ),
    agent=agente_de_resumo_global,
)

tarefa_de_revisão_de_resumo_global = Task(
    description="O resumo precisa ter um título"
                "O resumo precisa ter uma introdução"
                "O resumo precisa ter uma conclusão"
                "O resumo precisa ter uma seção de referências",
    expected_output="Um resumo global revisado dos textos extraídos das páginas do arquivo PDF que incorpora"
        "todas as melhorias especificadas. O resumo deve incluir: "
        "Um título claro e descritivo que resuma o conteúdo do documento. "
        "Uma introdução que contextualize o leitor sobre o assunto abordado. "
        "Uma conclusão que recapitule os pontos-chave e forneça insights finais. "
        "Uma seção de referências que liste todas as fontes utilizadas no resumo, "
        "se necessário. "
        "O resumo revisado deve ser coeso, claro e atender aos requisitos "
        "estabelecidos para garantir sua eficácia na comunicação do conteúdo.",
    agent=agente_revisor_do_resumo_global,
)


### EQUIPE 
crew = Crew(
    agents=[agente_resumidor_por_pagina, agente_de_resumo_global, agente_revisor_do_resumo_global],
    tasks=[tarefa_resumo_paginas, tarefa_de_aprimoramento_de_resumo, tarefa_de_resumo_global, tarefa_de_revisão_de_resumo_global],
    verbose=1
)

inputs = {"texto_paginas": texto_paginas_str}

### INICIAR O FLUXO DE TRABALHO
result = crew.kickoff(inputs=inputs)
