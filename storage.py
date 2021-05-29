import json


class DataStorage:
    def __init__(self, path_to_data_file):
        self.json_file_path = path_to_data_file
        self.json_data = None

    def _get_file_content(self):
        try:
            with open(self.json_file_path) as json_file:
                try:
                    self.json_data = json.load(json_file)
                except json.JSONDecodeError:
                    self.json_data = self._init_data_file()
        except FileNotFoundError:
            self.json_data = self._init_data_file()

    def _update_file_content(self):
        with open(self.json_file_path, "w+") as outfile:
            json.dump(self.json_data, outfile)

    def update_distance_table(self, measurement):
        self._get_file_content()
        self.json_data["distance_measurements"].append(measurement)
        self._update_file_content()

    def update_temperature_table(self, measurement):
        self._get_file_content()
        self.json_data["temperature_measurements"].append(measurement)
        self._update_file_content()

    def update_humidity_table(self, measurement):
        self._get_file_content()
        self.json_data["humidity_measurements"].append(measurement)
        self._update_file_content()

    def update_logs_table(self, logs_entry):
        self._get_file_content()
        self.json_data["logs"].append(logs_entry)
        self._update_file_content()

    @staticmethod
    def _init_data_file():
        return {"distance_measurements": [], "temperature_measurements": [], "humidity_measurements": [],
                "logs": []}
