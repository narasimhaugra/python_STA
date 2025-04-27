# Author - Varun Pandey
# Date - Jan 06, 2022
# @ Purpose - To create the output json file

import copy
import json
# from collections import OrderedDict
from pprint import pprint
import datetime
# import math

# Todo - make sure to capture and handle the cases for AGRs like 'Test Type' etc
class SWconfigDataDetermination:

    def __init__(self, TestType, Changeset, Integration_Build):
        self.TestType = TestType
        self.Changeset = Changeset
        self.Integration_Build = Integration_Build

    def fetch_test_type(self) -> str:
        return self.TestType   # todo - change this determination - done - determined as the ARGUMENT

    # read from RTC:
    def fetch_test_date(self, logfileParameters) -> str:
        return logfileParameters.get('RTC', "Test_Date_NOT_Found")

    # converts the hex data in sec to UTC, read from 'PP Timestamp'
    def fetch_build_date(self, logfileParameters):
        buildDateTimeparam = logfileParameters.get('buildDateTimeparam')
        if not buildDateTimeparam:
            return 'BUILD_Date_NOT_Found'
        else:
            # timeparam = 0x60D34BF2
            hexTimeinSec_utc = f'{buildDateTimeparam}'
            epochtime = int(hexTimeinSec_utc, 16) - 19800
            dt = datetime.datetime.fromtimestamp(epochtime)
            # print(dt)
            return dt # 'return build date'   # todo - change this determination - done

    def fetch_changeset(self) -> str:
        return self.Changeset   # todo - change this determination - done - identified as ARG

    def fetch_Integration_Build(self) -> str:
        return self.Integration_Build   # todo - change this determination - done - identified as ARG

    # read from Handle_serial_number
    def fetch_Handle_Serial_Num(self, logfileParameters) -> str:
        return logfileParameters.get('Handle_serial_number', "Handle_serial_number_NOT_Found")

    # read from Adapt BL Rev
    def fetch_Adapter_Bootloader_Version(self, logfileParameters) -> str:
        return logfileParameters.get('Adapt_BL_Rev', "Adapter_Bootloader_Version_NOT_Found")

    # read from EEA Rev
    def fetch_Adapter_EEA_Version(self, logfileParameters) -> str:
        return logfileParameters.get('EEA_Rev', "Adapter_EEA_Rev_NOT_Found")

    # read from EGIA Rev
    def fetch_Adapter_EGIA_Version(self, logfileParameters) -> str:
        return logfileParameters.get('EGIA_Rev', "Adapter_EGIA_Rev_NOT_Found")

    # read from PP BL Rev
    def fetch_Power_Pack_Bootloader_Version(self, logfileParameters) -> str:
        return logfileParameters.get('PP_BL_Rev', "Power_Pack_Bootloder_Version_NOT_Found")

    # read from PP Rev
    def fetch_Power_Pack_Version(self, logfileParameters):
        return logfileParameters.get('PP_Rev', "Power_Pack_Version_NOT_Found")

    def fetch_Blob_Version(self, logfileParameters) -> str:
        return logfileParameters.get('System Version', 'Blob_Version_NOT_Found') # same as System Version

    # read the Input log captured
    def fetchParametersfromLogFile(self, logfilePath):
        logfileParameters = {}  # returned post the file data is read
        '''
        sample data:
        
        17:00:14 RTC: 1641900614 = 2022/01/11 11:30:14 (UTC)        # RTC
        17:00:15   10410:    PP Timestamp   = 0x60D34BF2            # buildDateTimeparam
        17:00:15   10411:      PP Rev       = 29.4.2_DEBUG          # PP_Rev
        17:00:15   10411:      PP BL Rev    = 7.3.1                 # PP_BL_Rev
        17:00:15   10411:      Adapt BL Rev = 11.1.1                # Adapt_BL_Rev
        17:00:15   10411:      EGIA Rev     = 14.2.1                # EGIA_Rev
        17:00:15   10411:      EEA Rev      =                       # EEA_Rev
        17:00:15   10413: Handle serial number: C19AAK0451          # Handle_serial_number
        
        '''
        with open(logfilePath, 'r') as logfile:
            for singleLine in logfile:
                if 'RTC:' in singleLine and '(UTC)' in singleLine:
                    logfileParameters['RTC'] = singleLine.split('=')[1].strip()
                elif 'PP Timestamp' in singleLine:
                    logfileParameters['buildDateTimeparam'] = singleLine.split('=')[1].strip()
                elif 'PP Rev' in singleLine:
                    logfileParameters['PP_Rev'] = singleLine.split('=')[1].strip()
                elif 'PP BL Rev' in singleLine:
                    logfileParameters['PP_BL_Rev'] = singleLine.split('=')[1].strip()
                elif 'Adapt BL Rev' in singleLine:
                    logfileParameters['Adapt_BL_Rev'] = singleLine.split('=')[1].strip()
                elif 'EGIA Rev' in singleLine:
                    logfileParameters['EGIA_Rev'] = singleLine.split('=')[1].strip()
                elif 'EEA Rev' in singleLine:
                    data = singleLine.split('=')[1].strip()
                    logfileParameters['EEA_Rev'] = "N/A" if data == "" else data
                elif 'Handle serial number' in singleLine:
                    logfileParameters['Handle_serial_number'] = singleLine.split(':')[-1].strip()
                # added newly for Data Path - which will be used the read the event log file from the MCP logs
                #   but this will not ba added into the Test Config parameters
                elif 'Data path:' in singleLine:
                    logfileParameters['Data_path'] = singleLine.split(':')[1].strip()
                # System Version - Blob Version
                elif 'System Version' in singleLine:
                    logfileParameters['System Version'] = singleLine.split('=')[-1].strip()
        return logfileParameters

