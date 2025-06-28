#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demostración de Mejoras Avanzadas del Bot MedConnect
Prueba las nuevas capacidades de reconocimiento expandidas
"""

import sys
import os

# Agregar el directorio actual al path para importar funciones del bot
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar funciones del bot desde app.py
try:
    from app import detect_intent, INTENT_KEYWORDS
    print("✅ Funciones del bot importadas correctamente")
except ImportError as e:
    print(f"❌ Error al importar funciones del bot: {e}")
    sys.exit(1)

def test_nuevas_capacidades():
    """Prueba las nuevas capacidades de reconocimiento del bot"""
    
    print("🚀 DEMOSTRACIÓN DE MEJORAS AVANZADAS DEL BOT MEDCONNECT")
    print("=" * 70)
    
    # Frases de prueba para las nuevas funcionalidades
    test_cases = [
        # Medicamentos avanzados
        ("Me recetaron un nuevo medicamento", "medicamento"),
        ("Empezar medicamento para la presión", "medicamento"),
        ("¿Cómo va mi tratamiento?", "medicamento"),
        ("¿Funciona el medicamento que tomo?", "medicamento"),
        ("He notado efectos secundarios", "medicamento"),
        ("El medicamento me está dando reacción", "medicamento"),
        ("Creo que estoy mejorando con las pastillas", "medicamento"),
        
        # Exámenes avanzados
        ("Ya me hice los exámenes de sangre", "examen"),
        ("Tengo resultados de laboratorio", "examen"),
        ("Completé los análisis médicos", "examen"),
        ("Salieron los resultados", "examen"),
        ("Tengo que hacerme una radiografía", "examen"),
        ("Debo hacerme exámenes próximamente", "examen"),
        ("Tengo programada una ecografía", "examen"),
        ("Me van a hacer una resonancia", "examen"),
        
        # Recordatorios
        ("Recordarme tomar las pastillas", "recordatorio"),
        ("Necesito una alerta para mi medicamento", "recordatorio"),
        ("Avisar cuando sea hora de la medicina", "recordatorio"),
        ("Programar aviso para mi cita", "recordatorio"),
        
        # Citas futuras
        ("Quiero agendar una cita médica", "cita_futura"),
        ("Programar cita con el cardiólogo", "cita_futura"),
        ("Reservar hora con el doctor", "cita_futura"),
        ("Pedir hora para próxima semana", "cita_futura"),
        
        # Seguimiento
        ("¿Cómo voy con mi diabetes?", "seguimiento"),
        ("Evolución de mi presión arterial", "seguimiento"),
        ("¿Hay progreso en mi tratamiento?", "seguimiento"),
        ("¿Estoy mejorando?", "seguimiento"),
        ("¿Estoy empeorando?", "seguimiento"),
        
        # Casos tradicionales (deben seguir funcionando)
        ("Registrar una consulta médica", "consulta"),
        ("Anotar un medicamento", "medicamento"),
        ("Guardar un examen", "examen"),
        ("Ver mi historial", "historial"),
        ("Hola, ¿cómo estás?", "saludo"),
        ("Necesito ayuda", "ayuda"),
        ("Es una emergencia", "emergencia")
    ]
    
    print(f"\n🧪 PROBANDO {len(test_cases)} FRASES DIFERENTES")
    print("-" * 70)
    
    aciertos = 0
    total = len(test_cases)
    
    for i, (frase, categoria_esperada) in enumerate(test_cases, 1):
        categoria_detectada = detect_intent(frase)
        
        if categoria_detectada == categoria_esperada:
            status = "✅"
            aciertos += 1
        else:
            status = "❌"
        
        print(f"{status} {i:2d}. \"{frase}\"")
        print(f"     Esperado: {categoria_esperada} | Detectado: {categoria_detectada}")
        
        if categoria_detectada != categoria_esperada:
            print(f"     ⚠️  Error en detección")
        
        print()
    
    # Estadísticas finales
    precision = (aciertos / total) * 100
    print("📊 ESTADÍSTICAS FINALES")
    print("=" * 70)
    print(f"✅ Aciertos: {aciertos}/{total}")
    print(f"📈 Precisión: {precision:.1f}%")
    
    if precision >= 90:
        print("🎉 ¡EXCELENTE! El bot tiene alta precisión")
    elif precision >= 75:
        print("👍 ¡BUENO! El bot funciona bien")
    else:
        print("⚠️  MEJORABLE: El bot necesita ajustes")
    
    return aciertos, total

def mostrar_nuevas_categorias():
    """Muestra las nuevas categorías agregadas"""
    
    print("\n🆕 NUEVAS CATEGORÍAS AGREGADAS")
    print("=" * 70)
    
    nuevas_categorias = ['recordatorio', 'cita_futura', 'seguimiento']
    
    for categoria in nuevas_categorias:
        if categoria in INTENT_KEYWORDS:
            palabras = INTENT_KEYWORDS[categoria]
            print(f"\n📂 {categoria.upper().replace('_', ' ')}")
            print("-" * 40)
            for palabra in palabras:
                print(f"   • {palabra}")
    
    print(f"\n📈 TOTAL DE CATEGORÍAS: {len(INTENT_KEYWORDS)}")
    
    # Mostrar categorías expandidas
    print("\n🔄 CATEGORÍAS EXPANDIDAS")
    print("=" * 70)
    
    categorias_expandidas = ['medicamento', 'examen']
    
    for categoria in categorias_expandidas:
        if categoria in INTENT_KEYWORDS:
            palabras = INTENT_KEYWORDS[categoria]
            print(f"\n📂 {categoria.upper()}")
            print("-" * 40)
            print(f"   Total de palabras clave: {len(palabras)}")
            print("   Nuevas palabras agregadas:")
            
            if categoria == 'medicamento':
                nuevas = ['nuevo medicamento', 'empezar medicamento', 'comenzar tratamiento', 
                         'recetaron', 'prescribieron', 'como va', 'efectos', 'reacción', 
                         'funciona', 'mejora', 'empeora']
            elif categoria == 'examen':
                nuevas = ['me hice', 'ya me hice', 'tengo resultados', 'salieron', 'completé', 
                         'terminé examen', 'tengo que hacerme', 'debo hacerme', 'programado', 
                         'agendado', 'próximo examen', 'me van a hacer']
            
            for palabra in nuevas:
                print(f"     • {palabra}")

def mostrar_ejemplos_uso():
    """Muestra ejemplos de uso de las nuevas funcionalidades"""
    
    print("\n💡 EJEMPLOS DE USO AVANZADO")
    print("=" * 70)
    
    ejemplos = {
        "💊 MEDICAMENTOS AVANZADOS": [
            "Me recetaron un nuevo medicamento para la diabetes",
            "¿Cómo va mi tratamiento con losartán?",
            "El medicamento me está dando efectos secundarios",
            "¿Funciona la metformina que tomo?",
            "Creo que estoy mejorando con las pastillas"
        ],
        "🩺 EXÁMENES COMPLETOS": [
            "Ya me hice los exámenes de sangre ayer",
            "Tengo resultados de la ecografía",
            "Salieron los análisis de laboratorio",
            "Tengo que hacerme una resonancia magnética",
            "Debo hacerme exámenes la próxima semana",
            "Tengo programada una radiografía"
        ],
        "🔔 RECORDATORIOS": [
            "Recordarme tomar las pastillas a las 8am",
            "Necesito una alerta para mi medicamento",
            "Avisar cuando sea hora de la cita",
            "Programar aviso para renovar receta"
        ],
        "📅 CITAS FUTURAS": [
            "Quiero agendar una cita con el cardiólogo",
            "Programar cita para control mensual",
            "Reservar hora con el endocrinólogo",
            "Pedir hora para la próxima semana"
        ],
        "📊 SEGUIMIENTO": [
            "¿Cómo voy con mi diabetes?",
            "Evolución de mi presión arterial",
            "¿Hay progreso en mi tratamiento?",
            "¿Estoy mejorando con la dieta?",
            "Seguimiento de mi peso corporal"
        ]
    }
    
    for categoria, frases in ejemplos.items():
        print(f"\n{categoria}")
        print("-" * 50)
        for frase in frases:
            print(f"   💬 \"{frase}\"")

if __name__ == "__main__":
    print("🤖 INICIANDO DEMOSTRACIÓN DE MEJORAS DEL BOT")
    print("=" * 70)
    
    try:
        # Ejecutar pruebas
        aciertos, total = test_nuevas_capacidades()
        
        # Mostrar nuevas categorías
        mostrar_nuevas_categorias()
        
        # Mostrar ejemplos de uso
        mostrar_ejemplos_uso()
        
        print("\n🎯 RESUMEN DE MEJORAS")
        print("=" * 70)
        print("✅ Palabras clave expandidas para medicamentos")
        print("✅ Palabras clave expandidas para exámenes")
        print("✅ Nueva categoría: recordatorios")
        print("✅ Nueva categoría: citas futuras")
        print("✅ Nueva categoría: seguimiento")
        print(f"✅ Precisión de detección: {(aciertos/total)*100:.1f}%")
        
        print("\n🚀 ¡BOT MEDCONNECT MEJORADO Y LISTO!")
        
    except Exception as e:
        print(f"❌ Error durante la demostración: {e}")
        sys.exit(1) 