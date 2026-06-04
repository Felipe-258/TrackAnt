# TrackAnt — Plan del Proyecto

> Tracker de finanzas personales con metáfora visual de colonia de hormigas.
> **Stack**: Django + HTMX + Alpine.js + Tailwind CSS + SQLite (local-first).
> **Sin login obligatorio** — solo si se quiere sincronización multi-dispositivo.

---

## 1. Visión General

TrackAnt es una app de escritorio/web para trackear finanzas personales: ingresos, gastos, deudas, metas de ahorro, presupuestos, suscripciones y gastos compartidos. La UI está gamificada con una colonia de hormigas viva que refleja el estado financiero.

**Principios:**
- **Local-first**: SQLite en `~/.trackant/`, sin necesidad de internet.
- **Sin fricción**: no requiere registro ni login para uso local.
- **Rápido de usar**: formulario de transacción en segundos desde cualquier pantalla.
- **Visual**: la colonia de hormigas da feedback inmediato del estado financiero.

---

## 2. Stack Tecnológico

| Componente | Herramienta | Justificación |
|---|---|---|
| Backend | Django 5.x + Django REST Framework | ORM potente, admin gratis, ecosistema maduro |
| Frontend | Django Templates + HTMX + Alpine.js | SPA-like sin build tools, un solo proyecto |
| Estilos | Tailwind CSS (CDN) | Rápido de prototipar, responsive, dark mode |
| Base de datos | SQLite | Cero configuración, archivo portable |
| Gráficos | Chart.js (CDN) | Torta y barras para dashboard |
| Desktop | Navegador directo (+ futuro PyWebView) | Sin dependencias pesadas |
| Íconos | Emoji nativos + SVG custom | Sin librería externa |

---

## 3. Estructura del Proyecto

```
TrackAnt/
├── manage.py
├── requirements.txt
├── PLAN.md                         # Este documento
│
├── trackant/                       # Configuración Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── finances/                       # App core: transacciones y categorías
│   ├── models.py
│   │   ├── Currency                # Símbolo, código ISO, tasa de conversión
│   │   ├── Category                # Nombre, tipo (INCOME/EXPENSE), ícono, color
│   │   ├── Tag                     # Nombre, color (tabla de tags)
│   │   └── Transaction             # ──────────────────────────────────────
│   │       ├── type                  INCOME | EXPENSE
│   │       ├── amount                Decimal (12,2)
│   │       ├── currency              FK → Currency
│   │       ├── category              FK → Category
│   │       ├── tags                  M2M → Tag
│   │       ├── custom_tags           JSONField (tags libres)
│   │       ├── date                  Date
│   │       ├── note                  TextField
│   │       ├── receipt               ImageField (opcional)
│   │       └── is_recurring          BooleanField
│   │
│   ├── views/
│   │   ├── pages.py                # Vistas HTML (dashboard, CRUD)
│   │   └── api.py                  # DRF ViewSets
│   ├── serializers.py
│   ├── forms.py
│   ├── urls.py
│   └── templates/finances/
│
├── goals/                           # Metas de ahorro/compra
│   ├── models.py
│   │   └── Goal                     # Nombre, target_amount, current, deadline, color
│   ├── views/
│   └── templates/goals/
│
├── debts/                           # Deudas y préstamos
│   ├── models.py
│   │   ├── Debt                     # Persona, amount, type(OWE/OWED), date, interest
│   │   └── DebtPayment              # Monto, fecha, FK → Debt
│   ├── views/
│   └── templates/debts/
│
├── budgets/                         # Presupuestos mensuales
│   ├── models.py
│   │   └── Budget                   # Category, limit_amount, month, year
│   ├── views/
│   └── templates/budgets/
│
├── subscriptions/                   # Suscripciones recurrentes
│   ├── models.py
│   │   └── Subscription             # Name, amount, currency, cycle, next_date
│   ├── views/
│   └── templates/subscriptions/
│
├── splits/                          # Gastos compartidos
│   ├── models.py
│   │   ├── SplitGroup               # Nombre, miembros (JSON)
│   │   └── SplitExpense             # Amount, pagador, división
│   ├── views/
│   └── templates/splits/
│
├── ants/                            # Motor visual de la colonia
│   ├── templatetags/
│   │   └── ant_tags.py             # Template tags: {% ant_colony %}, {% worker_ants %}
│   ├── utils.py                     # Lógica: clima financiero, estado de la colonia
│   └── templates/ants/
│       ├── colony.html              # SVG hormiguero completo
│       ├── worker_ant.svg           # Sprite hormiga obrera
│       ├── queen_ant.svg            # Sprite hormiga reina
│       └── animations.css           # Keyframes de movimiento
│
├── templates/
│   ├── base.html                    # Layout principal: sidebar + navbar + contenido
│   ├── components/
│   │   ├── sidebar.html             # Navegación
│   │   ├── quick_add.html           # Botón/modal "Agregar rápido"
│   │   ├── transaction_row.html     # Fila HTMX para lista
│   │   └── currency_selector.html   # Selector de moneda
│   └── partials/
│       ├── pagination.html          # Paginación infinita HTMX
│       └── alerts.html              # Notificaciones toast
│
├── api/
│   ├── urls.py                      # Router API REST unificado
│   └── routers.py
│
├── static/
│   ├── css/
│   └── js/
│       ├── charts.js                # Config Chart.js para dashboard
│       └── ant_animations.js        # Control JS de animaciones
│
└── scripts/
    ├── run.sh                       # Levanta servidor + abre navegador
    └── trackant.desktop             # Shortcut Linux (.local/share/applications)
```

