# author - Deekonda Santosh &  Varun Pandey
# Ver # 1, dated - Dec 22, 2021
# Purpose - To have a common repository of relay data, which can be accessed across the code
TURN_ONN_INDIVIDUAL_RELAYS_IN_EACH_BANK = [
    # [Start Byte] [Address Byte] [Command Byte] [Data Bytes...] [Checksum Byte]
    [[170, 3, 254, 108, 1, 24],  # Turn On Relay 1 in Bank 1
     [170, 3, 254, 109, 1, 25],  # Turn On Relay 2 in Bank 1
     [170, 3, 254, 110, 1, 26],  # Turn On Relay 3 in Bank 1
     [170, 3, 254, 111, 1, 27],  # Turn On Relay 4 in Bank 1
     [170, 3, 254, 112, 1, 28],  # Turn On Relay 5 in Bank 1
     [170, 3, 254, 113, 1, 29],  # Turn On Relay 6 in Bank 1
     [170, 3, 254, 114, 1, 30],  # Turn On Relay 7 in Bank 1
     [170, 3, 254, 115, 1, 31],  # Turn On Relay 8 in Bank 1
     ],
    [[170, 3, 254, 108, 2, 25],  # Turn On Relay 1 in Bank 2
     [170, 3, 254, 109, 2, 26],  # Turn On Relay 2 in Bank 2
     [170, 3, 254, 110, 2, 27],  # Turn On Relay 3 in Bank 2
     [170, 3, 254, 111, 2, 28],  # Turn On Relay 4 in Bank 2
     [170, 3, 254, 112, 2, 29],  # Turn On Relay 5 in Bank 2
     [170, 3, 254, 113, 2, 30],  # Turn On Relay 6 in Bank 2
     [170, 3, 254, 114, 2, 31],  # Turn On Relay 7 in Bank 2
     [170, 3, 254, 115, 2, 32],  # Turn On Relay 8 in Bank 2
     ],
    [[170, 3, 254, 108, 3, 26],  # Turn On Relay 1 in Bank 3
     [170, 3, 254, 109, 3, 27],  # Turn On Relay 2 in Bank 3
     [170, 3, 254, 110, 3, 28],  # Turn On Relay 3 in Bank 3
     [170, 3, 254, 111, 3, 29],  # Turn On Relay 4 in Bank 3
     [170, 3, 254, 112, 3, 30],  # Turn On Relay 5 in Bank 3
     [170, 3, 254, 113, 3, 31],  # Turn On Relay 6 in Bank 3
     [170, 3, 254, 114, 3, 32],  # Turn On Relay 7 in Bank 3
     [170, 3, 254, 115, 3, 33],  # Turn On Relay 8 in Bank 3
     ],
    [[170, 3, 254, 108, 4, 27],  # Turn On Relay 1 in Bank 4
     [170, 3, 254, 109, 4, 28],  # Turn On Relay 2 in Bank 4
     [170, 3, 254, 110, 4, 29],  # Turn On Relay 3 in Bank 4
     [170, 3, 254, 111, 4, 30],  # Turn On Relay 4 in Bank 4
     [170, 3, 254, 112, 4, 31],  # Turn On Relay 5 in Bank 4
     [170, 3, 254, 113, 4, 32],  # Turn On Relay 6 in Bank 4
     [170, 3, 254, 114, 4, 33],  # Turn On Relay 7 in Bank 4
     [170, 3, 254, 115, 4, 34],  # Turn On Relay 8 in Bank 4
     ],
    [[170, 3, 254, 108, 5, 28],  # Turn On Relay 1 in Bank 5
     [170, 3, 254, 109, 5, 29],  # Turn On Relay 2 in Bank 5
     [170, 3, 254, 110, 5, 30],  # Turn On Relay 3 in Bank 5
     [170, 3, 254, 111, 5, 31],  # Turn On Relay 4 in Bank 5
     [170, 3, 254, 112, 5, 32],  # Turn On Relay 5 in Bank 5
     [170, 3, 254, 113, 5, 33],  # Turn On Relay 6 in Bank 5
     [170, 3, 254, 114, 5, 34],  # Turn On Relay 7 in Bank 5
     [170, 3, 254, 115, 5, 35],  # Turn On Relay 8 in Bank 5
     ],
    [[170, 3, 254, 108, 6, 29],  # Turn On Relay 1 in Bank 6
     [170, 3, 254, 109, 6, 30],  # Turn On Relay 2 in Bank 6
     [170, 3, 254, 110, 6, 31],  # Turn On Relay 3 in Bank 6
     [170, 3, 254, 111, 6, 32],  # Turn On Relay 4 in Bank 6
     [170, 3, 254, 112, 6, 33],  # Turn On Relay 5 in Bank 6
     [170, 3, 254, 113, 6, 34],  # Turn On Relay 6 in Bank 6
     [170, 3, 254, 114, 6, 35],  # Turn On Relay 7 in Bank 6
     [170, 3, 254, 115, 6, 36],  # Turn On Relay 8 in Bank 6
     ]]

