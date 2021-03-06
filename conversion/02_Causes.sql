alter table CollectionCauses
add Year integer;

update CollectionCauses cc set
    Year =
        ( select date_part('year', DateCollected)
          from Collections
          where CollectionId = cc.CollectionId
        );

alter table CollectionCauses
alter column Year set not null;

insert into CausesForYear
select distinct
    CauseId,
    Year,
    false
from CollectionCauses cc
where not exists
    ( select 1
      from CausesForYear
      where CauseId = cc.CauseId
        and Year = cc.Year
    );

alter table CausesForYear drop constraint CausesForYear_fk_1;

alter table CollectionCauses drop constraint CollectionCauses_fk_2;

alter table Causes drop constraint Causes_pk;

alter table Causes rename to Causes_backup;

create table CauseXref as
select
    CauseId as OldCauseId,
    Year,
    nextval('CauseId_s') as NewCauseId
from CausesForYear;

create table Causes (
    CauseId                     integer not null,
    Year                        integer not null,
    Description                 character varying(60) not null,
    Deductible                  boolean not null,
    Reported                    boolean not null,
    DonationAccountCode         character varying(10),
    LooseCashAccountCode        character varying(10),
    Notes                       character varying(250),
    constraint Causes_pk primary key (CauseId),
    constraint Causes_fk_1 foreign key (Year) references Years
);

insert into Causes
select
    x.NewCauseId,
    cy.Year,
    c.Description,
    cy.Deductible,
    c.IsReported,
    null
from
    Causes_backup c
    join CausesForYear cy
        on cy.CauseId = c.CauseId
    join CauseXref x
        on x.OldCauseId = cy.CauseId
        and x.Year = cy.Year;

alter table CollectionCash drop constraint CollectionCash_fk_1;

alter table Donations drop constraint Donations_fk_1;

update CollectionCauses cc set
    CauseId =
        ( select NewCauseId
          from CauseXref
          where OldCauseId = cc.CauseId
            and Year = cc.Year
        );

alter table CollectionCauses
add constraint CollectionCauses_fk_2
foreign key (CauseId)
references Causes;

alter table CollectionCauses
drop column Year;

update CollectionCash cc set
    CauseId =
        ( select NewCauseId
          from CauseXref
          where OldCauseId = cc.CauseId
            and Year =
                ( select date_part('year', DateCollected)
                  from Collections
                  where CollectionId = cc.CollectionId
                )
        );

alter table CollectionCash
add constraint CollectionCash_fk_1
foreign key (CollectionId, CauseId)
references CollectionCauses;

update Donations d set
    CauseId =
        ( select NewCauseId
          from CauseXref
          where OldCauseId = d.CauseId
            and Year =
                ( select date_part('year', DateCollected)
                  from Collections
                  where CollectionId = d.CollectionId
                )
        );

alter table Donations
add constraint Donations_fk_1
foreign key (CollectionId, CauseId)
references CollectionCauses;

drop table CausesForYear;

drop table CauseXref;

drop table Causes_backup;

