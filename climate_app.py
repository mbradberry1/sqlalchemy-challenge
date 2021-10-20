{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 18,
   "id": "a5060602",
   "metadata": {},
   "outputs": [],
   "source": [
    "import numpy as np\n",
    "import sqlalchemy\n",
    "from sqlalchemy.ext.automap import automap_base\n",
    "from sqlalchemy.orm import Session\n",
    "from sqlalchemy import create_engine, func\n",
    "\n",
    "from flask import Flask, jsonify\n",
    "\n",
    "import datetime as dt"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 19,
   "id": "4a6f3952",
   "metadata": {},
   "outputs": [],
   "source": [
    "engine = create_engine(\"sqlite:///Resources/hawaii.sqlite\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 20,
   "id": "507ff3a8",
   "metadata": {},
   "outputs": [],
   "source": [
    "Base = automap_base()\n",
    "Base.prepare(engine, reflect = True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 21,
   "id": "18f75f7a",
   "metadata": {},
   "outputs": [],
   "source": [
    "Measurement = Base.classes.measurement\n",
    "Station = Base.classes.station"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 22,
   "id": "6d859c57",
   "metadata": {},
   "outputs": [],
   "source": [
    "session = Session(engine)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 23,
   "id": "26ee305f",
   "metadata": {},
   "outputs": [],
   "source": [
    "app = Flask(__name__)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 24,
   "id": "4f27fa6b",
   "metadata": {},
   "outputs": [],
   "source": [
    "def calc_temps(start_date, end_date):\n",
    "    \"\"\"TMIN, TAVG, and TMAX for a list of dates.\n",
    "    \n",
    "    Args:\n",
    "        start_date (string): A date string in the format %Y-%m-%d\n",
    "        end_date (string): A date string in the format %Y-%m-%d\n",
    "        \n",
    "    Returns:\n",
    "        TMIN, TAVG, and TMAX\n",
    "    \"\"\"\n",
    "    \n",
    "    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\\\n",
    "        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 25,
   "id": "82e65ab2",
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/\")\n",
    "def main():\n",
    "    \"\"\"List all routes that are available.\"\"\"\n",
    "    return (\n",
    "        f\"Available Routes:<br/>\"\n",
    "        f\"/api/v1.0/precipitation<br/>\"\n",
    "        f\"/api/v1.0/stations<br/>\"\n",
    "        f\"/api/v1.0/tobs<br/>\"\n",
    "        f\"/api/v1.0/<start><br/>\"\n",
    "        f\"/api/v1.0/<start>/<end>\"\n",
    "    )"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 26,
   "id": "a1c8dffd",
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/api/v1.0/precipitation\")\n",
    "def precipitation():\n",
    "    \"\"\"Return the JSON representation of your dictionary.\"\"\"\n",
    "\n",
    "    print(\"Received precipitation api request.\")\n",
    "\n",
    "    final_date_query = session.query(func.max(func.strftime(\"%Y-%m-%d\", Measurement.date))).all()\n",
    "    max_date_string = final_date_query[0][0]\n",
    "    max_date = dt.datetime.strptime(max_date_string, \"%Y-%m-%d\")\n",
    "\n",
    "    \n",
    "    begin_date = max_date - dt.timedelta(365)\n",
    "\n",
    "    \n",
    "    precipitation_data = session.query(func.strftime(\"%Y-%m-%d\", Measurement.date), Measurement.prcp).\\\n",
    "        filter(func.strftime(\"%Y-%m-%d\", Measurement.date) >= begin_date).all()\n",
    "    \n",
    "\n",
    "    results_dict = {}\n",
    "    for result in precipitation_data:\n",
    "        results_dict[result[0]] = result[1]\n",
    "\n",
    "    return jsonify(results_dict)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 27,
   "id": "f1d2596e",
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/api/v1.0/stations\")\n",
    "def stations():\n",
    "    \"\"\"Return a JSON list of stations from the dataset.\"\"\"\n",
    "\n",
    "    print(\"Received station api request.\")\n",
    "\n",
    "    #query stations list\n",
    "    stations = session.query(Station).all()\n",
    "\n",
    "    #create a list of dictionaries\n",
    "    stations_list = []\n",
    "    for station in stations:\n",
    "        station_dict = {}\n",
    "        station_dict[\"id\"] = station.id\n",
    "        station_dict[\"station\"] = station.station\n",
    "        station_dict[\"name\"] = station.name\n",
    "        station_dict[\"latitude\"] = station.latitude\n",
    "        station_dict[\"longitude\"] = station.longitude\n",
    "        station_dict[\"elevation\"] = station.elevation\n",
    "        stations_list.append(station_dict)\n",
    "\n",
    "    return jsonify(stations_list)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 28,
   "id": "3d0c2951",
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/api/v1.0/tobs\")\n",
    "def tobs():\n",
    "    \"\"\"Return a JSON list of temperature observations for the previous year.\"\"\"\n",
    "\n",
    "    print(\"Received tobs api request.\")\n",
    "\n",
    "    #We find temperature data for the last year.  First we find the last date in the database\n",
    "    final_date_query = session.query(func.max(func.strftime(\"%Y-%m-%d\", Measurement.date))).all()\n",
    "    max_date_string = final_date_query[0][0]\n",
    "    max_date = dt.datetime.strptime(max_date_string, \"%Y-%m-%d\")\n",
    "\n",
    "    #set beginning of search query\n",
    "    begin_date = max_date - dt.timedelta(365)\n",
    "\n",
    "    #get temperature measurements for last year\n",
    "    results = session.query(Measurement).\\\n",
    "        filter(func.strftime(\"%Y-%m-%d\", Measurement.date) >= begin_date).all()\n",
    "\n",
    "    #create list of dictionaries (one for each observation)\n",
    "    tobs_list = []\n",
    "    for result in results:\n",
    "        tobs_dict = {}\n",
    "        tobs_dict[\"date\"] = result.date\n",
    "        tobs_dict[\"station\"] = result.station\n",
    "        tobs_dict[\"tobs\"] = result.tobs\n",
    "        tobs_list.append(tobs_dict)\n",
    "\n",
    "    return jsonify(tobs_list)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 29,
   "id": "09c22967",
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/api/v1.0/<start>\")\n",
    "def start(start):\n",
    "\n",
    "    print(\"Received start date api request.\")\n",
    "\n",
    "    #First we find the last date in the database\n",
    "    final_date_query = session.query(func.max(func.strftime(\"%Y-%m-%d\", Measurement.date))).all()\n",
    "    max_date = final_date_query[0][0]\n",
    "\n",
    "    #get the temperatures\n",
    "    temps = calc_temps(start, max_date)\n",
    "\n",
    "    #create a list\n",
    "    return_list = []\n",
    "    date_dict = {'start_date': start, 'end_date': max_date}\n",
    "    return_list.append(date_dict)\n",
    "    return_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})\n",
    "    return_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})\n",
    "    return_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})\n",
    "\n",
    "    return jsonify(return_list)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 30,
   "id": "064c9cd4",
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/api/v1.0/<start>/<end>\")\n",
    "def start_end(start, end):\n",
    "    \"\"\"Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start\n",
    "    or start-end range.\"\"\"\n",
    "\n",
    "    print(\"Received start date and end date api request.\")\n",
    "\n",
    "    #get the temperatures\n",
    "    temps = calc_temps(start, end)\n",
    "\n",
    "    #create a list\n",
    "    return_list = []\n",
    "    date_dict = {'start_date': start, 'end_date': end}\n",
    "    return_list.append(date_dict)\n",
    "    return_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})\n",
    "    return_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})\n",
    "    return_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})\n",
    "\n",
    "    return jsonify(return_list)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 31,
   "id": "d2309141",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      " * Serving Flask app \"__main__\" (lazy loading)\n",
      " * Environment: production\n",
      "   WARNING: This is a development server. Do not use it in a production deployment.\n",
      "   Use a production WSGI server instead.\n",
      " * Debug mode: on\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      " * Restarting with stat\n"
     ]
    },
    {
     "ename": "SystemExit",
     "evalue": "1",
     "output_type": "error",
     "traceback": [
      "An exception has occurred, use %tb to see the full traceback.\n",
      "\u001b[1;31mSystemExit\u001b[0m\u001b[1;31m:\u001b[0m 1\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "c:\\users\\mbradber\\anaconda3\\envs\\venv\\lib\\site-packages\\IPython\\core\\interactiveshell.py:3351: UserWarning: To exit: use 'exit', 'quit', or Ctrl-D.\n",
      "  warn(\"To exit: use 'exit', 'quit', or Ctrl-D.\", stacklevel=1)\n"
     ]
    }
   ],
   "source": [
    "if __name__ == \"__main__\":\n",
    "    app.run(debug = True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "626d0bba",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {},
 "nbformat": 4,
 "nbformat_minor": 5
}
