# pytube-with-tkinter-gui-
유튜브 프리미엄 이었지만 노래를 다운받지 못한 불쌍한 중생이 만든 것 (그래도 폰 새걸로 바꾸니까 다운받아지긴 하더라.)

---

### 대략 설명

그냥 exe파일 로 다운받고 싶다면?

[pytube-with-tkinter-gui 다운로드](https://github.com/UTurtle/pytube-with-tkinter-gui/releases/)

만약 프로젝트를 다운받아 보고 싶다면?

`git clone https://github.com/UTurtle/pytube-with-tkinter-gui.git`

어짜피 pytube 하나로 다 할 수 있으므로 CUI에 익숙하다면 pytube를 쓰자.

pytube: https://github.com/pytube/pytube

이거 만들면서 사용한 module
- time
- tkinter
- re
- ast
- threading
- os
- 나머지는 import문 참고

이거 만들면서 다운받은 package
- pytube 
- localStoragePy
- clipboard
- pydub
- ffmpeg-python
- pyinstaller
- 나머지는 requirements.txt 참고

대부분 MIT나 apache 라이센스 package를 사용했다고는 생각하지만 혹시 다른곳에 사용할 거라면 
requirements의 라이선스는 확인하자.
(여기에 있는 코드를 사용함으로써 생기는 불이득은 책임져주지 않을것이다.)

requirements.txt를 한번에 다운받는 방법은 밑에 링크 참고
- https://2siwon.github.io/pip/2017/09/25/pip-002-pip-freeze.html


만약 pytube.exceptions.RegexMatchError가 난다면 다음을 시도해 보자.
그래도 안되면 최신버전의 pytube를 설치하거나 issue탭을 자주 확인해보는게 도움이 된다.
- https://github.com/pytube/pytube/issues/1281#issuecomment-1099824478


---

### Window로 사용할 수 있게 exe로 만들기


pyinstaller 사용법은
src 폴더 안에서

`pyinstaller.exe .\__init__.py -F -w --specpath ../output --distpath ../output/dist --workpath ../output/build --name pytube-with-tkinter-gui`

이렇게 명령어를 치면된다.

근대 나는 console창을 보고 싶다 하면?

`pyinstaller.exe .\__init__.py -F --specpath ../output --distpath ../output/dist --workpath ../output/build --name pytube-with-tkinter-gui`

이렇게 -w 하나 빼버리면 된다.
pyinstaller에 대한 자세한 사항은
https://pyinstaller.org/en/stable/usage.html#

---

### ffmpeg

앨범 기능을 사용하려면 설치해야 한다. (기본으로 설치되지 않는다.)

나는 이걸보고 설치했다.
- https://root-blog.tistory.com/3

---

### 이슈 관련

##### HTTP Error 429: Too Many Requests

이것도 3천번~5천번 정도 다운받다 보면 `urllib.error.HTTPError: HTTP Error 429: Too Many Requests` 와 같은 Error가 뜨는데
그건 하도 영상을 다운받으니까 작작 다운받으라는 소리이므로 그럴때는 좀 시간이 지나서 쿨타임 좀 키고 다시 다운받으면 된다.
(아니면 IP를 바꿔도 된다.)

**다른 이슈는 알아서 Fork하거나 Clone해서 해결해주시면 감사하겠습니다.**

(국가의 부름에 의하여 1년 6개월동안 못 돌아오므로 Pull Request도 못볼 가능성이 농후합니다.)

### 참고

GUI 만들 때 도움 받은 곳
- https://softwarerecs.stackexchange.com/questions/32612/gui-drag-drop-style-gui-builder-for-python-tkinter

pytube 사용할 때 도움 받은 곳
- https://m.blog.naver.com/dsz08082/221753467977
- https://pytube.io/en/latest/