---

## 4. Modelos de Datos

### 4.1 `Currency`
| Campo | Tipo | Descripción |
|---|---|---|
| code | CharField(3) | Código ISO: ARS, USD, EUR |
| symbol | CharField(5) | Símbolo: $, U$S, € |
| name | CharField(50) | Nombre completo |
| rate_to_base | DecimalField | Tasa de conversión manual (ARS es base=1.0) |

### 4.2 `Category`
| Campo | Tipo | Descripción |
|---|---|---|
| name | CharField(100) | Ej: "Supermercado", "Salario" |
| type | CharField(7) | INCOME / EXPENSE |
| icon | CharField(10) | Emoji: 🛒, 💼, 🍕 |
| color | CharField(7) | Hex: #FF5733 |

### 4.3 `Tag`
| Campo | Tipo | Descripción |
|---|---|---|
| name | CharField(50) | Ej: "urgente", "recurrente" |
| color | CharField(7) | Hex: #3498db |

### 4.4 `Transaction`
| Campo | Tipo | Descripción |
|---|---|---|
| type | CharField(7) | INCOME / EXPENSE |
| amount | DecimalField(12,2) | Monto positivo |
| currency | FK → Currency | Moneda de la transacción |
| category | FK → Category | Categoría |
| tags | M2M → Tag | Tags estructurados (autocomplete) |
| custom_tags | JSONField | Tags libres: `["viaje2026", "compartido"]` |
| date | DateField | Fecha de la transacción |
| note | TextField | Nota opcional |
| receipt | ImageField | Foto del ticket (opcional) |
| is_recurring | BooleanField | ¿Es transacción recurrente? |
| created_at | DateTimeField | Auto |
| updated_at | DateTimeField | Auto |

> **Tags duales**: el formulario tiene un input con autocomplete que busca en `Tag` (tabla). Si el texto no matchea ningún tag existente, se guarda en `custom_tags` (JSON). Si matchea, se asocia vía ManyToMany.

### 4.5 `Goal`
| Campo | Tipo | Descripción |
|---|---|---|
| name | CharField(200) | "Vacaciones Europa 2026" |
| target_amount | DecimalField | Monto objetivo |
| current_amount | DecimalField | Progreso actual |
| currency | FK → Currency | Moneda de la meta |
| deadline | DateField | Fecha límite (nullable) |
| color | CharField(7) | Color de la barra |
| is_achieved | BooleanField | default=False |

### 4.6 `Debt`
| Campo | Tipo | Descripción |
|---|---|---|
| person | CharField(200) | Nombre de la persona |
| amount | DecimalField | Monto total de la deuda |
| currency | FK → Currency | Moneda |
| debt_type | CharField(4) | OWE (yo debo) / OWED (me deben) |
| date | DateField | Fecha de origen |
| interest_rate | DecimalField | Interés anual % (nullable) |
| note | TextField | Nota opcional |
| is_settled | BooleanField | ¿Saldada? |

