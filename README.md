# ALX Project Scraper

This script logs into the ALX intranet, scrapes the current projects, and stores the project IDs and names in a JSON file.

## Functions

- `check_or_create_user_data()`: Checks if the `data.sec` file exists and is not empty. If it doesn't exist or is empty, prompts the user to enter their email and password and stores these in the file. If the file exists and is not empty, reads the email and password from the file.

- `log_into_alx()`: Logs into the ALX intranet. Uses the email and password obtained from `check_or_create_user_data()`.

- `sanitize_project_name(project_name)`: Removes characters not allowed in folder names from the project name.

- `get_project_ids_to_alx_json()`: Scrapes the current projects from the ALX intranet and stores the project IDs and names in the `alx.json` file.

- `check_json_file(file_path)`: Checks if the specified JSON file exists and contains valid JSON data.

## Usage

first store your email and pass in a `.data.sec` file in the first two lines as this:
```
examle@gmail.com
pass123
```

Run the script with Python 3:

```bash
python3 request.py
```

When you run the script for the first time, it will prompt you to enter your ALX intranet email and password. These will be stored in the data.sec file. Do not share this file.

The script will log into the ALX intranet, scrape the current projects, and store the project IDs and names in the alx.json file.

This README provides a brief overview of what the script does, describes the functions in the script, and explains how to use the script. You can expand on this README as needed.