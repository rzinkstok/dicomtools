import common

FOLDER = r"C:\Conquest\data\F0179638"


def error(m, n=0):
    print(n * " " + f"ERROR: {m}")
    return False


def check_set(folder):
    all_fine = True

    patient = common.load_folder(folder)
    print()
    print(patient)
    if len(patient.studies) > 1:
        all_fine = error("Multiple studies")

    study = list(patient.studies.values())[0]
    print(">", study)

    if not study.single_frame_of_reference:
        all_fine = error("Study has multiple Frames of Reference", 2)

    for series in study.series.values():
        print("  >", series)
        if series.modality == "RTPLAN":
            for inst in series.instances.values():
                if inst.structure_set is None:
                    all_fine = error(f"RTPLAN references missing Structure Set", 4)
        elif series.modality == "RTSTRUCT":
            for inst in series.instances.values():
                if inst.ct is None:
                    all_fine = error(f"RTSTRUCT references missing CT", 4)
        elif series.modality == "RTDOSE":
            for inst in series.instances.values():
                if inst.rtplan is None:
                    all_fine = error(f"RTDOSE references missing RTPlan", 4)
                if inst.structure_set is None:
                    all_fine = error(f"RTDOSE references missing Structure Set", 4)

    if all_fine:
        print()
        print("Dataset is consistent")


if __name__ == "__main__":
    check_set(FOLDER)