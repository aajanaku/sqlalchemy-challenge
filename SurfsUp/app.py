# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, func, MetaData
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
metadata = MetaData()

# Reflect the tables from the database into metadata
metadata.reflect(bind=engine)
# reflect the tables
Base = automap_base()

# Reflect the tables from the database into the base
Base.prepare(engine, reflect=True)


# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
Session = sessionmaker(bind=engine)
session = Session()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def Welcome():

    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/yyyy-mm-dd<br/>"
        f"/api/v1.0/temp/yyyy-mm-dd/yyyy-mm-dd<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    rows = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()
    session.close()
    precip = {date: prcp for date, prcp in rows}
    return jsonify(precip)



@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()

    session.close()

    stations = list(np.ravel(results))
    return jsonify(stations=stations)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()

    session.close()
    temps = list(np.ravel(results))

    # Return the results
    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]


    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()

        session.close()

        temps = list(np.ravel(results))
        return jsonify(temps)       

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    temps = list(np.ravel(results))
    return jsonify(temps)    

if __name__ == "__main__":
    app.run()
