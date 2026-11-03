# Metodología de recopilación y conciliación

Versión en desarrollo de la migración a EGIF. Fuentes descargadas el
3 de noviembre de 2026. La metodología anterior se conserva en
[data-raw/legacy/METODOLOGIA.md](data-raw/legacy/METODOLOGIA.md).

## Fuentes y prioridad

Se conserva la base anterior de 449 incendios como referencia inmutable,
incluidas las fechas de 2012 ya recuperadas y las decisiones territoriales
documentadas. El Excel original queda archivado y deja de ser el maestro.

La fuente principal es [EGIF](https://servicio.mapa.gob.es/incendios/Search/Publico).
Se importan las 14 exportaciones completas de 2010–2023, con
149.290 partes en total. No se interpreta «Cerrado Revisión» como
prueba de cobertura anual completa. Se conserva literalmente el estado del
parte y se documentan recuentos por año y provincia.

Los registros anteriores sin correspondencia conservan su
[informe o avance de origen](data-raw/legacy/sources.csv). La ausencia en
una exportación no basta para excluir un incendio. En 2023 no aparecen
registros de Barcelona, Girona, Lleida, Tarragona, Navarra, Las Palmas ni
Santa Cruz de Tenerife. La ausencia de filas por provincia no prueba por sí
sola que no hubiera incendios.

## Unidades e identificadores

- `egif_part_id` identifica una fila de EGIF y se conserva como texto.
- `fire_id` identifica un incendio del registro propio. Es estable y no se
  renumera al ordenar, cambiar superficies o añadir datos.
- `data-raw/fire-registry.csv` enlaza ambos niveles y conserva la
  correspondencia con cada fila de la base anterior.
- Un incendio puede tener varios partes provinciales. Las agrupaciones
  son explícitas; no se deducen únicamente de superficies similares.

El producto de partes contiene 329 filas. El umbral de 500 ha
se aplica después de agrupar los partes vinculados. Se leen también los
partes menores de 500 ha, de modo que pueden incorporarse a un GIF si
existe una agrupación documentada. Los partes sin asignar que superan el
umbral se conservan como partes, sin inventar un identificador de incendio.
La selección no garantiza que se hayan descubierto todas las agrupaciones
posibles de partes menores de 500 ha.

La vista de incendios contiene 455 registros. Conserva
18 correspondencias anteriores pendientes y no suma automáticamente
los 15 partes seleccionados sin asignar. Por ello, sus agregados
describen la vista conciliada y no un recuento nacional definitivo.

## Conciliación y cambios

Los enlaces revisados se basan en fecha, provincia y municipio, variantes
documentadas de nombres y decisiones territoriales de la base anterior.
Las asociaciones históricas de Lobios/Portugal, Fonfría/Portugal y
As Neves/Portugal se conservan como inferencias identificadas.

En Hermisende y Oímbra, las coordenadas ETRS89 caen en los municipios
españoles de referencia y coinciden en fecha con la base anterior, aunque
EGIF declara origen Portugal. Se marca la correspondencia como espacial
y se conserva el origen declarado.

Hellín/Moratalla (2012) utiliza los partes `2012020224` y `2012300087`;
el informe confirma un solo incendio. Andilla (2012) utiliza
`2012460247` y `2012120050`; coinciden detección y extinción y su suma
reproduce el total del informe. Ontinyent (2010) utiliza `2010460119` y
`2010030107`, con detección y extinción coincidentes y superficie conjunta
coincidente con la base anterior. No existe una clave EGIF común en estos
extractos; las asociaciones quedan registradas para revisión.

EGIF sustituye las superficies de los registros vinculados, conservando
los valores anteriores y sus diferencias en la auditoría. Esto incluye
las revisiones de Chulilla y Llocnou de Sant Jeroni en 2012 y las revisiones
de los avances de 2022–2023. Se incorporan los partes de Cocentaina (2012),
Ibias y Allande (2017), Bonares, Torres de Albánchez y Jódar (2022), sin
correspondencia en la selección anterior. Ibias y Allande se habían
excluido al seguir el informe definitivo; reaparecen al adoptar EGIF como
fuente principal. Su agrupación puede revisarse si aparece nueva evidencia.

Los candidatos por proximidad de fecha y provincia se publican como
candidatos, nunca como enlaces confirmados. En Tineo, por ejemplo, no se
asigna un mismo parte a dos registros anteriores.

## Coordenadas y municipios

Los productos incluyen `longitude` y `latitude` en **EPSG:4326**, en grados
decimales, sin desplazar Canarias y sin intercambiar los ejes. Se conserva
la coordenada original con su huso y datum. La transformación utiliza sf y
PROJ: ETRS89/UTM, REGCAN95/UTM, WGS84/UTM o ED50/UTM cuando el datum está
declarado. Nunca se supone ED50 o ETRS89 cuando falta.

De los 329 partes seleccionados, 202 tienen coordenadas interpretables,
125 carecen de datum y dos carecen de coordenadas. En estos últimos las
columnas geográficas quedan vacías. Vacío significa desconocido, no cero.

Los GeoJSON conservan una Feature por registro y todas sus propiedades,
con identificadores de parte o incendio como `id`. Las geometrías son Point
en orden longitud/latitud, sin desplazar Canarias. Si faltan coordenadas,
`geometry` es nulo. No se incluyen perímetros ni se eliminan esos registros.

La vista de incendios toma el punto del primer parte vinculado con
coordenadas interpretables y lo identifica en `location_part_id`; no es
un centroide ni representa el perímetro completo. Para los demás se utiliza
una capital municipal IGN, con `location_method=municipal_seat`. Las
coordenadas de respaldo no se presentan como coordenadas de inicio.

Los puntos se cruzan con límites municipales GISCO 2024 mediante
`mapSpain::esp_get_munic(moveCAN = FALSE)`. Se conservan por separado
el municipio declarado y `geo_codmun`/`geo_municipality`. Una discrepancia
no provoca una corrección automática: puede reflejar error, redondeo,
origen exterior, proximidad a un límite o cambios de límites municipales.
No se asigna el municipio más cercano a puntos fuera de los límites.

## Reproducción y comprobaciones

1. Los ZIP originales se conservan en `data-raw/egif/` con SHA-256,
   fecha de descarga, recuentos y estado observado. No se dispone de
   capturas de los filtros; el año se verifica en cada fila de `Campania`.
2. `scripts/egif.py` lee los XLSX sin Excel ni dependencias Python externas.
3. `scripts/build_dataset.py` valida identificadores, años, duplicados,
   superficies y relaciones; utiliza aritmética decimal exacta.
4. `scripts/geolocate_parts.R` genera la transformación y el contraste
   municipal; se valida que sus entradas sigan coincidiendo con los partes.
5. `py scripts/build_dataset.py --check` comprueba todos los productos
   frente a las fuentes versionadas. Las pruebas cubren agrupaciones,
   umbrales, duplicados, respaldo y coordenadas desconocidas.

El diccionario de campos está en `_data/egif_part_fields.json` y
`_data/croissant_fields.json`. El descriptor Croissant describe los dos
recursos, sus claves, campos opcionales y huellas; no atribuye el DOI de la
versión archivada 1.0.0 a estos datos en desarrollo.

## Auditoría y limitaciones

- [Diferencias por incendio](rdata/audit/egif-comparison.csv).
- [Partes sin asignar](rdata/audit/egif-unassigned-parts.csv).
- [Candidatos sin confirmar](rdata/audit/egif-candidates.csv).
- [Cobertura observada por provincia](rdata/audit/egif-coverage.csv).
- [Recuentos y agregados](rdata/audit/egif-summary.json).

No se suman las superficies de los productos de partes e incendios.
Las superficies acumuladas pueden incluir terrenos quemados varias veces
y no representan una huella territorial única. Las fuentes de respaldo
mantienen sus limitaciones y carácter provisional; no se completan años
ni se eliminan registros por ausencia en EGIF. Los casos pendientes quedan
explícitos hasta disponer de evidencia suficiente.
