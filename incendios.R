#
# munis <- sf::st_drop_geometry(mapSpain::esp_get_capimun())
#
#
# aa2 <- sf::st_drop_geometry(mapSpain::esp_get_munic_siane(epsg=4326))
#
#
#
# munis[grep("Montit", munis$name), ]
# aa2[grep("Traba", aa2$name), ]

# GIF España desde 2010
# Datos obtenidos por scrapeado y depuración de los informes de MITECO
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


# 2. Carga datos y depura ----
gif_fires <- read_csv("data/gif_d2010.csv",
  col_types = cols(date = col_date(format = "%Y-%m-%d"))
)

gif_fires$codmun <- sprintf("%05d", gif_fires$codmun)

munis_sf <- esp_get_capimun(moveCAN = TRUE) %>%
  select(codmun = LAU_CODE) %>%
  # Trabajo en EPSG:4258 para la visualización (opinativo)
  st_transform(4258)

# Objeto sf a la izquierda para no perder la geometría
gif_fires_sf <- munis_sf %>%
  right_join(gif_fires) %>%
  # Reordeno columnas
  select(names(gif_fires)) %>%
  arrange(desc(date))

any(st_is_empty(gif_fires_sf))

# Expect FALSE

# 3. Plot principal ----

# Preparo fuentes y colores

font_add_google("Fira Sans", family = "fira")

# Colores básicos del plot
# https://www.schemecolor.com/fire-color-scheme.php
# The Fire Color Scheme palette has 6 colors which are Barn Red (#801100),
# Engineering International Orange (#B62203), Sinopia (#D73502),
# Orange (#FC6400), Philippine Orange (#FF7500) and Golden Poppy (#FAC000).
firepal <- c("#801100", "#B62203", "#FC6400", "#FF7500", "#FAC000")



# Paso las coordenadas a columnas para usarlos con geom_glow
coords <- gif_fires_sf %>%
  st_drop_geometry() %>%
  bind_cols(st_coordinates(gif_fires_sf)) %>%
  group_by(prov_name, munic_name, X, Y) %>%
  summarise(area_ha = sum(area_forestal_ha)) %>%
  ungroup()


# Extramos shapes auxiliares de españa
ccaa <- esp_get_ccaa(resolution = 1, year = 2024, moveCAN = TRUE) %>%
  st_transform(st_crs(gif_fires_sf))

canbox <- esp_get_can_box(moveCAN = TRUE) %>%
  st_transform(st_crs(ccaa))


# Prepara el texto de títulos y subtítulos

texttitle <- paste0(
  "<span style='color:", firepal[3],
  ";'>Grandes Incendios Forestales</span>**(GIF)**<sup>1</sup> en España ",
  "<span style='color:", firepal[3], ";'>(",
  min(year(gif_fires$date)), "-", max(year(gif_fires$date)), ")"
)

textsub <- paste0(
  "<sup>1</sup> Incendios que presentan <span style='color:",
  firepal[3], ";'>al menos 500 hectáreas forestales quemadas</span>"
)

# Main plot

showtext_auto()

