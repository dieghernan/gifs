# Casos que requieren evidencia adicional

Revisión de la instantánea EGIF descargada el 3 de noviembre de 2026.
Los candidatos no constituyen correspondencias confirmadas. Los datos
de respaldo se conservan mientras no pueda justificarse su sustitución.

## Registros anteriores pendientes

| Registro | Candidatos o discrepancia | Evidencia necesaria |
| --- | --- | --- |
| Montiel, 15/07/2022 | No se ha confirmado un parte equivalente; el informe provisional registra 799,08 ha. | Localización y parte de origen, incluidos posibles partes de otra provincia. |
| Quintanilla del Coco, 24/07/2022 | `2022090115`, Tejada, coincide en fecha; EGIF registra 1.808,04 ha frente a 1.819,69 ha. | Documento que relacione el parte de Tejada con el incendio denominado Quintanilla del Coco. |
| Almonte, 26/07/2022 | `2022210076`, Almonte, comienza el día 25; `2022210075`, Bonares, ya está incorporado. | Resolver la agrupación operativa Bonares-Almonte y comprobar que las superficies de ambos partes sean aditivas. |
| Piloña, 23/03/2023 | `2023330745` registra 58 ha; el avance, 552 ha. | Identificar el foco concreto y confirmar si hubo revisión de superficie o agrupación. |
| Tineo, 29/03/2023, 725 ha | Varios partes de Tineo/Allande próximos; `2023330574` ya está asignado a otro registro. | Identificador o localidad que distinga este fuego de Merillés, Porciles, Navelgas y los focos de Allande. |
| Piloña, 29/03/2023 | Varios partes del mismo día, entre ellos `2023330741`, `2023330754` y `2023330757`, todos menores de 500 ha. | Correspondencia del registro provisional con un foco o agrupación concreta. |
| Piloña, 03/04/2023 | Sin parte equivalente confirmado. | Localidad, hora de inicio o identificador del foco provisional. |
| Valdés, 05/04/2023 | `2023331156`, Navelgas/Tineo, comienza el 27 de marzo y afecta a dos municipios. | Determinar si el registro de Valdés es el mismo incendio o un foco integrado; no basta la semejanza de superficie. |
| Allande, 08/04/2023 | `2023330792`, Villagrufe, registra 444,08 ha frente a las 550 ha del avance. | Confirmar la identidad antes de aplicar una revisión que dejaría el incendio fuera del umbral GIF. |

## Partes grandes sin asignar

- `2022310161`, Valtierra, 17/06/2022: no se suma al parte de Arguedas
  del día 18; difieren fecha, hora y causa declarada.
- `2022090115`, Tejada: posible correspondencia con Quintanilla del Coco.
- `2022210076`, Almonte: revisar junto con Bonares.
- `2023331156`, Navelgas; `2023331157`, Porciles; `2023331158`, Santa
  Coloma; `2023331159`, Pola de Allande; `2023331160`, Bustantigo:
  no se crean cinco incendios nuevos mientras pueda haber correspondencias
  con los registros provisionales o agrupaciones entre focos.

## Revisión de las seis incorporaciones

| Parte | Revisión |
| --- | --- |
| `2012030081`, Cocentaina | Mantener el parte EGIF de 541,02 ha; no figura en la referencia anterior. |
| `2017331093`, Ibias | Mantener las 647,79 ha EGIF. La metodología histórica documenta su exclusión del listado definitivo anterior: es una diferencia de fuentes, no un error de transcripción que deba revertirse automáticamente. |
| `2017331590`, Allande | Mantener las 661,08 ha EGIF. La referencia histórica excluyó una entrada de 661,06 ha; conservar explícita esa discrepancia de fuente. |
| `2022210075`, Bonares | La independencia del incendio sigue pendiente de revisión junto con Almonte. |
| `2022230066`, Torres de Albánchez | Mantener el parte EGIF de 1.432,7663 ha. El punto cae en el territorio SIANE `53050`, no municipal; no sustituir el municipio declarado por uno inventado. |
| `2022230085`, Jódar | Mantener el parte EGIF de 586,9012 ha; no tiene correspondencia confirmada en la referencia anterior. |

La incorporación de estos partes expresa la prioridad de EGIF y no prueba
por sí sola que sus seis registros sean seis incendios independientes.

## Cambios de superficie

`rdata/audit/egif-comparison.csv` conserva el valor anterior, el valor EGIF
y la diferencia para cada incendio. Las mayores diferencias absolutas
afectan a Losacio, Chulilla, Legarda/Guirguillano, Riofrío de Aliste y
Gallipienzo/San Martín de Unx. En los casos ya enlazados se utiliza la
superficie forestal del parte, sin añadir la agrícola ni la no forestal.
Esto permite auditar la revisión, pero no atribuir su causa a una mejora
de medición si la fuente no lo explica.

## Fuentes adicionales

- [Parlamento de Navarra, comparecencia de Interior del 20/12/2022](https://parlamentodenavarra.es/sites/default/files/diarios-sesiones/PRES10071.pdf), pp. 30–32 del PDF: cronología y desalojos de los incendios de junio.
- [Protección Civil, informe de incendios de 2023](https://www.proteccioncivil.es/documents/20121/0/INFORME%2520IIFF%25202023-FINAL%2520%281%29.pdf/803a01c7-98b6-fc44-4b7f-988b2dfbbb08): documenta Navelgas/Foyedo y Valdés/Tineo/Lavadoira desde el 27 de marzo; su agrupación operativa no aporta una equivalencia completa de partes EGIF.
- [Junta de Andalucía, balance de campaña de 2022](https://www.juntadeandalucia.es/organismos/presidenciasanidadyemergencias/servicios/actualidad/noticias/detalle/371248.html): identifica Bonares-Almonte como un incendio operativo activo entre el 25 y el 28 de julio.

Puntagorda y Arafo de 2023 se conservan como respaldo por ausencia de partes
de la provincia 38 en la exportación, separados de esta lista de identidades
pendientes. La falta de registros provinciales no demuestra exhaustividad
de otras provincias ni ausencia de incendios.
