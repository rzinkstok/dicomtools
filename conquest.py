"""Interface classes for Conquest DICOM server items: patient, study, series and
instance.
All item classes come in two variants:
- the ConquestItem, which is rich object containing references to the database,
  the parent item and all child items
- the ConquestSimpleItem, which lacks the database reference and the connection
  to parent and child items, but which can be serialized.
"""
import os
from datetime import datetime

#from rtlibs.dicomrtz import dicom_open


class ConquestSimpleItem(object):
    """General, serializable Conquest database record.
    Args:
        data (dict): the raw database row corresponding to the current item
        item_type (str): the type of the item (patient, study, series or
            instance)
        subitem_type (str): the type of the item's subitems
        subitem_type (str): the plural of the item's subitem type
    """
    def __init__(self, data, item_type, subitem_type, subitem_type_plural):
        self.data = data
        self.item_type = item_type
        self.subitem_type = subitem_type
        self.subitem_type_plural = subitem_type_plural

    def get_item(self, item):
        """Retrieves an item from the database row.
        Args:
            item (str): the key of the item to retrieve
        Returns:
            str: the value of the item
        """
        try:
            return self.data[item]
        except KeyError:
            return None


class ConquestItem(object):
    """General Conquest database record.
    Args:
        conn (rtlibs.conquest.database.ConquestDatabaseConnection): the
            connection to the Conquest database
        parent (rtlibs.conquest.item.ConquestItem): the parent item of the
            current item
    """
    def __init__(self, conn, parent=None):
        self.conn = conn
        self._parent = parent

    @property
    def parent(self):
        """Retrieves the parent item. If there is none, it is loaded from the
        database.
        Returns:
            rtlibs.conquest.item.ConquestItem: the parent item
        """
        if self._parent is None:
            self.load_parent()
        return self._parent

    @parent.setter
    def parent(self, parent):
        """Set this item's parent item.
        Args:
            parent (rtlibs.conquest.item.ConquestItem): the Conquest item to
                set as parent
        """
        self._parent = parent

    @property
    def infodict(self):
        """Creates a simple dict with all UIDs of the item.
        Returns:
            dict: a dictionary of all UIDs
        """
        infodict = {'patient': self.patient_id}
        if hasattr(self, "study_uid"):
            infodict['study'] = self.study_uid
        if hasattr(self, "series_uid"):
            infodict['series'] = self.series_uid
        if hasattr(self, "instance_uid"):
            infodict['instance'] = self.instance_uid
        return infodict

    def simplify(self):
        """Create a serializable ConquestSimpleItem object from the current item.
        Returns:
            rtlibs.conquest.item.ConquestSimpleItem: the serializable version
            of the current item
        """
        if hasattr(self, "instance_uid"):
            return ConquestSimpleInstance(self.data)
        if hasattr(self, "series_uid"):
            return ConquestSimpleSeries(self.data)
        if hasattr(self, "study_uid"):
            return ConquestSimpleStudy(self.data)
        return ConquestSimplePatient(self.data)


