# Metodología de recopilación y validación

Fecha de revisión: **3 de noviembre de 2026**. Este documento describe la
versión revisada de los datos y los controles de publicación de esta
actualización.

## Alcance y unidad de observación

El conjunto reúne grandes incendios forestales (GIF) en España desde 2010.
Se incluyen incendios con al menos 500 hectáreas de superficie forestal
quemada. Cada fila representa un incendio, incluso cuando afecta a varios
municipios o provincias. No se incluyen todos los incendios forestales ni
se ofrece un seguimiento en tiempo real.

Los archivos [CSV](rdata/gif_d2010.csv) y [Excel](rdata/gif_d2010.xlsx)
contienen los mismos siete campos: `prov_name`, `cpro`, `munic_name`, `cmun`,
`codmun`, `date` y `area_forestal_ha`. La fecha representa el inicio del
incendio, con la excepción convencional de 2012 explicada más adelante.
La superficie se expresa en hectáreas forestales, no en superficie total
afectada cuando esta incluye terrenos no forestales.

## Fuentes y criterios de prioridad

La fuente principal es el Ministerio para la Transición Ecológica y el Reto
Demográfico (MITECO), mediante sus
[estadísticas definitivas](https://www.miteco.gob.es/es/biodiversidad/temas/incendios-forestales/estadisticas-datos.html)
y [avances informativos](https://www.miteco.gob.es/es/biodiversidad/temas/incendios-forestales/estadisticas-avances.html).
Para esta revisión se utilizaron estadísticas definitivas de 2010–2021 y
avances provisionales de 2022–2026. La clasificación corresponde a las
fuentes consultadas en esta revisión; debe comprobarse de nuevo al actualizar
el conjunto. Los siete campos de datos no incluyen una columna de estado.

Se prioriza el listado definitivo sobre el avance del mismo año. Un cambio
de nombre, origen o ámbito territorial requiere comprobar que se trata del
mismo incendio antes de sustituir el registro. No se emparejan incendios
únicamente por tener superficies parecidas ni por ser las únicas filas
sin correspondencia.

Las fuentes complementarias sirven para resolver identidades, topónimos y
afecciones territoriales. No sustituyen la superficie forestal del MITECO
por estimaciones de prensa, superficies municipales o estimaciones de
satélite. Los nombres de archivo que contienen «def» no bastan para decidir
la prioridad: se contrasta el contenido con el listado definitivo actual.

### Recopilación y extracción

1. Se localizan los informes anuales desde las páginas oficiales y se
   conservan sus enlaces, año y carácter definitivo o provisional.
2. Se extraen las tablas individuales de GIF de los PDF. Cuando el texto
   no permite leer la tabla, se utiliza OCR y comprobación visual; fue
   necesario para la tabla de 2010. Se revisan separadores decimales,
   separadores de millares y filas partidas entre páginas.
3. Para 2019 se contrasta la tabla definitiva de Power BI mediante la
   captura aportada por el mantenedor. El PDF consultado no mostraba el
   listado individual. La transcripción de las 15 filas suma 30.789,09 ha,
   igual al total visible. No se presenta como una descarga automatizada
   de Power BI.
4. Para 2026 se contrasta el listado estructurado publicado en la
   [estimación provisional del MITECO](https://www.miteco.gob.es/content/dam/miteco/es/biodiversidad/temas/incendios-forestales/estimacion_provisional.html).
   Es una fuente mutable. El último incendio incluido en el archivo tiene
   fecha 26/09/2026; esto no equivale a una cobertura anual completa.
5. Se cruzan los registros por año, fecha y municipio, con revisión de las
   excepciones. Se comparan las superficies con aritmética decimal y se
   conservan los valores anteriores en la auditoría de trabajo.

## Tratamiento de los registros

Los nombres de municipio y provincia son la referencia para comprobar los
códigos. Se corrigen erratas y se normalizan los textos en español,
respetando los nombres propios y sus tildes. Las descripciones territoriales
pueden conservar varios municipios o provincias indicados por el MITECO.

Los códigos se contrastan con la
[codificación municipal del INE](https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736177031&menu=ultiDatos&idp=1254734710990).
`cpro` corresponde a dos dígitos, `cmun` a tres y `codmun` a su concatenación
de cinco dígitos. Los archivos actuales pueden representarlos numéricamente,
sin ceros iniciales; al compararlos o reutilizarlos deben reconstruirse esas
anchuras. La coherencia aritmética del código no demuestra por sí sola que
el municipio sea correcto.

Cuando hay varios municipios, los códigos corresponden al primero de la
descripción y a su provincia. Se conserva una sola fila y la superficie del
incendio completo: no se reparte entre municipios ni se suma a la cifra del
avance que sustituye. Los cambios de orden territorial se trasladan también
a los códigos.

Las superficies y las fechas simples se actualizan con el definitivo cuando
la identidad del incendio está establecida. Las incorporaciones,
exclusiones y asociaciones dudosas de esta auditoría se resolvieron mediante
decisiones expresas del mantenedor. CSV y Excel se ordenan por fecha
ascendente y, para una misma fecha, por superficie descendente.

### Excepciones y decisiones relevantes

| Caso | Tratamiento aplicado | Limitación o fundamento |
| --- | --- | --- |
| 2012: fechas | Se conserva `2012-12-31` en los 41 incendios. | Es una fecha convencional para identificar el año; el informe utilizado no aporta fechas individuales. No permite análisis de estacionalidad. |
| 2012: Hellín / Moratalla | Una fila, Albacete / Murcia, código 02037 y 6.549,47 ha. | Se unifican las dos entradas provinciales del mismo incendio; se conserva su superficie conjunta. |
| 2013: Fonfría | Se conserva Fonfría, Zamora, 49071, 01/08/2013 y 837,56 ha. | El MITECO indica origen en Portugal; el mantenedor confirma Fonfría como municipio español afectado. |
| 2016: Bolbaite | Sustituye a Chella con código 46073 y 1.564,32 ha. | Se adopta el listado definitivo. |
| 2016: San Justo / Encinedo | Una fila: San Justo (San Ciprián) / Encinedo (Santa Eulalia de Cabrera), Zamora / León, 49189, 11/09/2016 y 1.197,52 ha. | La información contemporánea conecta ambos ámbitos; se sustituye la cifra anterior, sin sumarla. |
| 2017: exclusiones | Se retiran Ibias, 20/04, 647,79 ha; Allande, 14/10, 661,06 ha; Ponteareas, 15/10, 645,18 ha. | No figuran como registros independientes en el listado definitivo. Se conservan las otras entradas de Allande y Ponteareas. |
| 2017: As Neves / Portugal | Se conserva As Neves, Pontevedra, 36034, 15/10/2017, con 3.084,52 ha. | Asociación aprobada con la entrada Portugal del definitivo. El origen portugués está documentado, pero no se obtuvo un identificador EGIF común: la correspondencia sigue siendo una inferencia. |
| 2017: Vega de Pas | Se incorpora Cantabria, 39097, 10/03/2017 y 675 ha. | Registro del definitivo ausente en el archivo anterior. |
| 2019: definitivo | Se actualizan nueve superficies y la fecha de Salas a 02/03; se incorpora Encinedo, León, 24067, 06/01 y 539,54 ha. | Los 15 registros suman el total visible en Power BI. |
| 2020: Villalcampo y Torvizcón | Se excluye Villalcampo, 19/10, 664,29 ha; se incorpora Torvizcón, Granada, 18179, 28/12 y 617,51 ha. | Se sigue el listado definitivo. |
| 2021: Santa Coloma / Bellprat | Santa Coloma de Queralt / Bellprat, Tarragona / Barcelona, 43139, 24/07/2021 y 1.312,79 ha. | Se adopta el orden de origen y la fecha del definitivo, conservando ambos municipios. |
| 2021: Genalguacil | Sustituye a Jubrique con código 29057, 08/09/2021 y 8.651,26 ha. | Se adopta el listado definitivo. |

Para San Justo / Encinedo se consultó la
[información contemporánea de ICAL publicada en Astorga Digital](https://www.astorgadigital.com/intervienen-incendio-santa-eulalia-crabrera/)
y una [ponencia del CIFP de Almázcara](https://pfcyl.es/sites/default/files/eventos/adjuntos/coco-cipalmazcara.pdf).
Para el origen portugués de As Neves se consultó el
[Diario de Sesiones del Parlamento de Galicia del 17/10/2017](https://www.parlamentodegalicia.es/sitios/web/BibliotecaDiarioSesions/D100044.pdf).
Estas referencias sustentan el contexto territorial, no una nueva medición
de superficie.

## Resultados agregados y fuentes anuales

El archivo revisado contiene **449 incendios** y suma
**1.311.239,9728 ha** de superficie forestal quemada. Se conserva la precisión
de la fuente, incluida la de los registros provisionales de 2026. Las fechas
del primer y último registro son 27/02/2010 y 26/09/2026.

Los totales siguientes se calculan sobre las filas del archivo; no son la
superficie quemada por todos los incendios de España. Las sumas entre años
pueden incluir terrenos quemados más de una vez y no representan una huella
territorial única. Las cifras definitivas y provisionales se distinguen por
año en la tabla.

| Año | Incendios | Superficie forestal (ha) | Fuente utilizada |
| --- | ---: | ---: | --- |
| 2010 | 11 | 12.538,79 | [Definitiva](https://www.miteco.gob.es/content/dam/miteco/es/biodiversidad/temas/incendios-forestales/publicacion2010_def_tcm30-132568.pdf) |
| 2011 | 24 | 26.034,47 | [Definitiva](https://www.miteco.gob.es/content/dam/miteco/es/biodiversidad/temas/incendios-forestales/losincendiosforestalesenespanaano2011_tcm30-132591.pdf) |
| 2012 | 41 | 135.580,04 | [Definitiva](https://www.miteco.gob.es/content/dam/miteco/es/biodiversidad/temas/incendios-forestales/los_incendios_forestales_en_espana_2012_tcm30-132581.pdf) |
| 2013 | 17 | 19.690,12 | [Definitiva](https://www.miteco.gob.es/content/dam/miteco/es/biodiversidad/temas/incendios-forestales/los_incendios_forestales_en_espana_2013_tcm30-132601.pdf) |
| 2014 | 7 | 9.805,83 | [Definitiva](https://www.miteco.gob.es/content/dam/miteco/es/biodiversidad/temas/incendios-forestales/incendios_forestales_en_espana_2014_tcm30-425396.pdf) |
| 2015 | 16 | 39.790,32 | [Definitiva](https://www.miteco.gob.es/content/dam/miteco/es/biodiversidad/temas/incendios-forestales/iiff_2015_def_tcm30-442974.pdf) |
| 2016 | 22 | 33.323,70 | [Definitiva](https://www.miteco.gob.es/content/dam/miteco/es/biodiversidad/temas/incendios-forestales/IIFF_2016.pdf) |
| 2017 | 54 | 99.666,48 | [Definitiva](https://www.miteco.gob.es/content/dam/miteco/es/biodiversidad/temas/incendios-forestales/IIFF_2017.pdf) |
| 2018 | 3 | 4.924,57 | [Definitiva](https://www.miteco.gob.es/content/dam/miteco/es/biodiversidad/temas/incendios-forestales/IIFF_2018.pdf) |
| 2019 | 15 | 30.789,09 | [Definitiva, Power BI](https://app.powerbi.com/view?r=eyJrIjoiYzE0MzhkZGItYzZlOC00NGU1LTlkNWUtZjdkZjY1NTM1MWFhIiwidCI6ImRlODFhNTc4LTgxYWEtNGQzNS1hNWQ0LWZlZWQ4MTZiMTY1NCIsImMiOjl9) |
| 2020 | 19 | 34.186,78 | [Definitiva](https://www.miteco.gob.es/content/dam/miteco/es/biodiversidad/temas/incendios-forestales/IIFF_2020.pdf) |
| 2021 | 18 | 47.230,07 | [Definitiva](https://www.miteco.gob.es/content/dam/miteco/es/biodiversidad/temas/incendios-forestales/IIFF_2021.pdf) |
| 2022 | 57 | 216.441,75 | [Avance provisional](https://www.miteco.gob.es/content/dam/miteco/es/biodiversidad/temas/incendios-forestales/avance_1_enero_31_diciembre_2022_tcm30-560521.pdf) |
| 2023 | 19 | 52.823,97 | [Avance provisional](https://www.miteco.gob.es/content/dam/miteco/es/biodiversidad/temas/incendios-forestales/Avance_1_enero_31_diciembre_2023.pdf) |
| 2024 | 16 | 16.564,03 | [Avance provisional](https://www.miteco.gob.es/content/dam/miteco/es/biodiversidad/temas/incendios-forestales/Avance_1_enero_31_diciembre_2024.pdf) |
| 2025 | 63 | 310.108,07 | [Avance provisional](https://www.miteco.gob.es/content/dam/miteco/es/biodiversidad/temas/incendios-forestales/Avance_IIFF_2025_rev.pdf) |
| 2026 | 47 | 221.741,89 | [Avance provisional](https://www.miteco.gob.es/content/dam/miteco/es/biodiversidad/temas/incendios-forestales/estimacion_provisional.html) |
| **Total** | **449** | **1.311.239,97** | Cifras redondeadas a dos decimales para esta tabla. |

El [PDF de 2019](https://www.miteco.gob.es/content/dam/miteco/es/biodiversidad/temas/incendios-forestales/IIFF_2019.pdf)
se conserva como referencia anual, pero el contraste individual se realizó
con el Power BI enlazado en la tabla. El avance de 2019 sirvió como contraste
inicial y fue sustituido por ese listado definitivo.

## Validaciones realizadas

- **Integridad de formatos:** 449 filas en CSV y Excel, con igualdad de
  valores en las siete columnas tras leer ambos archivos de forma
  independiente con **readr** y **openxlsx**.
- **Orden:** fecha ascendente y superficie descendente para los empates,
  verificado sobre el archivo final.
- **Duplicados exactos:** no se encontraron filas idénticas. Esta prueba no
  demuestra por sí sola que no existan duplicados de un incendio con
  descripciones distintas; esos casos requieren el contraste documental.
- **Códigos territoriales:** comprobación de nombres y códigos, corrección
  de incoherencias y verificación de la composición `cpro` + `cmun` =
  `codmun` tras completar los ceros iniciales.
- **Contraste documental:** revisión anual de fechas, municipios y
  superficies, con las decisiones territoriales descritas arriba. Las
  fechas de 2012 se excluyen de la afirmación de coincidencia de fechas
  reales.
- **Superficies:** el CSV de comparación de trabajo contiene 449 filas y no
  deja diferencias de superficie respecto de las fuentes seleccionadas.
  La comprobación exacta detectó y corrigió tres diferencias residuales de
  0,01 ha: Esgos (2017), Robledo de Chavela y Vilar de Barrio (2020).
- **Control de 2019:** 15 registros y 30.789,09 ha, coincidentes con la tabla
  definitiva visible en Power BI.
- **Control agregado:** recuentos y sumas anuales calculados directamente
  desde el CSV y reconciliados con el total del archivo.

La carpeta local `gifs-miteco-audit/` conserva informes, extracciones,
captura de Power BI, valores anteriores, decisiones y el archivo
`comparacion-registros.csv`. Está excluida de Git. Este documento conserva
en el repositorio la síntesis metodológica, las decisiones relevantes y
los enlaces públicos, sin depender de esa carpeta para su lectura.

## Limitaciones y mantenimiento

No quedan decisiones abiertas por año en esta revisión. Esto no convierte
los avances en estadísticas definitivas ni elimina las incertidumbres
documentadas de Fonfría y As Neves. Las fuentes provisionales deben revisarse
cuando el MITECO publique nuevas versiones.

El mapa generado con **mapSpain** utiliza capitales municipales como
ubicaciones de referencia. Los puntos no representan el lugar exacto de
inicio ni el perímetro del incendio. Un registro intermunicipal se sitúa
mediante el primer municipio; no debe interpretarse como una distribución
espacial de toda la superficie afectada.

Los mapas y las imágenes para compartir se regeneran desde los datos
revisados. El JSON-LD de Dataset y el descriptor Croissant comparten
descripción, fechas, fuentes y condiciones de reutilización. Croissant
apunta a una revisión Git inmutable del CSV y declara su tamaño y SHA-256.
La compilación de Jekyll, el validador oficial de Croissant y las pruebas
de integración comprueban los productos antes de publicar. La comprobación
del despliegue se realiza después del envío a GitHub.

En futuras actualizaciones se debe registrar la fecha de consulta, la
versión de la fuente y los cambios aplicados; repetir las comprobaciones
de identidad, formato, códigos, orden y agregados; actualizar este
documento y regenerar los productos derivados. Una URL oficial mutable
no permite reconstruir por sí sola una versión histórica: conviene
conservar una copia de trabajo de la fuente utilizada.

## Atribución y reutilización

Origen de los datos: MITECO. Recopilación y adaptación: Diego HH.
La reutilización debe respetar el
[aviso legal del MITECO](https://www.miteco.gob.es/es/atencion-al-ciudadano/aviso-legal.html).
La licencia MIT del repositorio corresponde al código y la documentación;
no sustituye las condiciones de la fuente de datos. El proyecto es
independiente y no implica participación ni respaldo del Ministerio.