TURN_OFF_INDIVIDUAL_RELAYS_IN_EACH_BANK = [
    [[170, 3, 254, 100, 1, 16],  # Turn Off Relay 1 in Bank 1
     [170, 3, 254, 101, 1, 17],  # Turn Off Relay 2 in Bank 1
     [170, 3, 254, 102, 1, 18],  # Turn Off Relay 3 in Bank 1
     [170, 3, 254, 103, 1, 19],  # Turn Off Relay 4 in Bank 1
     [170, 3, 254, 104, 1, 20],  # Turn Off Relay 5 in Bank 1
     [170, 3, 254, 105, 1, 21],  # Turn Off Relay 6 in Bank 1
     [170, 3, 254, 106, 1, 22],  # Turn Off Relay 7 in Bank 1
     [170, 3, 254, 107, 1, 23],  # Turn Off Relay 8 in Bank 1
     ],
    [[170, 3, 254, 100, 2, 17],  # Turn Off Relay 1 in Bank 2
     [170, 3, 254, 101, 2, 18],  # Turn Off Relay 2 in Bank 2
     [170, 3, 254, 102, 2, 19],  # Turn Off Relay 3 in Bank 2
     [170, 3, 254, 103, 2, 20],  # Turn Off Relay 4 in Bank 2
     [170, 3, 254, 104, 2, 21],  # Turn Off Relay 5 in Bank 2
     [170, 3, 254, 105, 2, 22],  # Turn Off Relay 6 in Bank 2
     [170, 3, 254, 106, 2, 23],  # Turn Off Relay 7 in Bank 2
     [170, 3, 254, 107, 2, 24],  # Turn Off Relay 8 in Bank 2
     ],
    [[170, 3, 254, 100, 3, 18],  # Turn Off Relay 1 in Bank 3
     [170, 3, 254, 101, 3, 19],  # Turn Off Relay 2 in Bank 3
     [170, 3, 254, 102, 3, 20],  # Turn Off Relay 3 in Bank 3
     [170, 3, 254, 103, 3, 21],  # Turn Off Relay 4 in Bank 3
     [170, 3, 254, 104, 3, 22],  # Turn Off Relay 5 in Bank 3
     [170, 3, 254, 105, 3, 23],  # Turn Off Relay 6 in Bank 3
     [170, 3, 254, 106, 3, 24],  # Turn Off Relay 7 in Bank 3
     [170, 3, 254, 107, 3, 25],  # Turn Off Relay 8 in Bank 3
     ],
    [[170, 3, 254, 100, 4, 19],  # Turn Off Relay 1 in Bank 4
     [170, 3, 254, 101, 4, 20],  # Turn Off Relay 2 in Bank 4
     [170, 3, 254, 102, 4, 21],  # Turn Off Relay 3 in Bank 4
     [170, 3, 254, 103, 4, 22],  # Turn Off Relay 4 in Bank 4
     [170, 3, 254, 104, 4, 23],  # Turn Off Relay 5 in Bank 4
     [170, 3, 254, 105, 4, 24],  # Turn Off Relay 6 in Bank 4
     [170, 3, 254, 106, 4, 25],  # Turn Off Relay 7 in Bank 4
     [170, 3, 254, 107, 4, 26],  # Turn Off Relay 8 in Bank 4
     ],
    [[170, 3, 254, 100, 5, 20],  # Turn Off Relay 1 in Bank 5
     [170, 3, 254, 101, 5, 21],  # Turn Off Relay 2 in Bank 5
     [170, 3, 254, 102, 5, 22],  # Turn Off Relay 3 in Bank 5
     [170, 3, 254, 103, 5, 23],  # Turn Off Relay 4 in Bank 5
     [170, 3, 254, 104, 5, 24],  # Turn Off Relay 5 in Bank 5
     [170, 3, 254, 105, 5, 25],  # Turn Off Relay 6 in Bank 5
     [170, 3, 254, 106, 5, 26],  # Turn Off Relay 7 in Bank 5
     [170, 3, 254, 107, 5, 27],  # Turn Off Relay 8 in Bank 5
     ],
    [[170, 3, 254, 100, 6, 21],  # Turn Off Relay 1 in Bank 6
     [170, 3, 254, 101, 6, 22],  # Turn Off Relay 2 in Bank 6
     [170, 3, 254, 102, 6, 23],  # Turn Off Relay 3 in Bank 6
     [170, 3, 254, 103, 6, 24],  # Turn Off Relay 4 in Bank 6
     [170, 3, 254, 104, 6, 25],  # Turn Off Relay 5 in Bank 6
     [170, 3, 254, 105, 6, 26],  # Turn Off Relay 6 in Bank 6
     [170, 3, 254, 106, 6, 27],  # Turn Off Relay 7 in Bank 6
     [170, 3, 254, 107, 6, 28],  # Turn Off Relay 8 in Bank 6
     ]]