# generate Test Config data dict, which will be merged finally with the output dictionary
def generateSWConfDict(logfilePath, TestType, Changeset, Integration_Build):
    swConfigDict = {}       # containing all the elements related with the software configuration items

    '''
    # below json file format has to be generated for the output.json for "Test Config" key
        "Test Config": {
        "Test Type": "EGIA_Sanity_Checks",
        "Test Date": "2021/12/03 09:54:16 (UTC)",
        "Build Date": "2021/12/01 15:45:36 (UTC)",
        "Changeset": 492,
        "Integration Build": true,
        "Blob Version": "CS492",
        "Power Pack Version": "Version",
        "Power Pack Bootloader Version": "Version",
        "Adapter EGIA Version": "Version",
        "Adapter EEA Version": "N/A",
        "Adapter Bootloader Version": "Version",
        "Handle Serial Num": "C19A200133"
    },
    '''

    SWconfigDataDeterminationObj = SWconfigDataDetermination(TestType, Changeset, Integration_Build)

    # read the Input log captured - Todo - make sure that the text log file is captured and stored locally
    logfileParameters = SWconfigDataDeterminationObj.fetchParametersfromLogFile(logfilePath)

    # ARGUMENTS values are being set via the class constructor objects, but to keep the class structure uniform
    #   we have creating class functions too.
    swConfigDict["Test Type"] = SWconfigDataDeterminationObj.fetch_test_type()                          # Argument
    swConfigDict["Test Date"] = SWconfigDataDeterminationObj.fetch_test_date(logfileParameters)         # RTC
    swConfigDict["Build Date"] = SWconfigDataDeterminationObj.fetch_build_date(logfileParameters)       # PP Timestamp
    swConfigDict["Changeset"] = SWconfigDataDeterminationObj.fetch_changeset()                          # Argument
    swConfigDict["Integration Build"] = SWconfigDataDeterminationObj.fetch_Integration_Build()          # Argument
    swConfigDict["Blob Version"] = SWconfigDataDeterminationObj.fetch_Blob_Version(logfileParameters)   # System Version
    swConfigDict["Power Pack Version"] = SWconfigDataDeterminationObj.\
        fetch_Power_Pack_Version(logfileParameters)                                                     # PP Rev
    swConfigDict["Power Pack Bootloader Version"] = SWconfigDataDeterminationObj.\
        fetch_Power_Pack_Bootloader_Version(logfileParameters)                                          # PP BL Rev
    swConfigDict["Adapter EGIA Version"] = SWconfigDataDeterminationObj.\
        fetch_Adapter_EGIA_Version(logfileParameters)                                                   # EGIA Rev
    swConfigDict["Adapter EEA Version"] = SWconfigDataDeterminationObj.\
        fetch_Adapter_EEA_Version(logfileParameters)                                                    # EEA Rev
    swConfigDict["Adapter Bootloader Version"] = SWconfigDataDeterminationObj.\
        fetch_Adapter_Bootloader_Version(logfileParameters)                                             # Adapt BL Rev
    swConfigDict["Handle Serial Num"] = SWconfigDataDeterminationObj.\
        fetch_Handle_Serial_Num(logfileParameters)                                                      # Handle serial
                                                                                                        # number

    # create the outer dict
    swConfigOuterDict = {}
    swConfigOuterDict["Test Config"] = swConfigDict

    return swConfigOuterDict  # , logfileParameters.get('Data_path')

