# ascii-art-generator

An ASCII art generator that lets the user search the internet for images, then select any of the 5 top image results to turn into ASCII art. The user can also specify the desired width of generated art (width in characters). Utilizes a Google custom search engine which is accessed through a REST API. Compiled into a .exe file using pyinstaller. 

All downloaded images are stored in a temp folder. This temp folder is purged whenever the program is opened and closed to conserve disk space.

Note: Unfortunately, the free version of Google's custom search engine only allows for 100 API calls per day. Therefore a maximum of 100 searches can be made per day for all users combined. The program will throw an error when the limit is reached.
