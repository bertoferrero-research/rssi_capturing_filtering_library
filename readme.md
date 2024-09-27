# Capture Window

`capture_window` is a Python library designed for capturing and filtering RSSI signals. It is optimized for processing sensor readings, filtering them using various methods, and generating fingerprint datasets useful for signal analysis.

This library has been utilized in research for a PhD at the University of Alicante. This study is related to wireless signal capturing and is designed to be flexible and efficient in environments involving multiple sensors.

## Related Paper

This library is related to research paper that is currently under review. Once the paper is published, we will provide a reference and link to it here.

## Features

- Capture RSSI signals and process them in time windows.
- Customizable filtering methods: mean, median, mode, max, min, and Total Signal Strength (TSS).
- Support for multiple sensors and flexible window configurations.
- Generate fingerprints for signal analysis.

## Installation

You can install the library from PyPI using pip:

```bash
pip install capture-window @ git+https://github.com/bertoferrero-research/rssi_capturing_filtering_library@latest
```

## Usage

Here is how you can use the `SignalCaptureWindow` class to capture and filter RSSI signals:

### Offline Fingerprinting Example - Processing Stored Readings


```python
from capture_window import SignalCaptureWindow

# List of sensor MAC addresses
mac_list = ['00:11:22:33:44:55', '66:77:88:99:AA:BB']

# Window configuration settings
window_configuration_settings_row = {
    'parameters': {
        'def_min_window_size': 5.0,
        'def_max_window_size': 30.0,
        'def_min_entries_per_sensor': 3,
        'def_min_valid_sensors': 2,
        'def_invalid_sensor_value': 100,
        'def_sensor_filtering_tipe': 'mean'
    }
}

# Raw input data (sensor readings)
raw_input_data = [
    {'timestamp': 1, 'station_mac': '00:11:22:33:44:55', 'rssi': -65, 'position_x': 0, 'position_y': 0},
    {'timestamp': 2, 'station_mac': '00:11:22:33:44:55', 'rssi': -70, 'position_x': 0, 'position_y': 1},
    {'timestamp': 2, 'station_mac': '66:77:88:99:AA:BB', 'rssi': -80, 'position_x': 1, 'position_y': 0}
    # more readings...
]

# Initialize the capture window
window_capture = SignalCaptureWindow(
    sensor_mac_list=mac_list,
    min_window_size=window_configuration_settings_row['parameters']['def_min_window_size'],
    max_window_size=window_configuration_settings_row['parameters']['def_max_window_size'],
    min_entries_per_sensor=window_configuration_settings_row['parameters']['def_min_entries_per_sensor'],
    min_valid_sensors=window_configuration_settings_row['parameters']['def_min_valid_sensors'],
    invalid_sensor_value=window_configuration_settings_row['parameters']['def_invalid_sensor_value'],
    filter_method=window_configuration_settings_row['parameters']['def_sensor_filtering_tipe']
)

# Process the readings and generate a fingerprint
fingerprint = window_capture.process_readings(
    readings=raw_input_data,
    timestamp_head="timestamp",
    mac_sensor_head="station_mac",
    rssi_head="rssi",
    aggregate_data_heads=["position_x", "position_y"],
    reset_readings_stack=True
)

print(fingerprint)
```

### Online Fingerprinting Example - Processing Individual Readings in Real-Time