TURN_ONN_INDIVIDUAL_RELAY_IN_ALL_BANKS = [
    [170, 3, 254, 108, 0, 23],  # Turn On Relay 1 in All Relay Banks
    [170, 3, 254, 109, 0, 24],  # Turn On Relay 2 in All Relay Banks
    [170, 3, 254, 110, 0, 25],  # Turn On Relay 3 in All Relay Banks
    [170, 3, 254, 111, 0, 26],  # Turn On Relay 4 in All Relay Banks
    [170, 3, 254, 112, 0, 27],  # Turn On Relay 5 in All Relay Banks
    [170, 3, 254, 113, 0, 28],  # Turn On Relay 6 in All Relay Banks
    [170, 3, 254, 114, 0, 29],  # Turn On Relay 7 in All Relay Banks
    [170, 3, 254, 115, 0, 30],  # Turn On Relay 8 in All Relay Banks
]

TURN_OFF_INDIVIDUAL_RELAYS_IN_ALL_BANKS = [
    [170, 3, 254, 100, 0, 15],  # Turn Off Relay 1 in All Relay Banks
    [170, 3, 254, 101, 0, 16],  # Turn Off Relay 2 in All Relay Banks
    [170, 3, 254, 102, 0, 17],  # Turn Off Relay 3 in All Relay Banks
    [170, 3, 254, 103, 0, 18],  # Turn Off Relay 4 in All Relay Banks
    [170, 3, 254, 104, 0, 19],  # Turn Off Relay 5 in All Relay Banks
    [170, 3, 254, 105, 0, 20],  # Turn Off Relay 6 in All Relay Banks
    [170, 3, 254, 106, 0, 21],  # Turn Off Relay 7 in All Relay Banks
    [170, 3, 254, 107, 0, 22],  # Turn Off Relay 8 in All Relay Banks
]

