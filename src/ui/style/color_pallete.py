from matplotlib.colors import to_rgb

LIGHT_THEME_HEX = {
    "bg-dark": "#5C6D5D",
    "bg-secondary": "#71706E",
    "bg-tertiary": "#F5F5F0",
    "text-light": "#F5F5F0",
    "text-secondary": "#E5E4E2",
    "accent-primary": "#DCC0C0",
    "accent-secondary": "#E8D5E0",
    "accent-success": "#D4A574",
    "accent-error": "#C67B5C",
    "accent-muted": "#2C2C2C",
}

# Convert HEX to RGB
LIGHT_THEME_RGB = {
    key: tuple(int(to_rgb(value)[i] * 255) for i in range(3))
    for key, value in LIGHT_THEME_HEX.items()
}