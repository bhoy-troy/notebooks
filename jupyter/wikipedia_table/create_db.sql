DROP DATABASE IF EXISTS wikitable;
CREATE DATABASE wikitable;
CREATE USER IF NOT EXISTS 'nutty_professor'@'%' IDENTIFIED BY 'scientist';
GRANT ALL privileges ON `wikitable`.* TO 'nutty_professor'@'%';
FLUSH PRIVILEGES;

USE wikitable;

DROP TABLE IF EXISTS monarch;
CREATE TABLE IF NOT EXISTS monarch
(
    id    INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    CONSTRAINT monarch_unique UNIQUE (title)
);

DROP TABLE IF EXISTS party;
CREATE TABLE IF NOT EXISTS party
(
    id         INT AUTO_INCREMENT PRIMARY KEY,
    party_name VARCHAR(255) NOT NULL,
    CONSTRAINT party_unique UNIQUE (party_name)
);

DROP TABLE IF EXISTS prime_minister;
CREATE TABLE IF NOT EXISTS prime_minister
(
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(255) NOT NULL,
    alias      VARCHAR(255),
    title      VARCHAR(255),
    birth_date DATE         NOT NULL,
    death_date DATE,
    party_id   INT          NOT NULL,
    CONSTRAINT `fk_party_prime_minister`
        FOREIGN KEY (party_id) REFERENCES party (id)
            ON DELETE CASCADE
            ON UPDATE RESTRICT
);

DROP TABLE IF EXISTS prime_minister_term;
CREATE TABLE IF NOT EXISTS prime_minister_term
(
    id                INT AUTO_INCREMENT PRIMARY KEY,
    start_date        DATE    NOT NULL,
    end_date          DATE,
    prime_minister_id INT     NOT NULL,
    had_title         BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT `fk_prime_minister_term_prime_minister`
        FOREIGN KEY (prime_minister_id) REFERENCES prime_minister (id)


);

DROP TABLE IF EXISTS term_monarch;
CREATE TABLE IF NOT EXISTS term_monarch
(
    id         INT AUTO_INCREMENT PRIMARY KEY,
    term_id    INT,
    monarch_id INT

);
ALTER TABLE `term_monarch`
    ADD UNIQUE `unique_index` (`term_id`, `monarch_id`);