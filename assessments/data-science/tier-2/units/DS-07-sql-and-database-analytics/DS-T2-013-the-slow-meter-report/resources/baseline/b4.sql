SELECT m.feeder_id,
       1 + (SELECT COUNT(*) FROM vends v2 JOIN meters m2 ON m2.meter_id = v2.meter_id
            WHERE m2.feeder_id = m.feeder_id
              AND (v2.amount_ngn > v.amount_ngn OR (v2.amount_ngn = v.amount_ngn AND v2.vend_id < v.vend_id))) AS rank,
       v.vend_id, v.amount_ngn
FROM vends v JOIN meters m ON m.meter_id = v.meter_id
WHERE (SELECT COUNT(*) FROM vends v2 JOIN meters m2 ON m2.meter_id = v2.meter_id
       WHERE m2.feeder_id = m.feeder_id
         AND (v2.amount_ngn > v.amount_ngn OR (v2.amount_ngn = v.amount_ngn AND v2.vend_id < v.vend_id))) < 3
ORDER BY m.feeder_id, rank;
