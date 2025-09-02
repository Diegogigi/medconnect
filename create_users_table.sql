-- Script para crear la tabla de usuarios
-- Ejecutar en Railway PostgreSQL

-- Crear tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    tipo_usuario VARCHAR(20) NOT NULL CHECK (tipo_usuario IN ('paciente', 'profesional')),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE
);

-- Crear índice para búsquedas por email
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);

-- Crear índice para búsquedas por tipo de usuario
CREATE INDEX IF NOT EXISTS idx_usuarios_tipo ON usuarios(tipo_usuario);

-- Agregar comentarios
COMMENT ON TABLE usuarios IS 'Tabla de usuarios del sistema (pacientes y profesionales)';
COMMENT ON COLUMN usuarios.email IS 'Email único del usuario';
COMMENT ON COLUMN usuarios.password_hash IS 'Hash de la contraseña';
COMMENT ON COLUMN usuarios.tipo_usuario IS 'Tipo de usuario: paciente o profesional';
COMMENT ON COLUMN usuarios.activo IS 'Estado del usuario en el sistema';

-- Verificar que la tabla se creó correctamente
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'usuarios' 
ORDER BY ordinal_position; 