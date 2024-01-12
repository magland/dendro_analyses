import dendro.client as den


def main():
    # Load project D-000582
    project = den.load_project("a7852166")
    dandiset_id = "000582"

    # Assemble the nwb file names
    nwb_file_names = []
    dandiset_folder = project.get_folder(f"imported/{dandiset_id}")
    for subdir in dandiset_folder.get_folders():
        for session_nwb in subdir.get_files():
            nwb_file_names.append(session_nwb.file_name)

    for nwb_file_name in nwb_file_names:
        print(f"Submitting job for {nwb_file_name}")
        output_file_name = 'generated' + nwb_file_name[len('imported/'):] + '/tuning_curves_2d.nh5'
        den.submit_job(
            project=project,
            processor_name="dendro1.tuning_curves_2d",
            input_files=[
                den.SubmitJobInputFile(
                    name="input", file_name=nwb_file_name
                )
            ],
            output_files=[
                den.SubmitJobOutputFile(
                    name="output",
                    file_name=output_file_name,
                )
            ],
            parameters=[
                den.SubmitJobParameter(name="num_bins", value=30),
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
