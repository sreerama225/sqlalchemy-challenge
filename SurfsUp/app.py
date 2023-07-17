# Import the dependencies.

import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite",pool_pre_ping=True)

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with = engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )
    
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    #most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    date_prcp_scores = session.query(Measurement.date,Measurement.prcp).\
            filter(Measurement.date >= year_ago).\
            order_by(Measurement.date).all()
    precipitation ={date:prcp for date,prcp in date_prcp_scores}
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    stations = []
    results = session.query(Station.station, Station.id).all()
    for station, id in results:
        stations_dict = {}
        stations_dict['station'] = station
        stations_dict['id'] = id
        stations.append(stations_dict)
    # results = session.query(Station.station).all()
    # stations = list(np.ravel(results))
    
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    tobs_list = []
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    active_station = session.query(Measurement.station).\
                                order_by(func.count(Measurement.station).desc()).\
                                group_by(Measurement.station).first()
    active_station_number = active_station[0]
    
    last_12_months_temp = session.query(Measurement.date, Measurement.tobs).\
                    filter(Measurement.station == active_station_number).\
                    filter(Measurement.date >= year_ago).all()
                    
    for date, tobs in last_12_months_temp:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
        tobs_list.append(tobs_dict)
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def startDate(start):
    print(start)
    print("Enter the date in yyyy-MM-dd format")
    results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
                                filter(Measurement.date >= start).all()
    print(f"temp_list:: {results}")
    temp_list = []
    for min, max, avg in results:
        temp_dict = {}
        temp_dict['Minimum Temperature'] = min
        temp_dict['Maximum Temperature'] = max
        temp_dict['Average Temperature'] = avg
        temp_list.append(temp_dict)
    
    if temp_dict['Minimum Temperature']:
        return jsonify(temp_list)
    else:
        return jsonify("No Data found for the Start Date or not in the format - YYYY-MM-DD")
         


@app.route("/api/v1.0/<start>/<end>")
def startEndDates(start,end):
    print(start)
    print(end)
    print("Enter the date in yyyy-MM-dd format")
    results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
                                filter(Measurement.date >= start).\
                                filter(Measurement.date <= end).all()
    print(f"temp_list:: {results}")
    temp_list = []
    for min, max, avg in results:
        temp_dict = {}
        temp_dict['Minimum Temperature'] = min
        temp_dict['Maximum Temperature'] = max
        temp_dict['Average Temperature'] = avg
        temp_list.append(temp_dict)
    
    if temp_dict['Minimum Temperature']:
        return jsonify(temp_list)
    else:
        return jsonify("No Data found for the given Start and End Dates or Dates not in the format - YYYY-MM-DD")
    
if __name__ == '__main__':
    app.run(debug=True)