### 4.7 `DebtPayment`
| Campo | Tipo | Descripción |
|---|---|---|
| debt | FK → Debt | Deuda relacionada |
| amount | DecimalField | Monto del pago |
| date | DateField | Fecha del pago |

### 4.8 `Budget`
| Campo | Tipo | Descripción |
|---|---|---|
| category | FK → Category | Categoría a presupuestar |
| limit_amount | DecimalField | Límite mensual |
| currency | FK → Currency | Moneda |
| month | IntegerField | 1-12 |
| year | IntegerField | Año |

### 4.9 `Subscription`
| Campo | Tipo | Descripción |
|---|---|---|
| name | CharField(200) | "Netflix", "Spotify" |
| amount | DecimalField | Monto del cobro |
| currency | FK → Currency | Moneda |
| cycle | CharField(10) | WEEKLY / MONTHLY / YEARLY |
| next_date | DateField | Próxima fecha de cobro |
| is_active | BooleanField | default=True |

### 4.10 `SplitGroup`
| Campo | Tipo | Descripción |
|---|---|---|
| name | CharField(200) | "Viaje a la costa" |
| members | JSONField | `["Juan", "María", "Yo"]` |

### 4.11 `SplitExpense`
| Campo | Tipo | Descripción |
|---|---|---|
| group | FK → SplitGroup | Grupo de split |
| description | CharField(200) | "Cena restaurante" |
| amount | DecimalField | Monto total |
| currency | FK → Currency | Moneda |
| paid_by | CharField(200) | Quién pagó |
| date | DateField | Fecha |
| shares | JSONField | `{"Juan": 5000, "María": 5000, "Yo": 5000}` |

---

## 5. Diseño de la UI

### 5.1 Layout Principal

```
┌──────────────────────────────────────────────────────┐
│  🐜 TrackAnt               [✦ Agregar rápido]  [🌙]  │
├────────────┬─────────────────────────────────────────┤
│  Sidebar   │                                         │
│            │  ┌──────────┐ ┌─────────┐ ┌──────────┐ │
│ 📊 Home    │  │Balance   │ │ Gastos  │ │ Metas    │ │
│ 💰 Ingresos│  │ARS 125k  │ │ -$45k   │ │ 68% 🐜   │ │
│ 💸 Gastos  │  └──────────┘ └─────────┘ └──────────┘ │
│ 🎯 Metas   │                                         │
│ 💳 Deudas  │  ┌───────────────────────────────────┐  │
│ 📊 Presup. │  │        🏠  HORMIGUERO VIVO        │  │
│ 🔁 Subs.   │  │    🐜🐜→🍂🍂🐜→🍂    👑          │  │
│ 👥 Splits  │  │  Hormigas llevando hojas al nido  │  │
│ ⚙️ Ajustes │  └───────────────────────────────────┘  │
│            │                                         │
│            │  📈 Gastos por categoría (torta)        │
│            │  📊 Ingresos vs Gastos (barras)         │
│            │  📋 Últimas transacciones                │
└────────────┴─────────────────────────────────────────┘
```

### 5.2 Navegación (Sidebar)
- 📊 **Home** — Dashboard principal con hormiguero
- 💰 **Ingresos** — Lista filtrable de ingresos
- 💸 **Gastos** — Lista filtrable de gastos
- 🎯 **Metas** — Goals con progreso visual
- 💳 **Deudas** — Tabs "Debo" / "Me deben"
- 📊 **Presupuestos** — Budgets del mes
- 🔁 **Suscripciones** — Timeline de cobros
- 👥 **Splits** — Gastos compartidos
- ⚙️ **Ajustes** — Monedas, categorías, tags, exportación

### 5.3 Sistema Visual de Hormigas

```
Colonia (hormiguero en el dashboard):
├── 🐜 Hormigas obreras = transacciones del día
│     Hojitas verdes = ingresos, hojitas rojas = gastos
│
├── 👑 Hormiga reina = meta de ahorro principal
│     Crece visualmente con el progreso
│
├── 🛡️ Hormigas soldado = alertas de presupuesto
│     Aparecen cuando el gasto supera el 80% del límite
│
├── 🍂 Hojas acumuladas = balance del mes
│     Pila que crece o decrece
│
└── 🌤️/🌧️ Clima = estado financiero general
      Soleado: ahorro positivo, Lluvia: deudas altas
```

