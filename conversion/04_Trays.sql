create sequence TrayId_s;

create table Trays (
    TrayId              integer not null,
    DateDeposited       date not null,
    DateCollected       date not null,
    CauseId             integer not null,
    constraint Trays_pk primary key (TrayId),
    constraint Trays_uk_1 unique (DateDeposited, DateCollected, CauseId),
    constraint Trays_fk_1 foreign key (CauseId) references Causes
);

create index Trays_ix_1 on Trays (DateCollected);

insert into Trays
select
    nextval('TrayId_s'),
    dp.DateDeposited,
    ct.DateCollected,
    cc.CauseId
from
    CollectionCauses cc
    join Collections ct
        on ct.CollectionId = cc.CollectionId
    join Deposits dp
        on dp.DepositId = ct.DepositId
where exists
    ( select 1
      from Donations
      where CollectionId = cc.CollectionId
        and CauseId = cc.CauseId
        and SplitDonationId is null
    ) or exists
    ( select 1
      from CollectionCash
      where CollectionId = cc.CollectionId
        and CauseId = cc.CauseId
    ) or exists
    ( select 1
      from Donations d
      where CollectionId = cc.CollectionId
        and CauseId = cc.CauseId
        and SplitDonationId is not null
        and not exists
          ( select 1
            from Donations
            where SplitDonationId = d.SplitDonationId
              and DonationId < d.DonationId
          )
    )
group by
    dp.DateDeposited,
    ct.DateCollected,
    cc.CauseId;

