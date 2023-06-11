import asyncio
import requests
import re
import os
from bs4 import BeautifulSoup

async def main():
    f = open('list.txt')
    packages = f.read().splitlines()
    f.close()
    
    os.mkdir('srpm')
    failed = []
    for package in packages:
        # get package
        response = requests.get(f'https://openkoji.iscas.ac.cn/koji/search?match=glob&type=package&terms={package}', verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        allbuild = soup.find_all('a', string=re.compile('.+\.fc38$'))
        if len(allbuild) == 0:
            print(f'No builds for package {package}')
            continue
        
        # if there is already a noarch package
        response = requests.get('https://openkoji.iscas.ac.cn/koji/' + allbuild[0]['href'], verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.find('th', string='noarch'):
            continue

        # get latest build
        srpm = soup.find('a', string='download', href=re.compile('.+\.src\.rpm$'))
        if srpm is None:
            print(f'No srpm for package {package}')
            failed += package
            continue
        link = srpm['href']
        
        # download
        os.system(f'curl -o srpm/{package}.src.rpm {link}')
    
    f = open('failed.txt', 'w')
    f.write('\n'.join(failed))
    f.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())