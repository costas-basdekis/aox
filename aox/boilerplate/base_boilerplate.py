"""
Interface for the class that knows where challenges parts are, and can create
new ones.
"""

__all__ = ['BaseBoilerplate']


class BaseBoilerplate:
    """
    A class to know where challenges parts are, and has the ability to create
    new ones.

    All such functionality should be delegated to a concrete subclass of this,
    since they might be different ways to structure code.
    """
    def extract_from_filename(self, filename):
        """Get year, day, and part, from a filename"""
        raise NotImplementedError()

    def get_part_filename(self, year: int, day: int, part: str,
                          relative: bool = False):
        """Get the filename for a part"""
        raise NotImplementedError()

    def get_day_directory(self, year: int, day: int, relative: bool = False):
        """Get the directory for a day"""
        raise NotImplementedError()

    def get_day_input_filename(self, year: int, day: int,
                               relative: bool = False):
        """Get the path for a day's input"""
        raise NotImplementedError()

    def get_year_directory(self, year: int, relative: bool = False):
        """Get the directory for a year"""
        raise NotImplementedError()

    def get_part_module_name(self, year: int, day: int, part: str):
        """Get the module name for a part"""
        raise NotImplementedError()

    def create_part(self, year, day, part):
        """Create a new part"""
        raise NotImplementedError()
