import dendro.client as prc


def main():
    # Load project D-000582
    project = prc.load_project("a7852166")
    dandiset_id = "000582"

    # Select an NWB file
    asset_path = "sub-10073/sub-10073_ses-17010302_behavior+ecephys.nwb"

    prc.submit_job(
        project=project,
        processor_name="dendro1.tuning_curves_2d",
        input_files=[
            prc.SubmitJobInputFile(
                name="input", file_name=f"imported/{dandiset_id}/{asset_path}"
            )
        ],
        output_files=[
            prc.SubmitJobOutputFile(
                name="output",
                file_name=f"generated/{dandiset_id}/{asset_path}/tuning_curves_2d.nh5",
            )
        ],
        parameters=[
            prc.SubmitJobParameter(name="num_bins", value=30),
            prc.SubmitJobParameter(
                name="spatial_series_path",
                value="processing/behavior/Position/SpatialSeriesLED1",
            ),
        ],
        required_resources=prc.DendroJobRequiredResources(
            numCpus=2,
            numGpus=0,
            memoryGb=4,
            timeSec=60 * 60
        ),
        run_method='local'
    )


if __name__ == "__main__":
    main()
