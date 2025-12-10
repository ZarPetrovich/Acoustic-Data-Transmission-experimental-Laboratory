from matplotlib.colors import to_rgb

LIGHT_THEME_HEX = {
    "bg-dark": "#252323",
    "bg-secondary": "#030202",
    "bg-tertiary": "#F5F5F0",
    "text-light": "#f5f1ed",
    "text-secondary": "#E5E4E2",
    "accent-primary": "#4b4e58",
    "accent-secondary": "#d4d3d5",
    "accent-success": "#D4A574",
    "accent-error": "#C67B5C",
    "accent-muted": "#2C2C2C",
}

# Convert HEX to RGB
LIGHT_THEME_RGB = {
    key: tuple(int(to_rgb(value)[i] * 255) for i in range(3))
    for key, value in LIGHT_THEME_HEX.items()
}