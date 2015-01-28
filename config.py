from glue.config import tool_registry
from glue.qt.widgets import ImageWidget

import sys
sys.path.insert(0,'.')

from galfaglue import loaders
from galfaglue import viewers
from galfaglue import spectra
from galfaglue.plugin import GALFASpectrumTool

try:
    tool_registry.add(GALFASpectrumTool, widget_cls=ImageWidget)
except TypeError:
    tool_registry.add(GALFASpectrumTool, restrict_to=ImageWidget)
