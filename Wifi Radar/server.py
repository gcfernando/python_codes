#!/usr/bin/env python3
"""
Developer ::> Gehan Fernando
WiFi Military Radar - Backend Server
Windows / macOS / Linux

  Windows  ->  python server.py          (or double-click START_WINDOWS.bat)
  macOS    ->  python3 server.py
  Linux    ->  sudo python3 server.py

Open  ->  http://localhost:5000
Debug ->  http://localhost:5000/api/debug
"""

import subprocess, re, time, threading, platform, hashlib, os, sys, csv, io

# ── Auto-install deps ─────────────────────────────────────────────────────────
def ensure_deps():
    need = []
    try: import flask
    except ImportError: need.append('flask')
    try: import flask_cors
    except ImportError: need.append('flask-cors')
    if need:
        print(f"[SETUP] Installing: {need}", flush=True)
        subprocess.run([sys.executable,'-m','pip','install','--quiet']+need, check=True)
        os.execv(sys.executable, [sys.executable]+sys.argv)
ensure_deps()

from flask import Flask, jsonify, send_from_directory, Response, request
from flask_cors import CORS

app = Flask(__name__, static_folder='.')
CORS(app)
OS = platform.system()

state = {
    "networks":    [],
    "last_updated":0,
    "scan_count":  0,
    "os":          OS,
    "scanning":    False,
    "last_error":  "",
    "raw_output":  "",
    "method":      "—",
    "new_bssids":  [],   # BSSIDs discovered since last /api/scan poll
}
lock = threading.Lock()

