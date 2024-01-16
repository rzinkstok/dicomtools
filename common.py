import os
import datetime
import pydicom

RZI_PREFIX = '1.2.826.0.1.3680043.8.1200.'
IGNORE_DIRS = ["dbase", "incoming", "printer_files"]


def list_patients(datadir):
    patients = [x for x in os.listdir(datadir) if x not in IGNORE_DIRS]
    for i, v in enumerate(patients):
        print(f"{i + 1}: {v}")
    return patients


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
        study.parent = self
        return self.studies[study.uid]

    def list_studies(self):
        for i, v in enumerate(self.studies):
            print(f"{i + 1}: {v}")
        return list(self.studies.values())

    def __repr__(self):
        return f"Patient({self.patient_id}, {self.patient_name}, {self.date_of_birth}, {self.sex})"


class Study(object):
    def __init__(self, d):
        self.parent = None
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
        series.parent = self
        return self.series[series.uid]

    def list_series(self):
        for i, v in enumerate(self.series.values()):
            print(f"{i + 1}: {v.modality} {v.uid} {v.description}")
        return list(self.series.values())

    def find_series(self, series_uid):
        try:
            return self.series[series_uid]
        except KeyError:
            return None

    def find_instance(self, instance_uid):
        for series in self.series.values():
            result = series.find_instance(instance_uid)
            if result is not None:
                return result

    @property
    def single_frame_of_reference(self):
        frame_of_reference = None
        for series in self.series.values():
            for instance in series.instances.values():
                if frame_of_reference is None:
                    frame_of_reference = instance.frame_of_reference_uid
                else:
                    if instance.frame_of_reference_uid != frame_of_reference:
                        return False
        return True

    def __repr__(self):
        return f"Study({self.uid}, {self.description}, {self.date} {self.time})"


class Series(object):
    def __init__(self, d):
        self.parent = None
        self.uid = d.SeriesInstanceUID
        try:
            self.description = d.SeriesDescription
        except AttributeError:
            self.description = ''
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
        instance.parent = self
        return self.instances[instance.uid]

    def list_instances(self):
        for i, v in enumerate(self.instances):
            print(f"{i + 1}: {v}")
        return list(self.instances.values())

    def find_instance(self, instance_uid):
        try:
            return self.instances[instance_uid]
        except KeyError:
            return None

    def __repr__(self):
        return f"Series({self.modality}, {self.uid}, {self.description}, " \
               f"{self.patient_position}, {self.date} {self.time})"


def instance(d, file):
    if d.Modality == "RTPLAN":
        return RTPlan(d, file)
    elif d.Modality == "RTSTRUCT":
        return RTStruct(d, file)
    elif d.Modality == "RTDOSE":
        return RTDose(d, file)
    else:
        return Instance(d, file)


class Instance(object):
    def __init__(self, d, file):
        self.parent = None
        self.uid = d.SOPInstanceUID
        self.file = file
        self.ds = None

    @property
    def dataset(self):
        if self.ds is None:
            with open(self.file, "rb") as f:
                self.ds = pydicom.dcmread(f)
        return self.ds

    @property
    def frame_of_reference_uid(self):
        return self.dataset.FrameOfReferenceUID


class RTPlan(Instance):
    def __init__(self, d, file):
        super().__init__(d, file)

    @property
    def structure_set(self):
        instance_uid = self.dataset.ReferencedStructureSetSequence[0].ReferencedSOPInstanceUID
        return self.parent.parent.find_instance(instance_uid)


class RTStruct(Instance):
    def __init__(self, d, file):
        super().__init__(d, file)

    @property
    def ct(self):
        series_uid = self.dataset.ReferencedFrameOfReferenceSequence[0].RTReferencedStudySequence[0].RTReferencedSeriesSequence[0].SeriesInstanceUID
        return self.parent.parent.find_series(series_uid)

    @property
    def frame_of_reference_uid(self):
        return self.dataset.ReferencedFrameOfReferenceSequence[0].FrameOfReferenceUID


class RTDose(Instance):
    def __init__(self, d, file):
        super().__init__(d, file)

    @property
    def structure_set(self):
        instance_uid = self.dataset.ReferencedStructureSetSequence[0].ReferencedSOPInstanceUID
        return self.parent.parent.find_instance(instance_uid)

    @property
    def rtplan(self):
        instance_uid = self.dataset.ReferencedRTPlanSequence[0].ReferencedSOPInstanceUID
        return self.parent.parent.find_instance(instance_uid)


def get_uid():
    return RZI_PREFIX + datetime.datetime.now().strftime("%Y%m%d.%H%M%S.%f") # + '.' + str(os.getpid())


def select(items, item="item"):
    n = int(input(f"Select {item}: ")) - 1
    return items[n]


def load_data(datadir):
    patients = list_patients(datadir)
    patient_id = select(patients, "patient")
    patdir = os.path.join(datadir, patient_id)

    return load_folder(patdir)


def load_folder(folder):
    patient = None
    print()
    print("Loading data...")
    for f in os.listdir(folder):
        fpath = os.path.join(folder, f)
        with open(fpath, "rb") as f:
            d = pydicom.dcmread(f)
        if patient is None:
            patient = Patient(d)
        else:
            if d.PatientID != patient.patient_id:
                raise ValueError("Multiple patients found")
        study = patient.add_study(Study(d))
        series = study.add_series(Series(d))
        _ = series.add_instance(instance(d, fpath))
    return patient


def select_study(datadir, label="study"):
    patient = load_data(datadir)
    print(patient)
    study = select(patient.list_studies(), label)

    return study


def select_series(datadir, label="series"):
    study = select_study(datadir)
    series = select(study.list_series(), label)
    print()

    return series
