# Metadatos Croissant

El descriptor describe dos unidades relacionadas: partes EGIF y una vista
conciliada de incendios. Cada recurso está disponible en CSV y JSON.
Los RecordSet extraen el JSON mediante JSONPath para conservar códigos
como texto y distinguir valores nulos sin depender de inferencias del CSV.

## Fuentes

- `_data/structured_data.json`: descripción, procedencia, versión en desarrollo y recursos.
- `_data/egif_part_fields.json`: campos del producto de partes.
- `_data/croissant_fields.json`: campos de la vista de incendios.
- `_data/croissant_context.json`: contexto Croissant 1.1.
- `CITATION.cff`: cita de la versión archivada 1.0.0; no se atribuye su DOI a la migración.

`build_croissant.py` genera `croissant.json` y `_data/croissant.json`.
La página incorpora el mismo descriptor una sola vez. No editar esos
archivos generados a mano. La versión en desarrollo no tiene DOI propio.

## Generar y verificar

Primero reconstruir los productos como indica `data-raw/README.md`.
Guardar los cambios de CSV y JSON en un commit local, actualizar
`croissant.sourceRevision` al commit que los contiene y ejecutar:

```sh
py scripts/build_croissant.py
py scripts/build_croissant.py --check
mlcroissant validate --jsonld croissant.json
ruby scripts/citation.rb --check
bundle exec jekyll build
py -m unittest discover -s tests
```

Las huellas y tamaños proceden de los bytes Git para evitar diferencias
CRLF entre sistemas. Las pruebas del lector oficial recorren los dos
productos y verifican códigos, tipos, coordenadas y datos ausentes.

Una rama sin push no está disponible en las URL públicas. Para verificar
la lectura del lector oficial sobre los mismos archivos locales, en PowerShell:

```powershell
$env:GIFS_LOCAL_SNAPSHOT = '1'
py -m unittest discover -s tests
Remove-Item Env:GIFS_LOCAL_SNAPSHOT
```

Esta opción utiliza el mapeo de archivos del lector oficial, sin modificar
el descriptor ni sustituir sus datos por mocks. La prueba de descarga
pública queda para después del push autorizado.
