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
