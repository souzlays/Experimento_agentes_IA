# Experiment with AI agents

A organização dos experimentos é estabelecida na pasta `experimentos/`. O nome de um experimento é criado com base no dia e horário. O roteiro base de um experimento é definido na pasta `.template/`. Portanto, esse diretório é a referência para o método que cria experimentos.

## Preparando o ambiente

Após clonar o projeto, é necessário criar, ativar o venv e instalar as dependências:

- Linux
```bash
python -m venv .venv
. .venv/bin/activate
pip install -U pip setuptools
pip install poetry
poetry install
```

- Windows
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -U pip setuptools
pip install poetry
poetry install
```

## Criando um experimento (no Windows por Git Bash ou WSL)

Para tornar o script executável (habilitar apenas uma vez é suficiente):

```bash
chmod +x criar_experimento.sh
```

Para criar o experimento:

```bash
./criar_experimento.sh
```

## Como configurar o .env (no Windows por Git Bash ou WSL)

```bash
touch .env
```
> Pronto, basta adicionar as chaves de API que pretende utilizar e outros secrets (e.g. GROQ_API_KEY ...)

## Como instalar pacotes com poetry

```bash
poetry add <nome-do-pacote>
```