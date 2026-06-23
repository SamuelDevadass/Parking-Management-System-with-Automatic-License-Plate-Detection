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
