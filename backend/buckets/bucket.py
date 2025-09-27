"""
Bucket Class

A class that represents a budget allocation as a percentage.
Supports resizing.
"""


class Bucket:
    """
    A bucket that allocates money as a percentage.
    
    Attributes:
        name (str): The name of the bucket
        percentage (float): The percentage allocation
    """
    
    def __init__(self, name: str, percentage: float):
        """
        Initialize a bucket.
        
        Args:
            name (str): Name of the bucket
            percentage (float): Percentage allocation
        """
        self.name = name
        self.percentage = percentage
    
    def resize_percentage(self, new_percentage: float) -> None:
        """
        Resize the bucket by changing its percentage allocation.
        
        Args:
            new_percentage (float): New percentage
        """
        self.percentage = new_percentage
    
    def get_percentage(self) -> float:
        """
        Get the current percentage allocation.
        
        Returns:
            float: Current percentage
        """
        return self.percentage
    
    def __str__(self) -> str:
        """String representation of the budget bucket."""
        return (f"Bucket(name='{self.name}', "
                f"percentage={self.percentage:.2f}%)")
    
    def __repr__(self) -> str:
        """Detailed representation of the budget bucket."""
        return (f"Bucket(name='{self.name}', "
                f"percentage={self.percentage})")