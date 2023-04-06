# python-transcriber

A small program that runs in the command line listening for any new audio files added to a designated input folder. When one appears, it uses openai-whisper to transcribe it, formats the output, and prints it to a timestamped text file in the designated output folder.