main <- ggplot(ccaa) +
  geom_sf(fill = "grey10", color = "grey20") +
  geom_sf(data = canbox, color = "grey20") +
  geom_glowpoint(
    data = coords, aes(
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
  guides(size = guide_legend(
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
  )) +
  theme_void() +
  theme(
    text = element_text(color = "grey80", family = "fira"),
    plot.background = element_rect(fill = "black"),
    plot.margin = margin(t = 20, l = 20),
    plot.title = element_markdown(size = 110, hjust = .5),
    plot.subtitle = element_markdown(
      size = 65, hjust = .5,
      margin = margin(t = 10)
    ),
    legend.position = "bottom",
    legend.title = element_text(
      color = "grey80", size = 50,
      margin = margin(t = 20, b = 10)
    ),
    legend.text = element_text(
      color = "grey80", size = 70
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
      "©2022 Diego Hernangómez https://dieghernan.github.io. Las hectáreas se",
      " refieren únicamente a hectáreas forestales afectadas.\n",
      "Datos: Estadísticas de Incendios Forestales, MITECO. Estadísticas ",
      "definitivas y Avances"
    )
  )


# Para check visual, cuando se usa showtext_auto() las fuentes funcionan
# de una manera distinta entre el device plot y el archivo guardado
ggsave("main.png", main, dpi = 300, width = 4200, height = 4200, units = "px")


# 4. Plot secundario 1 (años) ----

years <- gif_fires %>%
  mutate(year = year(date)) %>%
  group_by(year) %>%
  summarise(overall = sum(area_forestal_ha))


sum(years$overall) %>% prettyNum(big.mark = ".", decimal.mark = ",")

texttitleins1 <- sum(years$overall) %>%
  prettyNum(big.mark = ".", decimal.mark = ",") %>%
  paste("ha.")

textsubins1 <- "forestales quemadas"


inset1 <- ggplot(years, aes(x = year)) +
  geom_col(aes(y = overall), fill = firepal[5], alpha = 0.6) +
  geom_smooth(aes(y = overall),
    se = FALSE, color = firepal[3],
    size = 2
  ) +
  coord_flip() +
  scale_x_reverse(breaks = unique(years$year)) +
  scale_y_continuous(
    labels = c("-", "50k", "100k", "150k", "200k"),
    breaks = c(0, 50000, 100000, 150000, 200000)
  ) +
  theme_minimal() +
  theme(
    panel.grid = element_blank(),
    panel.grid.major.x = element_line(
      color = alpha(firepal[4], .5), linetype = "dashed",
      linewidth = 0.5
    ),
    text = element_text(family = "fira", colour = "grey80"),
    plot.title = element_text(
      size = 70, face = "bold",
      color = firepal[3], hjust = 0
    ),
    plot.subtitle = element_text(
      size = 45, color = firepal[4],
      margin = margin(t = -10), hjust = 0
    ),
    axis.title.x = element_text(size = 30, hjust = .5),
    axis.text = element_text(size = 45, colour = "grey80"),
    axis.title = element_text(size = 45, hjust = 0)
  ) +
  labs(
    x = "",
    y = "hectáreas",
    title = texttitleins1,
    subtitle = textsubins1
  )
inset1
# Comprueba plot con tamaños en el output
inset1grob <- ggplotGrob(inset1)
main2 <- main +
  annotation_custom(inset1grob,
    xmin = -15,
    xmax = -9.8, ymin = 36.8, ymax = 42.8
  )

# Check visual
ggsave("main_inset1.png", main2,
  dpi = 300, width = 4200, height = 4200,
  units = "px"
)


# 5. Plot secundario 2 (incendios más graves) ----

topfires <- gif_fires %>%
  arrange(desc(area_forestal_ha)) %>%
  slice(1:5) %>%
  mutate(year = year(date)) %>%
  # Crea etiquetas
  mutate(
    labs = paste0(
      munic_name, ", ", prov_name,
      " (", year, ")"
    ),
    # Ordena por factores
    areafct = fct_reorder(paste0(
      prettyNum(round(area_forestal_ha, 0),
        big.mark = ".",
        decimal.mark = ","
      ),
      " ha."
    ), area_forestal_ha)
  )

# Simplifica etiquetas
topfires$labs <- gsub("/València", "", topfires$labs)



inset2 <- ggplot(topfires) +
  geom_text(
    aes(
      x = areafct, y = 3,
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
    panel.grid = element_blank(),
    axis.ticks = element_blank(),
    axis.text.x = element_blank(),
    strip.text = element_text(size = 12),
    text = element_text(family = "fira", color = "grey80"),
    axis.text.y = element_text(
      size = 38, hjust = 0,
      color = firepal[5],
      margin = margin(l = -20)
    ),
    plot.title.position = "plot",
    plot.title = element_text(
      size = 70, face = "bold",
      color = firepal[3],
      hjust = .8,
      margin = margin(b = 0)
    )
  ) +
  labs(
    x = "", y = "",
    title = "Incendios más destructivos"
  )

inset2


# Comprueba plot con tamaños en el output
inset2grob <- ggplotGrob(inset2)



main3 <- main2 +
  annotation_custom(inset2grob,
    xmin = -7, xmax = 6, ymin = 33.5, ymax = 36.6
  )


ggsave("gif_spain.png", main3,
  dpi = 300, width = 4200, height = 4200,
  units = "px"
)
