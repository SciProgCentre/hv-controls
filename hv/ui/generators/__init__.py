

from .base import Generator, GeneratorWidget
from .custom import CustomGeneratorWidget, CustomGenerator
from .scanning import ScanningParameters, ScanningGenerator, ScanningWidget
from .square_wave import SquareWave
from .rawtooth import ReversedRawtoothWave
from .stairs import Stairs, StairsWidget

GENERATOR_FACTORY = {
    SquareWave.NAME : lambda parent, device, parameters: ScanningWidget(parent, SquareWave(device, parameters)),
    Stairs.NAME : lambda parent, device, parameters: StairsWidget(parent, Stairs(device, parameters)),
    ReversedRawtoothWave.NAME : lambda parent, device, parameters: ScanningWidget(parent, ReversedRawtoothWave(device, parameters)),
    CustomGenerator.NAME : lambda parent, device, parameters : CustomGeneratorWidget(parent, CustomGenerator(device))
}