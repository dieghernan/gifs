# Límites SIANE y capitales municipales IGN, sin desplazar Canarias.
Sys.setlocale("LC_CTYPE", "English_United States.utf8")

boundaries <- mapSpain::esp_get_munic_siane(
  year = 2024,
  resolution = 3,
  moveCAN = FALSE,
  epsg = 4326,
  cache_dir = "dev/egif-geometry-siane"
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
  prov_name = boundaries$ine.prov.name,
  cmun = substr(boundaries$LAU_CODE, 3, 5),
  munic_name = boundaries$name,
  codmun = boundaries$LAU_CODE
)
dictionary <- dictionary[order(dictionary$codmun), ]
dictionary <- dictionary[
  dictionary$cpro %in% sprintf("%02d", 1:52) & !is.na(dictionary$munic_name),
]
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
