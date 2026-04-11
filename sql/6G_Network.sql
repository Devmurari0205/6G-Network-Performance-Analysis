-- CREATE A TABLE

CREATE TABLE Network_Performance (
	Date DATE,
	Timestamp TIME,
	Machine_ID INT,
	Operation_Mode VARCHAR (20),
	Temperature_C DECIMAL (7,3),
	Vibration_Hz DECIMAL(7,3),
	Power_Consumption_kW DECIMAL(7,3),
	Network_Latency_ms DECIMAL(7,3),
	Packet_Loss,1 DECIMAL(7,3),
	Quality_Control_Defect_Rate DECIMAL(7,3),
	Production_Speed_units_per_hr DECIMAL(7,3),
	Predictive_Maintenance_Score DECIMAL(7,3),
	Error_Rate DECIMAL(7,3),
	Efficiency_Status VARCHAR (10),
	Month INT,
	Month_Name VARCHAR,
	Hour INT
);


-- IMPORT TABLE

SELECT * FROM Network_Performance;

-- KIP QUERIES

-- 1) Network Stablility Index
SELECT ROUND(100 - (AVG(Network_Latency_ms)/50) * 50 - (AVG(Packet_Loss)/50) * 50,2) AS 
Network_Stability_Index
FROM Network_Performance;

-- 2) Avarage Packet loss 
SELECT ROUND (AVG(Packet_Loss),2) AS Avg_packet_loss_pct
FROM Network_Performance;

-- 3) Production Speed
SELECT ROUND (AVG(Production_Speed_units_per_hr),2) AS Avg_Production_Speed
FROM Network_Performance;

-- 4) Error Rate
SELECT ROUND(AVG(Error_Rate),2) AS Avg_Error_Rate
FROM Network_Performance;

-- 5) Defact Rate
SELECT ROUND(AVG(Quality_Control_Defect_Rate),2) AS Avg_Defect_Rate
FROM Network_Performance;

-- Efficiency Distribution
SELECT ROUND(SUM(CASE WHEN Efficiency_Status = 'High' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),2) AS Pct_High_Efficiency,
ROUND(SUM(CASE WHEN Efficiency_Status = 'Medium' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),2) AS Pct_Medium_Efficiency,
ROUND(SUM(CASE WHEN Efficiency_Status = 'Low' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),2) AS Pct_Low_Efficiency
FROM Network_Performance;

-- High Latency Event Rate
SELECT ROUND(SUM(CASE WHEN Network_Latency_ms > 30 THEN 1 ELSE 0 END) * 100 / COUNT(*),2) AS High_Latency_Event_Pct
FROM Network_Performance;

-- High Packet Loss Event Rate
SELECT ROUND(SUM(CASE WHEN Packet_Loss > 3.5 THEN 1 ELSE 0 END) * 100 / COUNT(*),2) AS High_Latency_Event_Pct
FROM Network_Performance;

-- Total Records
SELECT COUNT(*) AS Total_Records
FROM Network_Performance;

-- Network Performance Profiling
-- Analyze latency

SELECT 
	ROUND(MIN(Network_Latency_ms),2) AS min_latency,
	ROUND(AVG(Network_Latency_ms),2) AS avg_latency,
	ROUND(MAX(Network_Latency_ms),2) AS max_latency
FROM  Network_Performance;
	
-- Packet Loss Distribution
SELECT 
	ROUND(MIN(Packet_Loss),2) AS min_packet_loss,
	ROUND(AVG(Packet_Loss),2) AS avg_packet_loss,
	ROUND(MAX(Packet_Loss),2) AS max_packet_loss
FROM Network_Performance;
	
-- Network Quality Segmentation
SELECT ROUND(SUM(Network_Latency_ms),2) AS Network_Latency_ms,
	ROUND(SUM(Packet_Loss),2) AS Packet_Loss,
		CASE
			WHEN Network_Latency_ms < 20 AND Packet_Loss < 1 THEN 'Stable'
			WHEN Network_Latency_ms Between 20 AND 50 THEN 'Moderate'
			ELSE 'Unstable'
		END AS Network_Quality
		FROM Network_Performance
		GROUP BY Network_Quality;
	
-- Efficiency distribution by network quality

SELECT 
	Network_Quality,
	Efficiency_Status,
	COUNT(*) AS Total
