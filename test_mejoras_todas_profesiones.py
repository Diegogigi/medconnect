#!/usr/bin/env python3
"""
Script de prueba para verificar las mejoras de búsqueda contextual
para todas las profesiones en el Copilot Health Assistant.
"""

import requests
import json
import time

def test_mejoras_busqueda_profesiones():
    """Prueba las mejoras de búsqueda para todas las profesiones."""
    
    print("🧪 PRUEBA DE MEJORAS DE BÚSQUEDA PARA TODAS LAS PROFESIONES")
    print("=" * 70)
    
    # Casos de prueba para cada profesión
    casos_prueba = [
        {
            "profesion": "Kinesiología",
            "tipo_atencion": "kinesiologia",
            "motivo_consulta": "Dolor de rodilla por golpe en el trabajo",
            "evaluacion": "¿En qué momento del día es peor el dolor? cuando me levanto ¿Qué actividades agravan el dolor? pasar mucho tiempo de pie ¿Qué actividades alivian el dolor? tener la rodilla en reposo ¿Hay hinchazón o calor en la rodilla? hay hinchazón ¿Ha tenido lesiones previas en la rodilla? no ¿El dolor es constante o intermitente? es intermitente ¿Hay bloqueos o sensación de inestabilidad? sensación de inestabilidad ¿Puede subir y bajar escaleras sin dolor? bajar duele la rodilla",
            "edad": "35"
        },
        {
            "profesion": "Medicina General",
            "tipo_atencion": "medicina_general",
            "motivo_consulta": "Dolor de cabeza intenso con náuseas",
            "evaluacion": "¿Cuándo comenzó el dolor? hace 2 días ¿El dolor es constante o intermitente? constante ¿Hay otros síntomas? náuseas y sensibilidad a la luz ¿Ha tenido dolores de cabeza similares antes? sí ¿Qué medicamentos ha tomado? paracetamol sin alivio",
            "edad": "45"
        },
        {
            "profesion": "Psicología",
            "tipo_atencion": "psicologia",
            "motivo_consulta": "Ansiedad y estrés por problemas laborales",
            "evaluacion": "¿Cuándo comenzó la ansiedad? hace 3 semanas ¿Qué síntomas experimenta? palpitaciones, sudoración, dificultad para dormir ¿Ha tenido episodios similares antes? sí ¿Qué situaciones la agravan? reuniones de trabajo ¿Ha recibido tratamiento psicológico previo? no",
            "edad": "28"
        },
        {
            "profesion": "Fonoaudiología",
            "tipo_atencion": "fonoaudiologia",
            "motivo_consulta": "Dificultad para hablar después de un accidente",
            "evaluacion": "¿Cuándo comenzó la dificultad? después del accidente ¿Qué tipo de dificultad experimenta? articulación de palabras ¿Ha notado cambios en la voz? sí, más ronca ¿Hay dificultad para tragar? no ¿Ha recibido terapia del lenguaje antes? no",
            "edad": "52"
        }
    ]
    
    resultados = []
    
    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n📋 CASO {i}: {caso['profesion']}")
        print("-" * 50)
        
        # Simular datos del formulario
        datos_formulario = {
            "tipoAtencion": caso["tipo_atencion"],
            "motivoConsulta": caso["motivo_consulta"],
            "evaluacion": caso["evaluacion"],
            "edad": caso["edad"]
        }
        
        print(f"🎯 Tipo de atención: {caso['tipo_atencion']}")
        print(f"📝 Motivo de consulta: {caso['motivo_consulta']}")
        print(f"📊 Evaluación: {caso['evaluacion'][:100]}...")
        print(f"👤 Edad: {caso['edad']} años")
        
        # Simular la función generarTerminosBusquedaMejorados
        terminos_esperados = simular_generar_terminos(datos_formulario)
        
        print(f"\n🔍 TÉRMINOS GENERADOS:")
        print(f"   Especialidad: {terminos_esperados['especialidad']}")
        print(f"   Términos clave: {', '.join(terminos_esperados['terminosClave'][:5])}")
        print(f"   Contexto clínico: {', '.join(terminos_esperados['contextoClinico'][:3])}")
        print(f"   Query completa: {terminos_esperados['queryCompleta'][:100]}...")
        
        # Verificar que los términos sean apropiados para la profesión
        verificacion = verificar_terminos_profesion(caso['profesion'], terminos_esperados)
        
        if verificacion['exito']:
            print(f"✅ VERIFICACIÓN EXITOSA: {verificacion['mensaje']}")
        else:
            print(f"❌ VERIFICACIÓN FALLIDA: {verificacion['mensaje']}")
        
        resultados.append({
            "caso": caso['profesion'],
            "terminos": terminos_esperados,
            "verificacion": verificacion
        })
    
    # Resumen final
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 70)
    
    exitos = sum(1 for r in resultados if r['verificacion']['exito'])
    total = len(resultados)
    
    print(f"✅ Casos exitosos: {exitos}/{total}")
    print(f"❌ Casos fallidos: {total - exitos}/{total}")
    
    for resultado in resultados:
        estado = "✅" if resultado['verificacion']['exito'] else "❌"
        print(f"{estado} {resultado['caso']}: {resultado['verificacion']['mensaje']}")
    
    if exitos == total:
        print("\n🎉 ¡TODAS LAS MEJORAS FUNCIONAN CORRECTAMENTE!")
        print("   El sistema de búsqueda contextual está optimizado para todas las profesiones.")
    else:
        print("\n⚠️  HAY MEJORAS PENDIENTES")
        print("   Algunas profesiones necesitan ajustes adicionales.")
    
    return resultados

