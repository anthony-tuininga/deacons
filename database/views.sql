create view Donations_v as
select
    dr.Year,
    dp.DateDeposited,
    ct.DateCollected,
    d.DonationId,
    d.Cash,
    dc.CauseId,
    d.DonatorId,
    dc.Amount
from
    Donations d
    join DonationComponents dc
        on dc.DonationId = d.DonationId
    join Donators dr
        on dr.DonatorId = d.DonatorId
    join Collections ct
        on ct.CollectionId = d.CollectionId
    join Deposits dp
        on dp.DepositId = ct.DepositId;

