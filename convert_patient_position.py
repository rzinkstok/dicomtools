import os
from common import select_series, select, get_uid


DATADIR = "C:\\Users\\r.zinkstok\\DICOM\\"
DESTDIR = "c:\\temp\\"
UIDS = ["SOPInstanceUID", "SeriesInstanceUID", "StudyInstanceUID"]


if __name__ == "__main__":
    series = select_series(DATADIR)

    inst = series.instances.values[0].dataset
    print(f"ImagePositionPatient: {inst.ImagePositionPatient}")
    print(f"ImageOrientationPatient: {inst.ImageOrientationPatient}")
    try:
        print(f"PatientOrientation: {inst.PatientOrientation}")
    except AttributeError:
        pass
    print(f"PatientPosition: {inst.PatientPosition}")
    print(f"SliceLocation: {inst.SliceLocation}")
    print(f"SliceThickness: {inst.SliceThickness}")

    print()

    pps = ["HFS", "FFS", "HFP", "FFP"]
    pps.remove(series.patient_position)
    pp = select(pps, "new patient position")
    print()
    print(f"Changing patient position to {pp}...")

    uid_map = {}
    for instance in series.instances.values():
        d = instance.dataset

        # Save a copy of the original
        folder = os.path.join(DESTDIR, f"{d.SeriesInstanceUID}-orig")
        if not os.path.exists(folder):
            os.makedirs(folder)
        new_filename = os.path.join(folder, f"{d.SOPInstanceUID}.dcm")
        d.save_as(new_filename)

        old_pp = d.PatientPosition
        d.PatientPosition = pp
        d.SeriesDescription = f"{old_pp} -> {pp}"
        for uid in UIDS:
            cur_uid = getattr(d, uid)
            if cur_uid in uid_map:
                new_uid = uid_map[cur_uid]
            else:
                new_uid = get_uid()
                uid_map[cur_uid] = new_uid
            setattr(d, uid, new_uid)

        folder = os.path.join(DESTDIR, f"{d.SeriesInstanceUID}-{old_pp}to{pp}")
        if not os.path.exists(folder):
            os.makedirs(folder)
        new_filename = os.path.join(folder, f"{d.SOPInstanceUID}.dcm")
        d.save_as(new_filename)
    print("Done!")
