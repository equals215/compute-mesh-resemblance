# compute-mesh-resemblance
Small yet effective program to compute metrics used to compare mesh models resemblance to a reference model using vedo library in Python 3.  

## Usage
```bash
Usage:
  python3 main.py <reference_model_path> <meshes_directory_path> <output_csv_path> [--concurrency N]

Example:
  python3 main.py reference_model.stl meshes/ output.csv --concurrency 4

Required arguments:
  reference_model_path      Path to the reference STL file (e.g., reference_model.stl)
  meshes_directory_path     Path to the directory containing STL files to process
  output_csv_path           Path to the output CSV file

Optional arguments:
  --concurrency N           Number of files to process in parallel (default = 1)
  -h, --help                Show this help message and exit
```

## Installation
```bash
pip3 install -r requirements.txt
```

## Credits
This program was developed by [Thomas Foubert](https://github.com/equals215) with the help of the [vedo library](https://vedo.embl.es/) in Python 3.  
Any use of this program should cite the author of this code and the vedo library.

## License
This program is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for more information.  
`vedo` library is licensed under the MIT License. See the [LICENSE](https://github.com/marcomusy/vedo/blob/master/LICENSE) file for more information.