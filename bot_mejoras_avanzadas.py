#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mejoras Avanzadas para el Bot de Telegram
MedConnect - Funcionalidades Extendidas
"""

# Palabras clave expandidas para reconocimiento de intenciones
INTENT_KEYWORDS_AVANZADAS = {
    'consulta': ['consulta', 'médico', 'doctor', 'cita', 'visita', 'chequeo', 'revisión', 'control'],
    'medicamento': ['medicamento', 'medicina', 'pastilla', 'píldora', 'remedio', 'fármaco', 'droga', 'tratamiento'],
    'medicamento_nuevo': ['nuevo medicamento', 'empezar medicamento', 'comenzar tratamiento', 'recetaron', 'prescribieron'],
    'medicamento_seguimiento': ['como va', 'efectos', 'reacción', 'funciona', 'mejora', 'empeora'],
    'examen_realizado': ['me hice', 'ya me hice', 'tengo resultados', 'salieron', 'completé', 'terminé examen'],
    'examen_futuro': ['tengo que hacerme', 'debo hacerme', 'programado', 'agendado', 'próximo examen', 'me van a hacer'],
    'examen': ['examen', 'análisis', 'estudio', 'prueba', 'laboratorio', 'radiografía', 'ecografía', 'resonancia'],
    'recordatorio': ['recordar', 'recordatorio', 'alerta', 'avisar', 'notificar', 'programar aviso'],
    'historial': ['historial', 'historia', 'registro', 'datos', 'información', 'ver', 'mostrar', 'consultar'],
    'saludo': ['hola', 'buenos', 'buenas', 'saludos', 'hey', 'qué tal', 'cómo estás'],
    'despedida': ['adiós', 'chao', 'hasta luego', 'nos vemos', 'bye', 'gracias'],
    'ayuda': ['ayuda', 'help', 'auxilio', 'socorro', 'no entiendo', 'qué puedes hacer'],
    'emergencia': ['emergencia', 'urgente', 'grave', 'dolor fuerte', 'sangre', 'desmayo', 'accidente'],
    'cita_futura': ['próxima cita', 'agendar cita', 'programar cita', 'reservar hora', 'pedir hora'],
    'seguimiento': ['cómo voy', 'evolución', 'progreso', 'mejorando', 'empeorando', 'seguimiento']
}

def get_example_responses():
    """Ejemplos de respuestas mejoradas para el bot"""
    
    examples = {
        'medicamento_nuevo': {
            'user_registered': """¡Perfecto! {user_name}, veo que empezarás un nuevo medicamento. 💊✨

Es importante registrarlo bien desde el inicio. Necesito:

🆕 **Nuevo medicamento:**
1️⃣ ¿Cómo se llama el medicamento?
2️⃣ ¿Qué dosis te recetaron? (ej: 50mg, 2 tabletas)
3️⃣ ¿Cada cuánto tiempo lo tomas? (ej: cada 8 horas, 2 veces al día)
4️⃣ ¿Qué médico te lo recetó?
5️⃣ ¿Para qué condición es? (diagnóstico)
6️⃣ ¿Cuándo empezaste? (fecha de inicio)
7️⃣ ¿Por cuánto tiempo? (duración del tratamiento)

🔔 **¿Quieres que configure recordatorios?**
• Alertas para tomar el medicamento
• Recordatorio para renovar receta
• Seguimiento de efectos

¿Me das toda la información? 🤔""",
            
            'user_not_registered': """💊 ¡Excelente que quieras registrar tu nuevo medicamento desde el inicio!

**Para un registro completo del nuevo tratamiento necesito:**
1️⃣ Nombre del medicamento
2️⃣ Dosis exacta recetada
3️⃣ Frecuencia (cada cuánto tiempo)
4️⃣ Médico que lo prescribió
5️⃣ Condición que trata
6️⃣ Fecha de inicio del tratamiento
7️⃣ Duración esperada

🔔 **Recordatorios disponibles:**
• Para tomar el medicamento a tiempo
• Para renovar la receta médica
• Para hacer seguimiento de efectos

💡 **Para recordatorios automáticos:**
Vincula tu cuenta en https://medconnect.cl/profile

¿Me compartes los detalles del nuevo medicamento? 😊"""
        },
        
        'examen_realizado': {
            'user_registered': """¡Genial! {user_name}, me alegra que hayas completado tu examen. 🩺✅

Para registrar correctamente los resultados, necesito:

📋 **Detalles del examen realizado:**
1️⃣ ¿Qué tipo de examen fue? (sangre, orina, radiografía, etc.)
2️⃣ ¿Cuándo te lo hiciste? (fecha exacta)
3️⃣ ¿En qué laboratorio o centro médico?
4️⃣ ¿Cuáles fueron los resultados principales?
5️⃣ ¿Algún valor fuera de lo normal o preocupante?
6️⃣ ¿Qué te dijo el médico sobre los resultados?

