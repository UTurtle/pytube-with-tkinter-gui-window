import time
from tkinter import *
import tkinter.font as tkFont
from tkinter import Tk
import tkinter.ttk
from tkinter.scrolledtext import ScrolledText
import clipboard
import re
import ast

import threading
import os.path

from pydub import AudioSegment
from pytube import YouTube
from pytube import Playlist
from tkinter import filedialog
from localStoragePy import localStoragePy
from pytube.exceptions import PytubeError
import urllib.request
import xml.etree.ElementTree as et
import ffmpeg

from datetime import datetime


def app():
    # =========================================================
    # before init
    # =========================================================
    root: Tk = Tk()
    root.geometry("1100x550")
    root.title("tkinter with pytube")
    root.resizable(width=False, height=False)

    # Constant
    unknown = "unknown"
    custom_font = 'Segoe ui'

    # Variable
    is_audio = BooleanVar()
    is_play_list = BooleanVar()
    file_path_history = []

    # Album Option Variable
    is_album = BooleanVar()
    set_cover = BooleanVar()
    extract_lyrics_file = BooleanVar()  # TODO: 노래 가사 파일 추출 .lrc

    # Video Option Variable
    extract_subtitle = BooleanVar()  # TODO: 동영상 자막 파일 추출

    # Download Options Variable
    is_space_2_underbar = BooleanVar()
    new_folder_name_option = StringVar()
    modifier_option = StringVar()
    limit_amount_download_at_once = IntVar()
    download_cooltime = IntVar()

    # =========================================================
    # Loading LocalStorageValue
    # =========================================================
    local_storage = localStoragePy('youtube_downloader', 'json')

    # loading file_path_history
    file_path_history = local_storage.getItem('file_path_history')
    if file_path_history is None:
        file_path_history = []
    else:
        file_path_history = ast.literal_eval(file_path_history)

    # loading album options
    album_options = local_storage.getItem('album_options')
    if album_options is None:
        album_options = {
            'is_album': False,
            'set_cover': False,
            'extract_lyrics_file': False,
        }
    else:
        album_options = ast.literal_eval(album_options)

    # loading video options
    video_options = local_storage.getItem('video_options')
    if video_options is None:
        video_options = {
            'extract_subtitle': False,
        }
    else:
        video_options = ast.literal_eval(video_options)

    # loading download options
    download_options = local_storage.getItem('download_options')
    if download_options is None:
        download_options = {
            'limit_amount_download_at_once': 1,
            'download_cooltime': 0,
            'new_folder_name_option': 'None',
            'modifier_option': 'None',
            'is_space_2_underbar': False,
        }
    else:
        download_options = ast.literal_eval(download_options)

    def onClosing():
        """프로그램을 닫았을 때"""
        local_storage.setItem('file_path_history', file_path_history)

        album_options["is_album"] = is_album.get()
        album_options["set_cover"] = set_cover.get()
        album_options["extract_lyrics_file"] = extract_lyrics_file.get()
        local_storage.setItem('album_options', album_options)

        video_options["extract_subtitle"] = extract_subtitle.get()
        local_storage.setItem('video_options', video_options)

        download_options["limit_amount_download_at_once"] = int(limit_amount_download_at_once.get())
        download_options["download_cooltime"] = int(download_cooltime.get())
        download_options["new_folder_name_option"] = str(new_folder_name_option.get())
        download_options["modifier_option"] = str(modifier_option.get())
        download_options["is_space_2_underbar"] = is_space_2_underbar.get()
        local_storage.setItem('download_options', download_options)

        root.destroy()

    # tabbar
    tabbar = tkinter.ttk.Notebook(root, width=600, height=370)
    tabbar.place(x=0, y=170)

    # =========================================================
    # functions
    # =========================================================
    def info(text, level="DEBUG"):
        """
        debug 전용 함수

        :param text: str
        :param level: "INFO", "DEBUG", "WARNING", "ERROR", "DONE"
        """
        now = datetime.now()
        nowTime = now.strftime('%H:%M:%S')
        logger_box.configure(state='normal')
        logger_box.insert(END, "[{}] {}\n".format(nowTime, text), level)
        logger_box.configure(state='disabled')
        logger_box.see(END)
        print(text)

    def singleDownloadCommand():
        """하나의 추소를 받아서 유튜브 파일 다운로드"""
        url = youtube_link_entry.get()

        if is_play_list.get():
            p = Playlist(url)
            info(f"총 {len(p)}개의 영상을 다운받습니다.", level="INFO")
            for yt in p.videos:
                yt.playlist_title = p.title
                downloadYouTube(yt)
        else:
            yt = YouTube(url)
            downloadYouTube(yt)

    def multipleDownloadCommand():
        """여러 개의 주소를 받아서 유튜브 파일 다운로드"""
        text = youtube_links_input_area.get("1.0", 'end-1c')
        urls = urlFilter(text)
        info(f"총 {len(urls)}개의 URL을 확인했습니다.")
        for url in urls:
            if is_play_list.get():
                p = Playlist(url)
                info(f"{p.title}에서 총 {len(p)}개의 영상을 다운받습니다.", level="INFO")
                for yt in p.videos:
                    yt.playlist_title = p.title
                    downloadYouTube(yt)
            else:
                yt = YouTube(url)
                downloadYouTube(yt)

    def downloadYouTube(yt):
        """유튜브 파일 다운로드"""

        def getName(option, tag=None) -> str:
            """
            옵션에 해당하는 이름을 가져옴
            :param option: str
            :param tag: str 'Artist', 'Album', ‘Song’,
            """
            try:
                options_dict = {
                    'None': unknown,
                    'PlayList': yt.playlist_title if is_play_list.get() else unknown,
                    'Author': yt.author if yt.author else unknown,
                    'MetaData': yt.metadata[0][tag] if tag else unknown,
                }
                name = options_dict.get(option)
            except KeyError:
                name = option
            except IndexError:
                name = unknown
            return name

        def getMetaData() -> dict[str, str]:
            metadata = {
                'artist': getName('MetaData', tag='Artist'),
                'album': getName('MetaData', tag='Artist'),
                'title': getName('MetaData', tag='Song')
            }

            metadata['artist'] = metadata['artist'] if not unknown else yt.author
            metadata['title'] = metadata['title'] if not unknown else yt.title

            if is_play_list.get():
                metadata['album'] = metadata['album'] if not unknown else yt.playlist_title
            else:
                metadata['album'] = metadata['album'] if not unknown else ""

            return metadata

        def getDownloadPath4YT():
            """다운로드 경로 구하기"""
            yt.download_path = file_save_path_combobox.get()
            addFilePathHistiory(yt.download_path)

            option = new_folder_name_option.get()
            name = getName(option)
            if name != unknown:
                yt.download_path = f"{yt.download_path}/{name}"
            return yt

        def setModifier4YT():
            """파일 이름에 수식어 붙히기"""
            option = modifier_option.get()
            name = getName(option)
            if name != unknown:
                yt.title = f"{yt.title}/{name}"
            return yt

        def space2Underbar4YT():
            """공백을 언더바(_)로"""
            if is_space_2_underbar.get():
                yt.title = yt.title.replace(" ", "_")

        def videoDownload():
            """비디오 다운로드 (mp4)"""

            def extractSubtitle():
                """확장자가 .smi인 파일을 추출"""

                caption = yt.captions['ko']
                if caption is None:
                    caption = yt.captions['en']
                    if caption is None:
                        info(f"{yt.title}는 한글(또는 영어) 자막이 없습니다!")
                        return -1

                f = open(f"{yt.download_path}/{yt.title}.smi", "w", encoding="UTF-8")
                f.write("<SAMI>\n<BODY>\n")

                caption_xml = caption.xml_captions  # string 형식의 xml포멧 자막 파일 다운
                xml_root = et.fromstring(caption_xml)  # string 형식을 xml로 파싱
                xml_body = xml_root.find("body")
                tags = xml_body.findall("p")
                for tag in tags:
                    attr = tag.attrib
                    ms = attr.get("t")
                    if ms is False:
                        continue
                    str = tag.text
                    str = ' '.join(str.split())
                    tmp = f'\n<SYNC Start = {ms}>\n{str}<br>\n\n'
                    f.write(f"{tmp}")
                f.write("\n</BODY>\n</SAMI>")
                f.close()

            sema.acquire()
            info(f"{yt.title}을(를) 다운받습니다. \n길이는 {hourMinuteSecond(yt.length)} 입니다.", level="INFO")

            # 파일 스트리밍
            try:
                streams = yt.streams
                video = streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            except PytubeError as e:
                info(f"{yt.title}은(는) [[{e}]]라는 이유로 다운받을 수 없습니다!", level="ERROR")
                return -1

            try:
                video.download(f"{yt.download_path}")
                info(f"{yt.title}를 다운로드 했습니다!\n\n")
            except FileExistsError:
                print(f"이미 {yt.title}이(가) 있습니다!")

            # 추가 옵션
            if extract_subtitle.get():
                extractSubtitle()  # 가사 추출

            time.sleep(int(download_cooltime.get()))
            sema.release()

        def audioDownload():
            """노래 다운로드 (mp3)"""

            def extractLyricsFile():
                """확장자가 .lrc인 파일을 가져옴"""

                caption = yt.captions['ko']
                if caption is None:
                    caption = yt.captions['en']
                    if caption is None:
                        info(f"{yt.title}는 한글(또는 영어) 자막이 없습니다!", level="WARNING")
                        return -1

                f = open(f"{yt.download_path}/{yt.title}.lrc", "w", encoding="UTF-8")

                metadata = getMetaData()

                id_tags = f"""
[ar:{metadata.get('artist')}]
[al:{metadata.get('album')}]
[ti:{metadata.get('title')}]
[length:{yt.length}]
[by:Simple Youtube Downloader]

"""
                f.write(id_tags)
                caption_xml = caption.xml_captions  # string 형식의 xml포멧 자막 파일 다운

                xml_root = et.fromstring(caption_xml)  # string 형식을 xml로 파싱
                xml_body = xml_root.find("body")
                tags = xml_body.findall("p")
                for tag in tags:
                    attr = tag.attrib
                    ms = attr.get("t")
                    if ms is False:
                        continue
                    timing_tag = getTimingTag(int(ms))
                    str = tag.text
                    str = ' '.join(str.split())
                    f.write(f"{timing_tag} {str}\n")
                f.close()

            def convertMp4Mp3():
                base, ext = os.path.splitext(downloaded_file)
                try:
                    info(f"{yt.title}를 mp4에서 mp3로 변환을 시작합니다!\n", level="INFO")
                    video_file = ffmpeg.input(f"{base}.mp4")
                    audio_file = video_file.audio
                    stream = ffmpeg.output(audio_file, f"{base}.mp3")
                    ffmpeg.run(stream)  # 파일 출력
                    if os.path.isfile(f"{base}.mp4"):
                        os.remove(f"{base}.mp4")
                    info(f"{yt.title}을(를) mp4에서 mp3로 변환했습니다!\n\n", level="DONE")
                except:
                    info(f"{yt.title}의 변환에 실패했습니다! ffmpeg 가 설치되어 있는지 확인해주세요!\n\n", level="ERROR")
                    return -1

            def addAttributeMp3():  # TODO: 앨범 설정 추가
                """mp3에 속성 추가"""
                base, ext = os.path.splitext(downloaded_file)
                audio_file = base + '.mp3'
                mp3_thumbnail_path = base + '.jpg'
                try:
                    urllib.request.urlretrieve(yt.thumbnail_url, mp3_thumbnail_path)
                    metadata = getMetaData()
                    sound = AudioSegment.from_mp3(audio_file)
                    file_handle = sound.export(audio_file,
                                               format="mp3",
                                               tags={
                                                   "album": f"{metadata.get('album')}",
                                                   "artist": f"{metadata.get('artist')}"
                                               },
                                               cover=mp3_thumbnail_path)
                    info(f"{yt.title}의 속성 추가를 완료했습니다!\n\n", level="DONE")
                    if os.path.isfile(mp3_thumbnail_path):
                        os.remove(mp3_thumbnail_path)
                except Exception:
                    info(f"{yt.title}의 속성 추가를 실패했습니다!", level="WARNING")

            def replaceMp4Mp3():
                """mp4 -> mp3로 확장자 변경"""
                base, ext = os.path.splitext(downloaded_file)
                audio_file = base + '.mp3'
                try:
                    os.rename(downloaded_file, audio_file)
                except FileExistsError:
                    info(f"이미 {yt.title}이(가) 있습니다!", level="WARNING")

            sema.acquire()
            info(f"{yt.title}을(를) 다운받습니다. \n길이는 {hourMinuteSecond(yt.length)} 입니다.", level="INFO")

            # 파일 스트리밍
            try:
                streams = yt.streams
                audio = streams.filter(only_audio=True, file_extension='mp4').order_by('abr').desc().first()
            except PytubeError as e:
                info(f"{yt.title}은(는) [[{e}]]라는 이유로 다운받을 수 없습니다!", level="ERROR")
                return -1

            # 반드시 str을 이걸로 받아와야함.
            # f"{yt.download_path}/{yt.title}"은 보기에는 같을지언정 Win은 다르게 판정하여
            # 파일을 못 찾아서 절대로 확장자를 바꾸지 못함.
            try:
                downloaded_file = audio.download(f"{yt.download_path}")
                info(f"{yt.title}을(를) 다운로드 했습니다!\n\n", level="DONE")
            except FileExistsError:
                info(f"이미 {yt.title}이(가) 있습니다!", level="WARNING")

            # 추가 옵션
            if is_album.get():
                convertMp4Mp3()  # 투르 컨버트
                addAttributeMp3()  # 앨범 설정
            else:
                replaceMp4Mp3()  # 확장자만 변경

            if extract_lyrics_file.get():
                extractLyricsFile()  # 가사 추출

            time.sleep(int(download_cooltime.get()))
            sema.release()

        try:  # 도중에 오류가 나면 이 파일을 다운 받을 수 없음
            yt.check_availability()  # 사용 가능한가?
            getDownloadPath4YT()  # 다운로드 경로 구하기"
            setModifier4YT()  # 파일 이름에 수식어 붙히기"
            space2Underbar4YT()  # 공백을 언더바(_)로
        except PytubeError as e:
            info(f"{yt.watch_url}은(는) [[{e}]]라는 오류 때문에 다운받을 수 없습니다!!", level="ERROR")
            return -1

        createDirectory(yt.download_path)

        if is_audio.get():
            t = threading.Thread(target=audioDownload)
            t.start()
        else:
            t = threading.Thread(target=videoDownload)
            t.start()

    def createDirectory(path):
        """디렉토리가 없다면 새로 만든다."""
        if not os.path.isdir(path):
            os.makedirs(path)

    def getTimingTag(millisecond) -> str:
        mm = millisecond // (1000 * 60)
        ss = (millisecond % (1000 * 60)) // 1000
        xx = (millisecond % (1000 * 60)) % 1000
        xx = str(xx)
        xx = xx[:2]
        timing_tag = '[{:02d}:{:02d}:{:02s}]'.format(mm, ss, xx)
        return timing_tag

    def hourMinuteSecond(second):
        """초를 시:분:초로 바꿈"""
        hour = second // 3600
        min = (second % 3600) // 60
        sec = (second % 3600) % 60
        hour_min_sec = '[{:02d}:{:02d}:{:02d}]'.format(hour, min, sec)
        return hour_min_sec

    def openFolder():
        path = file_save_path_combobox.get()
        os.startfile(path)

    def urlFilter(text):
        re_pattern = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$\-@\.&+:/?=_]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        results = re.findall(re_pattern, text)
        info(f'다음의 링크들이 발견되었습니다 : {results}')
        return results

    def browseFolder():
        path = filedialog.askdirectory(initialdir="/", title="Select a Folder")
        file_save_path_combobox.delete(0, END)
        file_save_path_combobox.insert(0, path)
        addFilePathHistiory(path)

    def addFilePathHistiory(history):
        if history in file_path_history:
            return
        else:
            file_path_history.append(history)

    def pasteURL4Entry(entry):
        result = clipboard.paste()
        entry.delete(0, END)
        entry.insert(0, result)

    def pasteURL4Text(text):
        result = clipboard.paste()
        text.delete(1.0, END)
        text.insert(1.0, result)

    def deleteSettingAndHistory():
        file_path_history.clear()
        local_storage.clear()

    # =========================================================
    # root, logger
    # =========================================================
    title_label = Label(root)
    title_label["anchor"] = "center"
    ft = tkFont.Font(family=custom_font, size=22, weight='bold')
    title_label["font"] = ft
    title_label["justify"] = "center"
    title_label["text"] = "Simple Youtube Downloader"
    title_label["relief"] = "flat"
    title_label.place(x=0, y=0, width=600, height=50)

    file_save_path_label = Label(root)
    ft = tkFont.Font(family=custom_font, size=10)
    file_save_path_label["font"] = ft
    file_save_path_label["justify"] = "left"
    file_save_path_label["text"] = "File Save Path"
    file_save_path_label.place(x=60, y=50, width=480, height=25)

    file_explore_button = Button(root)
    file_explore_button["text"] = "Browse Folder"
    file_explore_button["command"] = browseFolder
    file_explore_button.place(x=50, y=80, width=100, height=30)

    file_save_path_combobox = tkinter.ttk.Combobox(root)
    ft = tkFont.Font(family=custom_font, size=12)
    file_save_path_combobox["font"] = ft
    file_save_path_combobox["justify"] = "left"
    file_save_path_combobox["text"] = "File Save Path"
    file_save_path_combobox["values"] = file_path_history
    file_save_path_combobox.place(x=170, y=80, width=380, height=30)
    try:
        file_save_path_combobox.insert(0, file_path_history[-1])
    except:
        pass

    # logger_box
    logger_box = ScrolledText(root, state='disabled', height=12)
    logger_box.place(x=600, y=0, width=500, height=550)

    ft = tkFont.Font(size=12)
    ft_done = tkFont.Font(size=12, weight="bold")
    ft_error = tkFont.Font(size=12, weight="bold")
    logger_box.configure(font=ft)
    logger_box.tag_config('INFO', foreground='black')
    logger_box.tag_config('DEBUG', foreground='gray')
    logger_box.tag_config('WARNING', foreground='#b18460')
    logger_box.tag_config('ERROR', foreground='#e93b18', font=ft_error)
    logger_box.tag_config('DONE', foreground='#376518', font=ft_done)

    # =========================================================
    # 1 page single_download_page
    # =========================================================
    single_download_page = tkinter.Frame(root)
    tabbar.add(single_download_page, text="Single Downloader")

    youtube_link_label = Label(single_download_page)
    ft = tkFont.Font(family=custom_font, size=10)
    youtube_link_label["font"] = ft
    youtube_link_label["justify"] = "left"
    youtube_link_label["text"] = "Youtube Link를 넣어주세요 (is_play_list를 체크하면 재생목록을 다운받습니다.)"
    youtube_link_label.place(x=60, y=10, width=480, height=25)

    youtube_link_entry = Entry(single_download_page)
    youtube_link_entry["borderwidth"] = "1px"
    ft = tkFont.Font(family=custom_font, size=12)
    youtube_link_entry["font"] = ft
    youtube_link_entry["justify"] = "left"
    youtube_link_entry["text"] = "Youtube Link"
    youtube_link_entry.place(x=50, y=100, width=500, height=30)

    youtube_link_entry_url_paste_button = Button(single_download_page)
    youtube_link_entry_url_paste_button["anchor"] = "center"
    youtube_link_entry_url_paste_button["bg"] = "#efefef"
    ft = tkFont.Font(family=custom_font, size=10)
    youtube_link_entry_url_paste_button["font"] = ft
    youtube_link_entry_url_paste_button["justify"] = "center"
    youtube_link_entry_url_paste_button["text"] = "Paste URL"
    youtube_link_entry_url_paste_button.place(x=250, y=210, width=100, height=25)
    youtube_link_entry_url_paste_button["command"] = lambda: pasteURL4Entry(youtube_link_entry)

    # repeat
    is_audio_checkbutton = Checkbutton(single_download_page)
    is_audio_checkbutton["anchor"] = "w"
    ft = tkFont.Font(family=custom_font, size=10)
    is_audio_checkbutton["font"] = ft
    is_audio_checkbutton["justify"] = "left"
    is_audio_checkbutton["text"] = " is_audio?"
    is_audio_checkbutton.place(x=60, y=250, width=85, height=25)
    is_audio_checkbutton["variable"] = is_audio

    is_playlist_checkbutton = Checkbutton(single_download_page)
    is_playlist_checkbutton["anchor"] = "w"
    ft = tkFont.Font(family=custom_font, size=10)
    is_playlist_checkbutton["font"] = ft
    is_playlist_checkbutton["justify"] = "left"
    is_playlist_checkbutton["text"] = " is_play_list?"
    is_playlist_checkbutton.place(x=150, y=250, width=125, height=25)
    is_playlist_checkbutton["variable"] = is_play_list

    open_folder_button = Button(single_download_page)
    open_folder_button["bg"] = "#efefef"
    ft = tkFont.Font(family=custom_font, size=10)
    open_folder_button["font"] = ft
    open_folder_button["justify"] = "center"
    open_folder_button["text"] = "Open Folder"
    open_folder_button.place(x=50, y=300, width=100, height=25)
    open_folder_button["command"] = openFolder

    single_download_button = Button(single_download_page)
    single_download_button["anchor"] = "center"
    single_download_button["bg"] = "#efefef"
    ft = tkFont.Font(family=custom_font, size=10, weight="bold")
    single_download_button["font"] = ft
    single_download_button["justify"] = "center"
    single_download_button["text"] = "Download!"
    single_download_button.place(x=450, y=300, width=100, height=25)
    single_download_button["command"] = singleDownloadCommand

    # =========================================================
    # 2 page multiple_download_page
    # =========================================================
    multiple_download_page = tkinter.Frame(root)
    tabbar.add(multiple_download_page, text="Multiple Downloader")

    youtube_link_label = Label(multiple_download_page)
    ft = tkFont.Font(family=custom_font, size=10)
    youtube_link_label["font"] = ft
    youtube_link_label["justify"] = "left"
    youtube_link_label["text"] = "유튜브 링크를 한줄씩 입력해 주세요"
    youtube_link_label.place(x=60, y=10, width=480, height=25)

    youtube_links_input_area = Text(multiple_download_page)
    youtube_links_input_area["borderwidth"] = "1px"
    ft = tkFont.Font(family=custom_font, size=12)
    youtube_links_input_area["font"] = ft
    youtube_links_input_area.place(x=50, y=40, width=500, height=150)

    youtube_links_input_area_paste_url_button = Button(multiple_download_page)
    youtube_links_input_area_paste_url_button["anchor"] = "center"
    youtube_links_input_area_paste_url_button["bg"] = "#efefef"
    ft = tkFont.Font(family=custom_font, size=10)
    youtube_links_input_area_paste_url_button["font"] = ft
    youtube_links_input_area_paste_url_button["justify"] = "center"
    youtube_links_input_area_paste_url_button["text"] = "Paste URL"
    youtube_links_input_area_paste_url_button.place(x=250, y=210, width=100, height=25)
    youtube_links_input_area_paste_url_button["command"] = lambda: pasteURL4Text(youtube_links_input_area)

    # repeat
    is_audio_check_button = Checkbutton(multiple_download_page)
    is_audio_check_button["anchor"] = "w"
    ft = tkFont.Font(family=custom_font, size=10)
    is_audio_check_button["font"] = ft
    is_audio_check_button["justify"] = "left"
    is_audio_check_button["text"] = " is_audio?"
    is_audio_check_button["relief"] = "flat"
    is_audio_check_button.place(x=60, y=250, width=85, height=25)
    is_audio_check_button["variable"] = is_audio

    is_playlist_check_button = Checkbutton(multiple_download_page)
    is_playlist_check_button["anchor"] = "w"
    ft = tkFont.Font(family=custom_font, size=10)
    is_playlist_check_button["font"] = ft
    is_playlist_check_button["justify"] = "left"
    is_playlist_check_button["text"] = " is_play_list?"
    is_playlist_check_button["relief"] = "flat"
    is_playlist_check_button.place(x=150, y=250, width=125, height=25)
    is_playlist_check_button["variable"] = is_play_list

    open_folder_button = Button(multiple_download_page)
    open_folder_button["bg"] = "#efefef"
    ft = tkFont.Font(family=custom_font, size=10)
    open_folder_button["font"] = ft
    open_folder_button["justify"] = "center"
    open_folder_button["text"] = "Open Folder"
    open_folder_button.place(x=50, y=300, width=100, height=25)
    open_folder_button["command"] = openFolder

    multiple_download_button = Button(multiple_download_page)
    multiple_download_button["anchor"] = "center"
    multiple_download_button["bg"] = "#efefef"
    ft = tkFont.Font(family=custom_font, size=10, weight="bold")
    multiple_download_button["font"] = ft
    multiple_download_button["justify"] = "center"
    multiple_download_button["text"] = "Download!"
    multiple_download_button.place(x=450, y=300, width=100, height=25)
    multiple_download_button["command"] = multipleDownloadCommand

    # =========================================================
    # 3 page album option
    # =========================================================
    album_options_page = tkinter.Frame(root)
    tabbar.add(album_options_page, text="Album Option")

    # Label
    artist_name_option_label = Label(album_options_page, text="아티스트의 이름을 정합니다.")
    album_name_option_label = Label(album_options_page, text="앨범의 이름을 정합니다.")

    # Checkbox
    is_album_checkbutton = Checkbutton(album_options_page,
                                       text="앨범 속성을 추가합니까? [ffmpeg가 설치되어 있어야함.]",
                                       variable=is_album)
    set_cover_checkbutton = Checkbutton(album_options_page,
                                        text="썸네일을 노래 커버로 사용합니까? [ffmpeg가 설치되어 있어야함.]",
                                        variable=set_cover)
    extract_lyrics_file_checkbutton = Checkbutton(album_options_page,
                                                  text="만약 가사가 있다면 가사파일(.lrc)을 추출합니까?",
                                                  variable=extract_lyrics_file)

    # Layout
    Label(album_options_page).pack(anchor="w", padx="50", pady="10")
    is_album_checkbutton.pack(anchor="w", padx="50", pady="3")
    set_cover_checkbutton.pack(anchor="w", padx="50", pady="3")
    extract_lyrics_file_checkbutton.pack(anchor="w", padx="50", pady="3")
    Label(album_options_page, text="이 옵션을 사용한다면 cmd창이 계속 껏다 켜졌다 할 수 있지만\n 파일 변환 및 속성 추가를 하는 것이므로 너무 놀라지 마세요.").pack(anchor="w", padx="50", pady="10")

    # Init Combobox Value
    is_album.set(album_options["is_album"])
    set_cover.set(album_options["set_cover"])
    extract_lyrics_file.set(album_options["extract_lyrics_file"])

    # =========================================================
    # 4 page video options
    # =========================================================
    video_options_page = tkinter.Frame(root)
    tabbar.add(video_options_page, text="Video Option")

    # Entry
    extract_subtitle_checkbutton = Checkbutton(video_options_page,
                                                  text="영상의 자막을 추출합니다.",
                                                  variable=extract_subtitle)
    # Layout
    Label(video_options_page, text="해상도가 높은 순으로 다운받습니다. (이 설정은 바꿀 수 없습니다.)").pack(anchor="w", padx="50", pady="10")
    extract_subtitle_checkbutton.pack(anchor="w", padx="50", pady="3")

    # Init Entry Value
    extract_subtitle.set(video_options["extract_subtitle"])

    # =========================================================
    # 5 page download options
    # =========================================================
    download_options_page = tkinter.Frame(root)
    tabbar.add(download_options_page, text="Download Option")

    # Label
    limit_amount_download_at_once_label = Label(download_options_page, text="한번에 얼마나 다운받을 것인가?")
    download_cooltime_label = Label(download_options_page, text="한번 다운받은 뒤 얼마나 기다렸다가 다운받을것인가? (단위는 초(s))")
    new_folder_name_option_label = Label(download_options_page, text="다음에 해당하는 이름으로 폴더를 생성해 다운받습니다.")
    modifier_option_label = Label(download_options_page, text="파일 이름에 붙힐 수식어")

    # Entry
    is_space_2_underbar_checkbutton = Checkbutton(download_options_page,
                                                  text="공백을 밑줄로 바꿉니다.",
                                                  variable=is_space_2_underbar)
    limit_amount_download_at_once_combobox = tkinter.ttk.Combobox(download_options_page,
                                                                  values=[i for i in range(1, 101)],
                                                                  state="readonly",
                                                                  textvariable=limit_amount_download_at_once)
    download_cooltime_combobox = tkinter.ttk.Combobox(download_options_page,
                                                      values=[i for i in range(0, 101)],
                                                      state="readonly",
                                                      textvariable=download_cooltime)
    new_folder_name_option_combobox = tkinter.ttk.Combobox(download_options_page,
                                                           values=['None', 'Playlist', 'Author'],
                                                           textvariable=new_folder_name_option)
    modifier_option_combobox = tkinter.ttk.Combobox(download_options_page,
                                                    values=['None', 'Playlist', 'Author'],
                                                    textvariable=modifier_option)

    # Button
    delete_setting_and_history = Button(download_options_page, text="Delete Setting And Path History")
    delete_setting_and_history["command"] = deleteSettingAndHistory

    # Layout
    Label(download_options_page).pack(anchor="w", padx="50", pady="10")
    is_space_2_underbar_checkbutton.pack(anchor="w", padx="50", pady="3")
    limit_amount_download_at_once_label.pack(anchor="w", padx="50", pady="3")
    limit_amount_download_at_once_combobox.pack(anchor="w", padx="50", pady="3")
    download_cooltime_label.pack(anchor="w", padx="50", pady="3")
    download_cooltime_combobox.pack(anchor="w", padx="50", pady="3")
    new_folder_name_option_label.pack(anchor="w", padx="50", pady="3")
    new_folder_name_option_combobox.pack(anchor="w", padx="50", pady="3")
    modifier_option_label.pack(anchor="w", padx="50", pady="3")
    modifier_option_combobox.pack(anchor="w", padx="50", pady="3")
    delete_setting_and_history.pack(anchor="w", padx="50", pady="3")

    # Init Entry Value
    is_space_2_underbar.set(download_options["is_space_2_underbar"])
    limit_amount_download_at_once_combobox.set(download_options["limit_amount_download_at_once"])
    download_cooltime_combobox.set(download_options["download_cooltime"])
    new_folder_name_option_combobox.set(download_options["new_folder_name_option"])
    modifier_option_combobox.set(download_options["modifier_option"])

    # =========================================================
    # after init
    # =========================================================
    sema = threading.Semaphore(int(limit_amount_download_at_once.get()))

    info(f"Loading Complete!")

    root.protocol("WM_DELETE_WINDOW", onClosing)
    root.mainloop()


if __name__ == "__main__":
    app()