import dendro.client as den


def main():
    project_id = "9638e926"  # D-000129
    dandiset_id = "000129"
    max_iterations = 500  # Max. iterations for the CEBRA model
    timeseries_name = "cursor_pos"  # The name of the timeseries in the nwb file

    # Load the project
    project = den.load_project(project_id)

    nwb_fname = f'imported/{dandiset_id}/sub-Indy/sub-Indy_desc-train_behavior+ecephys.nwb'
    output_model_fname = f'generated/{dandiset_id}/sub-Indy/sub-Indy_desc-train_behavior+ecephys.nh5/cebra_output.model'
    output_fname = f'generated/{dandiset_id}/sub-Indy/sub-Indy_desc-train_behavior+ecephys.nh5/cebra_output.nh5'

    den.submit_job(
        project=project,
        processor_name="cebra1.cebra1_nwb",
        input_files=[den.SubmitJobInputFile(name="input", file_name=nwb_fname)],
        output_files=[
            den.SubmitJobOutputFile(
                name="output",
                file_name=output_fname,
            ),
            den.SubmitJobOutputFile(
                name="output_model",
                file_name=output_model_fname,
            )
        ],
        parameters=[
            den.SubmitJobParameter(name="max_iterations", value=max_iterations),
            den.SubmitJobParameter(name="timeseries_name", value=timeseries_name)
        ],
        required_resources=den.DendroJobRequiredResources(
            numCpus=4, numGpus=0, memoryGb=12, timeSec=60 * 60
        ),
        run_method="aws_batch",
    )


if __name__ == "__main__":
    main()
