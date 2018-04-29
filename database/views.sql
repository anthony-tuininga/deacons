create view Donations_v as
select
    c.Year,
    d.DateDeposited,
    d.DateCollected,
    d.DonationId,
    d.Cash,
    dc.CauseId,
    d.DonatorId,
    dc.Amount
from
    Donations d
    join DonationComponents dc
        on dc.DonationId = d.DonationId
    join Causes c
        on c.CauseId = dc.CauseId;

create view DonationSummary as
select
    dr.Year,
    d.DateCollected,
    dc.CauseId,
    sum(case when cash = 'f' then dc.Amount else '$0' end) as ChequeAmount,
    sum(case when cash = 't' then dc.Amount else '$0' end) as CashAmount
from
    Donations d
    join DonationComponents dc
        on dc.DonationId = d.DonationId
    join Donators dr
        on dr.DonatorId = d.DonatorId
group by
    dr.Year,
    d.DateCollected,
    dc.CauseId;

create view CashSummary as
select
    c.Year,
    cs.DateCollected,
    cs.CauseId,
    sum(cs.Quantity * cd.Value) as Amount
from
    Cash cs
    join Causes c
        on c.CauseId = cs.CauseId
    join CashDenominations cd
        on cd.CashDenominationId = cs.CashDenominationId
group by
    c.Year,
    cs.DateCollected,
    cs.CauseId;

create view Deposits as
select
    DateDeposited,
    extract(year from DateCollected) as Year
from Donations
union
select
    DateDeposited,
    extract(year from DateCollected)
from Cash;

create view DepositCash as
select
    DateDeposited,
    CashDenominationId,
    sum(Quantity) as Quantity
from Cash
group by
    DateDeposited,
    CashDenominationId;

create view DepositCheques as
select
    d.DateDeposited,
    d.DonationId,
    sum(dc.Amount) as Amount
from
    Donations d
    join DonationComponents dc
        on dc.DonationId = d.DonationId
where d.Cash = 'f'
group by
    d.DateDeposited,
    d.DonationId;

