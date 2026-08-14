-- ==============================================================================
--  Script de creación de esquema MySQL para inventario de equipos informáticos
-- ==============================================================================
--
--  Base de datos: computers_inventory (o el nombre definido en MYSQL_DATABASE)
--  Motor: InnoDB
--  Charset: utf8mb4
--  Collation: utf8mb4_general_ci
--
--  Tablas:
--    1. computers    → Información general del equipo (clave primaria: machine_mac)
--    2. dimm_ram     → Módulos de memoria RAM por equipo (relación 1:N)
--
--  Uso:
--    mysql -u root -p < schema.sql
--    -- o desde un cliente MySQL:
--    SOURCE /ruta/al/archivo/schema.sql;
--
-- ==============================================================================

-- -----------------------------------------------------------------------------
--  1. Crear la base de datos (si no existe) y seleccionarla
-- -----------------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS computers_inventory
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_general_ci;

USE computers_inventory;

-- -----------------------------------------------------------------------------
--  2. Tabla principal: computers
-- -----------------------------------------------------------------------------
--  Almacena la información general de cada equipo informático.
--  La dirección MAC (machine_mac) actúa como identificador único.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS computers (
    -- Identificador primario: dirección MAC del adaptador de red
    machine_mac             VARCHAR(17)     NOT NULL,

    -- Información básica del equipo y usuario
    device_name             VARCHAR(100)    NOT NULL        COMMENT 'Nombre del equipo en la red',
    user_name               VARCHAR(100)    NOT NULL        COMMENT 'Usuario asignado al equipo',

    -- Información de red
    machine_ip              VARCHAR(45)                     COMMENT 'Dirección IP actual (IPv4 o IPv6)',

    -- Hardware: placa madre
    mobo_mark               VARCHAR(100)                    COMMENT 'Marca de la placa madre (ej: ASUS, Gigabyte)',
    mobo_model              VARCHAR(100)                    COMMENT 'Modelo de la placa madre',

    -- Hardware: procesador
    cpu_info                VARCHAR(200)                    COMMENT 'Información del procesador (marca, modelo, frecuencia)',

    -- Sistema operativo
    operative_system        VARCHAR(100)                    COMMENT 'Sistema operativo instalado (ej: Windows 11 Pro)',

    -- Hardware: almacenamiento principal
    storage_model           VARCHAR(100)                    COMMENT 'Modelo del disco de almacenamiento principal',
    storage_cap             BIGINT                          COMMENT 'Capacidad del almacenamiento en bytes',

    -- Acceso remoto
    anydesk_id              BIGINT                          COMMENT 'Identificador de AnyDesk para acceso remoto',

    -- Auditoría de timestamps (gestionados automáticamente por MySQL)
    updated_at              TIMESTAMP       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                                                            COMMENT 'Fecha de última actualización del registro',
    created_at              TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
                                                            COMMENT 'Fecha de creación del registro',

    -- Restricciones
    PRIMARY KEY (machine_mac)

) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_general_ci
  COMMENT='Registro maestro de equipos informáticos del inventario';

-- -----------------------------------------------------------------------------
--  3. Tabla secundaria: dimm_ram
-- -----------------------------------------------------------------------------
--  Almacena los módulos de memoria RAM instalados en cada equipo.
--  Relación 1:N con la tabla computers (machine_mac es clave foránea).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dimm_ram (
    -- Clave primaria autoincremental
    id                      INT             AUTO_INCREMENT  COMMENT 'ID autoincremental del módulo RAM',

    -- Clave foránea: vincula el módulo con el equipo
    machine_mac             VARCHAR(17)     NOT NULL        COMMENT 'MAC del equipo al que pertenece el módulo (FK → computers)',

    -- Identificadores físicos del módulo
    caption                 VARCHAR(100)                    COMMENT 'Descripción del dispositivo (ej: Physical Memory)',
    manufacturer            VARCHAR(100)                    COMMENT 'Fabricante del módulo (ej: Corsair, G.Skill)',
    part_number             VARCHAR(100)                    COMMENT 'Número de parte del fabricante',
    model                   VARCHAR(100)                    COMMENT 'Modelo comercial del módulo',
    tag                     VARCHAR(100)                    COMMENT 'Etiqueta interna del sistema (ej: Physical Memory 0)',
    bank_label              VARCHAR(50)                     COMMENT 'Etiqueta del banco de memoria (ej: BANK 0)',
    device_locator          VARCHAR(50)                     COMMENT 'Ubicación física en la placa (ej: DIMM_A1, DIMM_B2)',

    -- Especificaciones técnicas
    capacity                BIGINT          DEFAULT 0       COMMENT 'Capacidad en bytes (ej: 8589934592 = 8 GB)',
    speed                   INT             DEFAULT 0       COMMENT 'Velocidad nominal del módulo en MHz',
    configured_clock_speed  INT             DEFAULT 0       COMMENT 'Velocidad de reloj configurada por BIOS/UEFI en MHz',
    configured_voltage      INT             DEFAULT 0       COMMENT 'Voltaje operativo configurado en mV (ej: 1350 = 1.35V)',

    -- Restricciones
    PRIMARY KEY (id),

    FOREIGN KEY (machine_mac)
        REFERENCES computers(machine_mac)
        ON DELETE CASCADE
        ON UPDATE CASCADE

) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_general_ci
  COMMENT='Módulos de memoria RAM instalados en cada equipo';

-- -----------------------------------------------------------------------------
--  4. Índices adicionales
-- -----------------------------------------------------------------------------
--  Índice para acelerar búsquedas de RAM por MAC del equipo.
-- -----------------------------------------------------------------------------
CREATE INDEX idx_dimm_mac ON dimm_ram(machine_mac);

-- -----------------------------------------------------------------------------
--  5. (Opcional) Datos de ejemplo / seed
-- -----------------------------------------------------------------------------
--  Descomenta las siguientes líneas si deseas insertar un registro de prueba.
-- -----------------------------------------------------------------------------
--
-- INSERT INTO computers (
--     machine_mac, device_name, user_name, machine_ip,
--     mobo_mark, mobo_model, cpu_info, operative_system,
--     storage_model, storage_cap, anydesk_id
-- ) VALUES (
--     '00:1A:2B:3C:4D:5E',
--     'PC-OFICINA-01',
--     'juan.perez',
--     '192.168.1.25',
--     'ASUS',
--     'PRIME B450M',
--     'AMD Ryzen 5 3600 @ 3.60GHz',
--     'Windows 11 Pro',
--     'Samsung 870 EVO',
--     500107862016,
--     123456789
-- );
--
-- INSERT INTO dimm_ram (
--     machine_mac, caption, manufacturer, part_number, model,
--     tag, bank_label, device_locator, capacity, speed,
--     configured_clock_speed, configured_voltage
-- ) VALUES (
--     '00:1A:2B:3C:4D:5E',
--     'Physical Memory',
--     'Corsair',
--     'CMK16GX4M2B3200C16',
--     'Vengeance LPX',
--     'Physical Memory 0',
--     'BANK 0',
--     'DIMM_A1',
--     8589934592,
--     3200,
--     3200,
--     1350
-- );
