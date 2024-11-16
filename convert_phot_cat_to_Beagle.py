import numpy as np
import os
from astropy.io import fits
from astropy.io.fits.hdu.hdulist import HDUList
from astropy.table import Table
from collections import OrderedDict, defaultdict
import argparse
from enum import Enum


class FitsExt:
    fits = ".fits"
    fits_gz = ".fits.gz"


class ColumnNames:
    name = "name"
    extension = "extension"
    NIRSpec_ID = "NIRSpec_ID"
    NIRCam_ID = "NIRCam_ID"
    error_suffix = "_en"
    TIER = "TIER"
    FLAG = "FLAG"
    SIZE = {extension: "SIZE", name: "FWHM"}
    RA = {extension: "FLAG", name: "RA"}
    DEC = {extension: "FLAG", name: "DEC"}
    ID = "ID"


class PhotometryType:
    name = "name"
    extension = "extension"
    kron = {extension: "KRON_CONV", name: "KRON"}
    circ = {extension: "CIRC_CONV", name: "CIRC2"}


class Tier:
    goods_s_suffix = "_gs"
    goods_s = "GOODS-S"
    goods_s_infix = "goodss."
    goods_n_suffix = "_gn"
    goods_n = "GOODS-N"
    goods_n_infix = "goodsn."


FWHM_CUTOFF = 5.0


class DefaultFilters:
    name = "name"
    label = "label"
    err = "err"

    hst_jwst = [
        {name: "F435W", label: "HST_F435W"},
        {name: "F606W", label: "HST_F606W"},
        {name: "F775W", label: "HST_F775W"},
        {name: "F814W", label: "HST_F814W"},
        {name: "F850LP", label: "HST_F850LP"},
        {name: "F090W", label: "NRC_F090W"},
        {name: "F115W", label: "NRC_F115W"},
        {name: "F150W", label: "NRC_F150W"},
        {name: "F200W", label: "NRC_F200W"},
        {name: "F277W", label: "NRC_F277W"},
        {name: "F335M", label: "NRC_F335M"},
        {name: "F356W", label: "NRC_F356W"},
        {name: "F410M", label: "NRC_F410M"},
        {name: "F444W", label: "NRC_F444W"},
    ]

    extra = [
        "Johnson_U",
        "Johnson_V",
        "MOSFIRE_J",
        "synthetic_u",
        "synthetic_g",
        "synthetic_i",
    ]


def get_tier(tier: str) -> str:
    if tier.endswith(Tier.goods_s_suffix) or Tier.goods_s_suffix + "_" in tier:
        return Tier.goods_s
    elif tier.endswith(Tier.goods_n_suffix) or Tier.goods_n_suffix + "_" in tier:
        return Tier.goods_n
    else:
        raise ValueError(f"Cannot determine tier from {tier}")