# ─────────────────────────────────────────────────────────────────────────────
#  OUI VENDOR DATABASE  (top ~200 most common router vendors)
#  Format: first 6 hex chars (no colons, uppercase) -> vendor name
# ─────────────────────────────────────────────────────────────────────────────
OUI = {
    # TP-Link
    "1C61B4":"TP-Link","50C7BF":"TP-Link","A0F3C1":"TP-Link","C46E1F":"TP-Link",
    "8C8590":"TP-Link","B0487A":"TP-Link","E4F14E":"TP-Link","00E04C":"TP-Link",
    "D46E5C":"TP-Link","9C5322":"TP-Link","B4B024":"TP-Link","F8D111":"TP-Link",
    "10BF48":"TP-Link","2C4D54":"TP-Link","70085B":"TP-Link","3C52A1":"TP-Link",
    # ASUS
    "04D9F5":"ASUS","10BF48":"ASUS","107B44":"ASUS","1C872C":"ASUS",
    "2C56DC":"ASUS","2CFD55":"ASUS","305A3A":"ASUS","382C4A":"ASUS",
    "40167E":"ASUS","50465D":"ASUS","60A44C":"ASUS","6045CB":"ASUS",
    "74D02B":"ASUS","88D7F6":"ASUS","AC220B":"ASUS","B06EBF":"ASUS",
    "BC9946":"ASUS","E03F49":"ASUS","F832E4":"ASUS","04921F":"ASUS",
    # Netgear
    "00095B":"Netgear","001B2F":"Netgear","002275":"Netgear","00266C":"Netgear",
    "204E7F":"Netgear","28C68E":"Netgear","2CB05D":"Netgear","44947C":"Netgear",
    "4F58CD":"Netgear","6CB0CE":"Netgear","84189F":"Netgear","A021B7":"Netgear",
    "C03F0E":"Netgear","C4042A":"Netgear","E091F5":"Netgear","E4F4C6":"Netgear",
    # Linksys / Cisco
    "000C41":"Cisco","001225":"Cisco","0016B6":"Linksys","00183B":"Linksys",
    "001A70":"Linksys","001C10":"Linksys","001D7E":"Linksys","001E58":"Linksys",
    "002369":"Linksys","00259C":"Linksys","0026B9":"Linksys","C8BE19":"Linksys",
    # D-Link
    "001195":"D-Link","0015E9":"D-Link","00176F":"D-Link","001A2B":"D-Link",
    "001CF0":"D-Link","001E58":"D-Link","002191":"D-Link","00265A":"D-Link",
    "1CAFF7":"D-Link","2840B4":"D-Link","340A33":"D-Link","7C8BCA":"D-Link",
    "9094E4":"D-Link","B8A386":"D-Link","C8BE19":"D-Link","F07D68":"D-Link",
    # Huawei
    "001E10":"Huawei","002568":"Huawei","0025D3":"Huawei","00259E":"Huawei",
    "047503":"Huawei","086349":"Huawei","0C37DC":"Huawei","0C96BF":"Huawei",
    "2C9D65":"Huawei","3440B5":"Huawei","4C1FCC":"Huawei","5439DF":"Huawei",
    "6885C1":"Huawei","90E7C4":"Huawei","AC853D":"Huawei","D4612E":"Huawei",
    # Apple (Airport)
    "00030E":"Apple","000A27":"Apple","000A95":"Apple","000D93":"Apple",
    "001124":"Apple","001451":"Apple","0016CB":"Apple","0017F2":"Apple",
    "0019E3":"Apple","001B63":"Apple","001CB3":"Apple","001E52":"Apple",
    "0021E9":"Apple","002312":"Apple","002500":"Apple","002608":"Apple",
    "34363B":"Apple","38C986":"Apple","3C0754":"Apple","40A6D9":"Apple",
    "70E72C":"Apple","781FDB":"Apple","7CAF97":"Apple","98FE94":"Apple",
    # Ubiquiti
    "002722":"Ubiquiti","04186D":"Ubiquiti","0418D6":"Ubiquiti","044BC8":"Ubiquiti",
    "18E829":"Ubiquiti","24A43C":"Ubiquiti","44D9E7":"Ubiquiti","687278":"Ubiquiti",
    "788A20":"Ubiquiti","802AA8":"Ubiquiti","DC9FDB":"Ubiquiti","E063DA":"Ubiquiti",
    "F09FC2":"Ubiquiti","F492BF":"Ubiquiti","FCECDA":"Ubiquiti",
    # MikroTik
    "000C42":"MikroTik","18FD74":"MikroTik","2CC8E9":"MikroTik","4C5E0C":"MikroTik",
    "6C3B6B":"MikroTik","74AD5C":"MikroTik","B8690E":"MikroTik","C4AD34":"MikroTik",
    "D4CA6D":"MikroTik","DC2C6E":"MikroTik","E48D8C":"MikroTik",
    # Aruba / HP
    "000B86":"Aruba","001A1E":"Aruba","24DE C6":"Aruba","40E3D6":"Aruba",
    "6C7220":"Aruba","70888B":"Aruba","84D47E":"Aruba","885BB4":"Aruba",
    "94B40F":"Aruba","9C1C12":"Aruba","AC:A3:1E":"Aruba","D8C7C8":"Aruba",
    # Synology
    "001132":"Synology","0011FA":"Synology","BC5FF4":"Synology",
    # FRITZ!Box (AVM)
    "3C3712":"AVM","542D7F":"AVM","7851B2":"AVM","9489EA":"AVM",
    "A4B1E9":"AVM","AC1608":"AVM","B4795E":"AVM","C82360":"AVM","D43100":"AVM",
    # Belkin
    "001150":"Belkin","001CDF":"Belkin","082698":"Belkin","103755":"Belkin",
    "147D22":"Belkin","20AA4B":"Belkin","94103E":"Belkin","B44BD0":"Belkin",
    "EC1A59":"Belkin",
    # ZTE
    "001E73":"ZTE","0824AF":"ZTE","1C8779":"ZTE","203D66":"ZTE",
    "28CF39":"ZTE","34E0CF":"ZTE","3816D1":"ZTE","40F384":"ZTE",
    "48C654":"ZTE","4C09D4":"ZTE","5440AD":"ZTE","64136C":"ZTE",
    "6C8132":"ZTE","7871E5":"ZTE","8009D7":"ZTE","8C2DAA":"ZTE",
    # Xiaomi
    "001C14":"Xiaomi","0C1DAF":"Xiaomi","28D1273":"Xiaomi","34CE00":"Xiaomi",
    "50EC50":"Xiaomi","58:44:98":"Xiaomi","64B473":"Xiaomi","7851CB":"Xiaomi",
    "98FAE3":"Xiaomi","A45841":"Xiaomi","F48B32":"Xiaomi","FC64BA":"Xiaomi",
    # Samsung
    "001247":"Samsung","001599":"Samsung","0016DB":"Samsung","001A8A":"Samsung",
    "0021D2":"Samsung","002339":"Samsung","0024E9":"Samsung","002566":"Samsung",
    "10D542":"Samsung","1C66AA":"Samsung","2073E0":"Samsung","28987B":"Samsung",
    "3425E2":"Samsung","40E5CF":"Samsung","5C0A5B":"Samsung","5CD2E4":"Samsung",
    "6031CE":"Samsung","8018A7":"Samsung","8C71F8":"Samsung","90F1AA":"Samsung",
    "A06090":"Samsung","B47443":"Samsung","C867AF":"Samsung","D0176A":"Samsung",
    # Google (Nest/OnHub)
    "1C09EB":"Google","304167":"Google","38CA84":"Google","4C31FE":"Google",
    "54607E":"Google","587A62":"Google","704FF5":"Google","748A7C":"Google",
    "A47733":"Google","F88FCA":"Google",
    # Amazon (Eero/Echo)
    "107EFE":"Amazon","18742E":"Amazon","40B4CD":"Amazon","44650D":"Amazon",
    "5475D0":"Amazon","68370B":"Amazon","6C5697":"Amazon","74C246":"Amazon",
    "A002DC":"Amazon","AC63BE":"Amazon","B47C9C":"Amazon","F0272D":"Amazon",
    "FC65DE":"Amazon",
    # Comcast / Xfinity
    "000C46":"Arris","001469":"Arris","00905D":"Arris","1C6311":"Arris",
    "286ABA":"Arris","3840A6":"Arris","40D32D":"Arris","507688":"Arris",
    "60EF55":"Arris","74873C":"Arris","800009":"Arris","9C34BF":"Arris",
    # Motorola
    "000AF5":"Motorola","001B77":"Motorola","003A99":"Motorola","00E030":"Motorola",
    "1451D1":"Motorola","40409B":"Motorola","58B035":"Motorola",
    # Ruckus
    "000C2C":"Ruckus","001392":"Ruckus","189461":"Ruckus","24C9A1":"Ruckus",
    "2C5A0F":"Ruckus","4C0082":"Ruckus","58B633":"Ruckus","607B6A":"Ruckus",
    "74911A":"Ruckus","9C1C12":"Ruckus",
    # Eero
    "F45D76":"Eero","FC01DC":"Eero","AC84C9":"Eero","48A512":"Eero",
    # GL.iNet
    "94835B":"GL.iNet","E4956E":"GL.iNet","B4E842":"GL.iNet",
    # OpenWRT common
    "000CE6":"ChinaNet","000D88":"Actiontec","001871":"Actiontec",
}

