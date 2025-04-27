# Compare function have been refactored by Varun Pandey on Jan 4, 2022

# New function added to compare as XCompare by Manoj Vadali on 3rd Jan 2024. xCompare compares from the list of strings to compare if atleast one string is present in the strings obtained from power pack it results a failure.
# This fucntion is used to ensure when an action should not result a particular log string that string is not present in the captured strings from the power pack

# Purpose - to compare a set of strings with the strings received from PowerPack, and in case of any mismatch return
#   FAIL, else return PASS
import simple_colors


def Compare(Action, Strings_to_Compare, Strings_from_PowerPack):
    test_result = 'PASS'
    for singleElement in Strings_to_Compare:
        if singleElement.strip() in Strings_from_PowerPack:
            continue
        else:
            print(simple_colors.red(f'Fail: Missing String: {singleElement}'))
            # print(f'Fail: Missing String: {singleElement}')

            if test_result != 'FAIL':
                # print('Failed Test Step:', Action)
                test_result = 'FAIL'
    if test_result == "PASS":
        print('Test Step Pass:', Action)
    return test_result


def xCompare(Action, Strings_to_Compare, Strings_from_PowerPack):
    test_result = 'PASS'
    for singleElement in Strings_to_Compare:
        if singleElement.strip() in Strings_from_PowerPack:
            test_result = 'FAIL'
            print(singleElement)
            break
            # continue

    if test_result == 'FAIL':
        print('Failed Test Step:', Action)
        test_result = 'FAIL'
    if test_result == "PASS":
        print('Test Step Pass:', Action)
    return test_result


def compute_results(element:dict, xls_results:list, time_stamps:list, Strings_from_PowerPack:list) -> list:
    # header = ['Step #', 'Action String', 'Action PASS/FAIL', 'Actions', 'Requirement Ref #',
    # 'Expected Results', 'Actual Results (Event Strings)', 'PASS/FAIL']

    event_log_1 = str(element.get('event_log_1'))
    event_log_2 = str(element.get('event_log_2'))
    min_time_diff = element.get('min_time_diff')
    max_time_diff = element.get('max_time_diff')
    requirement_id = str(element.get('requirement_id'))
    action_string = str(element.get('action_string'))
    expected_result = str(element.get('expected_result'))
    # if already these event logs are checked and captured in the results, get the corresponding timestamps from there

    timestamp_1:int = 0
    timestamp_2:int = 0

    found_event_strings = xls_results[-2]  # Actual Results (Event Strings)
    for ele_in_event_strings in found_event_strings:
        ele_in_event_strings = str(ele_in_event_strings)
        # print(simple_colors.red(ele_in_event_strings.split(':')[0].strip()))
        if ele_in_event_strings.find(event_log_1) != -1 and len(ele_in_event_strings.split(':')) == 2:
            timestamp_1 = int(ele_in_event_strings.split(':')[0].strip())
        elif ele_in_event_strings.find(event_log_2) != -1 and len(ele_in_event_strings.split(':')) == 2:
            timestamp_2 = int(ele_in_event_strings.split(':')[0].strip())

    if timestamp_1 == 0 or timestamp_2 == 0:
        print(f"any of \nevent_log_1: {event_log_1}\nevent_log_2: {event_log_2}\n is/are not already verified")

        # check the event_log_1 and event_log_2 in the event logs captured from the MCP
        for event_log in Strings_from_PowerPack:
            event_log = str(event_log)
            if event_log.find(event_log_1) != -1:
                index_1 = Strings_from_PowerPack.index(event_log)
                timestamp_1 = int(time_stamps[index_1])
            elif event_log.find(event_log_2) != -1:
                index_2 = Strings_from_PowerPack.index(event_log)
                timestamp_2 = int(time_stamps[index_2])

    if timestamp_1 == 0 or timestamp_2 == 0:
        print(f"event_log_1: {event_log_1}\nevent_log_2: {event_log_2}\n are not found in the MCP logs as well")
    else:
        actions = xls_results[3]
        requirement_ids = xls_results[4]
        expected_results = xls_results[5]
        actual_results = xls_results[6]
        step_results = xls_results[-1]
        # finding the absolute difference between the two events
        # since the timestamps are available in milli Sec, converting them into Sec
        absolute_difference = abs(timestamp_1 - timestamp_2) / 1000
        actual_result = (f'{timestamp_1}: {event_log_1}\n{timestamp_2}: {event_log_2}'
                         f'\nTime Difference: {absolute_difference}')
        verification_result = 'FAIL'
        if max_time_diff >= absolute_difference >= min_time_diff:
            verification_result = 'PASS'
        actions.append(action_string)
        requirement_ids.append(requirement_id)
        expected_results.append(expected_result)
        actual_results.append(actual_result)
        step_results.append(verification_result)

        # adding all the results back to the xls_results list
        xls_results[3] = actions
        xls_results[4] = requirement_ids
        xls_results[5] = expected_results
        xls_results[6] = actual_results
        xls_results[-1] = step_results

    return xls_results


def calculate_time_difference(time_diff_verification:dict, xls_results:list, time_stamps:list,
                              Strings_from_PowerPack:list) -> list:
    if time_diff_verification is not None:
        for key, value in time_diff_verification.items():
            if key == 'time_difference':
                if value is not None:
                    for element in value:
                        xls_results = compute_results(element, xls_results, time_stamps, Strings_from_PowerPack)

    return xls_results


