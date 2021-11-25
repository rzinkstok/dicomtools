import pydicom
import datetime
import os

#DATADIR = "c:\\conquest\\data\\"
DATADIR = "C:\\Users\\r.zinkstok\\DICOM\\"
DESTDIR = "c:\\temp\\"
RZI_PREFIX = '1.2.826.0.1.3680043.8.1200.'
UIDS = ["SOPInstanceUID", "SeriesInstanceUID", "StudyInstanceUID"]


class Patient(object):
    def __init__(self, d):
        self.patient_id = d.PatientID
        self.patient_name = d.PatientName
        self.date_of_birth = d.PatientBirthDate
        self.sex = d.PatientSex
        self.studies = {}

    def add_study(self, study):
        if study.uid not in self.studies:
            self.studies[study.uid] = study
        return self.studies[study.uid]

    def __repr__(self):
        return f"Patient({self.patient_id}, {self.patient_name}, {self.date_of_birth}, {self.sex})"


class Study(object):
    def __init__(self, d):
        self.uid = d.StudyInstanceUID
        try:
            self.description = d.StudyDescription
        except AttributeError:
            self.description = ''
        self.date = d.StudyDate
        self.time = d.StudyTime
        self.series = {}

    def add_series(self, series):
        if series.uid not in self.series:
            self.series[series.uid] = series
        return self.series[series.uid]

    def __repr__(self):
        return f"Study({self.uid}, {self.description}, {self.date} {self.time})"


class Series(object):
    def __init__(self, d):
        self.uid = d.SeriesInstanceUID
        self.description = d.SeriesDescription
        try:
            self.date = d.SeriesDate
        except AttributeError:
            self.date = ''
        try:
            self.time = d.SeriesTime
        except AttributeError:
            self.time = ''
        self.modality = d.Modality
        try:
            self.patient_position = d.PatientPosition
        except AttributeError:
            self.patient_position = ''
        self.instances = {}

    def add_instance(self, instance):
        if instance.uid not in self.instances:
            self.instances[instance.uid] = instance
        return self.instances[instance.uid]

    def __repr__(self):
        return f"Series({self.modality}, {self.uid}, {self.description}, {self.patient_position}, {self.date} {self.time})"


class Instance(object):
    def __init__(self, d, file):
        self.uid = d.SOPInstanceUID
        self.file = file


def get_uid():
    return RZI_PREFIX + datetime.datetime.now().strftime("%Y%m%d.%H%M%S.%f") + '.' + str(os.getpid())


def select(list, item="item"):
    for i, v in enumerate(list):
        print(f"{i+1}: {v}")
    n = int(input(f"Select {item}: ")) - 1
    return list[n]


if __name__ == "__main__":
    patient_id = select(os.listdir(DATADIR), "patient")
    patdir = os.path.join(DATADIR, patient_id)

    patient = None
    print()
    print("Loading data...")
    for f in os.listdir(patdir):
        fpath = os.path.join(patdir, f)
        d = pydicom.dcmread(fpath)
        if patient is None:
            patient = Patient(d)
        study = patient.add_study(Study(d))
        series = study.add_series(Series(d))
        instance = series.add_instance(Instance(d, fpath))

    print(patient)
    study = select(list(patient.studies.values()), "study")
    print()

    series = select(list(study.series.values()), "series")
    print()

    inst = pydicom.dcmread(list(series.instances.values())[0].file)
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
        d = pydicom.dcmread(instance.file)

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
