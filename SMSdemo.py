
from scservo_sdk import SCSController


demo_smc=SCSController("/dev/ttyUSB0",115200)
demo_smc.init();
demo_smc.WritePosition(1,3000)
demo_smc.Close()

    