def lookup_vendor(bssid: str) -> str:
    """Look up manufacturer from first 3 bytes of MAC address."""
    oui = bssid.replace(':','').replace('-','').upper()[:6]
    return OUI.get(oui, 'Unknown')

# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def stable_pos(bssid):
    h = hashlib.md5(bssid.upper().encode()).hexdigest()
    return int(h[0:4],16)%360, 15+int(h[4:8],16)%72

def norm_sec(s):
    s = str(s).upper().strip()
    if not s or s in ('-','--','NONE','OPEN','OPN','OPENSYSTEM',''):
        return 'OPEN'
    if ('WPA2' in s and 'WPA3' in s) or 'WPA2/WPA3' in s or 'WPA3/WPA2' in s:
        return 'WPA2/WPA3'
    if 'WPA3' in s or 'SAE' in s or 'OWE' in s:
        return 'WPA3'
    if 'WPA2' in s or 'RSN' in s or 'CCMP' in s or '802.1X' in s:
        return 'WPA2'
    if 'WPA' in s or 'TKIP' in s:
        return 'WPA'
    if 'WEP' in s:
        return 'WEP'
    return 'WPA2'

def make_ap(ssid, bssid, sig_pct, sig_dbm, channel, security):
    bssid   = str(bssid).upper().replace('-',':').strip()
    channel = int(channel) if channel else 6
    try:    sig_pct = max(0, min(100, int(sig_pct)))
    except: sig_pct = 50
    sig_dbm = int(sig_dbm) if sig_dbm is not None else round(-100 + sig_pct*0.5)
    angle, dist = stable_pos(bssid)
    return {
        'ssid':       str(ssid).strip() or '<hidden>',
        'bssid':      bssid,
        'vendor':     lookup_vendor(bssid),
        'signal_pct': sig_pct,
        'signal_dbm': sig_dbm,
        'channel':    channel,
        'security':   norm_sec(security),
        'band':       '5GHz' if channel > 14 else '2.4GHz',
        'angle':      angle,
        'distance':   dist,
        'stale':      False,
    }

