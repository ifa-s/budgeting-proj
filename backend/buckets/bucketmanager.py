"""
BucketManager Class

A class that manages multiple budget buckets, ensuring their percentages 
add up to 100% and providing methods for financial operations.
"""

from typing import Dict, List, Optional
from backend.buckets.bucket import Bucket


class BucketManager:
    """
    Manages multiple budget buckets with percentage validation and financial operations.
    
    Attributes:
        buckets (Dict[str, Bucket]): Dictionary of bucket name to Bucket objects
        total_budget (float): Maximum budget amount to allocate across buckets
    """
    
    def __init__(self, total_budget: float = 0.0):
        """
        Initialize the BucketManager with no buckets. Unallocated space is
        implicitly (100 - sum of bucket percentages).
        
        Args:
            total_budget (float): Total budget amount available for allocation
        """
        self.buckets: Dict[str, Bucket] = {}
        self.total_budget = total_budget
    
    def add_bucket(self, name: str, percentage: float, current_value: float = 0.0) -> bool:
        """
        Add a new bucket to the manager if there is enough unallocated capacity.
        
        Args:
            name (str): Name of the bucket
            percentage (float): Percentage allocation (0-100)
            current_value (float): Deprecated. Ignored.
            
        Returns:
            bool: True if bucket was added successfully, False if insufficient unallocated percentage is available
        """
        if name in self.buckets:
            raise ValueError(f"Bucket '{name}' already exists")

        # Enforce total percentage constraint via unallocated space
        current_total = self.get_total_percentage()
        if current_total + percentage > 100.0 + 1e-6:
            return False
        
        bucket = Bucket(name, percentage)
        self.buckets[name] = bucket
        return True
    
    def remove_bucket(self, name: str) -> bool:
        """
        Remove a bucket from the manager.
        
        Args:
            name (str): Name of the bucket to remove
            
        Returns:
            bool: True if bucket was removed, False if bucket doesn't exist
        """
        if name not in self.buckets:
            return False
        
        # Remove the bucket (unallocated adjusts implicitly)
        del self.buckets[name]
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
        Check if the total percentage allocation does not exceed 100%.
        
        Returns:
            bool: True if total percentage ≤ 100% (within small epsilon), False otherwise
        """
        total = self.get_total_percentage()
        return total <= 100.0 + 0.01
    
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
        
        if total_without_bucket + new_percentage > 100.0 + 1e-6:
            return False
        self.buckets[name].resize_percentage(new_percentage)
        return True
    
    def set_total_budget(self, amount: float) -> None:
        """
        Set the total budget amount and update all bucket values accordingly.
        
        Args:
            amount (float): New total budget amount
        """
        self.total_budget = amount
    
    def get_total_budget(self) -> float:
        """
        Get the total budget amount.
        
        Returns:
            float: Total budget amount
        """
        return self.total_budget
    
    def add_amount_to_bucket(self, name: str, amount: float) -> bool:
        """
        Add an amount (in dollars) to a bucket by resizing its percentage
        based on the change relative to the total budget. Keeps total at 100%
        while enforcing that total percentages do not exceed 100%.
        
        Args:
            name (str): Name of the bucket
            amount (float): Amount to add
            
        Returns:
            bool: True if successful, False if bucket doesn't exist
        """
        if name not in self.buckets:
            return False
        if self.total_budget <= 0:
            return False

        target_bucket = self.buckets[name]
        old_pct = target_bucket.get_percentage()
        current_dollars = (old_pct / 100.0) * self.total_budget
        new_dollars = current_dollars + amount
        if new_dollars < 0:
            new_dollars = 0.0
        new_pct = (new_dollars / self.total_budget) * 100.0

        total_without_bucket = self.get_total_percentage() - old_pct
        proposed_total = total_without_bucket + new_pct

        # Enforce not exceeding 100% total
        if proposed_total > 100.0 + 1e-6:
            return False
        target_bucket.resize_percentage(new_pct)
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
        # Reuse the add logic with a negative amount
        return self.add_amount_to_bucket(name, -amount)
    
    def get_bucket_names(self) -> List[str]:
        """
        Get a list of all bucket names.
        
        Returns:
            List[str]: List of bucket names
        """
        return list(self.buckets.keys())
    
    def get_total_current_value(self) -> float:
        """
        Get the total allocated value across all buckets, computed from
        percentages and the total budget.
        
        Returns:
            float: Sum of allocations in dollars
        """
        return sum((bucket.get_percentage() / 100.0) * self.total_budget for bucket in self.buckets.values())
    
    def auto_resize_to_100_percent(self) -> bool:
        """
        Automatically resize all buckets proportionally to make total percentage equal 100%,
        but do not change the percentage of the bucket named 'rent'.
        
        Returns:
            bool: True if successful, False if no buckets exist
        """
        if not self.buckets:
            return False

        # Separate 'rent' bucket from others
        rent_bucket = self.buckets.get("rent")
        other_buckets = [b for name, b in self.buckets.items() if name != "rent"]

        # If all buckets are 'rent', nothing to do
        if not other_buckets and rent_bucket:
            return True

        # Compute total percentage for non-rent buckets
        rent_pct = rent_bucket.get_percentage() if rent_bucket else 0.0
        other_total = sum(b.get_percentage() for b in other_buckets)

        if other_total == 0:
            # If only rent has a percentage, set it to 100%
            if rent_bucket:
                rent_bucket.resize_percentage(100.0)
                return True
            return False

        # Scale only non-rent buckets to fill (100 - rent_pct)
        scaling_factor = (100.0 - rent_pct) / other_total

        for bucket in other_buckets:
            new_percentage = bucket.get_percentage() * scaling_factor
            bucket.resize_percentage(new_percentage)

        # Leave rent bucket unchanged
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