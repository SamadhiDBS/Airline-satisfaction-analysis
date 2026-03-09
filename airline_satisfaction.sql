--check if table exists
select count(*) from airline_satisfaction

--see first 10 rows
select * from airline_satisfaction limit 10


--1: What is our overall satisfaction rate?
select
	round(avg(satisfaction) * 100, 2) as overall_satisfaction_percent
from airline_satisfaction;

--2: How are satisfied vs dissatisfied customers distributed?
select
	case 
		when satisfaction = 1 then 'Satisfied'
		else 'Dissatisfied'
	end as customer_status,
	count(*) as passenger_count,
	round(count(*) * 100.0 / (select count(*) from airline_satisfaction), 2 ) as percentage
from airline_satisfaction
group by satisfaction;

--3: Which customer type is more satisfied?
select 
	case 
		when customer_type = 0 then 'Loyal customer'
		else 'Disloyal customer'
	end as customer_type,
	count(*) as total,
	round(avg(satisfaction) * 100, 2) as satisfaction_rate
from airline_satisfaction
group by customer_type;

--4: How does satisfaction vary by travel class?
select 
	case
		when class = 0 then 'Business'
		when class = 1 then 'Economy'
		else 'Economy Plus'
	end as travel_class,
	count(*) as passengers,
	round(avg(satisfaction) * 100, 2) as satisfaction_rate
from airline_satisfaction
group by class
order by satisfaction_rate desc;

--5: Which age groups are most/least satisfied?
select 
	case 
		when age < 18 then 'under 18'
		when age between 18 and 29 then '18-29'
		when age between 30 and 39 then '30-39'
		when age between 40 and 49 then '40-49'
		when age between 50 and 59 then '50-59'
		else '60+'
	end as age_group,
	count(*) as passengers,
	round(avg(satisfaction) * 100, 2) as satisfaction_rate
from airline_satisfaction
group by age_group
order by satisfaction_rate;

--6: What are the average ratings for each service?
SELECT 
    'Inflight WiFi' as service,
    ROUND(AVG(inflight_wifi_service), 2) as avg_rating
FROM airline_satisfaction
UNION ALL
SELECT 'Food & Drink', ROUND(AVG(food_and_drink), 2)
FROM airline_satisfaction
UNION ALL
SELECT 'Seat Comfort', ROUND(AVG(seat_comfort), 2)
FROM airline_satisfaction
UNION ALL
SELECT 'Inflight Entertainment', ROUND(AVG(inflight_entertainment), 2)
FROM airline_satisfaction
UNION ALL
SELECT 'Cleanliness', ROUND(AVG(cleanliness), 2)
FROM airline_satisfaction
UNION ALL
SELECT 'Baggage Handling', ROUND(AVG(baggage_handling), 2)
FROM airline_satisfaction
ORDER BY avg_rating DESC;

--7: What's the satisfaction rate based on WiFi rating?
SELECT 
    inflight_wifi_service as wifi_rating,
    COUNT(*) as passengers,
    ROUND(AVG(satisfaction) * 100, 2) as satisfaction_rate
FROM airline_satisfaction
GROUP BY inflight_wifi_service
ORDER BY inflight_wifi_service;

--8: Which service has the biggest gap between satisfied and dissatisfied?
SELECT 
    'Seat Comfort' as service,
    ROUND(AVG(CASE WHEN satisfaction = 1 THEN seat_comfort END), 2) as satisfied_avg,
    ROUND(AVG(CASE WHEN satisfaction = 0 THEN seat_comfort END), 2) as dissatisfied_avg,
    ROUND(AVG(CASE WHEN satisfaction = 1 THEN seat_comfort END) - 
          AVG(CASE WHEN satisfaction = 0 THEN seat_comfort END), 2) as gap
FROM airline_satisfaction
UNION ALL
SELECT 'Food & Drink',
    ROUND(AVG(CASE WHEN satisfaction = 1 THEN food_and_drink END), 2),
    ROUND(AVG(CASE WHEN satisfaction = 0 THEN food_and_drink END), 2),
    ROUND(AVG(CASE WHEN satisfaction = 1 THEN food_and_drink END) - 
          AVG(CASE WHEN satisfaction = 0 THEN food_and_drink END), 2)
FROM airline_satisfaction
ORDER BY gap DESC;

--9: How do delays affect satisfaction?
SELECT 
    CASE 
        WHEN departure_delay_in_minutes = 0 THEN 'No Delay'
        WHEN departure_delay_in_minutes BETWEEN 1 AND 30 THEN 'Minor (1-30 min)'
        WHEN departure_delay_in_minutes BETWEEN 31 AND 60 THEN 'Moderate (31-60 min)'
        ELSE 'Major (60+ min)'
    END as delay_category,
    COUNT(*) as flights,
    ROUND(CAST(AVG(satisfaction) * 100 AS numeric), 2) as satisfaction_rate
