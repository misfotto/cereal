#!/usr/bin/env python3
#
# Read / Write from Serial Ports
import time
import traceback
import libs.ccVars as vars
import serial.tools.list_ports
#
# Managing the GUI
import PySimpleGUI as sg
#
# Managing exceptions messages
import sys
#
import threading
import os
from serial.threaded import LineReader, ReaderThread
import numpy as np
import csv, time

from libs.tinycc import TinyCC

def list_coms():
    ports = serial.tools.list_ports.comports()

    pts = []

    for port, desc, hwid in sorted(ports):
        pts.append(port)

    return pts


# Serial Toolkit END

glob = True
# Reading from serial in a separate thead to avoid UI blocking.

out_file = []

cc_responses = []

def open_window():
    layout = [[sg.Text("New Window", key="new")]]
    window = sg.Window("Second Window", layout, modal=True)
    choice = None
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

    window.close()


def tr_serial_read(s, v):
    global glob
    global values

    split_data = []
    print("Start reading from {} ".format(v['com_port']))
    print(
        "Settings-Line Ending {}  Data Bits {}  Baud Rate {}  Separator '{}'".format(v['line_ending'], v['data_bits'],
                                                                                      v['baud_rate'], v['separator']))

    while glob:
        try:
            if v['line_ending'] == "USE DATABITS":
                line = s.read(v['data_bits'])
            else:
                eol = get_eol(v['send_line_ending'])
                line = s.read_until(eol)

            # out_file.append()
            line_string = line.decode('utf-8').rstrip("\n").rstrip("\r")
            if values['separator'] != '':
                # print("{} {}".format(values['separator'], v['separator']))
                splitted = line_string.split(values['separator'])

                # empty_slot = [""] * ( table_split_len - len(splitted))
                # split_data.append(splitted + empty_slot)
                string_data = "; ".join(splitted)
                string_data = string_data + "\n"
                split_data.append(string_data)
                # print("SPLITTED-{}".format(split_data))

                text = window.Element('parsed_content')
                text.update(text.get() + "\n" + " ".join(splitted))
                with open(str(t) + "_PARSE_RESULT.csv", 'a+', newline='\n') as myfile:
                    myfile.write(string_data)
                    # wr.writerow(string_data)

            # print("Tipo di ritorno {}".format(type(line)))
            # print(line_string)
            x = []
            for c in line_string:
                # print("CCCCCCCCC {}".format(type(c)))

                p_x = hex(ord(c) + 2)
                # print("CCC-{}".format(p_x))
                x.append(hex(ord(c) + 2))
            final_hex = " ".join(x)
            # print(final_hex)

            out_file.append([line_string, final_hex])

            # print(line.decode('utf-8')
            '''
            for line in s.read():
                if v['separator'] != '':
                    print(str(line))
                    splitted = line.split(v['separator'])
                    out_file.append(splitted)
                    print(splitted)
                else:
                    out_file.append(line)

                print("{} bit of data-{}".format(v['data_bits'], line))
            # while data = s.read(v['data_bits']):
            #    print("data-{}".format(data))
            '''

            window.Element('parse_table').update(out_file, num_rows=8)
        except:
            print("Unexpected error-{}".format(sys.exc_info()))
            glob = False

        # window.Element('split_table').update(split_data, num_rows=8)

    print("exiting...")


baud = [110, 150, 300, 1200,
        2400, 4800, 9600, 19200,
        38400, 57600, 115200,
        230400, 460800, 921600]

data_bits = [5, 6, 7, 8, 9]
stop_bits = [1, 1.5, 2]
com_ports = list_coms()
line_ending = ["USE DATABITS", "LF", "CR", "CRLF"]
send_line_ending = ["LF", "CR", "CRLF"]
#table_split_len = 12
#empty_table_split = [""] * table_split_len
t = time.time()

def get_eol( option ):
    if option == "LF":
        eol = b"\n"
    elif option == "CRLF":
        eol = b"\r\n"
    elif option == "CRLF":
        eol = b"\r"
    else:
        eol = bytes(option)

    return eol


