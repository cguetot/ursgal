#!/usr/bin/env python3
import ursgal
import os
import csv
import sys


class flash_lfq_1_1_1(ursgal.UNode):
    """
    """

    META_INFO = {
        "edit_version": 1.00,
        "name": "FlashLFQ",
        "version": "1.1.1",
        "release_date": "22-04-2020",
        "engine_type": {"quantification_engine": True,},
        "input_extensions": [".mzML"],
        "output_extensions": [".tsv"],
        "in_development": False,
        "create_own_folder": True,
        "include_in_git": False,
        "distributable": False,
        "utranslation_style": "flash_lfq_style_1",
        "engine": {
            "linux": {"64bit": {"exe": "CMD.exe",}},
            "darwin": {"64bit": {"exe": "CMD.exe",}},
            "win32": {"64bit": {"exe": "CMD.exe",}},
        },
        "citation": "",
    }

    def rewrite_psm_input(self, unified_csv, mod_types):
        fieldnames = [
            "File Name",
            "Scan Retention Time",
            "Precursor Charge",
            "Base Sequence",
            "Full Sequence",
            "Peptide Monoisotopic Mass",
            "Protein Accession",
        ]
        out_name = os.path.join(
            self.params["output_dir_path"], "flash_lfq_psm_input.tsv"
        )
        with open(unified_csv) as fin, open(out_name, "wt") as fout:
            reader = csv.DictReader(fin)
            writer = csv.DictWriter(fout, fieldnames=fieldnames, delimiter="\t")
            writer.writeheader()
            for line in reader:
                if line["Modifications"] == "":
                    full_seq = line["Sequence"]
                else:
                    full_seq = self.insert_mods(
                        line["Sequence"], line["Modifications"], mod_types
                    )
                line_to_write = {
                    "File Name": os.path.splitext(
                        os.path.basename(line["Raw data location"])
                    )[0],
                    "Scan Retention Time": float(line["Retention Time (s)"]) / 60,
                    "Precursor Charge": line["Charge"],
                    "Base Sequence": line["Sequence"],
                    "Full Sequence": full_seq,
                    "Peptide Monoisotopic Mass": line["uCalc Mass"],
                    "Protein Accession": line["Protein ID"],
                }
                writer.writerow(line_to_write)
        return out_name

    def insert_mods(self, sequence, ursgal_mods, mod_map):
        base_seq = sequence
        mods_sorted = sorted(
            [(m.split(":")[0], m.split(":")[1]) for m in ursgal_mods.split(";")],
            key=lambda x: x[1],
            reverse=True,
        )
        for m in mods_sorted:
            name, pos = m
            pos = int(pos)
            sequence = list(sequence)
            aa = base_seq[pos - 1]
            type = mod_map[aa]
            sequence.insert(pos, f"[Common {type}:{name} on {aa}]")
            sequence = "".join(sequence)
        return sequence

    def rewrite_as_csv(self, tsv_path):
        pass

    def __init__(self, *args, **kwargs):
        super(flash_lfq_1_1_1, self).__init__(*args, **kwargs)
        pass

    def preflight(self):
        print("[ -ENGINE- ] Executing quantification ..")
        self.time_point(tag="execution")

        if self.params["input_file"].endswith(".json"):
            mzml_files = []
            for fdict in self.params["input_file_dicts"]:
                mzml_files.append(fdict["full"])
        else:  # single mzML file
            mzml_files = os.path.join(
                self.params["input_dir_path"], self.params["input_file"]
            )
        # assert all mzml files are in the same folder
        if isinstance(mzml_files, list):
            mzml_dirs = []
            for f in mzml_files:
                mzml_dirs.append(os.path.dirname(f))
            if not len(set(mzml_dirs)) == 1:
                raise Exception("All mzmL files must be in the same directory!")

        if isinstance(mzml_files, str):
            input_file_dir = os.path.dirname(mzml_files)
        elif isinstance(mzml_files, list):
            input_file_dir = os.path.dirname(mzml_files[0])

        # Write ExperimentDesign.tsv
        # TODO move to own method
        experiment_setup = self.params["translations"]["experiment_setup"]
        if len(experiment_setup) > 0:
            with open(
                os.path.join(input_file_dir, "ExperimentalDesign.tsv"), "wt"
            ) as fout:
                fieldnames = ["FileName", "Condition", "Biorep", "Fraction", "Techrep"]
                writer = csv.DictWriter(fout, fieldnames=fieldnames, delimiter="\t")
                writer.writeheader()
                for line_dict in experiment_setup:
                    row = dict(zip(fieldnames, line_dict))
                    print(row)
                    writer.writerow(row)

        # Convert unified csv to FlashLFQ input
        unified_csv = self.params["translations"]["quantification_evidences"]
        psm_input = self.rewrite_psm_input(unified_csv)

        command_list = []
        if sys.platform in ["win32"]:
            command_list = []
        else:
            command_list = ["mono"]

        command_list.append(self.exe)
        command_list.extend(["--rep", input_file_dir])
        command_list.extend(["--idt", psm_input])
        command_list.extend(["--out", self.params["output_dir_path"]])
        # add all other parameters here
        breakpoint()
        self.params["command_list"] = command_list

    def postflight(self):
        output_files_basenames = [
            "QuantifiedPeaks.tsv",
            "QuantifiedPeptides.tsv",
            "QuantifiedProteins.tsv",
            "BayesianAnalysisBla.tsv",
        ]
        # rewrite to csv and rename
        for file in output_files_basenames:
            path = os.path.join(self.params["output_dir_path"], file)
            if os.path.exists(path):
                csv_file = self.rewrite_as_csv(path)
                suffix = os.path.splitext(csv_file)[0]
                outname, ext = os.path.splitext(csv_file)
                new_out = "{out_name}_{suffix}.{ext}"
                new_path = os.path.join(self.params["output_dir_path"], new_out)
                shutil.mv(path, new_path)
