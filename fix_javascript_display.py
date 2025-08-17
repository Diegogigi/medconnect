#!/usr/bin/env python3
"""
Script para corregir el problema de JavaScript mostrándose en la interfaz
"""


def fix_javascript_display():
    """Corrige el problema de JavaScript mostrándose en la interfaz"""

    template_path = "templates/professional.html"

    # Leer el archivo
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar y reemplazar el JavaScript mal formateado
    old_javascript = """    <script src="/static/js/enhanced-sidebar-ai.js"></script>

// Funciones de utilidad para la IA
window.showAINotification = function(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    setTimeout(() => notification.classList.add('show'), 100);
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
};

window.updateAIStatus = function(status, message) {
    const statusDot = document.getElementById('aiStatusDot');
    const statusText = document.getElementById('aiStatusText');
    
    if (statusDot) {
        statusDot.className = `status-dot ${status}`;
    }
    
    if (statusText) {
        statusText.textContent = message;
    }
};

window.showAIProgress = function(percentage, text) {
    const progress = document.getElementById('aiProgress');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    
    if (progress) {
        progress.style.display = 'block';
    }
    
    if (progressFill) {
        progressFill.style.width = `${percentage}%`;
    }
    
    if (progressText) {
        progressText.textContent = text;
    }
};

window.hideAIProgress = function() {
    const progress = document.getElementById('aiProgress');
    if (progress) {
        progress.style.display = 'none';
    }
};"""

    new_javascript = """    <script src="/static/js/enhanced-sidebar-ai.js"></script>
    
    <script>
    // Funciones de utilidad para la IA
    window.showAINotification = function(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        setTimeout(() => notification.classList.add('show'), 100);
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    };

    window.updateAIStatus = function(status, message) {
        const statusDot = document.getElementById('aiStatusDot');
        const statusText = document.getElementById('aiStatusText');
        
        if (statusDot) {
            statusDot.className = `status-dot ${status}`;
        }
        
        if (statusText) {
            statusText.textContent = message;
        }
    };

    window.showAIProgress = function(percentage, text) {
        const progress = document.getElementById('aiProgress');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        
        if (progress) {
            progress.style.display = 'block';
        }
        
        if (progressFill) {
            progressFill.style.width = `${percentage}%`;
        }
        
        if (progressText) {
            progressText.textContent = text;
        }
    };

    window.hideAIProgress = function() {
        const progress = document.getElementById('aiProgress');
        if (progress) {
            progress.style.display = 'none';
        }
    };
    </script>"""

    # Reemplazar el contenido
    if old_javascript in content:
        content = content.replace(old_javascript, new_javascript)
        print("✅ JavaScript corregido - ahora está dentro de etiquetas <script>")
    else:
        print("⚠️ No se encontró el JavaScript mal formateado")
        return False

    # Escribir el archivo corregido
    with open(template_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Template professional.html corregido exitosamente")
    return True


def main():
    """Función principal"""
    print("🔧 Corrigiendo problema de JavaScript en la interfaz...")

    if fix_javascript_display():
        print("\n🎉 ¡Problema corregido!")
        print("📋 El JavaScript ahora está correctamente dentro de etiquetas <script>")
        print("🚀 La interfaz debería funcionar correctamente sin mostrar código")
    else:
        print("\n❌ No se pudo corregir el problema")


if __name__ == "__main__":
    main()
