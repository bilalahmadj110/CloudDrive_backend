______ _______ _       _______    _    _______ _____ ______  _______ 
/ _____|_______) |     (_______)  | |  (_______|_____)  ___ \(_______)
| /      _____  | |      _____      \ \  _         _  | |   | |_____   
| |     |  ___) | |     |  ___)      \ \| |       | | | |   | |  ___)  
| \_____| |_____| |_____| |_____ _____) ) |_____ _| |_| |   | | |_____ 
\______)_______)_______)_______|______/ \______|_____)_|   |_|_______)
                                                                                                                                                        
                                                                                          
- PROJECT CELESTINE v.2.0 - SEP 2021
- PLEASE FOLLOW THESE INSTRUCTIONS CAREFULLY
- DO NOT EDIT OR RENAME ANY FILES/FOLDERS UNLESS SPECIFIED OTHERWISE

________________________________________________________________________________
HOW TO INSTALL
________________________________________________________________________________

0. Download and install python 3.8 or above from the link below:
	https://www.python.org/downloads/

1. Open a command prompt. 
	Press [Win]+[R] to open Run dialog.
	Type in cmd.exe and press [Enter].
	Inside cmd.exe, type in the following command:

		> python --version

	make sure the output shows 3.8 or above

2. Create a virtual environment
	Type in the following command in cmd.exe:

		> python -m venv C:/.../project_celestine_v2.0/env
	
    Python will copy some files to that folder. It will take a minute. 
	After it is complete activate the "env" by typing the following:

		> C:/.../env/Scripts/activate.bat

	You can now see an (env) prefix added to your command prompt.

3. Install needed packages
	A "requirements.txt" can found inside the project folder. Use it to
	install all the packages like so:

		> python -m pip install -r C:/.../requirements.txt


________________________________________________________________________________
HOW TO RUN
________________________________________________________________________________

0. Inside the src folder, there is a config.ini file. You may edit this file
	according to the instructions inside that file. This step is optional.

1. Use the command below in the activated command prompt:
	
	(env) > C:/.../project_celestine_v2.0/server

2. Server is now running silently. Open a web-browser and go to the URL below:

		http://localhost

	If all went well you should be able to see the webpage sent by the server

3. Check the logs folder (see config.ini) to see the messages from the server.

4. Access your server from another computer or network. You may have to 
	configure port-forwarding (port:80) in your router.

		http://XXX.XXX.XXX.XXX
