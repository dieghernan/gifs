# Preparación de la primera release

Estado: borrador local. Versión propuesta: `1.0.0`; etiqueta: `v1.0.0`.
La fecha de publicación y el DOI están pendientes de asignación.

## Notas de la release

### Grandes incendios forestales en España — v1.0.0

Primera versión auditada del conjunto de grandes incendios forestales en
España desde 2010. Contiene 449 incendios, fechados entre el 27 de febrero
de 2010 y el 26 de septiembre de 2026, con una superficie forestal quemada
acumulada de 1.311.239,9728 ha.

Incluye los datos en CSV y Excel, la metodología de recopilación y
validación, la infografía y el código utilizado para generarla. El
descriptor Croissant documenta los siete campos y enlaza una instantánea
inmutable del CSV con su suma SHA-256.

Los datos proceden de estadísticas definitivas del MITECO para 2010–2021
y avances provisionales para 2022–2026. Las fechas de 2012 son convencionales
y solo identifican el año. Los extremos temporales del archivo no indican
años completos de cobertura; el conjunto no ofrece seguimiento en tiempo
real. Los puntos del mapa representan capitales municipales de referencia,
no el origen exacto ni el perímetro de los incendios.

Origen de los datos: MITECO. Recopilación y adaptación: Diego Hernangómez.
La reutilización de los datos sigue el aviso legal del MITECO; el código y
la documentación se distribuyen bajo MIT. El proyecto es independiente y
no implica respaldo del Ministerio.

## Archivos de la publicación

El archivo del repositorio debe contener, como mínimo:

- `rdata/gif_d2010.csv` y `rdata/gif_d2010.xlsx`.
- `METODOLOGIA.md`, `README.md` y `CHANGELOG.md`.
- `gif_spain.png`, `incendios.R` y `sessioninfo.txt`.
- `croissant.json`, sus fuentes en `_data/` y los scripts de generación.
- `CITATION.cff`, `LICENSE` y los avisos de terceros incluidos en el proyecto.

Como adjuntos de la release de GitHub, ofrecer también el CSV, el Excel y la
infografía para facilitar la descarga. Comprobar en Zenodo qué archivos se
han archivado; los adjuntos de GitHub no deben ser la única copia del material.

## Comprobaciones antes de publicar

1. Revisar y guardar los cambios finales de imágenes y datos. Comprobar la
   igualdad de valores entre CSV y Excel y revisar visualmente la infografía.
2. Ejecutar las comprobaciones descritas en `scripts/README-croissant.md`:
   regeneración, validador oficial, compilación de Jekyll y pruebas.
3. Revisar `CITATION.cff`: título, autor, ORCID, versión y condiciones de
   reutilización. Añadir `date-released` y el año de `preferred-citation`
   cuando se conozca la fecha efectiva de publicación. Sustituir también
   «En preparación» en [CHANGELOG.md](CHANGELOG.md) por esa fecha y comprobar
   que sus novedades coinciden con las notas de la release.
4. Conectar el repositorio con Zenodo antes de publicar la release. Revisar
   la configuración del registro como conjunto de datos y la separación
   entre las condiciones del MITECO y la licencia MIT del código. El campo
   `license-url` de CFF documenta las condiciones de los datos, pero no se
   debe dar por hecho que la integración lo importe correctamente.
5. Si se necesita `.zenodo.json` para controlar la importación, prepararlo y
   validarlo antes de etiquetar. Zenodo da prioridad a ese archivo sobre
   `CITATION.cff`; ambos deben describir la misma publicación.
6. Crear la etiqueta y publicar la release sobre el commit revisado. Usar
   las notas anteriores como descripción.
7. Comprobar el registro archivado: tipo, archivos, autoría, versión,
   cobertura, atribución y condiciones de reutilización.

## Incorporación del DOI

Cuando Zenodo asigne el DOI de la versión, añadirlo a `doi` y
`preferred-citation.doi` en `CITATION.cff`. Usar el DOI de esa versión para
identificar esta instantánea y el DOI general para enlazar el proyecto a
través de sus versiones.

Añadir la cita y el enlace a Zenodo al README y a la web. Actualizar los
metadatos fuente en `_data/structured_data.json`, regenerar Croissant y
ajustar las pruebas que actualmente comprueban que no existe una versión
numerada. No editar a mano los descriptores generados.

Si el DOI se obtiene después de publicar, incorporarlo en un commit
posterior sin mover la etiqueta publicada. Si se quiere incluir el DOI
dentro de los archivos de la primera versión, reservarlo en un borrador de
Zenodo antes de cerrar el commit y publicar después ese mismo depósito.

## Referencias de publicación

- [Integración con GitHub](https://help.zenodo.org/docs/github/).
- [Metadatos de Zenodo](https://help.zenodo.org/docs/github/describe-software/zenodo-json/).
- [Versionado de DOI](https://zenodo.org/help/versioning).
