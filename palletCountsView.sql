create or replace view pallet_counts_by_model as
select 
    p.model_number,
    count(distinct pl.pallet_id) as pallet_count
from pallet pl
join product p 
    on pl.product_id = p.product_id
group by p.model_number
order by p.model_number;