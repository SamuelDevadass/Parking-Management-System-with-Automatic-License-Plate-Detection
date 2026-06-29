-- Table: public.organizations

-- DROP TABLE IF EXISTS public.organizations;

CREATE TABLE IF NOT EXISTS public.organizations
(
    org_id integer NOT NULL DEFAULT nextval('organizations_org_id_seq'::regclass),
    name text COLLATE pg_catalog."default" NOT NULL,
    admin_email text COLLATE pg_catalog."default",
    admin_phone character varying(20) COLLATE pg_catalog."default",
    CONSTRAINT organizations_pkey PRIMARY KEY (org_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.organizations
    OWNER to postgres;

-----------------------------------------------------------------------------------------------------------------------------------------------------

-- Table: public.parking_inventory

-- DROP TABLE IF EXISTS public.parking_inventory;

CREATE TABLE IF NOT EXISTS public.parking_inventory
(
    org_id integer NOT NULL DEFAULT nextval('parking_inventory_org_id_seq'::regclass),
    centre text COLLATE pg_catalog."default" NOT NULL,
    wing text COLLATE pg_catalog."default" NOT NULL,
    floor text COLLATE pg_catalog."default" NOT NULL,
    spot text COLLATE pg_catalog."default" NOT NULL,
    size text COLLATE pg_catalog."default",
    is_available boolean,
    CONSTRAINT parking_inventory_pkey PRIMARY KEY (org_id, centre, wing, floor, spot),
    CONSTRAINT fk_organization FOREIGN KEY (org_id)
        REFERENCES public.organizations (org_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.parking_inventory
    OWNER to postgres;

-----------------------------------------------------------------------------------------------------------------------------------------------------

    -- Table: public.parking_log

-- DROP TABLE IF EXISTS public.parking_log;

CREATE TABLE IF NOT EXISTS public.parking_log
(
    entry_time timestamp without time zone NOT NULL,
    license_number character varying(20) COLLATE pg_catalog."default" NOT NULL,
    exit_time timestamp without time zone,
    org_id integer NOT NULL DEFAULT nextval('parking_log_org_id_seq'::regclass),
    centre text COLLATE pg_catalog."default",
    wing text COLLATE pg_catalog."default",
    floor text COLLATE pg_catalog."default",
    spot text COLLATE pg_catalog."default",
    duration interval,
    amount numeric(10,2),
    owner_phone character varying(20) COLLATE pg_catalog."default",
    image_path text COLLATE pg_catalog."default",
    CONSTRAINT parking_log_pkey PRIMARY KEY (entry_time, license_number),
    CONSTRAINT fk_unique_spot FOREIGN KEY (org_id, centre, wing, floor, spot)
        REFERENCES public.parking_inventory (org_id, centre, wing, floor, spot) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.parking_log
    OWNER to postgres;


-----------------------------------------------------------------------------------------------------------------------------------------------------