# Coordenadas EGIF y contraste municipal; no se infiere un datum ausente.
Sys.setlocale("LC_CTYPE", "English_United States.utf8")

parts <- read.csv(
  "dev/egif-location-input.csv",
  colClasses = "character",
  check.names = FALSE,
  fileEncoding = "UTF-8",
  na.strings = ""
)

locations <- data.frame(
  egif_part_id = parts$egif_part_id,
  coordinate_x = parts$coordinate_x,
  coordinate_y = parts$coordinate_y,
  utm_zone = parts$utm_zone,
  datum = parts$datum,
  declared_codmun = parts$codmun,
  source_epsg = NA_integer_,
  longitude = NA_real_,
  latitude = NA_real_,
  location_status = "unknown_crs",
  geo_codmun = NA_character_,
  geo_boundary_code = NA_character_,
  geo_municipality = NA_character_,
  municipality_check = "not_checked",
  boundary_year = "2024",
  boundary_source = "IGN CartoBase ANE / SIANE",
  boundary_resolution = "3",
  stringsAsFactors = FALSE
)

zones <- suppressWarnings(as.integer(parts$utm_zone))
for (i in seq_len(nrow(parts))) {
  zone <- zones[i]
  if (!is.na(zone) && zone %in% 28:31 && !is.na(parts$datum[i])) {
    locations$source_epsg[i] <- switch(
      parts$datum[i],
      ETRS89 = 25800L + zone,
      WGS84 = 32600L + zone,
      ED50 = 23000L + zone,
      REGCAN95 = if (zone == 28) 4083L else NA_integer_,
      NA_integer_
    )
  }
}

x <- suppressWarnings(as.numeric(parts$coordinate_x))
y <- suppressWarnings(as.numeric(parts$coordinate_y))
missing <- is.na(x) | is.na(y) | x <= 0 | y <= 0
locations$location_status[missing] <- "missing_coordinates"
valid <- !missing & !is.na(locations$source_epsg)
for (epsg in unique(locations$source_epsg[valid])) {
  idx <- which(valid & locations$source_epsg == epsg)
  points <- sf::st_as_sf(
    data.frame(x = x[idx], y = y[idx]),
    coords = c("x", "y"),
    crs = epsg
  ) |>
    sf::st_transform(4326)
  xy <- sf::st_coordinates(points)
  locations$longitude[idx] <- xy[, 1]
  locations$latitude[idx] <- xy[, 2]
  locations$location_status[idx] <- "source_coordinates"
}

if (any(valid)) {
  boundaries <- mapSpain::esp_get_munic_siane(
    year = 2024,
    resolution = 3,
    moveCAN = FALSE,
    epsg = 4326,
    cache_dir = "dev/egif-geometry-siane"
  ) |>
    sf::st_make_valid() |>
    sf::st_transform(3035)
  idx <- which(valid)
  points <- sf::st_as_sf(
    locations[idx, ],
    coords = c("longitude", "latitude"),
    crs = 4326,
    remove = FALSE
  ) |>
    sf::st_transform(3035)
  hits <- sf::st_intersects(points, boundaries)
  for (j in seq_along(idx)) {
    i <- idx[j]
    hit <- hits[[j]]
    if (length(hit) == 1) {
      locations$geo_boundary_code[i] <- boundaries$LAU_CODE[hit]
      if (!substr(boundaries$LAU_CODE[hit], 1, 2) %in% sprintf("%02d", 1:52)) {
        locations$municipality_check[i] <- "non_municipal_territory"
        next
      }
      locations$geo_codmun[i] <- boundaries$LAU_CODE[hit]
      locations$geo_municipality[i] <- boundaries$name[hit]
      locations$municipality_check[i] <- if (is.na(parts$codmun[i])) {
        "declared_code_unavailable"
      } else if (parts$codmun[i] == locations$geo_codmun[i]) {
        "matches_declared"
      } else {
        "differs_from_declared"
      }
    } else {
      locations$municipality_check[i] <- if (length(hit)) {
        "multiple_boundaries"
      } else {
        "outside_boundaries"
      }
    }
  }
}

dir.create("data-derived", showWarnings = FALSE)
write.csv(
  locations,
  "data-derived/egif-locations.csv",
  row.names = FALSE,
  na = "",
  fileEncoding = "UTF-8"
)
print(table(locations$location_status))
print(table(locations$municipality_check))