class ConquestSimplePatient(ConquestSimpleItem):
    """A serializable Conquest patient object.
    Args:
        data (dict): the raw database row corresponding to the current patient
    """
    def __init__(self, data):
        ConquestSimpleItem.__init__(self, data, "patient", "study", "studies")

    @property
    def item_uid(self):
        """Getter for the item UID.
        Returns:
            str: the item UID, which is the patient ID
        """
        return self.patient_id

    @property
    def patient_id(self):
        """Getter for the patient ID.
        Returns:
            str: the patient ID
        """
        return self.data['PatientID']

    @property
    def name(self):
        """Getter for the patient name.
        Returns:
            str: the patient name
        """
        return self.data['PatientNam']

    @property
    def full_name_inv(self):
        """Getter for the patient name (last name first, then first name).
        Returns:
            str: the patient name
        """
        return "{}, {}".format(self.lastname, self.firstname)

    @property
    def lastname(self):
        """Getter for the patient last name.
        Returns:
            str: the patient last name
        """
        if "^" in self.name:
            return self.name.split("^")[0]
        return self.name

    @property
    def firstname(self):
        """Getter for the patient first name.
        Returns:
            str: the patient first name
        """
        if "^" in self.name:
            return self.name.split("^")[1]
        return ""

    @property
    def sex(self):
        """Getter for the patient sex.
        Returns:
            str: the patient sex
        """
        return self.data['PatientSex']

    @property
    def date_of_birth(self):
        """Getter for the patient's birth date
        Returns:
            datetime.date: the patient's birth date
        """
        if self.data['PatientBir'] == 'None' or not self.data['PatientBir']:
            return None
        return datetime.strptime(self.data['PatientBir'], '%Y%m%d').date()

    @property
    def data_path(self):
        """Getter for the data path.
        Returns:
            str: the data path
        """
        return self.data['data_path']

    @property
    def path(self):
        """Getter for the patient data path.
        Returns:
            str: the patient data path
        """
        return os.path.join(self.data_path, self.patient_id)

    @property
    def number_of_studies(self):
        """Getter for the number of studies belonging to the patient
        Returns:
            int: the number of studies belonging to the patient
        """
        return self.data['nstudies']

    @property
    def number_of_series(self):
        """Getter for the number of series belonging to the patient
        Returns:
            int: the number of series belonging to the patient
        """
        return self.data['nseries']

    @property
    def number_of_instances(self):
        """Getter for the number of instances belonging to the patient
        Returns:
            int: the number of instances belonging to the patient
        """
        return self.data['ninstances']

    @property
    def number_of_subitems(self):
        """Getter for the number of subitems belonging to the patient
        Returns:
            int: the number of subitems belonging to the patient
        """
        return self.number_of_studies

    @property
    def header(self):
        """Getter for the header to be displayed for the patient in a GUI.
        Returns:
            str: the header for the patient
        """
        return self.name

    @property
    def details(self):
        """Getter for the details to be displayed for the patient in a GUI.
        Returns:
            dict: the details for the patient
        """
        return [
            "Patient ID: {0}".format(self.patient_id),
            "Date of birth: {0}".format(self.date_of_birth),
            "Sex: {0}".format(self.sex),
        ]

    def __repr__(self):
        return "{0} ({1})".format(self.name, self.patient_id)


class ConquestPatient(ConquestItem, ConquestSimplePatient):
    """Conquest database record of a DICOM patient.
    Args:
        conn (rtlibs.conquest.database.ConquestDatabaseConnection): the
            connection to the Conquest database
        data (dict): the raw database row corresponding to the current patient
        parent (rtlibs.conquest.items.ConquestItem): the parent item of the
            current patient
    """
    def __init__(self, conn, data, parent=None):
        ConquestItem.__init__(self, conn, parent)
        ConquestSimplePatient.__init__(self, data)

    @property
    def studies(self):
        """Getter for the studies belonging to the patient.
        Returns:
            list: all rtlibs.conquest.items.ConquestStudy objects belonging to
            the patient
        """
        return self.conn.get_studies_for_patient(self)

    def get_study(self, study_uid):
        """Returns the study with the given study UID, provided it belongs to the
        patient.
        Args:
            study_uid (str): the UID of the study to retrieve
        Returns:
            rtlibs.conquest.items.ConquestStudy: the study with the given
            study UID
        """
        study = self.conn.get_study(study_uid)
        if study.patient_id != self.patient_id:
            return None
        return study

    @property
    def series(self):
        """Getter for all series belonging to the patient.
        Returns:
            list: all rtlibs.conquest.items.ConquestSeries objects belonging to
            the patient
        """
        series = []
        for study in self.studies:
            series.extend(study.series)
        return series

    @property
    def instances(self):
        """Getter for all instances belonging to the patient.
        Returns:
            list: all rtlibs.conquest.items.ConquestInstance objects belonging
            to the patient
        """
        instances = []
        for study in self.studies:
            instances.extend(study.instances)
        return instances

    def delete(self):
        """Delete all DICOM files and database records related to this patient.
        """
        self.conn.delete_patient(self.patient_id)

    @property
    def has_oblique_series(self):
        """Checks whether the patient has any series with oblique slices.
        Returns:
            bool: whether the patient has any series with oblique slices
        """
        for study in self.studies:
            if study.has_oblique_series:
                return True
        return False

    @property
    def uid_tree(self):
        """Retrieves a nested dict with the UIDs of all descendant items of the
        patient.
        Returns:
            dict: a nested dict with the UIDs of all all descendent items
        """
        study_dict = {}
        for study in self.studies:
            series_dict = {}
            for series in study.series:
                instance_list = []
                for instance in series.instances:
                    instance_list.append(instance.instance_uid)
                series_dict[series.series_uid] = instance_list
            study_dict[study.study_uid] = series_dict
        return study_dict


