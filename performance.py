import subprocess
import argparse
from colorama import Fore, Style
import re
import math
from datetime import datetime


def perf(options, protocol, receive, port):
    # Run the hyperf3 command and capture the output
    attempts = 0
    while attempts < 4:
        attempts += 1
        if protocol == "udp":
            result = subprocess.run(
                [
                    "iperf3",
                    "-c",
                    options.address,
                    port,
                    "--cport",
                    "55720",
                    "-u",
                    "-b",
                    "50M",
                    receive,
                ],
                capture_output=True,
                text=True,
            )
        else:
            result = subprocess.run(
                ["iperf3", "-c", options.address, port, "--cport", "55720", receive],
                capture_output=True,
                text=True,
            )
        # Check if the command was executed successfully
        if result.returncode == 0:
            output = result.stdout
            list = str.splitlines(output)

            # Use regex to find the bitrates of the sender and receiver
            sender_bitrate = re.search(
                r"MBytes  ([+-]?(?=\.\d|\d)(?:\d+)?(?:\.?\d*))(?:[Ee]([+-]?\d+))? Mbits/sec",
                list[-3],
            )
            # DEBUG
            # print(output)
            # print(list[-3])

            if sender_bitrate:
                try:
                    return float(sender_bitrate.group(1))
                except (ValueError, AttributeError) as e:
                    print(Fore.RED + f"[-] Error parsing the bitrate: {e}")
        else:
            print(
                Fore.RED
                + f"[-] Error executing the iperf3 command. Error message: {result.stderr}"
            )
    print(Fore.RED + f"[-] All 4° attempts failed.")
    return None


def dump(options, protocol, receive, file):
    # Set vars

    try:
        dump = subprocess.Popen(
            [
                "sudo",
                "tcpdump",
                "-i",
                options.interface,
                "-w",
                options.filename + file,
                protocol,
            ],
            stdin=subprocess.PIPE,
        )
        dump.stdin.write(b"password\n")
        dump.stdin.flush()

        # Run iperf3 test
        port = ""
        if options.port != None:
            port = "-p " + str(options.port)

        result = []
        # extract relevant data
        for i in range(10):
            result.append(perf(options, protocol, receive, port))
            print(Fore.GREEN + f"[{i}] Sender Bitrate: {result[-1]}" + Style.RESET_ALL)

        Min = min(result)  # MIN
        Max = max(result)  # MAX
        mean_value = sum(result) / len(result)  # MEAN
        sum_squared_diff = sum((x - mean_value) ** 2 for x in result)
        std_dev_value = math.sqrt(sum_squared_diff / (len(result) - 1))
        return Min, Max, mean_value, std_dev_value

    except Exception as e:
        print(Fore.RED + f"[-] Error during Dumping: {e}" + Style.RESET_ALL)

    finally:
        dump.terminate()
        print(
            Fore.GREEN
            + f"[+] --> DUMP Made Correctly for the file : {options.filename}{file}"
            + Style.RESET_ALL
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", dest="filename", help="write report to FILE")
    parser.add_argument(
        "-i", "--interface", dest="interface", help="write the interface"
    )
    parser.add_argument("-a", "--address", dest="address", help="write the address")
    parser.add_argument("-p", "--port", dest="port", help="write the port number")

    options = parser.parse_args()
    
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    print(Fore.BLUE + f"[+] TCP test" + Style.RESET_ALL)
    Min_TCP, Max_TCP, avg_TCP, std_dev_TCP = dump(
        options, protocol="tcp", receive="", file="-TCP"
    )
    print(Fore.BLUE + f"[+] UDP test" + Style.RESET_ALL)
    Min_UDP, Max_UDP, avg_UDP, std_dev_UDP = dump(
        options, protocol="udp", receive="", file="-UDP"
    )
    print(Fore.BLUE + f"[+] TCP test with receive instead of sending" + Style.RESET_ALL)
    Min_TCP_R, Max_TCP_R, avg_TCP_R, std_dev_TCP_R = dump(
        options, protocol="tcp", receive="-R", file="-TCP-R"
    )
    print(Fore.BLUE + f"[+] UDP with receive instead of sending" + Style.RESET_ALL)
    Min_UDP_R, Max_UDP_R, avg_UDP_R, std_dev_UDP_R = dump(
        options, protocol="udp", receive="-R", file="-UDP-R"
    )

    print(Fore.BLUE + f"|----------- FINAL RESULT -----------|")
    print(Fore.BLUE + f"|       | Avg  | Min  | Max  | StdD  |")
    print(
        Fore.BLUE
        + f"|  TCP  | {avg_TCP:.1f} | {Min_TCP:.1f} | {Max_TCP:.1f} | {std_dev_TCP:.1f}   |"
    )
    print(
        Fore.BLUE
        + f"|  UDP  | {avg_UDP:.1f} | {Min_UDP:.1f} | {Max_UDP:.1f} | {std_dev_UDP:.1f}   |"
    )
    print(
        Fore.BLUE
        + f"| TCP_R | {avg_TCP_R:.1f} | {Min_TCP_R:.1f} | {Max_TCP_R:.1f} | {std_dev_TCP_R:.1f}   |"
    )
    print(
        Fore.BLUE
        + f"| UDP_R | {avg_UDP_R:.1f} | {Min_UDP_R:.1f} | {Max_UDP_R:.1f} | {std_dev_UDP_R:.1f}   |"
    )
    print(Style.RESET_ALL)

    with open(f"RESULT-{options.filename}.txt", "w") as file:
      
        file.write(formatted_datetime + "\n")

    
        file.write(f"|----------- FINAL RESULT -----------|\n")
        file.write(f"|       | Avg  | Min  | Max  | StdD  |\n")
        file.write(
            f"|  TCP  | {avg_TCP:.1f} | {Min_TCP:.1f} | {Max_TCP:.1f} | {std_dev_TCP:.1f}   |\n"
        )
        file.write(
            f"|  UDP  | {avg_UDP:.1f} | {Min_UDP:.1f} | {Max_UDP:.1f} | {std_dev_UDP:.1f}   |\n"
        )
        file.write(
            f"| TCP_R | {avg_TCP_R:.1f} | {Min_TCP_R:.1f} | {Max_TCP_R:.1f} | {std_dev_TCP_R:.1f}   |\n"
        )
        file.write(
            f"| UDP_R | {avg_UDP_R:.1f} | {Min_UDP_R:.1f} | {Max_UDP_R:.1f} | {std_dev_UDP_R:.1f}   |\n"
        )

    print(Fore.GREEN + f"[+] --> RESULT SAVE ON : {options.filename}" + Style.RESET_ALL)


if __name__ == "__main__":
    main()
