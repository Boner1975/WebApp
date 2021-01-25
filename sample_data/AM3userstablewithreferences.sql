DROP TABLE IF EXISTS public.users;
CREATE TABLE users (
    user_id serial NOT NULL,
    user_name text,
    registration_date timestamp without time zone,
    count_of_asked_questions integer,
    count_of_answers integer,
    count_of_comments integer,
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