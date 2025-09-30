CREATE VIEW pallet_info_view AS
SELECT
    p.pallet_id,
    p.shelf_id,
    pr.model_number
FROM
    pallet p
JOIN
    product pr ON p.product_id = pr.product_id
ORDER BY
    p.pallet_id;