**Implementación**: SVG inline + animaciones CSS `@keyframes`. Las hormigas se generan dinámicamente vía template tags de Django según datos reales.

### 5.4 Formulario "Agregar Rápido"

```
┌─────────────────────────────────────┐
│  Agregar Transacción            [✕] │
│                                     │
│  Tipo:  [💰 Ingreso] [💸 Gasto]    │
│  Monto: [__________]  Moneda: [ARS▾]│
│  Categ: [Supermercado ▾]           │
│  Tags:  [comida__________] [+Agregar] │
│         🏷️ comida  🏷️ urgente       │
│  Fecha: [2026-06-03]               │
│  Nota:  [_________________________] │
│  📎 Foto ticket (opcional)          │
│                                     │
│  [Guardar]  [Guardar y nuevo]      │
└─────────────────────────────────────┘
```

> El campo tags muestra autocomplete con tags existentes. Tags nuevos se guardan en `custom_tags`.

---

## 6. API REST

### 6.1 Endpoints

```
/api/v1/
├── currencies/          GET, POST
├── categories/          GET, POST, PUT, DELETE
├── tags/                GET, POST, PUT, DELETE
├── transactions/        GET, POST, PUT, DELETE  (filtros: ?type=&category=&date_from=&date_to=&currency=)
├── goals/               GET, POST, PUT, DELETE
├── debts/               GET, POST, PUT, DELETE
├── debt-payments/       GET, POST
├── budgets/             GET, POST, PUT, DELETE
├── subscriptions/       GET, POST, PUT, DELETE
├── split-groups/        GET, POST, PUT, DELETE
├── split-expenses/      GET, POST, PUT, DELETE
├── stats/
│   ├── summary/         GET  (balance total, ingresos/gastos del mes)
│   ├── by-category/     GET  (gastos agrupados por categoría)
│   └── monthly/         GET  (ingresos vs gastos por mes)
└── ant-colony/
    └── state/           GET  (datos para renderizar la colonia)
```

### 6.2 Formato de Respuesta

```json
{
  "count": 150,
  "next": "http://localhost:8000/api/v1/transactions/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "type": "EXPENSE",
      "amount": "4500.00",
      "currency": {"code": "ARS", "symbol": "$"},
      "category": {"id": 3, "name": "Supermercado", "icon": "🛒", "color": "#FF5733"},
      "tags": [{"id": 1, "name": "comida", "color": "#3498db"}],
      "custom_tags": ["urgente"],
      "date": "2026-06-03",
      "note": "Compra semanal",
      "receipt": null,
      "is_recurring": false
    }
  ]
}
```

---

## 7. Plan de Ejecución

### Fase 1 — Setup del Proyecto
- Crear entorno virtual e instalar dependencias
- `django-admin startproject trackant`
- Configurar `settings.py` (SQLite en `~/.trackant/`, static, templates)
- Template `base.html` con Tailwind CDN + HTMX + Alpine.js + sidebar dummy
- `run.sh` y `.desktop` shortcut
- `git init` + `.gitignore`

### Fase 2 — App Finances (Core)
- Modelos: `Currency`, `Category`, `Tag`, `Transaction`
- Admin de Django registrado para todos
- CRUD de transacciones con HTMX (formularios inline, sin recarga)
- Tags duales con autocomplete (busca Tag existente, guarda en custom_tags si no)
- Filtros: por tipo, categoría, mes, moneda
- Búsqueda full-text en notas
- Paginación infinita con HTMX

### Fase 3 — Dashboard
- Tarjetas resumen: balance total, ingresos del mes, gastos del mes
- Chart.js: torta de gastos por categoría
- Chart.js: barras ingresos vs gastos mensuales
- Últimas 10 transacciones con scroll infinito
- Botón flotante "Agregar rápido" (modal HTMX)

### Fase 4 — App Goals
- Modelo `Goal`
- CRUD completo con HTMX
- Barra de progreso visual (CSS animations)
- Asignar transacciones automáticamente a un goal (vincular por tag o selección manual)
- Vista de metas activas vs completadas

### Fase 5 — App Debts
- Modelos `Debt` y `DebtPayment`
- Tabs "Debo" / "Me deben"
- CRUD de deudas y pagos
- Cálculo automático de saldo restante
- Plan de pagos sugerido (monto / cuotas sugeridas)
- Recordatorios visuales de deudas próximas a vencer

### Fase 6 — App Budgets
- Modelo `Budget`
- CRUD por mes
- Barra de progreso con alertas de color:
  - Verde: 0-50%
  - Amarillo: 50-80%
  - Naranja: 80-95%
  - Rojo: 95-100%+
- Alerta HTMX cuando se supera el 80%
- Vista comparativa: presupuestado vs real

### Fase 7 — App Subscriptions
- Modelo `Subscription`
- CRUD completo
- Timeline visual de próximos cobros (estilo calendario horizontal)
- Cálculo automático de gasto mensual total en suscripciones
- Badge de alerta cuando un cobro está a ≤3 días
- Detección: sugerir suscripción si una transacción se repite con mismo monto y nota

### Fase 8 — App Splits
- Modelos `SplitGroup` y `SplitExpense`
- Crear grupo (nombre + miembros)
- Agregar gasto: monto, quién pagó, cómo se divide
- Vista de balances: "Juan te debe $X en total"
- Marcar saldado cuando se paga

### Fase 9 — API REST
- DRF ViewSets para todos los modelos
- Serializers con nested relationships
- Filtros, búsqueda, ordenamiento, paginación
- Endpoints de stats: summary, by-category, monthly
- Endpoint `ant-colony/state/` para datos de la colonia
- Documentación con drf-spectacular (Swagger)

### Fase 10 — Sistema Visual de Hormigas
- SVG sprites: `worker_ant.svg`, `queen_ant.svg`
- CSS animations: caminata, carga de hojas, crecimiento de reina
- Template tags Django que reciben datos reales y renderizan SVG
- Clima financiero (sol, nubes, lluvia, tormenta) según balance
- Integración en el dashboard principal
- Ajustes de performance (las animaciones no deben trabar la UI)

---

## 8. Dependencias

```
# requirements.txt
Django>=5.0,<5.1
djangorestframework>=3.15
django-htmx>=1.19
django-widget-tweaks>=1.5
django-crispy-forms>=2.3
crispy-tailwind>=0.5
Pillow>=10.0
python-dateutil>=2.8
drf-spectacular>=0.27       # Swagger docs (fase 9)
```

---

## 9. Comandos Útiles

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario (opcional, para admin de Django)
python manage.py createsuperuser

# Servidor de desarrollo
python manage.py runserver

# O usar el script:
./scripts/run.sh
```

---

## 10. Roadmap Futuro (post v1)

- **PyWebView wrapper**: ventana nativa sin navegador
- **Sync cloud**: PostgreSQL + autenticación opcional para multi-dispositivo
- **ML predictions**: predecir gastos del mes siguiente con scikit-learn
- **OCR tickets**: escanear tickets con Tesseract
- **Export/Import**: CSV, JSON, PDF de reportes
- **Notificaciones nativas**: recordatorios de deudas y suscripciones
- **Dark mode**: toggle en sidebar (persistido en localStorage)
- **PWA**: service worker para uso offline en mobile

---

## 11. Notas de Diseño

- **Sin build tools JS**: Tailwind vía CDN + script `tailwind.config` inline. Si se necesita build, se migra a Vite solo para CSS.
- **HTMX**: todas las interacciones CRUD son sin recarga de página (hx-get, hx-post, hx-delete, hx-target).
- **Alpine.js**: solo para estado local de componentes (dropdowns, modales, tabs).
- **Chart.js**: se carga desde CDN, se instancia con datos que Django inyecta en `data-*` attributes o vía un endpoint `/api/v1/stats/`.
- **Responsive**: sidebar colapsa a bottom-tab-bar en mobile con Tailwind breakpoints.
- **Monedas**: las tasas de conversión son manuales en v1. Futuro: API de tasas en tiempo real.
