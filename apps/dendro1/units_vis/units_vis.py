#!/usr/bin/env python


from dendro.sdk import ProcessorBase, InputFile, OutputFile
from dendro.sdk import BaseModel, Field


class UnitsVisContext(BaseModel):
    input: InputFile = Field(description="Input NWB file")
    output: OutputFile = Field(description="Output .figurl file")
    units_path: str = Field(
        default='',
        description="Path to the units table. If empty, uses the default location for NWB files",
    )


class UnitsVisProcessor(ProcessorBase):
    name = "dendro1.units_vis"
    description = "Create a visualization for the unis in an NWB file"
    label = "dendro1.units_vis"
    tags = ["nwb"]
    attributes = {"wip": True}

    @staticmethod
    def run(context: UnitsVisContext):
        from .create_units_vis import create_units_vis

        url = context.input.get_url()
        units_path = context.units_path if context.units_path else None

        view = create_units_vis(url, units_path=units_path)
        figurl = view.url(label="Units visualization")

        output_fname = "output.figurl"
        with open(output_fname, "w") as f:
            f.write(figurl)

        context.output.upload(output_fname)
