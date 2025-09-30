create or replace view stock_counts as
select p.model_number, count(i.item_id) as count
from item i
join product p on i.product_id = p.product_id
group by p.model_number
order by p.model_number;