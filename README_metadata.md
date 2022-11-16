# Get metadata

First download azcopy: https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10

Then get the full filelist
```bash
mkdir metadata
./azcopy list https://lilablobssc.blob.core.windows.net/wellington-unzipped/images > metadata/filelist.txt
```

We can create a subset of the metadata for testing
```bash
cat filelist.txt | head -n 1000 | cut -d ' ' -f 2 | cut -d ';' -f 1 > metasubset.txt
```