# ─────────────────────────────────────────────────────────────────────────────
#  WINDOWS SCANNER
# ─────────────────────────────────────────────────────────────────────────────

def get_netsh_output():
    cf = 0x08000000 if OS=='Windows' else 0
    for enc in ('utf-8','cp1252','cp850','latin-1','mbcs'):
        try:
            r = subprocess.run(
                ['netsh','wlan','show','networks','mode=Bssid'],
                capture_output=True, timeout=25, creationflags=cf
            )
            text = r.stdout.decode(enc, errors='replace')
            if text.strip():
                return text
        except Exception as e:
            pass
    return ""

def scan_windows():
    raw  = get_netsh_output()
    nets = []
    if not raw.strip():
        return nets, raw, "netsh_no_output"

    txt = raw.replace('\r\n','\n').replace('\r','\n')

    # Two-level split: SSID blocks -> BSSID sub-blocks
    # METADATA_KEYWORDS: if a blank SSID causes the next metadata line to
    # be captured (e.g. "Network type : Infrastructure"), detect and strip it.
    JUNK = re.compile(
        r'^(?:network\s+type|authentication|encryption|bssid|signal|channel|'
        r'radio\s+type|basic\s+rates|other\s+rates|network\s+number)\s*:',
        re.IGNORECASE
    )
    parts = re.split(r'\nSSID\s+\d+\s*:\s*([^\n]*)', '\n'+txt)
    i = 1
    while i+1 < len(parts):
        raw_ssid   = parts[i].strip()
        ssid_block = parts[i+1]
        i += 2
        # If captured text looks like a metadata key:value, the real SSID was blank
        ssid = '<hidden>' if (not raw_ssid or JUNK.match(raw_ssid) or ':' in raw_ssid) else raw_ssid
        if re.match(r'[0-9A-Fa-f]{2}[:\-]', ssid): continue
        auth_m = re.search(r'(?i)authentication\s*:\s*(.+)', ssid_block)
        sec    = auth_m.group(1).strip() if auth_m else 'WPA2-Personal'
        bssid_parts = re.split(
            r'\n\s*BSSID\s+\d+\s*:\s*([0-9A-Fa-f]{2}(?:[:\-][0-9A-Fa-f]{2}){5})',
            '\n'+ssid_block
        )
        if len(bssid_parts) < 3:
            all_macs = re.findall(r'([0-9A-Fa-f]{2}(?:[:\-][0-9A-Fa-f]{2}){5})', ssid_block)
            all_sigs = re.findall(r'(?i)signal\s*:\s*(\d+)\s*%', ssid_block)
            all_chs  = re.findall(r'(?i)channel\s*:\s*(\d+)', ssid_block)
            for j, mac in enumerate(all_macs):
                nets.append(make_ap(ssid, mac.replace('-',':'),
                                    int(all_sigs[j]) if j<len(all_sigs) else 50,
                                    None, int(all_chs[j]) if j<len(all_chs) else 6, sec))
            continue
        j = 1
        while j+1 < len(bssid_parts):
            mac      = bssid_parts[j].strip().replace('-',':')
            subblock = bssid_parts[j+1]
            j += 2
            sig_m = re.search(r'(?i)signal\s*:\s*(\d+)\s*%', subblock)
            ch_m  = re.search(r'(?i)channel\s*:\s*(\d+)',     subblock)
            nets.append(make_ap(ssid, mac,
                                int(sig_m.group(1)) if sig_m else 50,
                                None, int(ch_m.group(1)) if ch_m else 6, sec))
    if nets: return nets, raw, f"netsh({len(nets)})"

    # Fallback state machine
    cur_ssid,cur_sec,cur_mac,cur_sig,cur_ch = '<hidden>','WPA2-Personal',None,50,6
    def commit():
        if cur_mac: nets.append(make_ap(cur_ssid,cur_mac,cur_sig,None,cur_ch,cur_sec))
    for line in txt.split('\n'):
        s = line.strip()
        if not s: continue
        m = re.match(r'^SSID\s+\d+\s*:\s*(.*)$', s, re.I)
        if m and not s.upper().startswith('BSSID'):
            commit(); cur_mac=None; cur_ssid=m.group(1).strip() or '<hidden>'
            cur_sec='WPA2-Personal'; cur_sig=50; cur_ch=6; continue
        m = re.match(r'^BSSID\s+\d+\s*:\s*(.+)$', s, re.I)
        if m:
            commit()
            mm = re.search(r'([0-9A-Fa-f]{2}(?:[:\-][0-9A-Fa-f]{2}){5})', m.group(1))
            cur_mac = mm.group(1).replace('-',':').upper() if mm else None
            cur_sig=50; cur_ch=6; continue
        m = re.match(r'^(?:authentication|auth)\s*:\s*(.+)$', s, re.I)
        if m: cur_sec=m.group(1).strip(); continue
        m = re.match(r'^signal\s*:\s*(\d+)\s*%', s, re.I)
        if m: cur_sig=int(m.group(1)); continue
        m = re.match(r'^channel\s*:\s*(\d+)', s, re.I)
        if m: cur_ch=int(m.group(1)); continue
    commit()
    return nets, raw, f"netsh_fallback({len(nets)})"

