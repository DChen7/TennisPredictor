drop table if exists players;
create table players (
	"name" text primary key not null,
	"height" real not null,
	"weight" real not null,
	"left_handed" integer not null,
	"age" integer not null
);