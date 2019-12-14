import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
        f"/api/v1.0/station<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>" 
        f"/api/v1.0/start/end"
    )


@app.route("/api/v1.0/precipitation")

def precipitation():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query 
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)


@app.route("/api/v1.0/station")

def station():
    """Return a list of all stations """
    
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


# query for the dates and temperature observations from a year from the last data point.
# Return a JSON list of Temperature Observations (tobs) for the previous year.
@app.route("/api/v1.0/tobs")

def tobs():
    """Return a list of tobs for prev yr """
    
    session = Session(engine)

    results =session.query(Measurement.date).order_by(Measurement.date.desc())
    lastDate =results[0][0]
    lastDate_dt = dt.date(int(lastDate[0:4]), int(lastDate[5:7]), int(lastDate[8:10]) ) 
    date_1yr_ago = lastDate_dt -dt.timedelta(days =365)

    results =session.query(Measurement.date, Measurement.tobs).group_by(Measurement.date).\
            filter(Measurement.date >= date_1yr_ago).all()

    session.close()

    # Convert list of tuples into normal list
    all_tobs = list(np.ravel(results))

    return jsonify(all_tobs)


# >>> When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and \
# equal to the start date.

@app.route("/api/v1.0/<start>")
def temps_start(start):

    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()
    session.close()

    # Convert list of tuples into normal list
    all_temps = list(np.ravel(results))
    return jsonify(all_temps)


# >>> When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates \
# between the start and end date inclusive.

@app.route("/api/v1.0/<start>/<end>")
def temps_start_end(start,end):

    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    # Convert list of tuples into normal list
    all_temps_range = list(np.ravel(results))
    return jsonify(all_temps_range)



if __name__ == '__main__':
    app.run(debug=True)
