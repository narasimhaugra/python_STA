# @Author - Thirupathi Mekala, dated - Jan 22, 2024
#
# Purpose - To have a unified list of dictionary data for Smoke Test Events data which comprises
# as Key   : The Event Name
# as Value : List of Strings to Compare

# from pprint import pprint

# Purpose : Create the Event dictionary
def frameEventDict(Length=None, Color=None):
    # this dict has to be updated every time in case we find a new event which isn't present under this
    eventDict = {}
    eventDict['Remove Signia Power Handle from Charger'] = ['GUI_NewState: WELCOME_SCREEN',
                                                            'Piezo: All Good',
                                                            'Initialization complete',
                                                            'SM_NewSystemEventAlert: INIT_COMPLETE',
                                                            'systemCheckCompleted complete',
                                                            'GUI_NewState: PROCEDURES_REMAINING',
                                                            'GUI_NewState: REQUEST_CLAMSHELL',
                                                            'Going to standby',
                                                            'Turning off OLED'
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

    # Adapter Connected
    eventDict['Adapter Connected'] = ['  1Wire Device Adapter authenticated and identified',
                                      ' GUI_NewState: ADAPTER_DETECTED',
                                      ' GUI_NewState: EGIA_ADAPTER_CALIBRATING',
                                      ' SM_NewSystemEventAlert: ADAPTER_FULLY_CALIBRATED',
                                      ' Piezo: All Good',
                                      ' GUI_NewState: EGIA_REQUEST_RELOAD'
                                      ]






    eventDict['EEA Clamping on Tissue'] = ['P_SIG_CLAMPING in GUI_MANAGER_EEA',
                                           '****  ENTERING OP CHS IDLE STATE  ****',
                                           '****  ENTERING OP CLAMP HIGHSPEED SUPER STATE  ****',
                                           '****  ENTERING OP LOWSPEED CLAMP SUPER STATE  ****',
                                           '****  ENTERING OP CLAMP CTC SUPER STATE  ****',
                                            'GUI_NewState: EEA_CTC_CLAMP_0',
                                           'GUI_NewState: EEA_CTC_CLAMP_50',
                                           'GUI_NewState: EEA_CTC_CLAMP_75',
                                           'CTC Percent = 100',
                                            '****  ENTERING OP CTC Idle STATE  ****',
                                            'Piezo: Limit Reached',
                                            'Piezo: Fully Clamped',
                                           'Piezo: Ready Tone',
                                            '****  ENTERING TISSUE RELAXATION STATE  ****',
                                            'LED_On',
                                            'GUI_NewState: EEA_TISSUE_RELAX',
                                           '****  ENTERING OP CLAMP CTC SUPER STATE  ****'  ]

    eventDict['EEA Green Key Ack'] = ['SM_NewSystemEventAlert: GREEN_KEY_PRESS',
                                      'P_SIG_GREEN_KEY_PRESS: entering fire mode',
                                      'LED_Blink',
                                      'Piezo: Enter Fire Mode',
                                      'GUI_NewState: EEA_FIREMODE_1',
                                       'GUI_NewState: EEA_FIREMODE_2',
                                      'SM_NewSystemEventAlert: GREEN_KEY_PRESS']

    eventDict['EEA Firing'] = ['****  ENTERING OP FM WRldCfg STAPLES DETECTED STATE  ****',
                               '****  ENTERING HIGHSPEED FIRE STATE  ****',
                               '****  ENTERING LOWSPEED STAPLE SUPER STATE  ****',
                               '****  ENTERING OP LSS STAPLE DETECT STATE  ****',
                               '****  ENTERING OP LSS STAPLE FORMATION STATE  ****',
                               '****  ENTERING OP LSS WRecID STAPLE COMPLETE STATE  ****',
                               '****  ENTERING LOWSPEED CUT SUPER STATE  ****',
                               'Piezo: Complete Fire',
                               'GUI_NewState: EEA_CUT_100',
                               'GUI_NewState: EEA_TILT_PROMPT_1',
                               'GUI_NewState: EEA_TILT_PROMPT_2'
                               ]



    # Tilt Operation of Anvil
    eventDict['Tilt Operation of Anvil'] = ['GUI_NewState: EEA_TILT_PROMPT_1',
                                            'GUI_NewState: EEA_TILT_PROMPT_2',
                                            'GUI_NewState: EEA_TILT_STARTED',
                                            'GUI_NewState: EEA_TILT_MIDLOW',
                                            'GUI_NewState: EEA_TILT_MIDHIGH',
                                            '****  ENTERING OP T WRecID TILT COMPLETE STATE  ****',
                                            # '****  ENTERING OP T WRecID TILT COMPLETE STATE  ****
                                            'Piezo: Ready Tone',
                                            'GUI_NewState: EEA_TILT_COMPLETE',
                                            'GUI_NewState: EEA_TILT_OPEN_PROMPT_1',
                                            'GUI_NewState: EEA_TILT_OPEN_PROMPT_2',
                                            'LED_Off'
                                            ]


    # SSE
    eventDict['SSE'] = ['GUI_NewState: EEA_RELOAD_FULLY_OPEN',
                        'GUI_NewState: EEA_TILTOPEN_STARTED',
                        'GUI_NewState: EEA_TILTOPEN_COMPLETE',
                        'Tilt Open Complete - Going to Fire Retract',
                        '****  ENTERING FIRE RETRACT SUPER STATE  ****',
                        '****  ENTERING LOCKUP STATE  ****',
                        'Piezo: Complete Fire']



    eventDict['EEA Remove Reload'] = ['1Wire Device Reload removed!',
                                      'P_SIG_RELOAD_REMOVED']

    eventDict['Remove EEA Adapter'] = ['1Wire Device Adapter removed!',
                                       'GUI_AdapterDisconnected',
                                       'GUI_NewState: REQUEST_ADAPTER']






    eventDict['EEA RELOAD Connected with Ship cap'] = [' 1Wire Device Reload attached on 1WireBus Reload',
                                                           # f' Reload Values, Size {Length}, Reload Values, Color {Color}',# Manoj Vadali commented and need to update as the color and length also writes 1W code in EEA                                      ' Smart reload', ' SM_NewSystemEventAlert: RELOAD_INSTALLED',
                                                           '****  ENTERING OP SCR IDLE STATE  ****',
                                                           'Smart reload', ' GUI_NewState: EEA_SHIPCAP_REMOVAL',
                                                           ' GUI_NewState: EEA_SHIPCAP_READY',
                                                           ]

    eventDict['EEA RELOAD Connected without Ship cap'] = [' 1Wire Device Reload attached on 1WireBus Reload',
                                                              # f' Reload Values, Size {Length}, Reload Values, Color {Color}',#
                                                              'Smart reload',
                                                              ' SM_NewSystemEventAlert: RELOAD_INSTALLED',
                                                              '****  ENTERING FULL OPEN SUPER STATE  ****',
                                                              '****  ENTERING OP FO IDLE STATE  ****',
                                                              'GUI_NewState: EEA_FULL_OPEN_PROMPT'

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

    # Retracting
    eventDict['Retracting'] = [' ****  ENTERING AO EGIA Retract STATE  ****',
                               ' GUI_NewState: EGIA_RETRACT_COMPLETE',
                               ' LED_On'
                               ]

    # Adapter 1W OC Retracting (adapter OC before firing mode during retracting "'Latching short on 1Wire bus Reload" is not coming

    # Unclamping
    eventDict['Unclamping'] = [' ****  ENTERING AO EGIA Unclamp STATE  ****',
                               ' EGIA FireRod, FULLY OPEN',
                               ' ****  ENTERING AO EGIA Idle STATE  ****',
                               ' LED_Off']


    # 'Remove Reload'
    eventDict['Remove Reload'] = [' GUI_NewState: EGIA_REQUEST_RELOAD']

    # 'Remove Cartridge'
    eventDict['Remove Cartridge'] = ['1Wire Device Cartridge removed!']

    # 'Remove Reload Adapter 1W OC in Fire Mode'

    # Remove Adapter
    eventDict['Remove Adapter'] = ['1Wire Device Adapter removed!',
                                   '$$ WARNING:  ADAPTER REMOVED!!! $$',
                                   ' GUI_NewState: REQUEST_ADAPTER'
                                   ]


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

    eventDict['Error Screens - Obstruction On Trocar Close'] = ['Piezo: Caution Tone',
                                                              'GUI_NewState: EEA_ERR_OBS_FORCE_OPEN_1',
                                                              'GUI_NewState: EEA_ERR_OBS_FORCE_OPEN_2' ]

    eventDict['Error Screens - Obstruction On Trocar Open'] = ['GUI_NewState: EEA_ERR_OBS_FORCE_CLOSE_1',
                                                               'GUI_NewState: EEA_ERR_OBS_FORCE_CLOSE_2']

    eventDict['Low Speed Clamping zone'] = ['****  ENTERING OP LOWSPEED CLAMP SUPER STATE  ****',
                                            'GUI_NewState: EEA_CTC_THIN_TISSUE',
                                            '****  ENTERING OP CLAMP CTC SUPER STATE  ****',
                                            'Piezo: Caution Tone',
                                            'LED_On']

    eventDict['EEA Locked'] = ['GUI_NewState: EEA_LOCKED']
    eventDict['EEA Caution Tone'] = ['Piezo: Caution Tone']
    eventDict['EEA Trocar Position Screen'] = ['GUI_NewState: EEA_FULL_OPEN_PROMPT']

    eventDict['EEA Adapter Connected with EEA Reload'] = ['GUI_NewState: ADAPTER_DETECTED',
                                          'SM_NewSystemEventAlert: ADAPTER_FULLY_CALIBRATED',
                                          'Piezo: All Good',
                                          'Clamp Cal, StopStatus = 0x001']

    eventDict['Remove EEA Adapter Connected and Reattach'] = ['SM_NewSystemEventAlert: ADAPTER_FULLY_CALIBRATED',
                                                          'GUI_NewState: EEA_FULL_OPEN_PROMPT',
                                                          ]

    eventDict['Trocar Retracts Slightly in High Speed Clamping'] = ['Sent Signal:  P_SIG_UNCLAMPING',
                                                                    'Sent Signal:  P_SIG_CLAMPING',
                                                                    '****  ENTERING OP CLAMP HIGHSPEED SUPER STATE  ****'
                                                                    ]

    eventDict['Verify EEA Trocar Position Screen Shows After Calibrating'] = ['GUI_NewState: REQUEST_ADAPTER',
                                                                    'SM_NewSystemEventAlert: ADAPTER_FULLY_CALIBRATED',
                                                                    'GUI_NewState: EEA_FULL_OPEN_PROMPT']

    eventDict['Verify EEA CTC Clamping in Progress screen shows at 100% after Calibrating'] = ['GUI_NewState: REQUEST_ADAPTER',
                                                                              'GUI_NewState: EEA_CLAMP100_TISSUE_RELAX',
                                                                              'GUI_NewState: EEA_TISSUE_RELAX']

    eventDict['Remove the Adapter During Stapling'] = ['GUI_AdapterDisconnected',
                                                        'GUI_NewState: ADAPTER_DETECTED',
                                                        'GUI_NewState: EEA_REC_HSFIRE_ENTRY_1',
                                                       'GUI_NewState: EEA_REC_HSFIRE_ENTRY_2',
                                                       '****  ENTERING OP HSFR IDLE STATE  ****'
                                                       ]
    eventDict['Verify Stapling Completes then Remove Adapter During Cutting'] = ['GUI_AdapterDisconnected',
                                                       'GUI_NewState: ADAPTER_DETECTED',
                                                       'GUI_NewState: EEA_REC_CUT_ENTRY_1',
                                                       'GUI_NewState: EEA_REC_CUT_ENTRY_2'
                                                       ]
    eventDict['Verify Cutting Completes then Remove Adapter'] = ['GUI_AdapterDisconnected',
                                                                'GUI_NewState: REQUEST_ADAPTER',
                                                                 'GUI_AdapterDisconnected',
                                                                 'GUI_NewState: EEA_TILT_PROMPT_1',
                                                                 'GUI_NewState: EEA_TILT_PROMPT_2',
                                                                 'GUI_NewState: EEA_CAL_START',
                                                                 'GUI_NewState: EEA_REC_CUT_FIRE'
                                                        ]
    eventDict['Reattach Adapter and Verify EEA Tilt Prompt Screens'] = ['GUI_NewState: REQUEST_ADAPTER',
                                                                 'GUI_NewState: ADAPTER_DETECTED',
                                                                 'GUI_NewState: EEA_TILT_PROMPT_1',
                                                                 'GUI_NewState: EEA_TILT_PROMPT_2'
                                                                        ]

    eventDict['Reattach Adapter when TILT_POSITION is Reached'] = ['GUI_NewState: REQUEST_ADAPTER',
                                                                        'GUI_NewState: ADAPTER_DETECTED',
                                                                        'GUI_NewState: EEA_TILT_STARTED',
                                                                        'GUI_NewState: EEA_TILT_COMPLETE'
                                                                   ]

    eventDict['Reattach Adapter and Verify EEA TILT_OPEN Prompt Screen'] = ['GUI_NewState: REQUEST_ADAPTER',
                                                                   'GUI_NewState: ADAPTER_DETECTED',
                                                                   'GUI_NewState: EEA_TILT_OPEN_PROMPT_1',
                                                                   'GUI_NewState: EEA_TILT_OPEN_PROMPT_2'
                                                                            ]
    eventDict['Reattach Adapter and Verify EEA TILT_OPEN Complete Screen'] = ['GUI_NewState: REQUEST_ADAPTER',
                                                                            'GUI_NewState: ADAPTER_DETECTED',
                                                                            'GUI_NewState: EEA_TILTOPEN_COMPLETE',
                                                                            'Fire Retract Complete - Going to LockUp'
                                                                            ]

    eventDict['EEA SURGICAL_SITE_EXTRACTION'] = ['****  ENTERING SURGICAL SITE EXTRACTION SUPER STATE  ****',
                                                                            'Go to SSE Idle State'
                                                                            ]
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
    eventDict['EEA Surgical Site Exit Prompt Screens'] = ['GUI_NewState: EEA_SSE_ROTATE_PROMPT'   ]

    eventDict['EEA Surgical Site Countdown Screens'] = ['GUI_NewState: EEA_SSE_COUNT1',
                                                         'GUI_NewState: EEA_TPR_DETECTING',
                                                         'Clamp Cal, StopStatus = 0x001',
                                                         'Piezo: Ready Tone',
                                                         'GUI_NewState: EEA_REMOVE_ADAPTER']


    # pprint(eventDict, indent=5)
    return eventDict


# takes the event name, and returns Strings to Compare, with Length and Color as optional arguments - to be used
#   during SULU, MULU and Cartridge Connected
def locateStringsToCompareFromSmokeEvent(eventName, Length=None, Color=None):
    print(eventName)

    # frame the event dictionary, for all the events
    eventDict = frameEventDict(Length, Color)

    # return the Strings to Compare
    return eventDict.get(eventName)


if __name__ == "__main__":
    print(locateStringsToCompareFromSmokeEvent('Remove Signia Power Handle from Charger'))
