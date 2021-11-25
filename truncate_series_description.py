import sys
from common import select_series

DATADIR = "C:\\Conquest\\data\\"


if __name__ == "__main__":
    while True:
        series = select_series(DATADIR)

        for uid, i in series.instances.items():
            d = i.dataset
            print(d.SeriesDescription, len(d.SeriesDescription))
            if len(d.SeriesDescription) > 64:
                d.SeriesDescription = d.SeriesDescription[:64]
                d.save_as(i.file)
                print(f"Truncated series description to {d.SeriesDescription}")
            else:
                print(f"Series description does not need to be truncated: {d.SeriesDescription}")

        print()
        if input("Another one (y/n)? ") == "n":
            sys.exit()