FROM(SELECT  *,
	CASE 
	WHEN Network_Latency_ms < 20 AND Packet_Loss < 1 THEN 'High'
		WHEN Network_Latency_ms Between 20 AND 50 THEN 'Medium'
		ELSE 'Low'
	END AS Network_Quality 
	FROM Network_Performance
) t
GROUP BY Network_Quality,Efficiency_Status
ORDER BY Network_Quality;


-- Latency Impact Diagnosi
-- Network vs Efficiency Analysis
SELECT
	ROUND(Network_Latency_ms,0) AS Latency_bucket,
	ROUND(AVG(Production_Speed_units_per_hr),2) AS Avg_speed
FROM Network_Performance
GROUP BY Latency_bucket
ORDER BY Latency_bucket;

-- Efficiency drop with latency
SELECT 
	Network_Latency_ms,
	ROUND(AVG(CASE WHEN Efficiency_Status = 'High' THEN 1 ELSE 0 END),0) AS high_efficincy_ratio
FROM Network_Performance
GROUP BY Network_Latency_ms
ORDER BY  Network_Latency_ms ;

-- Compare real-time vs delayed communication periods
SELECT 
		CASE 
		WHEN Network_Latency_ms < 20 THEN 'Real-Time'
		WHEN Network_Latency_ms >= 50 THEN 'Delayed'
		ELSE 'Morerate'
	END AS Communication_type,

	ROUND(AVG(Production_Speed_units_per_hr),1) AS avg_speed,
	ROUND(AVG(Error_Rate),1)AS avg_rate,
	ROUND(AVG(Quality_Control_Defect_Rate),1) AS avg_defact
FROM Network_Performance
GROUP BY Communication_type
ORDER BY Communication_type;

-- Packet Loss Impact Diagnostics
-- Correlate packet loss with error rate
SELECT 
	corr(Packet_Loss,Error_Rate) AS Packetloss_error_correlation
FROM Network_Performance;

-- Assess defect rate changes during packet loss spikes
SELECT
	CASE
		WHEN Packet_Loss > 2 THEN 'Spike'
		ELSE 'Normal'
	END AS packet_loss_condition,

	ROUND(AVG(Quality_Control_Defect_Rate),2) AS avg_defact_rate,
	COUNT(*) AS Total_Record
FROM Network_Performance
GROUP BY packet_loss_condition;
	
--Identify communication reliability thresholds
SELECT 
	ROUND(Network_Latency_ms,0) AS latency_buckets,
	ROUND(AVG(Production_Speed_units_per_hr),2) As avg_speed,
	ROUND(AVG(Error_Rate),2) AS avg_error_rate
FROM Network_Performance
GROUP BY latency_buckets
ORDER BY latency_buckets

-- Operation Mode Interaction Analysis
-- Evaluate network impact across operation modes
SELECT 
	Operation_Mode,
	ROUND(AVG(Network_Latency_ms),2) AS avg_latency,
	ROUND(AVG(Packet_Loss),2) AS avg_packet_loss,
	ROUND(AVG(Production_Speed_units_per_hr),2) AS avg_speed,
	ROUND(AVG(Error_Rate),2) AS avg_error_rate,
	ROUND(AVG(Quality_Control_Defect_Rate),2) AS avg_defect
FROM Network_Performance
GROUP BY Operation_Mode
ORDER BY Operation_Mode;

-- Identify modes most sensitive to communication delays
SELECT
	Operation_Mode,
	CORR(Network_Latency_ms,Production_Speed_units_per_hr) AS latency_speed_error,
	CORR(Network_Latency_ms,Error_Rate) AS latency_error_corr
FROM Network_Performance
GROUP BY Operation_Mode;

-- Compare efficiency stability under identical mechanical conditions
SELECT
	Operation_Mode,
    CASE 
        WHEN Network_Latency_ms < 20 THEN 'Low Latency'
        WHEN Network_Latency_ms > 50 THEN 'High Latency'
        ELSE 'Medium'
    END AS latency_group,
    
   ROUND(AVG(Production_Speed_units_per_hr),2) AS avg_speed,
   ROUND(AVG(Error_Rate),2) AS avg_error

FROM Network_Performance
GROUP BY Operation_Mode,latency_group
ORDER BY Operation_Mode;

-- SELECT ALL TABLE
SELECT * FROM Network_Performance;


