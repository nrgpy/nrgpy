# ![NRGPy](https://www.gravatar.com/avatar/6282094b092c756acc9f7552b164edfe?s=24) SymphoniePRO Deskop Software | Convert files on Linux

**Summary** <br>
The following is an example of how to convert RLD raw wind data files from SymphoniePRO Data Loggers to TXT format by using Wine on Ubuntu 20.04 Linux. Steps for other distros should be  similar. 

Note that this process requires the presence of an x-environment (GUI). The SymPRO Desktop installation will not complete without a graphical environment.

Also note that only command line functions are available. The program will not load the graphical user interface (as of 4/1/2021).
<br><br>
**Steps** <br>

1. Install Wine <br>
        `sudo apt install wine winetricks` <br><br>
1. Download SymphoniePRO installation media <br>
         `wget https://www.nrgsystems.com/assets/software-downloads/8968-SymPRODesktopApp-3.10.1.12.exe` <br><br>
1. Configure a 64-bit wine prefix. Note the last step will require you to install several versions of .NET framework (.NET 4, 4.5, 4.6, 4.6.1, 4.6.2, 4.7.2). There is no need to restart your computer between each installation. <br><br>This may take up to 20 minutes.<br>
          `export WINEPREFIX="/home/$USER/prefix64"` <br>
					`export WINEARCH=win64` <br>
					`winetricks win10` <br>
					`winetricks vcrun2013` <br>
					`winetricks dotnet472` <br>
1. Install the software <br>
           `wine 8968-SymPRODesktopApp-3.10.1.12.exe` <br>
					 `# accept defaults EXCEPT!! do not allow SymphoniePRO Desktop to make a firewall rule!` <br>
					 `# press enter to clear command line` <br>
1.  Try it out! <br>
	2.  Copy some files into your /home/$USER/Documents/Renewable NRG Systems/Raw directory <br>
	3.  Run a convert! <br>
	           `cd prefix64/drive_c/Program\ Files\ \(x86\)/Renewable\ NRG\ Systems/SymPRO\ Desktop/`<br>
						 `wine SymPRODesktop.exe /cmd convert /file "C:\\users\\[your-username]\\My Documents\\Renewable NRG Systems\\Raw\\353008\\353008_2021-01-*.rld"`<br><br>
						 
Files will be saved in your `/home/[your-username]/Documents/Renewable NRG Systems/Exports` folder!
