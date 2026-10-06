/* TrackAnt — parser de lenguaje natural para cargar transacciones.
   Sin IA: reglas simples sobre texto en español (es-AR). */
(function () {
  'use strict';

  var INCOME_WORDS = ['cobre', 'cobro', 'recibi', 'recibo', 'me pagaron', 'me depositaron', 'depositaron', 'deposito', 'sueldo', 'aguinaldo', 'ingreso', 'ingrese', 'gane', 'ganancia', 'venta', 'vendi'];
  var EXPENSE_WORDS = ['gaste', 'gasto', 'pague', 'pago', 'compre', 'compro', 'salio', 'me salio', 'cargue', 'debo', 'transferi', 'saque'];

  function norm(s) {
    return (s || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/\s+/g, ' ').trim();
  }

  var UNITS = { cero: 0, un: 1, uno: 1, una: 1, dos: 2, tres: 3, cuatro: 4, cinco: 5, seis: 6, siete: 7, ocho: 8, nueve: 9, diez: 10, once: 11, doce: 12, trece: 13, catorce: 14, quince: 15, dieciseis: 16, diecisiete: 17, dieciocho: 18, diecinueve: 19, veinte: 20, treinta: 30, cuarenta: 40, cincuenta: 50, sesenta: 60, setenta: 70, ochenta: 80, noventa: 90, cien: 100, ciento: 100, doscientos: 200, trescientos: 300, cuatrocientos: 400, quinientos: 500, seiscientos: 600, setecientos: 700, ochocientos: 800, novecientos: 900 };

  // ponytail: soporta unidades/decenas/centenas + "mil"/"millon". Decenas compuestas ("treinta y cinco") suman; no cubre "ciento veinte mil" perfecto.
  function wordsToNumber(text) {
    var tokens = text.split(/\s+/);
    var total = 0, current = 0, found = false;
    for (var i = 0; i < tokens.length; i++) {
      var w = tokens[i];
      if (w === 'mil' || w === 'miles') {
        current = (current || 1) * 1000;
        total += current; current = 0; found = true;
      } else if (w === 'millon' || w === 'millones') {
        current = (current || 1) * 1000000;
        total += current; current = 0; found = true;
      } else if (UNITS[w] != null) {
        current += UNITS[w]; found = true;
      }
    }
    total += current;
    return found ? total : null;
  }

  function parseAmount(text) {
    var m = text.match(/\d[\d.,]*/);
    if (m) {
      var raw = m[0], s;
      if (/^\d{1,3}(\.\d{3})+(,\d{1,2})?$/.test(raw)) s = raw.replace(/\./g, '').replace(',', '.');
      else if (/^\d{1,3}(,\d{3})+(\.\d{1,2})?$/.test(raw)) s = raw.replace(/,/g, '');
      else if (/^\d+,\d{1,2}$/.test(raw)) s = raw.replace(',', '.');
      else s = raw;
      var n = parseFloat(s);
      return isNaN(n) ? null : n;
    }
    return wordsToNumber(text);
  }

  function parseDate(text, now) {
    var d = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    if (/\banteayer\b/.test(text)) d.setDate(d.getDate() - 2);
    else if (/\bayer\b/.test(text)) d.setDate(d.getDate() - 1);
    var md = text.match(/\b(\d{1,2})[\/\-](\d{1,2})(?:[\/\-](\d{2,4}))?\b/);
    if (md) {
      var day = parseInt(md[1], 10), mon = parseInt(md[2], 10);
      var year = md[3] ? parseInt(md[3], 10) : now.getFullYear();
      if (year < 100) year += 2000;
      d = new Date(year, mon - 1, day);
    }
    return d;
  }

  function pad(n) { return String(n).padStart(2, '0'); }
  function toISO(d) { return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }

  function nlParse(text, categories, now) {
    now = now || new Date();
    var n = norm(text);
    var type = 'EXPENSE';
    for (var i = 0; i < INCOME_WORDS.length; i++) { if (n.indexOf(INCOME_WORDS[i]) !== -1) { type = 'INCOME'; break; } }
    if (type === 'EXPENSE') {
      for (var j = 0; j < EXPENSE_WORDS.length; j++) { if (n.indexOf(EXPENSE_WORDS[j]) !== -1) { type = 'EXPENSE'; break; } }
    }
    // quitar fechas antes de buscar el monto (ej: "12/09" no es plata)
    var amountText = n.replace(/\b\d{1,2}[\/\-]\d{1,2}(?:\/\d{2,4})?\b/g, ' ');
    var amount = parseAmount(amountText);
    var date = toISO(parseDate(n, now));

    var categoryId = null, categoryName = null;
    if (categories && categories.length) {
      var best = null;
      for (var k = 0; k < categories.length; k++) {
        var cn = norm(categories[k].name);
        if (cn && n.indexOf(cn) !== -1) {
          if (!best || cn.length > norm(best.name).length) best = categories[k];
        }
      }
      if (best) { categoryId = best.id; categoryName = best.name; }
    }

    return { type: type, amount: amount, date: date, categoryId: categoryId, categoryName: categoryName, note: (text || '').trim() };
  }

  function nlParseSelfTest() {
    var cats = [{ id: 1, name: 'Bar' }, { id: 2, name: 'Comida' }, { id: 3, name: 'Sueldo' }];
    var now = new Date(2026, 9, 6); // 6 oct 2026
    var r1 = nlParse('hoy gasté 6000 pesos en el bar', cats, now);
    console.assert(r1.type === 'EXPENSE', 'r1 type', r1);
    console.assert(r1.amount === 6000, 'r1 amount', r1);
    console.assert(r1.date === '2026-10-06', 'r1 date', r1);
    console.assert(r1.categoryName === 'Bar', 'r1 cat', r1);
    var r2 = nlParse('ayer compré una hamburguesa y me salió 3.500', cats, now);
    console.assert(r2.type === 'EXPENSE' && r2.amount === 3500, 'r2', r2);
    console.assert(r2.date === '2026-10-05', 'r2 date', r2);
    var r3 = nlParse('cobré el sueldo de seis mil', cats, now);
    console.assert(r3.type === 'INCOME' && r3.amount === 6000, 'r3', r3);
    console.assert(r3.categoryName === 'Sueldo', 'r3 cat', r3);
    var r4 = nlParse('el 12/09 pagué 800 de comida', cats, now);
    console.assert(r4.amount === 800, 'r4 amount', r4);
    console.assert(r4.date === '2026-09-12', 'r4 date', r4);
    console.assert(r4.categoryName === 'Comida', 'r4 cat', r4);
    return true;
  }

  window.nlParse = nlParse;
  window.nlParseSelfTest = nlParseSelfTest;
  if (typeof location !== 'undefined' && location.search.indexOf('nltest') !== -1) {
    nlParseSelfTest();
  }
})();
