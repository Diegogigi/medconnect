# 🚀 CONFIGURACIÓN POSTGRESQL EN RAILWAY

## ✅ VARIABLES DE ENTORNO NECESARIAS

Configura estas variables en tu proyecto de Railway:

### **🔗 BASE DE DATOS**

```
DATABASE_URL=postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway
```

### **🔑 AUTENTICACIÓN**

```
SECRET_KEY=tu_secret_key_super_seguro_aqui
FLASK_ENV=production
```

### **🤖 OPENROUTER API**

```
OPENROUTER_API_KEY=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
```

### **🌐 PUERTO**

```
PORT=8000
```

## 📋 PASOS PARA CONFIGURAR

1. **Ve a Railway Dashboard**
2. **Selecciona tu proyecto MedConnect**
3. **Ve a "Variables" o "Environment"**
4. **Agrega cada variable** con su valor correspondiente
5. **Guarda los cambios**
6. **Railway redeployeará automáticamente**

## 🎯 RESULTADO ESPERADO

Una vez configuradas las variables:

- ✅ La aplicación usará PostgreSQL en lugar de Google Sheets
- ✅ Los usuarios podrán iniciar sesión con credenciales reales
- ✅ Todas las funcionalidades estarán disponibles
- ✅ La aplicación será más rápida y confiable

## 🔍 VERIFICACIÓN

Para verificar que todo funciona:

1. **Accede a tu aplicación** en Railway
2. **Intenta iniciar sesión** con:
   - Email: `diego.castro.lagos@gmail.com`
   - Password: `password123`
3. **Verifica que puedes navegar** por todas las secciones

## 🚨 IMPORTANTE

- **No compartas** las credenciales de la base de datos
- **Mantén seguras** las variables de entorno
- **Haz backup** regular de la base de datos
