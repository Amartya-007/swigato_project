\
# filepath: g:\\swigato_project\\utils\\validation.py
from rich.console import Console
import re

console = Console()

def get_validated_input(prompt: str, validation_type: str, options: dict = None, optional: bool = False, default_value: str | None = None, custom_error_message: str | None = None) -> str | None:
    """
    Prompts the user for input and validates it based on the validation_type.

    Args:
        prompt (str): The message to display to the user.
        validation_type (str): The type of validation to perform.
                               Supported types: "not_empty", "integer", "yes_no", "choice", "float_positive", "regex".
        options (dict, optional): Additional options for validation.
                                  For "integer": {"min_val": int, "max_val": int}
                                  For "choice": {"choices": list_of_strings}
                                  For "float_positive": No options needed.
                                  For "not_empty": {"is_password": bool}
                                  For "regex": {"pattern": str} # Pattern for regex validation
        optional (bool, optional): If True and user enters empty string, returns default_value. Defaults to False.
        default_value (str | None, optional): The value to return if optional is True and input is empty. Defaults to None.
        custom_error_message (str | None, optional): A custom error message to display for validation failure.

    Returns:
        str | None: The validated user input, or default_value if applicable.
    """
    if options is None:
        options = {}

    while True:
        # Determine if input should be hidden (for passwords)
        is_password_input = False
        if validation_type == "not_empty" and options.get("is_password", False):
            is_password_input = True
        
        user_input = console.input(prompt, password=is_password_input).strip()

        if optional and not user_input: # If field is optional and user entered nothing
            return default_value

        if validation_type == "not_empty":
            if user_input: # If not optional, or if optional but user provided input
                return user_input
            else: # This case should only be hit if not optional and input is empty
                console.print(custom_error_message or "[red]Input cannot be empty. Please try again.[/red]")
        
        elif validation_type == "integer":
            # If optional and empty, it's already handled above and default_value returned.
            # If not optional and empty, it will fall through to ValueError or specific message.
            if not user_input: # Handles case where input is empty and not optional
                console.print(custom_error_message or "[red]Input cannot be empty. Please enter a whole number.[/red]")
                continue
            try:
                num = int(user_input)
                min_val = options.get("min_val")
                max_val = options.get("max_val")
                if (min_val is None or num >= min_val) and \
                   (max_val is None or num <= max_val):
                    return user_input # Return as string, convert in calling function if needed
                else:
                    if min_val is not None and max_val is not None:
                        console.print(custom_error_message or f"[red]Please enter a number between {min_val} and {max_val}.[/red]")
                    elif min_val is not None:
                        console.print(custom_error_message or f"[red]Please enter a number greater than or equal to {min_val}.[/red]")
                    elif max_val is not None:
                        console.print(custom_error_message or f"[red]Please enter a number less than or equal to {max_val}.[/red]")
                    else: # Should not happen
                         console.print(custom_error_message or f"[red]Invalid range for input.[/red]")
            except ValueError:
                console.print(custom_error_message or "[red]Invalid input. Please enter a whole number.[/red]")

        elif validation_type == "yes_no":
            # yes/no is typically not optional in the same way, but if it were and empty:
            if not user_input:
                 console.print(custom_error_message or "[red]Input cannot be empty. Please enter 'yes' or 'no'.[/red]")
                 continue
            if user_input.lower() in ['yes', 'y', 'no', 'n']:
                return user_input.lower()
            else:
                console.print(custom_error_message or "[red]Invalid input. Please enter 'yes' or 'no' (or 'y'/'n').[/red]")

        elif validation_type == "choice":
            if not user_input: # Choices are generally not optional without input
                 console.print(custom_error_message or "[red]Input cannot be empty. Please make a selection.[/red]")
                 continue
            valid_choices = options.get("choices", [])
            if user_input in valid_choices:
                return user_input
            else:
                console.print(custom_error_message or f"[red]Invalid choice. Please select from: {', '.join(valid_choices)}[/red]")
        
        elif validation_type == "float_positive":
            if not user_input:
                console.print(custom_error_message or "[red]Input cannot be empty. Please enter a positive number.[/red]")
                continue
            try:
                num = float(user_input)
                if num > 0:
                    return user_input # Return as string
                else:
                    console.print(custom_error_message or "[red]Please enter a positive number.[/red]")
            except ValueError:
                console.print(custom_error_message or "[red]Invalid input. Please enter a valid number.[/red]")
        
        elif validation_type == "regex":
            if not user_input and not optional: # Not optional and empty
                console.print(custom_error_message or "[red]Input cannot be empty.[/red]")
                continue
            # If optional and empty, it's handled at the beginning.
            # If not empty (whether optional or not), proceed with regex validation.
            
            pattern = options.get("pattern")
            if not pattern:
                console.print("[bold red]Configuration error: Regex pattern not provided for validation.[/bold red]")
                return None # Or raise an error

            import re
            if re.fullmatch(pattern, user_input):
                return user_input
            else:
                console.print(custom_error_message or "[red]Invalid format. Please try again.[/red]")
                
        else:
            console.print(f"[bold red]Unknown validation type: {validation_type}[/bold red]")
            return None # Or raise an error

def is_valid_password(password: str) -> tuple[bool, str]:
    """
    Validates a password based on the following criteria:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character (e.g., !@#$%^&*)
    Returns a tuple: (is_valid, message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password): # \d is for digit
        return False, "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        return False, "Password must contain at least one special character."
    return True, "Password is valid."
