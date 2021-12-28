---- MAIN CODE

if not exists(select * from sys.databases where name='budgets')
    create database budgets
GO

use budgets
GO


-- DOWN 

if exists(select * from INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
    where CONSTRAINT_NAME='fk_expenses_exp_user_id')
    alter table expenses drop constraint fk_expenses_exp_user_id

if exists(select * from INFORMATION_SCHEMA.TABLE_CONSTRAINTS
    where CONSTRAINT_NAME='fk_expenses_exp_merchant_id')
    alter table expenses drop constraint fk_expenses_exp_merchant_id

if exists(select * from INFORMATION_SCHEMA.TABLE_CONSTRAINTS
    where CONSTRAINT_NAME='fk_total_expenses_merchant_id')
    alter table total_expenses drop constraint fk_total_expenses_merchant_id

if exists(select * from INFORMATION_SCHEMA.TABLE_CONSTRAINTS
    where CONSTRAINT_NAME='fk_expenses_exp_category_id')
    alter table expenses drop constraint fk_expenses_exp_category_id

drop table if exists expenses

drop table if exists users

drop table if exists merchants 

drop table if exists total_expenses

drop table if exists categories 

drop view if exists v_item_wise_expenditure

drop view if exists v_person_wise_expenditure

GO
-- UP Metadata

create table expenses (
    exp_id int identity not null,
    exp_user_id int not null,
    exp_item_name VARCHAR(50) not null,
    exp_item_price money not null,
    exp_merchant_id int not null,
    exp_merchant_name VARCHAR(50) not NULL,
    exp_purchase_date DATE NOT NULL,
    exp_purchase_time Time NOT NULL,
    exp_category_id int not null,
    exp_description VARCHAR(50),
    CONSTRAINT pk_expenses_exp_id primary key(exp_id)
)


CREATE TABLE users (
    user_id int identity not null,
    user_firstname varchar(50) not null,
    user_lastname varchar(50) not null,
    constraint pk_users_user_id primary key (user_id)
)

alter table expenses 
    add constraint fk_expenses_exp_user_id foreign key (exp_user_id)
        references users(user_id)


CREATE table merchants (
    merchant_id int identity not null,
    merchant_name varchar(50) not null,
    merchant_address varchar(50),
    merchant_number varchar(50),
    constraint pk_merchants_merchant_id primary key (merchant_id)
)

alter table expenses 
    add constraint fk_expenses_exp_merchant_id foreign key (exp_merchant_id)
        references merchants(merchant_id)

create table total_expenses (
    sr_no int identity not null,
    merchant_id int not null,
    tax money not null,
    total_amt money not NULL,
    purchase_date date not null,
    purchase_time time not null,
    constraint pk_total_expenses_sr_no primary key (sr_no)
)

alter table total_expenses 
    add constraint fk_total_expenses_merchant_id foreign key (merchant_id)
        references merchants(merchant_id)



CREATE TABLE categories (
    category_id int identity not null,
    category_name varchar(50) not NULL,
    constraint pk_categories_category_id primary key (category_id)
)

alter table expenses 
    add constraint fk_expenses_exp_category_id FOREIGN key (exp_category_id)
        references categories(category_id)
GO

CREATE VIEW v_item_wise_expenditure AS
    with pivot_source as (
        select exp_item_name, sum(exp_item_price) as total , count(exp_item_name) as item_count from expenses
        group by exp_item_name
    )
    select distinct(C.exp_item_name), C.item_count, C. total , category_name from pivot_source C join  expenses A on C.exp_item_name=A.exp_item_name
    join categories B on 
        A.exp_category_id=B.category_id 

GO

CREATE VIEW v_person_wise_expenditure AS
    with pivot_source as (
        select exp_user_id, sum(exp_item_price) as total from expenses
        group by exp_user_id
    )
    select distinct(A.exp_user_id), A. total , 
    (user_firstname + ' ' + user_lastname) as user_name from 
    pivot_source A join  users B 
    on A.exp_user_id=B.user_id


GO


-- UP Data
-- insert into state_lookup (state_code) values
--     ('NY'),('NJ'),('CT')
-- Inserted using python script
INSERT INTO users (user_firstname, user_lastname) VALUES ('Trishla', 'Jain');
INSERT INTO users (user_firstname, user_lastname) VALUES ('Nivedita', 'Ravi'),('Mikhail', 'Pinto');

INSERT INTO categories (category_name) values ('Food'), ('Fun'), ('Rent'), ('Personal')
-- Verify
select * from expenses 
select * from users
select * from merchants
select * from total_expenses
select * from categories
select * from v_item_wise_expenditure
select * from v_person_wise_expenditure