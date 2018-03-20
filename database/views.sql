create view Donations_v as
select
    dr.Year,
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
    join Donators dr
        on dr.DonatorId = d.DonatorId;

