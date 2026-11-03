---
layout: default
dataset: true
title: Infografía de grandes incendios forestales
og_image: https://dieghernan.github.io/gifs/assets/social-preview.jpg
og_image_alt: Grandes incendios forestales en España, 2010–2026. Mapa oscuro con
  círculos naranjas proporcionales a la superficie forestal quemada.
og_image_width: 1200
og_image_height: 630
og_image_type: image/jpeg
date: 2025-02-21
last_modified_at: 2026-11-03
excerpt: |
    Infografía de grandes incendios forestales en España a partir de datos de MITECO.
    Elaborada con R.
project_links:
    - url: https://github.com/dieghernan/gifs/
      icon: fab fa-github my-2
      label: GitHub
---

Este proyecto reúne los datos y el código en **R** utilizados para crear una
infografía de grandes incendios forestales (GIF) en España. En este contexto,
GIF se refiere a incendios con al menos 500 hectáreas forestales quemadas.

El conjunto actual contiene 449 registros fechados entre el 27 de febrero de
2010 y el 26 de septiembre de 2026. Estas fechas corresponden al primer y al último
registro del archivo, no a años completos de cobertura. El conjunto no es un
servicio de seguimiento de incendios en tiempo real.

{% include custom/download_card.html %}

<p data-photoswipe-gallery="infographic">
  <a class="chulapa-photoswipe-item" href="{{ '/gif_spain.png' | relative_url }}" aria-label="Ampliar la infografía de grandes incendios forestales">
    <img class="img-fluid" src="{{ '/gif_spain.png' | relative_url }}" width="4200" height="4200" alt="Mapa de España con grandes incendios forestales de 2010 a 2026. El tamaño de los círculos naranjas indica las hectáreas forestales quemadas; un gráfico resume la superficie por año.">
  </a>
</p>

<p class="infographic-download"><a href="{{ site.data.citation.releaseUrl | replace: '/tag/', '/download/' }}/gif_spain.png">Descargar infografía PNG</a></p>

El CSV incluye la provincia, el municipio y sus códigos, la fecha y la
superficie forestal quemada en hectáreas. Los códigos deben leerse como texto
para conservar los ceros iniciales.

Las fechas de inicio de los 41 incendios de 2012 se han recuperado del
informe definitivo y contrastado con EGIF. Las diferencias de superficie
entre ambas fuentes se documentan en la metodología.

Cada fila representa un incendio. Cuando la descripción menciona varios
municipios o provincias, se conserva un único registro y su superficie
completa. Los códigos corresponden al primer municipio y a la primera
provincia mencionados; el mapa utiliza ese municipio como referencia.

Código disponible en <https://github.com/dieghernan/gifs/>.

La infografía se inspira en la técnica de cartografía de luciérnagas
presentada por Dominic Royé (<https://github.com/dominicroye>) en [Firefly
Cartography](https://dominicroye.github.io/blog/firefly-maps/).

## Fuentes de datos

Los datos proceden de las **estadísticas de incendios forestales** del
Ministerio para la Transición Ecológica y el Reto Demográfico (MITECO)
([Estadísticas del MITECO](https://www.miteco.gob.es/es/biodiversidad/temas/incendios-forestales/estadisticas-datos.html)),
incluidas estadísticas definitivas y avances informativos. El conjunto
combina ambas fuentes sin identificar en cada registro si el dato es
definitivo o provisional.

Origen de los datos: Ministerio para la Transición Ecológica y el Reto
Demográfico (MITECO). Recopilación y adaptación: Diego HH. Los datos
se reutilizan conforme al [aviso legal del MITECO](https://www.miteco.gob.es/es/atencion-al-ciudadano/aviso-legal.html),
con obligación de citar la fuente y conservar las condiciones y metadatos
originales. La licencia MIT del repositorio corresponde al código y la
documentación. Este proyecto es independiente y no implica participación ni
respaldo del Ministerio.

La [metodología de recopilación y validación](https://github.com/dieghernan/gifs/blob/main/METODOLOGIA.md)
detalla las fuentes por año, las decisiones, los agregados y las
limitaciones. Se utilizan estadísticas definitivas de 2010–2021 y avances
provisionales de 2022–2026.

El listado de GIF se recopila en `rdata/gif_d2010.xlsx`. El script
[incendios.R](https://github.com/dieghernan/gifs/blob/main/incendios.R)
lee ese archivo y exporta los registros a
`rdata/gif_d2010.csv`. Los códigos de provincia y municipio corresponden a la
codificación del INE
([Códigos de municipios del INE](https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736177031&menu=ultiDatos&idp=1254734710990)).

Para situar los registros en el mapa, el script utiliza el código de municipio
para enlazarlos con las capitales municipales del paquete de **R**
[**mapSpain**](https://ropenspain.github.io/mapSpain/). Los puntos representan
esas ubicaciones de referencia, no el lugar exacto de inicio ni el perímetro
de los incendios. El tamaño de cada círculo refleja la suma de las hectáreas
forestales quemadas de los registros asociados a la misma ubicación. El
gráfico anual también resume únicamente los registros incluidos en el conjunto.

La información de la sesión con la que se ha generado la infografía se
proporciona en el archivo [sessioninfo.txt](sessioninfo.txt).

<!-- citation:start; generated by scripts/citation.rb -->
## Cómo citar

> Hernangómez, D. (2026). *Grandes incendios forestales en España*
> (Version 1.0.0) [Data set].
> https://doi.org/10.5281/zenodo.23929997

<details markdown="1">
<summary>Referencia en BibTeX</summary>

```bibtex
@misc{hernangomez_grandes_incendios,
  author = {Hernangómez, Diego},
  title = {Grandes incendios forestales en España},
  year = {2026},
  version = {1.0.0},
  doi = {10.5281/zenodo.23929997},
  url = {https://dieghernan.github.io/gifs/},
  note = {Data set}
}
```

</details>

El [DOI general](https://doi.org/10.5281/zenodo.23929996) reúne las versiones del proyecto.
Para identificar los datos utilizados en un análisis, cite el DOI de la
versión correspondiente.
<!-- citation:end -->

## Referencias

Royé, Dominic. 2021. “Firefly Cartography.” June 1.
[https://dominicroye.github.io/blog/firefly-maps/](https://dominicroye.github.io/blog/firefly-maps/).
