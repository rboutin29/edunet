# EduNet
Interactive Educational web-interface that generates 'trees of knowledge' and 'puzzles of knowledge that aid in studying.

Backend:
- Not all the lecture puzzles have been hardcoded into the pz.html. Each course's transcipts must be hardcoded into the html
page because all the static files are loaded by Django when the page is first loaded.

- New courses cannot be added because the system checks that the courses came from the Yale free courses website. This must be
changed in the hardcode to add additional courses. If this is changed then the download technique used for each course must
also be changed because it is specialized for the download links of the Yale courses. Each download link may be different
and teachers may structure these folders differently. Currently the code follows a unique download structure of the Yale
professors

- CSS can be improved everywhere

- No current ability for users to email Optey team about feedback

- Not all the courses have been processed so user's will have to click the process link which takes a few minutes for each
lecture to process

- Puzzles are currently created by taking keywords, inserting them into an image and saving the image as a static file for
each lecture. If the words are arbitrarily long then they won't show up completely on the image because it is hardcoded. The
image is then loaded into an html page based on the course chosen and then broken into square puzzle pieces using javascript

- The website is currently still in development mode, i.e., debug = true

- This site works when the edunet application is within the site folder. The process of making a resuable application has
not been finished for the edunet app (tree and puzzle of knowledge)

- Security key is hardcoded and present in the github repository

- Make sure to ssh download apt-get install -y libglib2.0-0 libsm6 libxrender1 libxext6 for cv2 imports when redeploying