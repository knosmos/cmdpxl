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

Install the package with:
```sh
pip install cmdpxl
```

## Usage

Run with `cmdpxl`.

You can also specify the file path and resolution with cli, e.g., creating a new 10x10 image:

```
cmdpxl -f new_image.png -res 10,10
```
To get the full list of options:

```
$ cmdpxl --help
Usage: cmdpxl [OPTIONS]

Options:
  -f, --filepath PATH      Path for the file you want to open
  -res, --resolution TEXT  Image height and width separated by a comma, e.g.
                           10,10
  --help                   Show this message and exit.
  
```

## Why?
Good question.