def compare_with_test_status(Action_String, Strings_to_Compare:list, Strings_from_PowerPack:list, event_status,
                             is_event_connecting, time_stamps:list, test_status_flag=True, action:str=None, fix_vali_required=False):
                             #step_num=None):

    test_result = 'PASS'
    action_strings = []
    expected_results = []
    actual_results = []
    actual_results_status = []
    requirement_ref = []

    requirements_num_to_print = None
    time_diff_verification = None

    if fix_vali_required:
        pass
    else:
        print(simple_colors.yellow(f"Strings_to_Compare : {Strings_to_Compare}"))

    if (type(Strings_to_Compare) is list) and (type(Strings_to_Compare[0]) is list):
        log_strings_to_verify = Strings_to_Compare[0]
        action_strings = Strings_to_Compare[1]
        expected_results = Strings_to_Compare[1]
        # if len(Strings_to_Compare) == 2:
        #     requirements_num_to_print = None
        if len(Strings_to_Compare) == 3:
            expected_results = Strings_to_Compare[2]
        elif len(Strings_to_Compare) >= 4:
            requirements_num_to_print = Strings_to_Compare[3]
            expected_results = Strings_to_Compare[2]
            if len(Strings_to_Compare) == 5:
                time_diff_verification = Strings_to_Compare[4]

    else:
        log_strings_to_verify = Strings_to_Compare
        action_strings = Strings_to_Compare
        expected_results = Strings_to_Compare
    index = 0
    for string in log_strings_to_verify:
        is_event_log_present = False
        event_index = -1
        if requirements_num_to_print is None:
            requirement_ref.append('')
        else:
            requirement_ref.append(f"{requirements_num_to_print[index]}")
        for event_log in Strings_from_PowerPack:
            if string.strip() in Strings_to_Compare:
                is_event_log_present = True
                event_index = Strings_from_PowerPack.index(event_log)
                break
            elif str(event_log).find(string.strip()) != -1:
                is_event_log_present = True
                event_index = Strings_from_PowerPack.index(event_log)
                break
        if is_event_log_present:
            # if the test_status_flag is false, any element in the Strings_from_PowerPack matches with any element in
            # Strings_to_Compare list, make the test_result 'FAIL'
            if not test_status_flag:
                print(simple_colors.red(f'Fail: String Present: {string}'))
                test_result = 'FAIL'
            else:
                # event_index = Strings_from_PowerPack.index(string.strip())
                actual_results.append(f"{time_stamps[event_index]}: {Strings_from_PowerPack[event_index]}")
                # action_strings.append()
                # expected_results.append(f"{action_strings_to_print[index]}")
                # if requirements_num_to_print is None:
                #     requirement_ref.append('')
                # else:
                #     requirement_ref.append(f"{requirements_num_to_print[index]}")
                actual_results_status.append("PASS")
                # removing the found out strings and corresponding time stamps to have un necessary
                Strings_from_PowerPack.pop(event_index)
                time_stamps.pop(event_index)
        elif (Action_String.find('Firing') != -1) and string.strip() in ['LED_On', 'LED_Off']:
            actual_results.append(f"Since {string.strip()} is not present in the logs. Green LED is still blinking")
            actual_results_status.append("PASS")
            # requirement_ref.append(f"{requirements_num_to_print[index]}")

        else:
            # if the test_status_flag is true, any element in the Strings_from_PowerPack does not match with any
            # element in Strings_to_Compare list, make the test_result 'FAIL'
            if test_status_flag:
                print(simple_colors.red(f'Fail: Missing String: {string}'))
                test_result = 'FAIL'

                actual_results.append(f"{string.strip()}")
                # expected_results.append(f"{action_strings_to_print[index]}")
                # if requirements_num_to_print is None:
                #     requirement_ref.append('')
                # else:
                #     requirement_ref.append(f"{requirements_num_to_print[index]}")
                actual_results_status.append("FAIL")

        index += 1

    # If event_status is not None, it is a status variable. If the event_status is true or 1, the action has been
    # performed successfully and regardless of the event_logs strings, we pass the action. Also logging the missed
    # event strings.

    if test_status_flag:
        # if both event_status and is_event_connecting are true, then it is for connecting the event.
        # if both event_status and is_event_connecting are false, then it is for disconnecting the event.
        if event_status is not None:
            if (event_status and is_event_connecting) or not (event_status or is_event_connecting):
                test_result = 'PASS'
            else:
                test_result = 'FAIL'

        result_string = Action_String + ": " + test_result
    else:
        result_string = "X_" + Action_String + " : " + test_result

    if test_result == 'FAIL':
        if fix_vali_required:
            pass
        else:
            print(simple_colors.red(f'Failed Test Step: {Action_String}'))
    if test_result == "PASS":
        if fix_vali_required:
            pass
        else:
            print(simple_colors.green(f'Test Step Pass: {Action_String}'))

    Action_String = action if action is not None else Action_String
    # header = ['Step #', 'Action String', 'Action PASS/FAIL', 'Actions', 'Requirement Ref #',
    # 'Expected Results', 'Actual Results (Event Strings)', 'PASS/FAIL']
    xls_results = [Action_String, test_result, action_strings, requirement_ref, expected_results,
                           actual_results, actual_results_status]
    if time_diff_verification is not None:
        xls_results = calculate_time_difference(time_diff_verification, xls_results, time_stamps, Strings_from_PowerPack)

    if fix_vali_required:
        pass
    else:
        print(simple_colors.magenta(f'xls_results: {xls_results}'))

    return result_string, xls_results
