/*
  VIEW NAME: vw_capital_weather_station
  VIEW DESC: Find the closest weather station to each state capital
  DEPLOYMENT DTTM: _DEPLOYMENT_DTTM
*/

SELECT *
FROM (
  	SELECT
  	ROW_NUMBER() OVER(PARTITION BY Capital ORDER BY Distance ASC) AS ROW_RANK --Rank the weather stations by capital closest to farthest
  	,subq,*
  	FROM (
        	SELECT
        	ST_DISTANCE(
                    	ST_GEOGPOINT(capitals.longitude, capitals.latitude),
                    	ST_GEOGPOINT( stations.lon , stations.lat )
                    	)
                    	* 0.00062137 AS Distance --convert meters to miles
        	,CONCAT(capitals.description, ', ', capitals.name) AS Capital
        	,stations.usaf
          ,stations.wban
        	FROM `_RUN_PROJECT_ID.weather_analysis.us_state_capitals` capitals
            	CROSS JOIN `bigquery-public-data.noaa_gsod.stations` AS stations
        	WHERE stations.lat<50 AND stations.lat>15 AND stations.lon<-60 AND stations.lon>-130 --FILTER Weather Stations to USA region only
        	AND capitals.longitude IS NOT NULL AND capitals.latitude IS NOT NULL
      	) subq
  	) subq2
WHERE ROW_RANK = 1 --Select the closest weather station for each Capital