FROM airline_satisfaction
GROUP BY 
    CASE 
        WHEN departure_delay_in_minutes = 0 THEN 'No Delay'
        WHEN departure_delay_in_minutes BETWEEN 1 AND 30 THEN 'Minor (1-30 min)'
        WHEN departure_delay_in_minutes BETWEEN 31 AND 60 THEN 'Moderate (31-60 min)'
        ELSE 'Major (60+ min)'
    END
ORDER BY 
    MIN(departure_delay_in_minutes);

--10: What's the satisfaction rate for flights with NO delays?
SELECT 
    ROUND(AVG(satisfaction) * 100, 2) as satisfaction_rate
FROM airline_satisfaction
WHERE departure_delay_in_minutes = 0;

--11: Which class suffers the most from delays?
SELECT 
    CASE 
        WHEN class = 0 THEN 'Business'
        WHEN class = 1 THEN 'Economy'
        ELSE 'Economy Plus'
    END as travel_class,
    ROUND(CAST(AVG(departure_delay_in_minutes) AS numeric), 2) as avg_delay_minutes,
    ROUND(CAST(AVG(arrival_delay_in_minutes) AS numeric), 2) as avg_arrival_delay,
    ROUND(CAST(AVG(satisfaction) * 100 AS numeric), 2) as satisfaction_rate
FROM airline_satisfaction
GROUP BY class
ORDER BY AVG(departure_delay_in_minutes) DESC;

--12: Which services have the lowest ratings from dissatisfied customers?
SELECT 
    ROUND(AVG(CASE WHEN satisfaction = 0 THEN inflight_wifi_service END), 2) as wifi_for_dissatisfied,
    ROUND(AVG(CASE WHEN satisfaction = 0 THEN seat_comfort END), 2) as seat_for_dissatisfied,
    ROUND(AVG(CASE WHEN satisfaction = 0 THEN food_and_drink END), 2) as food_for_dissatisfied,
    ROUND(AVG(CASE WHEN satisfaction = 0 THEN cleanliness END), 2) as clean_for_dissatisfied,
    ROUND(AVG(CASE WHEN satisfaction = 0 THEN inflight_entertainment END), 2) as entertainment_for_dissatisfied
FROM airline_satisfaction;

--13: What's the satisfaction rate for Economy class with delays?
SELECT 
    CASE 
        WHEN departure_delay_in_minutes = 0 THEN 'No Delay'
        ELSE 'With Delay'
    END as delay_status,
    COUNT(*) as passengers,
    ROUND(AVG(satisfaction) * 100, 2) as satisfaction_rate
FROM airline_satisfaction
WHERE class = 1  -- Economy class
GROUP BY delay_status;

--14: Top 3 factors that would most improve satisfaction (correlation)
SELECT 
    'WiFi' as factor,
    ROUND(CORR(inflight_wifi_service, satisfaction)::numeric, 3) as correlation_with_satisfaction
FROM airline_satisfaction
UNION ALL
SELECT 'Seat Comfort', ROUND(CORR(seat_comfort, satisfaction)::numeric, 3)
FROM airline_satisfaction
UNION ALL
SELECT 'Food & Drink', ROUND(CORR(food_and_drink, satisfaction)::numeric, 3)
FROM airline_satisfaction
UNION ALL
SELECT 'Entertainment', ROUND(CORR(inflight_entertainment, satisfaction)::numeric, 3)
FROM airline_satisfaction
UNION ALL
SELECT 'Cleanliness', ROUND(CORR(cleanliness, satisfaction)::numeric, 3)
FROM airline_satisfaction
ORDER BY correlation_with_satisfaction DESC;


--15: What percentage of dissatisfied customers gave low WiFi ratings?
SELECT 
    COUNT(*) as dissatisfied_with_poor_wifi,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM airline_satisfaction WHERE satisfaction = 0), 2) as percentage
FROM airline_satisfaction
WHERE satisfaction = 0 AND inflight_wifi_service <= 2;

--16: What's the "tipping point" for delays?
SELECT 
    departure_delay_in_minutes,
    ROUND(AVG(satisfaction) * 100, 2) as satisfaction_rate
FROM airline_satisfaction
WHERE departure_delay_in_minutes BETWEEN 10 AND 120
GROUP BY departure_delay_in_minutes
ORDER BY departure_delay_in_minutes;

--17: Which passenger segment should we target first?
SELECT 
    CASE 
        WHEN customer_type = 0 THEN 'Loyal' ELSE 'Disloyal' 
    END as loyalty,
    CASE 
        WHEN class = 0 THEN 'Business'
        WHEN class = 1 THEN 'Economy'
        ELSE 'Eco Plus'
    END as class,
    COUNT(*) as passengers,
    ROUND(AVG(satisfaction) * 100, 2) as current_satisfaction,
    ROUND(100 - AVG(satisfaction) * 100, 2) as improvement_potential
FROM airline_satisfaction
GROUP BY loyalty, class
ORDER BY improvement_potential DESC
LIMIT 5;









