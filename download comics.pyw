#!/usr/bin/python3
# -*-coding:utf-8 -*-

import sys
import getcomics
import htmlsoup
import tools
import requests
import tkinter as tk
import tkinter.scrolledtext as tkst
from tkinter import ttk
import urllib.request
import urllib.error
import threading
import base64
import zpshare

url = ''
BASE = "https://getcomics.info/go.php-url=/"

exit_thread = False
exit_success = False


class Std_redirector(object):
    def __init__(self, widget):
        self.widget = widget

    def write(self, string):
        if not exit_thread:
            self.widget.insert(tk.END, string)
            self.widget.see(tk.END)

    def flush(self):
        pass


# our comicsList
class Getcomics(tk.Tk):

    def __init__(self):
        def myfunction(event):
            dlcanva.configure(
                    scrollregion=dlcanva.bbox("all"), width=200, height=200)
        super().__init__()
        sizex = 800  # largeur
        sizey = 600  # hauteur

        # Gets both half the screen width/height and window width/height
        posx = int(self.winfo_screenwidth()/2 - sizex/2)
        posy = int(self.winfo_screenheight()/2 - sizey/2)

        self.resultwidht = 50
        self.dlwidth = 40
        deepbg = '#263238'
        color1 = '#37474F'
        # color2='#455A64'
        dark2 = '#37474F'
        dark3 = '#455A64'
        fg = 'white'
        style = ttk.Style()
        style.configure("deepBG.TFrame", foreground=fg, background=deepbg,
                        border=0, relief='flat')
        style = ttk.Style()
        style.configure("dark1.TFrame", foreground=fg, background=color1,
                        border=0, relief='flat', highlightthickness=0)
        style = ttk.Style()
        style.configure("L.TLabel", foreground=fg, background=color1,
                        relief='raised', font=("Verdana", 12))
        self.page = 1
        self.currentpercent = tk.IntVar()
        self.percent = tk.IntVar()
        self.dlbytes = tk.IntVar()
        self.currentpercent.set(0)
        self.percent.set(0)
        self.dlbytes.set(0)
        self.maxpercent = 100
        self.listsize = 0
        self.usersearch = tk.StringVar()
        self.choices = ['Recherche par TAG', 'Recherche simple']
        self.mode = tk.StringVar()
        self.mode.set('Recherche simple')
        self.usersearch = tk.StringVar()
        self.buttonlist = list()
        self.searchlist = list()
        self.downloadlist = list()
        self.mylist = list()
        self.wm_geometry("%dx%d+%d+%d" % (sizex, sizey, posx, posy))
        self.title("Télécharger sur Getcomics V2019-02")
        self.configure(background=deepbg)

        topbar = ttk.Frame(self, style="deepBG.TFrame")
        mainframe = ttk.Frame(self, style="deepBG.TFrame")
        self.resultsframe = ttk.Frame(mainframe, style="dark1.TFrame")
        rightframe = ttk.Frame(mainframe, style="dark1.TFrame")
        buttonbar = ttk.Frame(self.resultsframe, style="deepBG.TFrame")

        bottombar = ttk.Frame(self, style="deepBG.TFrame")
        self.prevpage = tk.Button(
                buttonbar, text="page précédente", bg=dark3, fg=fg,
                font=("Verdana", 12), relief='raised', border=2,
                highlightthickness=0, command=self.gotoprevpage)
        nextpage = tk.Button(
                buttonbar, text="page suivante", bg=dark3, fg=fg,
                font=("Verdana", 12), relief='raised', border=2,
                highlightthickness=0, command=self.gotonextpage)
        # messageRecherche = tk.Label(
        #         topbar, text="Rechercher sur Getcomics", bg=dark2, fg=fg,
        #         justify=tk.CENTER, font=("Helvetica", 12))
        choice = tk.OptionMenu(topbar, self.mode, *self.choices)
        choice.config(bg=dark3, fg=fg, relief='flat',
                      border=0, highlightthickness=0)
        choice["menu"].config(bg=dark3, fg=fg, relief='flat', border=0)
        search = tk.Entry(topbar, width=self.resultwidht, justify='center',
                          insertbackground=fg, bg=dark2, fg=fg,
                          textvariable=self.usersearch, font=("Verdana", 12))

        dlcanva = tk.Canvas(rightframe, bg=color1, highlightthickness=0)
        self.dlframe = ttk.Frame(dlcanva, style="dark1.TFrame")
        scrollbar = ttk.Scrollbar(
                dlcanva, orient="vertical", command=dlcanva.yview)
        instructions = ttk.Label(
                self.resultsframe, style="L.TLabel",
                text='Cliquez pour ajouter un élément '\
                     'à votre liste de téléchargement')
        liste = tk.Label(rightframe, width=self.dlwidth, bg=dark2, fg=fg,
                         relief='raised', text="Liste de téléchargement",
                         font=("Verdana", 12))
        dlall = tk.Button(
                rightframe, bg=color1, fg=fg, highlightthickness=0,
                text="Télécharger la liste", font=("Verdana", 12, 'bold'),
                command=lambda: self.dlcom(self.downloadlist))

        outputtext = tkst.ScrolledText(
                bottombar, height=8, bg='black', fg='white', wrap=tk.WORD)
        self.progress = ttk.Progressbar(
                bottombar, orient="horizontal",
                variable=self.currentpercent, mode="determinate")
        self.progress2 = ttk.Progressbar(
                bottombar, orient="horizontal",
                variable=self.percent, mode="determinate")

        topbar.pack(fill='x', anchor='n', padx=20, pady=20)
        mainframe.pack(
                fill='both', expand=1, anchor='nw', padx=20, pady=(0, 5))
        self.resultsframe.pack(
                side='left', anchor='nw', fill='both', expand=1, padx=(0, 20))
        rightframe.pack(side='left', anchor='ne', fill='y', expand=1)
        buttonbar.pack(side='bottom', anchor='sw', fill='x', expand=1)

        nextpage.pack(side='right', padx=(0, 50))
        search.pack(side='left')
        choice.pack(side='right')
        search.focus_set()
        search.bind("<Return>", self.searchcomics)
        instructions.pack(fill='x')
        liste.pack(fill='x')
        dlcanva.pack(fill='both', expand=1)
        scrollbar.pack(side='right', fill='y')
        dlcanva.configure(yscrollcommand=scrollbar.set)
        dlcanva.create_window((0, 0), window=self.dlframe, anchor='nw')
        self.dlframe.bind("<Configure>", myfunction)
        dlall.pack(fill='x', side='bottom')

        bottombar.pack(fill='x')
        self.progress.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)
        self.progress2.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)
        outputtext.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)
        sys.stdout = Std_redirector(outputtext)

        self.searchcomics(None)

    def destroylist(self, widgetlist):
        for w in widgetlist:
            w.destroy()
        widgetlist.clear()
        pass

    # Search comics function
    def searchcomics(self, event):
        dark2 = '#546E7A'
        fg = '#FAFAFA'
        self.searchlist.clear()
        self.destroylist(self.buttonlist)
        searchmode = self.choices.index(self.mode.get())
        self.searchlist = getcomics.getresults(getcomics.searchurl(
                                                        self.usersearch.get(),
                                                        searchmode, self.page))
        # buttonlist = list()
        for i in self.searchlist:
            title = i[1] + ' (' + str(i[2]) + ')'
            newButton = tk.Button(
                    self.resultsframe, text=title, width=self.resultwidht,
                    relief='flat', border=0, bg=dark2, fg=fg,
                    activebackground='#FAFAFA', activeforeground='black',
                    highlightthickness=0, font=("Verdana", 10))
            newButton.config(
                    command=lambda button=newButton: self.addtodl(button))
            newButton.pack(fill='both', expand=1, pady=0)
            self.buttonlist.append(newButton)
        return

    # Download one comic
    def dlcom(self, liste):
        try:
            thread1 = threading.Thread(target=self.downAllCom, args=[liste])
            thread1.start()
        except Exception as e:
            print(e)
            print("Problem")
            pass

    # Click to add to DL list
    def addtodl(self, button):
        dark2 = '#546E7A'
        fg = '#FAFAFA'
        index = self.buttonlist.index(button)
        comic = button.cget('text')
        if comic not in (item[1] for item in self.downloadlist):
            if self.searchlist[index][2] is not None:
                bytes = tools.convert2bytes(self.searchlist[index][2])
                self.listsize += bytes
            newDL = tk.Button(
                    self.dlframe, text=button.cget('text').title(),
                    width=self.resultwidht, anchor='w', bg=dark2, fg=fg,
                    activebackground='#FAFAFA', activeforeground='black',
                    relief='flat', border=0, highlightthickness=0,
                    font=("Verdana", 10))
            newDL.config(command=lambda button=newDL: self.removedl(button))
            newDL.pack(fill='both', expand=1, pady=0)
            self.downloadlist.append((self.searchlist[index][0],
                                      self.searchlist[index][1],
                                      newDL, self.searchlist[index][2]))
            print("Taille de la file d'attente (donnée indicative) : "
                  + tools.bytes_2_human_readable(self.listsize))
        else:
            print("Already in your DL list")

    # Click to remove an item function
    def removedl(self, button):
        for i in self.downloadlist:
            if button == i[2]:
                if i[3] is not None:
                    bytes = tools.convert2bytes(i[3])
                    self.listsize -= bytes
                self.downloadlist.remove(i)
        button.destroy()
        print("Taille de la file d'attente (donnée indicative) : "
              + tools.bytes_2_human_readable(self.listsize))

    # DL all comics in the liste
    def downAllCom(self, liste):
        self.dlbytes.set(0)
        for dl in liste:
            try:
                self.downCom(dl[0])
            except Exception as e:
                print(e)
                print("Something went wrong")
        print("Terminé, vous pouvez quitter")
        return

    # Find download link
    def downCom(self, url):
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        headers = {'User-Agent': user_agent}
        try:
            req = urllib.request.Request(url, None, headers)
            finalurl = urllib.request.urlopen(req).geturl()
        except urllib.error.HTTPError:
            print("downCom got HTTPError from Request")
            raise
        print ("Trying " + finalurl)
        zippylink = ''
        try:
            soup = htmlsoup.url2soup(finalurl)
            downButtons = soup.select("div.aio-pulse > a")
            for button in downButtons:
                # if 'zippyshare' in str(button).lower() \
                #       and 'href' in button.a.attrs:
                if 'zippyshare' in button.get("href") \
                                or 'zippyshare' in button.get('title').lower():
                    zippylink = button.get("href")
                    print(zippylink)
                    try:
                        if str(zippylink).startswith(BASE):
                            print("Abracadabra !")
                            finalzippy = base64.b64decode(
                                                zippylink[len(BASE):]).decode()
                        else:
                            user_agent = 'Mozilla/4.0 '\
                                         '(compatible; MSIE 5.5; Windows NT)'
                            headers = {'User-Agent': user_agent}
                            req = urllib.request.Request(
                                    zippylink, None, headers)
                            finalzippy = urllib.request.urlopen(req).geturl()
                    except urllib.error.HTTPError as e:
                        print("can't obtain final zippyshare url")
                        print(e)
                        raise
                    except IOError:
                        print("Zippyhare download failed")
                    try:
                        print(finalzippy)
                        self.downComZippy(finalzippy)
                    except Exception as e:
                        print(e)
                        print("error in downComZippy")
        except urllib.error.HTTPError as e:
            print("downCom got HTTPError")
            print(e)
            raise
        return

    # Download from zippyshare
    def downComZippy(self, url):
        self.progress["value"] = 0
        soup = htmlsoup.url2soup(url)
        # downButton = soup.select('script[type="text/javascript"]')
        downButton = soup.find('a', id="dlbutton").find_next_sibling().text
        try:
            fullURL, fileName = zpshare.getZippyDL(url, downButton)
            print ("Download from zippyhare into : " + fileName)
            r = requests.get(fullURL, stream=True)
            size = int(r.headers['Content-length'])  # Size in bytes
            print(tools.bytes_2_human_readable(size))
        except Exception as e:
            print(e)
            print("Can't get download link on zippyshare page")

        # Download from url & trim it a little bit
        with open(fileName, 'wb') as f:
            try:
                dl = 0
                if self.listsize == 0:
                    self.listsize = 1
                for block in r.iter_content(51200):
                    dl += len(block)
                    self.currentpercent.set(int(100 * dl / size))
                    self.dlbytes.set(self.dlbytes.get() + len(block))
                    self.percent.set(
                            int(100 * self.dlbytes.get() / self.listsize))
                    f.write(block)
            except KeyboardInterrupt:
                pass
            except IOError:
                print("Error while writing file")
            try:
                r.close()
            except Exception:
                pass
            print ('Done\n--')
        return

    # Nexpage button function
    def gotonextpage(self):
        self.page = self.page + 1
        self.searchcomics(None)
        self.prevpage.pack(side='left', padx=(50, 0))

    # Previous page button function
    def gotoprevpage(self):
        if self.page > 1:
            self.page = self.page - 1
            self.prevpage.pack_forget()
        else:
            self.page = 1
        self.searchcomics(None)


if __name__ == "__main__":
    app = Getcomics()  # constructor, calls method __init__
    app.mainloop()
