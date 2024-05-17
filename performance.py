import iperf3
import subprocess
import argparse
from colorama import Fore, Style


def perf(client, options, receive, name, protocol):
    # Set vars
    remote_site = options.address
    test_duration = 10

    # Set Iperf Client Options
    client.server_hostname = remote_site
    client.zerocopy = True
    client.verbose = False
    client.port = 5201
    client.num_streams = 10
    client.duration = int(test_duration)
    client.protocol = protocol  # PROBLEMA
    client.reverse = receive
    client.length = 1472
    client.bandwidth = 50000000000

    try:
        dump = subprocess.Popen(
            [
                "sudo",
                "tcpdump",
                "-i",
                options.interface,
                "-w",
                name + "-" + options.filename,
            ],
            stdin=subprocess.PIPE,
        )
        dump.stdin.write(b"password\n")
        dump.stdin.flush()

        # Run iperf3 test
        result = client.run()

        # extract relevant data
        sent_mbps = int(result.sent_Mbps)
        received_mbps = int(result.received_Mbps)

        print(Fore.YELLOW + f"{protocol.upper()} sent_mbps: {sent_mbps}")
        print(Fore.YELLOW + f"{protocol.upper()} received_mbps: {received_mbps}")
        print(Fore.YELLOW + f"{protocol.upper()} reverse mode : {receive}")
        print(Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + f"Error during UDP test: {e}")
        print(Style.RESET_ALL)
    finally:
        dump.terminate()
        print(Fore.GREEN + f"[+] dump made for {options.filename} {name}")
        print(Style.RESET_ALL)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", dest="filename", help="write report to FILE")
    parser.add_argument(
        "-i", "--interface", dest="interface", help="write the interface"
    )
    parser.add_argument("-a", "--address", dest="address", help="write the address")

    options = parser.parse_args()

    client = iperf3.Client()
    perf(client, options, receive=False, name="TCP", protocol="tcp")

    clientB = iperf3.Client()
    perf(clientB, options, receive=False, name="UDP", protocol="udp")
    clientC = iperf3.Client()
    perf(clientC, options, receive=True, name="TCP-REC", protocol="tcp")
    clientD = iperf3.Client()
    perf(clientD, options, receive=True, name="UDP-REC", protocol="udp")


if __name__ == "__main__":
    main()
