alter table Cash drop constraint Cash_fk_2;

drop table CashDenominations;

create table CashDenominations (
    CashDenominationId integer not null,
    Value money not null,
    Description character varying(60) not null,
    QuantityMultiple integer not null,
    constraint CashDenominations_pk primary key (CashDenominationId)
);

insert into CashDenominations values (1, '$0.01', 'roll(s) of pennies', 50);
insert into CashDenominations values (2, '$0.05', 'roll(s) of nickels', 40);
insert into CashDenominations values (3, '$0.10', 'roll(s) of dimes', 50);
insert into CashDenominations values (4, '$0.25', 'roll(s) of quarters', 40);
insert into CashDenominations values (5, '$1.00', 'roll(s) of $1 coins', 25);
insert into CashDenominations values (6, '$2.00', 'roll(s) of $2 coins', 25);
insert into CashDenominations values (7, '$5.00', '$5 bill(s)', 1);
insert into CashDenominations values (8, '$10.00', '$10 bill(s)', 1);
insert into CashDenominations values (9, '$20.00', '$20 bill(s)', 1);
insert into CashDenominations values (10, '$50.00', '$50 bill(s)', 1);
insert into CashDenominations values (11, '$100.00', '$100 bill(s)', 1);

alter table Cash add constraint Cash_fk_2
foreign key (CashDenominationId) references CashDenominations;

