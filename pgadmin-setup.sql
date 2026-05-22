-- pgAdmin: opret database første gang (hvis du IKKE bruger Docker init)
-- Kør på server "PostgreSQL 16" som bruger postgres

CREATE DATABASE "QR"
    WITH ENCODING 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TEMPLATE template0;

-- Derefter: højreklik database QR → Query Tool → åbn og kør schema.sql, derefter seed.sql
