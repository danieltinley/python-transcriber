# CHANGELOG - Daniel Tinley [06-04-2023]
# - Refactored code overall to be more Pythonic, save space, and improve readability
# - Implemented regex functions for text replacement to improve speed and reliability
# - Swapped out os for pathlib to improve compatibility on different platforms
# - Updated variable/method names to snake_case to be more Pythonic
# - Consolidated import statements to avoid namespace conflicts
# - Added timestamps to output files

print("\nImporting Python Modules...")
from pathlib import Path
import whisper
import time
import re

print("Defining Python Functions...")
current_date = time.strftime('%d-%m-%Y')
current_time = time.strftime('%Hh%Mm%Ss')
input_dir = Path('input/')
output_dir = Path('output/')
poll_time = 5 # In seconds

# Return all files in a given directory
def scan_directory(my_dir):
    dir_path = Path(my_dir)
    only_files = [
        f.name for f in dir_path.iterdir()
        if f.is_file()
    ]
    
    return(only_files)

# Compare two lists
def compare_list(original_list, new_list):
    list_diff = [x for x in new_list if x not in original_list] # Files deleted during runtime will not be highlighted
    return(list_diff)

# Transcribe and format a new audio file and output to a text file
def process_file(new_file):
    print(f"\nNew file added to the input directory: {new_file}")

    for input_file in new_file:
        print(f"\nWorking on '{input_file}'")
        input_path = input_dir / input_file
        formats = {'mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm'}

        if input_path.suffix[1:] not in formats:
            print(f"\nSkipping file '{input_file}'")
            print("\nFile format not supported")
            print(f"\nSupported file formats are: '{formats}'")

        else:
            print("1. Transcribing...")
            output_file = f'{input_file.split(".")[0]} (at {current_time} on {current_date}).txt'
            result = model.transcribe(str(input_path), language="en", fp16=False)["text"]

            try:
                print("2. Replacing text...")
                def capitalize(match):
                    return match.group(0).upper()
                
                # Replacing text using regex functions
                # New conditions can be inserted if necessary, but pay attention to the order of operations for punctuation
                result = re.sub(r"cobb into|can't be to\.?", "copied to", result, flags=re.IGNORECASE) # Correct common errors
                result = re.sub(r"semicolon|semi colon|semi call in\.?", ":", result, flags=re.IGNORECASE) # Insert semicolons
                result = re.sub(r"new line|you line|new paragraph\.?", "\n", result, flags=re.IGNORECASE) # Insert new lines
                result = re.sub(r"full[\s-]?(stop|step)\.?", ".", result, flags=re.IGNORECASE) # Insert full stops
                result = re.sub(r"four[\s-]?(stop|step)\.?", ".", result, flags=re.IGNORECASE) # Insert full stops
                result = re.sub(r"closed brackets\.?", ")", result, flags=re.IGNORECASE) # Insert closed brackets
                result = re.sub(r"open brackets\.?", "(", result, flags=re.IGNORECASE) # Insert open brackets
                result = re.sub(r"question mark\.?", "?", result, flags=re.IGNORECASE) # Insert question marks
                result = re.sub(r"colon|call in\.?", ":", result, flags=re.IGNORECASE) # Insert colons
                result = re.sub(r"comma|come up\.?", ",", result, flags=re.IGNORECASE) # Insert commas
                result = re.sub(r"dash|hyphen\.?", "-", result, flags=re.IGNORECASE) # Insert hyphens
                result = re.sub(r"\.\s*\)", ")", result) # Remove unnecessary full stops before closed bracket
                result = re.sub(r"\s+\)", ")", result) # Remove unnecessary spacing before closed bracket
                result = re.sub(r"(\()\s+", r"\1", result) # Remove unnecessary spacing after open bracket
                result = re.sub(r"\s+(\.)", r"\1", result) # Remove unnecessary spacing before full stops
                result = re.sub(r"\.{2,}", ".", result) # Remove double full stops
                result = re.sub(r",\s+", " ", result) # Remove unnecessary commas
                result = re.sub(r"(?<=\. )\w", capitalize, result) # Ensure the first word of each sentence is capitalised
                result = result.lstrip() # Remove unnecessary spaces from beginning

                print(f"3. Writing results to '{output_file}' in '{output_dir}'")
                output_path = output_dir / output_file
                with output_path.open(mode = 'w') as f:
                    f.write(result)

                print(f"\nResults have been successfully written to '{output_file}' in '{output_dir}'")
                
            except:
                print("\nERROR: An exception occurred")
                print(f"Skipping file '{input_file}'")
            
    print(f"\nWatching directory '{input_dir}'...")

# Watch input folder and detect new files
def watch_dir(my_dir, poll_time):
    while True:
        if 'watching' not in locals(): # Check if the function has run before
            previous_file_list = scan_directory(input_dir)
        
        time.sleep(poll_time)
        
        new_file_list = scan_directory(input_dir)
        file_diff = compare_list(previous_file_list, new_file_list)
        previous_file_list = new_file_list

        if len(file_diff) == 0: continue
        process_file(file_diff)
        
while True:
    models = ['tiny', 'base', 'small', 'medium', 'large']
    model_size = input(f"\nEnter a Whisper model size ({models})\n> ")
    if model_size not in models:
        model_size = input(f"Enter a Whisper model size ({models})\n> ")
    else:
        break

print(f"\nLoading Whisper '{model_size}' model...")
model = whisper.load_model(model_size)
print(f"Watching directory '{input_dir}'...")
watch_dir(input_dir, poll_time)