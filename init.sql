CREATE TABLE IF NOT EXISTS public.users
(
    u_id character varying COLLATE pg_catalog."default" NOT NULL,
    u_username character varying COLLATE pg_catalog."default",
    u_password character varying COLLATE pg_catalog."default",
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone NOT NULL DEFAULT now(),
    created_by character varying COLLATE pg_catalog."default",
    updated_by character varying COLLATE pg_catalog."default",
    CONSTRAINT users_pkey PRIMARY KEY (u_id),
    CONSTRAINT users_u_username_key UNIQUE (u_username)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.users
    OWNER to postgres;
-- Index: idx_users_uid

-- DROP INDEX IF EXISTS public.idx_users_uid;

CREATE INDEX IF NOT EXISTS idx_users_uid
    ON public.users USING btree
    (u_id COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: idx_users_username

-- DROP INDEX IF EXISTS public.idx_users_username;

CREATE INDEX IF NOT EXISTS idx_users_username
    ON public.users USING btree
    (u_username COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;

INSERT INTO users (u_id, u_username, u_password)
SELECT 
    'uid_' || g AS u_id,
    'user_' || g AS u_username,
    md5(random()::text) AS u_password
FROM generate_series(1, 1000) AS g;
