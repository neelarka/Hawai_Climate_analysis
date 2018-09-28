import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import pandas as pd
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Latest Date
latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
# Date 12 months from the latest date
last_twelve_months = dt.datetime.strptime(latest_date, '%Y-%m-%d') - dt.timedelta(days=365)

#Flask set up
app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"Enter the start and end date in ISO format for next two routes:<br/>"
        #f"/api/v1.0/<start><br/>"
        #f"/api/v1.0/<start>/<end>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )


#########################################################################################
@app.route("/api/v1.0/tobs")
def temp_obs():
    """Return a JSON list of Temperature Observations (tobs) for the previous year"""
   # Retrieve the last 12 months of temperature data
    temp_results = session.query(Measurement.date, Measurement.tobs).\
                    filter(Measurement.date, Measurement.date >= last_twelve_months).\
                    group_by(Measurement.date).all()
    temp_obs = temp_results
    #dic = pd.DataFrame(temp_results).set_index('date').rename(columns={'tobs': 'temperature_observations'})
    #dic.temperature_observations = dic.temperature_observations.astype(float)
    #temp_obs = dic.to_dict()
    return jsonify(temp_obs)


#########################################################################################
@app.route("/api/v1.0/stations")
def station_name():
    """Return a JSON list of stations"""
   # Retrieve the list of stations
    results = session.query(Station.station).all()
    station_name = results
    return jsonify(station_name)


#########################################################################################
@app.route("/api/v1.0/precipitation")
def prcp_obs():
    """Return a JSON list of precipitation (prcp) for the previous year"""
   # Retrieve the list of stations
    p_results =  session.query(Measurement.date, Measurement.prcp).\
                    filter(Measurement.date >= last_twelve_months).\
                    group_by(Measurement.date).all()
    # Convert list of tuples into dictionary
    dic = pd.DataFrame(p_results).set_index('date').rename(columns={'prcp': 'precipitation'})
    #dic.precipitation = precipitation.astype(float)
    prcp_obs = dic.to_dict()
    return jsonify(prcp_obs)
#########################################################################################

@app.route("/api/v1.0/<start>")
def daily_normals(start): 
    """Fetch the date in "%y-%m-%d" format for all dates greater than and equal to the start date """
    #end =  dt.date(2017, 8, 23)
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter( Measurement.date >= start).all()
    daily_normals = list(np.ravel(results))
    return jsonify(daily_normals)

#########################################################################################
@app.route("/api/v1.0/<start>/<end>")
def trip_temp(start=None,end=None):
    """Return a JSON list of the minimum temperature, 
    the average temperature, and the max temperature for a given start or start-end range"""
    # Fetch the date in "%y-%m-%d" format for all dates greater than and equal to the start date and less the end date
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start, Measurement.date <= end).all()
    # Convert list of tuples into normal list
    trip_temp = list(np.ravel(results))
    return jsonify(trip_temp)


if __name__ == "__main__":
    app.run(debug=True)