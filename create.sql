CREATE TABLE sport2(
    id SMALLINT NOT NULL,
    sport VARCHAR(25) UNIQUE NOT NULL,
    parent SMALLINT,
    PRIMARY KEY(id),
    FOREIGN KEY(parent) REFERENCES sport2(id)
);

CREATE TABLE klass2(
    id SMALLINT NOT NULL,
    klass VARCHAR(25) UNIQUE NOT NULL,
    sport SMALLINT NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(sport) REFERENCES sport2(id)
);

CREATE TABLE title2(
    id SMALLINT NOT NULL,
    title VARCHAR(25) UNIQUE NOT NULL,
    name VARCHAR(50) UNIQUE NOT NULL,
    sport SMALLINT,
    klass SMALLINT,
    PRIMARY KEY(id),
    FOREIGN KEY(sport) REFERENCES sport2(id),
    FOREIGN KEY(klass) REFERENCES klass2(id)
);

CREATE TABLE dog2(
    id SMALLINT NOT NULL,
    kennel_name VARCHAR(50) UNIQUE NOT NULL,
    registration_number VARCHAR(25) UNIQUE NOT NULL,
    PRIMARY KEY(id)
);

CREATE TABLE competition_result2(
    id SMALLINT NOT NULL,
    klass SMALLINT NOT NULL,
    dog SMALLINT NOT NULL,
    date DATE NOT NULL,
    points DECIMAL(5, 2) NOT NULL,
    prize VARCHAR(25),
    PRIMARY KEY(id),
    FOREIGN KEY(klass) REFERENCES klass2(id),
    FOREIGN KEY(dog) REFERENCES dog2(id)
);

CREATE TABLE title_dog2(
    id SMALLINT NOT NULL,
    title SMALLINT NOT NULL,
    dog SMALLINT NOT NULL,
    date DATE NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(title) REFERENCES title2(id),
    FOREIGN KEY(dog) REFERENCES dog2(id)
);

CREATE TABLE exception2(
    id SMALLINT NOT NULL,
    exception TEXT NOT NULL,
    PRIMARY KEY(id)
);
