from datetime import datetime
import csv
import pandas


from core import utils, persistence

def transform_from_reader_type(reader):
    if isinstance(reader, persistence.FixedStringReader):
        return lambda x: x.decode()
    if isinstance(reader, persistence.TimestampReader):
        return lambda x: datetime.fromtimestamp(x)
    return None

def export_to_csv(destination, datastore, fields):

    expected_length = None
    for f in fields:
        if expected_length is None:
            expected_length = len(datastore.get_reader(f))
        else:
            length = len(datastore.get_reader(f))
            if length != expected_length:
                raise ValueError(f"field '{f}' is not the same length as the first field:"
                                 f"expected {expected_length} but got {length}")
    print('expected_length:', expected_length)
    readers = [datastore.get_reader(f) for f in fields]
    transforms = [transform_from_reader_type(r) for r in readers]

    with open(destination, 'w') as d:
        csvw = csv.writer(d)
        #header
        header = [None] * len(fields)
        names = [f.name.split('/')[-1] for f in fields]
        for i_f, f in enumerate(fields):
            header[i_f] = names[i_f]
        csvw.writerow(header)

        row = [None] * len(fields)
        for chunk in datastore.chunks(expected_length):
            s = slice(chunk[0], chunk[1])
            print(s)
            chunks = [r[s] for r in readers]
            for i_r in range(chunk[1] - chunk[0]):
                for i_c, c in enumerate(chunks):
                    if transforms[i_c] is not None:
                        row[i_c] = transforms[i_c](c[i_r])
                    else:
                        row[i_c] = c[i_r]
                csvw.writerow(row)
