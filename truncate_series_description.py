import pydicom
import os
import sys

DATADIR = "C:\\Conquest\\data\\"


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


def select(list, item="item"):
    for i, v in enumerate(list):
        print(f"{i+1}: {v}")
    n = int(input(f"Select {item}: ")) - 1
    if n < 0:
        sys.exit()
    return list[n]


if __name__ == "__main__":
    while True:
        patient_id = select([x for x in os.listdir(DATADIR) if x not in ["dbase", "incoming", "printer_files"]], "patient")
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

        for uid, i in series.instances.items():
            d = pydicom.read_file(i.file)
            print(d.SeriesDescription, len(d.SeriesDescription))
            d.SeriesDescription = d.SeriesDescription[:64]
            d.save_as(i.file)
