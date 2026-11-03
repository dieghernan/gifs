# GIF España desde 2010
Sys.setlocale("LC_CTYPE", "English_United States.utf8")
# Datos generados desde exportaciones EGIF y fuentes MITECO de respaldo.
# Estadísticas de Incendios Forestales:
# https://www.miteco.gob.es/es/biodiversidad/temas/incendios-forestales/estadisticas-incendios.html

# 1. Librerías ----
# Data wrangling
library(tidyverse)
library(lubridate)
# Espacial
library(mapSpain)
library(sf)
# Gráficos
library(showtext)
library(sysfonts)
library(ggshadow)
library(ggtext)

# Extra: utilities
library(sessioninfo)

# 2. Carga datos y depura ----
gif_fires <- read_csv(
  "rdata/gif_d2010.csv",
  col_types = cols(
    .default = col_character(),
    date = col_date(),
    area_forestal_ha = col_double(),
    longitude = col_double(),
    latitude = col_double()
  )
)

sum(gif_fires$area_forestal_ha)

gif_fires |>
  as_tibble() |>
  mutate(y = year(date)) |>
  group_by(y) |>
  summarise(ha_total = sum(area_forestal_ha)) |>
  arrange(desc(y))

gif_fires_sf <- gif_fires |>
  filter(!is.na(longitude), !is.na(latitude)) |>
  st_as_sf(coords = c("longitude", "latitude"), crs = 4326, remove = FALSE) |>
  st_transform(4258) |>
  mutate(name_ine = munic_name) |>
  arrange(desc(date))

canary_points <- gif_fires_sf$cpro %in% c("35", "38")
if (any(canary_points)) {
  map_geometry <- st_geometry(gif_fires_sf)
  map_geometry[canary_points] <- st_geometry(esp_move_can(gif_fires_sf[
    canary_points,
  ]))
  st_geometry(gif_fires_sf) <- map_geometry
}

any(st_is_empty(gif_fires_sf))

dir.create("data-derived", showWarnings = FALSE)
display_xy <- st_coordinates(gif_fires_sf)
write.csv(
  data.frame(
    fire_id = gif_fires_sf$fire_id,
    source_longitude = gif_fires_sf$longitude,
    source_latitude = gif_fires_sf$latitude,
    map_longitude = display_xy[, 1],
    map_latitude = display_xy[, 2]
  ),
  "data-derived/fire-map-locations.csv",
  row.names = FALSE
)

# Expect FALSE

# 3. Plot principal ----

# Preparo fuentes y colores

font_add(
  "fira",
  regular = "scripts/assets/fira-sans/FiraSans-Regular.ttf",
  bold = "scripts/assets/fira-sans/FiraSans-Bold.ttf"
)

# Colores básicos del plot
# https://www.schemecolor.com/fire-color-scheme.php
# The Fire Color Scheme palette has 6 colors which are Barn Red (#801100),
# Engineering International Orange (#B62203), Sinopia (#D73502),
# Orange (#FC6400), Philippine Orange (#FF7500) and Golden Poppy (#FAC000).
firepal <- c("#801100", "#B62203", "#FC6400", "#FF7500", "#FAC000")


# Paso las coordenadas a columnas para usarlos con geom_glow
coords <- gif_fires_sf |>
  st_drop_geometry() |>
  bind_cols(st_coordinates(gif_fires_sf)) |>
  group_by(prov_name, munic_name, X, Y) |>
  summarise(area_ha = sum(area_forestal_ha)) |>
  ungroup()


# Extramos shapes auxiliares de españa
ccaa <- esp_get_ccaa(resolution = 1, year = 2024, moveCAN = TRUE) |>
  st_transform(st_crs(gif_fires_sf))

provincias <- esp_get_prov(resolution = 1, year = 2024, moveCAN = TRUE) |>
  st_transform(st_crs(ccaa))

can_provincias <- esp_get_can_provinces(
  moveCAN = TRUE,
  epsg = st_crs(ccaa)$epsg
)

canbox <- esp_get_can_box(moveCAN = TRUE) |>
  st_transform(st_crs(ccaa))


# Prepara el texto de títulos y subtítulos