# ─────────────────────────────────────────────────────────────────────────────
#  macOS SCANNER
# ─────────────────────────────────────────────────────────────────────────────

def scan_macos():
    raw, nets = "", []
    for airport in [
        '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport',
        '/usr/local/bin/airport',
    ]:
        if not os.path.exists(airport): continue
        try:
            r = subprocess.run([airport,'-s'], capture_output=True, text=True, timeout=15)
            raw = r.stdout
            if raw.strip(): break
        except: pass
    for line in raw.strip().splitlines()[1:]:
        m = re.match(r'\s*(.+?)\s{2,}([0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5})\s+(-\d+)\s+(\S+)', line)
        if not m: continue
        ssid,bssid = m.group(1).strip() or '<hidden>', m.group(2)
        sig_dbm = int(m.group(3))
        ch_m = re.match(r'(\d+)', m.group(4))
        channel = int(ch_m.group(1)) if ch_m else 6
        sec = 'WPA2' if ('WPA2' in line or 'RSN' in line) else 'WPA' if 'WPA' in line else 'OPEN'
        nets.append(make_ap(ssid, bssid, max(0,min(100,2*(sig_dbm+100))), sig_dbm, channel, sec))
    if not nets:
        try:
            r = subprocess.run(['system_profiler','SPAirPortDataType'], capture_output=True, text=True, timeout=30)
            raw += r.stdout
            for block in re.split(r'\n(?=\s{8}\S)', raw):
                sm=re.match(r'\s+([^\n:]+):',block); bm=re.search(r'Network ID\s*:\s*([0-9a-fA-F:]{17})',block)
                gm=re.search(r'Signal / Noise\s*:\s*(-\d+)',block); cm=re.search(r'Channel\s*:\s*(\d+)',block)
                if sm and gm:
                    ssid=sm.group(1).strip(); bssid=bm.group(1) if bm else hashlib.md5(ssid.encode()).hexdigest()[:17]
                    sig_dbm=int(gm.group(1))
                    nets.append(make_ap(ssid,bssid,max(0,min(100,2*(sig_dbm+100))),sig_dbm,int(cm.group(1)) if cm else 6,'WPA2'))
        except: pass
    return nets, raw, f"airport({len(nets)})"

