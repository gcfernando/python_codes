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
import urllib.request, urllib.error, urllib.parse, json

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
#  VENDOR CACHE  — in-memory cache for API lookups + persistent file cache
# ─────────────────────────────────────────────────────────────────────────────
_vendor_cache      = {}          # oui6 -> vendor string
_vendor_pending    = set()       # ouis currently being looked up
_vendor_cache_lock = threading.Lock()
CACHE_FILE         = os.path.join(os.path.dirname(__file__), 'vendor_cache.json')

def _load_cache_file():
    """Load persisted vendor cache from disk on startup."""
    global _vendor_cache
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                data = json.load(f)
            with _vendor_cache_lock:
                _vendor_cache.update(data)
            print(f"[VENDOR] Loaded {len(data)} cached vendors from disk", flush=True)
    except Exception as e:
        print(f"[VENDOR] Cache load error: {e}", flush=True)

def _save_cache_file():
    """Persist vendor cache to disk."""
    try:
        with _vendor_cache_lock:
            data = dict(_vendor_cache)
        with open(CACHE_FILE, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"[VENDOR] Cache save error: {e}", flush=True)

def _fetch_vendor_api(bssid: str) -> str:
    """
    Query macvendors.com with the full MAC address.
    Accepts any format — we send XX:XX:XX:XX:XX:XX
    Returns vendor string or 'Unknown'.
    """
    url = f"https://api.macvendors.com/{urllib.parse.quote(bssid)}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'WiFi-Radar/5'})
        with urllib.request.urlopen(req, timeout=5) as r:
            vendor = r.read().decode('utf-8', errors='replace').strip()
            if vendor and len(vendor) < 80:
                return vendor
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return 'Unknown'        # legitimate "not found"
    except Exception:
        pass
    return 'Unknown'

def _vendor_lookup_thread(bssids: list):
    """
    Background thread: look up a batch of (oui6, full_bssid) pairs.
    Rate-limit: macvendors.com free tier = 1 req/sec.
    """
    changed = False
    for oui6, bssid in bssids:
        time.sleep(1.05)            # stay under 1 req/sec free limit
        vendor = _fetch_vendor_api(bssid)
        with _vendor_cache_lock:
            _vendor_cache[oui6] = vendor
            _vendor_pending.discard(oui6)
        print(f"[VENDOR] {bssid} ({oui6}) -> {vendor}", flush=True)
        changed = True
    if changed:
        _save_cache_file()

def lookup_vendor(bssid: str) -> str:
    """
    Look up manufacturer for a BSSID.
    1) In-memory / disk cache (instant — populated by macvendors.com API)
    2) Async API fetch via macvendors.com if not cached yet
    Returns immediately — resolved vendor appears on the next scan cycle.
    """
    clean = bssid.replace(':','').replace('-','').replace(' ','').upper()
    oui   = clean[:6]
    if len(oui) < 6:
        return 'Unknown'

    # 1. Memory / disk cache (instant)
    with _vendor_cache_lock:
        cached = _vendor_cache.get(oui)
        if cached is not None:
            return cached
        # 2. Queue async API lookup with full BSSID if not already pending
        if oui not in _vendor_pending:
            _vendor_pending.add(oui)
            threading.Thread(
                target=_vendor_lookup_thread,
                args=([(oui, bssid)],),
                daemon=True
            ).start()

    return 'Looking up…'



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

def norm_radio(s):
    """Normalise 802.11 radio type string to clean label."""
    s = str(s).upper().replace('802.11','').strip()
    # Map common netsh/nmcli variants
    for tag,label in [('BE','WiFi 7 (be)'),('AX','WiFi 6 (ax)'),('AC','WiFi 5 (ac)'),
                      ('N','WiFi 4 (n)'),('G','802.11g'),('B','802.11b'),('A','802.11a')]:
        if tag in s: return label
    return s if s else '—'

