create view Donations_v as
select
    c.Year,
    t.TrayId,
    t.DateDeposited,
    t.DateCollected,
    d.DonationId,
    d.Cash,
    dc.CauseId,
    d.DonatorId,
    dc.Amount
from
    Donations d
    join Trays t
        on t.TrayId = d.TrayId
    join DonationComponents dc
        on dc.DonationId = d.DonationId
    join Causes c
        on c.CauseId = dc.CauseId;

create view Trays_v as
select
    c.Year,
    t.TrayId,
    t.DateDeposited,
    t.DateCollected,
    t.CauseId,
    ( select coalesce(sum(dc.Amount), '$0')
      from
          Donations d
          join DonationComponents dc
              on dc.DonationId = d.DonationId
      where d.TrayId = t.TrayId
        and d.Cash = 'f'
    ) as ChequeAmount,
    ( select coalesce(sum(cs.Quantity * cd.Value), '$0')
      from
          Cash cs
          join CashDenominations cd
              on cd.CashDenominationId = cs.CashDenominationId
      where cs.TrayId = t.TrayId
    ) as CashAmount,
    ( select coalesce(sum(dc.Amount), '$0')
      from
          Donations d
          join DonationComponents dc
              on dc.DonationId = d.DonationId
      where d.TrayId = t.TrayId
        and d.Cash = 't'
    ) as CashDonationAmount
from
    Trays t
    join Causes c
        on c.CauseId = t.CauseId;

create view DonationSummary as
select
    dr.Year,
    t.DateCollected,
    t.DateDeposited,
    dc.CauseId,
    sum(case when cash = 'f' then dc.Amount else '$0' end) as ChequeAmount,
    sum(case when cash = 't' then dc.Amount else '$0' end) as CashAmount
from
    Donations d
    join Trays t
        on t.TrayId = d.TrayId
    join DonationComponents dc
        on dc.DonationId = d.DonationId
    join Donators dr
        on dr.DonatorId = d.DonatorId
group by
    dr.Year,
    t.DateCollected,
    t.DateDeposited,
    dc.CauseId;

create view CashSummary as
select
    c.Year,
    t.DateCollected,
    t.DateDeposited,
    t.CauseId,
    sum(cs.Quantity * cd.Value) as Amount
from
    Cash cs
    join Trays t
        on t.TrayId = cs.TrayId
    join Causes c
        on c.CauseId = t.CauseId
    join CashDenominations cd
        on cd.CashDenominationId = cs.CashDenominationId
group by
    c.Year,
    t.DateCollected,
    t.DateDeposited,
    t.CauseId;

create view Deposits as
select distinct
    DateDeposited,
    extract(year from DateCollected) as Year
from Trays;

create view DepositCash as
select
    t.DateDeposited,
    cs.CashDenominationId,
    sum(cs.Quantity) as Quantity
from
    Cash cs
    join Trays t
        on t.TrayId = cs.TrayId
group by
    t.DateDeposited,
    cs.CashDenominationId;

create view DepositCheques as
select
    t.DateDeposited,
    t.DateCollected,
    d.DonationId,
    sum(dc.Amount) as Amount
from
    Donations d
    join Trays t
        on t.TrayId = d.TrayId
    join DonationComponents dc
        on dc.DonationId = d.DonationId
where d.Cash = 'f'
group by
    t.DateDeposited,
    t.DateCollected,
    d.DonationId;

