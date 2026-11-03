# Historial de cambios

## 2.0.0 — 2026-11-03

- Publicación de 329 partes EGIF y una vista conciliada de 455 registros, con nueve identidades anteriores y ocho partes pendientes documentados y dos registros de Canarias de 2023 conservados por falta de cobertura EGIF provincial.
- Conciliación documental de tres cambios municipales de 2016–2017 y cuatro incendios de 2022, manteniendo los identificadores estables y adoptando fechas y superficies EGIF.
- Previews para compartir sin el recuadro de Canarias; las descargas conservan sus coordenadas reales y la infografía mantiene su desplazamiento cartográfico.

- Límites y diccionario municipales derivados de IGN SIANE mediante mapSpain, con fuente, año y resolución registrados y separación de códigos de territorios no municipales.

- Tarjetas de descarga tras la infografía, con formato y tamaño de archivo; JSON-LD como catálogo con dos conjuntos independientes y descriptores Croissant por conjunto.

- Productos GeoJSON de partes e incendios en EPSG:4326, con todas sus propiedades y geometría nula cuando no hay coordenadas interpretables.

- Migración a fuentes EGIF estructuradas de 2010–2023, con una fila por parte, identificadores estables, notas, procedencia y una vista de incendios que conserva informes y avances de respaldo.
- Coordenadas EPSG:4326, contraste municipal y distinción explícita de ubicaciones municipales de respaldo; se conservan las coordenadas originales y los casos sin datum.
- Excel anterior archivado; generación reproducible de CSV, auditorías y metadatos desde fuentes versionadas.

- Recuperadas las fechas de inicio de los 41 incendios de 2012, contrastadas entre el informe definitivo y EGIF, con auditoría reproducible de partes provinciales y discrepancias de superficie.

- Tarjeta de descarga del CSV con tamaño, fecha, versión, SHA-256 y DOI, adaptada a móvil y escritorio.
- Cita y metadatos de la versión generados desde `CITATION.cff`, con referencia en BibTeX y comprobación de coherencia antes de publicar.

## 1.0.0 — 2026-11-03

Primera versión auditada del conjunto de grandes incendios forestales en
España.

- Conjunto de 449 incendios con al menos 500 hectáreas forestales quemadas, fechado entre el 27 de febrero de 2010 y el 26 de septiembre de 2026 y disponible en CSV y Excel.
- Revisión de registros frente a las estadísticas definitivas del MITECO de 2010–2021 y los avances provisionales de 2022–2026, con correcciones de fechas, superficies, nombres y códigos territoriales.
- Metodología con fuentes anuales, decisiones de tratamiento, agregados y limitaciones, incluidas las fechas convencionales de 2012 y la cobertura parcial de los datos.
- Infografía y tarjetas para compartir actualizadas con los datos revisados.
- Descriptor Croissant y metadatos de Dataset con un enlace inmutable al CSV, su tamaño y su suma SHA-256.
- Comprobaciones automatizadas de integridad de datos, coherencia de metadatos y lectura del CSV con el validador oficial de Croissant.
- Archivo `CITATION.cff` para citar el conjunto, con autoría, ORCID y condiciones de reutilización de los datos.