```python
from capture_window import SignalCaptureWindow

# List of sensor MAC addresses
mac_list = ['00:11:22:33:44:55', '66:77:88:99:AA:BB']

# Window configuration settings
window_configuration_settings_row = {
    'parameters': {
        'def_min_window_size': 5.0,  # Minimum window size in seconds
        'def_max_window_size': 30.0,  # Maximum window size in seconds
        'def_min_entries_per_sensor': 3,  # Minimum number of readings per sensor
        'def_min_valid_sensors': 2,  # Minimum number of valid sensors
        'def_invalid_sensor_value': 100,  # Value for invalid sensor readings
        'def_sensor_filtering_tipe': 'mean'  # Filtering method (mean, median, mode, etc.)
    }
}

# Initialize the capture window
window_capture = SignalCaptureWindow(
    sensor_mac_list=mac_list,
    min_window_size=window_configuration_settings_row['parameters']['def_min_window_size'],
    max_window_size=window_configuration_settings_row['parameters']['def_max_window_size'],
    min_entries_per_sensor=window_configuration_settings_row['parameters']['def_min_entries_per_sensor'],
    min_valid_sensors=window_configuration_settings_row['parameters']['def_min_valid_sensors'],
    invalid_sensor_value=window_configuration_settings_row['parameters']['def_invalid_sensor_value'],
    filter_method=window_configuration_settings_row['parameters']['def_sensor_filtering_tipe']
)

# Simulating real-time data reception
live_readings = [
    {'timestamp': 1, 'station_mac': '00:11:22:33:44:55', 'rssi': -65},
    {'timestamp': 2, 'station_mac': '00:11:22:33:44:55', 'rssi': -70}
    # Simulating more live readings...
]

# Process each reading as it is received
for reading in live_readings:
    # Process each individual reading and check if a valid fingerprint is generated
    fingerprint = window_capture.process_reading(
        timestamp=reading['timestamp'],
        mac_sensor=reading['station_mac'],
        rssi=reading['rssi']
    )
    
    # If the fingerprint is valid, print it
    if fingerprint is not None:
        print(f"Fingerprint generated at timestamp {reading['timestamp']}: {fingerprint}")
    else:
        print(f"Reading at timestamp {reading['timestamp']} did not generate a valid fingerprint.")
```

### Parameters of the Class `SignalCaptureWindow`

- `sensor_mac_list`: List of sensor MAC addresses to be used.
- `min_window_size`: Minimum size of the time window in seconds.
- `max_window_size`: Maximum size of the time window in seconds.
- `min_entries_per_sensor`: Minimum number of entries required per sensor to be valid.
- `min_valid_sensors`: Minimum number of valid sensors to create a window.
- `filter_method`: The filtering method to be used (see the list of supported methods).
- `invalid_sensor_value`: Value assigned when a sensor reading is invalid.

### `process_readings` Method Parameters

- `readings`: A list of readings where each reading is a dictionary containing data like timestamp, MAC address, and RSSI values.
- `timestamp_head`: The key for the timestamp value in each reading dictionary (default: `"timestamp"`).
- `mac_sensor_head`: The key for the MAC address of the sensor in each reading (default: `"mac_sensor"`).
- `rssi_head`: The key for the RSSI value in each reading (default: `"rssi"`).
- `aggregate_data_heads`: A list of additional keys in the reading dictionaries that contain extra data (e.g., position or metadata) (default: `None`).
- `reset_readings_stack`: A boolean flag that indicates whether to reset the readings stack before and after processing (default: `False`).

### `process_reading` Method Parameters

- `timestamp`: The timestamp of the reading, representing when the data was captured.
- `mac_sensor`: The MAC address of the sensor from which the reading was received.
- `rssi`: The RSSI (Received Signal Strength Indicator) value associated with the reading.
- `aggregate_data` (`dict`, optional): Additional data that should be included in the fingerprint, such as position or metadata (default: `None`).

### Supported Filtering Methods

The `filter_method` parameter supports the following values:

- `mean`: Calculates the average RSSI value.
- `median`: Calculates the median of the RSSI values.
- `mode`: Calculates the mode of the RSSI values.
- `max`: Selects the maximum RSSI value.
- `min`: Selects the minimum RSSI value.
- `tss`: Calculates the Total Signal Strength (TSS) from the RSSI values.


## Contributing

If you'd like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/new-feature`).
3. Make your changes and commit them (`git commit -am 'Add new feature'`).
4. Push to your branch (`git push origin feature/new-feature`).
5. Open a Pull Request on this repository.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](./LICENSE) file for details.


