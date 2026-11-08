SELECT v.vend_id, v.meter_id,
       ROUND((SELECT SUM(p.kwh) FROM vends p WHERE p.meter_id = v.meter_id
              AND (p.vended_on < v.vended_on OR (p.vended_on = v.vended_on AND p.vend_id <= v.vend_id))), 2) AS running_kwh
FROM vends v
ORDER BY v.vend_id;
