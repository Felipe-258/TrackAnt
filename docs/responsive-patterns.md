# Patrones Responsive — TrackAnt

## Formularios — stacking en mobile
Todos los formularios usan `flex flex-col gap-4 sm:flex-row` para que los campos se apilen en mobile y se distribuyan en fila en desktop. Los anchos fijos (`w-32`, `w-36`) se aplican con `sm:` prefix.

## Botones de acción — igualar ancho
Footer de formularios y confirmaciones de delete usan `grid grid-cols-2 gap-3` para que Cancelar y Guardar/Eliminar tengan el mismo ancho. Los botones Cancelar tienen `text-center`.

## Transaction list — search toggle mobile
En mobile, el search es un ícono que expande un input full-width debajo del toolbar. En desktop, el input siempre es visible. Usa Alpine.js `searchOpen` con `sm:hidden` / `hidden sm:block`.

## Transaction cards mobile
`transaction_row.html` tiene layout dual: tabla para `sm:` y cards para `sm:hidden`. Las cards mobile muestran: fecha arriba, categoría debajo (misma columna), monto a la derecha, y three-dot menu. No muestran tags.

## Income/Expense lists
`income_list.html` y `expense_list.html` son templates muertos — no se usan. Las vistas `income_list` y `expense_list` renderizan `transaction_list.html` con `list_type` filtrado. En mobile usan las mismas cards que la lista de transacciones.

## Three-dot menu (acciones en dropdown)
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

## Dashboard — 2 columnas en mobile
KPI cards usan `grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4`. Padding/texto/iconos reducidos en mobile (`p-3 sm:p-5`, `text-lg sm:text-2xl`, `h-7 w-7 sm:h-9 sm:w-9`).

## Hormiguero — compacto en mobile
`min-h-[180px] sm:min-h-[300px]`. Weather effects y weather badge ocultos en mobile (`hidden sm:block`). Goal name label en `top-2 left-4`. Queen ant z-index `z-10` (debajo de sidebar `z-20`). Container `overflow-visible` para que el tooltip de la "i" sobresalga.

## Bottom Tab Bar (PWA standalone)
5 tabs: Home, Ingresos, Gastos, Metas, Más. Todos con `px-2`, `text-[10px]`, iconos `lucide` (1.25em). Safe area insets via `padding-bottom: var(--safe-bottom)`.
