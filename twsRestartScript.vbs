OPTION EXPLICIT
DIM strComputer,strProcess,res

strComputer = "." ' local computer
strProcess = "tws.exe"

call findAndKillProcess(strComputer,strProcess)

call startLoginTws()

' Function to check if a process is running and kill it
FUNCTION findAndKillProcess(BYVAL strComputer,BYVAL strProcessName)

	DIM objWMIService, strWMIQuery,colProcessList,element  
	

	strWMIQuery = "Select * from Win32_Process where name like '" & strProcessName & "'"
	
	SET objWMIService = GETOBJECT("winmgmts:"& "{impersonationLevel=impersonate}!\\"& strComputer & "\root\cimv2") 

	IF objWMIService.ExecQuery(strWMIQuery).Count > 0 THEN
		Set colProcessList = objWMIService.ExecQuery(strWMIQuery)
		findAndKillProcess= TRUE
		For Each element In colProcessList 
    		element.Terminate()
		NEXT  
	ELSE
		findAndKillProcess= FALSE
	END IF

END FUNCTION


FUNCTION startLoginTws()
	DIM WshShell 

' Create WScript Shell Object to access filesystem.
	Set WshShell = WScript.CreateObject("WScript.Shell")

' Start / Run NOTEPAD.EXE
	WshShell.Run "C:\Jts\tws.exe"

' Select, or bring Focus to a window named `NOTEPAD`
	WshShell.AppActivate "Login"

' Wait for 5 seconds
	WScript.Sleep 30000

	WshShell.SendKeys "colak1982"
	WScript.Sleep 1000
	WshShell.SendKeys "{TAB}"
	WScript.Sleep 1000
	WshShell.SendKeys "klk5489103"
	WScript.Sleep 1000
	WshShell.SendKeys "{ENTER}"
END FUNCTION