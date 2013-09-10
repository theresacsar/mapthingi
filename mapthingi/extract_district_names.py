from os import listdir
from os.path import isfile, join

def districtnames(folder):
    names = []

    # collect all poly filenames
    files = [
        join(folder,f) for f in listdir(folder) 
            if isfile(join(folder,f))
            and f.endswith(".poly")
    ];

    print("File count: %d" % len(files));

    for i, file_ in enumerate(files):
        fp = open(file_,"r")
        first_line = next(fp)
        names.append(unicode(first_line))
        fp.close()

    with open('district_names.csv','w') as f:
        for name in names:
            f.write(name)


districtnames("./poly")
