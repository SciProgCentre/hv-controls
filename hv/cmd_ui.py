import cmd, sys
from typing import Optional

from hv.hv_device import HVDevice


class HVShell(cmd.Cmd):
    intro = 'Welcome to the HV-controls shell.\nType help or ? to list commands, and Ctrl+D to exit.\n'
    _empty_promt = '(HV-controls): '
    prompt = _empty_promt

    device : Optional[HVDevice] = None
    devices = []

    def preloop(self) -> None:
        self.devices = HVDevice.find_usb_devices()

    def do_list(self, arg):
        "Print list of all devices."
        for i, dev in enumerate(self.devices):
            print("Device ID: {}".format(i))
            print(dev.device_info())
            print()


    def do_attach(self, arg):
        'Attach to device by ID: attach 0'
        try:
            device_id = int(arg[0])
            if len(self.devices) > device_id:
                self.device = self.devices[device_id]
                self.prompt = '(HV-controls, device {}): '.format(device_id)
                return
        except Exception:
            pass
        finally:
            print("Bad device ID")

    def do_detach(self, arg):
        "Detach device from shell."
        self.device = None
        self.prompt = self._empty_promt

    def do_setup(self, arg):
        'Setup the voltage:  setup 1500'
        try:
            voltage = float(arg[0])
            if self.device is not None:
                pass
        except Exception:
            pass
        finally:
            print("Bad voltage")

    def do_apply(self, arg):
        'Apply the established voltage.'
        pass

    def do_reset(self, arg):
        'Turn off.'
        pass

    def do_get(self, arg):
        "Get voltage and current"
        pass

    def do_eof(self, arg):
        sys.exit(0)

    def precmd(self, line):
        line = line.lower()
        return line

    def close(self):
        pass

    def parse(arg):
        'Convert a series of zero or more numbers to an argument tuple'
        return tuple(map(int, arg.split()))

if __name__ == '__main__':
    HVShell().cmdloop()