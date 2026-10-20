# Verificación de datos — Nvidia: de dos derrumbes a la era de la IA

Estado: ✅ consistente con la fuente · ⚠️ depende de la metodología / verificar · ❌ incorrecto

## Datos bursátiles

Serie usada para los gráficos: cierres **mensuales** ajustados de NVDA (Alpha Vantage, descargados el 20/10/2026,
`data/NVDA_monthly_adjusted.csv`). Las cifras exactas del guion (89,7 % y 85,1 %) provienen de la serie **diaria**
de investmentvisual.com, que no se pudo consultar desde el entorno de producción.

| Afirmación | Lo que muestra la serie mensual | Estado |
|---|---|---|
| Máximo en enero de 2002 | Cierre mensual más alto: dic 2001 (0,510) ≈ ene 2002 (0,501). El máximo intradía fue en enero (alto 72,66 USD sin ajustar) | ⚠️ coherente; la fecha exacta depende de la serie diaria |
| Caída de 89,7 % en ~9 meses | Mínimo de cierre mensual: sep 2002 (0,065) → −87 % desde ene 2002. Con cierres diarios la caída es mayor | ⚠️ verosímil; confirmar con la serie diaria |
| USD 10.000 → ~USD 1.030 | 10.000 × (1 − 0,897) = 1.030 | ✅ aritmética coherente con el 89,7 % |
| Recupera en noviembre de 2006 | El cierre mensual supera al de ene 2002 en oct 2006 | ⚠️ coherente (±1 mes según cierre diario/mensual) |
| Máximo en octubre de 2007 | Cierres mensuales: sep 2007 0,829 · oct 2007 0,809; el máximo diario cae en oct 2007 | ⚠️ coherente |
| Mínimo en noviembre de 2008, −85,1 % | Mínimo mensual: nov 2008 (0,171) → −79 % en cierres mensuales | ⚠️ verosímil con cierres diarios |
| Recupera en abril de 2016 (8,5 años) | Con ajuste por dividendos ya lo supera en mar 2016; sin dividendos, más tarde | ⚠️ depende de si se incluyen dividendos |

Los gráficos muestran la serie mensual y lo indican en pantalla («Cierres mensuales ajustados · Alpha Vantage ·
porcentajes del guion: serie diaria»). Las marcas de fecha siguen al guion.

## Datos históricos

| Afirmación | Fuente | Estado |
|---|---|---|
| Fundada en abril de 1993 por Jensen Huang, Chris Malachowsky y Curtis Priem | Cronología oficial de Nvidia | ✅ |
| La idea surge en un Denny's de San José, California | Relato de la empresa y de Huang en entrevistas | ✅ (relato de la empresa) |
| NV1 (1995), vendido en la Diamond Edge 3D | Cronología oficial / registros de producto | ✅ |
| NV1 no estaba alineado con Direct3D | Historia técnica ampliamente documentada (renderizado por superficies cuadráticas vs. triángulos) | ✅ |
| Despidos en 1996 | Relatos de la historia de la empresa | ✅ |
| En 1997, caja para ~un mes de sueldos | Relato de Jensen Huang («a 30 días de quebrar»); el guion lo atribuye correctamente | ✅ atribuido |
| RIVA 128 (1997), más de un millón de unidades en cuatro meses | Cronología oficial de Nvidia | ✅ |
| Alianza con TSMC en 1998 | Cronología oficial de Nvidia | ✅ |
| GeForce 256 (1999), «la primera GPU» | Cronología oficial (término popularizado por Nvidia) | ✅ |
| CUDA (2006) | Cronología oficial (anunciada en noviembre de 2006) | ✅ |
| Despegue de la IA generativa 2022–2023 | Contexto público (ChatGPT, nov 2022) | ✅ |

Ninguna corrección alteró el guion. Pendiente antes de publicar: confirmar las cifras diarias en investmentvisual.com.
