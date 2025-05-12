# START OF FILE FunPayCortex/main.py

import time
from pip._internal.cli.main import main

# todo убрать когда-то
while True:
    try:
        import lxml

        break
    except ModuleNotFoundError:
        main(["install", "-U", "lxml>=5.3.0"])
while True:
    try:
        import bcrypt

        break
    except ModuleNotFoundError:
        main(["install", "-U", "bcrypt>=4.2.0"])
import Utils.cardinal_tools # Keep filename?
import Utils.config_loader as cfg_loader
from first_setup import first_setup
from colorama import Fore, Style
from Utils.logger import LOGGER_CONFIG
import logging.config
import colorama
import sys
import os
from cortex import Cortex # Renamed import
import Utils.exceptions as excs
from locales.localizer import Localizer

# ASCII логотип (можешь заменить на свой, если хочешь)
logo = """ [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m
 [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m' [0m [38;5;0m" [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m
 [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;52m, [0m [38;5;52mi [0m [38;5;88m> [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m
 [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;52m, [0m [38;5;88m> [0m [38;5;9m1 [0m [38;5;160m[ [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m
 [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m' [0m [38;5;0m^ [0m [38;5;52m: [0m [38;5;124m? [0m [38;5;9m( [0m [38;5;9m( [0m [38;5;9m( [0m [38;5;0m^ [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m
 [38;5;0m. [0m [38;5;0m. [0m [38;5;0m' [0m [38;5;0m' [0m [38;5;0m' [0m [38;5;0m' [0m [38;5;0m' [0m [38;5;0m' [0m [38;5;0m' [0m [38;5;0m' [0m [38;5;0m' [0m [38;5;0m' [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m' [0m [38;5;0m' [0m [38;5;0m' [0m [38;5;0m' [0m [38;5;0m' [0m [38;5;0m' [0m [38;5;0m' [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m' [0m [38;5;0m' [0m [38;5;0m' [0m [38;5;0m' [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;0m. [0m [38;5;52mI [0m [38;5;160m{ [0m [38;5;9m( [0m [38;5;9m( [0m [38;5;9m) [0m [38;5;9m( [0m [38;5;52m: [0m [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m
 [0m. [0m. [0m  [0m  [0m  [0m  [0m  [0m  [0m  [0m  [0m  [0m  [0m  [0m  [0m. [0m  [0m  [0m  [0m  [0m  [0m  [0m  [0m  [0m  [0m  [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m  [0m  [0m  [0m  [0m  [0m  [0m  [0m  [0m. [0m. [0m. [0m. [0m [38;5;52m, [0m [38;5;160m[ [0m [38;5;9m( [0m [38;5;9m) [0m [38;5;9m( [0m [38;5;9m) [0m [38;5;9m( [0m [38;5;52mi [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m
 [0m  [0m [38;5;0ml [0m [38;5;60mt [0m [38;5;60m/ [0m [38;5;60mt [0m [38;5;60m/ [0m [38;5;59m/ [0m [38;5;59m/ [0m [38;5;59m/ [0m [38;5;59m/ [0m [38;5;59m/ [0m [38;5;59m/ [0m [38;5;17m! [0m [0m  [0m [38;5;59m- [0m [38;5;60mt [0m [38;5;60m/ [0m [38;5;60mt [0m [38;5;59m/ [0m [38;5;59m/ [0m [38;5;59m/ [0m [38;5;59m| [0m [38;5;59m[ [0m [38;5;17mi [0m. [0m  [0m. [0m. [0m. [0m. [0m. [0m  [0m  [0m [38;5;0ml [0m [38;5;59m} [0m [38;5;60mf [0m [38;5;102mn [0m [38;5;102mn [0m [38;5;60mt [0m [38;5;59m} [0m [38;5;17m! [0m. [0m. [0m. [0m [38;5;52mI [0m [38;5;9m( [0m [38;5;9m( [0m [38;5;9m( [0m [38;5;9m( [0m [38;5;9m( [0m [38;5;9m( [0m [38;5;9m) [0m [38;5;160m] [0m [0m' [0m. [0m. [0m. [0m. [0m. [0m. [0m
 [0m' [0m  [0m [38;5;59m1 [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;59m/ [0m  [0m [38;5;145mL [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;188ma [0m [38;5;59m| [0m  [0m. [0m. [0m  [0m [38;5;59m{ [0m [38;5;146mq [0m [38;5;15m@ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m@ [0m [38;5;59m- [0m  [0m` [0m [38;5;9m1 [0m [38;5;9m( [0m [38;5;9m( [0m [38;5;9m1 [0m [38;5;9m) [0m [38;5;9m) [0m [38;5;160m[ [0m [38;5;167m( [0m [38;5;168mc [0m" [0m  [0m. [0m. [0m. [0m. [0m. [0m
 [0m' [0m  [0m [38;5;59m} [0m [38;5;15m@ [0m [38;5;15mB [0m [38;5;15m@ [0m [38;5;188mM [0m [38;5;145mq [0m [38;5;146mp [0m [38;5;146mq [0m [38;5;146mq [0m [38;5;145mq [0m [38;5;146mq [0m [38;5;59m] [0m  [0m [38;5;102mY [0m [38;5;15m@ [0m [38;5;15mB [0m [38;5;15m@ [0m [38;5;188mb [0m [38;5;145mO [0m [38;5;145mZ [0m [38;5;188md [0m [38;5;15m@ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;59m) [0m  [0m. [0m [38;5;103mY [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;188m# [0m [38;5;188ma [0m [38;5;188m* [0m [38;5;15m% [0m [38;5;15m$ [0m [38;5;59m{ [0m  [0m [38;5;52ml [0m [38;5;9m( [0m [38;5;9m( [0m [38;5;160m[ [0m [38;5;95m{ [0m [38;5;124m] [0m [38;5;132mu [0m [38;5;188ma [0m [38;5;195m& [0m [38;5;182mb [0m, [0m. [0m. [0m. [0m. [0m. [0m. [0m
 [0m' [0m  [0m [38;5;59m} [0m [38;5;15m$ [0m [38;5;15m@ [0m [38;5;15m$ [0m [38;5;102mX [0m  [0m  [0m  [0m  [0m  [0m  [0m  [0m. [0m  [0m [38;5;102mX [0m [38;5;15m$ [0m [38;5;15m@ [0m [38;5;15m$ [0m [38;5;59m? [0m  [0m  [0m  [0m [38;5;59m/ [0m [38;5;15m$ [0m [38;5;15mB [0m [38;5;15m@ [0m [38;5;145mm [0m  [0m [38;5;60mt [0m [38;5;15m$ [0m [38;5;15m@ [0m [38;5;15m@ [0m [38;5;15m$ [0m [38;5;109mU [0m [38;5;17mi [0m` [0m. [0m' [0mI [0m [38;5;59m\ [0m [38;5;17m! [0m  [0m [38;5;124m- [0m [38;5;9m( [0m [38;5;9m) [0m [38;5;9m1 [0m [38;5;125m} [0m [38;5;95mt [0m [38;5;188mo [0m [38;5;224mW [0m [38;5;203mu [0m [38;5;9m1 [0m [38;5;160m{ [0m [38;5;124m- [0m [38;5;52mi [0m" [0m. [0m. [0m. [0m
 [0m' [0m  [0m [38;5;59m} [0m [38;5;15m$ [0m [38;5;15m@ [0m [38;5;15m$ [0m [38;5;188m* [0m [38;5;145mC [0m [38;5;145mC [0m [38;5;145mC [0m [38;5;145mC [0m [38;5;145mC [0m [38;5;102mj [0m. [0m  [0m [38;5;102mY [0m [38;5;15m$ [0m [38;5;15m@ [0m [38;5;15m$ [0m [38;5;102mx [0m [38;5;59m~ [0m [38;5;59m_ [0m [38;5;59m] [0m [38;5;145mZ [0m [38;5;15m@ [0m [38;5;15mB [0m [38;5;15m$ [0m [38;5;103mY [0m  [0m [38;5;188mh [0m [38;5;15m$ [0m [38;5;15m@ [0m [38;5;15m$ [0m [38;5;145mQ [0m  [0m  [0m  [0m. [0m  [0m  [0m  [0m  [0m  [0m [38;5;52m, [0m [38;5;9m) [0m [38;5;9m( [0m [38;5;9m) [0m [38;5;9m( [0m [38;5;160m[ [0m [38;5;188ma [0m [38;5;15m$ [0m [38;5;210mJ [0m [38;5;9m] [0m [38;5;9m) [0m [38;5;9m) [0m [38;5;160m[ [0m [38;5;124m- [0m [38;5;52m! [0m' [0m. [0m. [0m
 [0m' [0m  [0m [38;5;59m} [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;188ma [0m  [0m  [0m [38;5;102mY [0m [38;5;15m$ [0m [38;5;15m@ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;188mh [0m: [0m. [0m [38;5;188m* [0m [38;5;15m$ [0m [38;5;15m@ [0m [38;5;15m$ [0m [38;5;66mf [0m  [0m` [0m' [0m. [0m. [0m. [0m. [0m^ [0m [38;5;160m} [0m [38;5;9m( [0m [38;5;9m) [0m [38;5;9m( [0m [38;5;9m( [0m [38;5;160m] [0m [38;5;145mO [0m [38;5;15m$ [0m [38;5;188mk [0m [38;5;210mC [0m [38;5;131m( [0m [38;5;88m> [0m [38;5;52ml [0m [38;5;52m, [0m' [0m. [0m. [0m. [0m
 [0m' [0m  [0m [38;5;59m} [0m [38;5;15m$ [0m [38;5;15m@ [0m [38;5;15m$ [0m [38;5;188mh [0m [38;5;102mv [0m [38;5;102mc [0m [38;5;102mc [0m [38;5;102mv [0m [38;5;102mc [0m [38;5;59m\ [0m. [0m  [0m [38;5;102mY [0m [38;5;15m$ [0m [38;5;15m@ [0m [38;5;15m$ [0m [38;5;15m& [0m [38;5;188mM [0m [38;5;188mM [0m [38;5;188mo [0m [38;5;188md [0m [38;5;145mC [0m [38;5;59m( [0m` [0m  [0m  [0m [38;5;145mm [0m [38;5;15m$ [0m [38;5;15m@ [0m [38;5;15m$ [0m [38;5;188mo [0mI [0m  [0m  [0m  [0m. [0m^ [0m [38;5;88m> [0m [38;5;160m} [0m [38;5;9m1 [0m [38;5;160m{ [0m [38;5;160m{ [0m [38;5;9m1 [0m [38;5;9m) [0m [38;5;124m] [0m [38;5;152mp [0m [38;5;15m@ [0m [38;5;195m& [0m [38;5;195mB [0m [38;5;66mu [0m  [0m. [0m. [0m. [0m. [0m. [0m. [0m
 [0m' [0m  [0m [38;5;59m} [0m [38;5;15m$ [0m [38;5;15mB [0m [38;5;15m$ [0m [38;5;102mX [0m  [0m  [0m  [0m  [0m  [0m  [0m' [0m  [0m [38;5;102mX [0m [38;5;15m$ [0m [38;5;15mB [0m [38;5;15m$ [0m [38;5;59m) [0m' [0m^ [0m. [0m  [0m  [0m  [0m  [0m' [0m  [0m [38;5;59m~ [0m [38;5;15mB [0m [38;5;15m$ [0m [38;5;15m@ [0m [38;5;15m$ [0m [38;5;15m% [0m [38;5;145m0 [0m [38;5;102mx [0m [38;5;59m_ [0m [38;5;88m~ [0m [38;5;160m{ [0m [38;5;9m) [0m [38;5;160m1 [0m [38;5;160m{ [0m [38;5;160m{ [0m [38;5;160m{ [0m [38;5;9m1 [0m [38;5;9m( [0m [38;5;160m1 [0m [38;5;167m) [0m [38;5;131m| [0m [38;5;131mf [0m [38;5;167mx [0m [38;5;52m< [0m. [0m. [0m. [0m. [0m. [0m. [0m
 [0m' [0m  [0m [38;5;59m{ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;145mL [0m  [0m` [0m' [0m' [0m' [0m. [0m' [0m  [0m [38;5;109mU [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;59m1 [0m  [0m. [0m. [0m. [0m. [0m' [0m. [0m. [0m. [0m  [0m [38;5;59m+ [0m [38;5;188mk [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;15m$ [0m [38;5;224m* [0m [38;5;203mX [0m [38;5;9m( [0m [38;5;9m1 [0m [38;5;160m{ [0m [38;5;160m{ [0m [38;5;160m{ [0m [38;5;160m{ [0m [38;5;160m} [0m [38;5;160m{ [0m [38;5;9m( [0m [38;5;9m( [0m [38;5;9m( [0m [38;5;9m1 [0m [38;5;9m1 [0m [38;5;9m{ [0m [38;5;9m} [0m [38;5;52m: [0m. [0m. [0m. [0m. [0m. [0m. [0m
 [0m  [0m [38;5;59m- [0m [38;5;188mh [0m [38;5;188mb [0m [38;5;188mh [0m [38;5;102mn [0m  [0m. [0m. [0m. [0m. [0m. [0m. [0m  [0m [38;5;102mr [0m [38;5;188mh [0m [38;5;188mb [0m [38;5;188mh [0m [38;5;59m] [0m  [0m' [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m  [0m. [0m [38;5;59m] [0m [38;5;174mL [0m [38;5;203mv [0m [38;5;160m] [0m [38;5;160m] [0m [38;5;160m{ [0m [38;5;160m{ [0m [38;5;160m{ [0m [38;5;160m1 [0m [38;5;160m{ [0m [38;5;160m[ [0m [38;5;160m{ [0m [38;5;9m( [0m [38;5;9m( [0m [38;5;9m( [0m [38;5;9m) [0m [38;5;9m( [0m [38;5;9m( [0m [38;5;9m) [0m [38;5;88m< [0m. [0m. [0m. [0m. [0m. [0m. [0m
 [0m. [0m. [0m  [0m  [0m  [0m  [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m  [0m  [0m  [0m  [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m^ [0m [38;5;88mi [0m [38;5;160m? [0m [38;5;160m[ [0m [38;5;160m1 [0m [38;5;160m1 [0m [38;5;160m{ [0m [38;5;160m1 [0m [38;5;160m{ [0m [38;5;160m[ [0m [38;5;160m} [0m [38;5;9m) [0m [38;5;9m( [0m [38;5;9m) [0m [38;5;9m( [0m [38;5;9m( [0m [38;5;9m( [0m [38;5;9m( [0m [38;5;160m] [0m [38;5;52ml [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m
 [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m  [0m [38;5;52mi [0m [38;5;160m{ [0m [38;5;9m( [0m [38;5;160m1 [0m [38;5;160m1 [0m [38;5;160m{ [0m [38;5;160m1 [0m [38;5;160m{ [0m [38;5;160m[ [0m [38;5;160m[ [0m [38;5;160m{ [0m [38;5;9m( [0m [38;5;9m( [0m [38;5;9m( [0m [38;5;9m( [0m [38;5;9m( [0m [38;5;160m} [0m [38;5;88m~ [0m [38;5;52m; [0m' [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m
 [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m  [0m [38;5;52m, [0m [38;5;124m] [0m [38;5;9m) [0m [38;5;160m{ [0m [38;5;160m{ [0m [38;5;160m{ [0m [38;5;160m1 [0m [38;5;160m{ [0m [38;5;160m[ [0m [38;5;160m] [0m [38;5;160m{ [0m [38;5;9m( [0m [38;5;9m( [0m [38;5;9m( [0m [38;5;9m( [0m [38;5;160m} [0m [38;5;88m+ [0m [38;5;52m; [0m' [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m
 [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m  [0m [38;5;88m> [0m [38;5;160m1 [0m [38;5;160m1 [0m [38;5;160m{ [0m [38;5;160m{ [0m [38;5;160m1 [0m [38;5;160m} [0m [38;5;124m] [0m [38;5;124m] [0m [38;5;160m{ [0m [38;5;9m( [0m [38;5;9m( [0m [38;5;9m1 [0m [38;5;124m] [0m [38;5;88m< [0m [38;5;52m, [0m` [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m
 [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m  [0m^ [0m [38;5;124m? [0m [38;5;9m) [0m [38;5;160m1 [0m [38;5;160m{ [0m [38;5;160m{ [0m [38;5;160m[ [0m [38;5;160m] [0m [38;5;160m[ [0m [38;5;9m1 [0m [38;5;9m( [0m [38;5;160m{ [0m [38;5;124m+ [0m [38;5;52mI [0m` [0m. [0m^ [0m  [0m` [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m
 [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m  [0m [38;5;52ml [0m [38;5;160m1 [0m [38;5;9m( [0m [38;5;160m} [0m [38;5;160m[ [0m [38;5;160m[ [0m [38;5;160m] [0m [38;5;160m] [0m [38;5;160m] [0m [38;5;124m- [0m [38;5;52mi [0m [38;5;52m, [0m. [0m. [0m. [0m. [0m  [0m` [0mI [0m' [0m^ [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m
 [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m' [0m [38;5;88m< [0m [38;5;160m{ [0m [38;5;124m_ [0m [38;5;52mi [0m [38;5;88m< [0m [38;5;124m+ [0m [38;5;88m< [0m [38;5;52m! [0m [38;5;52m: [0m' [0m. [0m  [0m. [0m. [0m. [0m. [0m' [0m^ [0m" [0m" [0m` [0m' [0m. [0m. [0m. [0m. [0m. [0m. [0m
 [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m' [0m [38;5;52m, [0m' [0m. [0m" [0m [38;5;52m, [0m` [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m  [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m
 [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m. [0m
"""

