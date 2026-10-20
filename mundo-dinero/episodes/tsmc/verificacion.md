# Verificación de datos — TSMC: la fábrica que se volvió indispensable

Consulta: 20/10/2026. Estado: ✅ contrastado con datos · ✏️ corregido · 🔎 hecho histórico de conocimiento público, sin documento primario consultado en esta producción.

## Metodología bursátil

- **Serie:** ADR TSM (NYSE), cierres diarios de Financial Modeling Prep (FMP), del 08/10/1997 al 19/10/2026.
  - *Precio*: ajustado por splits y dividendos en acciones, **sin** dividendos en efectivo (`historical-price-eod-light`).
  - *Retorno total*: serie ajustada por dividendos (`historical-price-eod-dividend-adjusted`).
- **Los gráficos** muestran el último cierre de cada mes de la serie de *precio* (`data/TSM_monthly.csv`).
- No se mezcla el ADR con la acción de Taiwán (2330.TW).

| Afirmación (material de referencia) | Resultado con la serie | Estado |
|---|---|---|
| Caída de ~85 % entre feb-2000 y sep-2002 | Máximo 03/02/2000 US$ 25,74 → mínimo 09/10/2002 US$ 3,96 = **−84,6 %**. El mínimo cae en **octubre**, no en septiembre | ✏️ fecha corregida: «entre febrero de 2000 y octubre de 2002» |
| US$ 10.000 → ~US$ 1.500 | 10.000 × 3,96 / 25,74 = **US$ 1.538** | ✅ «unos mil quinientos» |
| Recuperación del máximo en julio de 2016 | Primer cierre ≥ US$ 25,74: **16/03/2016** (precio). Con dividendos reinvertidos: **02/01/2013** | ✏️ la voz dice «en 2016» y agrega la recuperación con dividendos (2013) |
| Caída de ~50 % en 2021–2022 y unos tres años de recuperación | Máximo 14/01/2022 US$ 140,66 → mínimo 03/11/2022 US$ 60,28 = **−57,1 %**; recupera el 06/03/2024 (~2 años) | ✏️ en pantalla se muestra −57 % (la voz no da cifra) |

## Cifras corporativas (Form 20-F 2025, SEC EDGAR, vía FMP)

| Concepto 2025 | NT$ (20-F) | US$ aprox. | Estado |
|---|---|---|---|
| Ingresos | 3.848.511 millones | ≈ 123.000 M | ✅ la voz dice «más de ciento veinte mil millones» |
| Ganancia neta | 1.735.678 millones | ≈ 55.600 M | ✅ «unos cincuenta y cinco mil millones» |
| Margen neto | 45,1 % | — | ✅ |
| Capex (compras de propiedad, planta y equipo) | 1.282.557 millones | ≈ 41.100 M | ✅ «cerca de cuarenta y un mil millones» |
| Inversión planificada 2026 | — | — | 🔎 guía de la empresa: no se cuantifica en pantalla; la voz dice «todavía mayor» |

Conversión: promedio de los cierres mensuales USD/TWD de 2025 (Alpha Vantage), ≈ 31,2 NT$ por dólar. El material de
referencia citaba NT$ 3,809 billones de ingresos (cifra de ventas mensuales informadas); el 20-F auditado dice 3,849.

## Hechos históricos

| Afirmación | Estado | Nota |
|---|---|---|
| TSMC fundada en febrero de 1987 por Morris Chang, con 55 años | 🔎 | Chang nació el 10/07/1931 |
| Chang: Texas Instruments 1958–1983 | 🔎 | 25 años; llegó a dirigir el negocio mundial de semiconductores |
| Estado de Taiwán ~48 %, Philips 27,6 % del capital inicial | 🔎 | Historia corporativa; el resto, inversores privados |
| «No competimos contra nuestros clientes»: modelo foundry puro | 🔎 | Principio declarado por la empresa |
| Nvidia nació sin fábrica; AMD separó sus fábricas (2009) | 🔎 | Ver episodios de Nvidia y AMD |
| Chang vuelve como CEO en 2009 «con 78 años» | ✏️ | Volvió en junio de 2009, con **77 años** (cumplía 78 en julio). Corregido en la voz |
| Taiwán a unos 130 km de China continental | 🔎 | Ancho mínimo del estrecho de Taiwán |
| Arizona, Japón (Kumamoto) operativos; Alemania (Dresde) en construcción | 🔎 | Estado de la primera planta de cada sitio según comunicados de TSMC; conviene reconfirmar antes de publicar |
| Concentración de clientes | 🔎 | La voz lo dice en términos cualitativos; los porcentajes del material (70 % / 76 % / 78 %) no se verificaron y no se muestran |

## Correcciones al texto de locución

1. Se quitaron las notas de producción leídas en voz alta («según la metodología indicada en el material de
   referencia», «estas fechas y magnitudes deben verificarse…», «son cifras que requieren cotejo…») y se reemplazaron
   por los datos verificados de arriba.
2. «entre 2000 y 2002» → «entre febrero de 2000 y octubre de 2002».
3. «Tenía 78 años» → «Tenía 77 años».
4. Ingresos y ganancia 2025 expresados como «más de ciento veinte mil millones» y «unos cincuenta y cinco mil millones».

## Pendiente antes de publicar

- Fotos con licencia de Morris Chang, obleas y fábricas de TSMC (ver `assets/LEEME.md`).
- Reconfirmar el estado de Arizona, Kumamoto y Dresde con el último comunicado de TSMC.
