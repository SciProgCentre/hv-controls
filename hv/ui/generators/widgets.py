from hv.ui.regulator import HVRegulator


def add_voltage_current_controls(parent, layout, generator):
    data = generator.device.data
    min_voltage_input = HVRegulator(parent, "Min Voltage, V:", 0.0, generator.parameters.max_voltage,
                                data.voltage_step, generator.parameters.min_voltage)
    max_voltage_input = HVRegulator(parent, "Max Voltage, V:", data.voltage_min, data.voltage_max,
                                data.voltage_step, generator.parameters.max_voltage)

    def min_voltage(x):
        generator.parameters.min_voltage = x

    def max_voltage(x):
        generator.parameters.max_voltage = x
        min_voltage_input.set_maximum(x)

    min_voltage_input.valueChanged.connect(min_voltage)
    max_voltage_input.valueChanged.connect(max_voltage)

    current_input = HVRegulator(parent, "Limiting current, {}:".format(data.resolve_current_label()),
                                data.current_min, data.current_max, data.resolve_current_step(),
                                generator.parameters.current)
    current_input.valueChanged.connect(lambda x: generator.parameters.__setattr__("current", x))
    layout.addWidget(min_voltage_input)
    layout.addWidget(max_voltage_input)
    layout.addWidget(current_input)
    return 0