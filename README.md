Cloud Tasks API — CI/CD com GitHub Actions, Docker e AWS EC2API REST de gerenciamento de tarefas desenvolvida em Python (Flask) com banco de dados SQLite, conteinerizada com Docker e implantada de forma automatizada em uma instância AWS EC2 (Ubuntu 24.04 LTS) por meio de pipelines de Integração Contínua (CI) e Entrega Contínua (CD) com GitHub Actions e GitHub Container Registry (GHCR).Autor: Pedro Mello BorgesRepositório: github.com/Pedromb7/cloud-tasks-api-awsArquitetura da SoluçãoDesenvolvedor (Branch feature/...)
       │
       ▼  [Pull Request]
GitHub Actions (CI) ──► pytest + Docker Build
       │
       ▼  [Merge na main]
GitHub Container Registry (GHCR) ──► ghcr.io/pedromb7/cloud-tasks-api-aws:<SHA>
       │
       ▼  [Workflow CD]
AWS EC2 (Ubuntu 24.04 | sa-east-1)
  ├── GitHub Self-Hosted Runner (deploy local via SSH 127.0.0.1)
  ├── Container: cloud-tasks-api (Porta 80:8000 | usuário não-root)
  └── Volume Docker: cloud-tasks-data:/data (/data/tasks.db)
Endpoints da APIMétodoRotaDescriçãoRetorno esperadoGET/Informações gerais do serviço e rotas disponíveis200 OK (JSON)GET/healthVerificação de saúde da aplicação e conexão com o SQLite200 OK / 503GET/versionVersão atual da API em execução200 OK (JSON)GET/tasksLista todas as tarefas (aceita filtro ?done=true ou ?done=false)200 OK (JSON)POST/tasksCria uma nova tarefa ({"title": "..."}, máx. 120 caracteres)201 Created (JSON)PATCH/tasks/<id>Atualiza o status de conclusão ({"done": true|false})200 OK / 404DELETE/tasks/<id>Remove uma tarefa pelo ID204 No Content / 404Exemplos de Uso (curl)# Verificar saúde e versão
curl http://<IP_PUBLICO_EC2>/health
curl http://<IP_PUBLICO_EC2>/version

# Criar uma tarefa
curl -X POST http://<IP_PUBLICO_EC2>/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title":"Estudar Computacao em Nuvem"}'

# Listar tarefas (todas ou filtradas por status)
curl http://<IP_PUBLICO_EC2>/tasks
curl "http://<IP_PUBLICO_EC2>/tasks?done=false"

# Marcar tarefa como concluída
curl -X PATCH http://<IP_PUBLICO_EC2>/tasks/1 \
  -H 'Content-Type: application/json' \
  -d '{"done":true}'

# Excluir tarefa
curl -X DELETE http://<IP_PUBLICO_EC2>/tasks/1
Execução Local e TestesRodando com Pythonpython -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Executar testes automatizados
pytest -v

# Iniciar servidor de desenvolvimento
flask --app app.main run --port 8000
Rodando com Docker e Volume Persistentedocker build -t cloud-tasks-api:local .
docker run -d --name cloud-tasks-api \
  -p 8000:8000 \
  -v cloud-tasks-data:/data \
  -e DB_PATH=/data/tasks.db \
  cloud-tasks-api:local
Pipeline CI/CD e Segurança na AWSIntegração Contínua (.github/workflows/ci.yml): Executada em todo Pull Request e push na main. Roda a suíte de testes (pytest), valida o build da imagem Docker e, após o merge na main, publica a imagem imutável no GHCR tagueada com o hash SHA do commit.Entrega Contínua (.github/workflows/cd.yml): Acionada automaticamente após o sucesso da CI na main. Utiliza um Self-Hosted Runner configurado dentro da própria instância EC2 para executar o scripts/deploy.sh, realizando o pull da nova imagem e recriando o contêiner sem perda de dados.Segurança e Persistência:Security Group: Porta 22 (SSH) restrita exclusivamente ao IP do administrador (/32), bloqueando acesso aberto (0.0.0.0/0); porta 80 (HTTP) liberada para acesso à API.Contêiner Não-Root: Aplicação executada com usuário sem privilégios (appuser).Persistência: Banco SQLite armazenado no volume Docker cloud-tasks-data:/data, sobrevivendo à destruição e recriação de contêineres.