💡 **Tip:** Si tienes los resultados en papel o digital, también puedes subirlos a tu perfil web.

¿Me compartes los detalles? 🤔""",
            
            'user_not_registered': """🩺 ¡Genial que hayas completado tu examen! Es importante registrar los resultados.

**Para un registro completo necesito:**
1️⃣ Tipo de examen realizado
2️⃣ Fecha exacta cuando te lo hiciste
3️⃣ Laboratorio o centro médico
4️⃣ Resultados principales obtenidos
5️⃣ Valores anormales o preocupantes
6️⃣ Comentarios del médico

💡 **Para guardarlo permanentemente:**
Vincula tu cuenta en https://medconnect.cl/profile

¿Me cuentas sobre los resultados de tu examen? 😊"""
        },
        
        'examen_futuro': {
            'user_registered': """¡Excelente! {user_name}, es muy responsable que planifiques tus exámenes. 📅🩺

Para programar tu recordatorio y registro, necesito:

⏰ **Detalles del examen programado:**
1️⃣ ¿Qué tipo de examen te van a hacer?
2️⃣ ¿Cuándo está programado? (fecha y hora)
3️⃣ ¿En qué laboratorio o centro médico?
4️⃣ ¿Quién te lo ordenó? (médico/especialista)
5️⃣ ¿Requiere preparación especial? (ayuno, etc.)
6️⃣ ¿Quieres que te recuerde antes?

🔔 **Puedo configurar alertas para:**
• Recordarte 1 día antes
• Recordarte el mismo día
• Recordarte sobre preparación especial

¿Me das los detalles para programarlo? 🤔""",
            
            'user_not_registered': """📅 ¡Excelente que planifiques tus exámenes con anticipación!

**Para programar tu examen necesito:**
1️⃣ Tipo de examen programado
2️⃣ Fecha y hora exacta
3️⃣ Laboratorio o centro médico
4️⃣ Médico que lo ordenó
5️⃣ Preparación especial requerida
6️⃣ Si quieres recordatorios

🔔 **Recordatorios disponibles:**
• 1 día antes del examen
• El mismo día por la mañana
• Sobre preparación especial

💡 **Para recordatorios automáticos:**
Vincula tu cuenta en https://medconnect.cl/profile

¿Me das los detalles del examen programado? 😊"""
        }
    }
    
    return examples

def demo_nuevas_funcionalidades():
    """Demostración de las nuevas funcionalidades"""
    
    print("🚀 NUEVAS FUNCIONALIDADES DEL BOT MEDCONNECT")
    print("=" * 60)
    
    print("\n💊 GESTIÓN AVANZADA DE MEDICAMENTOS")
    print("-" * 40)
    print("✅ Medicamentos nuevos con seguimiento completo")
    print("✅ Monitoreo de efectos y adherencia")
    print("✅ Recordatorios automáticos")
    print("✅ Renovación de recetas")
    
    print("\n🩺 SISTEMA COMPLETO DE EXÁMENES")
    print("-" * 40)
    print("✅ Exámenes realizados con resultados detallados")
    print("✅ Exámenes futuros con recordatorios")
    print("✅ Preparación especial y alertas")
    print("✅ Seguimiento de valores anormales")
    
    print("\n🔔 SISTEMA DE RECORDATORIOS")
    print("-" * 40)
    print("✅ Alertas para medicamentos")
    print("✅ Recordatorios de citas")
    print("✅ Preparación para exámenes")
    print("✅ Renovación de recetas")
    
    print("\n📊 SEGUIMIENTO PERSONALIZADO")
    print("-" * 40)
    print("✅ Evolución de tratamientos")
    print("✅ Efectos secundarios")
    print("✅ Adherencia a medicamentos")
    print("✅ Progreso en condiciones médicas")
    
    print("\n🎯 EJEMPLOS DE FRASES QUE ENTIENDE:")
    print("-" * 40)
    
    ejemplos = [
        ("Me recetaron un nuevo medicamento", "medicamento_nuevo"),
        ("¿Cómo va mi tratamiento?", "medicamento_seguimiento"),
        ("Ya me hice los exámenes de sangre", "examen_realizado"),
        ("Tengo programada una ecografía", "examen_futuro"),
        ("Recordarme tomar las pastillas", "recordatorio"),
        ("¿Cómo voy con mi diabetes?", "seguimiento"),
        ("Quiero agendar una cita", "cita_futura")
    ]
    
    for frase, categoria in ejemplos:
        print(f"• \"{frase}\" → {categoria}")
    
    print(f"\n📈 TOTAL DE CATEGORÍAS: {len(INTENT_KEYWORDS_AVANZADAS)}")
    print("🎉 ¡Bot listo para interacciones médicas avanzadas!")

if __name__ == "__main__":
    demo_nuevas_funcionalidades() 