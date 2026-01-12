import os
import shutil
from pathlib import Path

def fix_env_trailing_spaces(env_path: Path):
    """
    Reads the .env file, removes trailing spaces from values,
    and saves it back after creating a backup.
    """
    if not env_path.exists():
        print(f"Error: {env_path} does not exist.")
        return

    # Create backup
    backup_path = env_path.with_suffix(".env.bak")
    shutil.copy2(env_path, backup_path)
    print(f"Created backup at {backup_path}")

    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    cleaned_lines = []
    fixed_count = 0

    for line in lines:
        stripped_line = line.rstrip("\n")
        
        # Process lines that look like KEY=VALUE
        if "=" in stripped_line and not stripped_line.strip().startswith("#"):
            key, value = stripped_line.split("=", 1)
            # Remove trailing spaces from value
            cleaned_value = value.rstrip()
            
            if cleaned_value != value:
                fixed_count += 1
                cleaned_lines.append(f"{key}={cleaned_value}\n")
            else:
                cleaned_lines.append(line)
        else:
            # Preserve comments and empty lines as is
            cleaned_lines.append(line)

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(cleaned_lines)

    print(f"Successfully cleaned .env file. Fixed {fixed_count} lines.")

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    fix_env_trailing_spaces(env_file)
