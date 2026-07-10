-- Table: public.has_parking_spot

-- DROP TABLE IF EXISTS public.has_parking_spot;

CREATE TABLE IF NOT EXISTS public.has_parking_spot
(
    centre_id integer NOT NULL,
    wing text COLLATE pg_catalog."default" NOT NULL,
    floor text COLLATE pg_catalog."default" NOT NULL,
    spot_number text COLLATE pg_catalog."default" NOT NULL,
    size text COLLATE pg_catalog."default",
    availability boolean,
    CONSTRAINT has_parking_spot_pkey PRIMARY KEY (centre_id, wing, floor, spot_number),
    CONSTRAINT fk_floor FOREIGN KEY (centre_id, wing, floor)
        REFERENCES public.has_wing_floor (centre_id, wing, floor) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.has_parking_spot
    OWNER to postgres;

-------------------------------------------------------------------------------------------------------------------------------------------------

-- Table: public.has_wing_floor

-- DROP TABLE IF EXISTS public.has_wing_floor;

CREATE TABLE IF NOT EXISTS public.has_wing_floor
(
    centre_id integer NOT NULL,
    wing text COLLATE pg_catalog."default" NOT NULL,
    floor text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT has_wing_floor_pkey PRIMARY KEY (centre_id, wing, floor),
    CONSTRAINT fk_centre_id FOREIGN KEY (centre_id)
        REFERENCES public.owns_centre (centre_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.has_wing_floor
    OWNER to postgres;

-------------------------------------------------------------------------------------------------------------------------------------------------

-- Table: public.organization

-- DROP TABLE IF EXISTS public.organization;

CREATE TABLE IF NOT EXISTS public.organization
(
    org_id integer NOT NULL DEFAULT nextval('organization_org_id_seq'::regclass),
    name text COLLATE pg_catalog."default" NOT NULL,
    admin_name text COLLATE pg_catalog."default" NOT NULL,
    admin_phone character varying(20) COLLATE pg_catalog."default" NOT NULL,
    admin_email character varying(30) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT organization_pkey PRIMARY KEY (org_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.organization
    OWNER to postgres;

-------------------------------------------------------------------------------------------------------------------------------------------------

-- Table: public.owner

-- DROP TABLE IF EXISTS public.owner;

CREATE TABLE IF NOT EXISTS public.owner
(
    owner_id character varying(30) COLLATE pg_catalog."default" NOT NULL,
    name text COLLATE pg_catalog."default",
    CONSTRAINT owner_pkey PRIMARY KEY (owner_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.owner
    OWNER to postgres;

-------------------------------------------------------------------------------------------------------------------------------------------------

-- Table: public.owner_phone

-- DROP TABLE IF EXISTS public.owner_phone;

CREATE TABLE IF NOT EXISTS public.owner_phone
(
    owner_id character varying(30) COLLATE pg_catalog."default" NOT NULL,
    phone character varying(20) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT owner_phone_pkey PRIMARY KEY (owner_id, phone),
    CONSTRAINT fk_owner_id FOREIGN KEY (owner_id)
        REFERENCES public.owner (owner_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.owner_phone
    OWNER to postgres;

-------------------------------------------------------------------------------------------------------------------------------------------------

-- Table: public.owns_centre

-- DROP TABLE IF EXISTS public.owns_centre;

CREATE TABLE IF NOT EXISTS public.owns_centre
(
    org_id integer NOT NULL,
    centre_id integer NOT NULL DEFAULT nextval('owns_centre_centre_id_seq'::regclass),
    name text COLLATE pg_catalog."default" NOT NULL,
    address text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT owns_centre_pkey PRIMARY KEY (org_id, centre_id),
    CONSTRAINT unique_centre_id UNIQUE (centre_id),
    CONSTRAINT fk_org_id FOREIGN KEY (org_id)
        REFERENCES public.organization (org_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.owns_centre
    OWNER to postgres;

-------------------------------------------------------------------------------------------------------------------------------------------------

-- Table: public.owns_vehicle

-- DROP TABLE IF EXISTS public.owns_vehicle;

CREATE TABLE IF NOT EXISTS public.owns_vehicle
(
    owner_id character varying(30) COLLATE pg_catalog."default",
    license_number character varying(20) COLLATE pg_catalog."default" NOT NULL,
    model text COLLATE pg_catalog."default",
    colour text COLLATE pg_catalog."default",
    type text COLLATE pg_catalog."default",
    CONSTRAINT owns_vehicle_pkey PRIMARY KEY (license_number),
    CONSTRAINT fk_owner_id FOREIGN KEY (owner_id)
        REFERENCES public.owner (owner_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.owns_vehicle
    OWNER to postgres;

-------------------------------------------------------------------------------------------------------------------------------------------------

-- Table: public.parking_log

-- DROP TABLE IF EXISTS public.parking_log;

CREATE TABLE IF NOT EXISTS public.parking_log
(
    entry_time timestamp without time zone NOT NULL,
    license_number character varying(20) COLLATE pg_catalog."default" NOT NULL,
    exit_time timestamp without time zone,
    centre_id integer,
    wing text COLLATE pg_catalog."default" NOT NULL,
    floor text COLLATE pg_catalog."default" NOT NULL,
    spot_number text COLLATE pg_catalog."default",
    duration interval,
    amount numeric(10,2),
    image_folder_path text COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.parking_log
    OWNER to postgres;

-------------------------------------------------------------------------------------------------------------------------------------------------

-- Table: public.watchman_supervises

-- DROP TABLE IF EXISTS public.watchman_supervises;

CREATE TABLE IF NOT EXISTS public.watchman_supervises
(
    watchman_id integer NOT NULL DEFAULT nextval('watchman_supervises_watchman_id_seq'::regclass),
    name text COLLATE pg_catalog."default" NOT NULL,
    telephone character varying(20) COLLATE pg_catalog."default" NOT NULL,
    centre_id integer,
    wing text COLLATE pg_catalog."default" NOT NULL,
    floor text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT watchman_supervises_pkey PRIMARY KEY (watchman_id),
    CONSTRAINT fk_floor FOREIGN KEY (centre_id, wing, floor)
        REFERENCES public.has_wing_floor (centre_id, wing, floor) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.watchman_supervises
    OWNER to postgres;

-------------------------------------------------------------------------------------------------------------------------------------------------




