-- Q04: Net position of every member. contributed_ngn is the sum of all contribution rows. outstanding_ngn is the sum over that member's loans whose status is not 'cleared' of MAX(principal - repaid, 0), where repaid is that loan's total repayments. net_ngn = contributed_ngn - outstanding_ngn. Members with nothing show 0, never NULL.
-- Columns, in order: member_id, contributed_ngn, outstanding_ngn, net_ngn
-- ORDER BY member_id. One row per member.
-- Write ONE read-only SELECT (a WITH clause is allowed) below this line.

