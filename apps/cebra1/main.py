#!/usr/bin/env python


from dendro.sdk import App, ProcessorBase, InputFile, OutputFile
from dendro.sdk import BaseModel, Field


app = App(
    name="cebra1",
    description="Cebra processors",
    app_image="ghcr.io/magland/cebra1:latest",
    app_executable="/app/main.py",
)


class Cebra1NwbContext(BaseModel):
    input: InputFile = Field(description="Input NWB file")
    output: OutputFile = Field(description="Output .nh5 file")
    output_model: OutputFile = Field(description="Output .model file")
    timeseries_name: str = Field(description="Timeseries name, e.g. cursor_pos")
    max_iterations: int = Field(description="Max iterations")


class Cebra1NwbProcessor(ProcessorBase):
    name = "cebra1.cebra1_nwb"
    description = "Fit a CEBRA model to data in an NWB file"
    label = "cebra1.cebra1_nwb"
    tags = ["cebra", "nwb"]
    attributes = {"wip": True}

    @staticmethod
    def run(context: Cebra1NwbContext):
        import numpy as np
        import pynwb
        import h5py
        from nlb_tools.nwb_interface import NWBDataset
        import cebra
        from nh5 import h5_to_nh5

        input_file = context.input.get_file()
        input_nwb = pynwb.NWBHDF5IO(file=h5py.File(input_file, "r"), mode="r").read()

        max_iterations = context.max_iterations
        timeseries_name = context.timeseries_name

        # From https://stes.io/NeuroDataReHack2023/
        class Dataset(NWBDataset):

            def __init__(self, nwbfile):

                super().__init__(nwbfile, "*train", split_heldout=False)
                # To make computations faster, we will bin the whole dataset into 20ms bins
                self.resample(target_bin=20)

                for signal_type in set(self.data.columns.get_level_values(level=0)):
                    print(signal_type, self.data[signal_type].shape)
                    setattr(self, signal_type, self.data[signal_type].values)

                values = [tuple(v) for v in self.target_pos]
                unique_values = list(sorted(set([v for v in values if not np.isnan(v).any()])))
                self.target_pos_idx = np.array([-1 if np.isnan(v).any() else unique_values.index(v) for v in values], dtype=int)
        
        print('Loading dataset...')
        dataset = Dataset(input_nwb)
        timeseries = getattr(dataset, timeseries_name)

        model = cebra.CEBRA(
            # Our selected model will use 10 time bins (200ms) as its input
            model_architecture="offset10-model",

            # We will use mini-batches of size 1000 for optimization. You should
            # generally pick a number greater than 512, and larger values (if they
            # fit into memory) are generally better.
            batch_size=1000,

            # This is the number of steps to train. I ran an example with 10_000
            # which resulted in a usable embedding, but training longer might further
            # improve the results
            max_iterations=max_iterations,

            # This will be the number of output features. The optimal number depends
            # on the complexity of the dataset.
            output_dimension=8,

            # If you want to see a progress bar during training, specify this
            verbose=True

            # There are many more parameters to explore. Head to
            # https://cebra.ai/docs/api/sklearn/cebra.html to explore them.
        )

        print('Fitting model...')
        is_nan = np.isnan(dataset.spikes).any(axis=1)
        model.fit(
            dataset.spikes[~is_nan],
            timeseries[~is_nan]
        )

        print('Computing embedding...')
        # NOTE: we are going to need to worry about the NaNs here
        embedding = model.transform(dataset.spikes[~is_nan])

        output_h5_fname = "output.h5"
        with h5py.File(output_h5_fname, "w") as f:
            f.create_dataset("embedding", data=embedding.astype(np.float32))
            f.create_dataset("series/cursor_pos", data=timeseries[~is_nan].astype(np.float32))
            f.attrs["type"] = "cebra_output"
            f.attrs["format_version"] = 1

        output_nh5_fname = "output.nh5"
        h5_to_nh5(output_h5_fname, output_nh5_fname)

        context.output.upload(output_nh5_fname)


app.add_processor(Cebra1NwbProcessor)

if __name__ == "__main__":
    app.run()
