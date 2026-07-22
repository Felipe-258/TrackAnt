# TrackAnt — Guía para Agentes

## Resumen del Proyecto

**TrackAnt** es un tracker de finanzas personales local-first con metáfora visual de colonia de hormigas. Corre como app desktop/web con Django + HTMX + Alpine.js + Tailwind CSS + SQLite. No requiere login, internet, ni configuración.

- **Local-first**: SQLite en `~/.trackant/db.sqlite3`
- **Idioma UI**: Español (`es-AR`)
- **Sin fricción**: Sin registro, formulario rápido accesible desde cualquier pantalla
- **Visual**: Colonia de hormigas SVG animada que refleja la salud financiera

## Stack Tecnológico

| Componente | Tecnología |
|---|---|
| Backend | Django >=5.0,<5.1 |
| API | Django REST Framework >=3.15 |
| Filtros | django-filter >=25.1 |
| HTMX | django-htmx >=1.19 |
| Forms | django-widget-tweaks >=1.5, django-crispy-forms + crispy-tailwind |
| CSS | Tailwind CSS (CDN) con paleta de colores custom |
| JS | HTMX (CDN) + Alpine.js 3.x (CDN) + Chart.js 4.4.7 (CDN) |
| Iconos | Lucide (CDN) |
| DB | SQLite |

### CDNs cargados en `base.html`
- `cdn.tailwindcss.com` — Tailwind con config inline
- `unpkg.com/lucide@latest` — Iconos Lucide
- `unpkg.com/htmx.org@latest` — HTMX
- `cdn.jsdelivr.net/npm/alpinejs@3.x.x` — Alpine.js
- `cdn.jsdelivr.net/npm/chart.js@4.4.7` — Chart.js

## Estructura de Directorios

```
TrackAnt/
├── manage.py
├── requirements.txt
├── trackant/               # Config del proyecto Django
│   ├── settings.py
│   ├── urls.py             # URL raíz
│   └── wsgi.py
├── templates/              # Templates globales
│   ├── base.html           # Layout maestro
│   ├── components/         # Componentes reutilizables
│   │   ├── sidebar.html
│   │   ├── quick_add.html
│   │   ├── transaction_row.html
│   │   └── toast.html
│   └── partials/
│       └── pagination.html
├── static/                 # Static files globales (vacío actualmente)
├── finances/               # App core: transacciones, categorías, monedas, tags
├── goals/                  # App metas de ahorro
├── debts/                  # App deudas y préstamos
├── budgets/                # App presupuestos mensuales
├── subscriptions/          # App suscripciones recurrentes
├── splits/                 # App gastos compartidos
├── ants/                   # App visualización colonia de hormigas
├── api/                    # Router central API REST + stats
├── venv/                   # Entorno virtual
└── scripts/
    ├── run.sh
    └── trackant.desktop
```

## Apps y Sus Propósitos

### `finances` — App Core
Modelos: `Currency`, `Category`, `Tag`, `Transaction`

- **Dashboard** (`/`): KPIs (balance, ingresos/gastos mensuales, metas activas), gráficos de torta/barras, últimas 10 transacciones, widget colonia
- **Transacciones** (`/transactions/`): CRUD con HTMX, búsqueda, filtro por mes
- **Ingresos** (`/incomes/`): Listado de ingresos
- **Gastos** (`/expenses/`): Listado de gastos
- **Categorías** (`/categories/`): Listado (placeholder Fase 2)
- **Tags**: Sistema dual — tags estructurados (M2M `Tag`) + tags libres (`custom_tags` JSONField)
- **Comando seed_data**: `python manage.py seed_data` crea 6 monedas, 21 categorías, 8 tags

### `goals` — Metas de Ahorro
Modelo: `Goal`

- CRUD de metas con barras de progreso
- `goal_add_progress`: Suma dinero a una meta (usa `F()` expressions para evitar race conditions)
- Auto-marca `is_achieved=True` cuando `current_amount >= target_amount`
- **IMPORTANTE**: El campo `current_amount` es `DecimalField`. Siempre usar `Decimal()`, NUNCA `float()`. `Decimal + float` lanza `TypeError`.

### `debts` — Deudas
Modelos: `Debt`, `DebtPayment`

- Tipos: "Yo debo" (`OWE`) / "Me deben" (`OWED`)
- Vista detalle con historial de pagos + formulario inline de pago
- Auto-settled cuando `remaining <= 0`
- Tabs Alpine.js para cambiar entre tipos

### `budgets` — Presupuestos
Modelo: `Budget` (unique_together: category, month, year)

- Límite de gasto por categoría/mes/año
- Calcula `spent()` desde `Transaction`, muestra % usado con colores (ok/caution/warning/danger)
- Filtro HTMX de mes/año

