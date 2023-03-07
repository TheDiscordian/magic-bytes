import json, time, os
from collections import namedtuple

Row = namedtuple('Row', ['hex_signature', 'offset', 'extension', 'sub_signatures', 'sub_offset', 'offset_every'])
MapRow = namedtuple('Row', ['extension', 'sub_signatures', 'sub_offset', 'offset_every'])
ListRow = namedtuple('Row', ['hex_signature', 'offset', 'extension'])
lookup_map = json.load(open("../../dist/lookup_map.json", "r"))
offset_list = json.load(open("../../dist/offset_list.json", "r"))

def get_file_extension_from_bytes_offset_list(data, offset_list):
    for i in range(len(offset_list)):
        row = ListRow(*offset_list[i])
        sig = bytes.fromhex(row.hex_signature.replace(" ", "")) # TODO test dmg files
        if data[row.offset:row.offset + len(sig)] == sig:
            return row.extension
    return "unknown"

def get_file_extension_from_bytes_lookup_map(data, lookup_map):
    # Iterate over the bytes in the file.
    for i in range(len(data)):
        # Get the current byte as a hex string.
        hex_key = hex(data[i])[2:]
        # If the current byte is in the map, move to the next byte.
        if hex_key in lookup_map:
            lookup_map = lookup_map[hex_key]
        else: # If there are no more bytes, check if there's a row.
            if "r" in lookup_map:
                row = MapRow(*lookup_map["r"])
                if len(row.sub_signatures[0]) == 0:
                    return row.extension[0]
                else:
                    for j in range(len(row.sub_signatures)):
                        sig = bytes.fromhex(row.sub_signatures[j].replace(" ", ""))
                        if data[i + row.sub_offset:i + row.sub_offset + len(sig)] == sig:
                            return row.extension[j]
                    # No sub_signature.
                    break
            else: # No row.
                break
    return "unknown"

def get_file_extension_from_bytes(data, lookup_map, offset_list, prefer_offset=False):
    result = "unknown"
    if prefer_offset:
        result = get_file_extension_from_bytes_offset_list(data, offset_list)
    else:
        result = get_file_extension_from_bytes_lookup_map(data, lookup_map)
    if result == "unknown":
        if prefer_offset:
            result = get_file_extension_from_bytes_lookup_map(data, lookup_map)
        else:
            result = get_file_extension_from_bytes_offset_list(data, offset_list)
    return result

def get_file_extension(filename, lookup_map, offset_list=[]):
    with open(filename, "rb") as f:
        return get_file_extension_from_bytes(f.read(), lookup_map, offset_list)

# samples contains the path to every file in ../../samples.
samples = os.listdir("../../samples")
now = time.time()
ids = []
for sample in samples:
    ids.append((sample, get_file_extension("../../samples/" + sample, lookup_map, offset_list)))
time_taken = (time.time() - now) * 1000
for i in ids:
    print(i)
print("Time taken: %.2fms" % time_taken)