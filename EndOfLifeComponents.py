import EoL
from EoL import *
# import serial.tools.list_ports_windows
from ReadBatteryRSOC import read_battery_RSOC
from RelayControlBytes import *
from Serial_Control import serialControl


def EndOfLifeComponents(r, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte, CARTRIDGE_EEPROM_command_byte, NCDComPort,
                 PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, p):
    #print('normal firing', r, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte, CARTRIDGE_EEPROM_command_byte, i)
    #Test_Results = []


    serialControlObj = serialControl(r, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte, CARTRIDGE_EEPROM_command_byte, NCDComPort, PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath)
    serialControlObj.OpenSerialConnection()

    End_of_Life_Components(serialControlObj, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte, CARTRIDGE_EEPROM_command_byte, NCDComPort,
                 PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, p)
    serialControlObj.disconnectSerialConnection()


# Purpose-To perform Normal Firing Scenarios
def End_of_Life_Components(serialControlObj, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte, CARTRIDGE_EEPROM_command_byte, NCDComPort,
                 PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, p):
        # r = getrow('C:\Python\Test_Configurator.xlsx', 0)

##### CASE 1: No Procedures on Power Pack #####

    PowerPackComPort = PowerPackComPort
    SULU_EEPROM_command_byte = SULU_EEPROM_command_byte
    MULU_EEPROM_command_byte = MULU_EEPROM_command_byte
    CARTRIDGE_EEPROM_command_byte = CARTRIDGE_EEPROM_command_byte
    iterPass = 0
    firePass = 0
    TestBatteryLevelMax = serialControlObj.r['Battery RSOC Max Level']
    TestBatteryLevelMin = serialControlObj.r['Battery RSOC Min Level']
    clampingForce = serialControlObj.r['Clamping Force']
    firingForce = serialControlObj.r['Firing Force']
    articulationStateinFiring = serialControlObj.r['Articulation State for clamping & firing']
    numberOfFiringsinProcedure = serialControlObj.r['Num of Firings in Procedure']
    retractionForce = serialControlObj.r['Retraction Force']
    print(TestBatteryLevelMax, TestBatteryLevelMin, clampingForce, firingForce, articulationStateinFiring,
          numberOfFiringsinProcedure)

    # Initial setup
    serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    serialControlObj.wait(0.5)
    serialControlObj.Switch_ONN_Relay(3, 8)

    serialControlObj.wait(0.5)
    serialControlObj.Switch_ONN_Relay(3, 7)

    serialControlObj.wait(60)

    serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    print("Step: Remove Signia Power Handle from Charger")
    serialControlObj.wait(10)

    serialControlObj.Switch_ONN_Relay(1, 5)
    print("Step: Clamshell connected")
    serialControlObj.wait(10)

    while (read_battery_RSOC(25, PowerPackComPort) <= TestBatteryLevelMin):
       # Placing Power Pack on Charger as it is low battery
        serialControlObj.Switch_ONN_Relay(3, 7)
        serialControlObj.wait(.2)
        serialControlObj.Switch_ONN_Relay(3, 8)
        serialControlObj.wait(60)

    # Remove Power Pack from Charger as it is sufficiently charged.
    serialControlObj.Switch_OFF_Relay(3, 7)
    serialControlObj.wait(.2)
    serialControlObj.Switch_OFF_Relay(3, 8)


    # TEST STEP: Attach the EGIA Adapter
    serialControlObj.Switch_ONN_ALL_Relays_In_Each_Bank(1)  # B1 - ALL ON
    #print("Step: Adapter Connected")
    serialControlObj.wait(40)


# STEP 1 : Attach good Adapter to Power Pack with good Clamshell and no procedures remaining

    # Set End OF Life for Power pack (No Procedures remaining)
    EoL.EndOfLifeSet('Handle', 'NoProcedureRem')
    serialControlObj.wait(5)

    # Remove Clamshell
    serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    serialControlObj.wait(5)

    # Put the handle on charger
    serialControlObj.PlacingPowerPackOnCharger()

    # Remove the handle from charger
    serialControlObj.removingPowerPackFromCharger()

    # Reconnect Clamshell
    serialControlObj.connectClamshell()

    # Attach the EGIA Adapter
    serialControlObj.Switch_ONN_ALL_Relays_In_Each_Bank(1)  # B1 - ALL ON

# STEP 2 : Attach MULU to Adapter
    serialControlObj.ConnectingMULUReload()
    serialControlObj.wait(5)

# STEP 3 : Attach Cartridge to Reload
    serialControlObj.ConnectingCartridge(CARTRIDGE_EEPROM_command_byte, BlackBoxComPort)

# STEP 4 : Press a Safety key
    serialControlObj.GreenKeyAck()
    serialControlObj.wait(2)

    # Clear End Of Life condition
    EndOfLifeClear("Handle")