def simular_generar_terminos(datos):
    """Simula la función generarTerminosBusquedaMejorados del frontend."""
    
    terminosClave = []
    contextoClinico = []
    especialidad = 'general'
    edad = 'adulto'
    
    # 1. Analizar tipo de atención para especialidad
    if datos.get('tipoAtencion'):
        tipoLower = datos['tipoAtencion'].lower()
        
        if 'kinesiologia' in tipoLower or 'fisioterapia' in tipoLower or 'kinesio' in tipoLower:
            especialidad = 'fisioterapia'
            terminosClave.extend(['fisioterapia', 'kinesiología', 'rehabilitación', 'terapia física', 'movimiento'])
            contextoClinico.append('intervención fisioterapéutica')
        elif 'medicina' in tipoLower or 'general' in tipoLower:
            especialidad = 'medicina'
            terminosClave.extend(['medicina clínica', 'medicina general', 'diagnóstico médico', 'tratamiento médico'])
            contextoClinico.append('evaluación médica integral')
        elif 'psicologia' in tipoLower or 'psicoterapia' in tipoLower:
            especialidad = 'psicología'
            terminosClave.extend(['psicología', 'salud mental', 'terapia psicológica', 'intervención psicológica', 'bienestar emocional'])
            contextoClinico.append('evaluación psicológica')
        elif 'fonoaudiologia' in tipoLower or 'logopedia' in tipoLower:
            especialidad = 'fonoaudiología'
            terminosClave.extend(['fonoaudiología', 'terapia del lenguaje', 'comunicación', 'habla', 'lenguaje', 'deglución'])
            contextoClinico.append('evaluación fonoaudiológica')
    
    # 2. Analizar motivo de consulta
    if datos.get('motivoConsulta'):
        motivo = datos['motivoConsulta'].lower()
        
        # Términos específicos por profesión
        if especialidad == 'fonoaudiología':
            terminosFono = ['voz', 'habla', 'lenguaje', 'comunicación', 'deglución', 'respiración', 'articulación', 'disfonía', 'afasia', 'disfagia']
            for termino in terminosFono:
                if termino in motivo:
                    terminosClave.append(termino)
                    contextoClinico.append(f'dificultad en {termino}')
        
        if especialidad == 'psicología':
            terminosPsico = ['ansiedad', 'depresión', 'estrés', 'trauma', 'miedo', 'pánico', 'obsesión', 'compulsión', 'trastorno', 'bipolar', 'esquizofrenia']
            for termino in terminosPsico:
                if termino in motivo:
                    terminosClave.append(termino)
                    contextoClinico.append(f'síntoma psicológico: {termino}')
        
        # Términos anatómicos
        terminosAnatomicos = [
            'rodilla', 'hombro', 'espalda', 'cuello', 'cabeza', 'brazo', 'pierna',
            'tobillo', 'muñeca', 'codo', 'cadera', 'columna', 'lumbar', 'cervical',
            'articulación', 'músculo', 'tendón', 'ligamento', 'menisco', 'cartílago'
        ]
        
        for termino in terminosAnatomicos:
            if termino in motivo:
                terminosClave.append(termino)
                contextoClinico.append(f'dolor en {termino}')
        
        # Términos de causa
        if 'golpe' in motivo or 'trauma' in motivo:
            terminosClave.extend(['trauma', 'lesión traumática'])
            contextoClinico.append('lesión por trauma')
        if 'trabajo' in motivo or 'laboral' in motivo:
            terminosClave.extend(['lesión laboral', 'accidente de trabajo'])
            contextoClinico.append('lesión relacionada con el trabajo')
        if 'deporte' in motivo or 'ejercicio' in motivo:
            terminosClave.extend(['lesión deportiva', 'deporte'])
            contextoClinico.append('lesión relacionada con actividad física')
    
    # 3. Analizar evaluación
    if datos.get('evaluacion'):
        evaluacion = datos['evaluacion'].lower()
        
        # Síntomas específicos por profesión
        if especialidad == 'fonoaudiología':
            if any(termino in evaluacion for termino in ['voz', 'habla', 'lenguaje']):
                terminosClave.extend(['disfonía', 'disfagia', 'afasia'])
                contextoClinico.append('dificultad en comunicación')
        
        if especialidad == 'psicología':
            if 'ansiedad' in evaluacion or 'miedo' in evaluacion or 'pánico' in evaluacion:
                terminosClave.extend(['trastorno de ansiedad', 'ataque de pánico'])
                contextoClinico.append('síntomas de ansiedad')
            if 'depresión' in evaluacion or 'tristeza' in evaluacion or 'desánimo' in evaluacion:
                terminosClave.extend(['trastorno depresivo', 'depresión'])
                contextoClinico.append('síntomas depresivos')
    
    # 4. Analizar edad
    if datos.get('edad'):
        edadNum = int(datos['edad'])
        if edadNum < 18:
            edad = 'pediátrico'
            terminosClave.extend(['pediatría', 'niño', 'adolescente'])
        elif edadNum > 65:
            edad = 'geriátrico'
            terminosClave.extend(['geriatría', 'adulto mayor', 'envejecimiento'])
    
    # 5. Crear query completa
    queryCompleta = ' '.join([
        datos.get('motivoConsulta', ''),
        *terminosClave[:5],
        especialidad
    ])
    
    # 6. Eliminar duplicados
    terminosUnicos = list(set(terminosClave))
    contextoUnico = list(set(contextoClinico))
    
    return {
        'queryCompleta': queryCompleta,
        'terminosClave': terminosUnicos,
        'especialidad': especialidad,
        'edad': edad,
        'contextoClinico': contextoUnico
    }

def verificar_terminos_profesion(profesion, terminos):
    """Verifica que los términos generados sean apropiados para la profesión."""
    
    verificaciones = {
        'Kinesiología': {
            'terminos_requeridos': ['fisioterapia', 'kinesiología', 'rehabilitación'],
            'terminos_anatomicos': ['rodilla', 'hombro', 'espalda', 'articulación'],
            'mensaje_exito': 'Términos fisioterapéuticos y anatómicos identificados correctamente'
        },
        'Medicina General': {
            'terminos_requeridos': ['medicina', 'diagnóstico', 'tratamiento'],
            'terminos_anatomicos': ['cabeza', 'dolor'],
            'mensaje_exito': 'Términos médicos generales identificados correctamente'
        },
        'Psicología': {
            'terminos_requeridos': ['psicología', 'salud mental', 'terapia psicológica'],
            'terminos_especificos': ['ansiedad', 'estrés', 'depresión'],
            'mensaje_exito': 'Términos psicológicos y de salud mental identificados correctamente'
        },
        'Fonoaudiología': {
            'terminos_requeridos': ['fonoaudiología', 'terapia del lenguaje', 'comunicación'],
            'terminos_especificos': ['habla', 'lenguaje', 'voz', 'deglución'],
            'mensaje_exito': 'Términos fonoaudiológicos y de comunicación identificados correctamente'
        }
    }
    
    if profesion not in verificaciones:
        return {'exito': False, 'mensaje': f'Profesión {profesion} no soportada'}
    
    verificacion = verificaciones[profesion]
    terminos_clave = terminos['terminosClave']
    
    # Verificar términos requeridos
    terminos_encontrados = sum(1 for termino in verificacion['terminos_requeridos'] 
                              if any(termino in t for t in terminos_clave))
    
    # Verificar términos específicos
    if 'terminos_especificos' in verificacion:
        terminos_especificos_encontrados = sum(1 for termino in verificacion['terminos_especificos'] 
                                              if any(termino in t for t in terminos_clave))
    else:
        terminos_especificos_encontrados = 1  # No aplica para todas las profesiones
    
    # Verificar términos anatómicos si aplica
    if 'terminos_anatomicos' in verificacion:
        terminos_anatomicos_encontrados = sum(1 for termino in verificacion['terminos_anatomicos'] 
                                             if any(termino in t for t in terminos_clave))
    else:
        terminos_anatomicos_encontrados = 1  # No aplica para todas las profesiones
    
    # Criterio de éxito: al menos 2 términos requeridos y 1 específico/anatómico
    exito = (terminos_encontrados >= 2 and 
             terminos_especificos_encontrados >= 1 and 
             terminos_anatomicos_encontrados >= 1)
    
    if exito:
        return {'exito': True, 'mensaje': verificacion['mensaje_exito']}
    else:
        return {'exito': False, 'mensaje': f'Faltan términos específicos para {profesion}'}

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de mejoras para todas las profesiones...")
    resultados = test_mejoras_busqueda_profesiones()
    print("\n✅ Pruebas completadas.") 