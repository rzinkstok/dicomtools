from common import load_data, select

DATADIR = "C:\\Conquest\\data\\"


def set_uid(dataset, uid):
    if getattr(dataset, uid) == OLD_UID:
        setattr(dataset, uid, NEW_UID)
        print(f"{uid} changed")


if __name__ == "__main__":
    patient = load_data(DATADIR)
    print(patient)
    source_study = select(patient.list_studies(), "study to change")
    print()
    target_study = select(patient.list_studies(), "study to merge into")
    print()
    print("Merging")
    print(source_study)
    print("into")
    print(target_study)
    print()

    OLD_UID = source_study.uid
    NEW_UID = target_study.uid

    for series_uid, series in source_study.series.items():
        print()
        print(series)
        if input("Merge series (y/n)?") == "y":
            for uid, i in series.instances.items():
                d = i.dataset
                print(d.Modality)
                if d.StudyInstanceUID == OLD_UID:
                    d.StudyInstanceUID = NEW_UID
                    print("StudyInstanceUID changed")

                if d.Modality == "RTSTRUCT":
                    if d.ReferencedFrameOfReferenceSequence[0].RTReferencedStudySequence[0].ReferencedSOPInstanceUID == OLD_UID:
                        d.ReferencedFrameOfReferenceSequence[0].RTReferencedStudySequence[0].ReferencedSOPInstanceUID = NEW_UID
                        print("RTSTRUCT Referenced Study UID changed")

                if d.Modality == "RTPLAN":
                    pass

                if d.Modality == "RTDOSE":
                    if d.ReferencedStudySequence[0].ReferencedSOPInstanceUID == OLD_UID:
                        d.ReferencedStudySequence[0].ReferencedSOPInstanceUID = NEW_UID
                        print("RTDOSE Referenced Study UID changed")
                d.save_as(d.filename)
