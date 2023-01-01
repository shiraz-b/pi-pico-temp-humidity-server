# REST Server
# I used the Connecting to the Internet with Raspberry Pi Pico W as the basis
# for this code. (See: https://datasheets.raspberrypi.com/picow/connecting-to-the-internet-with-pico-w.pdf)
# However, I hacked this into a, very much first draft, python class to allow easy setup and usage
# for extracting specified "Verb [Resource..]" from the client.
# There's a fair amount of cleanup that can be done (not least of which is tidying up my very poor exception usage)
# Please go ahead and issue a PR if you want it cleaned up  - I just ask that you not alter the API without
# a conversation with me. thanks!
import network
import socket
import time
import rp2
import ledControl

class RESTService:
    
    # Member variables
    networkConnected     = False
    responseOutstanding  = False
    
    # Member Constants
    CONNECTIONMAXRETRIES = 15
    CONNECTRETRYDELAYMS  = 1000
    FASTFLASHTIME        = 2000
    FASTFLASHBLINK       = 50
    HOSTNAME             = "PiPicoTempHumid01"
    
    LINK_DOWN    = 0
    LINK_JOIN    = 1
    LINK_NOIP    = 2
    LINK_UP      = 3
    LINK_FAIL    = -1
    LINK_NONET   = -2
    LINK_BADAUTH = -3

    HTTP_OK        = "HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n"
    HTTP_NOT_FOUND = "HTTP/1.0 404 NOT FOUND\r\nContent-type: text/html\r\n\r\n<!DOCTYPE HTML PUBLIC \"-//IETF//DTD HTML 2.0//EN\"><html><head><title>404 Not Found</title></head><body><h1>Not Found</h1><p>The requested URL was not found on this server.</p><hr><address>Pi Pico Temperature/Humidity Sensor Port 80</address></body></html>"
    
    # Constructor: Input: SSID and Password
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password
        rp2.country("GB") # change to your country code or remove this line altogether
    
    def __connectionStatus(self, status):
        if status == self.LINK_DOWN:
            return "Link Down"
        elif status == self.LINK_DOWN:
            return "Link Down"
        elif status == self.LINK_JOIN:
            return "Join"
        elif status == self.LINK_NOIP:
            return "No IP"
        elif status == self.LINK_UP:
            return "Link Up"
        elif status == self.LINK_FAIL:
            return "Link Failure"
        elif status == self.LINK_NONET:
            return "No Network"
        elif status == self.LINK_BADAUTH:
            return "Authentication Failure"
        else:
            return "Unknown Status"
    
    # Connect to given ssid.
    #   return: True  - Connection succeeded and active
    #           False - Connection failed
    def connectAndListen(self):
        retries = 0
        
        # setup connection
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        # Hostname setting not supported yet: https://github.com/micropython/micropython/issues/8906
        # When it is, uncomment out this line to set a more meaningful hostname
        # self.wlan.config(hostname=self.HOSTNAME)
        self.wlan.connect(self.ssid, self.password)
        
        # Now wait for the connection to become active
        while retries < self.CONNECTIONMAXRETRIES:
            time.sleep_ms(self.CONNECTRETRYDELAYMS)
            status = self.wlan.status()
            # stop the retry loop if an error or good.
            if status <= self.LINK_FAIL or status >= self.LINK_UP:
                break
            print("Retry: " + str(retries) + ", Status: " + self.__connectionStatus(status))
            retries += 1
            ledControl.toggleLED("LED")
            
        # Handle connection errors
        if status != self.LINK_UP:
            print("Connection failure.  Status: " + self.__connectionStatus(status))
            wlan.disconnect()
            return False

        config = self.wlan.ifconfig()

        print("Connected!  IP Address: " + config[0])
        # Flash the internal LED quickly for 2 seconds to signal good connection
        ledControl.flashLED("LED", self.FASTFLASHTIME, self.FASTFLASHBLINK)

        # Now start listening
        address = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
        self.sock = socket.socket()
        self.sock.bind(address)
        self.sock.listen(1)
        print("Listening on: ", address)
        self.networkConnected = True
        return True
    
    # obtainRequest
    #   Will accept requests until the specified Verb and one of the list of
    #   resources has been asked for. Returns the resource requested.
    #   For all other non-matching REST requests a 404 is given as the response.
    #   e.g.  If you want to look for a GET on either /about or /mesurement you
    #   just need to call this method with: obtainRequest("GET", ["/about", "/measurement"])
    def obtainRequest(self, verb, *resources):
        
        # Precondition: Network is connected and not waiting for a response
        if not self.networkConnected or self.responseOutstanding:
            print("obtainRequest precondition failure")
            return "Fail"

        try:
            while True:
                print("Waiting for new connection")
                self.connection, conaddr = self.sock.accept()
                print("Client connection from: ", conaddr)
                request = self.connection.recv(1024)
                request = str(request)
                #print(request)
                # Requests come out as b'<stuff>' - we want the 'stuff' split out.
                requestList = request.split("'")[1].split()
                # print(*requestList, sep = "\n")
                requestVerb = requestList[0]
                requestResource = requestList[1]
                print("Verb: " + requestVerb + ", Resource: " + requestResource)
                # Range through the resources we are looking for to see if we have one
                for resource in resources:
                    if resource == requestResource:
                        print("Found resource:" + requestResource)
                        self.responseOutstanding = True
                        return resource
                        
                self.connection.send(self.HTTP_NOT_FOUND)
                self.connection.close()
                print("Resource not found.  Returned 404 and connection closed")

        except OSError as err:
            self.connection.close()
            print("Error: Connection Closed")
            return "Fail"

    # Send a response and close the connection
    def sendResponse(self, response):

        # Precondition: Network is connected and waiting for a response
        if not self.networkConnected or not self.responseOutstanding:
            print("sendResponse precondition failure")
            return False
        
        self.connection.send(self.HTTP_OK)
        self.connection.send(response)
        self.connection.close()
        self.responseOutstanding = False
        print("Success: Response sent and connection closed")
        
        return True
        
        
                  
    