# takes json file path as an input and generate the parsed string format data
def createOutputJsonFile(jsonpath, logfilePath, TestType, merged_PassFailDict, Changeset,
                         Integration_Build): #, WithFiring):
    jsonData = {}

    swConfigOuterDict = generateSWConfDict(logfilePath, TestType, Changeset, Integration_Build)
    with open(jsonpath, 'r') as jsonFile:

        # jsonData = json.load(jsonFile, object_pairs_hook=OrderedDict)
        jsonData = json.load(jsonFile)

        # updated the data_path in Test Config
        # jsonData["Test Config"]['Data_path'] = logfilePath

        # removing the "COM Setting", as it is not required in the output_code.json - this has been taken care
        #   in the for loop part
        # jsonData.pop("COM Setting", None)

        # we need to remove the Other Test Scenario's Data too, which are present in Input.json file while recording the
        #   same in output_code.json
        # Todo - this should have the value from arg coming into swConfigOuterDict
        currentTestScenario = swConfigOuterDict.get("Test Config").get('Test Type')
        keysToDeleteList = []
        for key in jsonData.keys():
            # just maintain the structure
            if key == currentTestScenario or key == "Test Config":
                continue
            else:
                # store the keys which have to be deleted specifically - "COM Setting" and key != currentTestScenario
                # Note - keys can't be deleted on run time as it will not be allowed to change the dictionary data
                #        while we are performing the looping operation in the dictionary
                keysToDeleteList.append(key)
        else:
            # delete the unwanted keys from final Data
            [jsonData.pop(keyToDelete, None) for keyToDelete in keysToDeleteList]

        # in the same jsonData, we will have to add up the "Test Results" and "Pass %" keys
        # created a list data so as to avoid run time error of dict update during run time
        jsonTestScenarios_List = copy.deepcopy(jsonData[currentTestScenario]["Test Scenarios"])
        for counter, singleInnerDict in enumerate(jsonTestScenarios_List):
            #print(singleInnerDict)
            # now update based on the scenario number - Todo - since this is a repetitive loop, for each scenario number
            #                                           we will update the same result every time - Can be refactored
            for scenarioKey, scenarioValue in singleInnerDict.items():
                if scenarioKey == 'Scenario Num':
                    # check if the singleInnerDict is having "Retraction Force" i.e. it has 'Firing = ' in the result
                    #   log
                    # if WithFiring and singleInnerDict.get("Retraction Force"):
                    # update the test results key
                    PassbyTotal = merged_PassFailDict.get(str(scenarioValue), None)
                    # print("PassbyTotal", PassbyTotal)
                    if PassbyTotal:
                        zero_index = float(int(PassbyTotal.split('/')[0]) * 100)
                        one_index = int(PassbyTotal.split('/')[1])
                        # print("index 0 ", zero_index)
                        # print("index 1 ", one_index)
                        if zero_index == 0.0 and one_index == 0:
                            zero_index = 1
                            one_index  = 1
                        # passPercentage = float(int(PassbyTotal.split('/')[0]) * 100 / int(PassbyTotal.split('/')[1]))
                        passPercentage = zero_index / one_index
                        jsonData[currentTestScenario]["Test Scenarios"][counter]["Test Results"] = PassbyTotal
                        jsonData[currentTestScenario]["Test Scenarios"][counter]["Pass %"] = passPercentage
                    '''elif not WithFiring and not singleInnerDict.get("Retraction Force"):
                        print(scenarioKey, scenarioValue)
                        # update the test results key
                        PassbyTotal = merged_PassFailDict.get(str(scenarioValue), None)
                        if PassbyTotal:
                            passPercentage = float(int(PassbyTotal.split('/')[0]) * 100 / int(PassbyTotal.split('/')[1]))
                            jsonData[currentTestScenario]["Test Scenarios"][counter]["Test Results"] = PassbyTotal
                            jsonData[currentTestScenario]["Test Scenarios"][counter]["Pass %"] = passPercentage'''


        # pprint(jsonData.get('COM Setting'), indent=2)

    # In case, if there is any existing key "Test Config" in Input.json --> which is not possible though but
    #   to make this code work for testing scenario, the following steps are done:
    #   Remove any pre-existing key "Test Config" and add the data from
    #       swConfigOuterDict["Test Config"] - re-initialize the data read from Input.json with swConfigOuterDict
    jsonDataWithSWConfig = {}
    jsonDataWithSWConfig["Test Config"] = swConfigOuterDict["Test Config"]
    jsonDataWithSWConfig.update(jsonData)

    with open("test_automation_results.json", 'w') as outputJsonFile:
        # Note - default encoding as made as str to deserialize the datetime data coming in "Build Date"
        json.dump(jsonDataWithSWConfig, outputJsonFile, indent=4, default=str)

