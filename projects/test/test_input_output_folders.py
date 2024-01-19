import dendro.client as den


def main():
    project_id = "53812deb"  # test-input-output-folders

    # Load the project
    project = den.load_project(project_id)

    den.submit_job(
        project=project,
        processor_name="dendro1.create_sample_folder",
        input_files=[],
        output_files=[
            den.SubmitJobOutputFile(
                name="output",
                file_name="test/sample_folder",
                is_folder=True
            )
        ],
        parameters=[],
        required_resources=den.DendroJobRequiredResources(
            numCpus=2, numGpus=0, memoryGb=4, timeSec=60 * 60
        ),
        run_method="local",
    )

    den.submit_job(
        project=project,
        processor_name="dendro1.tar",
        input_files=[
            den.SubmitJobInputFile(
                name="input",
                file_name="test/sample_folder",
                is_folder=True
            )
        ],
        output_files=[
            den.SubmitJobOutputFile(
                name="output",
                file_name="test/sample.tar",
            )
        ],
        parameters=[],
        required_resources=den.DendroJobRequiredResources(
            numCpus=2, numGpus=0, memoryGb=4, timeSec=60 * 60
        ),
        run_method="local",
    )

    den.submit_job(
        project=project,
        processor_name="dendro1.untar",
        input_files=[
            den.SubmitJobInputFile(
                name="input",
                file_name="test/sample.tar",
            )
        ],
        output_files=[
            den.SubmitJobOutputFile(
                name="output",
                file_name="test/sample_folder_2",
                is_folder=True
            )
        ],
        parameters=[],
        required_resources=den.DendroJobRequiredResources(
            numCpus=2, numGpus=0, memoryGb=4, timeSec=60 * 60
        ),
        run_method="local",
    )


if __name__ == "__main__":
    main()
