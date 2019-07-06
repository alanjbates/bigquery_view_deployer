/*
  VIEW NAME: vw_noaa_gsod_clean
  VIEW DESC: Limits the up the public noaa_gsod data to USA area.
             Provies meaningful column name aliases.
             Joins station location info to weather data.
  DEPLOYMENT DTTM: _DEPLOYMENT_DTTM
*/

SELECT
--Weather Station Location Information
ST_GEOGPOINT(st.lon, st.lat) AS StationGeoPoint
,st.lon AS StationLongitude
,st.lat AS StationLatitude
,CONCAT(w.stn,w.wban) AS StationId
,st.name AS StationName
,st.elev AS StationElevation
,st.country AS StationCountry
,st.state AS StationState
,CAST(CONCAT(w.year,'-', w.mo, '-',w.da) AS DATE) AS ObservationDate

--Temp Info
,w.temp AS AverageTemp
,w.max  AS MaxTemp
,w.min  AS MinTemp
,w.count_temp AS NumberofTempObservations

---Dewpoint Info
,w.dewp AS AverageDewpoint
,w.count_dewp AS NumberofDewpointObservations

--Pressure Info
,w.slp AS AverageSeaLevelPressure
,w.count_slp AS NumberofSeaLevelPressureObservations
,w.stp AS AverageStationPressure
,w.count_stp AS NumberofStationPressureObservations

--Wind Info
,w.wdsp AS AverageWindspeedKnots
,w.mxpsd AS MaxSustainedWindspeedKnots
,w.gust AS MaxGustWindspeedKnots
,w.count_wdsp AS NumberofWindspeedObservations

--Precipitation Info
,w.flag_prcp AS PrecipitationLengthLookup
,w.prcp AS TotalRainFallAndSnowMelt
,w.sndp AS SnowDepth
,w.visib AS AverageVisibilityDistance
,w.count_visib AS NumberofVisibilityObservations
,w.fog AS FogBoolean
,w.rain_drizzle AS RainBoolean
,w.snow_ice_pellets AS SnowIceBoolean
,w.hail AS HailBoolean
,w.thunder AS ThunderBoolean
,w.tornado_funnel_cloud  AS TornadoFunnelCloudBoolean

FROM `bigquery-public-data.noaa_gsod.gsod20*` as w  --20* will union all tables year 2000-2019
	INNER JOIN `bigquery-public-data.noaa_gsod.stations` as st
    	ON concat(st.usaf,st.wban)=concat(w.stn,w.wban)
   	 
WHERE st.lat<50  AND st.lat>15  AND st.lon<-60  AND st.lon>-130 --FILTER TO USA REGION ONLY
