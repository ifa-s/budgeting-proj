"""
BucketManager Class

A class that manages multiple budget buckets, ensuring their percentages 
add up to 100% and providing methods for financial operations.
"""

from typing import Dict, List, Optional
from bucket import Bucket


class BucketManager:
    """
    Manages multiple budget buckets with percentage validation and financial operations.
    
    Attributes:
        buckets (Dict[str, Bucket]): Dictionary of bucket name to Bucket objects
        total_budget (float): Maximum budget amount to allocate across buckets
    """
    
    def __init__(self, total_budget: float = 0.0):
        """
        Initialize the BucketManager with a default "free" bucket at 100%.
        
        Args:
            total_budget (float): Total budget amount available for allocation
        """
        self.buckets: Dict[str, Bucket] = {}
        self.total_budget = total_budget
        
        # Create default "free" bucket with 100% allocation
        free_bucket = Bucket("free", 100.0, total_budget)
        self.buckets["free"] = free_bucket
    
    def add_bucket(self, name: str, percentage: float, current_value: float = 0.0) -> bool:
        """
        Add a new bucket to the manager, automatically resizing "free" bucket if needed.
        
        Args:
            name (str): Name of the bucket
            percentage (float): Percentage allocation (0-100)
            current_value (float): Initial monetary value
            
        Returns:
            bool: True if bucket was added successfully, False if "free" bucket doesn't have enough percentage
        """
        if name in self.buckets:
            raise ValueError(f"Bucket '{name}' already exists")
        
        # Check if "free" bucket has enough percentage to allocate
        if "free" in self.buckets:
            free_percentage = self.buckets["free"].get_percentage()
            if percentage > free_percentage:
                return False
            
            # Resize "free" bucket to accommodate new bucket
            new_free_percentage = free_percentage - percentage
            self.buckets["free"].resize_percentage(new_free_percentage)
        else:
            # If no "free" bucket exists, check total percentage constraint
            current_total = self.get_total_percentage()
            if current_total + percentage > 100.0:
                return False
        
        bucket = Bucket(name, percentage, current_value)
        self.buckets[name] = bucket
        self._update_bucket_values()
        return True
    
    def remove_bucket(self, name: str) -> bool:
        """
        Remove a bucket from the manager, adding its percentage back to "free" bucket.
        
        Args:
            name (str): Name of the bucket to remove
            
        Returns:
            bool: True if bucket was removed, False if bucket doesn't exist
        """
        if name not in self.buckets:
            return False
        
        # Don't allow removing the "free" bucket
        if name == "free":
            return False
        
        # Get the percentage of the bucket being removed
        removed_percentage = self.buckets[name].get_percentage()
        
        # Remove the bucket
        del self.buckets[name]
        
        # Add the percentage back to "free" bucket
        if "free" in self.buckets:
            # If "free" bucket exists, add the removed percentage to it
            current_free_percentage = self.buckets["free"].get_percentage()
            new_free_percentage = current_free_percentage + removed_percentage
            self.buckets["free"].resize_percentage(new_free_percentage)
        else:
            # If "free" bucket doesn't exist, create it with the removed percentage
            # Calculate what percentage is needed to make it 100%
            current_total = self.get_total_percentage()
            needed_percentage = 100.0 - current_total
            free_bucket = Bucket("free", needed_percentage, 0.0)
            self.buckets["free"] = free_bucket
        
        self._update_bucket_values()
        return True
    
    def get_bucket(self, name: str) -> Optional[Bucket]:
        """
        Get a bucket by name.
        
        Args:
            name (str): Name of the bucket
            
        Returns:
            Optional[Bucket]: The bucket if found, None otherwise
        """
        return self.buckets.get(name)
    
    def get_total_percentage(self) -> float:
        """
        Calculate the total percentage allocation across all buckets.
        
        Returns:
            float: Total percentage (should be <= 100.0)
        """
        return sum(bucket.get_percentage() for bucket in self.buckets.values())
    
    def is_percentage_valid(self) -> bool:
        """
        Check if the total percentage allocation equals 100%.
        
        Returns:
            bool: True if percentages add up to 100%, False otherwise
        """
        total = self.get_total_percentage()
        return abs(total - 100.0) < 0.01  # Allow for small floating point errors
    
    def get_percentage_difference(self) -> float:
        """
        Get the difference between current total percentage and 100%.
        
        Returns:
            float: Difference (positive means over 100%, negative means under 100%)
        """
        return self.get_total_percentage() - 100.0
    
    def resize_bucket(self, name: str, new_percentage: float) -> bool:
        """
        Resize a bucket's percentage allocation.
        
        Args:
            name (str): Name of the bucket to resize
            new_percentage (float): New percentage allocation
            
        Returns:
            bool: True if resize was successful, False if it would cause invalid total percentage
        """
        if name not in self.buckets:
            raise ValueError(f"Bucket '{name}' does not exist")
        
        old_percentage = self.buckets[name].get_percentage()
        total_without_bucket = self.get_total_percentage() - old_percentage
        
        if total_without_bucket + new_percentage > 100.0:
            return False
        
        self.buckets[name].resize_percentage(new_percentage)
        self._update_bucket_values()
        return True
    
    def set_total_budget(self, amount: float) -> None:
        """
        Set the total budget amount and update all bucket values accordingly.
        
        Args:
            amount (float): New total budget amount
        """
        self.total_budget = amount
        self._update_bucket_values()
    
    def get_total_budget(self) -> float:
        """
        Get the total budget amount.
        
        Returns:
            float: Total budget amount
        """
        return self.total_budget
    
    def _update_bucket_values(self) -> None:
        """
        Update all bucket current values based on their percentages and total budget.
        """
        for bucket in self.buckets.values():
            allocated_amount = (bucket.get_percentage() / 100.0) * self.total_budget
            bucket.set_amount(allocated_amount)
    
    def add_amount_to_bucket(self, name: str, amount: float) -> bool:
        """
        Add an amount to a specific bucket.
        
        Args:
            name (str): Name of the bucket
            amount (float): Amount to add
            
        Returns:
            bool: True if successful, False if bucket doesn't exist
        """
        if name not in self.buckets:
            return False
        
        self.buckets[name].add_amount(amount)
        return True
    
    def subtract_amount_from_bucket(self, name: str, amount: float) -> bool:
        """
        Subtract an amount from a specific bucket.
        
        Args:
            name (str): Name of the bucket
            amount (float): Amount to subtract
            
        Returns:
            bool: True if successful, False if bucket doesn't exist
        """
        if name not in self.buckets:
            return False
        
        self.buckets[name].subtract_amount(amount)
        return True
    
    def get_bucket_names(self) -> List[str]:
        """
        Get a list of all bucket names.
        
        Returns:
            List[str]: List of bucket names
        """
        return list(self.buckets.keys())
    
    def get_total_current_value(self) -> float:
        """
        Get the total current value across all buckets.
        
        Returns:
            float: Sum of all bucket current values
        """
        return sum(bucket.get_current_value() for bucket in self.buckets.values())
    
    def rebalance_buckets(self) -> None:
        """
        Rebalance all buckets to match their percentage allocations based on total budget.
        This will reset all current values to match the percentage * total_budget.
        """
        self._update_bucket_values()
    
    def auto_resize_to_100_percent(self) -> bool:
        """
        Automatically resize all buckets proportionally to make total percentage equal 100%.
        
        Returns:
            bool: True if successful, False if no buckets exist
        """
        if not self.buckets:
            return False
        
        current_total = self.get_total_percentage()
        if current_total == 0:
            return False
        
        scaling_factor = 100.0 / current_total
        
        for bucket in self.buckets.values():
            new_percentage = bucket.get_percentage() * scaling_factor
            bucket.resize_percentage(new_percentage)
        
        self._update_bucket_values()
        return True
    
    def __str__(self) -> str:
        """String representation of the BucketManager."""
        bucket_info = "\n".join(f"  {bucket}" for bucket in self.buckets.values())
        total_pct = self.get_total_percentage()
        return (f"BucketManager(total_budget=${self.total_budget:.2f}, "
                f"total_percentage={total_pct:.2f}%):\n{bucket_info}")
    
    def __repr__(self) -> str:
        """Detailed representation of the BucketManager."""
        return (f"BucketManager(total_budget={self.total_budget}, "
                f"buckets={len(self.buckets)}, "
                f"total_percentage={self.get_total_percentage()})")