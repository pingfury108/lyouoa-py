-- Add migration script here
CREATE TABLE IF NOT EXISTS orders
(
    id                  TEXT        PRIMARY KEY NOT NULL,
    hotel_id            INTEGER     NOT NULL,
    hotel_name          TEXT        NOT NULL,
    customer_id         INTEGER     NOT NULL,
    group_id            TEXT        NOT NULL,
    group_name          TEXT        NOT NULL,
    room_type           TEXT        NOT NULL,
    check_in_time       DATETIME    NOT NULL,
    leave_time          DATETIME    NOT NULL,
    days                INTEGER     NOT NULL,
    unit_price          INTEGER     NOT NULL,
    room_number         INTEGER     NOT NULL,
    free_room_number    INTEGER     NOT NULL,
    lump_sum            INTEGER     NOT NULL,
    ower                TEXT        NOT NULL,
    opt_time            DATETIME    DEFAULT NULL,
    review              TEXT        DEFAULT NULL
);
