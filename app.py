from config import (DEBUG, PORT, HOST,
                    INPUT_DIR, OUTPUT_DIR, OUTPUT_PICTURES_DIR,
                    DDR_M1, DDR_M3, OPENSKY, DDR_M1_M3, DDR_M1_OPENSKY, STAT, FUEL, VFE, VP 
                    )
from config import *
from constants import (TMA_timezone,
                       DDR_M1_PLOT_COLOR, DDR_M3_PLOT_COLOR, OPENSKY_PLOT_COLOR, 
                       DDR_M1_ALTITUDES_COLOR, DDR_M3_ALTITUDES_COLOR, OPENSKY_ALTITUDES_COLOR, OPENSKY_STATES_ALTITUDES_COLOR
                       #TMA_COLOR, RWYS_COLOR, ENTRY_POINTS_COLOR
                       )


import os, glob

from flask import (Flask, render_template, request, redirect, url_for)
import forms

from datetime import datetime, time, timedelta
import pytz

import pandas as pd

import numpy as np

import flight_stat


app = Flask(__name__)

app.config.from_object('config')

if not os.path.exists(INPUT_DIR):
    os.makedirs(INPUT_DIR)
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
if not os.path.exists(OUTPUT_PICTURES_DIR):
    os.makedirs(OUTPUT_PICTURES_DIR)


ddr_stat_by_day_df = flight_stat.get_ddr_stat(os.path.join(INPUT_DIR, STAT_DDR_BY_DAY_CSV))
opensky_stat_by_day_df = flight_stat.get_opensky_stat(os.path.join(INPUT_DIR, STAT_OPENSKY_BY_DAY_CSV))


callsign = ''
in_out = 'all'
date_begin = 0
date_end = 0
date_begin_str = ''
date_end_str = ''
is_ddr_m1 = False
is_ddr_m3 = False
is_opensky = False


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/statistics/', methods=['GET', 'POST'])
def view_statistics_form():
    global ddr_stat_by_day_df
    global opensky_stat_by_day_df
    global date_begin_str, date_end_str

    form = forms.StatForm(request.form)
    if request.method == 'POST' and form.validate():
        date_begin = form.date_begin.data
        date_end = form.date_end.data
        date_begin_str = date_begin.strftime("%y%m%d")
        date_end_str = date_end.strftime("%y%m%d")

        # DDR
        df = ddr_stat_by_day_df[(ddr_stat_by_day_df['endDate'] >= date_begin_str) & (ddr_stat_by_day_df['endDate'] <= date_end_str)]
        
        ddr_number_of_days = len(df)
        
        ddr_number_of_flights = int(np.sum(df['number_of_flights']))

        total_arrival_delay_str = ''
        average_arrival_delay_str = ''

        total_departure_delay_str = ''
        average_departure_delay_str = ''

        kpi14_1b_str = ''
        kpi14_2b_str = ''

        if ddr_number_of_flights != 0:

            total_arrival_delay = int(np.sum(df['total_arrival_delay']))
            average_arrival_delay = total_arrival_delay/ddr_number_of_flights

            total_arrival_delay_str = str(timedelta(seconds=total_arrival_delay))
            average_arrival_delay_str  = "{0:.1f}".format(average_arrival_delay/60)

            #arrival_delayed_5_min_flights_number = int(np.sum(df['arrival_delayed_5_min_flights_number']))
            #kpi14_1b = (ddr_number_of_flights - arrival_delayed_5_min_flights_number)/ddr_number_of_flights*100
            #kpi14_1b_str = "{0:.1f}".format(kpi14_1b)

            arrival_delayed_15_min_flights_number = int(np.sum(df['arrival_delayed_15_min_flights_number']))
            kpi14_2b = (ddr_number_of_flights - arrival_delayed_15_min_flights_number)/ddr_number_of_flights*100
            kpi14_2b_str = "{0:.1f}".format(kpi14_2b)

            total_departure_delay = int(np.sum(df['total_departure_delay']))
            average_departure_delay = total_departure_delay/ddr_number_of_flights

            total_departure_delay_str =  str(timedelta(seconds=total_departure_delay))
            average_departure_delay_str = "{0:.1f}".format(average_departure_delay/60)

            sum_average_add_time = int(np.sum(df['average_add_time']))
            average_add_time = sum_average_add_time/ddr_number_of_days

            average_add_time_str = "{0:.1f}".format(average_add_time/60)


        # OPENSKY
        df = opensky_stat_by_day_df[(opensky_stat_by_day_df['date'] >= date_begin_str) & (opensky_stat_by_day_df['date'] <= date_end_str)]
        
        opensky_number_of_days = len(df)
        
        opensky_number_of_flights = int(np.sum(df['number_of_flights']))
        
        perc_level_flights_str = ''
        average_number_of_levels_str = ''
        average_distance_flown_level_str = ''
        average_time_flown_level_str = ''

        if opensky_number_of_flights != 0:
            
            sum_of_flights = np.sum(df['number_of_flights'])
            sum_of_level_flights = np.sum(df['number_of_level_flights'])
            perc_level_flights = sum_of_level_flights/sum_of_flights*100
            perc_level_flights_str = "{0:.1f}".format(perc_level_flights)
            
            sum_of_average_number_of_levels = np.sum(df['average_number_of_levels'])
            average_number_of_levels = sum_of_average_number_of_levels/opensky_number_of_days
            average_number_of_levels_str = "{0:.1f}".format(average_number_of_levels)
            
            sum_of_average_distance_flown_level = np.sum(df['average_distance_on_levels'])
            average_distance_flown_level = sum_of_average_distance_flown_level/opensky_number_of_days            
            average_distance_flown_level_str = "{0:.1f}".format(average_distance_flown_level)

            sum_of_average_time_flown_level = np.sum(df['average_time_on_levels'])
            average_time_flown_level = sum_of_average_time_flown_level/opensky_number_of_days
            average_time_flown_level_str  = "{0:.1f}".format(average_time_flown_level)

        return render_template('statistics.html', date_begin = date_begin, date_end = date_end,
                                ddr_number_of_flights = ddr_number_of_flights,
                                total_arrival_delay = total_arrival_delay_str, average_arrival_delay = average_arrival_delay_str,
                                kpi14_2b = kpi14_2b_str,
                                total_departure_delay = total_departure_delay_str,
                                average_departure_delay = average_departure_delay_str,
                                average_add_time_in_TMA = average_add_time_str,
                                opensky_number_of_flights = opensky_number_of_flights, P = perc_level_flights_str, 
                                L_avg = average_number_of_levels_str, D_avg = average_distance_flown_level_str,
                                T_avg = average_time_flown_level_str                                
                                )

    return render_template('form_statistics.html', form=form)


# No caching at all for API endpoints (to update pictures)
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'public, no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


if __name__ == '__main__':
    app.run(debug=DEBUG, host=HOST, port=PORT)
