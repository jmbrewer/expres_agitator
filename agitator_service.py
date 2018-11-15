"""
    EXPRES Fiber Agitator Service module

    Provides a python service that runs the Agitator Server in the
    background of the Windows computer.
"""
# Neccessary for running the agitator as a Windows service
import win32service  
import win32serviceutil  
import win32event  
import servicemanager

from agitator_server import AgitatorServer


class PySvc(win32serviceutil.ServiceFramework):
    # you can NET START/STOP the service by the following name
    _svc_name_ = "AgitSvc"
    # this text shows up as the service name in the Service
    # Control Manager (SCM)
    _svc_display_name_ = "Expres Agitator Service"
    # this text shows up as the description in the SCM
    _svc_description_ = "Accepts messages from EXPRES Manager and returns agitator info"

    def __init__(self, *args):
        win32serviceutil.ServiceFramework.__init__(self, *args)
        # create an event to listen for stop requests on
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    
    # core logic of the service
    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTING,
                              (self._svc_name_,' Starting Agitator'))
        
        # Create a new Exposure Meter Object
        #  turn off logRequests because Service can't write to stdout
        self.server = AgitatorServer(logRequests=False)
        
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,' Agitator Initialized'))
        
        # Start it running...it will listen for stops
        try:
            self.server.serve_forever()
        except Exception as err:
            servicemanager.LogMsg(servicemanager.EVENTLOG_ERROR_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,' Fatal error running server: {}'.format(err)))
    
    # called when we're being shut down
    def SvcStop(self):
        # tell the SCM we're shutting down
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STOPPING,
                              (self._svc_name_,' Shutting Down Exposure Meter'))
        # Stop the server
        self.server.stop()
        
        self.ReportServiceStatus(win32service.SERVICE_STOPPED) 
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STOPPED,
                              (self._svc_name_,' Exposure Meter Stopped'))
                              
        # fire the stop event  
        win32event.SetEvent(self.hWaitStop)
      

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(PySvc)
        
