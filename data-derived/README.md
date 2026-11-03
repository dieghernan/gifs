# Datos espaciales derivados

- `egif-locations.csv`: transformación de las coordenadas originales a
  EPSG:4326 y cruce con límites municipales GISCO 2024. Se reproduce con
  `scripts/geolocate_parts.R` después de preparar sus entradas. Las
  coordenadas, el datum, el huso y el código declarado se contrastan con
  el origen antes de generar los productos.
- `fire-map-locations.csv`: coordenadas de dibujo de la vista de incendios,
  generadas por `incendios.R`. Solo Canarias está desplazada para el mapa.
  No deben utilizarse como coordenadas geográficas del incendio; las
  coordenadas reales están en los productos finales y en las columnas
  `source_longitude` y `source_latitude` de este archivo.

Las capitales municipales de respaldo proceden de IGN mediante mapSpain.
Los límites municipales proceden de GISCO, edición 2024, mediante mapSpain.
No se supone que esos límites reproduzcan los del año de cada incendio.
