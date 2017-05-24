create database price_alarm_bot;

create user 'tele'@'localhost' identified by 'xpffp';
grant all privileges on price_alarm_bot.* to tele@'localhost';

use price_alarm_bot;

create table item(
    id int not null auto_increment,
    chat_id varchar(100) not null,
    name varchar(100) not null,
    code varchar(100) not null,
    price int not null,
    kind boolean not null,
    primary key(id)
);