# LogFileName Name and LogStringsList are mandatory arguments
# fileOpenMode is a default argument which is 'w' by default, can be overridden
#   by passing 'a' for opening the log file in append mode

# *IMP* functionality to save the logstring list into a text file("StartUpLog.txt"), which will be provided as an
#   input to calculatePassFail function as logfilePath argument
def convertListtoLogFile(LogStringsList, LogFileName, fileOpenMode='w'):
    with open(LogFileName, fileOpenMode) as logFile:
        [logFile.write(singleData + "\n") for singleData in LogStringsList]


# to calculate the PASS/FAIL percentage from the generated log
def calculatePassFail(ResultFileName, jsonpath, logfilePath, TestType, Changeset, Integration_Build): # , WithFiring=True):

    with open(ResultFileName, 'r') as logFile:
        scenarioStart = False
        numberofIteration = 0
        passCounter = 0
        scenarioNumber = repetitionNumber = 0
        scenarioName = ''

        # scenarioNum_Pass, and numberofIteration_Pass is added to make sure that the dict is appended for same
        #   scenarios and different iterations
        scenarioNum_Pass = {}
        numberofIteration_per_scenario = {}

        PassFailDict = {}  # Key as Scenario_Name + Scenario_Number + Repeatition_Number and
                            # Value as (Pass#/Total num of iteration) i.e. Pass Percentage

        # failForWithoutFire = False

        # scenario record - to store if the scenario is WithFiring or without Firing
        # scenarioNumberRecord = {}
        for singleLine in logFile:
            if '#' in singleLine and '@' in singleLine:
                scenarioStart = True

                # if we are not in the first iteration
                if numberofIteration:

                    scenarioNum_Pass[scenarioNumber] = (scenarioNum_Pass.get(scenarioNumber, 0) + passCounter) \
                        if scenarioNum_Pass.get(scenarioNumber) else passCounter

                    numberofIteration_per_scenario[scenarioNumber] = (numberofIteration_per_scenario.get(scenarioNumber,
                                                                                                         0) +
                                                                      numberofIteration) \
                        if numberofIteration_per_scenario.get(scenarioNumber) else numberofIteration

                    PassFailDict[str(scenarioName)+"_"+str(scenarioNumber)+"_" +
                                 str(repetitionNumber)] = str(passCounter)+"/" + str(numberofIteration)
                    # reset the counters
                    passCounter = 0

                # 2#1@Normal Firing
                scenarioNumber = singleLine.split('#')[0]
                repetitionNumber = singleLine.split('#')[1].split('@')[0]
                scenarioName = singleLine.split('@')[1].replace(' ', '_').strip()

                # reset the counters
                numberofIteration = 0
                failForWithoutFire = False
                continue

            # gets the counter of number of iterations#, in case when we are in the WITH Firing state
            if scenarioStart and '=' in singleLine and ":" in singleLine:# and WithFiring:

                # Firing =1:PASS
                numberofIteration = numberofIteration + 1

                # increment the pass counter
                if singleLine.split(':')[1].strip().lower() == "pass":
                    passCounter = passCounter + 1
            '''# for non - withFiring - any FAIL in the subsequent steps would be treated as a FAIL for whole step else
            #   it would be a PASS
            elif not WithFiring and not failForWithoutFire and scenarioStart and ":" in singleLine:
                # Adapter Connected:PASS
                numberofIteration = 1       # for cases when there is no Firing statement in the log of a test
                                            # the number of iteration will be 1, once it enters the block
                passCounter = 1             # pass counter will always be 1

                # found a fail, make the entire scenario as FAIL
                if singleLine.split(':')[0].lower() != "eventlog" and singleLine.split(':')[1].strip().lower() != "pass":
                    failForWithoutFire = True
                    passCounter = 0           # when it is failure, we should report it say that it is not passed i.e 0'''
        else:
            # for final data
            scenarioNum_Pass[scenarioNumber] = (scenarioNum_Pass.get(scenarioNumber, 0) + passCounter) \
                if scenarioNum_Pass.get(scenarioNumber) else passCounter

            numberofIteration_per_scenario[scenarioNumber] = (numberofIteration_per_scenario.get(scenarioNumber, 0) +
                                                              numberofIteration) \
                if numberofIteration_per_scenario.get(scenarioNumber) else numberofIteration

            PassFailDict[str(scenarioName) + "_" + str(scenarioNumber) + "_" +
                         str(repetitionNumber)] = str(passCounter) + "/" + str(numberofIteration)

    #pprint(PassFailDict, indent=4)
    #pprint(scenarioNum_Pass, indent=4)  # total pass per scenario - combined per iteration
    #pprint(numberofIteration_per_scenario, indent=4)    # total number of iterations per scenario - combined

    # now we can merge both the dict to get the final merged count
    merged_PassFailDict = {}
    for scenarioCounter, passNumber in scenarioNum_Pass.items():
        merged_PassFailDict[scenarioCounter] = str(passNumber) + "/" + \
                                               str(numberofIteration_per_scenario.get(scenarioCounter, 0))

    pprint(merged_PassFailDict, indent=4)
    # createOutputJsonFile is called for each time we want to merge the PASS Fail Result and the % data with
    #   output.json file
    createOutputJsonFile(jsonpath=jsonpath, logfilePath=logfilePath, TestType=TestType,
                         merged_PassFailDict=merged_PassFailDict, Changeset=Changeset,
                         Integration_Build=Integration_Build)#, WithFiring=WithFiring)


