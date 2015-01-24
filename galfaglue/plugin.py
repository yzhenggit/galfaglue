import os
import numpy as np

from glue.plugins.tools.spectrum_tool import SpectrumTool
from glue.qt.mouse_mode import RoiMode
from glue.qt import qt_roi
from glue.external.qt.QtGui import QIcon

from galfaglue.spectra import onoff

ICON = QIcon(os.path.join(os.path.dirname(__file__), 'galfa_spectrum.png'))


class GALFASpectrumExtractorMode(RoiMode):

    persistent = True

    def __init__(self, axes, **kwargs):
        super(GALFASpectrumExtractorMode, self).__init__(axes, **kwargs)
        self.icon = ICON
        self.mode_id = 'GALFA Spectrum'
        self.action_text = 'GALFA Spectrum'
        self.tool_tip = 'Extract a spectrum from the selection including background subtraction'
        self._roi_tool = qt_roi.QtRectangularROI(self._axes)
        self._roi_tool.plot_opts.update(edgecolor='#c51b7d',
                                        facecolor=None,
                                        edgewidth=3,
                                        alpha=1.0)


class GALFASpectrumTool(SpectrumTool):

    def _update_from_roi(self, roi):
        x, y = onoff(self.data, self.client.display_attribute, roi)
        self._set_profile(x, y)

    def _setup_mouse_mode(self):
        # This will be added to the ImageWidget's toolbar
        mode = GALFASpectrumExtractorMode(self.image_widget.client.axes,
                                          release_callback=self._update_profile)
        return mode
