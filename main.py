import clr  # from pythonnet
import os
import keyboard
import serial
import monotonic

# hardware types for OpenHardawareMonitor API
HARDWARE_TYPES = ['Mainboard',
                  'SuperIO',
                  'CPU',
                  'GpuNvidia',
                  'GpuAti',
                  'TBalancer',
                  'Heatmaster',
                  'HDD']

SESOR_TYPES = ['Voltage',
               'Clock',
               'Temperature',
               'Load',
               'Fan',
               'Flow',
               'Control',
               'Level']


def init_dependency():
    clr.AddReference(os.path.abspath(os.path.dirname(__file__)) + R'\OpenHardwareMonitorLib.dll')
    from OpenHardwareMonitor import Hardware
    hw = Hardware.Computer()
    hw.MainboardEnabled, hw.CPUEnabled, hw.RAMEnabled, hw.GPUEnabled, hw.HDDEnabled = (True, True, True, True, True)
    hw.Open()
    return hw


def parse_sensor(sensor):
    if sensor.Value is not None:
        if sensor.SensorType == SESOR_TYPES.index('Temperature'):
            return {"Name": sensor.Hardware.Name, "Value": sensor.Value,
                    "type": HARDWARE_TYPES[sensor.Hardware.HardwareType]}


def fetch_data(hardware):
    out = []
    for hw in hardware.Hardware:
        hw.Update()
        for sensor in hw.Sensors:
            thing = parse_sensor(sensor)
            if thing is not None:
                out.append(thing)
        for subhw in hw.SubHardware:
            subhw.Update()
            for subsensor in subhw.Sensors:
                thing = parse_sensor(subsensor)
                out.append(thing)
    return out


def main(hardware, COM_number, interval):
    should_close = False
    print('starting updating data and sending to COM ' + str(COM_number) + '\n')
    print('Press enter to stop program')
    hardware = init_dependency()
    prev_time = now_time = 0
    while not should_close:
        now_time = monotonic.time.time()
        if now_time - prev_time > interval:
            data = fetch_data(hardware)

            ser = serial.Serial('COM'+str(COM_number))
            ser.write(str(data[0]['Value']))
            prev_time = now_time
        if keyboard.is_pressed('enter'):
            should_close = True


hw = init_dependency()
main(hw, 4, 1)
