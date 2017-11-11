update Donations set DonatorId =
    ( select DonatorId
      from Donators
      where LastName = 'Anonymous'
    )
where DonatorId is null;

create table DonatorXref (
    OldDonatorId    integer not null,
    Year            integer not null,
    NewDonatorId    integer not null,
    constraint DonatorXref_pk primary key (OldDonatorId, Year),
    constraint DonatorXref_uk_1 unique (NewDonatorId)
);

insert into DonatorXref
select
    DonatorId,
    Year,
    nextval('DonatorId_s')
from
    ( select distinct
          DonatorId,
          ClaimYear as Year
      from Donations
    ) d;

insert into DonatorXref
select
    DonatorId,
    Year,
    nextval('DonatorId_s')
from
    ( select
          DonatorId,
          Year
      from DonatorsForYear dy
      where not exists
          ( select 1
            from DonatorXref
            where OldDonatorId = dy.DonatorId
              and Year = dy.Year
          )
    ) d;

insert into DonatorXref
select
    DonatorId,
    Year,
    nextval('DonatorId_s')
from
    ( select
          DonatorId,
          Year
      from TaxReceipts tr
      where not exists
          ( select 1
            from DonatorXref
            where OldDonatorId = tr.DonatorId
              and Year = tr.Year
          )
    ) tr;

alter table Donations drop constraint Donations_fk_3;

alter table DonatorsForYear drop constraint DonatorsForYear_fk_1;

alter table TaxReceipts drop constraint TaxReceipts_fk_2;

alter table SplitDonations drop constraint SplitDonations_fk_2;

alter table Donators drop constraint Donators_pk;

drop index Donators_uk_1;

alter table Donators rename to Donators_backup;

create table Donators (
    DonatorId       integer not null,
    Year            integer not null,
    Surname         character varying(30) not null,
    GivenNames      character varying(50),
    AssignedNumber  integer,
    Address         character varying(150),
    constraint Donators_pk primary key (DonatorId),
    constraint Donators_uk_1 unique (Year, Surname, GivenNames),
    constraint Donators_uk_2 unique (Year, AssignedNumber),
    constraint Donators_fk_1 foreign key (Year)
            references Years
);

insert into Donators
select
    x.NewDonatorId,
    x.Year,
    d.LastName,
    d.GivenNames,
    ( select AssignedNumber
      from DonatorsForYear
      where DonatorId = x.OldDonatorId
        and Year = x.Year
    ),
    d.Address
from
    DonatorXref x
    join Donators_backup d
        on d.DonatorId = x.OldDonatorId;

update Donations d set
    DonatorId =
        ( select NewDonatorId
          from DonatorXref
          where OldDonatorId = d.DonatorId
            and Year = d.ClaimYear
        );

alter table Donations
add constraint Donations_fk_3
foreign key (DonatorId)
references Donators;

update TaxReceipts tr set
    DonatorId = 
        ( select NewDonatorId
          from DonatorXref
          where OldDonatorId = tr.DonatorId
            and Year = tr.Year
        );

alter table TaxReceipts
add constraint TaxReceipts_fk_2
foreign key (DonatorId)
references Donators;

update SplitDonations sd set
    DonatorId = 
        ( select NewDonatorId
          from DonatorXref
          where OldDonatorId = sd.DonatorId
            and Year =
                ( select distinct ClaimYear
                  from Donations
                  where SplitDonationId = sd.SplitDonationId
                )
        );

alter table SplitDonations
add constraint SplitDonations_fk_2
foreign key (DonatorId)
references Donators;

drop table DonatorsForYear;

drop table DonatorXref;

drop table Donators_backup;

