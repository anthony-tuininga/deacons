/* remove any split donations that aren't actually used */
delete from SplitDonations sd
where not exists
    ( select 1
      from Donations
      where SplitDonationId = sd.SplitDonationId
    );

alter table Donations drop constraint Donations_pk;

alter table Donations drop constraint Donations_fk_1;

alter table Donations drop constraint Donations_fk_2;

alter table Donations drop constraint Donations_fk_3;

alter table Donations drop constraint Donations_fk_4;

drop index Donations_ix_1;

alter table Donations rename to Donations_backup;

create table DonationXref (
    OldDonationId       integer,
    OldSplitDonationId  integer,
    NewDonationId       integer,
    constraint DonationXref_uk_1 unique (OldDonationId),
    constraint DonationXref_uk_2 unique (OldSplitDonationId),
    constraint DonationXref_uk_3 unique (NewDonationId)
);

insert into DonationXref
select
    DonationId,
    null,
    nextval('DonationId_s')
from Donations_backup
where SplitDonationId is null;

insert into DonationXref
select
    null,
    SplitDonationId,
    nextval('DonationId_s')
from SplitDonations;

create table Donations (
    DonationId          integer not null,
    CollectionId        integer not null,
    DonatorId           integer not null,
    Cash                boolean not null,
    constraint Donations_pk primary key (DonationId),
    constraint Donations_fk_1 foreign key (CollectionId)
            references Collections,
    constraint Donations_fk_2 foreign key (DonatorId)
            references Donators
);

create index Donations_ix_1 on Donations (CollectionId);

create index Donations_ix_2 on Donations (DonatorId);

grant select on Donations to public;

create table DonationComponents (
    DonationId          integer not null,
    CauseId             integer not null,
    Amount              money not null,
    constraint DonationComponents_pk primary key
            (DonationId, CauseId),
    constraint DonationComponents_fk_1 foreign key (DonationId)
            references Donations on delete cascade,
    constraint DonationComponents_fk_2 foreign key (CauseId)
            references Causes
);

create index DonationComponents_ix_1 on DonationComponents (CauseId);

grant select on DonationComponents to public;

insert into Donations
select
    x.NewDonationId,
    d.CollectionId,
    d.DonatorId,
    d.Cash
from
    DonationXref x
    join Donations_backup d
        on d.DonationId = x.OldDonationId;

insert into Donations
select distinct
    x.NewDonationId,
    d.CollectionId,
    d.DonatorId,
    d.Cash
from
    DonationXref x
    join Donations_backup d
        on d.SplitDonationId = x.OldSplitDonationId;

insert into DonationComponents
select
    x.NewDonationId,
    d.CauseId,
    sum(d.Amount)
from
    DonationXref x
    join Donations_backup d
        on d.DonationId = x.OldDonationId
        or d.SplitDonationId = x.OldSplitDonationId
group by x.NewDonationId, d.CauseId;

create or replace view CollectionAmounts as
select
    cc.CollectionId,
    cc.CauseId,
    ( select coalesce(sum(dc.Amount), 0::money)
      from
          Donations d
          join DonationComponents dc
              on dc.DonationId = d.DonationId
              and dc.CauseId = cc.CauseId
      where d.CollectionId = cc.CollectionId
        and d.Cash = false
    ) as ChequeAmount,
    ( select coalesce(sum(dc.Amount), 0::money)
      from
          Donations d
          join DonationComponents dc
              on dc.DonationId = d.DonationId
              and dc.CauseId = cc.CauseId
      where d.CollectionId = cc.CollectionId
        and d.Cash = true
    ) as EnvelopeCash,
    ( select coalesce(sum(cd.Value * ccs.Quantity), 0::money)
      from
          CollectionCash ccs
          join CashDenominations cd
              on cd.CashDenominationId = ccs.CashDenominationId
      where ccs.CollectionId = cc.CollectionId
        and ccs.CauseId = cc.CauseId
    ) as CashAmount
from CollectionCauses cc;

drop table SplitDonations;

drop table DonationXref;

drop table Donations_backup;

