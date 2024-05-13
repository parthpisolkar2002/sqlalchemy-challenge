# Import the dependencies.
# Import necessary libraries
from flask import Flask, jsonify
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from datetime import timedelta

# Create engine to connect to SQLite database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)
# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create session
session = Session(engine)

# Create Flask app
app = Flask(__name__)

# Define routes
@app.route("/")
def home():
    """List all available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the JSON representation of your dictionary."""
    # Calculate the date one year ago from the last date in the database
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - timedelta(days=365)
    # Query for the last 12 months of precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()
    # Convert the query results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Query all stations
    stations = session.query(Station.station).all()
    # Convert list of tuples into normal list
    station_list = [station[0] for station in stations]
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations for the previous year."""
    # Query the most active station
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count().desc()).first()[0]
    # Calculate the date one year ago from the last date in the database
    one_year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - timedelta(days=365)
    # Query for the last 12 months of temperature observations for the most active station
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()
    # Convert the query results to a list of dictionaries
    tobs_list = []
    for date, tobs in tobs_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start_date(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start date."""
    # Query for TMIN, TAVG, and TMAX for all dates greater than or equal to the start date
    temperature_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    # Convert the query results to a list of dictionaries
    temperature_stats_list = []
    for result in temperature_stats:
        temperature_stats_dict = {}
        temperature_stats_dict["TMIN"] = result[0]
        temperature_stats_dict["TAVG"] = result[1]
        temperature_stats_dict["TMAX"] = result[2]
        temperature_stats_list.append(temperature_stats_dict)
    return jsonify(temperature_stats_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end range."""
    # Query for TMIN, TAVG, and TMAX for the date range
    temperature_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    # Convert the query results to a list of dictionaries
    temperature_stats_list = []
    for result in temperature_stats:
        temperature_stats_dict = {}
        temperature_stats_dict["TMIN"] = result[0]
        temperature_stats_dict["TAVG"] = result[1]
        temperature_stats_dict["TMAX"] = result[2]
        temperature_stats_list.append(temperature_stats_dict)
    return jsonify(temperature_stats_list)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)

