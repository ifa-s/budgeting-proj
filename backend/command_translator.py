"""
Command Translator for BucketManager

This class translates simple, space-delimited commands from the backend prompt
into real Python method calls on the BucketManager class. It parses commands by
looking at the first word in each line as the command, e.g.:
- SET_TOTAL_BUDGET <amount>
- ADD_BUCKET <name> <percentage> [<current_value>]
- REMOVE_BUCKET <name>
- RESIZE_BUCKET <name> <new_percentage>
- ADD_AMOUNT <name> <amount>
- SUBTRACT_AMOUNT <name> <amount>
- REBALANCE
- AUTO_RESIZE_TO_100

and executes them using the actual BucketManager methods.
"""

from typing import List, Optional, Tuple

from backend.buckets.bucketmanager import BucketManager


class CommandTranslator:
    """Translates backend commands into BucketManager method calls."""
    
    def __init__(self):
        """Initialize the translator with a BucketManager instance."""
        self.bucket_manager = BucketManager()
    
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
        """Parse a command by taking the first word as the command name.

        Returns the uppercased command type and the remaining tokens as args.
        """
        line = command.strip()
        if not line:
            return None
        tokens = line.split()
        if not tokens:
            return None
        cmd_type = tokens[0].upper()
        args = tokens[1:]
        return cmd_type, args
    
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
                
                # Check if bucket already exists
                existing_bucket = self.bucket_manager.get_bucket(name)
                if existing_bucket is not None:
                    # Bucket exists, resize it instead
                    success = self.bucket_manager.resize_bucket(name, percentage)
                    if success:
                        return f"✅ Resized existing bucket '{name}' to {percentage}%"
                    else:
                        return f"❌ Failed to resize bucket '{name}' - would exceed 100% total"
                else:
                    # Bucket doesn't exist, add it
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
                # Auto-create bucket at 0.00% if it doesn't exist
                created = False
                if self.bucket_manager.get_bucket(name) is None:
                    # Create with 0% so it's always feasible
                    self.bucket_manager.add_bucket(name, 0.0)
                    created = True
                success = self.bucket_manager.add_amount_to_bucket(name, amount)
                if success:
                    if created:
                        return (
                            f"✅ Created bucket '{name}' at 0.00% and added ${amount:.2f}"
                        )
                    return f"✅ Added ${amount:.2f} to bucket '{name}'"
                else:
                    return f"❌ Failed to add amount to bucket '{name}' - bucket doesn't exist"
                    
            elif cmd_type == 'SUBTRACT_AMOUNT':
                name = args[0]
                amount = float(args[1])
                # Auto-create bucket at 0.00% if it doesn't exist
                created = False
                if self.bucket_manager.get_bucket(name) is None:
                    self.bucket_manager.add_bucket(name, 0.0)
                    created = True
                success = self.bucket_manager.subtract_amount_from_bucket(name, amount)
                if success:
                    if created:
                        return (
                            f"✅ Created bucket '{name}' at 0.00% and subtracted ${amount:.2f}"
                        )
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
    

