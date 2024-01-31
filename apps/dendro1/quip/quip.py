#!/usr/bin/env python


import json
from dendro.sdk import (
    ProcessorBase,
    InputFile,
    OutputFolder,
)
from dendro.sdk import BaseModel, Field


class QuipContext(BaseModel):
    input: InputFile = Field(description="Input .nwb file")
    output: OutputFolder = Field(description="Output .json file")
    electrical_series_path: str = Field(
        description="Path to the electrical series in the NWB file, e.g., /acquisition/ElectricalSeries"
    )


class QuipProcessor(ProcessorBase):
    name = "dendro1.quip"
    description = "Run Quip on an electrophysiology NWB file"
    label = "dendro1.quip"
    tags = []
    attributes = {"wip": True}

    @staticmethod
    def run(context: QuipContext):
        from .NwbRecording import NwbRecording
        import mountainsort5.quip as quip

        print("Creating input recording")
        recording = NwbRecording(
            file=context.input.get_file(),
            electrical_series_path=context.electrical_series_path,
        )

        print("Running Quip")
        quip_output = quip.estimate_units(recording)

        ret = {"type": "quip.estimated_units", "quip_output": quip_output.to_dict()}
        print("Uploading output")
        with open("output.json", "w") as f:
            f.write(json.dumps(ret))
        context.output.upload("output.json")
