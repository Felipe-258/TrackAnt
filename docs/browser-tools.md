# Browser Automation — TrackAnt

## Obscura vs Chrome DevTools

### Instalación
Obscura está instalado en `~/.local/bin/obscura`. No requiere Chrome.

### Cuándo usar cada uno

| Tarea | Obscura | Chrome DevTools |
|-------|---------|-----------------|
| Scraping / extracción de contenido | ✅ Preferido | ✅ |
| Llenado de formularios | ✅ Preferido | ✅ |
| Navegación básica | ✅ Preferido | ✅ |
| **Screenshots** | ❌ | ✅ Obligatorio |
| **Performance tracing** | ❌ | ✅ Obligatorio |
| **Lighthouse audits** | ❌ | ✅ Obligatorio |
| **Device emulation** | ❌ | ✅ Obligatorio |
| **File uploads** | ❌ | ✅ Obligatorio |
| Anti-detección / stealth | ✅ | ❌ |

### Obscura — Comandos útiles

```bash
# Fetch con evaluación JS
~/.local/bin/obscura fetch https://example.com --eval "document.title"

# Extract HTML
~/.local/bin/obscura fetch https://example.com --dump html

# Extraer links
~/.local/bin/obscura fetch https://example.com --dump links

# Markdown
~/.local/bin/obscura fetch https://example.com --dump markdown

# Scraping paralelo
~/.local/bin/obscura scrape url1 url2 url3 --concurrency 10 --eval "document.title"

# Stealth mode (anti-detección)
~/.local/bin/obscura fetch https://example.com --stealth
```

### Chrome DevTools — Capacidades únicas

Las herramientas `chrome-devtools_*` siguen siendo necesarias para:
- `take_screenshot` — QA visual
- `performance_start_trace` — Análisis de performance
- `lighthouse_audit` — Accesibilidad, SEO, best practices
- `emulate` — Testing responsive (viewport, network throttling)
- `upload_file` — Testing de uploads
- `take_heapsnapshot` — Debug de memoria
