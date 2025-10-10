```aiignore
DolbaBot/
│── main.py
│── config.py
│── requirements.txt
│── Dockerfile
│── docker-compose.yml
│── alembic.ini
│
├── bot/
│   ├── __init__.py
│   ├── handlers.py
│   ├── commands.py
│
├── services/
│   ├── __init__.py
│   ├── balances.py
│   ├── reports.py
│   ├── formulas.py
│
├── exchanges/
│   ├── __init__.py
│   ├── base.py
│   ├── rapira.py
│
├── db/
│   ├── __init__.py
│   ├── models.py
│   ├── db_session.py
│
└── utils/
    ├── __init__.py
    ├── logger.py
    ├── helpers.py
```