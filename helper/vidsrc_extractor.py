import os
import re
import gzip
import base64
import requests

from io import BytesIO
from typing import Optional
from bs4 import BeautifulSoup

class VidSrcExtractor:
    def hunter_def(self, d, e, f) -> int:
        '''Used by self.hunter'''
        g = list("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/")
        h = g[0:e]
        i = g[0:f]
        d = list(d)[::-1]
        j = 0
        for c,b in enumerate(d):
            if b in h:
                j = j + h.index(b)*e**c
    
        k = ""
        while j > 0:
            k = i[j%f] + k
            j = (j - (j%f))//f
    
        return int(k) or 0
    
    def hunter(self, h, u, n, t, e, r) -> str:
        '''Decodes the common h,u,n,t,e,r packer'''
        r = ""
        i = 0
        while i < len(h):
            j = 0
            s = ""
            while h[i] is not n[e]:
                s = ''.join([s,h[i]])
                i = i + 1
    
            while j < len(n):
                s = s.replace(n[j],str(j))
                j = j + 1
    
            r = ''.join([r,''.join(map(chr, [self.hunter_def(s,e,10) - t]))])
            i = i + 1
    
        return r

    def decode_src(self, encoded, seed) -> str:
        '''decodes hash found @ vidsrc.me embed page'''
        encoded_buffer = bytes.fromhex(encoded)
        decoded = ""
        for i in range(len(encoded_buffer)):
            decoded += chr(encoded_buffer[i] ^ ord(seed[i % len(seed)]))
        return decoded
    
    def decode_base64_url_safe(self, s) -> bytearray:
        standardized_input = s.replace('_', '/').replace('-', '+')
        binary_data = base64.b64decode(standardized_input)

        return bytearray(binary_data)

    def handle_vidsrc_stream(self, url, source) -> str:
        '''Main vidsrc, get urls from here its fast'''
        max_retries = 50  # Set a reasonable maximum number of retries
        attempt = 0

        while attempt < max_retries:
            try:
                req = requests.get(url, headers={"Referer": source})
                hls_url_match = re.search(r'file:"([^"]*)"', req.text)

                if hls_url_match:
                    hls_url = hls_url_match.group(1)
                    hls_url = re.sub(r'\/\/\S+?=', '', hls_url).replace('#2', '')

                    try:
                        hls_url = base64.b64decode(hls_url).decode('utf-8')
                    except Exception: 
                        attempt += 1
                        continue  # Retry on base64 decoding failure

                    # Check if the URL ends with /list.m3u8
                    if hls_url.endswith("/list.m3u8"):
                        set_pass_match = re.search(r'var pass_path = "(.*?)";', req.text)
                        if set_pass_match and set_pass_match.group(1).startswith("//"):
                            set_pass = f"https:{set_pass_match.group(1)}"
                            requests.get(set_pass, headers={"Referer": source})
                        return hls_url

                print("URL match not found or incomplete URL in response, retrying...")
                attempt += 1
            except requests.RequestException as e:
                print(f"Request failed: {e}")
                attempt += 1

        print("Maximum retries reached, unable to retrieve full URL.")
        return None


    
    def handle_2embed(self, url, source) -> str:
        '''Site provides ssl error :( cannot fetch from here''' # this site works now, ill reverse in future
        pass

    def handle_multiembed(self, url, source) -> str:
        '''Fallback site used by vidsrc'''
        req = requests.get(url, headers={"Referer": source})
        matches = re.search(r'escape\(r\)\)}\((.*?)\)', req.text)
        processed_values = []

        if not matches:
            print("[Error] Failed to fetch multiembed, this is likely because of a captcha, try accessing the source below directly and solving the captcha before re-trying.")
            print(url)
            return None

        for val in matches.group(1).split(','):
            val = val.strip()
            if val.isdigit() or (val[0] == '-' and val[1:].isdigit()):
                processed_values.append(int(val))
            elif val[0] == '"' and val[-1] == '"':
                processed_values.append(val[1:-1])

        unpacked = self.hunter(*processed_values)
        hls_url = re.search(r'file:"([^"]*)"', unpacked).group(1)
        return hls_url
    
    def fetch_best_subtitle_url(self, code, language) -> Optional[str]:
        '''This site uses opensubs for fetching subtitles, this is doing the same, fetches the highest score subtitle'''
        if "_" in code:
            code, season_episode = code.split("_")
            season, episode = season_episode.split('x')
            url = f"https://rest.opensubtitles.org/search/episode-{episode}/imdbid-{code}/season-{season}/sublanguageid-{language}"
        else:
            url = f"https://rest.opensubtitles.org/search/imdbid-{code}/sublanguageid-{language}"
        
        headers = {
            'authority': 'rest.opensubtitles.org',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
            'x-user-agent': 'trailers.to-UA',
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            best_subtitle = max(response.json(), key=lambda x: x.get('score', 0), default=None)
            if best_subtitle:
                return best_subtitle.get("SubDownloadLink")
        
        return None

    def get_vidsrc_stream(self, name, media_type, code, language, season=None, episode=None) -> Optional[str]:
        provider = "imdb" if ("tt" in code) else "tmdb"
        url = f"https://vidsrc.me/embed/{media_type}?{provider}={code}"
        if season and episode:
            url += f"&season={season}&episode={episode}"

        print(f"Requesting {url}...")
        req = requests.get(url)
        soup = BeautifulSoup(req.text, "html.parser")
        sources = {attr.text: attr.get("data-hash") for attr in soup.find_all("div", {"class": "server"})}

        source = sources.get(name)
        if not source:
            print(f"No source found for {name}, available sources:", ", ".join(list(sources.keys())))
            return None, None

        req_1 = requests.get(f"https://rcp.vidsrc.me/rcp/{source}", headers={"Referer": url})
        soup = BeautifulSoup(req_1.text, "html.parser")

        encoded = soup.find("div", {"id": "hidden"}).get("data-h")
        seed = soup.find("body").get("data-i")

        decoded_url = self.decode_src(encoded, seed)
        if decoded_url.startswith("//"):
            decoded_url = f"https:{decoded_url}"

        req_2 = requests.get(decoded_url, allow_redirects=False, headers={"Referer": f"https://rcp.vidsrc.me/rcp/{source}"})
        location = req_2.headers.get("Location")
        
        subtitle = None
        if language:
            subtitle = self.fetch_best_subtitle_url(seed, language)

        if "vidsrc.stream" in location:
            return self.handle_vidsrc_stream(location, f"https://rcp.vidsrc.me/rcp/{source}"), subtitle
        if "2embed.cc" in location:
            print("[Warning] 2Embed does not work, this will not return anything!")
            return self.handle_2embed(location, f"https://rcp.vidsrc.me/rcp/{source}"), subtitle
        if "multiembed.mov" in location:
            return self.handle_multiembed(location, f"https://rcp.vidsrc.me/rcp/{source}"), subtitle


if __name__ == "__main__":
    vse = VidSrcExtractor()
    code = input("Input TMDB code for the movie: ")
    stream, subtitle = vse.get_vidsrc_stream("multiembed", "movie", code, "eng")
    print(f"Stream: {stream}")
    print(f"Subtitle: {subtitle}")