### `subscriptions` — Suscripciones
Modelo: `Subscription`

- Ciclos: WEEKLY, MONTHLY, YEARLY
- `monthly_cost()`: normaliza a costo mensual
- `days_until_next()`: días hasta próximo cobro
- Muestra total mensual y tiempo relativo (Hoy, Vencida, En X días)

### `splits` — Gastos Compartidos
Modelos: `SplitGroup`, `SplitExpense`

- Grupos de personas, gastos compartidos
- `balance()`: calcula saldos netos por miembro
- División equitativa automática al crear gasto

### `ants` — Colonia de Hormigas
Sin modelos. Solo vistas, template tags, CSS, y utils.

- `ants/utils.py`: Computa estado de la colonia desde datos reales (transacciones, metas, presupuestos)
- Hormigas obreras = cantidad de transacciones (máx 12), hormigas soldado = alertas de presupuesto (máx 4)
- Tamaño reina = progreso de meta (large ≥75%, medium ≥50%, small ≥25%, tiny <25%)
- Clima = relación ingresos/gastos (despejado/soleado/nublado/lluvioso/tormenta)
- Ciclo día/noche = hora real del sistema
- `ants/templatetags/ant_tags.py`: Tags/filtros custom para templates
- `ants/static/ants/css/colony.css`: Animaciones CSS keyframe

### `api` — Router API
Sin modelos. Agrega todos los routers de las apps + 3 endpoints de stats:
- `/api/v1/stats/` → balance, ingresos/gastos mensuales, conteos
- `/api/v1/stats/by-category/` → gastos por categoría del mes
- `/api/v1/stats/monthly/` → ingresos/gastos por mes del año

## Modelos — Relaciones Clave

```
Currency ──┬── Transaction
           ├── Goal
           ├── Debt
           ├── Budget
           └── SplitExpense

Category ──┬── Transaction
           ├── Budget (solo EXPENSE)
           └── Subscription (SET_NULL)

Tag ←──M2M──→ Transaction

Debt ──< DebtPayment (CASCADE)

SplitGroup ──< SplitExpense (CASCADE)
```

## API REST

Router en `/api/v1/` con `PageNumberPagination` (page_size=25).
Sin autenticación. Filtros: `DjangoFilterBackend`, `SearchFilter`, `OrderingFilter`.

| Endpoint | App |
|---|---|
| `currencies/` | finances |
| `categories/` | finances |
| `tags/` | finances |
| `transactions/` | finances |
| `goals/` | goals |
| `debts/` | debts |
| `debt-payments/` | debts |
| `budgets/` | budgets |
| `subscriptions/` | subscriptions |
| `split-groups/` | splits |
| `split-expenses/` | splits |
| `stats/` | api |
| `stats/by-category/` | api |
| `stats/monthly/` | api |

## URLs de Páginas

```
/                          → finances:dashboard
/transactions/             → finances:transaction_list (+ add, edit, delete)
/transactions/quick-add/   → finances:transaction_quick_add (POST-only, HTMX)
/incomes/                  → finances:income_list
/expenses/                 → finances:expense_list
/categories/               → finances:category_list
/goals/                    → goals:goal_list (+ add, edit, delete, add-progress)
/debts/                    → debts:debt_list (+ add, edit, delete, detail)
/budgets/                  → budgets:budget_list (+ add, edit, delete)
/subscriptions/            → subscriptions:subscription_list (+ add, edit, delete)
/splits/                   → splits:split_list (+ groups/add, /<pk>, /<pk>/edit, /<pk>/delete, expenses/add, expenses/<pk>/edit, expenses/<pk>/delete)
/ants/colony/              → ants:colony_view
/ants/playground/          → playground (solo DEBUG)
/admin/                    → Django admin
```

## Sistema de Diseño

### Paleta de Colores (Tailwind custom)

| Paleta | Uso semántico |
|---|---|
| `earth` | Fondos, bordes, texto neutro, chrome UI |
| `clay` | Gastos (montos negativos, botones delete, indicadores expense) |
| `sage` | Ingresos (montos positivos, indicadores income, éxito) |
| `gold` | Metas/ahorros (progreso, suscripciones, acentos) |

### Modo Oscuro
Estrategia `class`-based. Toggle Alpine.js, persistido en localStorage.

### Layout
- Sidebar fijo (`w-64`) con slide transition en mobile, safe area padding (`padding-top: var(--safe-top)`)
- Header sticky con backdrop blur, título de página, toggle dark mode, botón quick-add (desktop)
- Footer fijo
- **PWA Standalone**: Bottom tab bar (Home, Ingresos, Gastos, Metas, Más), sin FAB, safe area insets
- **Quick Add Modal**: Alpine.js slide-up modal (bottom sheet en mobile, centered en desktop), type/amount/category/date, trigger via `$dispatch('open-quick-add')`

