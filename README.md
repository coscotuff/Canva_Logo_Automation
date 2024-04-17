# Canva Logo Downloader

This repository contains a script that automates the process of downloading logos from Canva. By following the instructions below, you can easily download logos from Canva without manual intervention.

## Instructions

1. Install the required dependencies by running the following command:

    ```shell
    pip install -r requirements.txt
    ```

2. Run the `login.py` script to log in to Canva and save your session state. This step is necessary to ensure that you have access to the required resources. You can run the script using the following command:

    ```shell
    python login.py
    ```

    Make sure to provide your Canva login credentials when prompted.

3. After successfully logging in, run the `play.py` script to initiate the logo download process. The script will perform the download in three stages. Run the script in the following order:

    - Stage 1: Run the following command to start stage 1 of the download process:

      ```shell
      python play.py
      (Select option 1)
      ```


    - Stage 2: Once stage 1 is completed, proceed to stage 2 by running the following command:

      ```shell
      python play.py
      (Select option 2)
      ```

    - Stage 3: Finally, run the following command to complete the download process:

      ```shell
      python play.py
      (Select option 3)
      ```

    The script will automatically download the logos from Canva and save them to the specified location.

Please note that this script is intended for personal use only and should be used responsibly and in compliance with Canva's terms of service.

## License

This project is licensed under the [MIT License](LICENSE).