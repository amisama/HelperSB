# -*- coding: utf-8 -*-
from linepy import *
from linepy.gettoken import LineAuth
from akad.ttypes import ChatRoomAnnouncementContents, OpType, MediaType, ContentType, ApplicationType, TalkException, ErrorCode, Message
#from HTV import HanimeTV
from Scrap.translate import TranslateKyu
from datetime import datetime, timedelta, date
from bs4 import BeautifulSoup
from humanfriendly import format_timespan, format_size, format_number, format_length
from threading import Thread
from urllib.parse import urlencode, quote
from pathlib import Path
from ffmpy import FFmpeg
#from random import choice
#from zalgo_text import zalgo
import time, random, sys, json, codecs, re, os, shutil, requests, ast, pytz, atexit, traceback, base64, pafy, livejson, timeago, math, argparse, subprocess,traceback,humanize,asyncio,multiprocessing
#import Image2Anime, urllib3
#urllib3.disable_warnings()
from Lib.liff.ttypes import LiffChatContext, LiffContext, LiffSquareChatContext, LiffNoneContext, LiffViewRequest
#from line_notify import LineNotify
def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def update_non_existing_inplace(original_dict, to_add):
    for key, value in original_dict.items():
        if key not in to_add:
            to_add[key] = value
        if type(value) == dict:
            for k, v in value.items():
                if k not in to_add[key]:
                    to_add[key][k] = v
    original_dict.update(to_add)
    return original_dict

class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'
