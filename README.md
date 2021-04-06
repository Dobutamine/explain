How to install the developer edition of Explain

As Explain is completely open-source it only uses external open-source software-packages to run.

Install VS Code     : https://code.visualstudio.com/download <br>
Install Git	        : https://git-scm.com/downloads <br>
Install NodeJs		  : https://nodejs.org/en/download/ <br>
Sign up for GitHub	: https://github.com <br>

Go to the command prompt (Windows) or Terminal (Linux/OSX).<br>
Register your git username and email to Git with commands: <br>
      <i>git config --global user.name “your username”</i> <br>
      <i>git config –global user.email “your email”<i> <br>
<br>
Install the Yarn package manager with command:<br>
      <i>npm install -g yarn</i> <br>
<br>      
Install the Quasar framework with command:
      <i>npm install -g @quasar/cli<i>

-	Go to the command prompt (Windows) or Terminal(Linux/OSX) if not already open.
  * Make a directory where you want to put the explain application. 
    mkdir projects
  * Change directory to the newly created folder with command.
    cd projects
  * Clone the GitHub Explain project with command
    git clone https://github.com/Dobutamine/explain.git
  * Navigate into the explain directory with command
    cd explain
  * Update the dependencies with command
    yarn
        
WINDOWS USERS ONLY!
To allow the scripts to run, open the Powershell with administrator rights
  * You can find Powershell in your start menu. Right click Powershell en select Run as administrator. In the Powershell window type:
    Set-ExecutionPolicy unrestricted


First time run of Explain
-	Open VS Code from the desktop or Start menu
  * Goto File -> Open
    Navigate to the explain directory and select Open.
-	If asked by VS Code in right lower corner -> Install recommended extensions -> yes!
-	Create a new developer branch in VS Code to work in 
  * First click on the the master brach in the lower left corner of VS Code
- Create a new branch for yourself to work in (top middle in VS Code). You can choose any name.

To run the developer edition of Explain
-	In VS Code with the Explain project loaded (see step above)
  * Go to Terminal in the menu bar and choose New Terminal
  * In the terminal window below enter the command
    quasar dev
  * After compiling the explain developer edition is ready for use. 
  * Go to any browser (prefereably Chrome) and type in the addressbar
    localhost:8080


Have fun!