class ConquestSimpleStudy(ConquestSimpleItem):
    """A serializable Conquest study object.
    Args:
        data (dict): the raw database row corresponding to the current study
    """
    def __init__(self, data):
        ConquestSimpleItem.__init__(self, data, "study", "series", "series")

    @property
    def item_uid(self):
        """Getter for the item UID.
        Returns:
            str: the item UID, which is the study UID
        """
        return self.study_uid

    @property
    def patient_id(self):
        """Getter for the patient ID.
        Returns:
            str: the patient ID
        """
        return self.data['PatientID']

    @property
    def study_uid(self):
        """Getter for the study UID.
        Returns:
            str: the study UID
        """
        return self.data['StudyInsta']

    @property
    def study_date(self):
        """Getter for the study date.
        Returns:
            datetime.date: the study date
        """
        if "StudyDate" in self.data and self.data['StudyDate'] != "None" and \
                self.data['StudyDate'] is not None:
            return datetime.strptime(self.data['StudyDate'], "%Y%m%d").date()
        return None

    @property
    def study_time(self):
        """Getter for the study time.
        Returns:
            datetime.time: the study time
        """
        if "StudyTime" not in self.data:
            return None
        study_time = self.data['StudyTime']
        if study_time is None:
            return None
        if study_time.find(".") >= 0:
            study_time = study_time.split('.')[0]
        try:
            return datetime.strptime(study_time, "%H%M%S").time()
        except ValueError:
            return None

    @property
    def study_datetime(self):
        """Getter for the study date and time.
        Returns:
            datetime.datetime: the study date and time
        """
        try:
            return datetime.combine(self.study_date, self.study_time)
        except TypeError:
            return None

    @property
    def study_id(self):
        """Getter for the study ID.
        Returns:
            str: the study ID
        """
        return self.data.get('StudyID', None)

    @property
    def study_description(self):
        """Getter for the study description.
        Returns:
            str: the study description
        """
        return self.data.get('StudyDescr', None)

    @property
    def number_of_series(self):
        """Getter for the number of series in the study.
        Returns:
            int: the number of series in the study
        """
        return int(self.data['nseries'])

    @property
    def number_of_instances(self):
        """Getter for the number of instances in the study.
        Returns:
            int: the number of instances in the study
        """
        return int(self.data['ninstances'])

    @property
    def number_of_subitems(self):
        """Getter for the number of subitems in the study.
        Returns:
            int: the number of subitems in the study
        """
        return self.number_of_series

    @property
    def header(self):
        """Getter for the header to be displayed for the study in a GUI.
        Returns:
            str: the header for the study
        """
        return self.study_description

    @property
    def details(self):
        """Getter for the details to be displayed for the study in a GUI.
        Returns:
            str: the details for the study
        """
        return [
            "Date/time: {0}".format(self.study_datetime),
            "Study ID: {0}".format(self.study_id),
            "Study&nbsp;UID:&nbsp;{0}".format(self.study_uid)
        ]

    def __repr__(self):
        return "{0} ({1})".format(self.study_description, self.study_datetime)


class ConquestStudy(ConquestItem, ConquestSimpleStudy):
    """Conquest database record of a DICOM study.
    Args:
        conn (rtlibs.conquest.database.ConquestDatabaseConnection): the
            connection to the Conquest database
        data (dict): the raw database row corresponding to the current study
        parent (rtlibs.conquest.items.ConquestPatient): the parent item of the
            current study
    """
    def __init__(self, conn, data, parent=None):
        ConquestItem.__init__(self, conn, parent)
        ConquestSimpleStudy.__init__(self, data)

    def load_parent(self):
        """Loads the associated ConquestPatient object from the database and sets
        it as the parent object.
        """
        self.parent = self.conn.get_patient(self.patient_id)

    @property
    def series(self):
        """Getter for the series belonging to the study.
        Returns:
            list: all rtlibs.conquest.items.ConquestSeries objects belonging to
            the study
        """
        return self.conn.get_series_for_study(self)

    def get_series(self, series_uid):
        """Returns the series with the given series UID, provided it belongs to
        the study.
        Args:
            series_uid (str): the UID of the series to retrieve
        Returns:
            rtlibs.conquest.items.ConquestSeries: the series with the given
            series UID
        """
        series = self.conn.get_series(series_uid)
        if series.study_uid != self.study_uid:
            return None
        return series

    @property
    def instances(self):
        """Getter for all instances belonging to the study.
        Returns:
            list: all rtlibs.conquest.items.ConquestInstance objects belonging
            to the study
        """
        instances = []
        for series in self.series:
            instances.extend(series.instances)
        return instances

    @property
    def patient(self):
        """Getter for the patient that the study belongs to.
        Returns:
            rtlibs.conquest.items.ConquestPatient: the patient that the study
            belongs to
        """
        return self.parent

    def delete(self):
        """Deletes all DICOM files and database records related to this study.
        """
        self.conn.delete_study(self.study_uid)

    @property
    def has_oblique_series(self):
        """Checks whether the study has any series with oblique slices.
        Returns:
            bool: whether the study has any series with oblique slices
        """
        for series in self.series:
            if series.oblique:
                return True
        return False


