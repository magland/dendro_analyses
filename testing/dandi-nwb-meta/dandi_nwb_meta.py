import os
import dandi.dandiarchive as da
import json
import h5py
from typing import List
from typing import Union
from pydantic import BaseModel, Field
import numpy as np
import remfile
import gzip


def process_dandiset(dandiset_id: str, output_fname: str):
    if os.path.exists(output_fname):
        if output_fname.endswith(".gz"):
            with open(output_fname, "rb") as f:
                existing = json.loads(gzip.decompress(f.read()))
                existing = DandiNwbMetaDandiset(**existing)
        else:
            with open(output_fname, "r") as f:
                existing = json.load(f)
                existing = DandiNwbMetaDandiset(**existing)
    else:
        existing = None
    parsed_url = da.parse_dandi_url(f"https://dandiarchive.org/dandiset/{dandiset_id}")
    X = DandiNwbMetaDandiset(
        dandiset_id=dandiset_id, dandiset_version="draft", nwb_assets=[]
    )
    with parsed_url.navigate() as (client, dandiset, assets):
        asset_num = 0
        for asset in dandiset.get_assets():
            asset_num += 1
            if asset.path.endswith(".nwb"):
                item = next(
                    (x for x in existing.nwb_assets if x.asset_id == asset.identifier),
                    None,
                ) if existing else None
                if item:
                    print(f"{asset_num}: {X.dandiset_id} | {asset.path} | already processed")
                    X.nwb_assets.append(item)
                    continue
                if os.path.exists(f'cache/{dandiset_id}/{asset.identifier}'):
                    with open(f'cache/{dandiset_id}/{asset.identifier}', 'r') as f:
                        item = json.load(f)
                        item = DandiNwbMetaAsset(**item)
                        print(f"{asset_num}: {X.dandiset_id} | {asset.path} | from cache")
                        X.nwb_assets.append(item)
                        continue
                print(f"{asset_num}: {X.dandiset_id} | {asset.path}")
                A = DandiNwbMetaAsset(
                    asset_id=asset.identifier,
                    asset_path=asset.path,
                    nwb_metadata=DandiNWbMetaAssetNwbMetadata(groups=[], datasets=[]),
                )
                file = remfile.File(asset.download_url, verbose=False)
                with h5py.File(file, "r") as h5_file:
                    all_groups_in_h5_file = _get_h5_groups(h5_file)
                    for group in all_groups_in_h5_file:
                        A.nwb_metadata.groups.append(
                            H5MetadataGroup(
                                path=group.name, attrs=json.loads(_attrs_to_json(group))
                            )
                        )
                    all_datasets_in_h5_file = _get_h5_datasets(h5_file)
                    for dataset in all_datasets_in_h5_file:
                        dtype = _dtype_to_str(dataset)
                        A.nwb_metadata.datasets.append(
                            H5MetadataDataset(
                                path=dataset.name,
                                attrs=json.loads(_attrs_to_json(dataset)),
                                shape=_format_shape(dataset),
                                dtype=dtype,
                            )
                        )
                X.nwb_assets.append(A)
                os.makedirs(f'cache/{dandiset_id}', exist_ok=True)
                with open(f'cache/{dandiset_id}/{asset.identifier}', 'w') as f:
                    json.dump(A.dict(), f, indent=2)
    if output_fname.endswith(".gz"):
        with gzip.open(output_fname, "wb") as f:
            f.write(json.dumps(X.dict()).encode())
    else:
        with open(output_fname, "w") as f:
            json.dump(X.dict(), f, indent=2)


class H5MetadataGroup(BaseModel):
    path: str = Field(description="Path to the group")
    attrs: dict = Field(description="Attributes of the group")


class H5MetadataDataset(BaseModel):
    path: str = Field(description="Path to the dataset")
    attrs: dict = Field(description="Attributes of the dataset")
    shape: list = Field(description="Shape of the dataset")
    dtype: str = Field(description="Data type of the dataset")


class DandiNWbMetaAssetNwbMetadata(BaseModel):
    groups: List[H5MetadataGroup] = Field(description="HDF5 group metadata")
    datasets: List[H5MetadataDataset] = Field(description="HDF5 dataset metadata")


class DandiNwbMetaAsset(BaseModel):
    asset_id: str = Field(description="Asset identifier")
    asset_path: str = Field(description="Asset path")
    nwb_metadata: DandiNWbMetaAssetNwbMetadata = Field(description="NWB metadata")


class DandiNwbMetaDandiset(BaseModel):
    dandiset_id: str = Field(description="Dandiset identifier")
    dandiset_version: str = Field(description="Dandiset version")
    nwb_assets: List[DandiNwbMetaAsset] = Field(description="List of assets")


def _get_h5_groups(h5_file: h5py.File) -> list:
    """Returns a list of all groups in an h5 file.

    Args:
        h5_file (h5py.File): The h5 file.

    Returns:
        list: A list of all groups in the h5 file.
    """
    groups = []

    def _process_node(node: h5py.Group):
        groups.append(node)
        for child in node.values():
            if isinstance(child, h5py.Group):
                _process_node(child)
    _process_node(h5_file)
    return groups


def _get_h5_datasets(h5_file: h5py.File) -> list:
    """Returns a list of all datasets in an h5 file.

    Args:
        h5_file (h5py.File): The h5 file.

    Returns:
        list: A list of all datasets in the h5 file.
    """
    datasets = []

    def _process_node(node: h5py.Group):
        for child in node.values():
            if isinstance(child, h5py.Dataset):
                datasets.append(child)
            elif isinstance(child, h5py.Group):
                _process_node(child)
    _process_node(h5_file)
    return datasets


def _attrs_to_json(group: Union[h5py.Group, h5py.Dataset]) -> str:
    """Converts the attributes of an HDF5 group or dataset to a JSON-serializable format."""
    attrs_dict = {}
    for attr_name in group.attrs:
        value = group.attrs[attr_name]

        # Convert NumPy arrays to lists
        if isinstance(value, np.ndarray):
            value = value.tolist()
        # Handle other non-serializable types as needed
        elif isinstance(value, np.int64):
            value = int(value)
        # Handle References
        elif isinstance(value, h5py.Reference):
            value = str(value)

        # check if json serializable
        try:
            json.dumps(value)
        except TypeError:
            value = "Not JSON serializable"

        attrs_dict[attr_name] = value

    return json.dumps(attrs_dict)


def _dtype_to_str(dataset: h5py.Dataset) -> str:
    """Converts the dtype of an HDF5 dataset to a string."""
    dtype = dataset.dtype
    if dtype == np.dtype("int8"):
        return "int8"
    elif dtype == np.dtype("uint8"):
        return "uint8"
    elif dtype == np.dtype("int16"):
        return "int16"
    elif dtype == np.dtype("uint16"):
        return "uint16"
    elif dtype == np.dtype("int32"):
        return "int32"
    elif dtype == np.dtype("uint32"):
        return "uint32"
    elif dtype == np.dtype("int64"):
        return "int64"
    elif dtype == np.dtype("uint64"):
        return "uint64"
    elif dtype == np.dtype("float32"):
        return "float32"
    elif dtype == np.dtype("float64"):
        return "float64"
    else:
        # raise ValueError(f"Unsupported dtype: {dtype}")
        return "Unsupported dtype"


def _format_shape(dataset: h5py.Dataset) -> list:
    """Formats the shape of an HDF5 dataset to a list."""
    shape = dataset.shape
    return [int(dim) for dim in shape]