### Iconos
Lucide via CDN, renderizados como `<i data-lucide="icon-name" class="lucide"></i>`.
Tamaños: `.lucide` (1.25em), `.lucide-sm` (1em), `.lucide-lg` (1.5em).
Se recrean en cada swap HTMX.

### Animaciones CSS
- `animate-fade-in`: 0.3s ease-out (usada en toasts/mensajes)
- `ant-walk`: sway horizontal (usada en dashboard)
- `float`: flotación vertical suave
- Todas las animaciones de la colonia en `ants/static/ants/css/colony.css`

## Patrones de Código

### Vistas
- **Páginas**: Function-based views en `views/pages.py`
- **API**: DRF `ModelViewSet` en `views/api.py`
- Stats API: `@api_view(['GET'])` function-based
- URLs: `app_name` definido, snake_case para names
- Templates: `{% url 'app:name' %}`

### Templates
- Heredan de `'base.html'`
- Bloques: `title`, `page_title`, `page_subtitle`, `content`, `extra_scripts`
- Nombres: `<app>/<modelo>_<accion>.html`
- Parciales: `<app>/partials/<name>.html`
- Componentes compartidos: `components/<name>.html`

### HTMX
- CRUD interactions son HTMX-driven
- `request.htmx` check en vistas para partial vs full redirect
- `hx-get`, `hx-post`, `hx-target`, `hx-swap`, `hx-trigger`, `hx-push-url`
- Tags: búsqueda autocomplete con debounce 300ms
- Transacciones: search debounce 500ms

### Alpine.js
- Estado global: `sidebarOpen`, `darkMode` (en body `x-data`)
- Quick add modal: `quickAddModal()` + `quickCategoryDropdown()` en `components/quick_add.html`
- Tags en transaction_form: componente complejo con `tagIds`, `customTags`
- Debt tabs: `x-data="{ tab: 'owe' }"` para switchear
- Transacciones: search toggle con `searchOpen` en mobile
- Transiciones: sidebar slide, backdrop fade, toast fade

### Django Admin
Todos los modelos registrados con `list_display`, `list_filter`, `search_fields`.
Verbose names en español.

### Seed Data
`python manage.py seed_data` — ubicado en `finances/management/commands/seed_data.py`.
Idempotente (usa `get_or_create`).

## Patrones Responsive

### Formularios — stacking en mobile
Todos los formularios usan `flex flex-col gap-4 sm:flex-row` para que los campos se apilen en mobile y se distribuyan en fila en desktop. Los anchos fijos (`w-32`, `w-36`) se aplican con `sm:` prefix.

### Botones de acción — igualar ancho
Footer de formularios y confirmaciones de delete usan `grid grid-cols-2 gap-3` para que Cancelar y Guardar/Eliminar tengan el mismo ancho. Los botones Cancelar tienen `text-center`.

### Transaction list — search toggle mobile
En mobile, el search es un ícono que expande un input full-width debajo del toolbar. En desktop, el input siempre es visible. Usa Alpine.js `searchOpen` con `sm:hidden` / `hidden sm:block`.

### Transaction cards mobile
`transaction_row.html` tiene layout dual: tabla para `sm:` y cards para `sm:hidden`. Las cards mobile muestran: fecha arriba, categoría debajo (misma columna), monto a la derecha, y three-dot menu. No muestran tags.

### Income/Expense lists
`income_list.html` y `expense_list.html` son templates muertos — no se usan. Las vistas `income_list` y `expense_list` renderizan `transaction_list.html` con `list_type` filtrado. En mobile usan las mismas cards que la lista de transacciones.

### Three-dot menu (acciones en dropdown)
En mobile, los botones de acción (editar, eliminar, etc.) se agrupan en un menú "⋮" (ellipsis-vertical) que despliega un dropdown con Alpine.js. Patrón:

```html
<div class="relative" x-data="{ open: false, yPos: 0 }">
  <button @click="open = !open; yPos = $el.getBoundingClientRect().bottom + 4" class="touch-target ...">
    <i data-lucide="ellipsis-vertical" class="lucide-sm"></i>
  </button>
  <div x-show="open" @click.outside="open = false" x-transition
       :style="'position:fixed; top:' + yPos + 'px; right:8px'"
       class="z-50 w-44 overflow-hidden rounded-lg border bg-white shadow-lg ...">
    <a href="..." class="flex items-center gap-2 px-4 py-2.5 text-sm ...">Acción</a>
  </div>
</div>
```

**IMPORTANTE**: Usar `position: fixed` (no `absolute`) con yPos calculado via `getBoundingClientRect()`. `position: absolute` se corta por el `overflow-y-auto` de `<main>`. Desktop usa botones individuales (`hidden sm:flex`), mobile usa dropdown (`sm:hidden`).