class ConquestSimpleSeries(ConquestSimpleItem):
    """A serializable Conquest series object.
    Args:
        data (dict): the raw database row corresponding to the current series
    """
    def __init__(self, data):
        ConquestSimpleItem.__init__(self, data, "series", "instance",
                                    "instances")

    @property
    def item_uid(self):
        """Getter for the item UID.
        Returns:
            str: the item UID, which is the series UID
        """
        return self.series_uid

    @property
    def patient_id(self):
        """Getter for the patient ID.
        Returns:
            str: the patient ID
        """
        try:
            return self.data['SeriesPat']
        except KeyError:
            return self.data['PatientID']

    @property
    def study_uid(self):
        """Getter for the study UID.
        Returns:
            str: the study UID
        """
        return self.data['StudyInsta']

    @property
    def series_uid(self):
        """Getter for the series UID.
        Returns:
            str: the series UID
        """
        return self.data['SeriesInst']

    @property
    def series_date(self):
        """Getter for the series date.
        Returns:
            datetime.date: the series date
        """
        return datetime.strptime(self.data['SeriesDate'], "%Y%m%d").date()

    @property
    def series_time(self):
        """Getter for the series time.
        Returns:
            datetime.time: the series time
        """
        series_time = self.data['SeriesTime']
        if series_time.find(".") >= 0:
            series_time = series_time.split('.')[0]
        return datetime.strptime(series_time, "%H%M%S").time()

    @property
    def series_datetime(self):
        """Getter for the series date and time.
        Returns:
            datetime.time: the series time
        """
        return datetime.combine(self.series_date, self.series_time)

    @property
    def series_number(self):
        """Getter for the series number.
        Returns:
            str: the series number
        """
        return self.data.get('SeriesNumb', None)

    @property
    def series_description(self):
        """Getter for the series description.
        Returns:
            str: the series description
        """
        return self.data.get('SeriesDesc', None)

    @property
    def modality(self):
        """Getter for the series modality.
        Returns:
            str: the series modality
        """
        return self.data['Modality']

    @property
    def series_modality(self):
        """Alias for the series modality.
        Returns:
            str: the series modality
        """
        return self.modality

    @property
    def protocol_name(self):
        """Getter for the series protocol name.
        Returns:
            str: the series protocol name
        """
        return self.data.get('ProtocolNa', None)

    @property
    def manufacturer(self):
        """Getter for the series manufacturer.
        Returns:
            str: the series manufacturer
        """
        return self.data['Manufactur']

    @property
    def model_name(self):
        """Getter for the series model name.
        Returns:
            str: the series model name
        """
        return self.data.get('ModelName', None)

    @property
    def station_name(self):
        """Getter for the series station name.
        Returns:
            str: the series station name
        """
        return self.data.get('StationNam', None)

    @property
    def frame_of_reference_uid(self):
        """Getter for the Frame of Reference UID
        Returns:
            str: the Frame of Reference UID
        """
        return self.data['FrameOfRef']

    @property
    def number_of_instances(self):
        """Getter for the number of instances in the series
        Returns:
            int: the number of instances in the series
        """
        return int(self.data['ninstances'])

    @property
    def number_of_subitems(self):
        """Getter for the number of subitems (instances) in the series
        Returns:
            int: the number of subitems in the series
        """
        return self.number_of_instances

    @property
    def header(self):
        """Getter for the header to be displayed for the series in a GUI.
        Returns:
            str: the header for the series
        """
        return self.series_modality

    @property
    def details(self):
        """Getter for the details to be displayed for the series in a GUI.
        Returns:
            str: the details for the series
        """
        return [
            "Series&nbsp;UID:&nbsp;{0}".format(self.series_uid),
            "Description: {0}".format(self.series_description),
            "Protocol name: {0}".format(self.protocol_name),
            "Creator: {0} ({1})".format(self.model_name, self.station_name),
        ]

    def __repr__(self):
        return "{0} ({1}) {2}".format(self.modality, self.number_of_instances,
                                      self.series_uid)


