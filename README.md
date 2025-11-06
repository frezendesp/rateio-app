# Sistema de Rateio Pessoal

Aplicação completa para controle e rateio de despesas domésticas entre Fernando e sua esposa. O sistema é composto por uma API FastAPI executada com Gunicorn e um frontend em React com Tailwind CSS e Chart.js.

## Estrutura do Projeto

```
/opt/rateio-app/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── routes/
│   │   └── utils/
│   ├── requirements.txt
│   └── gunicorn.conf.py
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
├── data/
│   └── database.db
├── logs/
│   └── gunicorn.log
└── systemd/
    └── rateio.service
```

> As pastas `data/` e `logs/` são criadas automaticamente. O arquivo `data/database.db` armazena o banco SQLite padrão.

## Backend (FastAPI + Gunicorn)

### Requisitos
- Python 3.12+
- Virtualenv (opcional, mas recomendado)

### Instalação e Execução Local

```bash
./scripts/run_local_backend.sh
```

O script cria um ambiente virtual em `backend/venv`, instala as dependências listadas em `backend/requirements.txt` e executa o servidor Uvicorn com recarregamento automático na porta `8000`.

### Execução em Produção

1. Crie o ambiente virtual manualmente (ou via Ansible/CI).
2. Instale as dependências:
   ```bash
   cd /opt/rateio-app/backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Habilite o serviço systemd (requer permissões de superusuário):
   ```bash
   sudo ./scripts/install_systemd_service.sh
   ```
4. O serviço `rateio.service` executará o Gunicorn com o worker Uvicorn, ouvindo em `127.0.0.1:8000`.

## Frontend (React + Tailwind + Chart.js)

### Requisitos
- Node.js 20+
- npm ou yarn

### Instalação

```bash
cd frontend
npm install
```

### Desenvolvimento

```bash
npm run dev
```

O servidor Vite sobe em `http://127.0.0.1:5173` e possui proxy configurado para encaminhar requisições `/api` ao backend na porta `8000`.

### Build de Produção

```bash
npm run build
```

Os artefatos finais ficam em `frontend/dist`. Para deploys com Nginx, copie o conteúdo da pasta `dist` para `frontend/build` ou configure o servidor para apontar diretamente para `dist`.

## Banco de Dados

- Banco padrão: SQLite (`data/database.db`).
- Models e relacionamentos estão definidos em `backend/app/models.py`.
- Caso deseje usar outro banco (ex: PostgreSQL), defina a variável de ambiente `DATABASE_URL` antes de iniciar a aplicação.

## API

Principais rotas REST disponíveis (todas com prefixo `/api`):

| Recurso | Descrição |
|---------|-----------|
| `/people` | CRUD de pessoas (Fernando e esposa, por exemplo) |
| `/accounts` | Contas e cartões cadastrados |
| `/expenses` | Despesas individuais, com divisão proporcional |
| `/dashboard/summary` | Resumo financeiro consolidado |
| `/recurrences` | Controle de regras e geração de despesas recorrentes |

A documentação interativa Swagger está disponível em `http://127.0.0.1:8000/docs`.

## Recorrências

- Regras de recorrência permitem configurar frequência (diária, semanal, mensal, anual) e intervalo.
- A rota `POST /api/recurrences/{id}/generate` cria a próxima despesa com base no modelo associado.
- A rota `POST /api/recurrences/run-due` gera automaticamente todas as despesas vencidas até a data atual.

## Logs

- `logs/gunicorn.log` registra os acessos e erros do Gunicorn.
- Recomenda-se configurar `logrotate` em produção.

## Deploy com Nginx

O Nginx deve servir os arquivos estáticos do frontend e encaminhar `/api` para o Gunicorn. Um exemplo de configuração está disponível na documentação técnica em `DOCUMENTACAO_TECNICA.md` (não versionado automaticamente neste repositório).

## Testes

No momento o projeto não possui suíte de testes automatizados, mas a arquitetura modular permite adicionar facilmente testes unitários e de integração.

## Licença

Projeto criado para uso pessoal e educativo.
