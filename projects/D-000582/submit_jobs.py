import dendro.client as den


###################################################################################################
# Created: 2024-01-12 by Jeremy Magland
#
# This script submits jobs for all nwb sessions in the project
#
###################################################################################################


def main():
    project_id = "a7852166"  # D-000582
    dandiset_id = "000582"
    num_bins = 30  # The number of bins for the tuning curves

    # Load the project
    project = den.load_project(project_id)

    # Assemble the nwb file names
    nwb_file_names = []
    dandiset_folder = project.get_folder(f"imported/{dandiset_id}")
    for subdir in dandiset_folder.get_folders():
        for session_nwb in subdir.get_files():
            if session_nwb.file_name.endswith(".nwb"):
                nwb_file_names.append(session_nwb.file_name)

    # Loop through the nwb file names and submit a job for each one
    for nwb_file_name in nwb_file_names:
        print(f"Submitting job for {nwb_file_name}")
        output_file_name = (
            "generated" + nwb_file_name[len("imported/"):] + "/tuning_curves_2d.nh5"
        )
        den.submit_job(
            project=project,
            processor_name="dendro1.tuning_curves_2d",
            input_files=[den.SubmitJobInputFile(name="input", file_name=nwb_file_name)],
            output_files=[
                den.SubmitJobOutputFile(
                    name="output",
                    file_name=output_file_name,
                )
            ],
            parameters=[
                den.SubmitJobParameter(name="num_bins", value=num_bins),
                den.SubmitJobParameter(
                    name="spatial_series_path",
                    value="processing/behavior/Position/SpatialSeriesLED1",
                ),
            ],
            required_resources=den.DendroJobRequiredResources(
                numCpus=2, numGpus=0, memoryGb=4, timeSec=60 * 60
            ),
            run_method="local",
        )


if __name__ == "__main__":
    main()
