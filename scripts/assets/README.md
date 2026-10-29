# Social card sources

`municipal-centers.csv` and `regions.geojson` are derived from IGN data distributed
by mapSpain. Regional geometry uses the 2024 boundaries at resolution 1.
Coordinates use EPSG:4258 with the Canary Islands moved into a mainland inset,
matching the original infographic. Fire records remain in `rdata/gif_d2010.csv`.

To refresh the geometry from R with mapSpain and sf installed:

```r
m <- mapSpain::esp_get_capimun(moveCAN = TRUE) |> sf::st_transform(4258)
xy <- sf::st_coordinates(m)
write.csv(data.frame(codmun = m$LAU_CODE, lon = xy[, 1], lat = xy[, 2]),
          "scripts/assets/municipal-centers.csv", row.names = FALSE)
a <- mapSpain::esp_get_ccaa(resolution = 1, year = 2024, moveCAN = TRUE) |>
  sf::st_transform(4258)
sf::st_write(a, "scripts/assets/regions.geojson", delete_dsn = TRUE)
```

Map data attribution: Instituto Geográfico Nacional, CC BY 4.0.
Fira Sans font files retain their bundled OFL license.
