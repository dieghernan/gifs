# Diccionario municipal GISCO y capitales municipales IGN, sin desplazar Canarias.
Sys.setlocale("LC_CTYPE", "English_United States.utf8")

boundaries <- mapSpain::esp_get_munic(
  year = 2024,
  moveCAN = FALSE,
  epsg = 4326,
  cache_dir = "dev/egif-geometry"
)
seats <- mapSpain::esp_get_capimun(moveCAN = FALSE) |>
  sf::st_transform(4326)
xy <- sf::st_coordinates(seats)
centers <- data.frame(
  codmun = seats$LAU_CODE,
  longitude = xy[, 1],
  latitude = xy[, 2]
)
dictionary <- data.frame(
  cpro = substr(boundaries$LAU_CODE, 1, 2),
  prov_name = seats$ine.prov.name[match(
    substr(boundaries$LAU_CODE, 1, 2),
    seats$cpro
  )],
  cmun = substr(boundaries$LAU_CODE, 3, 5),
  munic_name = boundaries$LAU_NAME,
  codmun = boundaries$LAU_CODE
)
dictionary <- dictionary[order(dictionary$codmun), ]
centers <- centers[order(centers$codmun), ]
write.csv(
  dictionary,
  "data-raw/municipalities.csv",
  row.names = FALSE,
  na = "",
  fileEncoding = "UTF-8"
)
write.csv(
  centers,
  "data-raw/municipal-centers-4326.csv",
  row.names = FALSE,
  na = "",
  fileEncoding = "UTF-8"
)
