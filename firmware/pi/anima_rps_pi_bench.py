"""Raspberry Pi serial bench console for the ANIMA RPS controller.

Install pyserial and pass the 3.3 V UART device as the positional argument.
The console sends heartbeats but does not arm, configure or move the robot on startup.
"""
import argparse
import sys
import threading
import time


def console(port):
    import serial

    active = threading.Event()
    active.set()
    lock = threading.Lock()
    with serial.Serial(port, 115200, timeout=0.05, write_timeout=0.2) as device:
        def command(text):
            with lock:
                device.write((text + '\n').encode('ascii'))

        def poll():
            deadline = 0.0
            try:
                while active.is_set():
                    if time.monotonic() >= deadline:
                        command('PING')
                        deadline = time.monotonic() + 0.20
                    response = device.readline().decode('ascii', errors='replace').strip()
                    if response and response != 'PONG':
                        print(response, flush=True)
            except serial.SerialException as error:
                active.clear()
                print(f'Link lost: {error}', file=sys.stderr, flush=True)

        worker = threading.Thread(target=poll, daemon=True)
        worker.start()
        try:
            print('Serial bench console. Start with STATUS. Enter QUIT to stop and exit.')
            while active.is_set():
                text = input('ANIMA> ').strip().upper()
                if text == 'QUIT':
                    break
                if text and len(text) < 90 and text.isascii():
                    command(text)
        except (EOFError, KeyboardInterrupt):
            pass
        finally:
            active.clear()
            worker.join(0.5)
            try:
                command('STOP')
                device.flush()
            except serial.SerialException:
                pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('port', help='3.3 V UART device, such as /dev/ttyUSB0')
    console(parser.parse_args().port)
