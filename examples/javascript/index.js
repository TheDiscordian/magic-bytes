var fs = require('fs');
var lookup_map = JSON.parse(fs.readFileSync('../../dist/lookup_map.json', 'utf8'));
var offset_list = JSON.parse(fs.readFileSync('../../dist/offset_list.json', 'utf8'));

function hex_to_bytes(hex) {
	hex = hex.replace(/ /g, "");
    let bytes = new Uint8Array(hex.length / 2);
    for (let c = 0; c < hex.length; c += 2)
        bytes[c/2] = parseInt(hex.substr(c, 2), 16);
    return bytes;
}

// ListRow = namedtuple('Row', ['hex_signature', 'offset', 'extension'])
function get_file_extension_from_bytes_offset_list(data, offset_list) {
	for (var i = 0; i < offset_list.length; i++) {
		var row = offset_list[i];
		var sig = hex_to_bytes(row[0]);
		if (data.slice(row[1], row[1] + sig.length).equals(sig)) {
			return row[2];
		}
	}
	return "unknown";
}

// MapRow = namedtuple('Row', ['extension', 'sub_signatures', 'sub_offset', 'offset_every'])
function get_file_extension_from_bytes_lookup_map(data, lookup_map) {
	for (var i = 0; i < data.length; i++) {
		var hex_key = data[i].toString(16).toLowerCase();
		if (hex_key in lookup_map) {
			lookup_map = lookup_map[hex_key];
		} else {
			if ("r" in lookup_map) {
				var row = lookup_map["r"];
				if (row[1][0].length == 0) {
					return row[0][0];
				} else {
					for (var j = 0; j < row[1].length; j++) {
						var sig = hex_to_bytes(row[1][j]);
						if (data.slice(i + row[2], i + row[2] + sig.length).equals(sig)) {
							return row[0][j];
						}
					}
					break;
				}
			} else {
				break;
			}
		}
	}
	return "unknown";
}

function get_file_extension_from_bytes(data, lookup_map, offset_list, prefer_offset=false) {
	if (prefer_offset){
		var result = get_file_extension_from_bytes_offset_list(data, offset_list);
	} else {
		var result = get_file_extension_from_bytes_lookup_map(data, lookup_map);
	}
	if (result == "unknown") {
		if (prefer_offset){
			result = get_file_extension_from_bytes_lookup_map(data, lookup_map);
		} else {
			result = get_file_extension_from_bytes_offset_list(data, offset_list);
		}
	}
	return result;
}

function get_file_extension(filename, lookup_map, offset_list=[]) {
	try {
		let data = fs.readFileSync(filename);
		return get_file_extension_from_bytes(data, lookup_map, offset_list);

	} catch (err) {
		throw err;
	}
}

var files = fs.readdirSync('../../samples');
let now = Date.now();
for (var i = 0; i < files.length; i++) {
	var file = files[i];
	var ext = get_file_extension('../../samples/' + file, lookup_map, offset_list);
	files[i] = file + " -> " + ext;
}
let since = Date.now() - now;
for (var i = 0; i < files.length; i++) {
	console.log(files[i]);
}
console.log("Took " + (since) + "ms");