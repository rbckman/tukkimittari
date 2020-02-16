#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# TUKKIMITTARI
# by Robin Bäckman
# 2020

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.vkeyboard import VKeyboard
from kivy.uix.popup import Popup
from kivy.config import Config
from kivy.clock import Clock
from kivy.core.window import Window
from multiprocessing.pool import ThreadPool
import os

from functools import partial

import RPi.GPIO as GPIO
import time
import json

GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.OUT) #RELAY
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP) #NOLLARE
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP) #SVÄRD

GPIO.output(2, GPIO.HIGH)

givarna_tot = 0
givarna = 0
add_tot = False
btntime = time.time()

# Get path of the current dir, then use it as working directory:
rundir = os.path.dirname(__file__)
if rundir != '':
    os.chdir(rundir)
filmfolder = "/home/pi/Videos/"
if os.path.isdir(filmfolder) == False:
    os.makedirs(filmfolder)
folderdir = os.getcwd()


### -------- CHECK FOR UPDATES -------------------

os.system('git -C ' + folderdir + ' pull')

### --------- CHECK VERSION ------------------

with open(folderdir + '/VERSION') as f:
    version = f.readline().rstrip()
    vername = f.readline().rstrip()
    madeby = f.readline().rstrip()

### -------- START GIVARNA -----------------------

os.system('/usr/bin/python3 ' + folderdir + '/givarna.py &')



###--------- SPARA, LÄS, RADERA, SÄTT TILL TRÄSLAG --------------

# FILE I/O

try:
    tra_data = json.load(open('tra_data.json'))
except:
    tra_data = []

def tra_data_save(tra_data):
    json.dump(tra_data,open('tra_data.json','w'))

def tra_data_add(tra_data, slag, langd, totlangd):
    tra_data.append({'slag':slag, 'langd':langd, 'totlangd':totlangd})
    json.dump(tra_data,open('tra_data.json','w'))

# GET

def tra_data_langd(tra_data, slag):
    for i in tra_data:
        if i['slag'] == slag:
            return i['langd']

def tra_data_totlangd(tra_data, slag):
    for i in tra_data:
        if i['slag'] == slag:
            return i['totlangd']

def tra_data_lista(tra_data):
    tra_lista = []
    for i in tra_data:
        tra_lista.append(i['slag'])
    return tra_lista
     
# PUT

def tra_data_remove(tra_data, slag):
    c = 0
    for i in tra_data:
        if i['slag'] == slag:
            tra_data.pop(c)
        c = c + 1
    tra_data_save(tra_data)

def tra_data_totlangd_add(tra_data, slag, langd_add):
    c = 0
    for i in tra_data:
        if i['slag'] == slag:
            totlangd = int(i['totlangd'])
            if langd_add == 'nolla':
                totlangd = 0
            else:
                totlangd = totlangd + langd_add
            tra_data[c]['totlangd'] = totlangd
        c = c + 1
    tra_data_save(tra_data)

def tra_data_edit_langd(tra_data, slag, langd):   
    c = 0
    for i in tra_data:
        if i['slag'] == slag:
            tra_data[c]['langd'] = langd
        c = c + 1
    tra_data_save(tra_data)


###---------- SJÄLVA GUYEN ---------------------

