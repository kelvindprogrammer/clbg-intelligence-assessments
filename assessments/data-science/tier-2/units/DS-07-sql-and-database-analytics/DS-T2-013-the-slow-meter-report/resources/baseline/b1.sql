SELECT v.meter_id, v.vend_id, v.vended_on, v.amount_ngn
FROM vends v
WHERE v.vend_id = (SELECT v2.vend_id FROM vends v2 WHERE v2.meter_id = v.meter_id
                   ORDER BY v2.vended_on DESC, v2.vend_id DESC LIMIT 1)
ORDER BY v.meter_id;
