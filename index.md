---
layout: default
dataset: true
title: Infografía de grandes incendios forestales
og_image: https://dieghernan.github.io/gifs/assets/social-preview.jpg
og_image_alt: Grandes incendios forestales en España, 2010–2025. Mapa oscuro con
  círculos naranjas proporcionales a la superficie forestal quemada.
og_image_width: 1200
og_image_height: 630
og_image_type: image/jpeg
excerpt: |
    Infografía de grandes incendios forestales en España a partir de datos de MITECO.
    Elaborada con R.
project_links:
    - url: https://github.com/dieghernan/gifs/
      icon: fab fa-github my-2
      label: GitHub
---

![Mapa de España con grandes incendios forestales de 2010 a 2025. El tamaño de los círculos naranjas indica las hectáreas forestales quemadas; un gráfico resume la superficie por año.](https://raw.githubusercontent.com/dieghernan/gifs/refs/heads/main/gif_spain.png)

Este proyecto reúne los datos y el código **R** utilizados para crear una
infografía de grandes incendios forestales (GIF) en España. En este contexto,
GIF se refiere a incendios con al menos 500 hectáreas forestales quemadas.

El conjunto actual contiene 404 registros fechados entre el 27 de febrero de
2010 y el 21 de septiembre de 2025. Estas fechas describen los registros
incluidos; no representan un servicio de seguimiento en tiempo real.

<a class="btn btn-primary mb-3" href="https://raw.githubusercontent.com/dieghernan/gifs/main/rdata/gif_d2010.csv">Descargar dataset en CSV</a>

Código disponible en <https://github.com/dieghernan/gifs/>.

Infografía inspirada en el trabajo de Dominic Royé
(<https://github.com/dominicroye>) tal y como se muestra en el post [Firefly
cartography](https://dominicroye.github.io/blog/firefly-maps/).

## Fuentes de datos

La información está extraída de las **estadísticas de incendios forestales** del
MITECO
([Estadísticas del MITECO](https://www.miteco.gob.es/es/biodiversidad/temas/incendios-forestales/estadisticas-incendios.html)),
incluidas estadísticas definitivas y avances informativos.

<!-- FIXME: Confirmar por año qué datos son definitivos y cuáles provisionales. -->
El tratamiento de datos consiste en la extracción del
listado de GIF y la asignación a cada incendio del código de provincia y de
municipio correspondiente según el INE
([Códigos de municipios del INE](https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736177031&menu=ultiDatos&idp=1254734710990))
mediante el paquete de **R**
[**mapSpain**](https://ropenspain.github.io/mapSpain/) para generar la base de
datos `rdata/gif_d2010.csv`.

La información de la sesión con la que se ha generado la infografía se
proporciona en el archivo [sessioninfo.txt](sessioninfo.txt).

## Referencias

Royé, Dominic. 2021. “Firefly Cartography.” June 1, 2021.
<https://dominicroye.github.io/blog/firefly-maps/>.
