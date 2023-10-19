import threading
import cv2
import pickle
import struct
import numpy as np
import socket
from PIL import ImageGrab


class StreamingClient:
    """
    Abstract class for the generic streaming client.
    Attributes
    ----------
    Private:
        __host : str
            host address to connect to
        __port : int
            port to connect to
        __running : bool
            inicates if the client is already streaming or not
        __encoding_parameters : list
            a list of encoding parameters for OpenCV
        __client_socket : socket
            the main client socket
    Methods
    -------
    Private:
        __client_streaming : main method for streaming the client data
    Protected:
        _configure : sets basic configurations (overridden by child classes)
        _get_frame : returns the frame to be sent to the server (overridden by child classes)
        _cleanup : cleans up all the resources and closes everything
    Public:
        start_stream : starts the client stream in a new thread
    """

    def __init__(self, host, port, clientSocket):
        """
        Creates a new instance of StreamingClient.
        Parameters
        ----------
        host : str
            host address to connect to
        port : int
            port to connect to
        """
        self.__host = host
        self.__port = port
        self._configure()
        self.__running = False

        #client socket to recv request
        self.__client = clientSocket 

        # client socket to recv video
        self.__client_socket = None


    def startListening(self):
        request = ""
        while True:
            request = self.__client.recv(1024).decode("utf-8")
            if not request:
                break
            if request == "stream":
                self.start_stream()
            elif request == "stop":
                self.stop_stream()
            else:
                return
                

    def _configure(self):
        """
        Basic configuration function.
        """
        self.__encoding_parameters = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

    def _get_frame(self):
        """
        Basic function for getting the next frame.
        Returns
        -------
        frame : the next frame to be processed (default = None)
        """
        return None

    def _cleanup(self):
        """
        Cleans up resources and closes everything.
        """
        cv2.destroyAllWindows()

    def __client_streaming(self):
        """
        Main method for streaming the client data.
        """
        self.__client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__client_socket.connect((self.__host, self.__port))

        while self.__running:
            frame = self._get_frame()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result, frame = cv2.imencode('.jpg', frame, self.__encoding_parameters)
            data = pickle.dumps(frame, 0)
            size = len(data)

            try:
                self.__client_socket.send(struct.pack('>L', size) + data)
            except:
                self.__running = False

        self._cleanup()

    def start_stream(self):
        """
        Starts client stream if it is not already running.
        """

        if self.__running:
            print("Client is already streaming!")
        else:
            self.__running = True
            client_thread = threading.Thread(target=self.__client_streaming)
            client_thread.start()

    def stop_stream(self):
        """
        Stops client stream if running
        """
        try:
            self.__client_socket.close()
        except:
            pass
        if self.__running:
            self.__running = False
        else:
            print("Client not streaming!")



class ScreenShareClient(StreamingClient):
    """
    Class for the screen share streaming client.
    Attributes
    ----------
    Private:
        __host : str
            host address to connect to
        __port : int
            port to connect to
        __running : bool
            inicates if the client is already streaming or not
        __encoding_parameters : list
            a list of encoding parameters for OpenCV
        __client_socket : socket
            the main client socket
        __x_res : int
            the x resolution
        __y_res : int
            the y resolution
    Methods
    -------
    Protected:
        _get_frame : returns the screenshot frame to be sent to the server
    Public:
        start_stream : starts the screen sharing stream in a new thread
    """

    def __init__(self, host, port, clientSocket, x_res=1024, y_res=576):
        """
        Creates a new instance of ScreenShareClient.
        Parameters
        ----------
        host : str
            host address to connect to
        port : int
            port to connect to
        x_res : int
            the x resolution
        y_res : int
            the y resolution
        """
        self.__x_res = x_res
        self.__y_res = y_res
        super(ScreenShareClient, self).__init__(host, port, clientSocket)

    def _get_frame(self):
        """
        Gets the next screenshot.
        Returns
        -------
        frame : the next screenshot frame to be processed
        """
        screen = ImageGrab.grab() #pyautogui.screenshot()
        frame = np.array(screen)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (self.__x_res, self.__y_res), interpolation=cv2.INTER_AREA)

        return frame


#a = ScreenShareClient("localhost", 5000)
#a.start_stream()