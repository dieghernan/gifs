# Conciliación de 2012

Auditoría histórica anterior a la migración a EGIF. Sus valores de referencia
proceden de `data-raw/legacy/fires.csv`. La migración posterior adopta las
superficies EGIF; véase la [metodología actual](../../../METODOLOGIA.md).

Esta auditoría recupera las fechas de los 41 incendios del conjunto, sin
cambiar sus superficies ni incorporar nuevos incendios.

- `egif-parts.csv`: los 44 partes con al menos 500 ha de superficie forestal
  extraídos del Excel descargado de EGIF el 03/11/2026. No es una exportación
  de todos los incendios de 2012 ni una tabla de incendios ya agrupados.
- `report-dates.csv`: las 42 filas provinciales del cuadro 37 del informe
  definitivo, página impresa 76 (página 77 del PDF). Incluye los dos partes
  de Hellín/Moratalla; Andilla ya figura agregado en el informe.
- `sources.json`: procedencia, cobertura observada y SHA-256 de los originales.
  Los ZIP y PDF originales se conservan localmente en `gifs-miteco-audit/`.
- `comparison.csv`: cruce de los 41 incendios por provincia y municipio,
  fechas confirmadas por ambas fuentes, partes asociados y diferencias.
- `unmatched-parts.csv`: Cocentaina, pendiente de revisión porque cruza el
  umbral de 500 ha respecto del informe antiguo.

Reproducir el cruce desde los extractos versionados:

```sh
py scripts/audit_egif_2012.py
```

Este comando solo reproduce la comparación histórica y no modifica los
productos finales. Estos se regeneran con `py scripts/build_dataset.py`.
La aritmética de superficies usa decimales exactos. Las agrupaciones son
explícitas; no se emparejan partes únicamente por superficie.

En aquella revisión se conservaron las superficies del informe para Chulilla
y Llocnou de Sant Jeroni y no se incorporó Cocentaina. La asociación provincial de
Andilla se sustenta en las fechas y horas coincidentes y en la suma del
informe, sin una clave común disponible en el extracto. Véase
[la metodología](../../../METODOLOGIA.md#conciliación-de-egif-de-2012).