def get_value_from_multi_ext_fits(
    cat: HDUList,
    ext: str,
    column: str,
    ID: str | int | None = None,
    ID_column: str = ColumnNames.ID,
) -> float:
    if ID is not None:
        ID = int(ID)
        return cat[ext].data[column][cat[ext].data[ID_column] == ID][0]
    else:
        return cat[ext].data[column]


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--goods-s-catalogue",
        "--goods-s",
        help="Path to the GOODS-S catalogue",
        action="store",
        type=str,
        dest="goods_s",
    )

    parser.add_argument(
        "--goods-n-catalogue",
        "--goods-n",
        help="Path to the GOODS-N catalogue",
        action="store",
        type=str,
        dest="goods_n",
    )

    # The redshift catalogue used in Beagle
    parser.add_argument(
        "--input-catalogue",
        "-i",
        help="Path to the input catalogue",
        action="store",
        type=str,
        dest="input_catalogue",
        required=True,
    )

    # Whether to overwrite the output file if it exists
    parser.add_argument(
        "--overwrite",
        help="Overwrite the output file if it exists",
        action="store_true",
        dest="overwrite",
        default=False,
    )

    args = parser.parse_args()

    input_cat = Table.read(args.input_catalogue)

    phot_cat = {}

    output_cat = defaultdict(list)

    for i, obj in enumerate(input_cat):
        nircam_id = obj[ColumnNames.NIRCam_ID]
        nirspec_id = obj[ColumnNames.NIRSpec_ID]

        if not nircam_id:
            continue

        tier = get_tier(obj[ColumnNames.TIER])

        if tier == Tier.goods_s and Tier.goods_s not in phot_cat:
            if not args.goods_s:
                raise ValueError("GOODS-S catalogue not provided")
            phot_cat[Tier.goods_s] = fits.open(args.goods_s)
        elif tier == Tier.goods_n and Tier.goods_n not in phot_cat:
            if not args.goods_n:
                raise ValueError("GOODS-N catalogue not provided")
            phot_cat[Tier.goods_n] = fits.open(args.goods_n)

        size = get_value_from_multi_ext_fits(
            phot_cat[tier],
            ColumnNames.SIZE[ColumnNames.extension],
            ColumnNames.SIZE[ColumnNames.name],
            nircam_id,
        )
        ra = get_value_from_multi_ext_fits(
            phot_cat[tier],
            ColumnNames.RA[ColumnNames.extension],
            ColumnNames.RA[ColumnNames.name],
            nircam_id,
        )
        dec = get_value_from_multi_ext_fits(
            phot_cat[tier],
            ColumnNames.DEC[ColumnNames.extension],
            ColumnNames.DEC[ColumnNames.name],
            nircam_id,
        )
        print(nircam_id, size)

        output_cat[ColumnNames.NIRCam_ID].append(nircam_id)
        output_cat[ColumnNames.NIRSpec_ID].append(nirspec_id)
        output_cat[ColumnNames.RA[ColumnNames.name]].append(ra)
        output_cat[ColumnNames.DEC[ColumnNames.name]].append(dec)
        output_cat[ColumnNames.SIZE[ColumnNames.name]].append(size)

        row = np.where(
            phot_cat[tier][ColumnNames.FLAG].data[ColumnNames.ID] == nircam_id
        )[0][0]

        if size < FWHM_CUTOFF:
            phot_type = PhotometryType.circ
        else:
            phot_type = PhotometryType.kron

        for filter in DefaultFilters.hst_jwst:
            flag = phot_cat[tier][ColumnNames.FLAG].data[
                filter[DefaultFilters.name] + "_" + ColumnNames.FLAG
            ][row]
            phot_val = phot_cat[tier][phot_type[PhotometryType.extension]].data[
                filter[DefaultFilters.name] + "_" + phot_type[DefaultFilters.name]
            ][row]
            phot_err = phot_cat[tier][phot_type[PhotometryType.extension]].data[
                filter[DefaultFilters.name]
                + "_"
                + phot_type[DefaultFilters.name]
                + ColumnNames.error_suffix
            ][row]
            if flag == 0 and phot_val != 0:
                output_cat[filter[DefaultFilters.label]].append(phot_val)
                output_cat[
                    filter[DefaultFilters.label] + "_" + DefaultFilters.err
                ].append(phot_err)
            else:
                output_cat[filter[DefaultFilters.label]].append(-99)
                output_cat[
                    filter[DefaultFilters.label] + "_" + DefaultFilters.err
                ].append(-99)

        for filter in DefaultFilters.extra:
            output_cat[filter].append(-99)
            output_cat[filter + "_" + DefaultFilters.err].append(-99)

    output_table = Table(output_cat)

    # Extract the file name from the input catalogue path
    input_file_name = os.path.basename(args.input_catalogue)

    # Etract the path from the input catalogue path
    input_path = os.path.dirname(args.input_catalogue)

    # Etract the file name from the photometry catalogue path
    if args.goods_s:
        phot_file_name = os.path.basename(args.goods_s).replace(Tier.goods_s_infix, "")
    elif args.goods_n:
        phot_file_name = os.path.basename(args.goods_n).replace(Tier.goods_n_infix, "")

    output_file_name = (
        f"{remove_fits_ext(input_file_name)}.{remove_fits_ext(phot_file_name)}.fits"
    )

    output_table.write(
        os.path.join(input_path, output_file_name), overwrite=args.overwrite
    )


def remove_fits_ext(file_name: str) -> str:
    if file_name.endswith(FitsExt.fits_gz):
        return file_name.split(FitsExt.fits_gz)[0]
    elif file_name.endswith(FitsExt.fits):
        return file_name.split(FitsExt.fits)[0]
    else:
        return file_name


if __name__ == "__main__":
    main()
