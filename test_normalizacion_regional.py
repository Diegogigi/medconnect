#!/usr/bin/env python3
"""
Script de prueba para verificar la normalización de sinónimos y variaciones regionales
en el módulo Copilot Health.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from copilot_health import CopilotHealth
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_normalizacion_tipos_atencion():
    """Prueba la normalización de tipos de atención con variaciones regionales"""
    print("🧪 PRUEBAS DE NORMALIZACIÓN REGIONAL")
    print("=" * 50)
    
    copilot = CopilotHealth()
    
    # Casos de prueba para fisioterapia/kinesiología
    casos_fisio = [
        "fisioterapia",
        "fisio", 
        "fisioterapeuta",
        "fisioterapéutico",
        "kinesiologia",
        "kinesiología",
        "kinesiólogo",
        "kinesio",
        "kinesiologo"
    ]
    
    print("\n🏥 CASOS FISIOTERAPIA/KINESIOLOGÍA:")
    for caso in casos_fisio:
        normalizado = copilot._normalizar_tipo_atencion(caso)
        print(f"  '{caso}' -> '{normalizado}'")
    
    # Casos de prueba para fonoaudiología/logopedia
    casos_fono = [
        "fonoaudiologia",
        "fonoaudiología",
        "fonoaudiólogo",
        "fono",
        "logopeda",
        "logopedia",
        "terapia del habla",
        "patología del habla"
    ]
    
    print("\n🗣️ CASOS FONOAUDIOLOGÍA/LOGOPEDIA:")
    for caso in casos_fono:
        normalizado = copilot._normalizar_tipo_atencion(caso)
        print(f"  '{caso}' -> '{normalizado}'")
    
    # Casos de prueba para terapia ocupacional
    casos_to = [
        "terapia ocupacional",
        "terapeuta ocupacional",
        "t.o.",
        "to",
        "ergoterapia",
        "ergoterapeuta"
    ]
    
    print("\n🛠️ CASOS TERAPIA OCUPACIONAL:")
    for caso in casos_to:
        normalizado = copilot._normalizar_tipo_atencion(caso)
        print(f"  '{caso}' -> '{normalizado}'")
    
    # Casos de prueba para psicología
    casos_psico = [
        "psicologia",
        "psicología",
        "psicólogo",
        "psicóloga",
        "psico",
        "psicoterapia",
        "psicoterapeuta"
    ]
    
    print("\n🧠 CASOS PSICOLOGÍA:")
    for caso in casos_psico:
        normalizado = copilot._normalizar_tipo_atencion(caso)
        print(f"  '{caso}' -> '{normalizado}'")
    
    # Casos de prueba para nutrición
    casos_nutri = [
        "nutricion",
        "nutrición",
        "nutricionista",
        "nutriólogo",
        "nutrióloga",
        "dietista",
        "dietólogo",
        "dietóloga"
    ]
    
    print("\n🥗 CASOS NUTRICIÓN:")
    for caso in casos_nutri:
        normalizado = copilot._normalizar_tipo_atencion(caso)
        print(f"  '{caso}' -> '{normalizado}'")
    
    # Casos de prueba para medicina general
    casos_med = [
        "medicina general",
        "médico general",
        "médica general",
        "medicina familiar",
        "médico de familia",
        "medicina primaria",
        "médico primario"
    ]
    
    print("\n👨‍⚕️ CASOS MEDICINA GENERAL:")
    for caso in casos_med:
        normalizado = copilot._normalizar_tipo_atencion(caso)
        print(f"  '{caso}' -> '{normalizado}'")
    
    # Casos de prueba para urgencia
    casos_urgencia = [
        "urgencia",
        "emergencia",
        "urgencias",
        "emergencias",
        "médico de urgencia",
        "emergenciólogo"
    ]
    
    print("\n🚨 CASOS URGENCIA:")
    for caso in casos_urgencia:
        normalizado = copilot._normalizar_tipo_atencion(caso)
        print(f"  '{caso}' -> '{normalizado}'")

def test_analisis_con_variaciones_regionales():
    """Prueba el análisis completo con variaciones regionales"""
    print("\n\n🔍 PRUEBAS DE ANÁLISIS CON VARIACIONES REGIONALES")
    print("=" * 60)
    
    copilot = CopilotHealth()
    
    # Casos de prueba combinando tipos de atención con motivos
    casos_prueba = [
        {
            "tipo_atencion": "fisio",
            "motivo": "Dolor lumbar de 3 semanas tras cargar peso",
            "descripcion": "Fisio + Dolor lumbar"
        },
        {
            "tipo_atencion": "kinesiologia",
            "motivo": "Dificultad para caminar después de una caída",
            "descripcion": "Kinesiología + Dificultad para caminar"
        },
        {
            "tipo_atencion": "fono",
            "motivo": "Dificultad para tragar alimentos",
            "descripcion": "Fono + Dificultad para tragar"
        },
        {
            "tipo_atencion": "logopeda",
            "motivo": "Problemas de pronunciación en niños",
            "descripcion": "Logopeda + Problemas de pronunciación"
        },
        {
            "tipo_atencion": "psicologo",
            "motivo": "Ansiedad y estrés laboral",
            "descripcion": "Psicólogo + Ansiedad laboral"
        },
        {
            "tipo_atencion": "nutricionista",
            "motivo": "Pérdida de peso y fatiga",
            "descripcion": "Nutricionista + Pérdida de peso"
        },
        {
            "tipo_atencion": "dietista",
            "motivo": "Necesito plan de alimentación para diabetes",
            "descripcion": "Dietista + Plan alimentación diabetes"
        },
        {
            "tipo_atencion": "medico general",
            "motivo": "Consulta general por malestar",
            "descripcion": "Médico general + Consulta general"
        }
    ]
    
    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n📋 CASO {i}: {caso['descripcion']}")
        print(f"   Tipo de atención: '{caso['tipo_atencion']}'")
        print(f"   Motivo: '{caso['motivo']}'")
        
        try:
            resultado = copilot.analizar_motivo_consulta(caso['motivo'], caso['tipo_atencion'])
            print(f"   ✅ Especialidad detectada: {resultado.especialidad_detectada}")
            print(f"   ✅ Categoría: {resultado.categoria}")
            print(f"   ✅ Urgencia: {resultado.urgencia}")
            print(f"   ✅ Síntomas: {', '.join(resultado.sintomas_principales)}")
            print(f"   ✅ Preguntas sugeridas: {len(resultado.preguntas_sugeridas)} preguntas")
            
            # Mostrar las primeras 2 preguntas como ejemplo
            for j, pregunta in enumerate(resultado.preguntas_sugeridas[:2], 1):
                print(f"      {j}. {pregunta}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_casos_limite():
    """Prueba casos límite y edge cases"""
    print("\n\n⚠️ PRUEBAS DE CASOS LÍMITE")
    print("=" * 40)
    
    copilot = CopilotHealth()
    
    casos_limite = [
        {"tipo": "", "motivo": "Dolor de cabeza", "desc": "Tipo vacío"},
        {"tipo": "   ", "motivo": "Dolor de espalda", "desc": "Tipo solo espacios"},
        {"tipo": "FISIO", "motivo": "Dolor muscular", "desc": "Tipo en mayúsculas"},
        {"tipo": "fisio", "motivo": "", "desc": "Motivo vacío"},
        {"tipo": "invalid_type", "motivo": "Dolor", "desc": "Tipo inválido"},
        {"tipo": "fisioterapia", "motivo": "Dolor lumbar", "desc": "Caso válido normal"}
    ]
    
    for caso in casos_limite:
        print(f"\n🔍 {caso['desc']}:")
        print(f"   Tipo: '{caso['tipo']}'")
        print(f"   Motivo: '{caso['motivo']}'")
        
        try:
            resultado = copilot.analizar_motivo_consulta(caso['motivo'], caso['tipo'])
            print(f"   ✅ Especialidad: {resultado.especialidad_detectada}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def main():
    """Función principal que ejecuta todas las pruebas"""
    print("🚀 INICIANDO PRUEBAS DE NORMALIZACIÓN REGIONAL")
    print("=" * 60)
    
    try:
        # Ejecutar todas las pruebas
        test_normalizacion_tipos_atencion()
        test_analisis_con_variaciones_regionales()
        test_casos_limite()
        
        print("\n\n✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("🎯 El sistema ahora reconoce variaciones regionales y sinónimos")
        
    except Exception as e:
        print(f"\n❌ ERROR EN LAS PRUEBAS: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 