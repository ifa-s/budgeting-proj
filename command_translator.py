"""
Command Translator for BucketManager

This class translates "fake" function calls from the backend prompt into real Python
method calls on the BucketManager class. It parses commands like:
- SET_TOTAL_BUDGET <amount>
- ADD_BUCKET <name> <percentage> [<current_value>]
- REMOVE_BUCKET <name>
- RESIZE_BUCKET <name> <new_percentage>
- ADD_AMOUNT <name> <amount>
- SUBTRACT_AMOUNT <name> <amount>
- REBALANCE
- AUTO_RESIZE_TO_100

And executes them using the actual BucketManager methods.
"""

import sys
import re
from typing import List, Optional, Tuple
from pathlib import Path

# Add the backend directory to the path so we can import BucketManager
sys.path.append(str(Path(__file__).parent / "backend"))

try:
    from backend.buckets.bucketmanager import BucketManager
except ImportError as e:
    raise ImportError(f"Error importing BucketManager: {e}. Make sure the backend/buckets directory exists and contains bucketmanager.py")


class CommandTranslator:
    """Translates backend commands into BucketManager method calls."""
    
    def __init__(self):
        """Initialize the translator with a BucketManager instance."""
        self.bucket_manager = BucketManager()
        self.command_patterns = {
            'SET_TOTAL_BUDGET': r'SET_TOTAL_BUDGET\s+(\d+(?:\.\d+)?)',
            'ADD_BUCKET': r'ADD_BUCKET\s+(\w+)\s+(\d+(?:\.\d+)?)(?:\s+(\d+(?:\.\d+)?))?',
            'REMOVE_BUCKET': r'REMOVE_BUCKET\s+(\w+)',
            'RESIZE_BUCKET': r'RESIZE_BUCKET\s+(\w+)\s+(\d+(?:\.\d+)?)',
            'ADD_AMOUNT': r'ADD_AMOUNT\s+(\w+)\s+(\d+(?:\.\d+)?)',
            'SUBTRACT_AMOUNT': r'SUBTRACT_AMOUNT\s+(\w+)\s+(\d+(?:\.\d+)?)',
            'REBALANCE': r'REBALANCE',
            'AUTO_RESIZE_TO_100': r'AUTO_RESIZE_TO_100'
        }
    
    def __call__(self, command_string: str) -> str:
        """
        Make the class callable with a command string.
        
        Args:
            command_string (str): The command string to execute
            
        Returns:
            str: Result message from executing the command
        """
        commands = command_string.strip().split('\n')
        results = []
        
        for command in commands:
            command = command.strip()
            if command and command != "NO_ACTION":
                result = self.execute_command(command)
                results.append(result)
        
        return '\n'.join(results)
    
    def get_status(self) -> str:
        """Get the current status of the BucketManager as a string."""
        status_lines = [
            "="*60,
            "CURRENT BUCKET MANAGER STATUS",
            "="*60,
            str(self.bucket_manager),
            f"Total percentage: {self.bucket_manager.get_total_percentage():.2f}%",
            f"Percentage valid: {self.bucket_manager.is_percentage_valid()}",
            "="*60
        ]
        return '\n'.join(status_lines)
    
    def parse_command(self, command: str) -> Optional[Tuple[str, List[str]]]:
        """
        Parse a command string and return the command type and arguments.
        
        Args:
            command (str): The command string to parse
            
        Returns:
            Optional[Tuple[str, List[str]]]: Command type and arguments, or None if invalid
        """
        command = command.strip()
        
        for cmd_type, pattern in self.command_patterns.items():
            match = re.match(pattern, command, re.IGNORECASE)
            if match:
                args = list(match.groups())
                # Remove None values (optional arguments that weren't provided)
                args = [arg for arg in args if arg is not None]
                return cmd_type, args
        
        return None
    
    def execute_command(self, command: str) -> str:
        """
        Execute a single command.
        
        Args:
            command (str): The command to execute
            
        Returns:
            str: Result message from executing the command
        """
        parsed = self.parse_command(command)
        if not parsed:
            return f"Invalid command: {command}"
        
        cmd_type, args = parsed
        
        try:
            if cmd_type == 'SET_TOTAL_BUDGET':
                amount = float(args[0])
                self.bucket_manager.set_total_budget(amount)
                return f"✅ Set total budget to ${amount:.2f}"
                
            elif cmd_type == 'ADD_BUCKET':
                name = args[0]
                percentage = float(args[1])
                current_value = float(args[2]) if len(args) > 2 else 0.0
                
                success = self.bucket_manager.add_bucket(name, percentage, current_value)
                if success:
                    return f"✅ Added bucket '{name}' with {percentage}% allocation"
                else:
                    return f"❌ Failed to add bucket '{name}' - insufficient percentage available"
                    
            elif cmd_type == 'REMOVE_BUCKET':
                name = args[0]
                success = self.bucket_manager.remove_bucket(name)
                if success:
                    return f"✅ Removed bucket '{name}'"
                else:
                    return f"❌ Failed to remove bucket '{name}' - bucket doesn't exist or is 'free'"
                    
            elif cmd_type == 'RESIZE_BUCKET':
                name = args[0]
                new_percentage = float(args[1])
                success = self.bucket_manager.resize_bucket(name, new_percentage)
                if success:
                    return f"✅ Resized bucket '{name}' to {new_percentage}%"
                else:
                    return f"❌ Failed to resize bucket '{name}' - would exceed 100% total"
                    
            elif cmd_type == 'ADD_AMOUNT':
                name = args[0]
                amount = float(args[1])
                success = self.bucket_manager.add_amount_to_bucket(name, amount)
                if success:
                    return f"✅ Added ${amount:.2f} to bucket '{name}'"
                else:
                    return f"❌ Failed to add amount to bucket '{name}' - bucket doesn't exist"
                    
            elif cmd_type == 'SUBTRACT_AMOUNT':
                name = args[0]
                amount = float(args[1])
                success = self.bucket_manager.subtract_amount_from_bucket(name, amount)
                if success:
                    return f"✅ Subtracted ${amount:.2f} from bucket '{name}'"
                else:
                    return f"❌ Failed to subtract amount from bucket '{name}' - bucket doesn't exist"
                    
            elif cmd_type == 'REBALANCE':
                self.bucket_manager.rebalance_buckets()
                return "✅ Rebalanced all buckets to match percentage allocations"
                
            elif cmd_type == 'AUTO_RESIZE_TO_100':
                success = self.bucket_manager.auto_resize_to_100_percent()
                if success:
                    return "✅ Auto-resized all buckets to total 100%"
                else:
                    return "❌ Failed to auto-resize - no buckets exist"
            
            return "Unknown command type"
            
        except ValueError as e:
            return f"❌ Invalid argument: {e}"
        except Exception as e:
            return f"❌ Error executing command: {e}"
    
