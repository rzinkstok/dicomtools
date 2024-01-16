import pydicom
import os
import common

FOLDER = r"C:\Conquest\data\F0179638"
TAGS_TO_REMOVE = [(0x0010, 0x1000), (0x0010, 0x1002), (0x0010, 0x1001)]
TAGS_TO_CLEAR = []


def anonymize(folder):
    for f in os.listdir(folder):
        fn = os.path.join(folder, f)
        print(f)
        with open(fn, 'rb') as df:
            d = pydicom.dcmread(df, force=True)

        for g, t in TAGS_TO_REMOVE:
            try:
                d[g, t]
            except KeyError:
                continue

            del d[g, t]

        d.PatientBirthDate = "19500101"
        d.save_as(fn)


if __name__ == "__main__":
    anonymize(FOLDER)