#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo del Bot de Telegram con Lenguaje Natural Avanzado
MedConnect - Demostración de Capacidades
"""

import sys
import os

# Agregar el directorio actual al path para importar las funciones del bot
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar funciones del bot (simulando la estructura)
def simulate_bot_response():
    """Simula las respuestas del bot para demostración"""
    
    # Simulamos las funciones que están en app.py
    def detect_intent(text):
        """Detecta la intención del usuario basándose en palabras clave"""
        INTENT_KEYWORDS = {
            'consulta': ['consulta', 'médico', 'doctor', 'cita', 'visita', 'chequeo', 'revisión', 'control'],
            'medicamento': ['medicamento', 'medicina', 'pastilla', 'píldora', 'remedio', 'fármaco', 'droga', 'tratamiento'],
            'examen': ['examen', 'análisis', 'estudio', 'prueba', 'laboratorio', 'radiografía', 'ecografía', 'resonancia'],
            'historial': ['historial', 'historia', 'registro', 'datos', 'información', 'ver', 'mostrar', 'consultar'],
            'saludo': ['hola', 'buenos', 'buenas', 'saludos', 'hey', 'qué tal', 'cómo estás'],
            'despedida': ['adiós', 'chao', 'hasta luego', 'nos vemos', 'bye', 'gracias'],
            'ayuda': ['ayuda', 'help', 'auxilio', 'socorro', 'no entiendo', 'qué puedes hacer'],
            'emergencia': ['emergencia', 'urgente', 'grave', 'dolor fuerte', 'sangre', 'desmayo', 'accidente']
        }
        
        text_lower = text.lower()
        intent_scores = {}
        for intent, keywords in INTENT_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                intent_scores[intent] = score
        
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        return 'unknown'
    
    return detect_intent

def main():
    """Función principal de demostración"""
    print("🤖 DEMO: Bot de Telegram con Lenguaje Natural Avanzado")
    print("=" * 60)
    print("MedConnect - Capacidades de Procesamiento de Lenguaje Natural")
    print("=" * 60)
    
    # Inicializar función de detección
    detect_intent = simulate_bot_response()
    
    # Ejemplos de frases que el bot puede entender
    test_phrases = [
        # Consultas médicas
        ("Quiero registrar una consulta", "consulta"),
        ("Fui al médico ayer", "consulta"),
        ("Tengo una cita con el doctor", "consulta"),
        ("Necesito anotar mi chequeo médico", "consulta"),
        
        # Medicamentos
        ("Necesito registrar un medicamento", "medicamento"),
        ("Estoy tomando pastillas", "medicamento"),
        ("El doctor me recetó un remedio", "medicamento"),
        ("Quiero anotar mi tratamiento", "medicamento"),
        
        # Exámenes
        ("Me hice unos exámenes", "examen"),
        ("Tengo resultados de laboratorio", "examen"),
        ("Quiero registrar una radiografía", "examen"),
        ("Necesito guardar mi ecografía", "examen"),
        
        # Historial
        ("Muéstrame mi historial", "historial"),
        ("Quiero ver mis datos", "historial"),
        ("Consultar mi información médica", "historial"),
        ("Ver mi registro de salud", "historial"),
        
        # Saludos
        ("Hola", "saludo"),
        ("Buenos días", "saludo"),
        ("Qué tal", "saludo"),
        ("Cómo estás", "saludo"),
        
        # Despedidas
        ("Adiós", "despedida"),
        ("Hasta luego", "despedida"),
        ("Gracias", "despedida"),
        ("Nos vemos", "despedida"),
        
        # Ayuda
        ("Necesito ayuda", "ayuda"),
        ("No entiendo", "ayuda"),
        ("Qué puedes hacer", "ayuda"),
        
        # Emergencias
        ("Es una emergencia", "emergencia"),
        ("Tengo dolor fuerte", "emergencia"),
        ("Es urgente", "emergencia"),
        ("Tuve un accidente", "emergencia"),
    ]
    
    print("\n🎯 PRUEBAS DE RECONOCIMIENTO DE INTENCIONES")
    print("-" * 60)
    
    # Contadores para estadísticas
    total_tests = len(test_phrases)
    correct_detections = 0
    
    for phrase, expected_intent in test_phrases:
        detected_intent = detect_intent(phrase)
        is_correct = detected_intent == expected_intent
        
        if is_correct:
            correct_detections += 1
            status = "✅"
        else:
            status = "❌"
        
        print(f"{status} \"{phrase}\"")
        print(f"   Esperado: {expected_intent} | Detectado: {detected_intent}")
        print()
    
    # Mostrar estadísticas
    accuracy = (correct_detections / total_tests) * 100
    print("📊 ESTADÍSTICAS DE PRECISIÓN")
    print("-" * 60)
    print(f"Total de pruebas: {total_tests}")
    print(f"Detecciones correctas: {correct_detections}")
    print(f"Detecciones incorrectas: {total_tests - correct_detections}")
    print(f"Precisión: {accuracy:.1f}%")
    
    if accuracy >= 90:
        print("🎉 ¡EXCELENTE! El bot tiene alta precisión en reconocimiento")
    elif accuracy >= 75:
        print("👍 BUENO: El bot funciona bien, algunas mejoras posibles")
    else:
        print("⚠️  MEJORABLE: Se recomienda ajustar las palabras clave")
    
    print("\n🌟 CARACTERÍSTICAS DESTACADAS")
    print("-" * 60)
    print("✅ Reconocimiento de 8 categorías de intenciones")
    print("✅ Procesamiento de sinónimos y variaciones")
    print("✅ Detección prioritaria de emergencias")
    print("✅ Respuestas personalizadas por contexto")
    print("✅ Manejo de conversaciones naturales")
    print("✅ Variaciones aleatorias en respuestas")
    
    print("\n💡 EJEMPLOS DE USO EN TELEGRAM")
    print("-" * 60)
    print("Usuario: 'Hola'")
    print("Bot: '¡Hola! 😊 ¿Cómo estás hoy? ¿En qué puedo ayudarte?'")
    print()
    print("Usuario: 'Quiero anotar un medicamento'")
    print("Bot: '¡Perfecto! 👍 Para registrar tu medicamento necesito...'")
    print()
    print("Usuario: 'Tengo dolor fuerte en el pecho'")
    print("Bot: '🚨 EMERGENCIA DETECTADA 🚨 LLAMA INMEDIATAMENTE: 131 - SAMU'")
    
    print("\n🚀 ¡DEMO COMPLETADA!")
    print("=" * 60)
    print("El bot está listo para interacciones naturales en @Medconn_bot")
    print("Pruébalo en Telegram enviando mensajes como los ejemplos mostrados.")

if __name__ == "__main__":
    main() 