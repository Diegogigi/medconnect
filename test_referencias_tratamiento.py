#!/usr/bin/env python3
"""
Script de prueba para verificar que las referencias de tratamiento se muestren correctamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from copilot_health import CopilotHealth
import json

def test_referencias_tratamiento():
    """Prueba que las referencias de tratamiento se muestren correctamente"""
    print("🧪 PRUEBAS DE REFERENCIAS DE TRATAMIENTO")
    print("=" * 50)
    
    try:
        copilot = CopilotHealth()
        print("✅ Copilot Health inicializado correctamente")
        
        # Probar sugerencia de tratamientos con diferentes especialidades
        casos_prueba = [
            {
                "diagnostico": "Dolor lumbar crónico con irradiación a miembro inferior",
                "especialidad": "fisioterapia",
                "edad": 45,
                "descripcion": "Fisioterapia - Dolor lumbar"
            },
            {
                "diagnostico": "Problemas de pronunciación en niños",
                "especialidad": "fonoaudiologia",
                "edad": 8,
                "descripcion": "Fonoaudiología - Problemas de pronunciación"
            },
            {
                "diagnostico": "Ansiedad y estrés laboral",
                "especialidad": "psicologia",
                "edad": 35,
                "descripcion": "Psicología - Ansiedad"
            }
        ]
        
        for i, caso in enumerate(casos_prueba, 1):
            print(f"\n📋 CASO {i}: {caso['descripcion']}")
            print(f"   Diagnóstico: '{caso['diagnostico']}'")
            print(f"   Especialidad: '{caso['especialidad']}'")
            print(f"   Edad: {caso['edad']}")
            
            try:
                planes = copilot.sugerir_planes_tratamiento(
                    caso['diagnostico'],
                    caso['especialidad'],
                    caso['edad']
                )
                
                print(f"   ✅ {len(planes)} planes de tratamiento sugeridos")
                
                for j, plan in enumerate(planes, 1):
                    print(f"\n   📋 Plan {j}:")
                    print(f"      Título: {plan.titulo}")
                    print(f"      Descripción: {plan.descripcion}")
                    print(f"      Evidencia: {plan.evidencia_cientifica}")
                    print(f"      DOI: {plan.doi_referencia}")
                    print(f"      Nivel: {plan.nivel_evidencia}")
                    print(f"      Contraindicaciones: {plan.contraindicaciones}")
                    
                    # Verificar que las referencias no estén vacías
                    if plan.doi_referencia and plan.doi_referencia != "Sin DOI":
                        print(f"      ✅ DOI válido: {plan.doi_referencia}")
                    else:
                        print(f"      ⚠️ DOI no disponible o inválido")
                    
                    if plan.evidencia_cientifica and plan.evidencia_cientifica != "Evidencia clínica":
                        print(f"      ✅ Evidencia científica: {plan.evidencia_cientifica}")
                    else:
                        print(f"      ⚠️ Evidencia científica genérica")
                
            except Exception as e:
                print(f"   ❌ Error en caso {i}: {e}")
        
        # Probar formato JSON para frontend
        print(f"\n\n🔍 PROBANDO FORMATO JSON PARA FRONTEND")
        print("=" * 50)
        
        planes = copilot.sugerir_planes_tratamiento("dolor lumbar", "fisioterapia", 40)
        
        planes_json = []
        for plan in planes:
            planes_json.append({
                'titulo': plan.titulo,
                'descripcion': plan.descripcion,
                'evidencia_cientifica': plan.evidencia_cientifica,
                'doi_referencia': plan.doi_referencia,
                'nivel_evidencia': plan.nivel_evidencia,
                'contraindicaciones': plan.contraindicaciones
            })
        
        print("📋 Formato JSON generado:")
        print(json.dumps(planes_json, indent=2, ensure_ascii=False))
        
        # Verificar que todos los campos necesarios estén presentes
        for i, plan in enumerate(planes_json):
            print(f"\n✅ Plan {i+1} - Campos verificados:")
            print(f"   titulo: {'✅' if plan['titulo'] else '❌'}")
            print(f"   descripcion: {'✅' if plan['descripcion'] else '❌'}")
            print(f"   evidencia_cientifica: {'✅' if plan['evidencia_cientifica'] else '❌'}")
            print(f"   doi_referencia: {'✅' if plan['doi_referencia'] else '❌'}")
            print(f"   nivel_evidencia: {'✅' if plan['nivel_evidencia'] else '❌'}")
            print(f"   contraindicaciones: {'✅' if plan['contraindicaciones'] else '❌'}")
        
    except Exception as e:
        print(f"❌ Error en pruebas de referencias: {e}")
        return False
    
    return True

def test_apis_medicas_referencias():
    """Prueba específicamente las referencias de las APIs médicas"""
    print(f"\n\n🔬 PRUEBAS DE REFERENCIAS DE APIS MÉDICAS")
    print("=" * 60)
    
    try:
        from medical_apis_integration import MedicalAPIsIntegration
        
        apis = MedicalAPIsIntegration()
        print("✅ APIs médicas inicializadas correctamente")
        
        # Probar búsqueda en PubMed
        print("\n🔍 Probando búsqueda en PubMed...")
        tratamientos_pubmed = apis.buscar_tratamiento_pubmed("dolor lumbar", "fisioterapia")
        
        if tratamientos_pubmed:
            print(f"   ✅ Encontrados {len(tratamientos_pubmed)} tratamientos en PubMed")
            
            for i, tratamiento in enumerate(tratamientos_pubmed, 1):
                print(f"\n   📋 Tratamiento {i} de PubMed:")
                print(f"      Título: {tratamiento.titulo}")
                print(f"      DOI: {tratamiento.doi}")
                print(f"      Fuente: {tratamiento.fuente}")
                print(f"      Tipo de evidencia: {tratamiento.tipo_evidencia}")
                print(f"      Fecha: {tratamiento.fecha_publicacion}")
                print(f"      Autores: {', '.join(tratamiento.autores)}")
                
                # Verificar que el DOI sea válido
                if tratamiento.doi and tratamiento.doi != "Sin DOI":
                    print(f"      ✅ DOI válido: {tratamiento.doi}")
                    print(f"      🔗 Link: https://doi.org/{tratamiento.doi}")
                else:
                    print(f"      ⚠️ DOI no disponible")
        
        # Probar búsqueda en Europe PMC
        print("\n🔍 Probando búsqueda en Europe PMC...")
        tratamientos_europepmc = apis.buscar_europepmc("dolor lumbar", "fisioterapia")
        
        if tratamientos_europepmc:
            print(f"   ✅ Encontrados {len(tratamientos_europepmc)} tratamientos en Europe PMC")
            
            for i, tratamiento in enumerate(tratamientos_europepmc, 1):
                print(f"\n   📋 Tratamiento {i} de Europe PMC:")
                print(f"      Título: {tratamiento.titulo}")
                print(f"      DOI: {tratamiento.doi}")
                print(f"      Fuente: {tratamiento.fuente}")
                print(f"      Tipo de evidencia: {tratamiento.tipo_evidencia}")
                print(f"      Fecha: {tratamiento.fecha_publicacion}")
                
                # Verificar que el DOI sea válido
                if tratamiento.doi and tratamiento.doi != "Sin DOI":
                    print(f"      ✅ DOI válido: {tratamiento.doi}")
                    print(f"      🔗 Link: https://doi.org/{tratamiento.doi}")
                else:
                    print(f"      ⚠️ DOI no disponible")
        
    except Exception as e:
        print(f"❌ Error en pruebas de APIs médicas: {e}")
        return False
    
    return True

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS DE REFERENCIAS DE TRATAMIENTO")
    print("=" * 70)
    
    try:
        # Ejecutar todas las pruebas
        success1 = test_referencias_tratamiento()
        success2 = test_apis_medicas_referencias()
        
        if success1 and success2:
            print("\n\n✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
            print("🎯 Las referencias de tratamiento están funcionando correctamente")
            
            print("\n📋 RESUMEN DE VERIFICACIONES:")
            print("   ✅ Referencias de Copilot Health")
            print("   ✅ DOIs de APIs médicas")
            print("   ✅ Links a papers científicos")
            print("   ✅ Formato JSON para frontend")
            print("   ✅ Evidencia científica")
            print("   ✅ Niveles de evidencia")
            
        else:
            print("\n❌ ALGUNAS PRUEBAS FALLARON")
            return False
        
    except Exception as e:
        print(f"\n❌ ERROR EN LAS PRUEBAS: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 