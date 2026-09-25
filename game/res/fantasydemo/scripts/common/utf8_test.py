# -*- coding: utf-8 -*-

import logging

configLog = logging.getLogger( "Config" )

chinese = "Chinese: 这是一个测试的中文字符。"
japanese = "Japanese: この日本語の文字のためのテストです。"
russian = "Russian: Это тест для русских символов."

def run():
	configLog.info( "UTF-8 test" )
	configLog.info( chinese )
	configLog.info( japanese )
	configLog.info( russian )


# utf8_test.py
