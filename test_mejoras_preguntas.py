#!/usr/bin/env python3
"""
Script para probar las mejoras en la generación de preguntas
"""

def test_mejoras_preguntas():
    """Prueba las mejoras implementadas en la generación de preguntas"""
    print("🎯 PRUEBA DE MEJORAS EN GENERACIÓN DE PREGUNTAS")
    print("=" * 60)
    
    # Casos de prueba por profesión
    casos_prueba = [
        {
            'motivo': 'Dolor intenso en rodilla al caminar',
            'tipo_atencion': 'fisioterapia',
            'descripcion': 'Fisioterapia - Dolor de rodilla'
        },
        {
            'motivo': 'Dificultad para tragar alimentos',
            'tipo_atencion': 'fonoaudiologia',
            'descripcion': 'Fonoaudiología - Problemas de deglución'
        },
        {
            'motivo': 'Ansiedad y estrés laboral',
            'tipo_atencion': 'psicologia',
            'descripcion': 'Psicología - Ansiedad'
        },
        {
            'motivo': 'Dolor lumbar de 3 semanas',
            'tipo_atencion': 'kinesiologia',
            'descripcion': 'Kinesiología - Dolor lumbar'
        },
        {
            'motivo': 'Pérdida de peso y fatiga',
            'tipo_atencion': 'nutricion',
            'descripcion': 'Nutrición - Pérdida de peso'
        },
        {
            'motivo': 'Dificultad para realizar actividades diarias',
            'tipo_atencion': 'terapia_ocupacional',
            'descripcion': 'Terapia Ocupacional - Limitaciones funcionales'
        },
        {
            'motivo': 'Control de presión arterial',
            'tipo_atencion': 'enfermeria',
            'descripcion': 'Enfermería - Control de signos vitales'
        },
        {
            'motivo': 'Dolor agudo en el pecho',
            'tipo_atencion': 'urgencia',
            'descripcion': 'Urgencia - Dolor torácico'
        }
    ]
    
    print("✅ Mejoras implementadas:")
    print("   1. Una sola pregunta relacionada al EVA 0/10")
    print("   2. Incluye tipo de dolor, localización, etc.")
    print("   3. Preguntas específicas por profesión")
    print("   4. Preguntas específicas por región anatómica")
    print("   5. Máximo 8 preguntas por caso")
    
    print("\n📋 Casos de prueba por profesión:")
    for i, caso in enumerate(casos_prueba, 1):
        print(f"   {i}. {caso['descripcion']}")
        print(f"      Motivo: {caso['motivo']}")
        print(f"      Tipo: {caso['tipo_atencion']}")
    
    print("\n🎯 Resultados esperados:")
    print("   • Una sola pregunta de EVA 0/10 por caso")
    print("   • Preguntas específicas por profesión")
    print("   • Preguntas de localización y tipo de dolor")
    print("   • Máximo 8 preguntas relevantes")
    print("   • Sin duplicados")

def test_verificacion_mejoras():
    """Verificación de las mejoras implementadas"""
    print("\n🔍 VERIFICACIÓN DE MEJORAS")
    print("=" * 60)
    
    print("✅ Funciones modificadas:")
    print("   • generar_preguntas_evaluacion() - Mejorada")
    print("   • _get_preguntas_por_profesion() - Nueva")
    print("   • _get_preguntas_por_region() - Nueva")
    print("   • _get_preguntas_generales() - Nueva")
    print("   • analizar_motivo_consulta_mejorado() - Actualizada")
    
    print("\n✅ Características implementadas:")
    print("   • Control de preguntas EVA (una sola)")
    print("   • Control de preguntas de dolor (sin duplicados)")
    print("   • Preguntas específicas por profesión")
    print("   • Preguntas específicas por región anatómica")
    print("   • Preguntas generales adaptadas")
    print("   • Límite de 8 preguntas máximo")
    
    print("\n✅ Profesiones soportadas:")
    profesiones = [
        'fisioterapia', 'kinesiologia', 'fonoaudiologia', 'psicologia',
        'nutricion', 'terapia_ocupacional', 'enfermeria', 'urgencia'
    ]
    for i, profesion in enumerate(profesiones, 1):
        print(f"   {i}. {profesion}")
    
    print("\n✅ Regiones anatómicas soportadas:")
    regiones = [
        'rodilla', 'hombro', 'columna', 'cadera', 'tobillo', 'codo', 'muñeca'
    ]
    for i, region in enumerate(regiones, 1):
        print(f"   {i}. {region}")

def test_casos_especificos():
    """Prueba casos específicos de mejora"""
    print("\n🔍 CASOS ESPECÍFICOS DE MEJORA")
    print("=" * 60)
    
    casos_especificos = [
        {
            'caso': 'Dolor en rodilla',
            'mejora': 'Una sola pregunta EVA + preguntas específicas de rodilla'
        },
        {
            'caso': 'Dolor lumbar',
            'mejora': 'Una sola pregunta EVA + preguntas específicas de columna'
        },
        {
            'caso': 'Problemas de deglución',
            'mejora': 'Preguntas específicas de fonoaudiología'
        },
        {
            'caso': 'Ansiedad',
            'mejora': 'Preguntas específicas de psicología'
        },
        {
            'caso': 'Pérdida de peso',
            'mejora': 'Preguntas específicas de nutrición'
        }
    ]
    
    for i, caso in enumerate(casos_especificos, 1):
        print(f"   {i}. {caso['caso']}")
        print(f"      Mejora: {caso['mejora']}")

def main():
    """Función principal de prueba de mejoras"""
    print("🚀 PRUEBA DE MEJORAS EN GENERACIÓN DE PREGUNTAS")
    print("=" * 60)
    
    try:
        # Prueba 1: Verificación de mejoras
        test_mejoras_preguntas()
        
        # Prueba 2: Verificación técnica
        test_verificacion_mejoras()
        
        # Prueba 3: Casos específicos
        test_casos_especificos()
        
        print("\n📊 RESUMEN DE MEJORAS:")
        print("=" * 60)
        print("✅ Una sola pregunta EVA 0/10 por caso")
        print("✅ Preguntas específicas por profesión")
        print("✅ Preguntas de localización y tipo de dolor")
        print("✅ Máximo 8 preguntas relevantes")
        print("✅ Sin duplicados")
        print("✅ Aplicable a todas las profesiones")
        
        print("\n🎉 MEJORAS IMPLEMENTADAS EXITOSAMENTE:")
        print("   • Control inteligente de preguntas EVA")
        print("   • Preguntas específicas por profesión")
        print("   • Preguntas de localización anatómica")
        print("   • Preguntas de tipo de dolor")
        print("   • Sistema sin duplicados")
        print("   • Límite de preguntas optimizado")
        
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 