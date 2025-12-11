from matplotlib.colors import to_rgb

LIGHT_THEME_HEX = {
    "bg-dark": "#0E0E10",
    "bg-secondary": "#19191D", # New: Added for subtle visual layers

    "text-light": "#E0E0E0",
    "text-secondary": "#9B9B9B",

    "push-button-bckg": "#3A3A3A",
    "push-button-border": "#3A3A3A",
    "push-button-hover": "#878787",

    "grp-btn-bckg": "#0E0E10",
    "grp-btn-checked": "#E0E0E0",
    "grp-btn-border": "#E0E0E0",

    "logging-success": "#6a9d74",
    "logging-error": "#d85368",
    "logging-muted": "#f6e997",
}

# Convert HEX to RGB
LIGHT_THEME_RGB = {
    key: tuple(int(to_rgb(value)[i] * 255) for i in range(3))
    for key, value in LIGHT_THEME_HEX.items()
}