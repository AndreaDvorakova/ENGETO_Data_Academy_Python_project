# ENGETO_Data_Academy_Python_project
Final project for Data Academy in Python

## How to run on streamlit:
https://andreadvorakova-engeto-data-academy-python-proj-main-app-mta5i6.streamlitapp.com/

## How to run on local:

* Open cmd in given folder, create virtualenv (virtualenv venv), then activate the virtualenv (venv\Scripts\activate)
* pip install -r requirements.txt
* streamlit run main_app.py
* To run jupyter notebook, just type jupyter notebook into cmd with within activated virtualenv

Note - data obtained from Engeto data_academy database

# What it is about:

* The app is processing data from the database about the bike rentals in Edinburgh.
* The structure of the site is:

## Homepage - basic info about the app and link to github

## Standard description - collecting subpages about the descriptive analysis

* Identifying the active/nonactive stations. Data is represented by barchart from the most active to the least and grouped separatly for start station and end statio
* Most busy/least busy stations are deducted from the overall sum of rentals/returns in each station
* Potential surplus/shortage of bikes in the stations
* Table representing the distances between the stations
* Rental duration

## Analysis - answering the questions from the task

* Show the progress of the demand in time
* Identify the possible causes of fluctuation
* Find out the effect of weather on the demand for bicycles
* Bike rentals in weekdays
