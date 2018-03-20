create table Cash (
    CashId              integer not null,
    DateCollected       date not null,
    DateDeposited       date not null,
    CauseId             integer not null,
    CashDenominationId  integer not null,
    Quantity            smallint not null,
    constraint Cash_pk primary key (CashId),
    constraint Cash_uk_1 unique
            (DateCollected, DateDeposited, CauseId, CashDenominationId),
    constraint Cash_fk_1 foreign key (CauseId) references Causes,
    constraint Cash_fk_2 foreign key (CashDenominationId)
            references CashDenominations
);

grant select on Cash to public;

insert into Cash
select
    min(cc.CollectionCashId),
    ct.DateCollected,
    dp.DateDeposited,
    cc.CauseId,
    cc.CashDenominationId,
    sum(cc.Quantity)
from
    CollectionCash cc
    join Collections ct
        on ct.CollectionId = cc.CollectionId
    join Deposits dp
        on dp.DepositId = ct.DepositId
group by
    ct.DateCollected,
    dp.DateDeposited,
    cc.CauseId,
    cc.CashDenominationId
having sum(cc.Quantity) != 0;

drop table CollectionCash;

alter sequence CollectionCashId_s rename to CashId_s;

drop sequence CollectionCashId_s;

drop table CollectionCauses;

drop table Collections;

drop sequence CollectionId_s;

drop table Deposits;

drop sequence DepositId_s;

