alter table Years drop column PromptForReceiptGeneration;

alter table Years add column notes character varying(250);

update TaxReceipts set Canceled = 'f' where Canceled is null;

alter table TaxReceipts alter column Canceled set not null;

