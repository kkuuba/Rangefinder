import RPi.GPIO as GPIO
import Adafruit_DHT
import threading
import time
from datetime import datetime
from storage import DataStorage


class Sensors:

    def __init__(self, camera_object):
        self.gpio_trigger = 18
        self.gpio_echo = 24
        self.gpio_temp = 17
        self.dht11_sensor = None
        self.camera_obj = camera_object
        self.temperature = 22
        self.info_str = "Temp. {} deg                       {}m                      Humidity: {}%\n\n\n\n\n\n\n+"
        self.humidity = None
        self.distance = None
        self.sensor_measurements = DataStorage("data.json")
        self.threads = []
        self.prepare_gpio_ports()
        self.start_sensor_agent()

    def start_sensor_agent(self):
        self.threads.append(threading.Thread(target=self.update_distance_temp_and_humidity, args=[]))
        self.threads[-1].daemon = True
        self.threads[-1].start()
        self._wait_for_sensors_measure()

    def update_distance_temp_and_humidity(self):
        while True:
            self._get_temperature_and_humidity()
            self._calculate_distance_based_on_temperature()
            self._validate_distance_measurement()
            self.camera_obj.annotate_text = self.info_str.format(self.temperature, str(round(self.distance) / 100),
                                                                 self.humidity)

    def prepare_gpio_ports(self):
        self.dht11_sensor = Adafruit_DHT.DHT11
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_trigger, GPIO.OUT)
        GPIO.setup(self.gpio_echo, GPIO.IN)

    def _get_echo_time_from_hcsr04(self):
        GPIO.output(self.gpio_trigger, True)
        time.sleep(0.00001)
        GPIO.output(self.gpio_trigger, False)

        start_time = time.time()
        stop_time = time.time()
        while GPIO.input(self.gpio_echo) == 0:
            start_time = time.time()

        while GPIO.input(self.gpio_echo) == 1:
            stop_time = time.time()

        return stop_time - start_time

    def _get_temperature_and_humidity(self):
        self.humidity, self.temperature = Adafruit_DHT.read_retry(self.dht11_sensor, self.gpio_temp)
        self.sensor_measurements.update_temperature_table(self.temperature)
        self.sensor_measurements.update_humidity_table(self.humidity)

    def _calculate_distance_based_on_temperature(self):
        sound_speed = 331.5 + 0.6 * self.temperature
        self.distance = ((sound_speed * 100) * self._get_echo_time_from_hcsr04()) / 2

    def _validate_distance_measurement(self):
        if self.distance < 15:
            self.distance = self.sensor_measurements.json_data["distance_measurements"][-1]
            self.sensor_measurements.update_logs_table(
                {str(datetime.now()): "distance measurement disturbed (result < 20 cm)"})
        else:
            self.sensor_measurements.update_distance_table(self.distance)

    def _wait_for_sensors_measure(self):
        measurements_ongoing = True
        timer = 0
        while measurements_ongoing or timer > 20:
            time.sleep(1)
            if self.temperature and self.distance and self.humidity:
                measurements_ongoing = False
            else:
                timer = timer + 1
