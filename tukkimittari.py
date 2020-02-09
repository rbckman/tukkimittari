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
from kivy.config import Config
from kivy.clock import Clock
from multiprocessing.pool import ThreadPool

import time
import json

###--------- LÄS ELLER NOLLA GIVARNA---------------

def starta_givarna():
    givare1 = 0
    while True:
        givare1 += 1
        time.sleep(0.005)
        f = open("/dev/shm/kaparens_givare", "w")
        f.write(str(givare1))
        f.close()

###--------- SPARA, LÄS, RADERA, SÄTT TILL TRÄSLAG --------------

try:
    tra_data = json.load(open('tra_data.json'))
except:
    tra_data = []

def tra_data_save(tra_data):
    json.dump(tra_data,open('tra_data.json','w'))

def tra_data_add(tra_data, slag, langd, totlangd):
    tra_data.append({'slag':slag, 'langd':langd, 'totlangd':totlangd})
    json.dump(tra_data,open('tra_data.json','w'))

def tra_data_remove(tra_data, slag):
    c = 0
    for i in tra_data:
        if i['slag'] == slag:
            tra_data.pop(c)
        c = c + 1
    tra_data_save(tra_data)

def tra_data_langd(tra_data, slag):
    for i in tra_data:
        if i['slag'] == slag:
            return i['langd']


###---------- SJÄLVA GUYEN ---------------------

class Tukkimittari(App):
    def build(self):
        pool = ThreadPool(processes=1)
        pool.apply_async(starta_givarna)

        def las_givarna(dt):
            f = open("/dev/shm/kaparens_givare", "r")
            langd_display.text = f.read()

        Clock.schedule_interval(las_givarna, 0.01)

        root_widget = BoxLayout(orientation='vertical')

        # langd_display     | Sort | Mått läsare | inställd längd | totala längden
        # ------------------------------------------------------------------------
        # edit_button_grid  | edit sort | edit längd | nolla totala | Remove | Add
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
            langd_display.text = sort_input.text + langd_input.text

        def add_tra_slag(instance):
            tra_data_add(tra_data, sort_input.text, langd_input.text, 0)
            tra_button_grid.add_widget(Button(text=sort_input.text))
            update_buttons()

        def remove_tra_slag(instance):
            tra_data_remove(tra_data, sort_input.text)
            for i in tra_button_grid.children:
                print(i)
                print(i.text)
                if i.text == sort_input.text:
                    tra_button_grid.remove_widget(i)
            update_buttons()
 
        def tra_button_action(instance):
            sort_input.text = instance.text
            langd_input.text = tra_data_langd(tra_data, instance.text)

        def nolla(instance):
            nolla_givaren()

        langd_display = Label(size_hint_y=1, font_size=50)
        edit_button_grid = GridLayout(cols=6, size_hint_y=1)
        tra_button_grid = GridLayout(cols=10, size_hint_y=1)

        count_tra_slag()

        sort_input = TextInput(text='sort', halign='center', multiline=False, font_size=25)
        langd_input = TextInput(text='langd', halign='center', multiline=False, font_size=25)

        apply_button = Button(text='Apply')
        apply_button.bind(on_press=edit_tra_slag)

        add_button = Button(text='Add')
        add_button.bind(on_press=add_tra_slag)

        remove_button = Button(text='Remove')
        remove_button.bind(on_press=remove_tra_slag)

        nolla_button = Button(text='Nolla')
        nolla_button.bind(on_press=nolla)

        edit_button_grid.add_widget(sort_input)
        edit_button_grid.add_widget(langd_input)
        edit_button_grid.add_widget(apply_button)
        edit_button_grid.add_widget(nolla_button)
        edit_button_grid.add_widget(remove_button)
        edit_button_grid.add_widget(add_button)

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

Tukkimittari().run()

