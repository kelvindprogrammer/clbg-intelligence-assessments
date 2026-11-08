SELECT v.vend_id,
       CAST(julianday(v.vended_on) - julianday((SELECT p.vended_on FROM vends p WHERE p.meter_id = v.meter_id
              AND (p.vended_on < v.vended_on OR (p.vended_on = v.vended_on AND p.vend_id < v.vend_id))
              ORDER BY p.vended_on DESC, p.vend_id DESC LIMIT 1)) AS INTEGER) AS gap_days
FROM vends v
ORDER BY v.vend_id;