up = [
    [
        sg.Text(size=20, text="Serial Status"), sg.Text(size=2, text="{}".format(u'\u258a\u258a\u258a'), key="serial_status"),
        sg.Text(size=8, text="Serial Port"),
        sg.Drop(size=86, values=com_ports, default_value=com_ports[0], enable_events=True, key="com_port"),
        sg.Button(button_text="Refresh COMs", enable_events=True, key="refresh_com")
    ],
]

sx = [
    [sg.Text("Serial Configuration")],
    [sg.Text(size=8, text="Baud Rate"),
     sg.Drop(size=12, values=baud, default_value=baud[6], enable_events=True, key="baud_rate")],
    [sg.Text(size=8, text="Data Bits"),
     sg.Drop(size=12, values=data_bits, default_value=data_bits[3], enable_events=True, key="data_bits")],
    [sg.Text(size=8, text="Stop Bits"),
     sg.Drop(size=12, values=stop_bits, default_value=stop_bits[0], enable_events=True, key="stop_bits")],
    [sg.Text(size=8, text="Line Ending"),
     sg.Drop(size=12, values=line_ending, default_value=line_ending[1], enable_events=True, key="line_ending")],

    [sg.Text("Flow Control")],
    [sg.Checkbox('Software Flow Control', default=True, key="swctrl")],
    [sg.Checkbox('RTS HW Flow Control', default=False, key="hwrts")],
    [sg.Checkbox('DSR HW Flow Control', default=False, key="hwdsr")],
]

serial_tab_sx = [
    []
    ]

serial_tab_dx = [
    []
    ]

serial_tab = [
    [
sg.Button(button_text="Open Serial", size=12, key="start_capture"),

     sg.Button(button_text="Close Serial", size=12, key="stop_com"),
        sg.Text(text="SESSION TIMESTAMP: {}".format(t)),
sg.In(size=8, default_text="", key="separator")
    ],
    [
        sg.Text(size=63, text="Command"),
        sg.Text(size=10, text="Line Ending"),

    ],
    [
        sg.In(default_text="start_random_char", key="serial_cmd", size=72),
        sg.Drop(size=12, values=send_line_ending, default_value=send_line_ending[0], enable_events=True, key="send_line_ending"),
        sg.Button(button_text="Send", size=10, key="send_cmd")
    ],
    [
        sg.HorizontalSeparator()
    ],

    [
        sg.Table([ [ "UTF-8", "HEX" ] ], num_rows=8, expand_x=True, key="parse_table")
    ],
    [
        sg.Multiline("", size=(30, 5),  enable_events=True, key="parsed_content", expand_x=True)
    ]
#[sg.Table([ empty_table_split ], num_rows=8, expand_x=True, key="split_table")]
]

dx_tab_2 = [
[
        sg.Button(button_text="Open ccTalk", size=12, key="start_cc_capture"),
        sg.Button(button_text="Close ccTalk", size=12, key="close_cc_talk"),


    ],
[
        sg.Text(size=8, text="Sender"),
        sg.Text(size=9, text=" Destination"),
        sg.Text(size=28, text=" Header"),
        sg.Text(size=70, text="Payload"),

        ],
    [
        sg.In(default_text="3", key="cc_src", size=10),
        sg.In(default_text="1", key="cc_dest", size=10),

        sg.Drop(size=30, values=vars.cc_command, default_value=vars.cc_command[0], enable_events=True,
                key="cc_command"),
        sg.In(default_text="00 01 02", key="cc_cmd", size=72),

        sg.Button(
            button_text="Send",
            size=10,
            key="cc_send"
            )
        ],


    [
        sg.Table(
            [
                ['', '', '','', '', '','']
            ],
            auto_size_columns=False,
            col_widths=[1, 3, 1, 3, 30, 30, 3],
            headings=['dst', ' data len', 'src', 'header', 'data', 'data (ascii)','checksum'],
            num_rows=8,
            expand_x=True,
            key="cc_response_table"
            )
    ]
]

raw_output = [[
    #sg.Output(key='outp', expand_x=True, expand_y=True)
    ]]

tabs = [
    [
        sg.TabGroup([
            [
                sg.Tab('Serial', serial_tab),
                sg.Tab('ccTalk', dx_tab_2),
                sg.Tab('Raw Output', raw_output)
            ]
        ])
    ],
    [
        #sg.Output(size=(80, 10), font='Courier 8', key='outp')
    ],
]


