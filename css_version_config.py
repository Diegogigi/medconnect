
# Configuración para forzar recarga de CSS
# Agregar a app.py o config.py

import time

# Versión del CSS para evitar caché
CSS_VERSION = 1753995281

# Función para generar URLs de CSS con versión
def css_url(filename):
    return f'/static/css/{filename}?v={CSS_VERSION}'

# En las plantillas, usar:
# <link rel="stylesheet" href="{ css_url('professional-styles.css') }">
