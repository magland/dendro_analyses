#!/usr/bin/env python


import os
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING
from dendro.sdk import App, ProcessorBase, InputFile, OutputFile, OutputFolder, InputFolder
from dendro.sdk import BaseModel, Field
from matplotlib.pylab import f

if TYPE_CHECKING:
    import pynwb

app = App(
    name="dendro1",
    description="Miscellaneous dendro processors",
    app_image="ghcr.io/magland/dendro1:latest",
    app_executable="/app/main.py",
)


class TuningCurves2DContext(BaseModel):
    input: InputFile = Field(description="Input NWB file")
    output: OutputFile = Field(description="Output .nh5 file")
    spatial_series_path: str = Field(
        description="Path to spatial series within NWB file, e.g. 'processing/behavior/Position/SpatialSeriesLED1'"
    )
    units_path: str = Field(
        default="units", description="Path to units within NWB file, default: 'units'"
    )
    num_bins: int = Field(
        description="Number of bins (in one dimension) for tuning curves"
    )


class TuningCurves2DProcessor(ProcessorBase):
    name = "dendro1.tuning_curves_2d"
    description = "Create 2D tuning curves from an NWB file using Pynapple"
    label = "dendro1.tuning_curves_2d"
    tags = ["pynapple", "nwb"]
    attributes = {"wip": True}

    @staticmethod
    def run(context: TuningCurves2DContext):
        import numpy as np
        import pynwb
        import pynapple as nap
        import h5py
        from h5_to_nh5 import h5_to_nh5

        input_file = context.input.get_file()
        input_nwb = pynwb.NWBHDF5IO(file=h5py.File(input_file, "r"), mode="r").read()

        num_bins = context.num_bins
        spatial_series_path = context.spatial_series_path
        units_path = context.units_path

        # Load the spatial series into a pynapple TsdFrame
        spatial_series = _load_nwb_object(input_nwb, spatial_series_path)
        position_over_time = nap.TsdFrame(
            d=spatial_series.data[:],
            t=spatial_series.timestamps[:],
            columns=["x", "y"],
        )

        # Load the unit spike times into a pynapple TsGroup
        units = _load_nwb_object(input_nwb, units_path)
        unit_names = units["unit_name"][:]
        unit_spike_times = units["spike_times"][:]
        spike_times_group = nap.TsGroup(
            {i: unit_spike_times[i] for i in range(len(unit_names))}
        )

        # Compute 2D tuning curves
        rate_maps, position_bins = nap.compute_2d_tuning_curves(
            spike_times_group,
            position_over_time,
            num_bins,
        )

        rate_maps_concat = np.zeros(
            (len(unit_names), num_bins, num_bins), dtype=np.float32
        )
        for i in range(len(unit_names)):
            rate_maps_concat[i, :, :] = rate_maps[i].astype(np.float32)
        x_bin_positions = position_bins[0].astype(np.float32)
        y_bin_positions = position_bins[1].astype(np.float32)

        output_h5_fname = "output.h5"
        with h5py.File(output_h5_fname, "w") as f:
            f.create_dataset("rate_maps", data=rate_maps_concat)
            f.create_dataset("x_bin_positions", data=x_bin_positions)
            f.create_dataset("y_bin_positions", data=y_bin_positions)
            f.attrs["unit_ids"] = [x for x in unit_names]
            f.attrs["type"] = "tuning_curves_2d"
            f.attrs["format_version"] = 1

        output_nh5_fname = "output.nh5"
        h5_to_nh5(output_h5_fname, output_nh5_fname)

        context.output.upload(output_nh5_fname)


class CreateSampleFolderContext(BaseModel):
    output: OutputFolder = Field(description="Output folder")


class CreateSampleFolderProcessor(ProcessorBase):
    name = "dendro1.create_sample_folder"
    description = "Create a sample folder for testing purposes"
    label = "dendro1.create_sample_folder"
    tags = []
    attributes = {"wip": True}

    @staticmethod
    def run(context: CreateSampleFolderContext):
        output = context.output
        with TemporaryDirectory() as tmpdir:
            print(f"Creating sample folder: {tmpdir}")
            fname1 = f"{tmpdir}/file1.txt"
            fname2 = f"{tmpdir}/file2.txt"
            with open(fname1, "w") as f:
                f.write("hello")
            with open(fname2, "w") as f:
                f.write("world")
            print(f"Uploading sample folder: {tmpdir}")
            output.upload(tmpdir)


class TarContext(BaseModel):
    input: InputFolder = Field(description="Input folder")
    output: OutputFile = Field(description="Output .tar file")


class TarProcessor(ProcessorBase):
    name = "dendro1.tar"
    description = "Create a tar file from a folder"
    label = "dendro1.tar"
    tags = []
    attributes = {"wip": True}

    @staticmethod
    def run(context: TarContext):
        import tarfile

        input = context.input
        output = context.output
        print('Downloading input folder')
        input.download('input_folder')
        output_fname = 'output.tar'
        print(f'Creating tar file: {output_fname}')
        with tarfile.open(output_fname, "w") as tar:
            # add each of the files and directories inside input_folder
            for name in os.listdir("input_folder"):
                tar.add(f"input_folder/{name}", arcname=name)
        print(f'Uploading tar file: {output_fname}')
        output.upload(output_fname)


class UntarContext(BaseModel):
    input: InputFile = Field(description="Input .tar file")
    output: OutputFolder = Field(description="Output folder")


class UntarProcessor(ProcessorBase):
    name = "dendro1.untar"
    description = "Extract a tar file into a folder"
    label = "dendro1.untar"
    tags = []
    attributes = {"wip": True}

    @staticmethod
    def run(context: UntarContext):
        import tarfile

        input = context.input
        output = context.output
        print('Downloading input tar file')
        input.download('input.tar')
        output_folder = 'output_folder'
        print('Extracting tar file: input.tar')
        with tarfile.open('input.tar', "r") as tar:
            tar.extractall(output_folder)
        print(f'Uploading output folder: {output_folder}')
        output.upload(output_folder)


def _load_nwb_object(nwbfile: "pynwb.NWBFile", path: str):
    """
    Load an object from an NWB file given its path.
    """
    path_parts = path.split("/")
    obj = nwbfile
    for i, part in enumerate(path_parts):
        if i == 0:
            if part == "processing":
                obj = obj.processing
                continue
            elif part == "units":
                obj = obj.units
                continue
        obj = obj[part]
    return obj


app.add_processor(TuningCurves2DProcessor)
app.add_processor(CreateSampleFolderProcessor)
app.add_processor(TarProcessor)
app.add_processor(UntarProcessor)

if __name__ == "__main__":
    app.run()