layout = [
    up,
    [
        sg.Column(sx, vertical_alignment="top"),
        #sg.VSeperator(),
        sg.Column(tabs),
    ],


]

# Create the window
window = sg.Window("Cereal", layout)
ser = serial.Serial()
reading_thread = None
event, values = window.read()


#sys.exit()
# Create an event loop
while True:
    event, values = window.read()
    #print(event, values)
    print("Serial Open?: {}".format(ser.is_open))
    if ser.is_open == True:
        window['serial_status'].update(text_color="green")
    else:
        window['serial_status'].update(text_color="red")

    if event == "refresh_com":
        com_ports = list_coms()
        window.Element('com_port').update(values=com_ports, set_to_index=0)

    if event == "start_capture":
        window["start_capture"].Update(disabled=False)

        try:
            ser = serial.Serial()
            ser.baudrate = values['baud_rate']
            ser.port = values['com_port']
            ser.open()
            window['serial_status'].update(text_color="green")
            glob = True
            reading_thread = threading.Thread(target=tr_serial_read, args=(ser, values,), daemon=True)
            reading_thread.start()
            #reading_thread.join()

        except serial.SerialException as e:
            print("Serial Exception: {}\n".format(e))
        except:
            print("Unexpected error: {}".format(sys.exc_info()))

    if event == "start_cc_capture":
        window["start_capture"].Update(disabled=False)

        try:
            ser = serial.Serial()
            ser.baudrate = values['baud_rate']
            ser.port = values['com_port']
            ser.open()
            window['serial_status'].update(text_color="green")

            #reading_thread = threading.Thread(target=tr_serial_cc_read, args=(ser, values,), daemon=True)
            #reading_thread.start()
            #reading_thread.join()

        except serial.SerialException as e:
            print("Serial Exception: {}\n".format(e))
        except:
            print("Unexpected error: {}".format(sys.exc_info()))


    if event == "stop_com":
        try:
            print("Closing com...")
            if reading_thread is not None:
                print("Killing reading thread")
                glob = False

            print("Closing Serial Port!")
            # TODO-Controllare se è aprta
            ser.close()
            window['serial_status'].update(text_color="red")

        except:
            print("Unexpected error-{}".format(sys.exc_info()))

    if event == "cc_send":

        c = TinyCC(ser)

        #a, b = c.create_msg(code=2, data=[2])

        splitted_cmd = values['cc_cmd'].split(' ')
        print(splitted_cmd)
        data = list(map(int, splitted_cmd))
        print(values['cc_command'])
        command = int(values['cc_command'].split(': ')[1])
        print("Data sent: {}".format(data))
        byte_sent, response = c.send_command(command=command, args=data, dest=int(values['cc_dest']), src=int(values['cc_src']) )

        if response == []:
            cc_responses.append([
                "",
                "",
                "",
                "",
                "No response",
                "",
                "",
                ])
        else:
            ascii_res = list(map(chr, response['data']))
            ascii_res = "".join(ascii_res)
            cc_responses.append([
                response['sender'],
                response['n_args'],
                response['receiver'],
                response['header'],
                response['data'],
                ascii_res,
                response['sum'],
            ])
            print("ccTalk Response-{}".format(response))
            print("Data-{}".format(response['data']))
            print("Data ascii-{}".format(ascii_res))

        window['cc_response_table'].update(cc_responses)

    if event == "send_cmd":

        print("--> Invio comando-{}".format(values['serial_cmd']))
        try:
            eol = get_eol(values['send_line_ending'])
            # TODO-Controllare se la porta è già aperta #os.linesep
            cmd = bytes(values['serial_cmd'] , encoding='utf8')+ eol
            ser.write(cmd)

        except serial.SerialException:
            print("Serial Exception: {}".format(sys.exc_info()))
        except:
            print("Unexpected error: {}".format(sys.exc_info()[1]))

    # End program if user closes window or
    # presses the OK button
    if event == "OK" or event == sg.WIN_CLOSED:

        with open(str(t) +"_RAW_OUTPUT.txt", "w") as txt_file:
            for line in out_file:
                txt_file.write("\n".join(line) + "\n---\n")  # works with any number of elements in a line
        break

# window.close()
