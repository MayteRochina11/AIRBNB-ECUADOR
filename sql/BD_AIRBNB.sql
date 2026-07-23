
-- =========================================================
-- SISTEMA INMOBILIARIO (venta | arriendo | hospedaje corto)
-- Script COMPLETO de creación de base de datos - PostgreSQL
-- PARTE 1: Tablas, PKs, FKs, CHECKs e índices
-- =========================================================

-- Si quieres arrancar limpio, descomenta:
-- DROP SCHEMA public CASCADE;
-- CREATE SCHEMA public;

-- =========================================================
-- 1. USUARIOS
-- =========================================================
CREATE TABLE USUARIOS (
    id_usuario      SERIAL PRIMARY KEY,
    nombre          VARCHAR(150) NOT NULL,
    email           VARCHAR(150) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    rol             VARCHAR(20)  NOT NULL
                    CHECK (rol IN ('host', 'agente', 'comprador', 'viajero')),
    verificado      BOOLEAN NOT NULL DEFAULT FALSE,
    telefono        VARCHAR(20)
);

-- =========================================================
-- 2. AGENTES  
-- =========================================================
CREATE TABLE AGENTES (
    id_agente             SERIAL PRIMARY KEY,
    id_usuario            INT NOT NULL UNIQUE
                          REFERENCES USUARIOS(id_usuario) ON DELETE CASCADE,
    licencia              VARCHAR(100),
    especialidad          VARCHAR(20)
                          CHECK (especialidad IN ('venta', 'arriendo', 'ambos')),
    comision_porcentaje   DECIMAL(5,2),
    propiedades_activas   INT DEFAULT 0
);

