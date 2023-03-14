import os
from common import select_study, select_series, get_uid

DATADIR = "C:\\Conquest\\data\\"
DESTDIR = "C:\\Temp\\ResetUPI\\"


if __name__ == "__main__":
    study = select_study(DATADIR)
    for ser in list(study.series.values()):
        if ser.modality not in ["RTPLAN", "RTDOSE"]:
            continue

        instance = list(ser.instances.values())[0]
        rtplan = instance.dataset
        print()
        print(ser.modality)
        print(rtplan.SOPInstanceUID)
        print("StudyDescription:", rtplan.StudyDescription)

        if ser.modality == "RTPLAN":
            print("RTPlanDescription:", rtplan.RTPlanDescription)

        try:
            sd = rtplan.SeriesDescription
        except AttributeError:
            sd = ''
        print("SeriesDescription:", sd)

        if not rtplan.PatientSex:
            rtplan.PatientSex = "M"
        print("Sex:", rtplan.PatientSex)

        if not rtplan.PatientBirthDate:
            rtplan.PatientBirthDate = "19790401"
        print("BirthDate:", rtplan.PatientBirthDate)

        if sd and sd.find("=") < 0:
            upi = sd[3:]
            print("UPI:", upi)
            new_sd = f"U={upi}"
            print("New SeriesDescription:", new_sd)
            rtplan.SeriesDescription = new_sd

        rtplan.save_as(instance.file)