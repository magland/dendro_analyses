#!/usr/bin/env python


import os
from tempfile import TemporaryDirectory
from dendro.sdk import (
    ProcessorBase,
    InputFile,
    OutputFile,
    OutputFolder,
    InputFolder,
)
from dendro.sdk import BaseModel, Field


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
        print("Downloading input folder")
        input.download("input_folder")
        output_fname = "output.tar"
        print(f"Creating tar file: {output_fname}")
        with tarfile.open(output_fname, "w") as tar:
            # add each of the files and directories inside input_folder
            for name in os.listdir("input_folder"):
                tar.add(f"input_folder/{name}", arcname=name)
        print(f"Uploading tar file: {output_fname}")
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
        print("Downloading input tar file")
        input.download("input.tar")
        output_folder = "output_folder"
        print("Extracting tar file: input.tar")
        with tarfile.open("input.tar", "r") as tar:
            tar.extractall(output_folder)
        print(f"Uploading output folder: {output_folder}")
        output.upload(output_folder)