# specific function created to modify the below Test Config keys - which are coming as NOT defined
def update_SW_Config_Dict(ProjectName, TestDate, BuildDate, BlobVersion, PowerPackVersion, PowerPackBootloaderVersion,
                          AdapterEGIAVersion, AdapterEEAVersion, AdapterBootloaderVersion):
    '''with open("test_automation_results.json", 'w') as outputJsonFile:
        # Note - default encoding as made as str to deserialize the datetime data coming in "Build Date"
        json.dump(jsonDataWithSWConfig, outputJsonFile, indent=4, default=str)
    "Test Config": {
                    "Test Type": "EGIA_Sanity_Checks",
                    "Test Date": "Test_Date_NOT_Found",
                    "Build Date": "BUILD_Date_NOT_Found",
                    "Changeset": "791",
                    "Integration Build": "True",
                    "Blob Version": "29.5.1.0.ENG",
                    "Power Pack Version": "Power_Pack_Version_NOT_Found",
                    "Power Pack Bootloader Version": "Power_Pack_Bootloder_Version_NOT_Found",
                    "Adapter EGIA Version": "Adapter_EGIA_Rev_NOT_Found",
                    "Adapter EEA Version": "Adapter_EEA_Rev_NOT_Found",
                    "Adapter Bootloader Version": "Adapter_Bootloader_Version_NOT_Found",
                    "Handle Serial Num": "C19AAK0451"
                    }'''

    with open("test_automation_results.json", 'r') as jsonFile:

        # jsonData = json.load(jsonFile, object_pairs_hook=OrderedDict)
        jsonData = json.load(jsonFile)

        # we need to remove the Other Test Scenario's Data too, which are present in Input.json file while recording the
        #   same in output_code.json
        # Todo - this should have the value from arg coming into swConfigOuterDict
        #currentTestDate = jsonData.get("Test Config").get("Test Date")   # 2022-06-23 03-50-20 (UTC) Test Date format to be modified to match with Build Date format Done by manoj Vadali
        #2022-06-23 03-50-20 (UTC) ---->   2022-06-23 03:50:20 (UTC)
        #T = '2022-06-23 03-50-20 (UTC)'
        #T=T.split()

        jsonData["Test Config"]["Project"] = ProjectName # Project Name changed to Project by Manoj Vadali as per Andrew's inputs
        jsonData["Test Config"]["Test Date"] = TestDate
        jsonData["Test Config"]["Build Date"] = BuildDate
        jsonData["Test Config"]["Blob Version"] = BlobVersion
        jsonData["Test Config"]["Power Pack Version"] = PowerPackVersion
        jsonData["Test Config"]["Power Pack Bootloader Version"] = PowerPackBootloaderVersion
        jsonData["Test Config"]["Adapter EGIA Version"] = AdapterEGIAVersion
        jsonData["Test Config"]["Adapter EEA Version"] = AdapterEEAVersion
        jsonData["Test Config"]["Adapter Bootloader Version"] = AdapterBootloaderVersion

    # updating the same data again to test_automation_results.json
    with open("test_automation_results.json", 'w') as outputJsonFile:
        # Note - default encoding as made as str to deserialize the datetime data coming in "Build Date"
        json.dump(jsonData, outputJsonFile, indent=4, default=str)


