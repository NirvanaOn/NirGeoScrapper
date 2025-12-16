import subprocess, os, datetime

CONTAINER = "kali-recon"
DATA_DIR = "../data"

# ================= CORE EXEC =================
def dexec(cmd):
    try:
        return subprocess.run(
            ["docker", "exec", CONTAINER] + cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        ).stdout.strip()
    except Exception as e:
        return f"[ERROR] {e}"

def write(report, title, data):
    report.write(f"\n[{title}]\n")
    report.write(data + "\n")
    report.write("-" * 70 + "\n")
    report.flush()

# ================= MAIN =================
def main():
    target = input("Target domain: ").strip()
    level = input("Scan level (fast / medium / high): ").strip().lower()

    if level not in ["fast", "medium", "high"]:
        print("Invalid scan level")
        return

    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs(DATA_DIR, exist_ok=True)
    base = f"{DATA_DIR}/{target}_{level}_{ts}"
    report_path = base + "_REPORT.txt"

    with open(report_path, "w", encoding="utf-8") as report:
        report.write("VAPT AUTOMATED REPORT\n")
        report.write(f"Target : {target}\n")
        report.write(f"Level  : {level.upper()}\n")
        report.write(f"Time   : {ts}\n")
        report.write("=" * 70 + "\n")

        # ================= FAST =================
        print("[+] FAST Recon")

        write(report, "TECHNOLOGY (WHATWEB)",
              dexec(["whatweb", "--no-errors", "--color=never", target]))

        write(report, "WAF DETECTION",
              dexec(["wafw00f", target]))

        write(report, "HTTP PROBE",
              dexec([
                  "bash", "-c",
                  f"echo {target} | httpx-toolkit -sc -title -ip -cdn -timeout 0 -silent"
              ]))

        write(report, "TLS / SSL INFO",
              dexec([
                  "nmap", "--script", "ssl-cert,ssl-enum-ciphers",
                  "-p", "443", target
              ]))

        write(report, "SSL SCAN",
              dexec(["sslscan", target]))

        if level == "fast":
            print(f"[✔] FAST scan complete → {report_path}")
            return

        # ================= MEDIUM =================
        print("[+] MEDIUM Recon")

        subs = dexec(["subfinder", "-d", target, "-silent"])
        write(report, "SUBDOMAINS", subs)

        alive = dexec([
            "bash", "-c",
            f"subfinder -d {target} -silent | httpx-toolkit -sc -timeout 0 -silent"
        ])
        write(report, "ALIVE HOSTS", alive)

        write(report, "DNS ENUMERATION",
              dexec(["dnsrecon", "-d", target]))

        write(report, "PORT SCAN (TOP 100)",
              dexec(["nmap", "-Pn", "-T3", "--top-ports", "100", target]))

        write(report, "OSINT (theHarvester)",
              dexec([
                  "theHarvester", "-d", target,
                  "-b", "bing,crtsh,duckduckgo"
              ]))

        urls = (
            dexec(["gau", target]) +
            "\n" +
            dexec(["waybackurls", target])
        )

        urls_file = base + "_urls.txt"
        with open(urls_file, "w") as f:
            f.write(urls)

        write(report, "PASSIVE URLS", urls)

        if level == "medium":
            print(f"[✔] MEDIUM scan complete → {report_path}")
            return

        # ================= HIGH =================
        print("[+] HIGH Recon")

        write(report, "CRAWLING (KATANA)",
              dexec([
                  "katana",
                  "-u", f"https://{target}",
                  "-d", "5",
                  "-jc",
                  "-ps",
                  "-silent"
              ]))

        write(report, "PARAMETER DISCOVERY",
              dexec(["paramspider", "-d", target]))

        write(report, "GF XSS FILTER",
              dexec(["bash", "-c", f"cat {urls_file} | gf xss"]))

        write(report, "DALFOX XSS SCAN",
              dexec([
                  "dalfox", "file", urls_file,
                  "--timeout", "0"
              ]))

        write(report, "NUCLEI VULNERABILITY SCAN",
              dexec([
                  "nuclei",
                  "-u", f"https://{target}",
                  "-severity", "medium,high,critical",
                  "-timeout", "0",
                  "-retries", "0",
                  "-rl", "0",
                  "-nc"
              ]))

        write(report, "CORS MISCONFIGURATION",
              dexec(["corsy", "-u", target]))

    print(f"\n[✔] HIGH scan complete → {report_path}")

# ================= ENTRY =================
if __name__ == "__main__":
    main()
