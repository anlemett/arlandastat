import pandas as pd

def get_ddr_stat(csv_input_file):
    df = pd.read_csv(csv_input_file, sep=' ',
                     names = ['endDate', 'number_of_flights', 'arrival_delayed_15_min_flights_number', 'enroute_delayed_15_min_flights_number',
                              'total_departure_delay', 'average_departure_delay', 'total_arrival_delay', 'average_arrival_delay',
                              'total_enroute_delay', 'average_enroute_delay', 'total_add_time_TMA', 'average_add_time'],
                     index_col=[0],
                     dtype={'flightId':int, 'endDate':str, 'endTime':str, 'departure_delay':int, 'arrival_delay':int, 'add_time':int})

    return df


def get_opensky_stat(csv_input_file):
    df = pd.read_csv(csv_input_file, sep=' ',
                     names = ['date', 'number_of_flights', 'number_of_level_flights', 'total_number_of_levels', 'average_number_of_levels',
                            'total_time_on_levels', 'average_time_on_levels', 'total_distance_on_levels', 'average_distance_on_levels'],
                     index_col=[0],
                     dtype={'date':str})

    return df
