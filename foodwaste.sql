-- 1. Providers per city
SELECT "City", COUNT(*) AS provider_count
FROM providers
GROUP BY "City";

-- 2. Receivers per city
SELECT "City", COUNT(*) AS receiver_count
FROM receivers
GROUP BY "City";

-- 3. Provider type contributing the most food
SELECT "Provider_Type", SUM("Quantity") AS total_quantity
FROM food_listings
GROUP BY "Provider_Type"
ORDER BY total_quantity DESC
LIMIT 1;

-- 4. Contact info of providers in a specific city (e.g., 'New Jessica')
SELECT "Name", "Contact"
FROM providers
WHERE "City" = 'New Jessica';

-- 5. Receivers with the most food claims
SELECT r."Name", COUNT(c."Claim_ID") AS total_claims
FROM claims c
JOIN receivers r ON c."Receiver_ID" = r."Receiver_ID"
GROUP BY r."Name"
ORDER BY total_claims DESC;

-- 6. Total quantity of food available
SELECT SUM("Quantity") AS total_quantity
FROM food_listings;

-- 7. City with highest number of food listings
SELECT "Location", COUNT(*) AS listings
FROM food_listings
GROUP BY "Location"
ORDER BY listings DESC
LIMIT 1;

-- 8. Most commonly available food types
SELECT "Food_Type", COUNT(*) AS count
FROM food_listings
GROUP BY "Food_Type"
ORDER BY count DESC;

-- 9. Food claims per food item
SELECT "Food_ID", COUNT(*) AS claims
FROM claims
GROUP BY "Food_ID"
ORDER BY claims DESC;

-- 10. Provider with most completed food claims
SELECT p."Name", COUNT(*) AS completed_claims
FROM claims c
JOIN food_listings f ON c."Food_ID" = f."Food_ID"
JOIN providers p ON f."Provider_ID" = p."Provider_ID"
WHERE c."Status" = 'Completed'
GROUP BY p."Name"
ORDER BY completed_claims DESC
LIMIT 1;

-- 11. Percentage of claim statuses
SELECT "Status", COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims) AS percentage
FROM claims
GROUP BY "Status";

-- 12. Average quantity claimed per receiver
SELECT r."Name", AVG(f."Quantity") AS avg_quantity
FROM claims c
JOIN food_listings f ON c."Food_ID" = f."Food_ID"
JOIN receivers r ON c."Receiver_ID" = r."Receiver_ID"
GROUP BY r."Name";

-- 13. Most claimed meal type
SELECT f."Meal_Type", COUNT(*) AS claims
FROM claims c
JOIN food_listings f ON c."Food_ID" = f."Food_ID"
GROUP BY f."Meal_Type"
ORDER BY claims DESC
LIMIT 1;

-- 14. Total quantity donated by each provider
SELECT p."Name", SUM(f."Quantity") AS total_donated
FROM food_listings f
JOIN providers p ON f."Provider_ID" = p."Provider_ID"
GROUP BY p."Name"
ORDER BY total_donated DESC;

-- 15. Food items expiring in the next 7 days
SELECT "Food_Name", "Expiry_Date"
FROM food_listings
WHERE "Expiry_Date" <= CURRENT_DATE + INTERVAL '7 days'
ORDER BY "Expiry_Date";

-- 16. Most donated food item
SELECT "Food_Name", COUNT(*) AS times_listed
FROM food_listings
GROUP BY "Food_Name"
ORDER BY times_listed DESC
LIMIT 1;