# STEP 5 : Attach good Adapter to Power Pack with good Clamshell and 0 procedure limit
    EoL.EndOfLifeSet('Handle', 'ZeroProcedureLimit')
    serialControlObj.wait(5)

    # Remove Clamshell
    serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    serialControlObj.wait(5)

    # Put the handle on charger
    serialControlObj.PlacingPowerPackOnCharger()

    # Remove the handle from charger
    serialControlObj.removingPowerPackFromCharger()

    # Reconnect Clamshell
    serialControlObj.connectClamshell()

    # Attach the EGIA Adapter
    serialControlObj.Switch_ONN_ALL_Relays_In_Each_Bank(1)  # B1 - ALL ON

# STEP 6 : Attach MULU to Adapter
    serialControlObj.ConnectingMULUReload()
    serialControlObj.wait(5)

# STEP 7 : Attach Cartridge to Reload
    serialControlObj.ConnectingCartridge(CARTRIDGE_EEPROM_command_byte, BlackBoxComPort)

# STEP 8 : Press a Safety key
    serialControlObj.GreenKeyAck()
    serialControlObj.wait(2)

# Clear End Of Life condition
    EndOfLifeClear("Handle")

#### CASE 2: No Firings on Power Pack

# STEP 9 : Attach good Adapter to Power Pack with good Clamshell and no firings remaining
    EoL.EndOfLifeSet('Handle', 'NoFireRem')
    serialControlObj.wait(5)

    # Remove Clamshell
    serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    serialControlObj.wait(5)

    # Put the handle on charger
    serialControlObj.PlacingPowerPackOnCharger()

    # Remove the handle from charger
    serialControlObj.removingPowerPackFromCharger()

    # Reconnect Clamshell
    serialControlObj.connectClamshell()

    # Attach the EGIA Adapter
    serialControlObj.Switch_ONN_ALL_Relays_In_Each_Bank(1)  # B1 - ALL ON

# STEP 10 : Attach MULU to Adapter
    serialControlObj.ConnectingMULUReload()
    serialControlObj.wait(5)

# STEP 11 : Attach Cartridge to Reload
    serialControlObj.ConnectingCartridge(CARTRIDGE_EEPROM_command_byte, BlackBoxComPort)

# STEP 12 : Press a Safety key
    serialControlObj.GreenKeyAck()
    serialControlObj.wait(2)

    # Clear End Of Life condition
    EndOfLifeClear("Handle")

# STEP 13 : Attach good Adapter to Power Pack with good Clamshell and 0 fire limit
    EoL.EndOfLifeSet('Handle', 'ZeroFireLimit')
    serialControlObj.wait(5)

    # Remove Clamshell
    serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    serialControlObj.wait(5)

    # Put the handle on charger
    serialControlObj.PlacingPowerPackOnCharger()

    # Remove the handle from charger
    serialControlObj.removingPowerPackFromCharger()

    # Reconnect Clamshell
    serialControlObj.connectClamshell()

    # Attach the EGIA Adapter
    serialControlObj.Switch_ONN_ALL_Relays_In_Each_Bank(1)  # B1 - ALL ON

# STEP 14 : Attach MULU to Adapter
    serialControlObj.ConnectingMULUReload()
    serialControlObj.wait(5)

# STEP 15 : Attach Cartridge to Reload
    serialControlObj.ConnectingCartridge(CARTRIDGE_EEPROM_command_byte, BlackBoxComPort)

# STEP 16 : Press a Safety key
    serialControlObj.GreenKeyAck()
    serialControlObj.wait(2)

 # Clear End Of Life condition
    EndOfLifeClear("Handle")

# Remove Cartridge from Reload
    serialControlObj.Switch_OFF_Relay(3, 3)  # B3:R3 - OFF
    serialControlObj.Switch_OFF_Relay(3, 4)  # B3:R4 - OFF
    serialControlObj.wait(2)
# Remove MULU from Adapter
    serialControlObj.RemovingMULUReload()
    serialControlObj.wait(5)

#### CASE 3: Used Clamshell ####
# STEP 17: Remove non-EOL Power Pack from Charger and attach Used Clamshell
    # Remove Adapter
    serialControlObj.removeAdapter()
    serialControlObj.wait(5)
    # Step to make the Clamshell as Used
    EndOfLifeSet('Clamshell', '')
    serialControlObj.wait(5)
    # Remove Clamshell
    removeClamshell(self)
    serialControlObj.wait(5)
    # Place the Handle back on Charger
    serialControlObj.PlacingPowerPackOnCharger()
    serialControlObj.wait(10)
    # Remove the handle from charger
    removingPowerPackFromCharger(self)
    serialControlObj.wait(.2)
    # Connect used Clamshell
    serialControlObj.connectClamshell()
    serialControlObj.wait(5)

# STEP 18: Attach good Adapter to Power Pack
    serialControlObj.Switch_ONN_ALL_Relays_In_Each_Bank(1)  # B1 - ALL ON
# STEP 19:










