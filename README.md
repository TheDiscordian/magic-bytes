# What is this?

This is a language agnostic way to identify file types by their magic numbers.

This supports every signature in https://en.wikipedia.org/wiki/List_of_file_signatures, with some changes & additions.

For usage, see the [examples directory](./examples).

## Different files

- [file_sigs.csv](./file_sigs.csv) is the source of truth for file signatures.
- [dist/rows_map.json](./dist/rows_map.json) is a map of all the file signatures, except those in `offset_list.json`, it's primarily used for generating `lookup_map.json`.
- [dist/offset_list.json](./dist/offset_list.json) is a list of all the file signatures that need to be checked at a specific offset.
- [dist/lookup_map.json](./dist/lookup_map.json) is a lookup map of all the file signatures, except those in `offset_list.json`. It's used to quickly lookup a signature of unknown length.

# Extensions

## Additions

Add new extensions by modifying [file_sigs.csv](./file_sigs.csv), put it in this list, then run `python3 convert.py`. Afterwards, submit a PR. All contributions are loved and welcome.

## Supported extensions (shortened, see CSV for full list)


| Extension | Description | File Type |
| --------- | ----------- | --------- |
| .7z       | 7-Zip File Format | Archive |
| .bz2      | Bzip2 Compressed File | Archive |
| .gz       | Gzip Compressed File | Archive |
| .rar      | RAR Archive File | Archive |
| .tar      | Tape Archive File | Archive |
| .tar.gz   | Compressed Tarball File | Archive |
| .zip      | ZIP Archive File | Archive |
| .class    | Java Class File | Executable |
| .crx      | Chrome Extension File | Executable |
| .elf      | Executable and Linkable Format File | Executable |
| .exe      | Windows Executable File | Executable |
| .bmp      | Bitmap Image File | Image |
| .cr2      | Canon Raw Image File | Image |
| .flif     | Free Lossless Image Format File | Image |
| .gif      | Graphical Interchange Format File | Image |
| .ico      | Icon File | Image |
| .jpg      | JPEG Image File | Image |
| .png      | Portable Network Graphics File | Image |
| .svg      | Scalable Vector Graphics File | Image |
| .tif      | Tagged Image File Format | Image |
| .webp     | WebP Image File | Image |
| .eot      | Embedded OpenType Font File | Font |
| .otf      | OpenType Font File
