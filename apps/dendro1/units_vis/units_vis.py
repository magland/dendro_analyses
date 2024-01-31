#!/usr/bin/env python


from typing import Optional
from dendro.sdk import ProcessorBase, InputFile, OutputFile
from dendro.sdk import BaseModel, Field


class UnitsVisContext(BaseModel):
    input: InputFile = Field(description="Input NWB file")
    output: OutputFile = Field(description="Output .figurl file")
    units_path: str = Field(
        default='',
        description="Path to the units table. If empty, uses the default location for NWB files",
    )
    sampling_frequency: Optional[float] = Field(
        default=None,
        description="Sampling frequency. If None, will try to read from the NWB file",
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
        sampling_frequency = context.sampling_frequency

        view = create_units_vis(url, units_path=units_path, sampling_frequency=sampling_frequency)
        figurl = view.url(label="Units visualization")

        output_fname = "output.figurl"
        with open(output_fname, "w") as f:
            f.write(figurl)

        context.output.upload(output_fname)