class ConquestSeries(ConquestItem, ConquestSimpleSeries):
    """Conquest database record of a DICOM series.
    Args:
        conn (rtlibs.conquest.database.ConquestDatabaseConnection): the
            connection to the Conquest database
        data (dict): the raw database row corresponding to the current series
        parent (rtlibs.conquest.items.ConquestStudy): the parent item of the
            current series
    """
    def __init__(self, conn, data, parent=None):
        ConquestItem.__init__(self, conn, parent)
        ConquestSimpleSeries.__init__(self, data)

    def load_parent(self):
        """Loads the associated ConquestStudy object from the database and sets it
        as the parent object.
        """
        self.parent = self.conn.get_study(self.study_uid)

    def __len__(self):
        """Returns the number of instances in the series.
        Returns:
            int: the number of instances in the series
        """
        return len(self.instances)

    @property
    def instances(self):
        """Getter for all instances belonging to the series.
        Returns:
            list: all rtlibs.conquest.items.ConquestInstance objects belonging
            to the series
        """
        return self.conn.get_instances_for_series(self)

    @property
    def instance_uids(self):
        """Getter for the UIDs of all instances belonging to the series
        Returns:
            list: the UIDs of all instances belonging to the series
        """
        return [i.instance_uid for i in self.instances]

    @property
    def ordered_instance_uids(self):
        """Getter for the ordered UIDs of all instances belonging to the series.
        The instances are sorted by slice location when present, otherwise by
        image number.
        Returns:
            list: the ordered UIDs of all instances belonging to the series
        """
        return self.conn.get_ordered_instance_uids_for_series(self)

    def get_instance(self, instance_uid):
        """Returns the instance with the given instance UID, provided it belongs
        to the series.
        Args:
            instance_uid (str): the UID of the instance to retrieve
        Returns:
            rtlibs.conquest.items.ConquestInstance: the instance with the given
            series UID
        """
        instance = self.conn.get_instance(instance_uid)
        if instance.series_uid != self.series_uid:
            return None
        return instance

    @property
    def study(self):
        """Getter for the study that the series belongs to.
        Returns:
            rtlibs.conquest.items.ConquestStudy: the study that the series
            belongs to
        """
        return self.parent

    @property
    def patient(self):
        """Getter for the patient that the series belongs to.
        Returns:
            rtlibs.conquest.items.ConquestPatient: the patient that the series
            belongs to
        """
        return self.study.patient

    @property
    def oblique(self):
        """Checks whether the series contains oblique slices. This is checked only
        for the first slice in the series.
        Returns:
            bool: whether the series contains oblique slices
        """
        return self.instances[0].oblique

    @property
    def oblique_angle(self):
        """Returns the angle between the slice normal and the positive Z-axis.
        Returns:
            float: the angle between the slice normal and the positive Z-axis
        """
        return self.instances[0].oblique_angle

    def delete(self):
        """Deletes all DICOM files and database records related to this series.
        """
        self.conn.delete_series(self.series_uid)


