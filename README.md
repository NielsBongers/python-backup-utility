# Python backup utility 

## Overview 

A simple Python utility that creates backups of a certain root folder, excluding specified subfolders, and copies them over. After copying, the hashes of the source and destinations are compared. This takes quite some time, and if files change, the code may complain, so it's recommended to this while not in use. 

## Features 

### Overwrite-protection 

A target folder is created with the current date. If this folder already exists (for example, if the code is ran twice, or if the date on the machine is changed), a subfolder with a UUID as name will be created, to prevent overwriting previous backups. 

### Hashing 

During each run, a SHA1 hash for each file is made, and saved for the source files. Then, after copying, the destination hashes are also calculated, and the overall folder's mesh is compared, warning if they do not match. This can take a long time, so if this is an issue, it can be disabled in the config by setting ```compare_hashes: false```. 

### Excluded folders

In the ```config.yaml```, folders can be excluded. By default, I have excluded the Google Drive synchronization folders - those tend to give errors. 

```yaml
excluded_folders: 
    - .tmp.driveupload
    - .tmp.drivedownload
    - Folders 
    - That 
    - Don't 
    - Need 
    - Backups 
```

### VeraCrypt 

I use an external drive encrypted with VeraCrypt. If set in the YAML config, and a `password.yaml` file is created in the ```config``` folder, a drive can automatically be unlocked to a drive letter (by default this is ```Q://```). 

````yaml
password: [veracrypt-password]
````

## Future plans 

I wrote this because I wanted to improve on my current simple ```robocopy``` script, and because I wanted to explore using Python for sysadmin tasks, instead of shell scripts/PowerShell/Batch. I am curious about checking hashes for individual files, and only copying them over if changes have occurred, while maintaining reliability. 