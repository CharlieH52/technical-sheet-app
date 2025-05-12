# What is?
Store the main information about a computer *(actually only Windows)* in a **JSON** local storage, with the posibility than upload the same information in a **Google Sheet** like a *Data Base*.

You can share that sheet with your admin partners for the management of the computers in your organization network.

Don't pay for that, be smart... Ofcourse if you don't need anything else.

## Requirements
* Gspread
* Pandas
* Psutil
* Pyinstaller
* Regex

## Configuration

> [!IMPORTANT] 
> You can change in the *main.py* file the constant value of **SHEET_FUNCTION** to True, if you don't need these feature.

### 1. Enable the necessary Google API's and how to configure it
1. Add a new project in [Google Developers Console](https://console.developers.google.com/).
2. Search and enable these API's "Google Drive API" and "Google Sheets API".
3. Go to "APIs and Services", move to "Credentials" section, and create a new "Service Account".
4. Click on edit, go to "Keys" section and add a new JSON key, save it in the root path of the proyect.
> [!CAUTION]
> Don't expose the API key or that will be delete.
5. Copy the email of your *Service Account*, created in the step 3.
6. Create and share a Google Sheet with this email, and give it editor permissions.
