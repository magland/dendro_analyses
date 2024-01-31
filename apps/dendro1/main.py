#!/usr/bin/env python


from dendro.sdk import (
    App,
)
from tuning_curves_2d.tuning_curves_2d import TuningCurves2DProcessor
from folder_io.folder_io import (
    CreateSampleFolderProcessor,
    TarProcessor,
    UntarProcessor,
)
from quip.quip import QuipProcessor

app = App(
    name="dendro1",
    description="Miscellaneous dendro processors",
    app_image="ghcr.io/magland/dendro1:latest",
    app_executable="/app/main.py",
)


app.add_processor(TuningCurves2DProcessor)
app.add_processor(CreateSampleFolderProcessor)
app.add_processor(TarProcessor)
app.add_processor(UntarProcessor)
app.add_processor(QuipProcessor)

if __name__ == "__main__":
    app.run()
