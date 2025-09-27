```aiignore
bot_project/
│── pyproject.toml        
│── alembic.ini          
│── .env                  
│── README.md
│── docker-compose.yml    # Postgres + бот
│── Dockerfile
│
├── app/
│   ├── __init__.py
│   │
│   ├── interface/        # (адаптеры: Telegram, API, CLI)
│   │   ├── __init__.py
│   │   ├── telegram_bot.py
│   │   └── handlers/     
│   │       ├── __init__.py
│   │       ├── balance.py
│   │       ├── exchange.py
│   │       └── reports.py
│   │
│   ├── application/    
│   │   ├── __init__.py
│   │   ├── balance_uc.py 
│   │   ├── close_day_uc.py    
│   │   ├── formula_uc.py   
│   │   └── exchange_uc.py   
│   │
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── models/       
│   │   │   ├── __init__.py
│   │   │   ├── balance.py
│   │   │   ├── transaction.py
│   │   │   └── formula.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── balance_service.py
│   │   │   └── formula_service.py
│   │   ├── repositories/ 
│   │   │   ├── __init__.py
│   │   │   └── balance_repo.py
│   │   └── providers/       
│   │       ├── __init__.py
│   │       ├── exchange_provider.py
│   │       └── report_exporter.py
│   │
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py          # настройка SQLAlchemy
│   │   │   ├── session.py       # async session factory
│   │   │   └── migrations/      # alembic scripts
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   └── postgres_balance_repo.py
│   │   ├── providers/
│   │   │   ├── __init__.py
│   │   │   ├── rapira_adapter.py
│   │   │   └── exporters.py     # CSVExporter, ExcelExporter
│   │
│   └── config.py         
│
└── main.py          

```