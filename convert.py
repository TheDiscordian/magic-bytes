import csv, json, os
from collections import namedtuple
extensions = {} # FIXME remove this
# Don't like this script? Please improve it or make a new one. Changes are hugely welcome.

# CSV file is generated from https://en.wikipedia.org/wiki/List_of_file_signatures using https://github.com/gambolputty/wikitable2csv

# Define the named tuple that will hold the data for each row
# hex_signature is the bytes expected to be found at offset (starting from the end of the file, if
# negative). Extension is the resulting extension the file should have if it has the signature, it's
# stored as a list. The first entry should be used always if there's no sub_signature, otherwise the
# extension index should be the same as the sub_signature index. Sub_signatures is a list of
# signatures that should appear to fully satisfy the signature requirements to determine the file
# type. Specificially a sub_signature should be at len(hex_signature) + sub_offset. Offset_every is
# used for things like signature "G" (mpg), where the signature appears every x bytes. If set, first
# offset should be checked, and then offset_every until EOF (or you feel satisfied I suppose).
Row = namedtuple('Row', ['hex_signature', 'offset', 'extension', 'sub_signatures', 'sub_offset', 'offset_every'])
MapRow = namedtuple('Row', ['extension', 'sub_signatures', 'sub_offset', 'offset_every'])
ListRow = namedtuple('Row', ['hex_signature', 'offset', 'extension'])

# Create an empty dictionary to hold the objects without offsets.
rows_map = {}
# Create an empty list to hold all the objects with offsets.
offset_list = []

# INFO As the Wikipedia table has random newlines added to the hex signatures, we *MUST* check the
# ISO 8859-1 column to see how many entries there truely are in a row. This field isn't consistent
# either though (See: PDB / XML), and newlines are randomly added into the ISO 8859-1 column as
# well. As a result, we specify manually the formats which are impossible to guess at what to do,
# and tell the parser explicitly to treat it as one line.
# Any signature belonging to a jank extension will be treated as one entry (for a multi-entry row
# see mp3 for an example).
jank = ["PDB", "fits", "cwk", "vdi"]
# Info about each extension:
# PDB: Maybe we should just omit this? Are 24 null bytes really a reasonable way to determine a signature?
# The rest of them: These are only janky because of the Wikipedia formatting

# INFO Items in skip are more janky than jank. skip was made because of the several xml entries
# which are identical, but contain null bytes for seemingly no reason. Items are only skipped if
# they contain new lines in their ISO 8859-1 column (which means normal xml files are still
# supported).
skip = ["xml"]

# ALWAYS_SKIP is a list of entries that should always be skipped, regardless of the contents of the
# ISO 8859-1 column. This is for entries which aren't clear enough to parse. For example mxf is
# skipped because "0-65535 (run-in)" isn't a clear offset. PIC is excluded because a single null
# byte is far from reliable.
ALWAYS_SKIP = ["mxf", "PIC"]

# TODO There is a special case, see signature "G", it occurs every 188 bytes.
# Currently this only works with signature "G", and sets "offset_every" to 188.
special = ["G"]

def str_sig_to_bytes(sig):
    return bytes.fromhex(sig.replace(" ", ""))

def rows_map_to_lookup_map(rows_map):
    lookup_map = {}
    for sig, row in rows_map.items():
        bin_sig = str_sig_to_bytes(sig)
        curMap = lookup_map
        for i in range(len(bin_sig)):
            hex_key = hex(bin_sig[i])[2:]
            # If this is a new entry, create a new map for it.
            if not hex_key in curMap:
                curMap[hex_key] = {}
            # If this is the last byte, add the row to the map.
            if i == len(bin_sig) - 1:
                curMap[hex_key]["r"] = MapRow(*row[2:])
            else:
                # Otherwise, move to the next map.
                curMap = curMap[hex_key]
    return lookup_map

def get_sigs(sig, iso):
    sig_newlines = '\n' in sig
    iso_newlines = '\n' in iso
    if not sig_newlines and not iso_newlines:
        return [sig]
    if not iso_newlines and sig_newlines:
        return [sig.replace("\n", " ")]

    sigs = sig.split("\n")
    isos = iso.split("\n")
    if len(sigs) != len(isos):
        print("ERROR: sigs and isos are not the same length")
        print("SIG:", sig)
        exit(1)
    return sigs

