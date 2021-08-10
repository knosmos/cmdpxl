# cmdpxl: a totally practical command-line image editor
![ezgif com-gif-maker (2)](https://user-images.githubusercontent.com/30610197/128618252-d00100dd-6ca4-4089-b7a1-d7790b99a1cc.gif)

## Features
cmdpxl has many exciting functionalities, including
- Editing pixels *one at a time*!
- Saving images!
- An undo function!
- A fill tool!
- Cool image filters!

## Installation
Requires `opencv-python`. It *should* be multiplatform, but it has only been tested on Windows 10.

To install requirements, run:

```sh
pip install -r requirements.txt
```

## Usage

Run with `py cmdpxl/main.py`, or as follows: 

`py cmdpxl/main.py -f new_image.png -res 10,10`

To edit an existing file:

`py cmdpxl/main.py -f file.png`

## Why?
Good question.
