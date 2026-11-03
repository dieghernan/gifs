# Fuentes del conjunto

El maestro son las fuentes estructuradas y el registro de correspondencias.
El Excel anterior se conserva solo como archivo histórico.

- `egif/`: ZIP originales completos y manifiesto SHA-256, fecha y cobertura observada.
- `legacy/fires.csv`: referencia inmutable de los 449 registros anteriores.
- `legacy/gif_d2010.xlsx`: Excel histórico, no utilizado por el generador.
- `legacy/sources.csv`: enlaces anuales de informes y avances de respaldo.
- `fire-registry.csv`: identificadores estables, enlaces a partes y decisiones.
- `reconciliation/`: evidencia documental de las correspondencias revisadas.
- `municipalities.csv`: diccionario IGN SIANE 2024 (resolución 3); códigos como texto.
- `municipality-aliases.csv`: variantes explícitas de nombres EGIF.
- `municipal-centers-4326.csv`: capitales municipales IGN sin desplazar Canarias.

## Actualizar

Importar una carpeta de nuevas exportaciones, indicando su fecha real:

```sh
py scripts/import_egif.py CARPETA --download-date AAAA-MM-DD
```

Una instantánea anual distinta exige `--replace`, después de revisar los
cambios. El importador no decide correspondencias ni elimina registros.
Mantener los identificadores existentes al editar `fire-registry.csv`;
asignar un nuevo identificador una sola vez cuando se incorpora un incendio.
Las filas de respaldo sin partes no deben convertirse en partes ficticios.
El campo opcional `reference_location=egif_origin` sustituye el municipio
de referencia anterior por el origen del primer parte enlazado cuando
existe una corrección documental. Si está vacío se conserva la referencia
anterior. No equivale a una lista de todos los municipios afectados.

Regenerar coordenadas cuando cambien las fuentes, las agrupaciones o los
alias municipales:

```sh
py scripts/build_dataset.py --prepare-locations
Rscript scripts/geolocate_parts.R
py scripts/build_dataset.py
py scripts/build_dataset.py --check
Rscript incendios.R
py scripts/social_banners.py
```

La transformación espacial necesita R, sf y mapSpain. Las reconstrucciones
ordinarias de los CSV usan la caché versionada `data-derived/egif-locations.csv`
y solo necesitan Python estándar. El generador rechaza una caché cuyo parte,
coordenadas, datum, huso o código municipal declarado hayan cambiado.
`scripts/update_geography.R` actualiza los diccionarios y capitales;
esa actualización requiere repetir el contraste espacial.

Los metadatos Croissant se regeneran después del commit de datos, usando
el commit que contiene ambos CSV como `croissant.sourceRevision`.
La lectura pública de esa URL solo puede comprobarse después del push.