-- =========================================================
-- 3. PROPIEDADES
-- =========================================================
CREATE TABLE PROPIEDADES (
    id_propiedad        SERIAL PRIMARY KEY,
    id_propietario       INT NOT NULL REFERENCES USUARIOS(id_usuario),
    id_agente            INT REFERENCES AGENTES(id_agente),
    titulo               VARCHAR(200) NOT NULL,
    descripcion          TEXT,
    tipo_propiedad       VARCHAR(20) NOT NULL
                         CHECK (tipo_propiedad IN ('casa', 'cabana', 'habitacion', 'apartamento')),
    modalidad            VARCHAR(20) NOT NULL
                         CHECK (modalidad IN ('venta', 'arriendo', 'hospedaje_corto')),
    ciudad               VARCHAR(100) NOT NULL,
    direccion            VARCHAR(255),
    precio               DECIMAL(12,2) NOT NULL,
    unidad_precio        VARCHAR(10) NOT NULL
                         CHECK (unidad_precio IN ('total', 'mes', 'noche')),
    capacidad_personas   INT,
    habitaciones         INT,
    banos                INT,
    metros_cuadrados     DECIMAL(8,2),
    activa               BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX idx_propiedades_propietario ON PROPIEDADES(id_propietario);
CREATE INDEX idx_propiedades_agente ON PROPIEDADES(id_agente);
CREATE INDEX idx_propiedades_ciudad ON PROPIEDADES(ciudad);

-- =========================================================
-- 4. FOTOS_PROPIEDAD
-- =========================================================
CREATE TABLE FOTOS_PROPIEDAD (
    id_foto        SERIAL PRIMARY KEY,
    id_propiedad   INT NOT NULL REFERENCES PROPIEDADES(id_propiedad) ON DELETE CASCADE,
    url_foto       VARCHAR(500) NOT NULL,
    es_principal   BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX idx_fotos_propiedad ON FOTOS_PROPIEDAD(id_propiedad);

-- =========================================================
-- 5. AMENIDADES
-- =========================================================
CREATE TABLE AMENIDADES (
    id_amenidad   SERIAL PRIMARY KEY,
    nombre        VARCHAR(100) NOT NULL,
    categoria     VARCHAR(20)
                 CHECK (categoria IN ('basica', 'premium', 'exterior'))
);

-- =========================================================
-- 6. PROPIEDAD_AMENIDADES (N:M)
-- =========================================================
CREATE TABLE PROPIEDAD_AMENIDADES (
    id_propiedad   INT NOT NULL REFERENCES PROPIEDADES(id_propiedad) ON DELETE CASCADE,
    id_amenidad    INT NOT NULL REFERENCES AMENIDADES(id_amenidad) ON DELETE CASCADE,
    PRIMARY KEY (id_propiedad, id_amenidad)
);

-- =========================================================
-- 7. DISPONIBILIDAD
-- =========================================================
CREATE TABLE DISPONIBILIDAD (
    id_disponibilidad   SERIAL PRIMARY KEY,
    id_propiedad        INT NOT NULL REFERENCES PROPIEDADES(id_propiedad) ON DELETE CASCADE,
    fecha               DATE NOT NULL,
    disponible          BOOLEAN NOT NULL DEFAULT TRUE,
    precio_especial     DECIMAL(12,2),
    UNIQUE (id_propiedad, fecha)
);

CREATE INDEX idx_disponibilidad_propiedad_fecha ON DISPONIBILIDAD(id_propiedad, fecha);

-- =========================================================
-- 8. RESERVAS_HOSPEDAJE
-- =========================================================
CREATE TABLE RESERVAS_HOSPEDAJE (
    id_reserva        SERIAL PRIMARY KEY,
    id_propiedad      INT NOT NULL REFERENCES PROPIEDADES(id_propiedad),
    id_huesped        INT NOT NULL REFERENCES USUARIOS(id_usuario),
    fecha_entrada     DATE NOT NULL,
    fecha_salida      DATE NOT NULL,
    num_huespedes     INT NOT NULL,
    precio_total      DECIMAL(12,2) NOT NULL,
    estado            VARCHAR(20) NOT NULL DEFAULT 'pendiente'
                     CHECK (estado IN ('pendiente', 'confirmada', 'cancelada', 'completada')),
    tipo_alojamiento  VARCHAR(20)
                     CHECK (tipo_alojamiento IN ('hospedaje', 'cabana')),
    CHECK (fecha_salida > fecha_entrada)
);

CREATE INDEX idx_reservas_propiedad ON RESERVAS_HOSPEDAJE(id_propiedad);
CREATE INDEX idx_reservas_huesped ON RESERVAS_HOSPEDAJE(id_huesped);

-- =========================================================
-- 9. CONTRATOS_ARRIENDO
-- =========================================================
CREATE TABLE CONTRATOS_ARRIENDO (
    id_contrato        SERIAL PRIMARY KEY,
    id_propiedad       INT NOT NULL UNIQUE REFERENCES PROPIEDADES(id_propiedad),
    id_arrendatario    INT NOT NULL REFERENCES USUARIOS(id_usuario),
    id_propietario     INT NOT NULL REFERENCES USUARIOS(id_usuario),
    fecha_inicio       DATE NOT NULL,
    fecha_fin          DATE,
    canon_mensual      DECIMAL(12,2) NOT NULL,
    deposito_garantia  DECIMAL(12,2),
    estado             VARCHAR(20) NOT NULL DEFAULT 'borrador'
                      CHECK (estado IN ('borrador', 'activo', 'vencido', 'terminado')),
    duracion_meses     INT
);

CREATE INDEX idx_contratos_arrendatario ON CONTRATOS_ARRIENDO(id_arrendatario);
CREATE INDEX idx_contratos_propietario ON CONTRATOS_ARRIENDO(id_propietario);

-- =========================================================
-- 10. PROCESO_VENTA
-- =========================================================
CREATE TABLE PROCESO_VENTA (
    id_venta         SERIAL PRIMARY KEY,
    id_propiedad     INT NOT NULL UNIQUE REFERENCES PROPIEDADES(id_propiedad),
    id_comprador     INT REFERENCES USUARIOS(id_usuario),
    id_vendedor      INT NOT NULL REFERENCES USUARIOS(id_usuario),
    id_agente        INT REFERENCES AGENTES(id_agente),
    precio_oferta    DECIMAL(12,2),
    precio_acordado  DECIMAL(12,2),
    estado           VARCHAR(20) NOT NULL DEFAULT 'oferta'
                    CHECK (estado IN ('oferta', 'negociacion', 'aprobado', 'escritura', 'cerrado')),
    fecha_oferta     DATE,
    fecha_cierre     DATE
);

CREATE INDEX idx_venta_comprador ON PROCESO_VENTA(id_comprador);
CREATE INDEX idx_venta_vendedor ON PROCESO_VENTA(id_vendedor);
CREATE INDEX idx_venta_agente ON PROCESO_VENTA(id_agente);

-- =========================================================
-- 11. OFERTAS_COMPRA
-- =========================================================
CREATE TABLE OFERTAS_COMPRA (
    id_oferta      SERIAL PRIMARY KEY,
    id_venta       INT NOT NULL REFERENCES PROCESO_VENTA(id_venta) ON DELETE CASCADE,
    id_comprador   INT NOT NULL REFERENCES USUARIOS(id_usuario),
    monto_oferta   DECIMAL(12,2) NOT NULL,
    mensaje        TEXT,
    estado         VARCHAR(20) NOT NULL DEFAULT 'enviada'
                  CHECK (estado IN ('enviada', 'aceptada', 'rechazada', 'contraoferta')),
    fecha_oferta   DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE INDEX idx_ofertas_venta ON OFERTAS_COMPRA(id_venta);

-- =========================================================
-- 12. DOCUMENTOS  (referencia polimórfica: venta | arriendo | reserva)
-- =========================================================
CREATE TABLE DOCUMENTOS (
    id_documento     SERIAL PRIMARY KEY,
    id_referencia    INT NOT NULL,   -- apunta a PROCESO_VENTA / CONTRATOS_ARRIENDO / RESERVAS_HOSPEDAJE según tipo_referencia
    tipo_referencia  VARCHAR(20) NOT NULL
                    CHECK (tipo_referencia IN ('venta', 'arriendo', 'reserva')),
    tipo_doc         VARCHAR(20)
                    CHECK (tipo_doc IN ('contrato', 'escritura', 'recibo', 'identificacion')),
    url_archivo      VARCHAR(500) NOT NULL,
    fecha_subida     DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE INDEX idx_documentos_referencia ON DOCUMENTOS(tipo_referencia, id_referencia);

-- =========================================================
-- 13. PAGOS  (referencia polimórfica: reserva | arriendo | venta)
-- =========================================================
CREATE TABLE PAGOS (
    id_pago          SERIAL PRIMARY KEY,
    id_referencia    INT NOT NULL,   -- apunta a RESERVAS_HOSPEDAJE / CONTRATOS_ARRIENDO / PROCESO_VENTA según tipo_referencia
    tipo_referencia  VARCHAR(20) NOT NULL
                    CHECK (tipo_referencia IN ('reserva', 'arriendo', 'venta')),
    monto            DECIMAL(12,2) NOT NULL,
    metodo_pago      VARCHAR(50),
    estado           VARCHAR(20) NOT NULL DEFAULT 'pendiente'
                    CHECK (estado IN ('pendiente', 'completado', 'fallido', 'reembolsado')),
    concepto         VARCHAR(20)
                    CHECK (concepto IN ('canon', 'deposito', 'reserva', 'cuota_inicial')),
    fecha_pago       DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE INDEX idx_pagos_referencia ON PAGOS(tipo_referencia, id_referencia);

-- =========================================================
-- 14. RESEÑAS  (referencia polimórfica: reserva | arriendo)
-- =========================================================
CREATE TABLE RESEÑAS (
    id_resena        SERIAL PRIMARY KEY,
    id_propiedad     INT NOT NULL REFERENCES PROPIEDADES(id_propiedad) ON DELETE CASCADE,
    id_autor         INT NOT NULL REFERENCES USUARIOS(id_usuario),
    id_referencia    INT NOT NULL,   -- apunta a RESERVAS_HOSPEDAJE / CONTRATOS_ARRIENDO según tipo_referencia
    tipo_referencia  VARCHAR(20) NOT NULL
                    CHECK (tipo_referencia IN ('reserva', 'arriendo')),
    calificacion     INT NOT NULL CHECK (calificacion BETWEEN 1 AND 5),
    comentario       TEXT,
    cal_limpieza     INT CHECK (cal_limpieza BETWEEN 1 AND 5),
    cal_ubicacion    INT CHECK (cal_ubicacion BETWEEN 1 AND 5),
    cal_comunicacion INT CHECK (cal_comunicacion BETWEEN 1 AND 5)
);

CREATE INDEX idx_resenas_propiedad ON RESEÑAS(id_propiedad);
CREATE INDEX idx_resenas_referencia ON RESEÑAS(tipo_referencia, id_referencia);

-- =========================================================
-- TRIGGERS DE VALIDACIÓN PARA REFERENCIAS POLIMÓRFICAS
-- (DOCUMENTOS, PAGOS, RESEÑAS)
-- =========================================================

-- =========================================================
-- 1. DOCUMENTOS
--    tipo_referencia: 'venta' -> PROCESO_VENTA
--                     'arriendo' -> CONTRATOS_ARRIENDO
--                     'reserva' -> RESERVAS_HOSPEDAJE
-- =========================================================
CREATE OR REPLACE FUNCTION fn_validar_referencia_documentos()
RETURNS TRIGGER AS $$
DECLARE
    existe BOOLEAN;
BEGIN
    CASE NEW.tipo_referencia
        WHEN 'venta' THEN
            SELECT EXISTS(SELECT 1 FROM PROCESO_VENTA WHERE id_venta = NEW.id_referencia) INTO existe;
        WHEN 'arriendo' THEN
            SELECT EXISTS(SELECT 1 FROM CONTRATOS_ARRIENDO WHERE id_contrato = NEW.id_referencia) INTO existe;
        WHEN 'reserva' THEN
            SELECT EXISTS(SELECT 1 FROM RESERVAS_HOSPEDAJE WHERE id_reserva = NEW.id_referencia) INTO existe;
        ELSE
            RAISE EXCEPTION 'tipo_referencia % no es válido en DOCUMENTOS', NEW.tipo_referencia;
    END CASE;

    IF NOT existe THEN
        RAISE EXCEPTION 'id_referencia % no existe en la tabla correspondiente a tipo_referencia=%',
            NEW.id_referencia, NEW.tipo_referencia;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validar_referencia_documentos
BEFORE INSERT OR UPDATE ON DOCUMENTOS
FOR EACH ROW
EXECUTE FUNCTION fn_validar_referencia_documentos();


-- =========================================================
-- 2. PAGOS
--    tipo_referencia: 'reserva' -> RESERVAS_HOSPEDAJE
--                     'arriendo' -> CONTRATOS_ARRIENDO
--                     'venta' -> PROCESO_VENTA
-- =========================================================
CREATE OR REPLACE FUNCTION fn_validar_referencia_pagos()
RETURNS TRIGGER AS $$
DECLARE
    existe BOOLEAN;
BEGIN
    CASE NEW.tipo_referencia
        WHEN 'reserva' THEN
            SELECT EXISTS(SELECT 1 FROM RESERVAS_HOSPEDAJE WHERE id_reserva = NEW.id_referencia) INTO existe;
        WHEN 'arriendo' THEN
            SELECT EXISTS(SELECT 1 FROM CONTRATOS_ARRIENDO WHERE id_contrato = NEW.id_referencia) INTO existe;
        WHEN 'venta' THEN
            SELECT EXISTS(SELECT 1 FROM PROCESO_VENTA WHERE id_venta = NEW.id_referencia) INTO existe;
        ELSE
            RAISE EXCEPTION 'tipo_referencia % no es válido en PAGOS', NEW.tipo_referencia;
    END CASE;

    IF NOT existe THEN
        RAISE EXCEPTION 'id_referencia % no existe en la tabla correspondiente a tipo_referencia=%',
            NEW.id_referencia, NEW.tipo_referencia;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validar_referencia_pagos
BEFORE INSERT OR UPDATE ON PAGOS
FOR EACH ROW
EXECUTE FUNCTION fn_validar_referencia_pagos();


-- =========================================================
-- 3. RESEÑAS
--    tipo_referencia: 'reserva' -> RESERVAS_HOSPEDAJE
--                     'arriendo' -> CONTRATOS_ARRIENDO
-- =========================================================
CREATE OR REPLACE FUNCTION fn_validar_referencia_resenas()
RETURNS TRIGGER AS $$
DECLARE
    existe BOOLEAN;
BEGIN
    CASE NEW.tipo_referencia
        WHEN 'reserva' THEN
            SELECT EXISTS(SELECT 1 FROM RESERVAS_HOSPEDAJE WHERE id_reserva = NEW.id_referencia) INTO existe;
        WHEN 'arriendo' THEN
            SELECT EXISTS(SELECT 1 FROM CONTRATOS_ARRIENDO WHERE id_contrato = NEW.id_referencia) INTO existe;
        ELSE
            RAISE EXCEPTION 'tipo_referencia % no es válido en RESEÑAS', NEW.tipo_referencia;
    END CASE;

    IF NOT existe THEN
        RAISE EXCEPTION 'id_referencia % no existe en la tabla correspondiente a tipo_referencia=%',
            NEW.id_referencia, NEW.tipo_referencia;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validar_referencia_resenas
BEFORE INSERT OR UPDATE ON RESEÑAS
FOR EACH ROW
EXECUTE FUNCTION fn_validar_referencia_resenas();

-- ===============================================================
-- CONFIRMANDO QUE ESTA MONDA SI VALE :'(
-- ===============================================================

-- LAS TABLAS

SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- LOS TRIGGERS
SELECT trigger_name, event_object_table 
FROM information_schema.triggers 
ORDER BY event_object_table;

-- PROBANDO LOS TRIGGERS
INSERT INTO PAGOS (id_referencia, tipo_referencia, monto, estado)
VALUES (99999, 'venta', 100.00, 'pendiente');

INSERT INTO USUARIOS (nombre, email, password_hash, rol, verificado)
VALUES ('Prueba Romeo', 'romeo@test.com', 'hash123', 'host', true);

SELECT * FROM USUARIOS;