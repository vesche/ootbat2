#!/usr/bin/python

import os, re, time, subprocess, shutil, pkg_resources
from playsound import playsound

path_sysfs_power_supply = '/sys/class/power_supply'
path_oot_low_health_wav = pkg_resources.resource_filename(__name__, 'OOT_LowHealth.wav')
low_battery_setting = 10


def get_number_of_batteries() -> int:
    return len([f for f in os.listdir(path_sysfs_power_supply) if re.match(r'^BAT\d+$', f)])


def get_battery_data(number_of_batteries: int) -> dict:
    battery_data = dict()
    for n in range(number_of_batteries):
        battery_name = f'BAT{n}'
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
    number_of_batteries = get_number_of_batteries()
    notify_send_exists = shutil.which('notify-send') is not None
    try:
        while True:
            battery_data = get_battery_data(number_of_batteries)
            battery_percentage = sum(battery['percentage'] for battery in battery_data.values())
            battery_statuses = {battery['status'] for battery in battery_data.values()}
            if (battery_percentage < low_battery_setting) and ('Discharging' in battery_statuses):
                if notify_send_exists:
                    subprocess.run(['notify-send', 'ootbat2', 'Low battery, charge me!'])
                playsound(path_oot_low_health_wav)
            time.sleep(3)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
