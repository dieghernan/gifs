---
layout: default
title: Infografía de GIF (Grandes Incendios Forestales)
excerpt: |
    Infografía de GIF (Grandes Incendios Forestales) en base a los datos de MITECO. 
    Creado con el software R.
project_links:
    - url: https://github.com/dieghernan/gifs/
      icon: fab fa-github my-2
      label: GitHub
---

![Incendios forestales en España](https://raw.githubusercontent.com/dieghernan/gifs/refs/heads/main/gif_spain.png)

Infografía creada con **R**. Código disponible en <https://github.com/dieghernan/gifs/>

Infografía inspirada en el trabajo de Dominic Royé
(<https://github.com/dominicroye>) tal y como se muestra en el post [Firefly
cartography](https://dominicroye.github.io/blog/firefly-maps/).

## Fuentes de datos

La información está extraída de las **Estadística incendios forestales** del
MITECO
([link](https://www.miteco.gob.es/es/biodiversidad/temas/incendios-forestales/estadisticas-incendios.html)),
específicamente de Estadísticas Definitivas (hasta 2015) y de Avances
Informativos (resto). El tratamiento de datos consiste en la extracción del
listado de GIF y la asignación a cada incendio del código de provincia y de
municipio correspondiente según el INE
([link](https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736177031&menu=ultiDatos&idp=1254734710990))
mediante la librería de **R**
[**mapSpain**](https://ropenspain.github.io/mapSpain/) para generar la base de
datos `rdata/gif_d2010.csv`.

La información de la sesión con la que se ha generado la infografía se
proporcionan en el archivo [sessioninfo.txt](sessioninfo.txt)

## Referencias

Royé, Dominic. 2021. "Firefly Cartography." June 1,2021.
<https://dominicroye.github.io/blog/firefly-maps/>.
