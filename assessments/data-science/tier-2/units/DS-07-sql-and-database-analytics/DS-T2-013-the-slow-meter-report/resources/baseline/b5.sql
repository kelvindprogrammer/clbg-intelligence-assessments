SELECT d.feeder_id, d.vended_on,
       (SELECT SUM(v.amount_ngn) FROM vends v JOIN meters m ON m.meter_id = v.meter_id
        WHERE m.feeder_id = d.feeder_id AND v.vended_on <= d.vended_on AND v.vended_on > date(d.vended_on, '-7 day')) AS revenue_7d
FROM (SELECT DISTINCT m.feeder_id, v.vended_on FROM vends v JOIN meters m ON m.meter_id = v.meter_id) d
ORDER BY d.feeder_id, d.vended_on;
