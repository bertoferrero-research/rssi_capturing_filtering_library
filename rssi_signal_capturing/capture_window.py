import math
from typing import Any, Dict, List, Optional

import numpy as np
from scipy import stats


class SignalCaptureWindow:

    def __init__(self, sensor_mac_list: str, min_window_size: float, max_window_size: float, min_entries_per_sensor: int, min_valid_sensors: int, filter_method: str, invalid_sensor_value: int = 100):
        """
        Initialize a CaptureWindow object.

        Args:
            sensor_mac_list (str): A string containing the list of sensor MAC addresses.
            min_window_size (float): The minimum size of the window in seconds.
            max_window_size (float): The maximum size of the window in seconds.
            min_entries_per_sensor (int): The minimum number of entries required for a valid sensor.
            min_valid_sensors (int): The minimum number of valid sensors required for a valid window.
            filter_method (str): The method used for filtering the window.
            invalid_sensor_value (int, optional): The value used to represent invalid sensor readings. Defaults to 100.
        """

        # Assign properties
        self._sensor_mac_list = sensor_mac_list
        self._min_window_size = min_window_size
        self._max_window_size = max_window_size
        self._min_entries_per_sensor = min_entries_per_sensor
        self._min_valid_sensors = min_valid_sensors
        self._filter_method = filter_method
        self._invalid_sensor_value = invalid_sensor_value

        # Initialize buffer
        self._readings_stack = []

    def process_reading(self, timestamp: float, mac_sensor:str, rssi: int, aggregate_data: dict = None) -> Optional[dict]:
            """
            Process a reading and return the fingerprint data if the capture window is valid.

            Args:
                timestamp (float): The timestamp of the reading.
                mac_sensor (str): The MAC address of the sensor.
                rssi (int): The RSSI value of the reading.
                aggregate_data (dict, optional): Extra data to be included in the fingerprint. Defaults to None.

            Returns:
                Optional[dict]: The fingerprint data as a dictionary, or None if the capture window is not valid.
            """
            
            # Create the data row and append it to the data buffer
            reading_row = {
                'timestamp': timestamp,
                'mac_sensor': mac_sensor,
                'rssi': rssi
            }
            self._readings_stack.append(reading_row)

            # Remove old readings
            while len(self._readings_stack) > 0 and timestamp - self._readings_stack[0]['timestamp'] > self._max_window_size:
                self._readings_stack.pop(0)

            # Check if the capture window is valid
            if not self.check_valid_window(timestamp=timestamp):
                return None
            
            # Compose the fingerprint getting first a copy from the stack and cleaning it
            readings_stack = list(self._readings_stack)
            self._readings_stack = []
            fingerprint = self.compose_fingerprint_data(readings_stack=readings_stack)

            #Aggregate the timestamp
            fingerprint['timestamp'] = timestamp

            # Append extra data if it is provided
            if aggregate_data is not None:
                fingerprint = {**aggregate_data, **fingerprint}

            return fingerprint
        
    def check_valid_window(self, timestamp: float) -> bool:
        """
        Check if the window is valid based on the given timestamp.

        Args:
            timestamp (float): The timestamp to check against.

        Returns:
            bool: True if the window is valid, False otherwise.
        """
        # check minimal length
        if not (len(self._readings_stack) > 0 and timestamp - self._readings_stack[0]['timestamp'] >= self._min_window_size):
            return False

        # Check how many valid sensors are in the pool. To do this, we need to count how many sensors have at least x entries (according to the configuration)
        valid_sensors = 0
        for sensor_mac in self._sensor_mac_list:
            if len(list(filter(lambda x: x['mac_sensor'] == sensor_mac, self._readings_stack))) >= self._min_entries_per_sensor:
                valid_sensors += 1
        # If there are not enough valid sensors, continue
        if valid_sensors < self._min_valid_sensors:
            return False

        # All covered
        return True
    
    def compose_fingerprint_data(self, readings_stack: list) -> dict:
        """
        Composes the fingerprint data based on the sensor readings and the specified filter method.

        Returns:
            A dictionary containing the composed fingerprint data, where the keys are the sensor MAC addresses
            and the values are the filtered RSSI values.

        Raises:
            Exception: If an invalid filtering type is specified.
        """
        fingerprint = {}
        for sensor_mac in self._sensor_mac_list:
            # Get the sensor readings
            sensor_readings = list(filter(lambda x: x['mac_sensor'] == sensor_mac, readings_stack))
            # Check if the sensor is valid
            if len(sensor_readings) >= self._min_entries_per_sensor:
                # If it's valid, apply the filter
                if self._filter_method == 'mean':
                    fingerprint[sensor_mac] = math.floor(np.mean(list(map(lambda x: x['rssi'], sensor_readings))))
                elif self._filter_method == 'median':
                    fingerprint[sensor_mac] = math.floor(np.median(list(map(lambda x: x['rssi'], sensor_readings))))
                elif self._filter_method == 'mode':
                    fingerprint[sensor_mac] = math.floor(stats.mode(list(map(lambda x: x['rssi'], sensor_readings)))[0])
                elif self._filter_method == 'max':
                    fingerprint[sensor_mac] = math.floor(np.max(list(map(lambda x: x['rssi'], sensor_readings))))
                elif self._filter_method == 'min':
                    fingerprint[sensor_mac] = math.floor(np.min(list(map(lambda x: x['rssi'], sensor_readings))))
                elif self._filter_method == 'tss':
                    fingerprint[sensor_mac] = np.sum(list(map(lambda x: 10**(x['rssi']/10), sensor_readings)))
                else:
                    raise Exception('Invalid filtering type')
            else:
                # If it's not valid, assign the invalid value
                fingerprint[sensor_mac] = self._invalid_sensor_value

        return fingerprint
    
    def process_readings(self, readings: List[Dict[str, Any]], timestamp_head: str = "timestamp", mac_sensor_head: str = "mac_sensor", rssi_head: str = "rssi", aggregate_data_heads: list = [], reset_readings_stack: bool = False) -> List[Dict[str, Any]]:
            """
            Process a list of readings and return a list of fingerprints.

            Args:
                readings (List[Dict[str, Any]]): A list of readings, where each reading is a dictionary.
                timestamp_head (str, optional): The key for the timestamp value in each reading dictionary. Defaults to "timestamp".
                mac_sensor_head (str, optional): The key for the mac_sensor value in each reading dictionary. Defaults to "mac_sensor".
                rssi_head (str, optional): The key for the rssi value in each reading dictionary. Defaults to "rssi".
                aggregate_data_heads (list, optional): A list of keys for additional aggregate data in each reading dictionary. Defaults to [].
                reset_readings_stack (bool, optional): Whether to reset the readings stack. Defaults to False.

            Returns:
                List[Dict[str, Any]]: A list of fingerprints, where each fingerprint is a dictionary.
            """
            # Reset the stack if it is required
            if reset_readings_stack:
                self._readings_stack = []
            
            # Initialize the fingerprint
            fingerprints = []

            # Iterate over each reading
            for reading in readings:

                # Extract information from the reading
                timestamp = reading[timestamp_head]
                mac_sensor = reading[mac_sensor_head]
                rssi = reading[rssi_head]
                aggregate_data = None
                if len(aggregate_data_heads) > 0:
                    aggregate_data = {head: reading[head] for head in aggregate_data_heads}

                # Process the individual read
                fingerprint = self.process_reading(timestamp=timestamp, mac_sensor=mac_sensor, rssi=rssi, aggregate_data=aggregate_data)
                if fingerprint is not None:
                    fingerprints.append(fingerprint)

            
            # Reset the stack again if it is required
            if reset_readings_stack:
                self._readings_stack = []

            return fingerprints





