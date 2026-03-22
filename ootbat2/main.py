#!/usr/bin/python

import os, re, time, subprocess, shutil
from importlib.resources import files
from playsound3 import playsound

low_battery_setting = 10
path_sysfs_power_supply = '/sys/class/power_supply'


def get_battery_names() -> list[str]:
    return sorted(f for f in os.listdir(path_sysfs_power_supply) if re.match(r'^BAT\d+$', f))


def get_battery_data(battery_names: list[str]) -> dict:
    battery_data = dict()
    for battery_name in battery_names:
        path_battery = os.path.join(path_sysfs_power_supply, battery_name)
        path_battery_capacity = os.path.join(path_battery, 'capacity')
        path_battery_status = os.path.join(path_battery, 'status')
        with open(path_battery_capacity) as f:
            battery_percentage = int(f.read())
        with open(path_battery_status) as f:
            battery_status = f.read().strip()
        battery_data[battery_name] = {
            'percentage': battery_percentage,
            'status': battery_status
        }
    return battery_data


def main():
    battery_names = get_battery_names()
    notify_send_exists = shutil.which('notify-send') is not None
    wav_file_path = str(files('ootbat2').joinpath('OOT_LowHealth.wav'))

    try:
        while True:
            battery_data = get_battery_data(battery_names)
            battery_percentage = sum(battery['percentage'] for battery in battery_data.values())
            battery_statuses = {battery['status'] for battery in battery_data.values()}
            if (battery_percentage < low_battery_setting) and ('Discharging' in battery_statuses):
                if notify_send_exists:
                    subprocess.run(['notify-send', 'ootbat2', 'Low battery, charge me!'])
                playsound(wav_file_path)
            time.sleep(3)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
