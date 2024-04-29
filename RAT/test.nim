import httpclient, strutils

proc getPublicIPAddress(): string =
    var client = newHttpClient()
    let response = client.get("https://api.ipify.org")
    
    return response.body.strip()
    

# Example usage:
let publicIP = getPublicIPAddress()
echo "Public IP Address: ", publicIP
