"""
Bucket Class

A class that represents a budget allocation as a percentage.
Supports resizing and tracking current values.
"""


class Bucket:
    """
    A bucket that allocates money as a percentage.
    
    Attributes:
        name (str): The name of the bucket
        percentage (float): The percentage allocation
        current_value (float): The current monetary value of this bucket
    """
    
    def __init__(self, name: str, percentage: float, current_value: float = 0.0):
        """
        Initialize a bucket.
        
        Args:
            name (str): Name of the bucket
            percentage (float): Percentage allocation
            current_value (float): Current monetary value
        """
        self.name = name
        self.percentage = percentage
        self.current_value = current_value
    
    def resize_percentage(self, new_percentage: float) -> None:
        """
        Resize the bucket by changing its percentage allocation.
        
        Args:
            new_percentage (float): New percentage
        """
        self.percentage = new_percentage
    
    def get_current_value(self) -> float:
        """
        Get the current monetary value of this bucket.
        @return: The current value of the bucket
        
        Returns:
            float: Current value in dollars
        """
        return self.current_value
    
    def get_percentage(self) -> float:
        """
        Get the current percentage allocation.
        
        Returns:
            float: Current percentage
        """
        return self.percentage
    
    def add_amount(self, amount: float) -> None:
        """
        Add a specific amount to the bucket.
        
        Args:
            amount (float): Amount to add
        """
        self.current_value += amount
    
    def subtract_amount(self, amount: float) -> None:
        """
        Subtract a specific amount from the bucket.
        
        Args:
            amount (float): Amount to subtract
        """
        self.current_value -= amount
    
    def set_amount(self, amount: float) -> None:
        """
        Set the bucket to a specific dollar amount.
        
        Args:
            amount (float): Amount to set
        """
        self.current_value = amount
    
    def __str__(self) -> str:
        """String representation of the budget bucket."""
        return (f"Bucket(name='{self.name}', "
                f"percentage={self.percentage:.2f}%, "
                f"current_value=${self.current_value:.2f})")
    
    def __repr__(self) -> str:
        """Detailed representation of the budget bucket."""
        return (f"Bucket(name='{self.name}', "
                f"percentage={self.percentage}, "
                f"current_value={self.current_value})")