TURN_ONN_ALL_RELAYS_IN_EACH_BANK = [
    [170, 3, 254, 130, 1, 46],  # Turn On All Relays in Bank 1
    [170, 3, 254, 130, 2, 47],  # Turn On All Relays in Bank 2
    [170, 3, 254, 130, 3, 48],  # Turn On All Relays in Bank 3
    [170, 3, 254, 130, 4, 49],  # Turn On All Relays in Bank 4
]

TURN_OFF_ALL_RELAYS_IN_EACH_BANK = [
    [170, 3, 254, 129, 1, 45],  # Turn Off All Relays in Bank 1
    [170, 3, 254, 129, 2, 46],  # Turn Off All Relays in Bank 2
    [170, 3, 254, 129, 3, 47],  # Turn Off All Relays in Bank 3
    [170, 3, 254, 129, 4, 48],  # Turn Off All Relays in Bank 4
    [170, 3, 254, 129, 5, 49],  # Turn Off All Relays in Bank 3
    [170, 3, 254, 129, 6, 50],  # Turn Off All Relays in Bank 4
]

TURN_ONN_ALL_RELAYS_IN_ALL_BANKS = [
    [170, 3, 254, 130, 0, 45],  # Turn All Banks All Relays On
]

TURN_OFF_ALL_RELAYS_IN_ALL_BANKS = [[170, 3, 254, 129, 0, 44]]  # Turn All Banks All Relays Off


