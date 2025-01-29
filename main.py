import os
import csv
import sys
import vedo
import concurrent.futures

def load_model(file_path):
    print(f"Loading {file_path}")
    mesh = vedo.Mesh(file_path)
    return mesh

def process_mesh_batches(reference_mesh_path, directory_path, concurrency=1):
    """
    Process STL files in parallel using the given concurrency level.
    """
    results = {}
    file_list = [filename for filename in os.listdir(directory_path) if filename.endswith('.stl')]

    # Load reference mesh once
    reference_mesh = load_model(reference_mesh_path)
    reference_pcd = vedo.Points(inputobj=reference_mesh)

    def process_mesh(filename):
        """
        Process a single mesh file by:
          - Loading the mesh
          - Aligning it to the reference
          - Calculating average squared distance, Chamfer distance, and Hausdorff distance
        """
        print(f"Processing {filename}")
        file_path = os.path.join(directory_path, filename)
        model_mesh = load_model(file_path)

        print(f"{filename}: Aligning model to reference")
        model_mesh.align_to(reference_mesh, use_centroids=True, rigid=True)

        print(f"{filename}: Computing average squared distance")
        d = 0
        for p in model_mesh.vertices:
            cpt = reference_mesh.closest_point(p)
            d += vedo.mag2(p - cpt)  # square of residual distance
        average_squared_distance = d / model_mesh.npoints

        model_pcd = vedo.Points(inputobj=model_mesh)

        print(f"{filename}: Computing Chamfer distance")
        chamfer_distance = model_pcd.chamfer_distance(reference_pcd)

        print(f"{filename}: Computing Hausdorff distance")
        hausdorff_distance = model_pcd.hausdorff_distance(reference_pcd)

        return filename, {
            'average_squared_distance': average_squared_distance,
            'chamfer_distance': chamfer_distance,
            'hausdorff_distance': hausdorff_distance
        }

    # Process files in parallel using a ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        future_to_filename = {executor.submit(process_mesh, f): f for f in file_list}

        for future in concurrent.futures.as_completed(future_to_filename):
            filename = future_to_filename[future]
            filename, result = future.result()
            results[filename] = result

    return results

if __name__ == "__main__":
    help_message = f"""
Usage:
  python3 {sys.argv[0]} <reference_model_path> <meshes_directory_path> <output_csv_path> [--concurrency N]

Example:
  python3 {sys.argv[0]} reference_model.stl meshes/ output.csv --concurrency 4

Required arguments:
  reference_model_path      Path to the reference STL file (e.g., reference_model.stl)
  meshes_directory_path     Path to the directory containing STL files to process
  output_csv_path           Path to the output CSV file

Optional arguments:
  --concurrency N           Number of files to process in parallel (default = 1)
  -h, --help                Show this help message and exit
"""

    if '-h' in sys.argv or '--help' in sys.argv or len(sys.argv) < 4:
        print(help_message)
        sys.exit(0 if ('-h' in sys.argv or '--help' in sys.argv) else 1)

    reference_model_path = sys.argv[1]
    meshes_directory_path = sys.argv[2]
    output_csv_path = sys.argv[3]

    concurrency = 1

    if '--concurrency' in sys.argv:
        try:
            idx = sys.argv.index('--concurrency')
            concurrency = int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            print("Error: --concurrency flag provided but no valid integer found.")
            print(help_message)
            sys.exit(1)

    results = process_mesh_batches(reference_model_path, meshes_directory_path, concurrency=concurrency)

    with open(output_csv_path, 'w', newline='') as csvfile:
        fieldnames = ['model', 'average_squared_distance', 'chamfer_distance', 'hausdorff_distance']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for filename, distances in results.items():
            writer.writerow({ 'model': filename, **distances})

    print("The results have been written to", output_csv_path)
