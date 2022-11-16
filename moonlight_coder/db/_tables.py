USERS = """CREATE TABLE users(
    username text NOT NULL PRIMARY KEY, 
    email text NOT NULL,
    first_name text NOT NULL, 
    last_name text NOT NULL
    );"""

ANSWERS = """CREATE TABLE answers(
    username text, 
    uuid text NOT NULL, 
    ignore int DEFAULT 0 NOT NULL,
    num_correct int DEFAULT 0 NOT NULL, 
    num_incorrect int DEFAULT 0 NOT NULL, 
    streak int DEFAULT 0 NOT NULL,
    PRIMARY KEY(username, uuid),
    FOREIGN KEY(username) REFERENCES users(username)
    );"""

TABLE_DEFS = [USERS, ANSWERS]
