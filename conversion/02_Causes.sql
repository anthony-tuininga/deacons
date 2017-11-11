alter table Cheques
add Year integer;

update Cheques cq set
    Year =
        ( select max(date_part('year', d.DateDeposited))
          from
              ChequeAmounts cqa
              join Collections c
                  on c.CollectionId = cqa.CollectionId
              join Deposits d
                  on d.DepositId = c.DepositId
          where cqa.ChequeId = cq.ChequeId
        );

alter table Cheques
alter column Year set not null;

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
from Cheques cq
where not exists
    ( select 1
      from CausesForYear
      where CauseId = cq.CauseId
        and Year = cq.Year
    );

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

alter table Cheques drop constraint Cheques_fk_1;

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

update Cheques cq set
    CauseId =
        ( select NewCauseId
          from CauseXref
          where OldCauseId = cq.CauseId
             and Year = cq.Year
        );

alter table Cheques
add constraint Cheques_fk_1
foreign key (CauseId)
references Causes;

alter table Cheques
drop column Year;

alter table ChequeAmounts drop constraint ChequeAmounts_fk_2;

alter table CollectionCash drop constraint CollectionCash_fk_1;

alter table Donations drop constraint Donations_fk_1;

alter table UnremittedAmounts drop constraint UnremittedAmounts_fk_1;

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

update ChequeAmounts ca set
    CauseId =
        ( select NewCauseId
          from CauseXref
          where OldCauseId = ca.CauseId
            and Year =
                ( select date_part('year', DateCollected)
                  from Collections
                  where CollectionId = ca.CollectionId
                )
        );

alter table ChequeAmounts
add constraint ChequeAmounts_fk_2
foreign key (CollectionId, CauseId)
references CollectionCauses;

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

update UnremittedAmounts ua set
    CauseId =
        ( select NewCauseId
          from CauseXref
          where OldCauseId = ua.CauseId
            and Year =
                ( select date_part('year', DateCollected)
                  from Collections
                  where CollectionId = ua.CollectionId
                )
        );

alter table UnremittedAmounts
add constraint UnremittedAmounts_fk_1
foreign key (CollectionId, CauseId)
references CollectionCauses;

drop table CausesForYear;

drop table CauseXref;

drop table Causes_backup;

