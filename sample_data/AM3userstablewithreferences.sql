DROP TABLE IF EXISTS public.users;
CREATE TABLE users (
    user_id serial NOT NULL,
    user_name text,
    password text,
    registration_date timestamp without time zone,
    reputation integer
);

ALTER TABLE ONLY users
    ADD CONSTRAINT pk_users PRIMARY KEY (user_id);

ALTER TABLE question
    ADD COLUMN IF NOT EXISTS user_id INTEGER ;

ALTER TABLE ONLY question
    ADD CONSTRAINT fk_user_id foreign key (user_id) REFERENCES users(user_id);

ALTER TABLE answer
    ADD COLUMN IF NOT EXISTS user_id INTEGER ;

ALTER TABLE ONLY answer
    ADD CONSTRAINT fk_user_id foreign key (user_id) REFERENCES users(user_id);

ALTER TABLE comment
    ADD COLUMN IF NOT EXISTS user_id INTEGER ;

ALTER TABLE ONLY comment
    ADD CONSTRAINT fk_user_id foreign key (user_id) REFERENCES users(user_id);

ALTER TABLE answer
    ADD COLUMN IF NOT EXISTS accepted bool;