VERSION = "0.1.15.19" # You might want to update this to your own version scheme

Utils.cardinal_tools.set_console_title(f"FunPay Cortex v{VERSION}") # Changed name

if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
else:
    os.chdir(os.path.dirname(__file__))

folders = ["configs", "logs", "storage", "storage/cache", "storage/plugins", "storage/products", "plugins"]
for i in folders:
    if not os.path.exists(i):
        os.makedirs(i)

files = ["configs/auto_delivery.cfg", "configs/auto_response.cfg"]
for i in files:
    if not os.path.exists(i):
        with open(i, "w", encoding="utf-8") as f:
            ...

colorama.init()

logging.config.dictConfig(LOGGER_CONFIG)
logging.raiseExceptions = False
logger = logging.getLogger("main")
logger.debug("------------------------------------------------------------------")

print(f"{Style.RESET_ALL}{logo}")
print(f"{Fore.RED}{Style.BRIGHT}v{VERSION}{Style.RESET_ALL} ({Fore.YELLOW}Обновления отключены{Style.RESET_ALL})\n") # Added update disabled note
print(f"{Fore.MAGENTA}{Style.BRIGHT}Автор: {Fore.BLUE}{Style.BRIGHT}@beedge{Style.RESET_ALL}") # Changed author

if not os.path.exists("configs/_main.cfg"):
    first_setup()
    sys.exit()

