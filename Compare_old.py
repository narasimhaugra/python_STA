# Compare function have been refactored by Varun Pandey on Jan 4, 2022

# Purpose - to compare a set of strings with the strings received from PowerPack, and in case of any mismatch return
#   FAIL, else return PASS
def Compare(Action, Strings_to_Compare, Strings_from_PowerPack):
    test_result = 'PASS'
    for singleElement in Strings_to_Compare:
        if singleElement.strip() in Strings_from_PowerPack:
            continue
        else:
            print('Fail: Missing String:', singleElement)

            if test_result != 'FAIL':
                # print('Failed Test Step:', Action)
                test_result = 'FAIL'
    if test_result == "PASS":
        print('Test Step Pass:', Action)
    return test_result
