# WifiPerformance-Iperf3
## WiFI LAB Iperf3 performance evaluation POLITO
This is a tool created to automatically manage a Wi-Fi Ethernet performance measurement simulation using the [Iperf](https://github.com/esnet/iperf) and [tcpdump](https://github.com/the-tcpdump-group/tcpdump) tools.


### INSTALLATION SET UP
To ensure the tool functions correctly, make sure you have all dependencies installed.
---

Run these commands for an GNU/Linux Debian environment.

```bash
sudo apt install tcpdump
sudo apt install iperf3
pip install -r requirements.txt
```


---
To run the script, type the command:

```bash
python3 performance.py -f <fileName> -i <NameInterface> -a <address>
```

or 

```bash
python3 performance.py -f <fileName> -i <NameInterface> -a <address> -p <portNumber>[optional]
```



### OUTPUT EXAMPLE of a correct execution
```
          2024-05-21 10:39:06
|----------- FINAL RESULT -----------|
|       | Avg  | Min  | Max  | StdD  |
|  TCP  | 49.7 | 47.0 | 52.8 | 1.7   |
|  UDP  | 48.5 | 38.0 | 50.0 | 3.7   |
| TCP_R | 29.3 | 22.4 | 32.2 | 3.2   |
| UDP_R | 30.3 | 2.5 | 38.0 | 12.0   |
```