if sys.platform == "linux" and os.getenv('FPCORTEX_IS_RUNNIG_AS_SERVICE', '0') == '1': # Changed ENV var name maybe?
    import getpass
    service_name = "FunPayCortex" # Changed service name
    run_dir = f"/run/{service_name}"
    user_run_dir = f"{run_dir}/{getpass.getuser()}"
    pid_file_path = f"{user_run_dir}/{service_name}.pid"

    # Ensure directories exist with correct permissions
    if not os.path.exists(run_dir):
        os.makedirs(run_dir, mode=0o755)
        # Optionally set owner/group if needed, e.g., using shutil.chown if run as root initially
    if not os.path.exists(user_run_dir):
         os.makedirs(user_run_dir, mode=0o755)
         # Optionally set owner/group

    try:
        pid = str(os.getpid())
        with open(pid_file_path, "w") as pidFile:
             pidFile.write(pid)
        # Optionally set owner/group for the pid file itself
        logger.info(f"$GREENPID файл создан: {pid_file_path}, PID процесса: {pid}")
    except Exception as e:
         logger.error(f"Не удалось создать PID файл {pid_file_path}: {e}")


# Removed code related to delete.json and file updates as updates are disabled

try:
    logger.info("$MAGENTAЗагружаю конфиг _main.cfg...")  # locale
    MAIN_CFG = cfg_loader.load_main_config("configs/_main.cfg")
    localizer = Localizer(MAIN_CFG["Other"]["language"])
    _ = localizer.translate

    logger.info("$MAGENTAЗагружаю конфиг auto_response.cfg...")  # locale
    AR_CFG = cfg_loader.load_auto_response_config("configs/auto_response.cfg")
    RAW_AR_CFG = cfg_loader.load_raw_auto_response_config("configs/auto_response.cfg")

    logger.info("$MAGENTAЗагружаю конфиг auto_delivery.cfg...")  # locale
    AD_CFG = cfg_loader.load_auto_delivery_config("configs/auto_delivery.cfg")
