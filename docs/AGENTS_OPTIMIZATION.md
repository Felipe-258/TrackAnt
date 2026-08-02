# PROMPT: Optimizar AGENTS.md para cualquier proyecto

## TAREA

Optimizar el `AGENTS.md` de un proyecto para:
1. Reducir tokens (objetivo: -30% a -50%)
2. Agregar información crítica que falta (gaps)
3. Mover secciones largas a `docs/` separados

## PROCESO

### Paso 1: Leer AGENTS.md actual

Identificar:
- Líneas totales
- Secciones redundantes o demasiado verbose
- Información que se puede inferir del código

### Paso 2: Explorar gaps con task agent

Lanzar task agent tipo "explore" para encontrar:
- Apps/modelos no documentados
- Patrones de código críticos no documentados
- Settings importantes faltantes
- Signals, services, management commands
- Relaciones entre apps
- Config fields que afectan comportamiento

### Paso 3: Clasificar gaps por prioridad

- **CRÍTICO**: Sin esto, un agente no puede trabajar correctamente
- **ALTO**: Información que ahorra consultas frecuentes
- **MEDIO**: Útil pero no bloqueante
- **BAJO**: Nice-to-have

### Paso 4: Decidir estructura final

#### Opción A: Todo en AGENTS.md (proyectos simples)
- Objetivo: <150 líneas
- Solo info crítica

#### Opción B: AGENTS.md + docs/ (proyectos complejos)
- AGENTS.md: ~150-200 líneas (info crítica)
- docs/: Detalle profundo para referencia

### Paso 5: Crear/mover archivos

1. `docs/[topico]-patterns.md` ← Secciones de implementación
2. `docs/[topico]-system.md` ← Detalle de sistemas complejos
3. Reescribir `AGENTS.md` optimizado

## ESTRUCTURA AGENTS.md OPTIMIZADO

```markdown
# [NOMBRE_PROYECTO] — Guía para Agentes

## Resumen del Proyecto
- Descripción en 1-2 líneas
- Stack principal

## Stack Tecnológico
- Tabla compacta
- Versiones pinned si aplica

## Estructura de Directorios
- Lista plana comprimida (sin archivos individuales)

## [Sistema Crítico] (si existe)
- Ej: Multi-tenancy, Auth, Permissions
- Patrón que TODAS las vistas usan

## Apps y Sus Propósitos
- Por cada app: modelos + feature clave + warning crítico
- 1-3 líneas por app

## Modelos — Relaciones Clave
- Diagrama ASCII de relaciones principales

## API REST (si aplica)
- Tabla de endpoints

## URLs de Páginas
- Lista compacta

## Sistema de Diseño (si aplica)
- Solo paleta de colores + layout key

## Patrones de Código
- Por cada patrón: 1-2 líneas + ejemplo si es complejo

## Convenciones Importantes
- Lista numerada, 1 línea c/u
- Incluir: git, testing, deployment

## Comandos de Desarrollo
- Solo comandos esenciales

## Settings Clave
- Lista de settings que afectan comportamiento

## Bugs Conocidos (Lecciones)
- Solo patrones que causaron bugs (3-5 máx)
```

## CONVENCIONES DE COMPRESIÓN

1. **Eliminar**: Archivos vacíos, bugs ya resueltos, info inferible del código
2. **Comprimir**: Estructura directorios a lista plana, apps a 1-3 líneas
3. **Mover a docs/**: Patrones responsive, browser tools, sistemas complejos
4. **Mantener igual**: Convenciones, settings, commands, patrones críticos

## DOCS SEPARADOS (crear solo si es necesario)

- `docs/responsive-patterns.md` — Si hay muchos patrones mobile/desktop
- `docs/browser-tools.md` — Si hay herramientas de testing/automation
- `docs/[sistema].md` — Si hay sistemas complejos (auth, multi-tenancy, etc.)

## EJEMPLO DE APLICACIÓN

### Antes (439 líneas)
- Estructura directorios verbose (30 líneas)
- Apps descritas en exceso (67 líneas)
- Patrones responsive en AGENTS.md (45 líneas)
- Browser tools en AGENTS.md (50 líneas)
- Bugs conocidos redundantes (18 líneas)

### Después (294 líneas + 3 docs)
- Estructura comprimida (18 líneas)
- Apps concisas (40 líneas)
- Patrones responsive → `docs/responsive-patterns.md`
- Browser tools → `docs/browser-tools.md`
- Colony system → `docs/colony-system.md` (nuevo)
- Bugs comprimidos (5 líneas)
- **Reducción: -33% en AGENTS.md**

### Gaps típicos a buscar

| Categoría | Ejemplos |
|-----------|----------|
| **Modelos faltantes** | Modelos generados por signals, modelos intermedios |
| **Auth/Permisos** | Sistema de usuarios, roles, middleware |
| **Multi-tenancy** | Filtros por tenant, datos globales vs privados |
| **Auto-creación** | Signals, services que crean datos en otras apps |
| **Config fields** | Campos que controlan comportamiento visible |
| **Settings** | Variables que afectan middleware, auth, uploads |
| **Commands** | Management commands disponibles |
| **API gaps** | Endpoints no documentados, ViewSets especiales |