def make_ap(ssid, bssid, sig_pct, sig_dbm, channel, security,
            radio_type='—', noise_dbm=None, cipher='—', net_type='Infrastructure',
            rates=None):
    bssid   = str(bssid).upper().replace('-',':').strip()
    channel = int(channel) if channel else 6
    try:    sig_pct = max(0, min(100, int(sig_pct)))
    except: sig_pct = 50
    sig_dbm = int(sig_dbm) if sig_dbm is not None else round(-100 + sig_pct*0.5)
    noise_dbm = int(noise_dbm) if noise_dbm is not None else None
    snr = (sig_dbm - noise_dbm) if noise_dbm is not None else None
    # Parse rates list — accept "1 2 5.5 11 54" or ["54","48",...] etc.
    if rates:
        if isinstance(rates, str):
            rate_vals = re.findall(r'[\d.]+', rates)
        else:
            rate_vals = [str(r) for r in rates]
        try:
            rate_floats = sorted([float(x) for x in rate_vals], reverse=True)
            max_rate    = rate_floats[0] if rate_floats else None
            rates_str   = ', '.join(str(int(r) if r==int(r) else r) for r in rate_floats[:8])
        except:
            max_rate, rates_str = None, '—'
    else:
        max_rate, rates_str = None, '—'
    angle, dist = stable_pos(bssid)
    return {
        'ssid':       str(ssid).strip() or '<hidden>',
        'bssid':      bssid,
        'vendor':     lookup_vendor(bssid),
        'signal_pct': sig_pct,
        'signal_dbm': sig_dbm,
        'noise_dbm':  noise_dbm,
        'snr':        snr,
        'channel':    channel,
        'security':   norm_sec(security),
        'cipher':     cipher if cipher else '—',
        'radio_type': norm_radio(radio_type),
        'net_type':   net_type if net_type else 'Infrastructure',
        'rates':      rates_str,
        'max_rate':   max_rate,
        'band':       '6GHz' if channel > 180 else '5GHz' if channel > 14 else '2.4GHz',
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
        auth_m   = re.search(r'(?i)authentication\s*:\s*(.+)', ssid_block)
        cipher_m = re.search(r'(?i)encryption\s*:\s*(.+)',     ssid_block)
        radio_m  = re.search(r'(?i)radio\s+type\s*:\s*(.+)',   ssid_block)
        ntype_m  = re.search(r'(?i)network\s+type\s*:\s*(.+)', ssid_block)
        sec      = auth_m.group(1).strip()   if auth_m   else 'WPA2-Personal'
        cipher   = cipher_m.group(1).strip() if cipher_m else '—'
        radio    = radio_m.group(1).strip()  if radio_m  else '—'
        net_type = ntype_m.group(1).strip()  if ntype_m  else 'Infrastructure'
        bssid_parts = re.split(
            r'\n\s*BSSID\s+\d+\s*:\s*([0-9A-Fa-f]{2}(?:[:\-][0-9A-Fa-f]{2}){5})',
            '\n'+ssid_block
        )
        if len(bssid_parts) < 3:
            all_macs = re.findall(r'([0-9A-Fa-f]{2}(?:[:\-][0-9A-Fa-f]{2}){5})', ssid_block)
            all_sigs = re.findall(r'(?i)signal\s*:\s*(\d+)\s*%', ssid_block)
            all_chs  = re.findall(r'(?i)channel\s*:\s*(\d+)', ssid_block)
            br_m     = re.search(r'(?i)basic\s+rates.*?:\s*(.+)',  ssid_block)
            or_m     = re.search(r'(?i)other\s+rates.*?:\s*(.+)',  ssid_block)
            rates    = (br_m.group(1) if br_m else '') + ' ' + (or_m.group(1) if or_m else '')
            for j, mac in enumerate(all_macs):
                nets.append(make_ap(ssid, mac.replace('-',':'),
                                    int(all_sigs[j]) if j<len(all_sigs) else 50,
                                    None, int(all_chs[j]) if j<len(all_chs) else 6,
                                    sec, radio, None, cipher, net_type, rates.strip() or None))
            continue
        j = 1
        while j+1 < len(bssid_parts):
            mac      = bssid_parts[j].strip().replace('-',':')
            subblock = bssid_parts[j+1]
            j += 2
            sig_m  = re.search(r'(?i)signal\s*:\s*(\d+)\s*%', subblock)
            ch_m   = re.search(r'(?i)channel\s*:\s*(\d+)',     subblock)
            br_m   = re.search(r'(?i)basic\s+rates.*?:\s*(.+)',  subblock)
            or_m   = re.search(r'(?i)other\s+rates.*?:\s*(.+)',  subblock)
            rates  = (br_m.group(1) if br_m else '') + ' ' + (or_m.group(1) if or_m else '')
            nets.append(make_ap(ssid, mac,
                                int(sig_m.group(1)) if sig_m else 50,
                                None, int(ch_m.group(1)) if ch_m else 6,
                                sec, radio, None, cipher, net_type, rates.strip() or None))
    if nets: return nets, raw, f"netsh({len(nets)})"

    # Fallback state machine
    cur_ssid,cur_sec,cur_mac,cur_sig,cur_ch = '<hidden>','WPA2-Personal',None,50,6
    cur_radio,cur_cipher,cur_ntype,cur_rates = '—','—','Infrastructure',''
    def commit():
        if cur_mac: nets.append(make_ap(cur_ssid,cur_mac,cur_sig,None,cur_ch,cur_sec,
                                        cur_radio,None,cur_cipher,cur_ntype,
                                        cur_rates.strip() or None))
    for line in txt.split('\n'):
        s = line.strip()
        if not s: continue
        m = re.match(r'^SSID\s+\d+\s*:\s*(.*)$', s, re.I)
        if m and not s.upper().startswith('BSSID'):
            commit(); cur_mac=None; cur_ssid=m.group(1).strip() or '<hidden>'
            cur_sec='WPA2-Personal'; cur_sig=50; cur_ch=6
            cur_radio='—'; cur_cipher='—'; cur_ntype='Infrastructure'; cur_rates=''; continue
        m = re.match(r'^BSSID\s+\d+\s*:\s*(.+)$', s, re.I)
        if m:
            commit()
            mm = re.search(r'([0-9A-Fa-f]{2}(?:[:\-][0-9A-Fa-f]{2}){5})', m.group(1))
            cur_mac = mm.group(1).replace('-',':').upper() if mm else None
            cur_sig=50; cur_ch=6; continue
        m = re.match(r'^(?:authentication|auth)\s*:\s*(.+)$', s, re.I)
        if m: cur_sec=m.group(1).strip(); continue
        m = re.match(r'^encryption\s*:\s*(.+)$', s, re.I)
        if m: cur_cipher=m.group(1).strip(); continue
        m = re.match(r'^radio\s+type\s*:\s*(.+)$', s, re.I)
        if m: cur_radio=m.group(1).strip(); continue
        m = re.match(r'^network\s+type\s*:\s*(.+)$', s, re.I)
        if m: cur_ntype=m.group(1).strip(); continue
        m = re.match(r'^(?:basic|other)\s+rates.*?:\s*(.+)$', s, re.I)
        if m: cur_rates += ' ' + m.group(1); continue
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
        # airport -s columns: SSID  BSSID  RSSI  CHANNEL  HT  CC  SECURITY
        m = re.match(r'\s*(.+?)\s{2,}([0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5})\s+(-\d+)\s+(\S+)\s*(\S*)\s*(\S*)\s*(.*)', line)
        if not m: continue
        ssid    = m.group(1).strip() or '<hidden>'
        bssid   = m.group(2)
        sig_dbm = int(m.group(3))
        ch_raw  = m.group(4)
        ht_flag = m.group(5)   # e.g. Y/N for HT (802.11n)
        sec_raw = m.group(7)
        ch_m    = re.match(r'(\d+)', ch_raw)
        channel = int(ch_m.group(1)) if ch_m else 6
        sec     = 'WPA2' if ('WPA2' in line or 'RSN' in line) else 'WPA' if 'WPA' in line else 'OPEN'
        # Derive radio type from HT flag + channel band
        if ht_flag.upper() == 'Y':
            radio = '802.11n' if channel <= 14 else '802.11ac'
        else:
            radio = '802.11g' if channel <= 14 else '802.11a'
        nets.append(make_ap(ssid, bssid, max(0,min(100,2*(sig_dbm+100))), sig_dbm,
                            channel, sec, radio, None, '—', 'Infrastructure'))
    if not nets:
        try:
            r = subprocess.run(['system_profiler','SPAirPortDataType'], capture_output=True, text=True, timeout=30)
            raw += r.stdout
            for block in re.split(r'\n(?=\s{8}\S)', raw):
                sm=re.match(r'\s+([^\n:]+):',block)
                bm=re.search(r'Network ID\s*:\s*([0-9a-fA-F:]{17})',block)
                gm=re.search(r'Signal / Noise\s*:\s*(-\d+)\s*/\s*(-\d+)',block)
                cm=re.search(r'Channel\s*:\s*(\d+)',block)
                if sm and gm:
                    ssid    = sm.group(1).strip()
                    bssid   = bm.group(1) if bm else hashlib.md5(ssid.encode()).hexdigest()[:17]
                    sig_dbm = int(gm.group(1))
                    noise   = int(gm.group(2)) if gm.lastindex >= 2 else None
                    ch      = int(cm.group(1)) if cm else 6
                    nets.append(make_ap(ssid, bssid, max(0,min(100,2*(sig_dbm+100))),
                                        sig_dbm, ch, 'WPA2', '—', noise, '—', 'Infrastructure'))
        except: pass
    return nets, raw, f"airport({len(nets)})"

# ─────────────────────────────────────────────────────────────────────────────
#  LINUX SCANNER
# ─────────────────────────────────────────────────────────────────────────────

def scan_linux():
    raw, nets = "", []
    try:
        # Request extra fields: MODE=net_type, SIGNAL_RATE for radio hint
        r = subprocess.run(
            ['nmcli','--terse','--fields',
             'SSID,BSSID,SIGNAL,CHAN,SECURITY,RSN-FLAGS,WPA-FLAGS,MODE',
             'dev','wifi','list','--rescan','yes'],
            capture_output=True, text=True, timeout=20)
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
                sec      = parts[4] if len(parts)>4 else 'WPA2'
                rsn_flag = parts[5] if len(parts)>5 else ''
                # Derive cipher from RSN flags
                cipher = 'CCMP' if 'ccmp' in rsn_flag.lower() else \
                         'TKIP' if 'tkip' in rsn_flag.lower() else '—'
                net_type = parts[7].strip() if len(parts)>7 else 'Infrastructure'
                nets.append(make_ap(ssid, bssid, sp, None, ch, sec,
                                    '—', None, cipher, net_type))
            if nets: return nets, raw, f"nmcli({len(nets)})"
    except FileNotFoundError: raw+="\n[nmcli not found]"
    except Exception as e: raw+=f"\n[nmcli: {e}]"
    try:
        r = subprocess.run(['iwlist','scan'], capture_output=True, text=True, timeout=20)
        raw += r.stdout
        for cell in re.split(r'Cell \d+ - ', r.stdout)[1:]:
            sm=re.search(r'ESSID:"([^"]*)"',cell)
            bm=re.search(r'Address: ([0-9A-Fa-f:]{17})',cell)
            gm=re.search(r'Signal level[=:](-?\d+)',cell)
            nm=re.search(r'Noise level[=:](-?\d+)',cell)
            cm=re.search(r'Channel[=:](\d+)',cell)
            em=re.search(r'Encryption key:(on|off)',cell)
            rm=re.search(r'IEEE\s+802\.11(\w+)',cell)
            # Rates: "Bit Rates:54 Mb/s; 48 Mb/s; ..."
            rates_raw = re.findall(r'(\d+(?:\.\d+)?)\s*Mb/s', cell)
            rates = ' '.join(rates_raw) if rates_raw else None
            if not bm: continue
            sig_dbm  = int(gm.group(1)) if gm else -80
            noise    = int(nm.group(1)) if nm else None
            radio    = f'802.11{rm.group(1)}' if rm else '—'
            # Cipher from IE info
            cipher   = 'CCMP' if 'CCMP' in cell else 'TKIP' if 'TKIP' in cell else '—'
            nets.append(make_ap(
                sm.group(1) if sm else '<hidden>', bm.group(1),
                max(0,min(100,2*(sig_dbm+100))), sig_dbm,
                int(cm.group(1)) if cm else 6,
                ('WPA2' if 'WPA2' in cell else 'WPA' if 'WPA' in cell else 'WEP')
                if em and em.group(1)=='on' else 'OPEN',
                radio, noise, cipher, 'Infrastructure', rates))
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
        new  = state['new_bssids'][:]
        state['new_bssids'] = []
        payload = {
            'networks':     state['networks'],
            'last_updated': state['last_updated'],
            'scan_count':   state['scan_count'],
            'os':           state['os'],
            'scanning':     state['scanning'],
            'method':       state['method'],
            'total':        len(state['networks']),
            'new_bssids':   new,
        }
    # Build ETag from scan_count + network count (cheap fingerprint)
    etag = f'"{state["scan_count"]}-{len(state["networks"])}"'
    if_none = request.headers.get('If-None-Match','')
    if if_none == etag and not new:
        return Response(status=304)
    resp = jsonify(payload)
    resp.headers['ETag']          = etag
    resp.headers['Cache-Control'] = 'no-cache'
    return resp

@app.route('/api/export/csv')
def api_export_csv():
    """Download all currently visible networks as a CSV file."""
    with lock:
        nets = state['networks'][:]
    buf = io.StringIO()
    w   = csv.writer(buf)
    w.writerow(['SSID','BSSID','Vendor','Signal_dBm','Signal_%','Noise_dBm','SNR_dB',
                'Channel','Band','Security','Cipher','Radio_Type','Net_Type',
                'Max_Rate_Mbps','Rates_Mbps','Status','First_Seen','Last_Seen'])
    for n in sorted(nets, key=lambda x: -x['signal_pct']):
        w.writerow([
            n['ssid'], n['bssid'], n.get('vendor','Unknown'),
            n['signal_dbm'], n['signal_pct'],
            n.get('noise_dbm','—'), n.get('snr','—'),
            n['channel'], n['band'], n['security'],
            n.get('cipher','—'), n.get('radio_type','—'), n.get('net_type','—'),
            n.get('max_rate','—'), n.get('rates','—'),
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
            snr_str  = f"SNR:{n.get('snr','?'):>3}dB" if n.get('snr') else ''
            rate_str = f"{n.get('max_rate','?')}Mbps" if n.get('max_rate') else ''
            lines.append(f"    {n['ssid']:<26} {n['bssid']}  {n['signal_dbm']:>4}dBm"
                         f"  ch{n['channel']:>3}  {n['security']:<10}  {n.get('radio_type','—'):<14}"
                         f"  {n.get('cipher','—'):<6}  {snr_str:<10}  {rate_str:<10}  {n.get('vendor','?')}")
        lines += ["","  RAW:","─"*60, state['raw_output']]
        return Response('\n'.join(lines), mimetype='text/plain')

@app.route('/api/vendor_cache')
def api_vendor_cache():
    """Show current vendor cache stats and contents."""
    with _vendor_cache_lock:
        data = dict(_vendor_cache)
        pending = list(_vendor_pending)
    lines = [f"Cached entries : {len(data)}",
             f"Pending lookups: {len(pending)}",
             "",
             "── CACHE ──"]
    for k, v in sorted(data.items()):
        lines.append(f"  {k}  →  {v}")
    if pending:
        lines += ["", "── PENDING ──"]
        for k in pending:
            lines.append(f"  {k}  (fetching…)")
    return Response('\n'.join(lines), mimetype='text/plain')

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__=='__main__':
    _load_cache_file()          # restore persisted vendor cache
    print(f"""
╔══════════════════════════════════════════════════╗
║   WiFi MILITARY RADAR  v5 PROD  –  {OS:<13}      ║
╠══════════════════════════════════════════════════╣
║  Radar  →  http://localhost:5000                 ║
║  Export →  http://localhost:5000/api/export/csv  ║
║  Debug  →  http://localhost:5000/api/debug       ║
║  Vendor →  http://localhost:5000/api/vendor_cache║
╚══════════════════════════════════════════════════╝""", flush=True)
    threading.Thread(target=scanner_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
