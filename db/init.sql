CREATE USER ${DB_REPL_USER} WITH REPLICATION ENCRYPTED PASSWORD '${DB_REPL_PASSWORD}';
SELECT pg_create_physical_replication_slot('replication_slot');

CREATE DATABASE db;

\connect db

CREATE TABLE phone_numbers(
  id SERIAL PRIMARY KEY,
  phone_number VARCHAR(100) NOT NULL
);
CREATE TABLE emails(
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL
);

INSERT INTO emails (email) VALUES ('test@test.com'), ('testst@mail.ru');
INSERT INTO phone_numbers (phone_number) VALUES ('89617291234'), ('+7-913-666-31-55');


