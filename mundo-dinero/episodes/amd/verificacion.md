# Verificación de datos — AMD: la empresa que dejó de fabricar para volver a competir

Consulta: 20/10/2026. Estado: ✅ contrastado · ⚠️ coherente, depende de la metodología · 🔎 hecho histórico de conocimiento público, sin documento primario consultado en esta producción.

## Fuentes de datos usadas

- **Precios:** Alpha Vantage `TIME_SERIES_MONTHLY_ADJUSTED` (AMD), con ajuste por splits. AMD no pagó dividendos
  en el período, así que el ajuste por dividendos es irrelevante. Archivo: `data/AMD_monthly_adjusted.csv`
  (columnas high/low sin ajustar: el split 2:1 de agosto de 2000 obliga a dividir por 2 los valores previos).
- **Estados financieros:** Alpha Vantage `INCOME_STATEMENT` y `BALANCE_SHEET` (anuales), normalizados a partir de los
  10-K presentados ante la SEC.

## Cifras financieras y bursátiles

| Afirmación del guion | Dato | Estado |
|---|---|---|
| En 2015 la acción llegó a US$ 1,61 | Mínimo intradía de jul-2015: US$ 1,61 (cierre mensual más bajo: sep-2015, US$ 1,715) | ✅ |
| Perdía dinero (2015) | Resultado neto 2015: −US$ 660 M | ✅ |
| Más deuda que liquidez (2015) | Deuda total US$ 2.237 M vs. efectivo + inversiones de corto plazo US$ 785 M; patrimonio neto −US$ 412 M | ✅ |
| Diez años después facturó más de US$ 34.000 M | Ingresos 2025: US$ 34.639 M (2015: US$ 3.991 M) | ✅ |
| 2000–2002: caída de ~94 % | Máximo intradía jun-2000: US$ 97,00 / 2 = US$ 48,50 (ajustado por split) → mínimo intradía oct-2002: US$ 3,10 → −93,6 % | ✅ (intradía) |
| US$ 10.000 → ~US$ 640 | 10.000 × 3,10 / 48,50 = 639 | ✅ |
| Caída superior al 90 % desde el máximo de 2006 hasta fines de 2008 | Máximo intradía mar-2006 US$ 42,70 → mínimo intradía nov-2008 US$ 1,62 → −96,2 %. Cierres mensuales: ene-2006 US$ 41,80 → dic-2008 US$ 2,16 → −94,8 % | ✅ |
| Las pérdidas se acumularon (2006–2008) | Resultado neto: 2006 −166 M · 2007 −3.379 M · 2008 −3.098 M; deuda total fin 2008: 4.776 M | ✅ |

Los gráficos de pantalla usan **cierres mensuales** (por eso el pico y el piso visibles difieren de los intradía);
cada gráfico lo indica en su nota al pie, junto con la caída intradía que menciona la voz.

## Hechos históricos

| Afirmación | Estado | Nota |
|---|---|---|
| Fundada en 1969 por Jerry Sanders y otros siete (ex Fairchild Semiconductor) | 🔎 | Historia corporativa de AMD (1 de mayo de 1969) |
| IBM exigió una segunda fuente; Intel y AMD firmaron un acuerdo (1982) | 🔎 | Acuerdo de licencia cruzada de 1982 |
| La relación terminó en litigios | 🔎 | Arbitraje desde 1987; acuerdo final en 1995 |
| Compra de NexGen en 1996, base del K6 | 🔎 | Cierre a comienzos de 1996; K6 lanzado en 1997 |
| Athlon en 1999 | 🔎 | Lanzamiento en junio de 1999 |
| Opteron y Athlon 64 en 2003; AMD64 extiende x86 a 64 bits con compatibilidad | 🔎 | Opteron (abril) y Athlon 64 (septiembre) de 2003 |
| Compra de ATI en 2006 por ~US$ 5.400 M | 🔎 | Anunciada en jul-2006, cerrada en oct-2006 |
| Separación de las fábricas en 2009, creación de GlobalFoundries | 🔎 | Marzo de 2009, con ATIC (Abu Dabi). AMD siguió atada por contratos de suministro (WSA) durante años: la separación fue progresiva |
| Bulldozer no revirtió su posición; chips para PlayStation y Xbox | 🔎 | Bulldozer 2011; PS4 y Xbox One (2013) usan chips semipersonalizados de AMD |
| Lisa Su, directora ejecutiva desde 2014 | 🔎 | Asumió en octubre de 2014 |
| Zen; Ryzen y EPYC en 2017 | 🔎 | Ryzen (marzo) y EPYC (junio) de 2017 |
| Producción con TSMC; dificultades de Intel en sus procesos | 🔎 | Zen 2 en 7 nm de TSMC (2019); retrasos de Intel en 10 nm |
| Compra de Xilinx en 2022, operación en acciones | 🔎 | Cerrada el 14/02/2022, pago 100 % en acciones |
| EPYC e Instinct en centros de datos e IA; Nvidia como rival central | 🔎 | Contexto público |

## Correcciones al guion

1. Escena s48: la frase original («…según los datos que deberán contrastarse con su informe anual antes de publicar
   este video») era una nota de producción. Como el dato quedó contrastado (US$ 34.639 M), la narración dice:
   «…según su informe anual».
2. Sin otras correcciones: las cifras del guion coinciden con las series consultadas.

## Pendiente antes de publicar

- Confirmar los hechos 🔎 contra los documentos primarios (10-K, comunicados) si se quiere citar página y fecha.
- Agregar fotos con licencia de Jerry Sanders, Lisa Su y de los productos (ver `assets/LEEME.md`); sin ellas, las
  escenas muestran tarjetas tipográficas e ilustraciones rotuladas.