class Tukkimittari(App):
    def build(self):

        def las_givarna(dt):
            global givarna_tot, givarna, givarna_old, add_tot, btntime
            if givarna_tot == None:
                givarna_tot = 0

            if givarna - givarna_tot < 0 and givarna < 0:
                givarna_tot + givarna_tot + 2

            # LÄS GIVARNA
            try:
                f = open("/dev/shm/kaparens_givare", "r")
                givarna = f.read()
                givarna = int(givarna)
            except:
                givarna = givarna_old
            givarna_old = givarna

            # LÄS TRÄ SORTER
            sort = sort_input.text
            tra_lista = tra_data_lista(tra_data)

            # SVÄRD
            if GPIO.input(3) == False and givarna_tot != givarna:
                GPIO.output(2, GPIO.HIGH)
                if add_tot == True:
                    tra_data_totlangd_add(tra_data, sort, givarna - givarna_tot)
                givarna_tot = givarna 
                print(givarna_tot)

            # ADD TOT LANGD
            if GPIO.input(17) == False:
                print(time.time() - btntime)
                if time.time() - btntime > 1:
                    if add_tot == True:
                        add_tot = False
                        btntime = time.time()
                        adding_label.text = 'NOPE'
                    else:
                        add_tot = True
                        btntime = time.time()
                        adding_label.text = 'ADDING'
                    #tra_data_totlangd_add(tra_data, sort, givarna - givarna_tot)

            if sort in tra_lista:
                totlangd = tra_data_totlangd(tra_data, sort)
                langd = tra_data_langd(tra_data, sort)
                langd = int(langd)
            else:
                totlangd = 0
                langd = 0

            # RELAY PÅ / AV
            if givarna - givarna_tot >= langd:
                GPIO.output(2, GPIO.LOW)
            else:
                GPIO.output(2, GPIO.HIGH)

            # DISPLAY
            langd_display.text = str(givarna - givarna_tot) + ' cm / ' + str(langd) + ' cm / tot. ' + str(round(totlangd*0.01,1)) + ' m'

        Clock.schedule_interval(las_givarna, 0.01)

        root_widget = BoxLayout(orientation='vertical')

        # namn_button       | Ny   | Ladda
        # ------------------------------------------------------------------------
        # langd_display     | Sort | Mått läsare | inställd längd | totala längden
        # ------------------------------------------------------------------------
        # edit_button_grid  | edit sort | edit längd | exit | Remove | Add
        # ------------------------------------------------------------------------
        # tra_button_grid   | Björk | Gran | Tall | Asp | Ved |
        # ------------------------------------------------------------------------

        def count_tra_slag():
            for tra in tra_data:
                tra_button_grid.add_widget(Button(text=tra['slag']))

        def update_buttons():
            for button in tra_button_grid.children:
                button.bind(on_press=tra_button_action)

        def edit_tra_slag(instance):
            tra_data_edit_langd(tra_data, sort_input.text, langd_input.text)
            langd_display.text = sort_input.text + langd_input.text

        def add_tra_slag(instance):
            tra_data_add(tra_data, sort_input.text, langd_input.text, 0)
            tra_button_grid.add_widget(Button(text=sort_input.text))
            update_buttons()

        def remove_tra_slag(instance):
            def yes(instance):
                tra_data_remove(tra_data, sort_input.text)
                for i in tra_button_grid.children:
                    print(i)
                    print(i.text)
                    if i.text == sort_input.text:
                        tra_button_grid.remove_widget(i)
                update_buttons()
                popup.dismiss()

            yes_button = Button(text='Joo')
            no_button = Button(text='Nää')

            popup_widget = BoxLayout(orientation='vertical')
            popup_widget.add_widget(Label(text='E du nu rikit sääkär?'))
            popup_widget.add_widget(no_button)
            popup_widget.add_widget(yes_button)
            popup = Popup(title='Radera ' + sort_input.text, content=popup_widget, size_hint=(0.5,0.5))

            yes_button.bind(on_press=yes)
            no_button.bind(on_press=popup.dismiss)

            popup.open()

 
        def tra_button_action(instance):
            sort_input.text = instance.text
            langd_input.text = tra_data_langd(tra_data, instance.text)

        def nolla(instance):
            def yes(instance):
                tra_data_totlangd_add(tra_data, sort_input.text, 'nolla')
                popup.dismiss()

            yes_button = Button(text='Joo')
            no_button = Button(text='Nää')

            popup_widget = BoxLayout(orientation='vertical')
            popup_widget.add_widget(Label(text='E du nu rikit sääkär?'))
            popup_widget.add_widget(no_button)
            popup_widget.add_widget(yes_button)
            popup = Popup(title='Nolla totala längden', content=popup_widget, size_hint=(0.5,0.5))

            yes_button.bind(on_press=yes)
            no_button.bind(on_press=popup.dismiss)

            popup.open()

        def exit(instance):
            App.get_running_app().stop()

        upper_button_grid = GridLayout(cols=5, size_hint_y=0.6)
        langd_display = Label(size_hint_y=2, font_size=50)
        edit_button_grid = GridLayout(cols=6, size_hint_y=2)
        tra_button_grid = GridLayout(cols=10, size_hint_y=2)

        count_tra_slag()

        sort_input = TextInput(text='sort', halign='center', multiline=False, font_size=25)
        langd_input = TextInput(text='langd', halign='center', multiline=False, font_size=25)

        apply_button = Button(text='Apply')
        apply_button.bind(on_press=edit_tra_slag)

        add_button = Button(text='Add')
        add_button.bind(on_press=add_tra_slag)

        remove_button = Button(text='Remove', size_hint_x=0.5)
        remove_button.bind(on_press=remove_tra_slag)

        nolla_button = Button(text='Nolla tot.')
        nolla_button.bind(on_press=nolla)

        exit_button = Button(text='Quit')
        exit_button.bind(on_press=exit)

        name_label = Label(text=vername + ' ~ ' + version, halign='center', font_size=25, size_hint_x=4)
        madeby_label = Label(text=madeby, halign='center', font_size=12, size_hint_x=4)
        adding_label = Label(text='NOPE', halign='center', font_size=12)

        upper_button_grid.add_widget(name_label)
        upper_button_grid.add_widget(madeby_label)
        upper_button_grid.add_widget(adding_label)
        upper_button_grid.add_widget(nolla_button)
        upper_button_grid.add_widget(exit_button) 

        edit_button_grid.add_widget(sort_input)
        edit_button_grid.add_widget(langd_input)
        edit_button_grid.add_widget(apply_button)
        edit_button_grid.add_widget(add_button)
        edit_button_grid.add_widget(remove_button)

        root_widget.add_widget(upper_button_grid)
        root_widget.add_widget(langd_display)
        root_widget.add_widget(edit_button_grid)
        root_widget.add_widget(tra_button_grid)

        update_buttons()

        def edit_button_action(instance):
            if instance.text == 'Add':
                pass

        for button in edit_button_grid.children:
            button.bind(on_press=edit_button_action)

        return root_widget

Window.fullscreen = 'auto'
Tukkimittari().run()
os.system('pkill python3')
GPIO.cleanup()