texttitle <- paste0(
  "<span style='color:",
  firepal[3],
  ";'>Grandes Incendios Forestales</span>**(GIF)**<sup>1</sup> en España ",
  "<span style='color:",
  firepal[3],
  ";'>(",
  min(year(gif_fires$date)),
  "-",
  max(year(gif_fires$date)),
  ")"
)

textsub <- paste0(
  "<sup>1</sup> Incendios que presentan <span style='color:",
  firepal[3],
  ";'>al menos 500 hectáreas forestales quemadas</span>"
)

# Main plot

showtext_auto()

main <- ggplot(ccaa) +
  geom_sf(fill = "grey10", color = NA) +
  geom_sf(data = provincias, fill = NA, color = "grey18", linewidth = 0.15) +
  geom_sf(fill = NA, color = "grey28", linewidth = 0.25) +
  geom_sf(
    data = can_provincias,
    color = "grey18",
    linewidth = 0.15,
    linetype = "dashed"
  ) +
  geom_sf(data = canbox, color = "grey28", linewidth = 0.25) +
  geom_glowpoint(
    data = coords,
    aes(
      x = X,
      y = Y,
      size = area_ha
    ),
    color = firepal[3],
    alpha = 0.8,
    shadowsize = 3,
    shadowalpha = 0.02,
    shadowcolour = firepal[2]
  ) +
  scale_size_continuous(
    range = c(.5, 10),
    breaks = c(1000, 5000, 10000, 20000, 30000),
    labels = scales::label_number(
      big.mark = ".",
      decimal.mark = ","
    )
  ) +
  guides(
    size = guide_legend(
      title = "hectáreas forestales quemadas",
      direction = "horizontal",
      title.position = "top",
      keywidth = 10,
      title.hjust = 0,
      label.hjust = .5,
      nrow = 1,
      byrow = TRUE,
      reverse = FALSE,
      label.position = "bottom"
    )
  ) +
  theme_void() +
  theme(
    text = element_text(color = "grey80", family = "fira"),
    plot.background = element_rect(fill = "black"),
    plot.margin = margin(t = 20, l = 20),
    plot.title = element_markdown(size = 110, hjust = .5),
    plot.subtitle = element_markdown(
      size = 65,
      hjust = .5,
      margin = margin(t = 10)
    ),
    legend.position = "bottom",
    legend.title = element_text(
      color = "grey80",
      size = 50,
      margin = margin(t = 20, b = 10)
    ),
    legend.text = element_text(
      color = "grey80",
      size = 70
    ),
    plot.caption.position = "plot",
    plot.caption = element_text(
      size = 40,
      face = "plain",
      hjust = 0,
      lineheight = .5,
      margin = margin(t = 40, b = 5)
    )
  ) +
  labs(
    title = texttitle,
    subtitle = textsub,
    caption = paste0(
      "©",
      year(Sys.Date()),
      " Diego HH https://dieghernan.github.io.",
      " Las hectáreas se refieren únicamente a hectáreas forestales",
      " afectadas.\nDatos: Estadísticas de Incendios Forestales, MITECO.",
      " EGIF, informes y avances. Ubicación EGIF o referencia municipal."
    )
  )


# Para check visual, cuando se usa showtext_auto() las fuentes funcionan
# de una manera distinta entre el device plot y el archivo guardado
ggsave("main.png", main, dpi = 300, width = 4200, height = 4200, units = "px")


# 4. Plot secundario 1 (años) ----

years <- gif_fires |>
  mutate(year = year(date)) |>
  group_by(year) |>
  summarise(overall = sum(area_forestal_ha))


sum(years$overall) |> prettyNum(big.mark = ".", decimal.mark = ",")

texttitleins1 <- sum(years$overall) |>
  prettyNum(big.mark = ".", decimal.mark = ",") |>
  paste("ha.")

textsubins1 <- "forestales quemadas"