except excs.ConfigParseError as e:
    logger.error(e)
    logger.error("Завершаю программу...")  # locale
    time.sleep(5)
    sys.exit()
except UnicodeDecodeError:
    logger.error("Произошла ошибка при расшифровке UTF-8. Убедитесь, что кодировка файла = UTF-8, "
                 "а формат конца строк = LF.")  # locale
    logger.error("Завершаю программу...")  # locale
    time.sleep(5)
    sys.exit()
except:
    logger.critical("Произошла непредвиденная ошибка.")  # locale
    logger.warning("TRACEBACK", exc_info=True)
    logger.error("Завершаю программу...")  # locale
    time.sleep(5)
    sys.exit()

localizer = Localizer(MAIN_CFG["Other"]["language"])

try:
    Cortex(MAIN_CFG, AD_CFG, AR_CFG, RAW_AR_CFG, VERSION).init().run() # Renamed class call
except KeyboardInterrupt:
    logger.info("Завершаю программу...")  # locale
    sys.exit()
except:
    logger.critical("При работе Кортекса произошла необработанная ошибка.") # Renamed comment
    logger.warning("TRACEBACK", exc_info=True)
    logger.critical("Завершаю программу...")  # locale
    time.sleep(5)
    sys.exit()

# END OF FILE FunPayCortex/main.py