# Open the CSV file for reading
with open('file_sigs.csv', newline='') as csvfile:
    # skipped_entries keeps track of every entry that was skipped, and the reason (unless it's in
    # `skip`)
    skipped_entries = []
    reader = csv.DictReader(csvfile)
    for row in reader:
        offset_every = 0
        if row['ISO 8859-1'] in special:
            offset_every = 188 # G is special, it occurs every 188 bytes

        sigs = []
        extension = ""
        if row['Extension'] != "":
            extension = row['Extension'].split()[0]

        if extension in ALWAYS_SKIP:
            continue
        # Skip the row if it contains a newline in the ISO 8859-1 column and the extension is in
        # the skip list.
        if '\n' in row['ISO 8859-1'] and extension in skip:
            continue
        # If the extension is in the jank list, treat it as a single entry.
        if extension in jank:
            sigs = [row['Hex signature'].upper().replace("\n", " ")]
        else:
            sigs = get_sigs(row['Hex signature'].upper(), row['ISO 8859-1'])

        for raw_sig in sigs:
            # Set offset to an integer
            offset = 0
            _offset = row['Offset'].split()[0].upper()
            if _offset[:4] == "END–": # Wikipedia uses an Em dash, this isn't an error
                offset = -int(_offset[4:])
            elif len(_offset) >= 2 and _offset[1] == "X" or "A" in _offset or "B" in _offset or "C" in _offset or "D" in _offset or "E" in _offset or "F" in _offset:
                offset = int(_offset, 16)
            else:
                try:
                    offset = int(_offset.split()[0])
                except ValueError:
                    # We failed to parse the offset, skip this entry, and add it to skipped_entries
                    skipped_entries.append((row, "Offset failed to parse"))
                    break

            # Some entries contain extra info in brackets, let's strip that out
            if "(" in raw_sig:
                raw_sig = raw_sig[:raw_sig.index("(")].strip()

            sig, sub = "", ""
            sub_offset = 0
            # Handle the case where there is a sub signature (check for wildcards)
            if "?" in raw_sig:
                sig = raw_sig[:raw_sig.index("?")].strip()
                sub = raw_sig[len(raw_sig)-raw_sig[::-1].index("?"):].strip()
                sub_offset = int(len(raw_sig[len(sig):(len(raw_sig)-len(sub))].replace(" ", "").replace("\xa0", ""))/2)
            else:
                sig = raw_sig

            if extension != "" and not extension in extensions:
                print("-", extension)
                extensions[extension] = None

            if sig in rows_map and offset == 0:
                _row = rows_map[sig]
                _row.sub_signatures.append(sub)
                _row.extension.append(extension)

                if sub_offset != _row.sub_offset:
                    print("ERROR: sub_offset mismatch")
                    print("_ROW:", _row)
                    print("ROW:", row)
                    print("row.sub_offset:", sub_offset)
                    exit(1)
            else:
                if offset == 0:
                    new_row = Row(hex_signature=sig, offset=offset, extension=[extension], sub_signatures=[sub], sub_offset=sub_offset, offset_every=offset_every)
                    # Add the new Row object to the dictionary, using the hex_signature as the key
                    rows_map[sig] = new_row
                else:
                    # We use a ListRow here because list rows don't have sub signatures or special cases, we can store less data.
                    new_row = ListRow(hex_signature=sig, offset=offset, extension=extension)
                    offset_list.append(new_row)

    if len(skipped_entries) > 0:
        print("Skipped entries:")
        for row in skipped_entries:
            print("\t", row)

# Create dist directory if it doesn't exist
if not os.path.exists("dist"):
    os.makedirs("dist")

json.dump(rows_map, open("dist/rows_map.json", "w"))
json.dump(offset_list, open("dist/offset_list.json", "w"))
lookup_map = rows_map_to_lookup_map(rows_map)
json.dump(lookup_map, open("dist/lookup_map.json", "w"))
print("Rows in map:", len(rows_map))
print("Rows in offset_list:", len(offset_list))