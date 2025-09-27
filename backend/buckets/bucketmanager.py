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
        Initialize the BucketManager with a default "free" bucket at 100%.
        
        Args:
            total_budget (float): Total budget amount available for allocation
        """
        self.buckets: Dict[str, Bucket] = {}
        self.total_budget = total_budget
        
        # Create default "free" bucket with 100% allocation
        free_bucket = Bucket("free", 100.0)
        self.buckets["free"] = free_bucket
    
    def add_bucket(self, name: str, percentage: float, current_value: float = 0.0) -> bool:
        """
        Add a new bucket to the manager, automatically resizing "free" bucket if needed.
        
        Args:
            name (str): Name of the bucket
            percentage (float): Percentage allocation (0-100)
            current_value (float): Deprecated. Ignored.
            
        Returns:
            bool: True if bucket was added successfully, False if "free" bucket doesn't have enough percentage
        """
        if name in self.buckets:
            raise ValueError(f"Bucket '{name}' already exists")
        
        # Check if "free" bucket has enough percentage to allocate
        if "free" in self.buckets:
            free_percentage = self.buckets["free"].get_percentage()
            if percentage > free_percentage:
                # If not enough, just use all that's left in free
                percentage = free_percentage
            if free_percentage == 0.0:
                return False
            # Resize "free" bucket to accommodate new bucket
            new_free_percentage = free_percentage - percentage
            self.buckets["free"].resize_percentage(new_free_percentage)
        else:
            # If no "free" bucket exists, check total percentage constraint
            current_total = self.get_total_percentage()
            if current_total + percentage > 100.0:
                return False
        
        bucket = Bucket(name, percentage)
        self.buckets[name] = bucket
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
            free_bucket = Bucket("free", needed_percentage)
            self.buckets["free"] = free_bucket
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
            # Try resizing the free bucket to 0 and try again
            if "free" in self.buckets and self.buckets["free"].get_percentage() > 0:
                free_old_pct = self.buckets["free"].get_percentage()
                self.buckets["free"].resize_percentage(0.0)
                total_without_bucket = self.get_total_percentage() - old_percentage
                if total_without_bucket + new_percentage > 100.0:
                    # Still not possible, revert free bucket and fail
                    self.buckets["free"].resize_percentage(free_old_pct)
                    return False
            else:
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
        by adjusting the "free" bucket when possible.
        
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

        # If modifying the free bucket, only allow exact total of 100%
        if name == "free":
            if abs(proposed_total - 100.0) > 0.01:
                return False
            target_bucket.resize_percentage(new_pct)
            return True

        # Adjust free bucket to keep total at 100%
        if "free" in self.buckets:
            free_bucket = self.buckets["free"]
            free_old = free_bucket.get_percentage()
            delta_pct = new_pct - old_pct
            free_new = free_old - delta_pct
            if free_new < -0.01:
                return False
            target_bucket.resize_percentage(new_pct)
            free_bucket.resize_percentage(max(free_new, 0.0))
            return True

        # No free bucket exists; enforce not exceeding 100%
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