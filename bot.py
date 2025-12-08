
import json
import time
import requests
from eth_account import Account
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

URL = "https://pharoshub.xyz/assets/api/check-wallet"
HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://pharoshub.xyz",
    "referer": "https://pharoshub.xyz/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
}

COOKIES = {
    "_ga": "GA1.1.253428267.1752550830",
    "_ga_9R37J7CL3J": "GS2.1.s1763693869$o10$g1$t1763693880$j49$l0$h0"
}

DELAY = 1.8

def private_key_to_address(pk: str) -> str | None:
    try:
        pk = pk.strip().replace("0x", "")
        return Account.from_key(bytes.fromhex(pk)).address.lower()
    except:
        return None

def check_wallet(address: str):
    try:
        resp = requests.post(URL, json={"wallet_address": address}, headers=HEADERS, cookies=COOKIES, timeout=20)
        if resp.status_code == 200:
            return resp.json()
        else:
            return {"success": False, "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def pretty_print(data: dict, address: str):
    addr = address.upper()
    if not data.get("success"):
        print(f"{Fore.CYAN}→ {addr}")
        print(f"   {Fore.RED}Failed: {data.get('error', 'Unknown error')}{Style.RESET_ALL}\n")
        return

    d = data
    points = f"{Fore.YELLOW}{d['total_points']:,}{Style.RESET_ALL}"
    rank = f"{Fore.MAGENTA}#{d['exact_rank']:,}{Style.RESET_ALL}"
    total = f"{Fore.CYAN}{d.get('total_users_count', 'N/A'):,}{Style.RESET_ALL}"
    level = f"{Fore.GREEN}{d['current_level']}{Style.RESET_ALL}"
    next_lvl = f"{Fore.GREEN}{d['next_level']}{Style.RESET_ALL}"
    need = f"{Fore.RED}{d['points_needed']:,}{Style.RESET_ALL}" if d['points_needed'] > 0 else f"{Fore.GREEN}Max Level!{Style.RESET_ALL}"

    print(f"""
{Fore.CYAN}→ {addr}{Style.RESET_ALL}
   ├─ Total Points      : {points}
   ├─ Rank              : {rank} out of {total} users
   ├─ Level             : {level} → {next_lvl} ({need})
   ├─ Member Since      : {Fore.BLUE}{d['member_since'][:10]}{Style.RESET_ALL}
   ├─ atlantic_onchain  : {Fore.CYAN}{d['atlantic_onchain']}{Style.RESET_ALL}
   ├─ topnod            : {d['topnod']}
   ├─ faroswap_swaps    : {d['faroswap_swaps']}
   ├─ faroswap_lp       : {d['faroswap_lp']}
   ├─ asseto            : {d['asseto']}
   ├─ grandline         : {d['grandline']}
   ├─ bitverse          : {Fore.YELLOW}{d['bitverse']}{Style.RESET_ALL}
   ├─ bitverse_swap     : {d['bitverse_swap']}
   ├─ bitverse_lp       : {d['bitverse_lp']}
   ├─ zenith            : {d['zenith']}
   ├─ aquaflux_earn     : {d['aquaflux_earn']}
   └─ aquaflux_structure: {d['aquaflux_structure']}
{Style.RESET_ALL}""")


def save_clean_result(address: str, data: dict):
    if not data.get("success"):
        clean = {"address": address.upper(), "error": data.get("error", "Failed")}
    else:
        clean = {
            "address": address.upper(),
            "total_points": data["total_points"],
            "rank": data["exact_rank"],
            "level": data["current_level"],
            "points_needed": data["points_needed"],
            "atlantic_onchain": data["atlantic_onchain"],
            "topnod": data["topnod"],
            "faroswap_swaps": data["faroswap_swaps"],
            "faroswap_lp": data["faroswap_lp"],
            "asseto": data["asseto"],
            "grandline": data["grandline"],
            "bitverse": data["bitverse"],
            "bitverse_swap": data["bitverse_swap"],
            "bitverse_lp": data["bitverse_lp"],
            "zenith": data["zenith"],
            "aquaflux_earn": data["aquaflux_earn"],
            "aquaflux_structure": data["aquaflux_structure"],
            "member_since": data["member_since"][:10]
        }
    with open("result.txt", "a", encoding="utf-8") as f:
        json.dump(clean, f, ensure_ascii=False)
        f.write("\n")

def main():
    print(f"{Fore.MAGENTA}{'═' * 55}")
    print(f"{Fore.CYAN}     PHAROS HUB MULTI WALLET CHECKER")
    print(f"{Fore.MAGENTA}{'═' * 55}{Style.RESET_ALL}\n")

    try:
        with open("accounts.txt", "r", encoding="utf-8") as f:
            keys = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        print(f"{Fore.GREEN}Loaded {len(keys)} wallets from accounts.txt{Style.RESET_ALL}\n")
    except FileNotFoundError:
        print(f"{Fore.RED}Error: accounts.txt not found!{Style.RESET_ALL}")
        return

    open("result.txt", "w", encoding="utf-8").close()

    for i, pk in enumerate(keys, 1):
        addr = private_key_to_address(pk)
        if not addr:
            print(f"{Fore.RED}Invalid private key skipped{Style.RESET_ALL}")
            continue

        print(f"{Fore.WHITE}[{i}/{len(keys)}] Checking {addr.upper()}{Style.RESET_ALL}", end="")
        result = check_wallet(addr)
        print(f" → {Fore.GREEN}OK{Style.RESET_ALL}")

        pretty_print(result, addr)
        save_clean_result(addr, result)

        if i < len(keys):
            time.sleep(DELAY)

    print(f"\n{Fore.MAGENTA}╔{'═' * 53}╗")
    print(f"{Fore.CYAN}   All done! Clean results saved to result.txt")
    print(f"{Fore.MAGENTA}╚{'═' * 53}╝{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