class ConquestSimpleInstance(ConquestSimpleItem):
    """A serializable Conquest instance object.
    Args:
        data (dict): the raw database row corresponding to the current instance
    """
    def __init__(self, data):
        ConquestSimpleItem.__init__(self, data, "instance", None, None)

    @property
    def item_uid(self):
        """Getter for the item UID.
        Returns:
            str: the item UID, which is the instance UID
        """
        return self.instance_uid

    @property
    def patient_id(self):
        """Getter for the patient ID
        Returns:
            str: the patient ID
        """
        try:
            return self.data['ImagePat']
        except KeyError:
            return self.data['PatientID']

    @property
    def study_uid(self):
        """Getter for the study UID.
        Returns:
            str: the study UID
        """
        return self.data['StudyInsta']

    @property
    def series_uid(self):
        """Getter for the series UID.
        Returns:
            str: the series UID
        """
        return self.data['SeriesInst']

    @property
    def instance_uid(self):
        """Getter for the instance UID.
        Returns:
            str: the instance UID
        """
        return self.data['SOPInstanc']

    @property
    def instance_number(self):
        """Getter for the instance number.
        Returns:
            str: the instance number
        """
        return self.data['ImageNumbe']

    @property
    def image_number(self):
        """Getter for the image number
        Returns:
            str: the image number
        """
        return self.instance_number

    @property
    def instance_date(self):
        """Getter for the instance date.
        Returns:
            datetime.date: the instance date
        """
        return self.data['ImageDate']

    @property
    def instance_time(self):
        """Getter for the instance time.
        Returns:
            datetime.time: the instance time
        """
        return self.data['ImageTime']

    @property
    def acquisition_date(self):
        """Getter for the instance acquisition date.
        Returns:
            datetime.date: the instance acquisition date
        """
        return self.data['AcqDate']

    @property
    def acquisition_time(self):
        """Getter for the instance acquisition time.
        Returns:
            datetime.time: the instance acquisition time
        """
        return self.data['AcqTime']

    @property
    def slice_location(self):
        """Getter for the instance slice location.
        Returns:
            float: the instance slice location
        """
        return self.data['SliceLocat']

    @property
    def modality(self):
        """Getter for the instance modality.
        Returns:
            str: the instance modality
        """
        try:
            return self.data['Modality']
        except KeyError:
            return None

    @property
    def oblique_angle(self):
        """Returns the angle between the slice normal and the positive Z-axis.
        Returns:
            float: the angle between the slice normal and the positive Z-axis
        """
        if self.modality not in ['MR', 'CT', 'SC']:
            return None
        try:
            return self.file.oblique_angle
        except AttributeError:
            return None

    @property
    def oblique(self):
        """Checks whether the instance is oblique.
        Returns:
            bool: whether the instance is oblique
        """
        if self.modality not in ['MR', 'CT', 'SC']:
            return False
        try:
            return self.file.oblique
        except AttributeError:
            return False

    @property
    def filename(self):
        """Getter for the DICOM file path relative to the Conquest server's data
        path.
        Returns:
            str: the relative path to the DICOM file
        """
        return self.data['ObjectFile']

    @property
    def data_path(self):
        """Getter for the Conquest server's data path.
        Returns:
            str: the path where all DICOM files are stored
        """
        return self.data['data_path']

    @property
    def filepath(self):
        """Getter for the full path to the DICOM file associated with the
        instance.
        Returns:
            str: the full path to the DICOM file
        """
        return os.path.join(self.data_path, self.filename)

    @property
    def file(self):
        """Getter for the DICOM file object associated with the instance.
        Returns:
            rtlibs.dicomrtz.DICOMFileObject: the opened DICOM file
        """
        return dicom_open(self.filepath, force=True)

    @property
    def number_of_instances(self):
        """Getter for the number of instances in the current instance.
        Returns:
            int: the number of instances
        """
        return 1

    @property
    def header(self):
        """Getter for the header to be displayed for the instance in a GUI.
        Returns:
            str: the header for the instance
        """
        return self.modality
        # return "Instance UID: {0}".format(self.instance_uid)

    @property
    def details(self):
        """Getter for the details to be displayed for the instance in a GUI.
        Returns:
            str: the details for the instance
        """
        return [
            "Instance&nbsp;UID:&nbsp;{0}".format(self.instance_uid)
        ]

    def __repr__(self):
        return "instance {0}".format(self.instance_uid)


class ConquestInstance(ConquestItem, ConquestSimpleInstance):
    """Conquest database record of a DICOM instance.
    Args:
        conn (rtlibs.conquest.database.ConquestDatabaseConnection): the
            connection to the Conquest database
        data (dict): the raw database row corresponding to the current instance
        parent (rtlibs.conquest.items.ConquestInstance): the parent item of the
            current instance
    """
    def __init__(self, conn, data, parent=None):
        ConquestItem.__init__(self, conn, parent)
        ConquestSimpleInstance.__init__(self, data)

    def load_parent(self):
        """Loads the associated ConquestSeries object from the database and sets
        it as the parent object.
        """
        self.parent = self.conn.get_series(self.series_uid)

    @property
    def series(self):
        """Getter for the series that the instance belongs to.
        Returns:
            rtlibs.conquest.items.ConquestSeries: the series that the instance
            belongs to
        """
        return self.parent

    @property
    def study(self):
        """Getter for the study that the instance belongs to.
        Returns:
            rtlibs.conquest.items.ConquestStudy: the study that the instance
            belongs to
        """
        return self.series.study

    @property
    def patient(self):
        """Getter for the patient that the instance belongs to.
        Returns:
            rtlibs.conquest.items.ConquestPatient: the patient that the
            instance belongs to
        """
        return self.study.patient

    @property
    def instances(self):
        """Getter for all instances in this instance. Of course, that is only one.
        Returns:
            list: all instances in this instance
        """
        return [self]

    def delete(self):
        """Deletes the DICOM file and database record related to this instance.
        """
        self.conn.delete_instance(self.instance_uid)