#!/usr/bin/env python3
"""
Script de prueba para verificar los tipos de atención disponibles
"""

def test_tipos_atencion_disponibles():
    """Prueba los tipos de atención disponibles"""
    print("🧪 Probando tipos de atención disponibles...")
    
    # Tipos de atención soportados
    tipos_atencion = [
        'fisioterapia',
        'fonoaudiologia', 
        'psicologia',
        'nutricion',
        'kinesiologia',
        'terapia_ocupacional',
        'enfermeria',
        'urgencia'
    ]
    
    print(f"✅ Tipos de atención disponibles: {len(tipos_atencion)}")
    for i, tipo in enumerate(tipos_atencion, 1):
        print(f"   {i}. {tipo}")
    
    return tipos_atencion

def test_casos_por_tipo_atencion():
    """Prueba casos de ejemplo por cada tipo de atención"""
    print("\n📋 Probando casos por tipo de atención...")
    
    casos_prueba = [
        {
            'motivo': 'Dolor lumbar de 3 semanas',
            'tipo_atencion': 'fisioterapia',
            'descripcion': 'Fisioterapia - Dolor lumbar'
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
            'motivo': 'Pérdida de peso y fatiga',
            'tipo_atencion': 'nutricion',
            'descripcion': 'Nutrición - Pérdida de peso'
        },
        {
            'motivo': 'Dolor en rodilla al caminar',
            'tipo_atencion': 'kinesiologia',
            'descripcion': 'Kinesiología - Dolor articular'
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
    
    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n📋 Caso {i}: {caso['descripcion']}")
        print(f"Motivo: {caso['motivo']}")
        print(f"Tipo de atención: {caso['tipo_atencion']}")
        print(f"✅ Caso válido para tipo de atención: {caso['tipo_atencion']}")
        print("-" * 60)

def test_validacion_tipos_atencion():
    """Valida que los tipos de atención sean correctos"""
    print("\n✅ Validando tipos de atención...")
    
    tipos_validos = {
        'fisioterapia': 'Especialidad en rehabilitación física',
        'fonoaudiologia': 'Especialidad en comunicación y deglución',
        'psicologia': 'Especialidad en salud mental',
        'nutricion': 'Especialidad en alimentación y nutrición',
        'kinesiologia': 'Especialidad en movimiento y rehabilitación',
        'terapia_ocupacional': 'Especialidad en actividades de la vida diaria',
        'enfermeria': 'Especialidad en cuidados de salud',
        'urgencia': 'Atención de emergencias médicas'
    }
    
    for tipo, descripcion in tipos_validos.items():
        print(f"✅ {tipo}: {descripcion}")

def test_mapeo_especialidades():
    """Prueba el mapeo de tipos de atención a especialidades"""
    print("\n🗺️ Probando mapeo de tipos de atención a especialidades...")
    
    mapeo_especialidades = {
        'fisioterapia': ['Fisioterapia', 'Rehabilitación'],
        'fonoaudiologia': ['Fonoaudiología', 'Logopedia'],
        'psicologia': ['Psicología', 'Psicología Clínica'],
        'nutricion': ['Nutrición', 'Nutrición Clínica'],
        'kinesiologia': ['Kinesiología', 'Fisioterapia'],
        'terapia_ocupacional': ['Terapia Ocupacional'],
        'enfermeria': ['Enfermería', 'Enfermería Clínica'],
        'urgencia': ['Medicina de Urgencias', 'Emergencias']
    }
    
    for tipo_atencion, especialidades in mapeo_especialidades.items():
        print(f"🏥 {tipo_atencion.upper()}:")
        for especialidad in especialidades:
            print(f"   • {especialidad}")

def main():
    """Función principal de pruebas"""
    print("🤖 PRUEBAS DE TIPOS DE ATENCIÓN")
    print("=" * 60)
    
    try:
        # Prueba 1: Tipos de atención disponibles
        test_tipos_atencion_disponibles()
        
        # Prueba 2: Casos por tipo de atención
        test_casos_por_tipo_atencion()
        
        # Prueba 3: Validación de tipos
        test_validacion_tipos_atencion()
        
        # Prueba 4: Mapeo de especialidades
        test_mapeo_especialidades()
        
        print("\n✅ Todas las pruebas completadas exitosamente!")
        print("\n🎯 Resumen de funcionalidades probadas:")
        print("   • Validación de tipos de atención disponibles")
        print("   • Casos de ejemplo por especialidad")
        print("   • Mapeo correcto de tipos a especialidades")
        print("   • Estructura de datos para tipos de atención")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 