READ_INDIVIDUAL_RELAY_STATUS_IN_EACH_BANK = [
    [[170, 3, 254, 116, 1, 32],  # Read the On/Off Status of Relay 1 in Bank 1
     [170, 3, 254, 117, 1, 33],  # Read the On/Off Status of Relay 2 in Bank 1
     [170, 3, 254, 118, 1, 34],  # Read the On/Off Status of Relay 3 in Bank 1
     [170, 3, 254, 119, 1, 35],  # Read the On/Off Status of Relay 4 in Bank 1
     [170, 3, 254, 120, 1, 36],  # Read the On/Off Status of Relay 5 in Bank 1
     [170, 3, 254, 121, 1, 37],  # Read the On/Off Status of Relay 6 in Bank 1
     [170, 3, 254, 122, 1, 38],  # Read the On/Off Status of Relay 7 in Bank 1
     [170, 3, 254, 123, 1, 39],  # Read the On/Off Status of Relay 8 in Bank 1
     ],
    [[170, 3, 254, 116, 2, 33],  # Read the On/Off Status of Relay 1 in Bank 2
     [170, 3, 254, 117, 2, 34],  # Read the On/Off Status of Relay 2 in Bank 2
     [170, 3, 254, 118, 2, 35],  # Read the On/Off Status of Relay 3 in Bank 2
     [170, 3, 254, 119, 2, 36],  # Read the On/Off Status of Relay 4 in Bank 2
     [170, 3, 254, 120, 2, 37],  # Read the On/Off Status of Relay 5 in Bank 2
     [170, 3, 254, 121, 2, 38],  # Read the On/Off Status of Relay 6 in Bank 2
     [170, 3, 254, 122, 2, 39],  # Read the On/Off Status of Relay 7 in Bank 2
     [170, 3, 254, 123, 2, 40],  # Read the On/Off Status of Relay 8 in Bank 2
     ],
    [[170, 3, 254, 116, 3, 34],  # Read the On/Off Status of Relay 1 in Bank 3
     [170, 3, 254, 117, 3, 35],  # Read the On/Off Status of Relay 2 in Bank 3
     [170, 3, 254, 118, 3, 36],  # Read the On/Off Status of Relay 3 in Bank 3
     [170, 3, 254, 119, 3, 37],  # Read the On/Off Status of Relay 4 in Bank 3
     [170, 3, 254, 120, 3, 38],  # Read the On/Off Status of Relay 5 in Bank 3
     [170, 3, 254, 121, 3, 39],  # Read the On/Off Status of Relay 6 in Bank 3
     [170, 3, 254, 122, 3, 40],  # Read the On/Off Status of Relay 7 in Bank 3
     [170, 3, 254, 123, 3, 41],  # Read the On/Off Status of Relay 8 in Bank 3
     ],

    [[170, 3, 254, 116, 4, 35],  # Read the On/Off Status of Relay 1 in Bank 4
     [170, 3, 254, 117, 4, 36],  # Read the On/Off Status of Relay 2 in Bank 4
     [170, 3, 254, 118, 4, 37],  # Read the On/Off Status of Relay 3 in Bank 4
     [170, 3, 254, 119, 4, 38],  # Read the On/Off Status of Relay 4 in Bank 4
     [170, 3, 254, 120, 4, 39],  # Read the On/Off Status of Relay 5 in Bank 4
     [170, 3, 254, 121, 4, 40],  # Read the On/Off Status of Relay 6 in Bank 4
     [170, 3, 254, 122, 4, 41],  # Read the On/Off Status of Relay 7 in Bank 4
     [170, 3, 254, 123, 4, 42],  # Read the On/Off Status of Relay 8 in Bank 4
     ],

    [[170, 3, 254, 116, 5, 36],  # Read the On/Off Status of Relay 1 in Bank 5
     [170, 3, 254, 117, 5, 37],  # Read the On/Off Status of Relay 2 in Bank 5
     [170, 3, 254, 118, 5, 38],  # Read the On/Off Status of Relay 3 in Bank 5
     [170, 3, 254, 119, 5, 39],  # Read the On/Off Status of Relay 4 in Bank 5
     [170, 3, 254, 120, 5, 40],  # Read the On/Off Status of Relay 5 in Bank 5
     [170, 3, 254, 121, 5, 41],  # Read the On/Off Status of Relay 6 in Bank 5
     [170, 3, 254, 122, 5, 42],  # Read the On/Off Status of Relay 7 in Bank 5
     [170, 3, 254, 123, 5, 43],  # Read the On/Off Status of Relay 8 in Bank 5
     ],

    [[170, 3, 254, 116, 6, 37],  # Read the On/Off Status of Relay 1 in Bank 6
     [170, 3, 254, 117, 6, 38],  # Read the On/Off Status of Relay 2 in Bank 6
     [170, 3, 254, 118, 6, 39],  # Read the On/Off Status of Relay 3 in Bank 6
     [170, 3, 254, 119, 6, 40],  # Read the On/Off Status of Relay 4 in Bank 6
     [170, 3, 254, 120, 6, 41],  # Read the On/Off Status of Relay 5 in Bank 6
     [170, 3, 254, 121, 6, 42],  # Read the On/Off Status of Relay 6 in Bank 6
     [170, 3, 254, 122, 6, 43],  # Read the On/Off Status of Relay 7 in Bank 6
     [170, 3, 254, 123, 6, 44],  # Read the On/Off Status of Relay 8 in Bank 6
     ],
]

READ_ALL_RELAY_STATUS_IN_EACH_BANK = [
    [170, 3, 254, 124, 1, 40],  # Read the On/Off Status of All Relays in Bank 1
    [170, 3, 254, 124, 2, 41],  # Read the On/Off Status of All Relays in Bank 2
    [170, 3, 254, 124, 3, 42],  # Read the On/Off Status of All Relays in Bank 3
    [170, 3, 254, 124, 4, 43],  # Read the On/Off Status of All Relays in Bank 4
    [170, 3, 254, 124, 5, 44],  # Read the On/Off Status of All Relays in Bank 5
    [170, 3, 254, 124, 6, 45],  # Read the On/Off Status of All Relays in Bank 6
]
