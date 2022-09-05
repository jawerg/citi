from download.Collector import Collector

if __name__ == '__main__':

    # Use provided link to get all files needed for the task.
    Collector().download_files().prep_base_files()