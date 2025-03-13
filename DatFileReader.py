from typing import Dict, Union, List, Tuple, Optional
import numpy as np
import os
import csv

class DatFileReader:
    """
    A class for reading and managing data from .DAT and .CSV files.

    This class reads a data file, storing header information and data points.
    It provides methods to access header info, x and y data, and individual data points.
    """

    def __init__(self, file_path: str, header_lines: int = 5) -> None:
        """
        Initialize the DatFileReader with a file path and number of header lines.

        Args:
            file_path (str): Path to the data file (.DAT or .CSV).
            header_lines (int, optional): Number of header lines in the file. Defaults to 5.
        """
        self.file_path: str = file_path
        self.header_lines: int = header_lines
        self.header_info: Dict[str, str] = {}
        self.x_data: Optional[np.ndarray] = None
        self.y_data: Union[np.ndarray, List[np.ndarray]] = None
        self._read_file()

    def _read_file(self) -> None:
        """
        Read the data file, extracting header information and data points.

        Supports both DAT and CSV formats.
        """
        file_extension = os.path.splitext(self.file_path)[1].lower()

        with open(self.file_path, 'r') as file:
            # Read header information
            for i in range(self.header_lines):
                line = file.readline().strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    self.header_info[key.strip()] = value.strip()
                elif ';' in line:
                    key, value = line.split(';', 1)
                    self.header_info[key.strip()] = value.strip()
                else:
                    self.header_info[f'Header_Line_{i + 1}'] = line

            # Read data points
            if file_extension == '.csv':
                csv_reader = csv.reader(file)
                data = []
                for row in csv_reader:
                    try:
                        # Filter out empty strings and convert to float
                        float_row = [float(cell) for cell in row if cell.strip()]
                        if float_row:  # Only append non-empty rows
                            data.append(float_row)
                    except ValueError:
                        # Skip rows that can't be converted to float
                        continue
                data = np.array(data)
            else:  # For .DAT files
                data = []
                for line in file:
                    try:
                        # Split the line by semicolon and convert to float, ignoring empty fields
                        float_row = [float(cell) for cell in line.strip().split(';') if cell.strip()]
                        if float_row:  # Only append non-empty rows
                            data.append(float_row)
                    except ValueError:
                        # Skip rows that can't be converted to float
                        continue
                data = np.array(data)

        if data.size > 0:
            self.x_data = data[:, 0]
            if data.shape[1] == 2:
                self.y_data = data[:, 1]
            else:
                self.y_data = [data[:, i] for i in range(1, data.shape[1])]
        else:
            raise ValueError("No valid data found in the file.")

    def get_y_data(self) -> Union[np.ndarray, List[np.ndarray]]:
        """
        Get the y-axis data.

        Returns:
            Union[np.ndarray, List[np.ndarray]]: An array containing all y-axis values if single-dimensional,
            or a list of arrays for multi-dimensional data.
        """
        return self.y_data

    def get_datapoints(self) -> np.ndarray:
        """
        Get all datapoints as a combined array of x and y values.

        Returns:
            np.ndarray: A 2D array where each row is a datapoint (x, y1, y2, ...).
        """
        if isinstance(self.y_data, np.ndarray):
            return np.column_stack((self.x_data, self.y_data))
        else:
            return np.column_stack([self.x_data] + self.y_data)

    def __getitem__(self, index: Union[int, slice, List[int], range]) -> np.ndarray:
        """
        Get a specific datapoint or multiple datapoints.

        Args:
            index (Union[int, slice, List[int], range]): The index, slice, list of indices, or range of datapoints to retrieve.

        Returns:
            np.ndarray: The requested datapoint(s).
        """
        if isinstance(index, (list, range)):
            x = self.x_data[index]
            if isinstance(self.y_data, np.ndarray):
                y = self.y_data[index]
            else:
                y = np.array([y[index] for y in self.y_data]).T
        else:
            x = self.x_data[index]
            if isinstance(self.y_data, np.ndarray):
                y = self.y_data[index]
            else:
                y = np.array([y[index] for y in self.y_data])

        if x.ndim == 0:  # Single item
            return np.hstack((x, y))
        else:  # Multiple items
            return np.column_stack((x, y))

    def get_y_for_x(self, x_value: float, x_range: Optional[float] = None) -> Union[np.ndarray, float, List[Union[np.ndarray, float]]]:
        """
        Get y value(s) for a specific x value or a range of x values.

        This method supports two modes of operation:
        1. Single x value (by only supplying x_value and not x_range):
           Returns the y value corresponding to the closest x value in the data.
        2. Range of x values (by supplying x_value and x_range):
           Returns all y values corresponding to x values within the specified range.

        Args:
            x_value (float): A single x value to query or the lower bound of the range.
            x_range (float, optional): The upper bound of the x range. Defaults to None.

        Returns:
            Union[np.ndarray, float, List[Union[np.ndarray, float]]]:
                - If only x_value is provided: Returns a single y value (float) or list of y values for multi-dimensional data.
                - If x_range is provided: Returns a 1D array or list of 1D arrays for multi-dimensional data.

        Raises:
            ValueError: If neither x_value nor x_range is provided.
        """
        if x_range is not None:
            x_min, x_max = x_value, x_range
            mask = (self.x_data >= x_min) & (self.x_data <= x_max)
            if isinstance(self.y_data, np.ndarray):
                return self.y_data[mask]
            else:
                return [y[mask] for y in self.y_data]
        elif x_value is not None:
            idx = np.argmin(np.abs(self.x_data - x_value))
            if isinstance(self.y_data, np.ndarray):
                return self.y_data[idx]
            else:
                return [y[idx] for y in self.y_data]
        else:
            raise ValueError("Either x_value or x_range must be provided")

    def get_header_value(self, key: str) -> Optional[str]:
        """
        Get a specific header value from the header information.

        Args:
            key (str): The key of the header value to retrieve.

        Returns:
            Optional[str]: The value associated with the key if found, None otherwise.
        """
        return self.header_info.get(key, None)

    def __len__(self):
        """
        Return the length of the data set. Prior to doing this it asserts that the x and y data have the same length.
        :return:
        """
        assert len(self.x_data) == len(self.y_data)
        return len(self.x_data)

    def get_index_for_x(self, x_value: float, tolerance: float = 1e-6) -> Optional[int]:
        """
        Find the index of the closest x value to the given x_value.

        Args:
            x_value (float): The x value to search for.
            tolerance (float, optional): The maximum allowed difference between the given x_value
                                         and the closest found value. Defaults to 1e-6.

        Returns:
            Optional[int]: The index of the closest x value if found within the tolerance, None otherwise.
        """
        if self.x_data is None:
            return None

        closest_index = np.argmin(np.abs(self.x_data - x_value))
        if np.abs(self.x_data[closest_index] - x_value) <= tolerance:
            return closest_index
        else:
            return None
