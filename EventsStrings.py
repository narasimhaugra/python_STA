# @Author - Varun Pandey, dated - Jan 04, 2022
# Updated by Manoj Vadali - 27-Sep-2022 (Included EEA Test Strings)

# Purpose - To have a unified list of dictionary data for Events data which comprises
# as Key   : The Event Name
# as Value : List of Strings to Compare

# from pprint import pprint

# Purpose : Create the Event dictionary
def frameEventDict(Length=None, Color=None):
    # this dict has to be updated every time in case we find a new event which isn't present under this
    eventDict = {}
    # 'Remove Signia Power Handle from Charger'
    eventDict['Remove Signia Power Handle from Charger'] = ['GUI_NewState: WELCOME_SCREEN',
                                                            'Piezo: All Good',
                                                            'Initialization complete',
                                                            'SM_NewSystemEventAlert: INIT_COMPLETE',
                                                            'systemCheckCompleted complete',
                                                            'GUI_NewState: PROCEDURES_REMAINING',
                                                            'GUI_NewState: REQUEST_CLAMSHELL'
                                                            # 'Going to standby',
                                                            # 'Turning off OLED'
                                                            ]
    # 'Remove Signia Power Handle from Charger Low Battery'
    eventDict['Remove Signia Power Handle from Charger Low Battery'] = ['GUI_NewState: WELCOME_SCREEN',
                                                                        'Piezo: Low Battery',
                                                                        'Initialization complete',
                                                                        'SM_NewSystemEventAlert: INIT_COMPLETE',
                                                                        'systemCheckCompleted complete',
                                                                        'GUI_NewState: PROCEDURES_REMAINING',
                                                                        # 'GUI_NewState: REQUEST_CLAMSHELL',
                                                                        'Going to standby',
                                                                        'Turning off OLED'
                                                                        ]

    # 'Clamshell Connected'
    eventDict['Clamshell Connected'] = [' 1Wire Device Clamshell attached on 1WireBus Clamshell',
                                        '  1Wire Device Clamshell authenticated and identified',
                                        ' OneWire_TestDeviceWritable: Clamshell Starting test',
                                        ' Saving OneWire memory to device Clamshell',
                                        ' Succeeded writing OneWire memory to device Clamshell',
                                        ' OneWire_TestDeviceWritable: Clamshell Passed test',
                                        ' P_SIG_CLAMSHELL_CONNECTED',
                                        ' SM_NewSystemEventAlert: CLAMSHELL_INSTALLED',
                                        ' GUI_NewState: REQUEST_ADAPTER'
                                        ]
    eventDict['Adapter Connected 450475'] = ['EEA Adapter Values, StartPos(0)']
    # Adapter Connected
    eventDict['Adapter Connected'] = ['  1Wire Device Adapter authenticated and identified',
                                      ' GUI_NewState: ADAPTER_DETECTED',
                                      ' GUI_NewState: EGIA_ADAPTER_CALIBRATING',
                                      ' SM_NewSystemEventAlert: ADAPTER_FULLY_CALIBRATED',
                                      ' Piezo: All Good',
                                      ' GUI_NewState: EGIA_REQUEST_RELOAD'
                                      ]

    eventDict['EEA Adapter 1W Short Circuit in Fire Mode'] = ['GUI_NewState: EEA_FIREMODE_2',
                                                              'Transient short detected on 1Wire bus Reload, count = 1',
                                                              'Transient short detected on 1Wire bus Reload, count = 2']
                                                              #EEA]

    eventDict['EEA Adapter 1W Short Circuit Before Entering Fire Mode'] = [
        'Transient short detected on 1Wire bus Reload, count = 1',
        'Transient short detected on 1Wire bus Reload, count = 2',
        'Transient short detected on 1Wire bus Reload, count = 3']

    # Adapter Connected Low Battery
    eventDict['Adapter Connected Low Battery'] = ['  1Wire Device Adapter authenticated and identified',
                                                  ' GUI_NewState: ADAPTER_DETECTED',
                                                  ' GUI_NewState: EGIA_ADAPTER_CALIBRATING',
                                                  ' SM_NewSystemEventAlert: ADAPTER_FULLY_CALIBRATED',
                                                  ' Piezo: Low Battery',
                                                  ' GUI_NewState: EGIA_REQUEST_RELOAD'
                                                  ]

    ''
    eventDict['EEA Adapter Connected with UART Rx & Tx Open Circuit'] = [
        '1Wire Device Adapter authenticated and identified',
        ' GUI_NewState: ADAPTER_DETECTED',
        # ' GUI_NewState: EGIA_ADAPTER_CALIBRATING',
        # ' SM_NewSystemEventAlert: ADAPTER_FULLY_CALIBRATED',
        # ' Piezo: Low Battery',
        # ' GUI_NewState: EGIA_REQUEST_RELOAD'
        'SIG_RETRY_TIME_OUT',
        'Sending SERIALCMD_BOOT_ENTER to adapter',
        'No adapter CPU found.  Cycling power',
        'GUI_NewState: EGIA_ADAPTER_ERROR', 'Error: ADAPTER, ADAPTER_UART',
        'SM_NewSystemEventAlert: ADAPTER_UART_ERROR',
        'Piezo: Error Tone', 'ERROR EEA adapter HW version not retrieved, continuing to allow emergency operation only'

    ]

    eventDict['Tip Protector Detection'] = ['GUI_NewState: EEA_TPR_DETECTING',
                                            'EEA Clamp Cal, Anvil or TipProtector Detected!!!!',
                                            'Piezo: All Good',
                                            'GUI_NewState: EEA_ERR_TIP_REMOVAL']

    eventDict['Trocar Retraction Post Tip Protector Detection'] = ['System Status Query for Calibration',
                                                                   'System Status: OK to Calibrate',
                                                                   'GUI_NewState: EEA_CAL_START',
                                                                   '****  ENTERING OP TPR WRecID CALIBRATE STATE  ****',
                                                                   'WRITE Recovery ID (1) to EEA Adapter, Calibration',
                                                                   '****  ENTERING OP CALIBRATE SUPER STATE  ****',
                                                                   '****  ENTERING OP CAL WAdptTare ****',
                                                                   'SM_NewSystemEventAlert: ADAPTER_FULLY_CALIBRATED',
                                                                   'Piezo: All Good',
                                                                   'GUI_NewState: EEA_REQUEST_CARTRIDGE',
                                                                   '****  ENTERING OP CAL IDLE STATE  ****']

    eventDict['Pre-Calibrated EEA Adapter connected'] = ['  1Wire Device Adapter authenticated and identified',
                                                         ' GUI_NewState: ADAPTER_DETECTED',
                                                         ' GUI_NewState: EGIA_ADAPTER_CALIBRATING',
                                                         ' SM_NewSystemEventAlert: ADAPTER_FULLY_CALIBRATED',
                                                         ' Piezo: Low Battery',
                                                         ' GUI_NewState: EGIA_REQUEST_RELOAD'
                                                         ]

    eventDict['EEA Trocar Extention with Reload'] = [  # 'Go to FO WMotHead Opening State',
        # '****  ENTERING OP FO WMotHead Opening STATE  ****',
        'Sent Signal:  P_SIG_UNCLAMPING',
        'P_SIG_UNCLAMPING in GUI_MANAGER_EEA',
        'Sent Signal:  P_SIG_MOTOR_STOPPED',
        'P_SIG_MOTOR_STOPPED in GUI_MANAGER_EEA']

    eventDict['EEA Clamping on Tissue'] = ['P_SIG_CLAMPING in GUI_MANAGER_EEA',
                                           '****  ENTERING OP CHS IDLE STATE  ****',
                                           '****  ENTERING OP CLAMP HIGHSPEED SUPER STATE  ****',
                                           '****  ENTERING OP LOWSPEED CLAMP SUPER STATE  ****',
                                           '****  ENTERING OP CLAMP CTC SUPER STATE  ****',
                                           '****  ENTERING OP CTC Idle STATE  ****',
                                           'Piezo: Limit Reached',
                                           'Piezo: Fully Clamped',
                                           '****  ENTERING TISSUE RELAXATION STATE  ****',
                                           'LED_On',
                                           'GUI_NewState: EEA_TISSUE_RELAX']

    eventDict['EEA Green Key Ack'] = ['P_SIG_GREEN_KEY_PRESS: entering fire mode',
                                      'LED_Blink',
                                      'Piezo: Enter Fire Mode',
                                      'GUI_NewState: EEA_FIREMODE_1',
                                      # 'GUI_NewState: EEA_FIREMODE_2',#
                                      'SM_NewSystemEventAlert: GREEN_KEY_PRESS']

    eventDict['EEA Green Key Ack 400860'] = ['SM_NewSystemEventAlert: GREEN_KEY_PRESS',
                                      'Getting EEA Recovery State...',
                                      'Piezo: All Good' ]

    eventDict['EEA Firing'] = ['****  ENTERING OP FM WRldCfg STAPLES DETECTED STATE  ****',
                               '****  ENTERING HIGHSPEED FIRE STATE  ****',
                               '****  ENTERING LOWSPEED STAPLE SUPER STATE  ****',
                               '****  ENTERING OP LSS STAPLE DETECT STATE  ****',
                               '****  ENTERING OP LSS STAPLE FORMATION STATE  ****',
                               '****  ENTERING OP LSS WRecID STAPLE COMPLETE STATE  ****',
                               '****  ENTERING LOWSPEED CUT SUPER STATE  ****',
                               'Piezo: Complete Fire'
                               ]

    eventDict['EEA Firing with Adapter 1W Open Circuit'] = ['****  ENTERING OP FM WRldCfg STAPLES DETECTED STATE  ****',
                                                            '****  ENTERING HIGHSPEED FIRE STATE  ****',
                                                            '****  ENTERING LOWSPEED STAPLE SUPER STATE  ****',
                                                            '****  ENTERING OP LSS STAPLE DETECT STATE  ****',
                                                            '****  ENTERING OP LSS STAPLE FORMATION STATE  ****',
                                                            '****  ENTERING OP LSS WRecID STAPLE COMPLETE STATE  ****',
                                                            '****  ENTERING LOWSPEED CUT SUPER STATE  ****',
                                                           # 'Piezo: Complete Fire',
                                                            # 'GUI_NewState: EEA_TILT_PROMPT_1',
                                                            # 'GUI_NewState: EEA_TILT_PROMPT_2',
                                                            'Low Level OneWire Write of page 0 unsucessful after 5 tries',
                                                            'One Wire Low: Page 1 Write Unsucessful']

    eventDict['EEA Firing with Adapter 1W Short Circuit'] = [
        '****  ENTERING OP FM WRldCfg STAPLES DETECTED STATE  ****',
        '****  ENTERING HIGHSPEED FIRE STATE  ****',
        '****  ENTERING LOWSPEED STAPLE SUPER STATE  ****',
        '****  ENTERING OP LSS STAPLE DETECT STATE  ****',
        '****  ENTERING OP LSS STAPLE FORMATION STATE  ****',
        '****  ENTERING OP LSS WRecID STAPLE COMPLETE STATE  ****',
        '****  ENTERING LOWSPEED CUT SUPER STATE  ****',
        'Piezo: Complete Fire',
        # 'GUI_NewState: EEA_TILT_PROMPT_1',
        # 'GUI_NewState: EEA_TILT_PROMPT_2',
        'Low Level OneWire Write of page 0 unsucessful after 5 tries',
        'One Wire Low: Page 1 Write Unsucessful']

    eventDict['EEA Firing with Adapter UART Rx Tx Open Circuit'] = [
        '****  ENTERING OP FM WRldCfg STAPLES DETECTED STATE  ****',
        '****  ENTERING HIGHSPEED FIRE STATE  ****',
        '****  ENTERING LOWSPEED STAPLE SUPER STATE  ****',
        '****  ENTERING OP LSS STAPLE DETECT STATE  ****',
        '****  ENTERING OP LSS STAPLE FORMATION STATE  ****',
        '****  ENTERING OP LSS WRecID STAPLE COMPLETE STATE  ****',
        '****  ENTERING LOWSPEED CUT SUPER STATE  ****',
        'Piezo: Complete Fire',
        'GUI_SSENewState: EEA_TILT_PROMPT_1',
        'GUI_NewState: EEA_TILT_PROMPT_2',
        # 'Low Level OneWire Write of page 0 unsucessful after 5 tries',
        # 'One Wire Low: Page 1 Write Unsucessful',
        # 'One Wire Low: Page 1 Write Unsucessful',
        'Recovery Write: ID via OW',
        'OW Write Set Recovery ID']

    # Tilt Operation of Anvil
    eventDict['Tilt Operation of Anvil'] = [#'GUI_NewState: EEA_TILT_PROMPT_1',
                                            'GUI_NewState: EEA_TILT_STARTED',
                                            'GUI_NewState: EEA_TILT_MIDLOW',
                                            'GUI_NewState: EEA_TILT_MIDHIGH',
                                            '****  ENTERING OP T WRecID TILT COMPLETE STATE  ****',
                                            # '****  ENTERING OP T WRecID TILT COMPLETE STATE  ****
                                            'Piezo: Ready Tone',
                                            'GUI_NewState: EEA_TILT_COMPLETE',
                                            'GUI_NewState: EEA_TILT_OPEN_PROMPT_1',
                                            'GUI_NewState: EEA_TILT_OPEN_PROMPT_2',
                                            'WRITE Recovery ID (8) to EEA Adapter, Tilt Complete',
                                            'LED_Off'
                                            ]

    eventDict['Tilt Operation of Anvil with UART Rx & Tx Open Circuit'] = ['GUI_NewState: EEA_TILT_PROMPT_1',
                                                                           'GUI_NewState: EEA_TILT_PROMPT_2',
                                                                           'GUI_NewState: EEA_TILT_STARTED',
                                                                           'GUI_NewState: EEA_TILT_MIDLOW',
                                                                           'GUI_NewState: EEA_TILT_MIDHIGH',
                                                                           '****  ENTERING OP T WRecID TILT COMPLETE STATE  ****',
                                                                           # 'Piezo: Ready Tone',
                                                                           # 'GUI_NewState: EEA_TILT_COMPLETE',
                                                                           # 'GUI_NewState: EEA_TILT_OPEN_PROMPT_1',
                                                                           # 'GUI_NewState: EEA_TILT_OPEN_PROMPT_2',
                                                                           'GUI_NewState: EGIA_ADAPTER_ERROR',
                                                                           'Error: ADAPTER, ADAPTER_UART',
                                                                           'SM_NewSystemEventAlert: ADAPTER_UART_ERROR',
                                                                           'Piezo: Error Tone']

    # SSE
    eventDict['SSE'] = ['GUI_NewState: EEA_RELOAD_FULLY_OPEN',
                        'GUI_NewState: EEA_TILTOPEN_STARTED',
                        'GUI_NewState: EEA_TILTOPEN_COMPLETE',
                        'Tilt Open Complete - Going to Fire Retract',
                        '****  ENTERING FIRE RETRACT SUPER STATE  ****',
                        '****  ENTERING LOCKUP STATE  ****',
                        'Piezo: Complete Fire']

    eventDict['Tilt Prompt Open'] = ['GUI_NewState: EEA_RELOAD_FULLY_OPEN',
                                     'GUI_NewState: EEA_TILTOPEN_STARTED',
                                     'GUI_NewState: EEA_TILTOPEN_COMPLETE',
                                     'Tilt Open Complete - Going to Fire Retract',
                                     '****  ENTERING FIRE RETRACT SUPER STATE  ****',
                                     '****  ENTERING LOCKUP STATE  ****',
                                     'Piezo: Complete Fire']

    eventDict['EEA SURGICAL_SITE_EXTRACTION'] = ['****  ENTERING SURGICAL SITE EXTRACTION SUPER STATE  ****',
                                                 'Go to SSE Idle State'
                                                 ]
    eventDict['EEA Lock Screen Present'] = [' GUI_NewState: EEA_LOCKED',
                                            'Sent Graphic Signal (41), Locked']
    eventDict['SSE Fully Opening State'] = ['****  ENTERING OP SSE WMotHead Opening STATE  ****',
                                            'ACK, ACK, ACK - SSE WMotHead Opening State',
                                            'Start Motor Opening',
                                            'Sent Signal:  P_SIG_UNCLAMPING'
                                            ]
    eventDict['SSE Fully Closing State'] = ['****  ENTERING OP SSE WMotHead Closing STATE  ****',
                                            'ACK, ACK, ACK - SSE WMotHead Closing State',
                                            'Start Motor Closing',
                                            'Sent Signal:  P_SIG_CLAMPING'
                                            ]
    eventDict['EEA Surgical Site Exit Prompt Screens'] = ['GUI_NewState: EEA_SSE_ROTATE_PROMPT']

    eventDict['EEA Surgical Site Countdown Screens'] = ['GUI_NewState: EEA_SSE_COUNT1',
                                                        'GUI_NewState: EEA_TPR_DETECTING',
                                                        'Clamp Cal, StopStatus = 0x001',
                                                        'Piezo: Ready Tone',
                                                        'GUI_NewState: EEA_REMOVE_ADAPTER']

    eventDict['SSE with Adapter 1W Open Circuit'] = ['GUI_NewState: EEA_RELOAD_FULLY_OPEN',
                                                     'GUI_NewState: EEA_TILTOPEN_STARTED',
                                                     'GUI_NewState: EEA_TILTOPEN_COMPLETE',
                                                     'Tilt Open Complete - Going to Fire Retract',
                                                     '****  ENTERING FIRE RETRACT SUPER STATE  ****',
                                                     '****  ENTERING LOCKUP STATE  ****',
                                                     'Failed to write OneWire memory to device Adapter',
                                                     'GUI_NewState: EGIA_ADAPTER_ERROR',
                                                     'Error: ADAPTER, ONEWIRE_WRITE_ERROR',
                                                     'Piezo: Error Tone',
                                                     'Low Level OneWire Write of page 0 unsucessful after 5 tries',
                                                     'One Wire Low: Page 1 Write Unsucessful']

    eventDict['Tilt Prompt Open with Adapter 1W Open Circuit'] = ['GUI_NewState: EEA_RELOAD_FULLY_OPEN',
                                                                  'GUI_NewState: EEA_TILTOPEN_STARTED',
                                                                  'GUI_NewState: EEA_TILTOPEN_COMPLETE',
                                                                  'Tilt Open Complete - Going to Fire Retract',
                                                                  '****  ENTERING FIRE RETRACT SUPER STATE  ****',
                                                                  '****  ENTERING LOCKUP STATE  ****',
                                                                  'Failed to write OneWire memory to device Adapter',
                                                                  'GUI_NewState: EGIA_ADAPTER_ERROR',
                                                                  'Error: ADAPTER, ONEWIRE_WRITE_ERROR',
                                                                  'Piezo: Error Tone',
                                                                  'Low Level OneWire Write of page 0 unsucessful after 5 tries',
                                                                  'One Wire Low: Page 1 Write Unsucessful']

    eventDict['SSE with Adapter 1W Short Circuit'] = ['GUI_NewState: EEA_RELOAD_FULLY_OPEN',
                                                      'GUI_NewState: EEA_TILTOPEN_STARTED',
                                                      'GUI_NewState: EEA_TILTOPEN_COMPLETE',
                                                      'Tilt Open Complete - Going to Fire Retract',
                                                      '****  ENTERING FIRE RETRACT SUPER STATE  ****',
                                                      '****  ENTERING LOCKUP STATE  ****',
                                                      # 'GUI_NewState: EGIA_ADAPTER_ERROR',
                                                      # 'Error: ADAPTER, ONEWIRE_WRITE_ERROR',
                                                      'Piezo: Complete Fire',
                                                      'Low Level OneWire Write of page 0 unsucessful after 5 tries',
                                                      'One Wire Low: Page 1 Write Unsucessful']

    eventDict['SSE with Adapter UART Rx & Tx Open Circuit'] = ['GUI_NewState: EEA_RELOAD_FULLY_OPEN',
                                                               'GUI_NewState: EEA_TILTOPEN_STARTED',
                                                               'GUI_NewState: EEA_TILTOPEN_COMPLETE',
                                                               'Tilt Open Complete - Going to Fire Retract',
                                                               '****  ENTERING FIRE RETRACT SUPER STATE  ****',
                                                               '****  ENTERING LOCKUP STATE  ****',
                                                               # 'GUI_NewState: EGIA_ADAPTER_ERROR',
                                                               # 'Error: ADAPTER, ONEWIRE_WRITE_ERROR',
                                                               'GUI_NewState: EEA_RELOAD_FULLY_OPEN',
                                                               'Piezo: Complete Fire',
                                                               # 'Low Level OneWire Write of page 0 unsucessful after 5 tries',
                                                               # 'One Wire Low: Page 1 Write Unsucessful'
                                                               'Recovery Write: ID via OW', 'OW Write Set Recovery ID']

    eventDict['Tilt Prompt Open with Adapter UART Rx & Tx Open Circuit'] = ['GUI_NewState: EEA_RELOAD_FULLY_OPEN',
                                                                            'GUI_NewState: EEA_TILTOPEN_STARTED',
                                                                            'GUI_NewState: EEA_TILTOPEN_COMPLETE',
                                                                            'Tilt Open Complete - Going to Fire Retract',
                                                                            '****  ENTERING FIRE RETRACT SUPER STATE  ****',
                                                                            '****  ENTERING LOCKUP STATE  ****',
                                                                            'GUI_NewState: EEA_RELOAD_FULLY_OPEN',
                                                                            'Piezo: Complete Fire',
                                                                            'OW Write Set Recovery ID']

    eventDict['EEA Remove Reload'] = ['P_SIG_RELOAD_REMOVED']

    eventDict['Remove EEA Adapter'] = ['1Wire Device Adapter removed!',
                                       'GUI_AdapterDisconnected',
                                       'GUI_NewState: REQUEST_ADAPTER']

    eventDict['Remove EEA Adapter with Adapter 1W Short Circuit'] = ['1Wire Device Adapter removed!',
                                                                     'GUI_AdapterDisconnected',
                                                                     'GUI_NewState: REQUEST_ADAPTER']
    # , 'Transient short detected on 1Wire bus Adapter, count = 1',
    #                                                              'Transient short detected on 1Wire bus Adapter, count = 2', 'Transient short detected on 1Wire bus Adapter, count = 3',
    #                                                              'Error: ADAPTER, ONEWIRE_SHORT', 'SM_NewSystemEventAlert: ONEWIRE_SHORT_ERROR',
    #                                                              'Piezo: Error Tone', 'Low Level OneWire Write of page 0 unsucessful after 5 tries', 'One Wire Low: Page 1 Write Unsucessful']

    eventDict['Remove EEA Adapter with Clamshell 1W Open Circuit'] = ['1Wire Device Adapter removed!',
                                                                      'GUI_AdapterDisconnected',
                                                                      'GUI_NewState: REQUEST_ADAPTER',
                                                                      '1Wire Device Clamshell removed!',
                                                                      'P_SIG_CLAMSHELL_REMOVED',
                                                                      'GUI_NewState: REQUEST_CLAMSHELL']

    eventDict['Remove EEA Adapter with Clamshell 1W Short Circuit'] = ['1Wire Device Adapter removed!',
                                                                       'GUI_AdapterDisconnected',
                                                                       'GUI_NewState: REQUEST_ADAPTER',
                                                                       'Error: CLAMSHELL, ONEWIRE_SHORT',
                                                                       # 'Piezo: Error Tone',
                                                                       'SM_Charger: On battery charger. Waiting for system init.']

    eventDict['EEA Adapter UART Rx & Tx Open Circuit'] = [
        # 'Adapter in ExitBootloader', updated this string on 10th Nov
        '---- ADAPTER: ENTERING EEA EXIT BOOTLOADER STATE ----', '5V on retry']

    eventDict['EEA Adapter UART Rx & Tx Open Circuit Restored'] = ['Adapter UART Error Recovered',
                                                                   'Adapter in Main App']

    eventDict['EEA Adapter Connected With Restored Rx & Tx'] = ['Reload has no firings remaining',
                                                                'Piezo: Caution Tone',
                                                                'Piezo: Error Tone',
                                                                'GUI_NewState: EEA_ERR_ADAPTER'
                                                                ]
    eventDict['EEA Trocar Extention with SSE'] = ['****  ENTERING OP SSE Idle STATE  ****',
                                                  'GUI_NewState: EEA_FULL_OPEN_PROMPT',
                                                  'GUI_NewState: EEA_ERR_ADAPTER'
                                                  ]

    eventDict['Remove EEA Reload with SSE Prompt'] = ['GUI_NewState: EEA_SSE_ROTATE_PROMPT']

    eventDict['EEA SSE Countdown Exit'] = ['GUI_NewState: EEA_SSE_COUNT1',
                                           'GUI_NewState: EEA_TPR_DETECTING',
                                           'Clamp Cal, StopStatus = 0x001',
                                           'Piezo: Ready Tone',
                                           'GUI_NewState: EEA_REMOVE_ADAPTER']

    eventDict['EEA Green Key Ack With UART Rx Tx Restored'] = ['Error:  Adapter Communications Lost',
                                                               'Piezo: Error Tone', ]
    # Green Right Key Pressed

    # Adapter CW Rotated
    eventDict['Adapter CW Rotated'] = [' ****  ENTERING AO EGIA Rotate CW STATE  ****',
                                       ' ****  ENTERING AO EGIA Idle STATE  ****'
                                       ]

    # Adapter CCW Rotated
    eventDict['Adapter CCW Rotated'] = [' ****  ENTERING AO EGIA Rotate CCW STATE  ****',
                                        ' ****  ENTERING AO EGIA Idle STATE  ****'
                                        ]

    # 'Tri-Staple Connected'
    eventDict['Tri-Staple Connected'] = ['P_SIG_RELOAD_SWITCH_EVENT: switch closed',
                                         'Dumb reload',
                                         ' SM_NewSystemEventAlert: RELOAD_INSTALLED',
                                         ' GUI_NewState: EGIA_WAIT_FOR_CLAMP_CYCLE_CLOSE'
                                         ]

    if Length and Color:
        eventDict['SULU Connected'] = [' 1Wire Device Reload attached on 1WireBus Reload',
                                       ' P_SIG_RELOAD_SWITCH_EVENT: switch closed',
                                       f' ReloadConnected: Type=SULU, Length={Length}, Color={Color}',
                                       ' Smart reload', ' SM_NewSystemEventAlert: RELOAD_INSTALLED',
                                       ' GUI_NewState: EGIA_WAIT_FOR_CLAMP_CYCLE_CLOSE'
                                       ]

        # if Length and Color:
        # 'Cartridge Connected'
        eventDict['Cartridge Connected'] = [' 1Wire Device Cartridge attached on 1WireBus Reload',
                                            ' OneWire_TestDeviceWritable: Cartridge Passed test',
                                            ' SM_NewSystemEventAlert: CARTRIDGE_INSTALLED',
                                            f' CartridgeConnected: Length={Length}, Color={Color}']

        eventDict['EEA RELOAD Connected with Ship cap'] = [' 1Wire Device Reload attached on 1WireBus Reload',
                                                           '****  ENTERING OP SCR IDLE STATE  ****',
                                                           'Smart reload', ' GUI_NewState: EEA_SHIPCAP_REMOVAL',
                                                           ' GUI_NewState: EEA_SHIPCAP_READY'
                                                           ]

        eventDict['EEA RELOAD Connected with Ship cap Diameter 31 or 33'] = [' 1Wire Device Reload authenticated and identified',
                                                           'SM_NewSystemEventAlert: RELOAD_INSTALLED',
                                                           'Smart reload',
                                                            'P_SIG_RELOAD_CONNECTED'
                                                           ]

        eventDict['EEA RELOAD Connected without Ship cap'] = [' 1Wire Device Reload attached on 1WireBus Reload',
                                                              # f' Reload Values, Size {Length}, Reload Values, Color {Color}',#
                                                              'Smart reload',
                                                              ' SM_NewSystemEventAlert: RELOAD_INSTALLED',
                                                              '****  ENTERING FULL OPEN SUPER STATE  ****',
                                                              '****  ENTERING OP FO IDLE STATE  ****',
                                                              'GUI_NewState: EEA_FULL_OPEN_PROMPT'

                                                              ]
        eventDict['EEA RELOAD Connected with TAID'] = ['Sent Graphic Signal (4), TAID Removal, Ready',
                                                           'GUI_NewState: EEA_TAID_READY',
                                                           ]

    elif Length:
        # 'MULU Connected'
        eventDict['MULU Connected'] = [' 1Wire Device Reload attached on 1WireBus Reload',
                                       ' P_SIG_RELOAD_SWITCH_EVENT: switch closed',
                                       f' ReloadConnected: Type=MULU, Length={Length}',
                                       f' Smart reload', ' SM_NewSystemEventAlert: RELOAD_INSTALLED',
                                       ' GUI_NewState: EGIA_WAIT_FOR_CLAMP_CYCLE_CLOSE'
                                       ]

    # 'Clamp Cycle Test Clamping'
    eventDict['Clamp Cycle Test Clamping'] = [' ****  ENTERING AO EGIA Clamp STATE  ****',
                                              ' SM_NewSystemEventAlert: FULLY_CLAMPED',
                                              ' Piezo: Fully Clamped',
                                              ' GUI_NewState: EGIA_WAIT_FOR_CLAMP_CYCLE_OPEN'
                                              ]

    # 'Clamp Cycle Test Un-Clamping'
    eventDict['Clamp Cycle Test Un-Clamping'] = [' ****  ENTERING AO EGIA Unclamp STATE  ****',
                                                 ' EGIA FireRod, FULLY OPEN',
                                                 ' SM_NewSystemEventAlert: CLAMPCYCLE_DONE',
                                                 ' Piezo: Ready Tone'
                                                 ]

    # 'MULU Clamp Cycle Test Clamping without Cartridge'
    eventDict['MULU Clamp Cycle Test Clamping without Cartridge'] = [' ****  ENTERING AO EGIA Clamp STATE  ****',
                                                                     ' SM_NewSystemEventAlert: FULLY_CLAMPED',
                                                                     ' Piezo: Fully Clamped',
                                                                     ' GUI_NewState: EGIA_WAIT_FOR_CLAMP_CYCLE_OPEN',
                                                                     'Get Allowed To Fire:',
                                                                     'NO: Invalid Cartridge OneWire data',
                                                                     'NO: cartridge OneWire write test FAILED',
                                                                     'NO: cartridge not connected',
                                                                     'NO: cartridge not authenticated',
                                                                     'NO: clamp cycle not completed']

    # 'MULU Clamp Cycle Test Un-Clamping without Cartidge'
    eventDict['MULU Clamp Cycle Test Un-Clamping without Cartridge'] = [' ****  ENTERING AO EGIA Unclamp STATE  ****',
                                                                        ' EGIA FireRod, FULLY OPEN',
                                                                        ' SM_NewSystemEventAlert: CLAMPCYCLE_DONE',
                                                                        'GUI_NewState: EGIA_RELOAD_NOT_FULLY_CLAMPED'
                                                                        ]

    # 'Clamp Cycle Test Un-Clamping Low Battery'
    eventDict['Clamp Cycle Test Un-Clamping Low Battery'] = [' ****  ENTERING AO EGIA Unclamp STATE  ****',
                                                             ' EGIA FireRod, FULLY OPEN',
                                                             ' SM_NewSystemEventAlert: CLAMPCYCLE_DONE',
                                                             ' Piezo: Low Battery'
                                                             ]

    # 'Adapter 1W SC with Reload'
    eventDict['Adapter 1W SC with Reload'] = ['Transient short detected on 1Wire bus Reload, count = 1',
                                              'Transient short detected on 1Wire bus Reload, count = 2',
                                              'Latching short on 1Wire bus Reload']

    # 'Clamping on Tissue'
    eventDict['Clamping on Tissue'] = [' SM_NewSystemEventAlert: FULLY_CLAMPED',
                                       ' GUI_NewState: EGIA_RELOAD_FULLY_CLAMPED',
                                       ' Get Allowed To Fire:',
                                       '   YES: allowed to fire',
                                       ' LED_On',
                                       ' Piezo: Fully Clamped'
                                       '****  ENTERING OP CLAMP CTC SUPER STATE  ****',
                                       'Piezo: Limit Reached',
                                       'GUI_NewState: EEA_CTC_CLAMP_50',
                                       'GUI_NewState: EEA_CTC_CLAMP_0',
                                       'GUI_NewState: EEA_CTC_CLAMP_75',
                                       'CTC Percent = 100',
                                       'GUI_NewState: EEA_TISSUE_RELAX',
                                       'Piezo: Ready Tone'
                                       ]

    # 'Green Key Ack'
    eventDict['Green Key Ack'] = [' P_SIG_GREEN_KEY_PRESS: entering fire mode',
                                  ' LED_Blink',
                                  # ' GUI_NewState: EGIA_ENTERED_FIRE_MODE',
                                  'GUI_NewState: EEA_FIREMODE_1',
                                  ' ****  ENTERING AO EGIA Fire Idle STATE  ****',
                                  ' Piezo: Enter Fire Mode',
                                  'GUI_NewState: EEA_FIREMODE_2'
                                  ]


    # Firing
    eventDict['Firing'] = ['  ****  ENTERING AO EGIA Firing STATE  ****',
                           ' GUI_NewState: EGIA_FIRE_COMPLETE',
                           ' Piezo: Complete Fire'
                           ]
    # Firing with Adapter UART Rx Tx OC
    eventDict['Firing with Adapter UART Rx Tx OC'] = ['  ****  ENTERING AO EGIA Firing STATE  ****',
                                                      ' GUI_NewState: EGIA_FIRE_COMPLETE',
                                                      ' Piezo: Complete Fire', 'Adapter, Strain Gauge Error = 1'
                                                      ]

    # Retracting
    eventDict['Retracting'] = [' ****  ENTERING AO EGIA Retract STATE  ****',
                               ' GUI_NewState: EGIA_RETRACT_COMPLETE',
                               ' LED_On'
                               ]

    # Adapter 1W OC Retracting (adapter OC before firing mode during retracting "'Latching short on 1Wire bus Reload" is not coming
    eventDict['Adapter 1W OC Retracting'] = [' ****  ENTERING AO EGIA Retract STATE  ****',
                                             ' GUI_NewState: EGIA_RETRACT_COMPLETE',
                                             ' LED_On', 'Low Level OneWire Write of page 0 unsucessful after 5 tries',
                                             'One Wire Low: Page 1 Write Unsucessful']

    # Adapter 1W SC Retracting
    eventDict['Adapter 1W SC Retracting'] = [' ****  ENTERING AO EGIA Retract STATE  ****',
                                             ' GUI_NewState: EGIA_RETRACT_COMPLETE',
                                             ' LED_On', 'Low Level OneWire Write of page 0 unsucessful after 5 tries',
                                             'One Wire Low: Page 1 Write Unsucessful',
                                             ]
    # Adapter UART Rx Tx OC Retracting
    eventDict['Adapter UART Rx Tx OC Retracting'] = [' ****  ENTERING AO EGIA Retract STATE  ****',
                                                     ' GUI_NewState: EGIA_RETRACT_COMPLETE',
                                                     ' LED_On',
                                                     'Low Level OneWire Write of page 0 unsucessful after 5 tries',
                                                     'One Wire Low: Page 1 Write Unsucessful',
                                                     'Adapter, Strain Gauge Error = 1',
                                                     'GUI_NewState: EGIA_ADAPTER_ERROR', 'Error: ADAPTER, ADAPTER_UART',
                                                     'SM_NewSystemEventAlert: ADAPTER_UART_ERROR', 'Piezo: Error Tone']

    # Clamshell 1W OC Retracting
    eventDict['Clamshell 1W OC Retracting'] = ['Adapter NOT yet stored in clamshell 1Wire memory',
                                               '****  ENTERING AO EGIA Retract STATE  ****',
                                               ' GUI_NewState: EGIA_RETRACT_COMPLETE',
                                               'Latching short on 1Wire bus Reload',
                                               ' LED_On', 'Low Level OneWire Write of page 0 unsucessful after 5 tries',
                                               'One Wire Low: Page 1 Write Unsucessful',
                                               ]

    # Clamshell 1W SC Retracting
    eventDict['Clamshell 1W SC Retracting'] = ['Adapter NOT yet stored in clamshell 1Wire memory',
                                               '****  ENTERING AO EGIA Retract STATE  ****',
                                               ' GUI_NewState: EGIA_RETRACT_COMPLETE',
                                               ' LED_On', 'Low Level OneWire Write of page 0 unsucessful after 5 tries',
                                               'One Wire Low: Page 1 Write Unsucessful',
                                               ]
    # UART disconnection #20:52:17  4958130: Adapter in ExitBootloader  0:52:17  4958140: 5V on retry

    # fire completion : Adapter, Strain Gauge Error = 1

    # Adapter 1W OC Before Fire Mode
    eventDict['Adapter 1W OC Before Fire Mode'] = ['Latching short on 1Wire bus Reload']

    # Unclamping
    eventDict['Unclamping'] = [' ****  ENTERING AO EGIA Unclamp STATE  ****',
                               ' EGIA FireRod, FULLY OPEN',
                               ' ****  ENTERING AO EGIA Idle STATE  ****',
                               ' LED_Off']

    # Unclamping with Adapter UART Rx Tx OC Before Firing
    eventDict['Unclamping with Adapter UART Rx Tx OC Before Firing'] = [' ****  ENTERING AO EGIA Unclamp STATE  ****',
                                                                        ' EGIA FireRod, FULLY OPEN',
                                                                        ' ****  ENTERING AO EGIA Idle STATE  ****',
                                                                        ' Adapter, Strain Gauge Error = 1']

    # Unclamping with Adapter UART Rx Tx OC in Fire Mode
    eventDict['Unclamping with Adapter UART Rx Tx OC in Fire Mode'] = [' ****  ENTERING AO EGIA Unclamp STATE  ****',
                                                                       ' EGIA FireRod, FULLY OPEN',
                                                                       ' ****  ENTERING AO EGIA Idle STATE  ****',
                                                                       ' Adapter, Strain Gauge Error = 1']

    # Adapter UART Rx Tx OC Before Fire Mode
    eventDict['Adapter UART Rx Tx OC Before Fire Mode'] = ['Adapter in ExitBootloader', '5V on retry',
                                                           'GUI_NewState: EGIA_ADAPTER_ERROR',
                                                           'Error: ADAPTER, ADAPTER_UART',
                                                           'SM_NewSystemEventAlert: ADAPTER_UART_ERROR',
                                                           'Piezo: Error Tone']

    # Adapter UART Rx Tx OC without Reload 01:43:18  16607309: Adapter in ExitBootloader
    eventDict['Adapter UART Rx Tx OC without Reload'] = ['Adapter in ExitBootloader', '5V on retry',
                                                         'GUI_NewState: EGIA_ADAPTER_ERROR',
                                                         'Error: ADAPTER, ADAPTER_UART',
                                                         'SM_NewSystemEventAlert: ADAPTER_UART_ERROR',
                                                         'Piezo: Error Tone']

    # Adapter UART Rx Tx OC in Fire Mode
    eventDict['Adapter UART Rx Tx OC in Fire Mode'] = ['Adapter in ExitBootloader', '5V on retry']

    # Green Key ACK - Adapter UART Rx Tx OC Before Fire Mode
    eventDict['Green Key ACK - Adapter UART Rx Tx OC Before Fire Mode'] = ['Get Allowed To Fire:',
                                                                           'NO: adapter communications lost',
                                                                           'NO: strain gauge not streaming',
                                                                           'SM_NewSystemEventAlert: GREEN_KEY_PRESS',
                                                                           'Adapter error', 'Piezo: Error Tone',
                                                                           'GUI_NewState: EGIA_RELOAD_NOT_FULLY_CLAMPED']

    # 'Remove Reload'
    eventDict['Remove Reload'] = [' GUI_NewState: EGIA_REQUEST_RELOAD']

    # 'Remove Cartridge'
    eventDict['Remove Cartridge'] = ['1Wire Device Cartridge removed!']

    # 'Remove Reload Adapter 1W OC in Fire Mode'
    eventDict['Remove Reload - Adapter 1W OC in Fire Mode'] = [
        'Low Level OneWire Write of page 0 unsucessful after 5 tries', 'One Wire Low: Page 1 Write Unsucessful',
        'Failed to write OneWire memory to device Adapter', 'GUI_NewState: EGIA_ADAPTER_ERROR',
        'SM_NewSystemEventAlert: UNKNOWN_ADAPTER', 'Error: ADAPTER, ONEWIRE_WRITE_ERROR',
        'Piezo: Error Tone']
    # 'Remove Reload - Clamshell 1W OC in Fire Mode & before fire mode'
    eventDict['Remove Reload - Clamshell 1W OC'] = ['Low Level OneWire Write of page 0 unsucessful after 5 tries',
                                                    'One Wire Low: Page 1 Write Unsucessful',
                                                    'Failed to write OneWire memory to device Clamshell',
                                                    'GUI_NewState: EGIA_REQUEST_RELOAD']

    # 'Remove Reload - Clamshell 1W SC in Fire Mode & before fire mode'
    eventDict['Remove Reload - Clamshell 1W SC'] = ['Low Level OneWire Write of page 0 unsucessful after 5 tries',
                                                    'One Wire Low: Page 1 Write Unsucessful',
                                                    'Transient short detected on 1Wire bus Adapter, count = 1',
                                                    'Failed to write OneWire memory to device Clamshell',
                                                    'GUI_NewState: EGIA_REQUEST_RELOAD']
    # 'Remove Reload - Adapter 1W SC in Fire Mode & before fire mode' - removed'Error: ADAPTER, ONEWIRE_WRITE_ERROR',
    eventDict['Remove Reload - Adapter 1W SC'] = ['Low Level OneWire Write of page 0 unsucessful after 5 tries',
                                                  'Transient short detected on 1Wire bus Adapter, count = 1',
                                                  'Failed to write OneWire memory to device Adapter',
                                                  'One Wire Low: Page 1 Write Unsucessful',
                                                  'GUI_NewState: EGIA_REQUEST_RELOAD',
                                                  'GUI_NewState: EGIA_ADAPTER_ERROR',
                                                  'SM_NewSystemEventAlert: UNKNOWN_ADAPTER',
                                                  'Piezo: Error Tone', 'Short detected on 1Wire bus Adapter',
                                                  'Error: ADAPTER, ONEWIRE_SHORT',
                                                  'SM_NewSystemEventAlert: ONEWIRE_SHORT_ERROR']

    # 'Remove Reload Adapter 1W OC Before Fire Mode'
    eventDict['Remove Reload - Adapter 1W OC Before Fire Mode'] = [
        'Low Level OneWire Write of page 0 unsucessful after 5 tries', 'One Wire Low: Page 1 Write Unsucessful',
        'Failed to write OneWire memory to device Adapter', 'GUI_NewState: EGIA_ADAPTER_ERROR',
        'SM_NewSystemEventAlert: UNKNOWN_ADAPTER', 'Error: ADAPTER, ONEWIRE_WRITE_ERROR',
        'Piezo: Error Tone']

    # Remove Reload Emergency Retraction
    eventDict['Remove Reload Emergency Retraction'] = ['P_SIG_RELOAD_SWITCH_EVENT: switch opened',
                                                       'GUI_NewState: EGIA_ADAPTER_CALIBRATING',
                                                       ' Piezo: All Good', 'Calibration successful',
                                                       'SM_NewSystemEventAlert: ADAPTER_FULLY_CALIBRATED',
                                                       'GUI_NewState: EGIA_REQUEST_RELOAD'
                                                       ]

    # Remove Adapter
    eventDict['Remove Adapter'] = ['1Wire Device Adapter removed!',
                                   '$$ WARNING:  ADAPTER REMOVED!!! $$',
                                   ' GUI_NewState: REQUEST_ADAPTER'
                                   ]

    # Remove Adapter - Clamshell 1W SC
    eventDict['Remove Adapter - Clamshell 1W SC'] = [' GUI_NewState: REQUEST_ADAPTER',
                                                     'Short detected on 1Wire bus Clamshell',
                                                     'Error: CLAMSHELL, ONEWIRE_SHORT',
                                                     'SM_NewSystemEventAlert: ONEWIRE_SHORT_ERROR', 'Piezo: Error Tone',
                                                     'SM_Charger: On battery charger. Waiting for system init.']

    # Remove Adapter - Emergency Retraction
    eventDict['Remove Adapter - Emergency Retraction'] = [' GUI_NewState: REQUEST_ADAPTER',
                                                          'Short detected on 1Wire bus Clamshell',
                                                          'Error: CLAMSHELL, ONEWIRE_SHORT,',
                                                          'SM_NewSystemEventAlert: ONEWIRE_SHORT_ERROR',
                                                          'Piezo: Error Tone',
                                                          'SM_Charger: On battery charger. Waiting for system init.']

    # Remove Clamshell
    eventDict['Remove Clamshell'] = ['1Wire Device Clamshell removed!',
                                     'P_SIG_CLAMSHELL_REMOVED',
                                     'GUI_NewState: REQUEST_CLAMSHELL']

    # On-Charger
    eventDict['On-Charger'] = ['1Wire Device Charger attached on 1WireBus Handle',
                               ' SM_Charger: On battery charger. Waiting for system init.',
                               ' SM_Charger: OneWire data has been written', ' SM_Charger: Charging!',
                               ' Successfully sent BEGIN_CHARGING msg to charger']

    # 'Ship Mode'
    eventDict['Ship Mode'] = [' SM_NewSystemEventAlert: SYSTEM_SHUTDOWN',
                              ' Piezo: Shut Down',
                              ' Powering off the motorpack!',
                              ]

    # 'Power Pack wakeup from Ship Mode'
    eventDict['Power Pack wakeup from Ship Mode'] = [' GUI_NewState: WELCOME_SCREEN',
                                                     ' Piezo: All Good',
                                                     ' Initialization complete',
                                                     ' SM_NewSystemEventAlert: INIT_COMPLETE',
                                                     ' systemCheckCompleted complete',
                                                     ' GUI_NewState: PROCEDURES_REMAINING',
                                                     ' GUI_NewState: REQUEST_CLAMSHELL',
                                                     ' Going to standby',
                                                     ' Turning off OLED'
                                                     ]

    # Emergency Retracting
    eventDict['Emergency Retracting'] = ['1Wire Device Adapter attached on 1WireBus Adapter',
                                         ' GUI_NewState: EGIA_RELOAD_DURING_CALIBRATION',
                                         ' Piezo: Retract Tone', 'Adapter Attached: reloadConnected = 1',
                                         ' Piezo: Caution Tone'
                                         ]

    # Reload Right Articulation
    eventDict['Right Articulation'] = ['****  ENTERING AO EGIA Artic Right STATE  ****',
                                       ' ****  ENTERING AO EGIA Idle STATE  ****']
    # Reload Left Articulation
    eventDict['Left Articulation'] = ['****  ENTERING AO EGIA Artic Left STATE  ****',
                                      ' ****  ENTERING AO EGIA Idle STATE  ****']
    # Reload Center Articulation
    eventDict['Centering Articulation'] = ['****  ENTERING AO EGIA Artic Center STATE  ****',
                                           ' ****  ENTERING AO EGIA Idle STATE  ****']

    # Remove Signia Power Handle from Charger - Charge Cycle'
    eventDict['Remove Signia Power Handle from Charger - Charge Cycle'] = [' GUI_NewState: WELCOME_SCREEN',
                                                                           ' Piezo: All Good',
                                                                           ' Initialization complete',
                                                                           ' SM_NewSystemEventAlert: INIT_COMPLETE',
                                                                           ' systemCheckCompleted complete']

    ##   EEA Specific Log Strings ##
    # EEA Adapter Connected # Updated this to reflect integrated trocar by Manoj Vadali on 6th November 2023
    eventDict['EEA Adapter Connected'] = ['  1Wire Device Adapter authenticated and identified',
                                          ' GUI_NewState: ADAPTER_DETECTED',
                                          '****  ENTERING EEA INITIALIZE STATE  ****',
                                          '****  ENTERING OPERATE SUPER STATE  ****',
                                          # '****  ENTERING TIP PROTECTOR REMOVAL SUPER STATE  ****',
                                          'System Status Query for Calibration',
                                          'System Status: OK to Calibrate',
                                          # added below strings (6th Nov 23)
                                          'GUI_NewState: EEA_CAL_START',
                                          '****  ENTERING OP CALIBRATE SUPER STATE  ****',
                                          '****  ENTERING OP CAL WAdptTare ****',
                                          'SM_NewSystemEventAlert: ADAPTER_FULLY_CALIBRATED',
                                          'Piezo: All Good',
                                          'GUI_NewState: EEA_REQUEST_CARTRIDGE',
                                          '****  ENTERING OP CAL IDLE STATE  ****']

    eventDict['Trocar Home Position'] = ['Clamp Cal, StopStatus = 0x001']

    eventDict['Adapter reset string'] = ['GUI_NewState: EEA_RELOAD_FULLY_OPEN']

    eventDict['Error Screens - Obstruction On Trocar Close'] = ['Actively Detecting Obstruction Force',
                                                                'Piezo: Caution Tone',
                                                                'GUI_NewState: EEA_ERR_OBS_FORCE_OPEN_1',
                                                                'GUI_NewState: EEA_ERR_OBS_FORCE_OPEN_2']

    eventDict['Error Screens - Obstruction On Trocar Open'] = ['GUI_NewState: EEA_ERR_OBS_FORCE_CLOSE_1',
                                                               'GUI_NewState: EEA_ERR_OBS_FORCE_CLOSE_2']

    eventDict['Low Speed Clamping zone'] = ['****  ENTERING OP LOWSPEED CLAMP SUPER STATE  ****',
                                            'GUI_NewState: EEA_CTC_THIN_TISSUE',
                                            '****  ENTERING OP CLAMP CTC SUPER STATE  ****',
                                            'GUI_NewState: EEA_CTC_THIN_TISSUE',
                                            'Piezo: Caution Tone',
                                            'LED_On']

    eventDict['EEA Locked'] = ['GUI_NewState: EEA_LOCKED']
    eventDict['EEA Caution Tone'] = ['Piezo: Caution Tone']
    eventDict['EEA Trocar Position Screen'] = ['GUI_NewState: EEA_FULL_OPEN_PROMPT']
    eventDict['Remove Adapter When 1st EEA Stapling In Progress'] = [
                                                '****  ENTERING OP FM WRldCfg STAPLES DETECTED STATE  ****',
                                                'WRITE Recovery ID (5) to EEA Adapter, Staple Started',
                                                '1Wire Device Adapter removed!',
                                                '$$ WARNING:  ADAPTER REMOVED!!! $$',
                                                'LED_Off',
                                                'GUI_NewState: REQUEST_ADAPTER']

    eventDict['Remove Adapter When 2nd EEA Stapling In Progress'] = [
                                        '****  ENTERING OP FM WRldCfg STAPLES DETECTED STATE  ****',
                                        'WRITE Recovery ID (6) to EEA Adapter, Staple Complete',
                                        '1Wire Device Adapter removed!',
                                        '$$ WARNING:  ADAPTER REMOVED!!! $$',
                                        'LED_Off',
                                        'GUI_NewState: REQUEST_ADAPTER']

    eventDict['EEA Adapter Re-Connected After Stapling In Progress'] = [
        '---- ADAPTER: ENTERING EEA FETCH RECOVERY ITEMS STATE ----',
        '****  ENTERING EEA INITIALIZE STATE  ****',
        'SG TARE:  RECOVER',
        '****  ENTERING OP HIGHSPEED FIRE RECOVERY SUPER STATE  ****',
        '****  ENTERING OP HSFR IDLE STATE  ****',
        'GUI_NewState: EEA_REC_HSFIRE_ENTRY_1',
        'GUI_NewState: EEA_REC_HSFIRE_ENTRY_2'
        ]

    eventDict['Rotation During SP IP'] = ['CW Right Rotate Key Pressed',
                                            'CW Right Rotate Key Released',
                                           'GUI_NewState: EEA_REC_HSFIRE_ENTRY_2',
                                           'GUI_NewState: EEA_REC_HSFIRE_ENTRY_1']

    eventDict['Articulation During SP IP'] = [
                                           'Left Articulation Pressed',
                                           'Left Articulation Released',
                                           'GUI_NewState: EEA_REC_HSFIRE_ENTRY_2',
                                           'GUI_NewState: EEA_REC_HSFIRE_ENTRY_1']

    eventDict['Close Operation During SP IP'] = [
                               'Close Key Pressed',
                               'Close Key Released',
                               'GUI_NewState: EEA_REC_HSFIRE_ENTRY_2',
                               'GUI_NewState: EEA_REC_HSFIRE_ENTRY_1']

    eventDict['Rotation Operation During SP IP'] = ['CW Right Rotate Key Pressed',
                                                    'CCW Right Rotate Key Pressed',
                                                    'CCW Left Rotate Key Pressed',
                                                    'CW Left Rotate Key Pressed',
                                                    'GUI_NewState: EEA_REC_HSFIRE_ENTRY_2',
                                                    'GUI_NewState: EEA_REC_HSFIRE_ENTRY_1'
                                                    ]

    eventDict['No Staples Detected State Exit'] = ['LED_Off',
                                                   'GUI_NewState: EEA_REC_HSFIRE_ENTRY_1',
                                                   '****  ENTERING OP SSE WRecID SURGSITE EXTRACT STATE ****',
                                                   'Piezo: Caution Tone',
                                                   'GUI_NewState: EEA_REMOVE_RELOAD',
                                                   'GUI_NewState: EEA_FULL_OPEN_PROMPT'
                                                   ]

    eventDict['EEA Remove Reload Enter SSE'] = ['1Wire Device Reload removed!',
                                                'GUI_NewState: EEA_SSE_ROTATE_PROMPT']

    eventDict['SSE Exit'] = ['****  ENTERING OP SSE Calibrate Idle STATE  ****',
                             '****  ENTERING OP SSE WRecID INIT STATE ****',
                             'Piezo: Ready Tone']

    # pprint(eventDict, indent=5)
    return eventDict


# takes the event name, and returns Strings to Compare, with Length and Color as optional arguments - to be used
#   during SULU, MULU and Cartridge Connected
def locateStringsToCompareFromEvent(eventName, Length=None, Color=None):
    # print("locate strings ",eventName)

    # frame the event dictionary, for all the events
    eventDict = frameEventDict(Length, Color)

    # return the Strings to Compare
    return eventDict.get(eventName)


if __name__ == "__main__":
    print(locateStringsToCompareFromEvent('Remove Signia Power Handle from Charger'))
