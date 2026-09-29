# 🐜 TrackAnt

> Tus finanzas, tu colonia.

Tracker de finanzas personales local-first con metáfora visual de colonia de hormigas. Corre como app desktop/web con Django + HTMX + Alpine.js + Tailwind CSS + SQLite. No requiere login, internet, ni configuración.

## Features

- **Dashboard** — KPIs, gráficos de torta/barras, últimas transacciones, widget colonia
- **Transacciones** — CRUD con búsqueda, filtro por mes, quick-add modal
- **Ingresos/Gastos** — Listados filtrados por tipo
- **Metas de ahorro** — Barras de progreso, auto-marca al alcanzar objetivo
- **Deudas** — Tracking de "yo debo" / "me deben" con historial de pagos
- **Presupuestos** — Límites mensuales por categoría con alertas
- **Suscripciones** — Ciclos semanales/mensuales/anuales con normalización
- **Gastos compartidos** — Grupos, división equitativa, balance por miembro
- **Colonia de hormigas** — Visualización SVG animada que refleja salud financiera
- **PWA** — Instalable como app, funciona offline, bottom tab bar
- **Dark mode** — Toggle con persistencia en localStorage
- **Multi-moneda** — Soporte para múltiples monedas por colonia

## Quick start

### Requisitos

- Python 3.10+
- Git

### Instalación

```bash
git clone https://github.com/user/TrackAnt.git
cd TrackAnt
./scripts/run.sh
```

El script crea el venv, instala dependencias, corre migraciones, carga seed data y levanta el servidor en `http://localhost:8000`.

### Instalación manual

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

## Stack

| Componente | Tecnología |
|---|---|
| Backend | Django 5.0 |
| API | Django REST Framework |
| Frontend | HTMX + Alpine.js + Tailwind CSS |
| Charts | Chart.js |
| Icons | Lucide |
| DB | SQLite (local-first) |
| PWA | Service Worker + Manifest |

## Estructura

```
TrackAnt/
├── finances/       # Core: transacciones, categorías, monedas
├── goals/          # Reservas e Inversiones
├── debts/          # Deudas y préstamos
├── budgets/        # Presupuestos mensuales
├── subscriptions/  # Suscripciones recurrentes
├── splits/         # Gastos compartidos
├── ants/           # Colonia de hormigas (visualización)
├── api/            # Router API REST + stats
├── users/          # Auth, sesiones, colonias
├── templates/      # Templates globales + componentes
├── static/         # CSS, JS, icons, manifest, SW
└── scripts/        # run.sh, trackant.desktop
```

## API

Todas las APIs están en `/api/v1/` sin autenticación (local-first).

| Endpoint | Descripción |
|---|---|
| `GET/POST /api/v1/transactions/` | CRUD transacciones |
| `GET/POST /api/v1/reserves/` | CRUD reservas |
| `GET/POST /api/v1/debts/` | CRUD deudas |
| `GET/POST /api/v1/budgets/` | CRUD presupuestos |
| `GET/POST /api/v1/subscriptions/` | CRUD suscripciones |
| `GET /api/v1/stats/` | Balance, ingresos/gastos mensuales |
| `GET /api/v1/stats/by-category/` | Gastos por categoría |
| `GET /api/v1/stats/monthly/` | Ingresos/gastos por mes |

## Desarrollo

```bash
# Servidor
python manage.py runserver

# Migraciones
python manage.py makemigrations && python manage.py migrate

# Seed data
python manage.py seed_data

# Admin
python manage.py createsuperuser
```

## Datos

- DB SQLite en `~/.trackant/db.sqlite3`
- Sin login requerido (colonia invitada automática)
- Sin conexión a internet necesaria
- Idioma: español (es-AR)

## License

MIT