# ─────────────────────────────────────────────────────────────────────────────
#  LINUX SCANNER
# ─────────────────────────────────────────────────────────────────────────────

def scan_linux():
    raw, nets = "", []
    try:
        r = subprocess.run(['nmcli','--terse','--fields','SSID,BSSID,SIGNAL,CHAN,SECURITY',
                            'dev','wifi','list','--rescan','yes'], capture_output=True, text=True, timeout=20)
        raw = r.stdout
        if r.returncode==0 and raw.strip():
            for line in raw.strip().splitlines():
                parts = [p.replace('\\:',':') for p in re.split(r'(?<!\\):',line)]
                if len(parts)<4: continue
                ssid, bssid = parts[0], parts[1]
                if not re.match(r'[0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){5}', bssid): continue
                try: sp=int(parts[2])
                except: sp=50
                try: ch=int(parts[3])
                except: ch=6
                nets.append(make_ap(ssid, bssid, sp, None, ch, parts[4] if len(parts)>4 else 'WPA2'))
            if nets: return nets, raw, f"nmcli({len(nets)})"
    except FileNotFoundError: raw+="\n[nmcli not found]"
    except Exception as e: raw+=f"\n[nmcli: {e}]"
    try:
        r = subprocess.run(['iwlist','scan'], capture_output=True, text=True, timeout=20)
        raw += r.stdout
        for cell in re.split(r'Cell \d+ - ', r.stdout)[1:]:
            sm=re.search(r'ESSID:"([^"]*)"',cell); bm=re.search(r'Address: ([0-9A-Fa-f:]{17})',cell)
            gm=re.search(r'Signal level[=:](-?\d+)',cell); cm=re.search(r'Channel[=:](\d+)',cell)
            em=re.search(r'Encryption key:(on|off)',cell)
            if not bm: continue
            sig_dbm=int(gm.group(1)) if gm else -80
            nets.append(make_ap(sm.group(1) if sm else '<hidden>', bm.group(1),
                                max(0,min(100,2*(sig_dbm+100))), sig_dbm,
                                int(cm.group(1)) if cm else 6,
                                ('WPA2' if 'WPA2' in cell else 'WPA' if 'WPA' in cell else 'WEP')
                                if em and em.group(1)=='on' else 'OPEN'))
        if nets: return nets, raw, f"iwlist({len(nets)})"
    except: pass
    return nets, raw, "linux_none"

def do_scan():
    if OS=='Windows': return scan_windows()
    if OS=='Darwin':  return scan_macos()
    return scan_linux()

# ─────────────────────────────────────────────────────────────────────────────
#  BACKGROUND SCANNER THREAD
# ─────────────────────────────────────────────────────────────────────────────