if __name__ == "__main__":
    TestType = 'EGIA_Regression_Test'       # todo - test type will come as a CLI argument
    Changeset = 492                         # todo - test type will come as a CLI argument
    Integration_Build = True                # todo - test type will come as a CLI argument

    LogStringsList = ['PowerPack USB Connection Established', 'SYSTEM_AREA_START:',
                      'Ver03: savedCRC = 3FF5  calculatedCRC = 3FF5  version = 3',
                      'SavedSystemData is valid', 'Reset type:', 'Software',
                      'FPGA Feature Row Ok! Original Data =  0x200', '!!main FPGA Refresh Start!!',
                      '!!main FPGA Refresh Done!!', '1W RTC: Not Detected. Code = 1',
                      'VerifySecret Address= 17 E4 EA B6 00 00 00 42', 'UpdateFPGA: FPGA is current',
                      'Flash usage = 713K of 932K = 76.5%', 'Handle init complete',
                      'Memory = 02 02 04 32 37 30 35 32 30 31',
                      '39 2D 30 32 31 33 0D 0A 00 00', '00 00 00 00 00 00 00 00 00 00',
                      '00 00 00 00 00 00 00 00 00 00', '00 00 00 00 00 00 00 00 00 00',
                      '00 00 00 00 00 00 00 00 00 00', '00 2C B3 55',
                      '1Wire Device Battery attached on 1WireBus Handle',
                      'Address= 17 E4 EA B6 00 00 00 42', '1Wire Device Battery authenticated and identified',
                      'OneWire_TestDeviceWritable: Battery Starting test',
                      'VerifySecret Address= 17 03 31 8D 00 00 00 1C',
                      'Memory = 02 01 04 43 31 39 41 41 4B 30', '34 35 31 0D 0A 00 00 EB 7F 00',
                      'A0 86 8F 00 10 27 00 00 00 00', '00 00 00 00 00 A1 00 00 00 00',
                      '00 00 00 00 00 00 00 00 00 00', '00 00 00 00 00 00 00 00 00 00', '00 CD D6 89',
                      '1Wire Device Handle attached on 1WireBus Handle', 'Address= 17 03 31 8D 00 00 00 1C',
                      '1Wire Device Handle authenticated and identified',
                      'OneWire_TestDeviceWritable: Handle Starting test',
                      'Saving OneWire memory to device Handle', 'OneWire_TestDeviceWritable: Handle Passed test',
                      'Handle used counts:   fire = 127, procedure = 143',
                      'Handle remain counts: fire = 34337, procedure = 9857', 'Saving OneWire memory to device Battery',
                      'OneWire_TestDeviceWritable: Battery Passed test',
                      'Spawning Task Priority 6, Keypad Condition Monitor Object', 'GUI_NewState: OLED_TEST',
                      'Active Versions:', 'System Version = 40.1.2.0.ENG', 'PP Timestamp   = 0x61F00E45',
                      'PP BL Timestamp= 0x615C7D01', 'Jed Timestamp  = 0x61F00D6D',
                      'Succeeded writing OneWire memory to device Battery', 'Memory = 02 02 04 32 37 30 35 32 30 31',
                      '39 2D 30 32 31 33 0D 0A 00 00', '00 00 00 00 00 00 00 00 00 00', '00 00 00 00 00 00 00 00 00 00',
                      '00 00 00 00 00 00 00 00 00 00', '00 00 00 00 00 00 00 00 00 00', '00 2D 72 95',
                      'Saving OneWire memory to device Handle', 'Succeeded writing OneWire memory to device Handle',
                      'Memory = 02 01 04 43 31 39 41 41 4B 30', '34 35 31 0D 0A 00 00 EB 7F 00',
                      'A0 86 8F 00 10 27 00 00 00 00', '00 00 00 00 00 A1 00 00 00 00', '00 00 00 00 00 00 00 00 00 00',
                      '00 00 00 00 00 00 00 00 00 00', '00 CE 96 88', 'Battery Design Charge Capacity = 2050',
                      'Full Charge Capacity = 1752', 'Battery Charge Cycle Count = 52', 'GUI_NewState: WELCOME_SCREEN',
                      'BQ Flash parameters have previously been validated',
                      'Bat1: BatV=8279,C1V=4140,C2V=4139,Cur=-89,CTemp=28.6,CalcRSOC=93,BqRSOC=99',
                      'Bat2: SSt=0h,OpSt=107h,ChrSt=410h,PFSt=0h,GSt=111Eh,TCA=0',
                      'dprintf queue full, waiting for room', 'dprintf queue ready', 'Blob Timestamp    = 0x61F00ECB',
                      'dprintf queue full, waiting for room', 'dprintf queue ready', 'Agile Number = 00000000',
                      'PP Rev       = 40.1.2.0.ENG', 'PP BL Rev    = 7.4.1', 'Jed Rev      = 8',
                      'Adapt BL Rev = 11.2.1', 'EGIA Rev     = 14.3.1', 'EEA Rev      = 5.1.2',
                      'jumpedFromBootloader = 1', 'TaskSPI2Tx running...Delay 5 Seconds', 'Battery log version = 11',
                      'Time: 2022-01-26 08:01:30', 'Data path: \\data\\data_001901\\001915',
                      'Handle serial number: C19AAK0451', 'Enter SPI startup sequence',
                      'AO_spawn_toPool() - priority = 8   Motor Test Object', 'Motor Test, Starting',
                      'Adapter, Strain Gauge Error = 19', 'MOTION IN PROGRESS', '***** FPGA_ReProgram start *****',
                      '!!FPGA Refresh Start!!', '!!FPGA Refresh Done!!', 'FPGA_ReProgram end', 'MOTION STOPPED',
                      'Motor 0 Stopped, Peak = 0, Valley = 0, CurLimit = 8000, SGUFPeak = -99.0, SGPeak = 0.0',
                      'Adapter, Strain Gauge Error = 19', 'MOTION IN PROGRESS', '***** FPGA_ReProgram start *****',
                      '!!FPGA Refresh Start!!', '!!FPGA Refresh Done!!', 'FPGA_ReProgram end', 'MOTION STOPPED',
                      'Motor 1 Stopped, Peak = 0, Valley = 0, CurLimit = 8000, SGUFPeak = -99.0, SGPeak = 0.0',
                      'Adapter, Strain Gauge Error = 19', 'MOTION IN PROGRESS', '***** FPGA_ReProgram start *****',
                      '!!FPGA Refresh Start!!', '!!FPGA Refresh Done!!', 'FPGA_ReProgram end', 'MOTION STOPPED',
                      'Motor 2 Stopped, Peak = 0, Valley = 0, CurLimit = 8000, SGUFPeak = -99.0, SGPeak = 0.0',
                      'Ending task priority 8 - Motor Test Object', 'Motor Test Results:',
                      'Motor A0 = PASS Motor B1 = PASS Motor C2 = PASS', 'Initialization complete',
                      'SM_NewSystemEventAlert: INIT_COMPLETE', 'Piezo: All Good', 'systemCheckCompleted complete',
                      'GUI_NewState: PROCEDURES_REMAINING', 'GUI_NewState: REQUEST_CLAMSHELL',
                      '*** Event Queue PRINT has 0 free ***', 'Going to standby', 'Turning off OLED']
    convertListtoLogFile(LogStringsList, 'StartUpLog.txt')
    #createOutputJsonFile(jsonpath="Input.json", logfilePath="StartUpLog.txt", TestType=TestType,
    #               merged_PassFailDict=merged_PassFailDict)
    calculatePassFail(ResultFileName="sample_result-11.txt", jsonpath="Input.json", logfilePath="StartUpLog.txt",
    #calculatePassFail(ResultFileName="sample_result-no-fire.txt", jsonpath="Input.json", logfilePath="StartUpLog.txt",
                      TestType=TestType, Changeset=Changeset, Integration_Build=Integration_Build)#, WithFiring=True)

    # update Test Config Dict, there is a possibility of updating *_NOT_Found values with the respective data which
    # is being passed
    '''
    "Test Config": {
                    "Test Type": "EGIA_Sanity_Checks",
                    "Test Date": "Test_Date_NOT_Found",
                    "Build Date": "BUILD_Date_NOT_Found",
                    "Changeset": "791",
                    "Integration Build": "True",
                    "Blob Version": "29.5.1.0.ENG",
                    "Power Pack Version": "Power_Pack_Version_NOT_Found",
                    "Power Pack Bootloader Version": "Power_Pack_Bootloder_Version_NOT_Found",
                    "Adapter EGIA Version": "Adapter_EGIA_Rev_NOT_Found",
                    "Adapter EEA Version": "Adapter_EEA_Rev_NOT_Found",
                    "Adapter Bootloader Version": "Adapter_Bootloader_Version_NOT_Found",
                    "Handle Serial Num": "C19AAK0451"
                    }
    '''
    update_SW_Config_Dict(ProjectName="P" , TestDate="A", BuildDate="B", BlobVersion="C", PowerPackVersion="D",
                          PowerPackBootloaderVersion="E",
                          AdapterEGIAVersion="F", AdapterEEAVersion="G", AdapterBootloaderVersion="H")