Aplicado en: goal_list.html, transaction_row.html (mobile + desktop), budget_list, subscription_list, debt_list.

### Dashboard — 2 columnas en mobile
KPI cards usan `grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4`. Padding/texto/iconos reducidos en mobile (`p-3 sm:p-5`, `text-lg sm:text-2xl`, `h-7 w-7 sm:h-9 sm:w-9`).

### Hormiguero — compacto en mobile
`min-h-[180px] sm:min-h-[300px]`. Weather effects y weather badge ocultos en mobile (`hidden sm:block`). Goal name label en `top-2 left-4`. Queen ant z-index `z-10` (debajo de sidebar `z-20`). Container `overflow-visible` para que el tooltip de la "i" sobresalga.

### Bottom Tab Bar (PWA standalone)
5 tabs: Home, Ingresos, Gastos, Metas, Más. Todos con `px-2`, `text-[10px]`, iconos `lucide` (1.25em). Safe area insets via `padding-bottom: var(--safe-bottom)`.

## Comandos de Desarrollo

```bash
source venv/bin/activate

# Servidor
python manage.py runserver

# Migraciones
python manage.py makemigrations
python manage.py migrate

# Seed data inicial
python manage.py seed_data

# Tests (stubs vacíos actualmente)
python manage.py test

# Django checks
python manage.py check

# Admin
python manage.py createsuperuser

# Script rápido (crea venv, migra, seed, runserver 0.0.0.0:8000)
./scripts/run.sh
```

## Convenciones Importantes

1. **Decimal, nunca float**: Todos los montos son `DecimalField`. Siempre usar `from decimal import Decimal`. `Decimal + float` → `TypeError`.
2. **F() expressions**: Para updates atómicos de campos numéricos usar `Model.objects.filter(pk=pk).update(campo=F('campo') + valor)`.
3. **select_related('currency')**: Siempre que se accede a `goal.currency.symbol` en template, usar `.select_related('currency')` en el queryset.
4. **Mensajes Django**: Se renderizan en `base.html` con estilos condicionales por tag (success=sage, error=clay, warning=gold, info=earth).
5. **request.resolver_match.namespace**: Usar namespace para active state del sidebar (ej: `namespace == 'goals'`), no view_name exacto.
6. **Nombres de apps**: `finances`, `goals`, `debts`, `budgets`, `subscriptions`, `splits`, `ants`, `api`.
7. **Nunca commitear sin que el usuario lo pida explícitamente**.
8. **Nunca hacer git push a main sin autorización explícita del usuario**. Siempre preguntar antes de pushear.
9. **Al hacer cambios en main, actualizar también la imagen Docker en GHCR**. Después de commitear y pushear, ejecutar `./build-push-deploy.sh` o al menos buildear y subir la imagen con la versión correspondiente del archivo `VERSION`.

## Bugs Conocidos y Fixes Recientes

### TypeError en goal_add_progress (FIXED)
- **Causa**: `g.current_amount += float(amount)` — `Decimal` + `float` → `TypeError`
- **Fix**: Cambiar a `Decimal(amount)` y usar `F()` expressions con `.update()`
- **Archivo**: `goals/views/pages.py:49-71`

### Mensajes flash invisibles (FIXED)
- **Causa**: No había `{% if messages %}` en `base.html`
- **Fix**: Bloque de mensajes al inicio de `<main>` con estilos por tipo

### Sidebar no resalta en sub-páginas de metas (FIXED)
- **Causa**: `current == 'goals:goal_list'` solo matcheaba la lista
- **Fix**: `namespace == 'goals'` en `sidebar.html`

### Race condition en current_amount (FIXED)
- **Causa**: Lectura y escritura en dos pasos separados
- **Fix**: `Goal.objects.filter(pk=pk).update(current_amount=F('current_amount') + amount)`

## Settings Clave

- `LANGUAGE_CODE = 'es-AR'`
- `TIME_ZONE = 'America/Argentina/Buenos_Aires'`
- `DEBUG`: de env `TRACKANT_DEBUG`, default `True`
- `SECRET_KEY`: de env `TRACKANT_SECRET_KEY`, fallback inseguro
- DB: `~/.trackant/db.sqlite3` (creado automáticamente)
- Sin password validators
- REST_FRAMEWORK sin auth, paginación 25 items por página

## Archivos Vacíos Notables

- Todos los `tests.py` son stubs vacíos (solo `import TestCase`)
- `static/css/` y `static/js/` están vacíos (todo es CDN o inline)
- `api/migrations/` no tiene migraciones reales (sin modelos)
- No hay config de linting/formatting (`.flake8`, `pyproject.toml`, etc.)