def scanner_loop():
    known     = {}
    ever_seen = set()   # all BSSIDs ever detected this session

    while True:
        try:
            with lock: state['scanning'] = True
            nets, raw, method = do_scan()
            now = int(time.time())
            print(f"[{time.strftime('%H:%M:%S')}] {method}  total={len(nets)}", flush=True)

            new_bssids = []
            updated    = {}
            for n in nets:
                k = n['bssid']
                n['first_seen'] = known[k]['first_seen'] if k in known else now
                n['last_seen']  = now
                n['stale']      = False
                updated[k]      = n
                if k not in ever_seen:
                    ever_seen.add(k)
                    new_bssids.append(k)   # brand-new this session

            for k, old in known.items():
                if k not in updated and (now-old.get('last_seen',0)) < 30:
                    old = dict(old); old['stale']=True; updated[k]=old
            known = {k:v for k,v in updated.items() if (now-v.get('last_seen',0))<60}

            with lock:
                state['networks']     = list(known.values())
                state['last_updated'] = now
                state['scan_count']  += 1
                state['scanning']     = False
                state['method']       = method
                state['raw_output']   = raw[:4000]
                state['last_error']   = ''
                state['new_bssids']   = new_bssids   # frontend picks these up

        except Exception as e:
            with lock: state['scanning']=False; state['last_error']=str(e)
            print(f"[ERROR] {e}", flush=True)
        time.sleep(4)

# ─────────────────────────────────────────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/api/scan')
def api_scan():
    with lock:
        new = state['new_bssids'][:]
        state['new_bssids'] = []          # clear after delivery
        return jsonify({
            'networks':     state['networks'],
            'last_updated': state['last_updated'],
            'scan_count':   state['scan_count'],
            'os':           state['os'],
            'scanning':     state['scanning'],
            'method':       state['method'],
            'total':        len(state['networks']),
            'new_bssids':   new,
        })

@app.route('/api/export/csv')
def api_export_csv():
    """Download all currently visible networks as a CSV file."""
    with lock:
        nets = state['networks'][:]
    buf = io.StringIO()
    w   = csv.writer(buf)
    w.writerow(['SSID','BSSID','Vendor','Signal_dBm','Signal_%',
                'Channel','Band','Security','Status','First_Seen','Last_Seen'])
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    for n in sorted(nets, key=lambda x: -x['signal_pct']):
        w.writerow([
            n['ssid'], n['bssid'], n.get('vendor','Unknown'),
            n['signal_dbm'], n['signal_pct'],
            n['channel'], n['band'], n['security'],
            'STALE' if n.get('stale') else 'ACTIVE',
            time.strftime('%H:%M:%S', time.localtime(n.get('first_seen',0))),
            time.strftime('%H:%M:%S', time.localtime(n.get('last_seen',0))),
        ])
    fname = f"wifi_scan_{time.strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        buf.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{fname}"'}
    )

@app.route('/api/debug')
def api_debug():
    with lock:
        lines = ["═"*60,"  WiFi Radar v5 PROD  –  Debug","═"*60,
                 f"  OS={state['os']}  Method={state['method']}",
                 f"  Scans={state['scan_count']}  Networks={len(state['networks'])}",
                 f"  Error={state['last_error'] or 'none'}","","  NETWORKS:"]
        for n in state['networks']:
            lines.append(f"    {n['ssid']:<26} {n['bssid']}  {n['signal_dbm']:>4}dBm"
                         f"  ch{n['channel']:>3}  {n['security']:<10}  {n.get('vendor','?')}")
        lines += ["","  RAW:","─"*60, state['raw_output']]
        return Response('\n'.join(lines), mimetype='text/plain')

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__=='__main__':
    print(f"""
╔══════════════════════════════════════════════════╗
║   WiFi MILITARY RADAR  v5 PROD  –  {OS:<13}      ║
╠══════════════════════════════════════════════════╣
║  Radar  →  http://localhost:5000                 ║
║  Export →  http://localhost:5000/api/export/csv  ║
║  Debug  →  http://localhost:5000/api/debug       ║
╚══════════════════════════════════════════════════╝""", flush=True)
    threading.Thread(target=scanner_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
