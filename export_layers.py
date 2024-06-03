import os
import sys
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(filename='C:\\Users\\Nocturne\\Desktop\\Exporter\\export_layers.log', level=logging.DEBUG, format='%(asctime)s %(message)s')

# Set environment variables for QGIS
qgis_prefix_path = r"C:\Program Files\QGIS 3.36.3"
qt_plugin_path = os.path.join(qgis_prefix_path, r"apps\Qt5\plugins")
qgis_python_path = os.path.join(qgis_prefix_path, r"apps\qgis\python")
python_home = os.path.join(qgis_prefix_path, r"apps\Python312")

os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = qt_plugin_path
os.environ['QGIS_PREFIX_PATH'] = qgis_prefix_path
os.environ['PYTHONHOME'] = python_home
os.environ['PYTHONPATH'] = qgis_python_path

# Add QGIS Python and other necessary directories to PATH
os.environ['PATH'] += os.pathsep + os.path.join(qgis_prefix_path, r"apps\qgis\bin")
os.environ['PATH'] += os.pathsep + os.path.join(qgis_prefix_path, r"apps\Qt5\bin")
os.environ['PATH'] += os.pathsep + os.path.join(qgis_prefix_path, r"apps\Python312\Scripts")
os.environ['PATH'] += os.pathsep + python_home

# Add QGIS Python libraries to the path
sys.path.append(qgis_python_path)
sys.path.append(os.path.join(qgis_python_path, r"plugins"))
sys.path.append(os.path.join(python_home, r"Lib\site-packages"))

from qgis.core import (
    QgsProject,
    QgsVectorFileWriter,
    QgsMapLayer,
    QgsApplication,
    QgsCoordinateTransformContext,
    QgsVectorLayer
)
from qgis.PyQt.QtCore import QCoreApplication

def main():
    logging.info("Script started.")
    
    # Initialize QGIS Application (only needed if running outside QGIS environment)
    QCoreApplication.setOrganizationName("QGIS")
    QCoreApplication.setApplicationName("QGIS")
    qgs = QgsApplication([], False)
    qgs.initQgis()

    # Define the project file path
    project_file_path = r'C:\Users\Nocturne\Desktop\Exporter\exporter.qgz'

    # Get the current date and time for directory naming
    current_datetime = datetime.now().strftime('%Y-%m-%d_%I-%M-%S_%p')
    output_directory = os.path.join(r'C:\Users\Nocturne\Desktop\Exporter', f'output_{current_datetime}')

    # Ensure the output directory exists
    try:
        os.makedirs(output_directory, exist_ok=True)
        logging.info(f"Created output directory: {output_directory}")
    except Exception as e:
        logging.error(f"Failed to create output directory: {e}")
        return

    # Load the QGIS project
    project = QgsProject.instance()
    try:
        project.read(project_file_path)
        logging.info(f"Loaded project file: {project_file_path}")
    except Exception as e:
        logging.error(f"Failed to load project file: {e}")
        return

    # Export all vector layers to Shapefiles with the original names
    for layer in project.mapLayers().values():
        if isinstance(layer, QgsVectorLayer):
            layer_name = layer.name()
            layer_crs = layer.crs().authid()  # Get the CRS of the layer
            output_file = os.path.join(output_directory, f"{layer_name}.shp")
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = "ESRI Shapefile"
            options.fileEncoding = "UTF-8"
            transform_context = QgsCoordinateTransformContext()
            error, _ = QgsVectorFileWriter.writeAsVectorFormatV2(
                layer,
                output_file,
                transform_context,
                options
            )
            if error == QgsVectorFileWriter.NoError:
                logging.info(f"Successfully exported vector layer: {layer_name} with CRS: {layer_crs} to {output_file}")
            else:
                logging.error(f"Error exporting vector layer: {layer_name}, {error}")

    # Cleanup QGIS Application (only needed if running outside QGIS environment)
    qgs.exitQgis()
    logging.info("Script finished.")

if __name__ == "__main__":
    main()