inset1 <- ggplot(years, aes(x = year)) +
  geom_col(aes(y = overall), fill = firepal[5], alpha = 0.6) +
  geom_smooth(aes(y = overall), se = FALSE, color = firepal[3], linewidth = 2) +
  coord_flip() +
  scale_x_reverse(breaks = unique(years$year)) +
  scale_y_continuous(
    labels = c("-", "", "100", "", "200", "", "300"),
    breaks = c(0, 50000, 100000, 150000, 200000, 250000, 300000)
  ) +
  theme_minimal() +
  theme(
    plot.background = element_blank(),
    panel.grid = element_blank(),
    panel.grid.major.x = element_line(
      color = alpha(firepal[4], .5),
      linetype = "dashed",
      linewidth = 0.5
    ),
    text = element_text(family = "fira", colour = "grey80"),
    plot.title = element_text(
      size = 70,
      face = "bold",
      color = firepal[3],
      hjust = 0
    ),
    plot.subtitle = element_text(
      size = 45,
      color = firepal[4],
      margin = margin(t = 10),
      hjust = 0
    ),
    axis.title.x = element_text(size = 30, hjust = .5),
    axis.text = element_text(size = 45, colour = "grey80"),
    axis.title = element_text(size = 45, hjust = 0)
  ) +
  labs(
    x = "",
    y = "hectáreas (miles)",
    title = texttitleins1,
    subtitle = textsubins1
  )
inset1
# Comprueba plot con tamaños en el output
inset1grob <- ggplotGrob(inset1)
main2 <- main +
  annotation_custom(
    inset1grob,
    xmin = -15,
    xmax = -9.8,
    ymin = 36.8,
    ymax = 42.8
  )

# Check visual
ggsave(
  "main_inset1.png",
  main2,
  dpi = 300,
  width = 4200,
  height = 4200,
  units = "px"
)


# 5. Plot secundario 2 (incendios más graves) ----

topfires <- gif_fires |>
  arrange(desc(area_forestal_ha)) |>
  slice(1:5) |>
  mutate(year = year(date)) |>
  # Crea etiquetas
  mutate(
    labs = paste0(
      if_else(
        str_detect(munic_name, fixed(" / ")),
        paste0(str_trim(str_extract(munic_name, "^[^/]+")), " y otros"),
        munic_name
      ),
      ", ",
      str_trim(str_extract(prov_name, "^[^/]+")),
      " (",
      year,
      ")"
    ),
    # Ordena por factores
    areafct = fct_reorder(
      paste0(
        prettyNum(
          round(area_forestal_ha, 0),
          big.mark = ".",
          decimal.mark = ","
        ),
        " ha."
      ),
      area_forestal_ha
    )
  )

# Simplifica etiquetas
topfires$labs <- gsub("/València", "", topfires$labs)


inset2 <- ggplot(topfires) +
  geom_text(
    aes(
      x = areafct,
      y = 3,
      label = labs,
      size = area_forestal_ha,
      color = area_forestal_ha
    ),
    show.legend = FALSE,
    family = "fira",
    hjust = 1
  ) +
  coord_flip(ylim = c(-20, 2)) +
  scale_x_discrete(position = "top") +
  scale_size_continuous(range = c(13, 25)) +
  scale_color_gradientn(colors = rev(firepal[-c(1:2)])) +
  theme_minimal() +
  theme(
    plot.background = element_blank(),
    panel.grid = element_blank(),
    axis.ticks = element_blank(),
    axis.text.x = element_blank(),
    strip.text = element_text(size = 12),
    text = element_text(family = "fira", color = "grey80"),
    axis.text.y = element_text(
      size = 38,
      hjust = 0,
      color = firepal[5],
      margin = margin(l = -20)
    ),
    plot.title.position = "plot",
    plot.title = element_text(
      size = 70,
      face = "bold",
      color = firepal[3],
      hjust = .8,
      margin = margin(b = 0)
    )
  ) +
  labs(
    x = "",
    y = "",
    title = "Incendios más destructivos"
  )

inset2


# Comprueba plot con tamaños en el output
inset2grob <- ggplotGrob(inset2)


main3 <- main2 +
  annotation_custom(inset2grob, xmin = -7, xmax = 6, ymin = 33.5, ymax = 36.6)


ggsave(
  "gif_spain.png",
  main3,
  dpi = 300,
  width = 4200,
  height = 4200,
  units = "px"
)

# Compresión local sin pérdida cuando OptiPNG está disponible.
optipng <- Sys.which("optipng")
if (nzchar(optipng)) {
  system2(
    optipng,
    c("-quiet", "-o2", "main.png", "main_inset1.png", "gif_spain.png")
  )
}

# 6. Utilities ----

# Escribe info de sesión
sessioninfo::session_info(to_file = "sessioninfo.txt")

# La compresión adicional de imágenes se realiza por separado.
