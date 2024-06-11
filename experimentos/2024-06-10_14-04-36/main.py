from crewai import Agent, Task, Crew
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
import os
import time

search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool() 

current_path = os.path.dirname(os.path.abspath(__file__)) + "/results/"

# AGENTS
searcher = Agent(
    role="Senior News Researcher",
    goal="Research, analyze, and summarize the latest news based on the provided topic.",
    backstory="You are a seasoned researcher dedicated to providing comprehensive and detailed summaries of current news topics. "
              "Your task is to gather the most relevant and up-to-date information from credible sources, "
              "ensuring the audience receives accurate, insightful, and actionable summaries. "
              "If the content is in Portuguese, you should perform the search in English and provide the response in English."
              "You ALWAYS delegate the task to the Quality Checker to ensure the information that you search is accurate and reliable. until the Quality Checker approves the information."
              "You search other sources if the first one does not provide enough information."
              "You should search based on the current date and the topic provided.",
    allow_delegation=True, # true to allow delegation
    verbose=True,
)


quality_checker = Agent(
    role="Quality Checker",
    goal="Verify the accuracy and quality of the content.",
    backstory="You are responsible for ensuring the content is accurate, high-quality, and aligns with the provided topic: {topic}, and the current date. {current_date}. "
              "Your task is to review the content provided by the Senior News Researcher and classify it based on its technical depth and popularity. "
              "If you find any discrepancies or inconsistencies, you inform the Senior News Researcher to make the necessary corrections and conduct new searches to improve the content. "
              "You also evaluate whether the information is current and pertinent to the topic and provided date. "
              "You use english as the primary language for your responses."
              "You pass some informations that need to be included in the article to improve the quality of the content."
              "If the consensus is that the content is accurate and high-quality, you approve it for the next stage.",
    allow_delegation=False,
    tools=[search_tool, scrape_tool],
    verbose=True,
    output_file="quality_checker_output.txt",
)


classificator = Agent(
    role="Content Classifier",
    goal="Classify the content based on its technical depth and popularity.",
    backstory="You are tasked with categorizing the content based on its technical complexity and popularity. "
              "Your classification will help determine the appropriate platform for publishing the content, "
              "whether it's highly technical, tech-popular, or popular content. "
              "Your analysis will guide the subsequent agents in tailoring the content for the target audience and platform. "
              "You aim to provide valuable insights for effective content distribution and engagement.",
    allow_delegation=False,
    verbose=False,
)


linkedin_writer = Agent(
    role="LinkedIn Content Writer",
    goal="Craft a professional and engaging LinkedIn post based on the provided content.",
    backstory="You are a skilled writer specializing in creating compelling and professional content for LinkedIn. "
              "Your task is to transform the provided content into a concise and engaging LinkedIn post that resonates with a professional audience. "
              "You should maintain a formal tone and focus on delivering valuable insights and perspectives. "
              "Your writing should encourage discussion and interaction among LinkedIn users.",
    allow_delegation=False,
    verbose=False,
)


tweet_writer = Agent(
    role="Tweet Content Writer",
    goal="Compose a concise and engaging tweet based on the provided content.",
    backstory="You are a social media expert with a talent for crafting engaging and impactful tweets. "
              "Your task is to distill the key points of the provided content into a concise and compelling tweet that captures the audience's attention. "
              "You should leverage hashtags and engaging language to maximize reach and engagement. "
              "Your tweet should spark curiosity and encourage users to read the full content.",
    allow_delegation=False,
    verbose=False,
)


# TASKS
search_task = Task(
    description="Search the web in English, analyze, and summarize the latest news based on the provided topic: {topic} and the current date: {current_date}.",
    expected_output="A detailed summary of the latest news related to the provided topic in Markdown format.",
    agent=searcher,
    tools=[search_tool, scrape_tool],
    output_file=current_path + "search_result.md",
)


classification_task = Task(
    description="Classify the content based on its technical depth and popularity.",
    expected_output="A classification of the content as 'Tech', 'Tech-Popular', or 'Popular'. Provide a way writters can use this classification to create better content for segmented audiences.",
    agent=classificator,
    output_file=current_path + "classification_result.md"
)


linkedin_post_task = Task(
    description="Craft a professional and engaging LinkedIn post based on the provided content.",
    expected_output="A well-written LinkedIn post tailored for a professional audience. Markdown format. based on the provided content adn classification. Use classification to tailor the content.",
    agent=linkedin_writer,
    context=[search_task, classification_task],
    output_file=current_path +"content_linkedin.md",
    async_execution=False
)


tweet_task = Task(
    description="Compose a concise and engaging tweet based on the provided content with emojis.",
    expected_output="A compelling tweet that captures the essence of the content and encourages engagement. based on the provided content and classification. Use classification to tailor the content.",
    agent=tweet_writer,
    context=[search_task, classification_task],
    output_file=current_path +"content_tweet.md",
    async_execution=False
)


crew = Crew(
    agents=[searcher, quality_checker, classificator, linkedin_writer, tweet_writer],
    #tasks=[search_task, quality_check_task, classification_task, linkedin_post_task, tweet_task],
    tasks=[search_task, classification_task, linkedin_post_task, tweet_task],
    verbose=2,
    memory=False #precissa openai
)

current_date = time.strftime("%Y-%m-%d")
inputs = {"topic": """Suposto vazamento massivo de documentos sigilosos do Google pode explicar como seu motor de buscas realmente funciona: mais de 2.500 páginas detalham como os algoritmos da plataforma classificam os resultados e desmentem algumas das informações repassadas pela empresa ao longo dos anos, como o uso de dados do Chrome para a detecção de padrões de navegação e sugestões em buscas. O Google ainda não forneceu comentários a respeito da veracidade do vazamento. As informações são do site The Verge.""", "current_date":
current_date}

result = crew.kickoff(inputs=inputs)