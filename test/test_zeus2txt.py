#! /usr/bin/env python
# vim: set fileencoding=utf-8 :
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 Kirill V. Lyadvinsky
# http://www.codeatcpp.com
#
# Licensed under the BSD 3-Clause license.
# See LICENSE file in the project root for full license information.
#
""" zeus2txt.py tests """

import io
import os
import tempfile
import unittest
from collections import namedtuple
import logging
from mock import patch

from zxtools import zeus2txt
from zxtools.common import safe_parse_args



class TestZeus2Txt(unittest.TestCase):
    def test_args_parser(self):
        args_parser = zeus2txt.create_parser()

        with self.assertRaises(SystemExit):
            with patch('sys.argv', ["zeus2txt.py", "-h", "-v"]):
                zeus2txt.main()

        with self.assertRaises(SystemExit):
            with patch('sys.argv', ["zeus2txt.py"]):
                zeus2txt.main()

        temp_in_file = tempfile.mkstemp()[1]
        input_file = open(temp_in_file, "w")
        input_file.close()
        temp_out_file = tempfile.mkstemp()[1]
        try:
            args = safe_parse_args(args_parser, ["info", temp_in_file])
            self.assertEqual(args.func, zeus2txt.show_info)
            args.zeus_file.close()

            args = safe_parse_args(args_parser,
                                   ["convert", temp_in_file, temp_out_file])
            self.assertEqual(args.func, zeus2txt.convert_file)
            args.zeus_file.close()
            args.output_file.close()
        finally:
            os.remove(temp_in_file)
            os.remove(temp_out_file)

    @staticmethod
    def prepare_convert_args(test_data, include_code=False):
        test_file = io.BytesIO(test_data)
        temp_output_path = tempfile.mkstemp()[1]
        temp_output_file = open(temp_output_path, "w")

        args = namedtuple('Args', "zeus_file output_file include_code")
        parsed_args = args(test_file, temp_output_file, include_code)
        return parsed_args, temp_output_path, temp_output_file

    def test_undefined_token(self):
        logging.basicConfig(level=logging.DEBUG)
        args, temp_output_path, temp_output_file = self.prepare_convert_args(
            b"\x0A\x00\x0A\x06\xFF\x2C\x34\x32\x00\xFF\xFF")

        try:
            zeus2txt.convert_file(args)
            temp_output_file.close()
            temp_output_file = open(temp_output_path, "r")
            lines = temp_output_file.read().splitlines()
            self.assertEqual(lines, ["00010       ,42", ""])
        finally:
            temp_output_file.close()
            os.remove(temp_output_path)

    def test_no_eof(self):
        args, temp_output_path, temp_output_file = self.prepare_convert_args(
            b"\x0A\x00\x0A\x06\x82\x87\x2C\x34\x32\x00")

        try:
            zeus2txt.convert_file(args)
            temp_output_file.close()
            temp_output_file = open(temp_output_path, "r")
            lines = temp_output_file.read().splitlines()
            self.assertEqual(lines, ["00010       ADD BC,42", ])
        finally:
            temp_output_file.close()
            os.remove(temp_output_path)

    def test_include_code(self):
        args, temp_output_path, temp_output_file = self.prepare_convert_args(
            b"\x0A\x00\x0A\x06\x82\x87\x2C\x34\x32\x00", True)

        try:
            zeus2txt.convert_file(args)
            temp_output_file.close()
            temp_output_file = open(temp_output_path, "r")
            lines = temp_output_file.read().splitlines()
            self.assertEqual(lines, ["00010       ADD BC,42"
                                     "              ; 0x000A "
                                     "0x0A 0x06 0x82 0x87 "
                                     "0x2C 0x34 0x32 0x00 ", ])
        finally:
            temp_output_file.close()
            os.remove(temp_output_path)

    def test_convert(self):
        args, temp_output_path, temp_output_file = self.prepare_convert_args(
            self.test_data)

        try:
            zeus2txt.convert_file(args)
            temp_output_file.close()
            temp_output_file = open(temp_output_path, "rb")
            lines = temp_output_file.read().splitlines()
            expected_lines = self.test_output.split(b"\n")
            self.assertEqual(lines, expected_lines)
        finally:
            temp_output_file.close()
            os.remove(temp_output_path)

    def setUp(self):
        self.test_data = (
            b"\x00\x00\x3B\x20\x4C\x4F\x41\x44\x45\x52\x20\x66\x6F\x72\x20\x46"
            b"\x2E\x45\x44\x49\x54\x4F\x52\x00\x00\x00\x3B\x20\x4C\x2E\x4B\x2E"
            b"\x50\x72\x6F\x64\x75\x63\x74\x69\x6F\x6E\x00\x0A\x00\x0A\x06\xBF"
            b"\x35\x30\x30\x30\x30\x00\x14\x00\x0A\x06\x8A\x43\x4C\x53\x00\x1E"
            b"\x00\x0A\x06\x8A\x53\x48\x52\x00\x28\x00\x0A\x06\x8A\x4E\x45\x57"
            b"\x53\x48\x00\x32\x00\x0A\x06\xB3\x94\x2C\x4D\x53\x47\x31\x00\x3C"
            b"\x00\x0A\x06\xB3\x87\x2C\x33\x39\x00\x46\x00\x0A\x06\x8A\x23\x32"
            b"\x30\x33\x43\x00\x50\x00\x0A\x06\x8A\x53\x54\x41\x4E\x44\x00\x5A"
            b"\x00\x0A\x06\xB3\xA5\x2C\x32\x32\x37\x38\x34\x00\x64\x00\x0A\x06"
            b"\xB3\x94\x2C\x32\x32\x37\x38\x33\x00\x6E\x00\x0A\x06\xB3\x87\x2C"
            b"\x35\x31\x31\x00\x78\x00\x0A\x06\xB3\x28\xA5\x29\x2C\x30\x00\x82"
            b"\x00\x0A\x06\xB7\x00\x8C\x00\x0A\x06\xB0\x4C\x4F\x41\x44\x00\x3F"
            b"\x9C\x45\x4E\x44\x0A\x03\xCC\x00\x40\x9C\x43\x4C\x53\x0A\x03\xB3"
            b"\xA5\x2C\x31\x36\x33\x38\x34\x00\x4A\x9C\x0A\x06\xB3\x94\x2C\x31"
            b"\x36\x33\x38\x35\x00\x54\x9C\x0A\x06\xB3\x87\x2C\x36\x31\x34\x33"
            b"\x00\x5E\x9C\x0A\x06\xB3\x28\xA5\x29\x2C\x30\x00\x68\x9C\x0A\x06"
            b"\xB7\x00\x72\x9C\x0A\x06\xB3\xA5\x2C\x32\x32\x35\x32\x38\x00\x7C"
            b"\x9C\x0A\x06\xB3\x94\x2C\x32\x32\x35\x32\x39\x00\x86\x9C\x0A\x06"
            b"\xB3\x87\x2C\x37\x36\x37\x00\x90\x9C\x0A\x06\xB3\x28\xA5\x29\x2C"
            b"\x37\x00\x9A\x9C\x0A\x06\xB7\x00\xA4\x9C\x0A\x06\xE3\x80\x00\xAE"
            b"\x9C\xC2\x28\x32\x35\x34\x29\x2C\x80\x3A\xB3\x80\x2C\x37\x00\xAF"
            b"\x9C\x0A\x06\xB3\x28\x32\x33\x36\x32\x34\x29\x2C\x80\x00\xB8\x9C"
            b"\x43\x48\x4F\x50\x45\x20\xB3\x80\x2C\x32\x00\xC2\x9C\x0A\x06\x8A"
            b"\x23\x31\x36\x30\x31\x00\xCC\x9C\x0A\x06\xCC\x00\xD6\x9C\x53\x48"
            b"\x52\x0A\x03\xB3\xA5\x2C\x31\x35\x36\x31\x36\x00\xE0\x9C\x0A\x06"
            b"\xB3\x94\x2C\x33\x30\x30\x30\x30\x00\xEA\x9C\x0A\x06\xB3\x87\x2C"
            b"\x37\x36\x38\x00\xF4\x9C\x0A\x06\xB7\x00\xFE\x9C\x0A\x06\xB3\xA5"
            b"\x2C\x33\x30\x30\x30\x30\x00\x08\x9D\x0A\x06\xB3\x86\x2C\x39\x36"
            b"\x00\x12\x9D\x53\x48\x32\x0A\x03\xC9\x87\x00\x1C\x9D\x0A\x06\xB3"
            b"\x86\x2C\x34\x00\x26\x9D\x53\x48\x33\x0A\x03\xA9\xA5\x00\x30\x9D"
            b"\x0A\x06\x9C\x53\x48\x33\x00\x3A\x9D\x0A\x06\xB3\x86\x2C\x34\x00"
            b"\x44\x9D\x53\x48\x34\x0A\x03\xB3\x80\x2C\x28\xA5\x29\x00\x4E\x9D"
            b"\x0A\x06\xD2\x00\x58\x9D\x0A\x06\xBE\x28\xA5\x29\x00\x62\x9D\x0A"
            b"\x06\xB3\x28\xA5\x29\x2C\x80\x00\x6C\x9D\x0A\x06\xA9\xA5\x00\x76"
            b"\x9D\x0A\x06\x9C\x53\x48\x34\x00\x80\x9D\x0A\x06\xC8\x87\x00\x8A"
            b"\x9D\x0A\x06\x9C\x53\x48\x32\x00\x94\x9D\x0A\x06\xCC\x00\x9E\x9D"
            b"\x53\x54\x41\x4E\x44\x20\xB3\xA5\x2C\x31\x35\x36\x31\x36\x00\xA8"
            b"\x9D\x0A\x06\x95\xA3\x00\xB2\x9D\x0A\x06\xB3\x28\x32\x33\x36\x30"
            b"\x36\x29\x2C\xA5\x00\xBC\x9D\x0A\x06\xCC\x00\xC6\x9D\x4E\x45\x57"
            b"\x53\x48\x20\xB3\xA5\x2C\x41\x44\x52\x53\x48\x00\xD0\x9D\x0A\x06"
            b"\x95\xA3\x00\xDA\x9D\x0A\x06\xB3\x28\x32\x33\x36\x30\x36\x29\x2C"
            b"\xA5\x00\xE4\x9D\x0A\x06\xCC\x00\xEE\x9D\x46\x46\x49\x4C\x45\x20"
            b"\xB3\x80\x2C\x28\x32\x30\x37\x30\x38\x29\x00\xF8\x9D\x0A\x06\x8C"
            b"\x30\x00\x02\x9E\x0A\x06\xB1\xE4\x2C\x4E\x46\x49\x4C\x45\x00\x0C"
            b"\x9E\x0A\x06\xB3\x86\x2C\x80\x00\x16\x9E\x0A\x06\xB3\x94\x2C\x31"
            b"\x38\x34\x33\x32\x00\x20\x9E\x46\x46\x32\x0A\x03\xB3\xA5\x2C\x46"
            b"\x4E\x41\x4D\x45\x00\x2A\x9E\x0A\x06\xB3\x28\x50\x44\x45\x29\x2C"
            b"\x94\x00\x34\x9E\x0A\x06\xB3\x28\x50\x42\x43\x29\x2C\x87\x00\x3E"
            b"\x9E\x0A\x06\xB3\x86\x2C\x38\x00\x48\x9E\x46\x46\x33\x0A\x03\xB3"
            b"\x80\x2C\x28\x94\x29\x00\x52\x9E\x0A\x06\x8C\x28\xA5\x29\x00\x5C"
            b"\x9E\x0A\x06\xB1\xBD\x2C\x4E\x45\x58\x54\x46\x00\x66\x9E\x0A\x06"
            b"\xA9\x94\x00\x70\x9E\x0A\x06\xA9\xA5\x00\x7A\x9E\x0A\x06\x9C\x46"
            b"\x46\x33\x00\x84\x9E\x0A\x06\xB3\x80\x2C\x28\x94\x29\x00\x8E\x9E"
            b"\x0A\x06\x8C\x36\x39\x00\x98\x9E\x0A\x06\xB1\xBD\x2C\x4E\x45\x58"
            b"\x54\x46\x00\xA2\x9E\x0A\x06\xB3\xA5\x2C\x36\x00\xAC\x9E\x0A\x06"
            b"\x82\xA5\x2C\x94\x00\xB6\x9E\x0A\x06\xB3\x80\x2C\x28\xA5\x29\x00"
            b"\xC0\x9E\x0A\x06\xB3\x28\x53\x45\x43\x29\x2C\x80\x00\xCA\x9E\x0A"
            b"\x06\xA9\xA5\x00\xD4\x9E\x0A\x06\xB3\x80\x2C\x28\xA5\x29\x00\xDE"
            b"\x9E\x0A\x06\xB3\x28\x54\x52\x43\x29\x2C\x80\x00\xE8\x9E\x0A\x06"
            b"\xB0\x4C\x4F\x41\x32\x00\xF2\x9E\x4E\x45\x58\x54\x46\x20\xB3\x94"
            b"\x2C\x28\x50\x44\x45\x29\x00\xFC\x9E\x0A\x06\xB3\xA5\x2C\x31\x36"
            b"\x00\x06\x9F\x0A\x06\x82\xA5\x2C\x94\x00\x10\x9F\x0A\x06\xA1\x94"
            b"\x2C\xA5\x00\x1A\x9F\x0A\x06\xB3\x87\x2C\x28\x50\x42\x43\x29\x00"
            b"\x24\x9F\x0A\x06\x9C\x46\x46\x32\x00\x2E\x9F\x4E\x46\x49\x4C\x45"
            b"\x20\x8A\x4E\x45\x57\x53\x48\x00\x38\x9F\x0A\x06\xB3\x94\x2C\x4D"
            b"\x53\x47\x32\x00\x42\x9F\x0A\x06\xB3\x87\x2C\x4D\x53\x47\x33\x2D"
            b"\x4D\x53\x47\x32\x00\x4C\x9F\x0A\x06\x8A\x23\x32\x30\x33\x43\x00"
            b"\x4D\x9F\x0A\x06\x8A\x42\x45\x45\x50\x00\x4E\x9F\x0A\x06\xB3\x94"
            b"\x2C\x4D\x53\x47\x33\x00\x4F\x9F\x0A\x06\xB3\x87\x2C\x54\x52\x43"
            b"\x2D\x4D\x53\x47\x33\x00\x50\x9F\x0A\x06\x8A\x23\x32\x30\x33\x43"
            b"\x00\x60\x9F\x8A\x50\x41\x55\x53\x3A\x8A\x53\x54\x41\x4E\x44\x00"
            b"\x6A\x9F\x0A\x06\xB0\x4C\x4F\x41\x44\x00\x74\x9F\x50\x41\x55\x53"
            b"\x0A\x02\xE3\x80\x00\x7E\x9F\x0A\x06\xB3\x28\x32\x33\x35\x36\x30"
            b"\x29\x2C\x80\x00\x88\x9F\x50\x41\x32\x0A\x03\xB3\x80\x2C\x28\x32"
            b"\x33\x35\x36\x30\x29\x00\x92\x9F\x0A\x06\x8C\x30\x00\x9C\x9F\x0A"
            b"\x06\xCC\x20\xBD\x00\xA6\x9F\x0A\x06\xB1\x50\x41\x32\x00\xB0\x9F"
            b"\x42\x45\x45\x50\x0A\x02\xB3\x94\x2C\x23\x30\x31\x30\x35\x00\xBA"
            b"\x9F\x0A\x06\xB3\xA5\x2C\x23\x30\x36\x36\x36\x00\xC4\x9F\x0A\x06"
            b"\x8A\x23\x30\x33\x42\x35\x00\xCE\x9F\x0A\x06\xCC\x00\xD8\x9F\x4C"
            b"\x4F\x41\x44\x0A\x02\xB3\xA5\x2C\x32\x32\x35\x36\x30\x00\xE2\x9F"
            b"\x0A\x06\xB3\x94\x2C\x32\x32\x35\x36\x31\x00\xEC\x9F\x0A\x06\xB3"
            b"\x87\x2C\x37\x33\x36\x00\xF6\x9F\x0A\x06\xB3\x28\xA5\x29\x2C\x30"
            b"\x00\x00\xA0\x0A\x06\xB7\x00\x0A\xA0\x0A\x06\xB3\x87\x2C\x23\x30"
            b"\x39\x30\x35\x00\x14\xA0\x0A\x06\xB3\x94\x2C\x30\x00\x1E\xA0\x0A"
            b"\x06\xB3\xA5\x2C\x31\x38\x34\x33\x32\x00\x28\xA0\x0A\x06\x8A\x31"
            b"\x35\x36\x33\x35\x00\x32\xA0\x0A\x06\xB0\x46\x46\x49\x4C\x45\x00"
            b"\x3C\xA0\x4C\x4F\x41\x32\x0A\x02\xB3\x80\x2C\x28\x53\x45\x43\x29"
            b"\x00\x46\xA0\x0A\x06\xB3\x9D\x2C\x80\x00\x50\xA0\x0A\x06\xB3\x80"
            b"\x2C\x28\x54\x52\x43\x29\x00\x5A\xA0\x0A\x06\xB3\x92\x2C\x80\x00"
            b"\x64\xA0\x0A\x06\xB3\x87\x2C\x23\x32\x36\x30\x35\x00\x6E\xA0\x0A"
            b"\x06\xB3\xA5\x2C\x33\x30\x30\x30\x30\x00\x78\xA0\x0A\x06\x8A\x31"
            b"\x35\x36\x33\x35\x00\x82\xA0\x0A\x06\xB0\x33\x31\x36\x39\x33\x00"
            b"\x60\xEA\x41\x44\x52\x53\x48\x20\xA0\x33\x30\x30\x30\x30\x00\x6A"
            b"\xEA\x4D\x53\x47\x31\x0A\x02\x96\x32\x32\x2C\x30\x2C\x30\x2C\x31"
            b"\x37\x2C\x30\x00\x74\xEA\x0A\x06\x96\x31\x36\x2C\x37\x00\x7E\xEA"
            b"\x97\x22\x46\x4F\x4E\x54\x20\x45\x44\x49\x54\x4F\x52\x20\x62\x79"
            b"\x20\x4C\x79\x61\x22\x00\x88\xEA\x97\x22\x64\x76\x69\x6E\x73\x6B"
            b"\x79\x20\x4B\x69\x72\x69\x6C\x6C\x22\x00\x92\xEA\x46\x4E\x41\x4D"
            b"\x45\x20\x97\x22\x65\x64\x69\x74\x6F\x72\x0A\x02\x22\x00\x9C\xEA"
            b"\x50\x44\x45\x0A\x03\x99\x30\x00\xA6\xEA\x50\x42\x43\x0A\x03\x99"
            b"\x30\x00\xB0\xEA\x4D\x53\x47\x32\x0A\x02\x96\x32\x32\x2C\x35\x2C"
            b"\x30\x2C\x31\x37\x2C\x30\x00\xBA\xEA\x96\x31\x36\x2C\x37\x2C\x31"
            b"\x39\x2C\x31\x00\xC4\xEA\x97\x22\x46\x69\x6C\x65\x20\x27\x65\x64"
            b"\x69\x74\x6F\x72\x0A\x02\x3C\x9D\x3E\x27\x22\x00\xCE\xEA\x97\x22"
            b"\x20\x6E\x6F\x74\x20\x66\x6F\x75\x6E\x64\x22\x00\xD8\xEA\x4D\x53"
            b"\x47\x33\x0A\x02\x96\x32\x32\x2C\x36\x2C\x30\x2C\x31\x37\x2C\x30"
            b"\x00\xDD\xEA\x0A\x06\x96\x31\x36\x2C\x37\x2C\x31\x39\x2C\x30\x00"
            b"\xE2\xEA\x97\x22\x50\x52\x45\x53\x53\x20\x41\x4E\x59\x20\x4B\x45"
            b"\x59\x20\x46\x4F\x52\x20\x22\x00\xEC\xEA\x97\x22\x52\x45\x4C\x4F"
            b"\x41\x44\x20\x46\x49\x4C\x45\x22\x00\x00\xEB\x54\x52\x43\x0A\x03"
            b"\x96\x30\x00\x0A\xEB\x53\x45\x43\x0A\x03\x96\x30\x00\x14\xEB\x45"
            b"\x4E\x44\x32\x0A\x02\xBB\x00\xFF\xFF"
        )
        self.test_output = (
            b"\x30\x30\x30\x30\x30\x20\x3B\x20\x4C\x4F\x41\x44\x45\x52\x20\x66"
            b"\x6F\x72\x20\x46\x2E\x45\x44\x49\x54\x4F\x52\x0A\x30\x30\x30\x30"
            b"\x30\x20\x3B\x20\x4C\x2E\x4B\x2E\x50\x72\x6F\x64\x75\x63\x74\x69"
            b"\x6F\x6E\x0A\x30\x30\x30\x31\x30\x20\x20\x20\x20\x20\x20\x20\x4F"
            b"\x52\x47\x20\x35\x30\x30\x30\x30\x0A\x30\x30\x30\x32\x30\x20\x20"
            b"\x20\x20\x20\x20\x20\x43\x41\x4C\x4C\x20\x43\x4C\x53\x0A\x30\x30"
            b"\x30\x33\x30\x20\x20\x20\x20\x20\x20\x20\x43\x41\x4C\x4C\x20\x53"
            b"\x48\x52\x0A\x30\x30\x30\x34\x30\x20\x20\x20\x20\x20\x20\x20\x43"
            b"\x41\x4C\x4C\x20\x4E\x45\x57\x53\x48\x0A\x30\x30\x30\x35\x30\x20"
            b"\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x44\x45\x2C\x4D\x53\x47\x31"
            b"\x0A\x30\x30\x30\x36\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x20"
            b"\x42\x43\x2C\x33\x39\x0A\x30\x30\x30\x37\x30\x20\x20\x20\x20\x20"
            b"\x20\x20\x43\x41\x4C\x4C\x20\x23\x32\x30\x33\x43\x0A\x30\x30\x30"
            b"\x38\x30\x20\x20\x20\x20\x20\x20\x20\x43\x41\x4C\x4C\x20\x53\x54"
            b"\x41\x4E\x44\x0A\x30\x30\x30\x39\x30\x20\x20\x20\x20\x20\x20\x20"
            b"\x4C\x44\x20\x48\x4C\x2C\x32\x32\x37\x38\x34\x0A\x30\x30\x31\x30"
            b"\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x44\x45\x2C\x32\x32"
            b"\x37\x38\x33\x0A\x30\x30\x31\x31\x30\x20\x20\x20\x20\x20\x20\x20"
            b"\x4C\x44\x20\x42\x43\x2C\x35\x31\x31\x0A\x30\x30\x31\x32\x30\x20"
            b"\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x28\x48\x4C\x29\x2C\x30\x0A"
            b"\x30\x30\x31\x33\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x49\x52"
            b"\x0A\x30\x30\x31\x34\x30\x20\x20\x20\x20\x20\x20\x20\x4A\x50\x20"
            b"\x4C\x4F\x41\x44\x0A\x33\x39\x39\x39\x39\x20\x45\x4E\x44\x20\x20"
            b"\x20\x52\x45\x54\x0A\x34\x30\x30\x30\x30\x20\x43\x4C\x53\x20\x20"
            b"\x20\x4C\x44\x20\x48\x4C\x2C\x31\x36\x33\x38\x34\x0A\x34\x30\x30"
            b"\x31\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x44\x45\x2C\x31"
            b"\x36\x33\x38\x35\x0A\x34\x30\x30\x32\x30\x20\x20\x20\x20\x20\x20"
            b"\x20\x4C\x44\x20\x42\x43\x2C\x36\x31\x34\x33\x0A\x34\x30\x30\x33"
            b"\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x28\x48\x4C\x29\x2C"
            b"\x30\x0A\x34\x30\x30\x34\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44"
            b"\x49\x52\x0A\x34\x30\x30\x35\x30\x20\x20\x20\x20\x20\x20\x20\x4C"
            b"\x44\x20\x48\x4C\x2C\x32\x32\x35\x32\x38\x0A\x34\x30\x30\x36\x30"
            b"\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x44\x45\x2C\x32\x32\x35"
            b"\x32\x39\x0A\x34\x30\x30\x37\x30\x20\x20\x20\x20\x20\x20\x20\x4C"
            b"\x44\x20\x42\x43\x2C\x37\x36\x37\x0A\x34\x30\x30\x38\x30\x20\x20"
            b"\x20\x20\x20\x20\x20\x4C\x44\x20\x28\x48\x4C\x29\x2C\x37\x0A\x34"
            b"\x30\x30\x39\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x49\x52\x0A"
            b"\x34\x30\x31\x30\x30\x20\x20\x20\x20\x20\x20\x20\x58\x4F\x52\x20"
            b"\x41\x0A\x34\x30\x31\x31\x30\x20\x4F\x55\x54\x20\x28\x32\x35\x34"
            b"\x29\x2C\x41\x3A\x4C\x44\x20\x41\x2C\x37\x0A\x34\x30\x31\x31\x31"
            b"\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x28\x32\x33\x36\x32\x34"
            b"\x29\x2C\x41\x0A\x34\x30\x31\x32\x30\x20\x43\x48\x4F\x50\x45\x20"
            b"\x4C\x44\x20\x41\x2C\x32\x0A\x34\x30\x31\x33\x30\x20\x20\x20\x20"
            b"\x20\x20\x20\x43\x41\x4C\x4C\x20\x23\x31\x36\x30\x31\x0A\x34\x30"
            b"\x31\x34\x30\x20\x20\x20\x20\x20\x20\x20\x52\x45\x54\x0A\x34\x30"
            b"\x31\x35\x30\x20\x53\x48\x52\x20\x20\x20\x4C\x44\x20\x48\x4C\x2C"
            b"\x31\x35\x36\x31\x36\x0A\x34\x30\x31\x36\x30\x20\x20\x20\x20\x20"
            b"\x20\x20\x4C\x44\x20\x44\x45\x2C\x33\x30\x30\x30\x30\x0A\x34\x30"
            b"\x31\x37\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x42\x43\x2C"
            b"\x37\x36\x38\x0A\x34\x30\x31\x38\x30\x20\x20\x20\x20\x20\x20\x20"
            b"\x4C\x44\x49\x52\x0A\x34\x30\x31\x39\x30\x20\x20\x20\x20\x20\x20"
            b"\x20\x4C\x44\x20\x48\x4C\x2C\x33\x30\x30\x30\x30\x0A\x34\x30\x32"
            b"\x30\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x42\x2C\x39\x36"
            b"\x0A\x34\x30\x32\x31\x30\x20\x53\x48\x32\x20\x20\x20\x50\x55\x53"
            b"\x48\x20\x42\x43\x0A\x34\x30\x32\x32\x30\x20\x20\x20\x20\x20\x20"
            b"\x20\x4C\x44\x20\x42\x2C\x34\x0A\x34\x30\x32\x33\x30\x20\x53\x48"
            b"\x33\x20\x20\x20\x49\x4E\x43\x20\x48\x4C\x0A\x34\x30\x32\x34\x30"
            b"\x20\x20\x20\x20\x20\x20\x20\x44\x4A\x4E\x5A\x20\x53\x48\x33\x0A"
            b"\x34\x30\x32\x35\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x42"
            b"\x2C\x34\x0A\x34\x30\x32\x36\x30\x20\x53\x48\x34\x20\x20\x20\x4C"
            b"\x44\x20\x41\x2C\x28\x48\x4C\x29\x0A\x34\x30\x32\x37\x30\x20\x20"
            b"\x20\x20\x20\x20\x20\x52\x4C\x43\x41\x0A\x34\x30\x32\x38\x30\x20"
            b"\x20\x20\x20\x20\x20\x20\x4F\x52\x20\x28\x48\x4C\x29\x0A\x34\x30"
            b"\x32\x39\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x28\x48\x4C"
            b"\x29\x2C\x41\x0A\x34\x30\x33\x30\x30\x20\x20\x20\x20\x20\x20\x20"
            b"\x49\x4E\x43\x20\x48\x4C\x0A\x34\x30\x33\x31\x30\x20\x20\x20\x20"
            b"\x20\x20\x20\x44\x4A\x4E\x5A\x20\x53\x48\x34\x0A\x34\x30\x33\x32"
            b"\x30\x20\x20\x20\x20\x20\x20\x20\x50\x4F\x50\x20\x42\x43\x0A\x34"
            b"\x30\x33\x33\x30\x20\x20\x20\x20\x20\x20\x20\x44\x4A\x4E\x5A\x20"
            b"\x53\x48\x32\x0A\x34\x30\x33\x34\x30\x20\x20\x20\x20\x20\x20\x20"
            b"\x52\x45\x54\x0A\x34\x30\x33\x35\x30\x20\x53\x54\x41\x4E\x44\x20"
            b"\x4C\x44\x20\x48\x4C\x2C\x31\x35\x36\x31\x36\x0A\x34\x30\x33\x36"
            b"\x30\x20\x20\x20\x20\x20\x20\x20\x44\x45\x43\x20\x48\x0A\x34\x30"
            b"\x33\x37\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x28\x32\x33"
            b"\x36\x30\x36\x29\x2C\x48\x4C\x0A\x34\x30\x33\x38\x30\x20\x20\x20"
            b"\x20\x20\x20\x20\x52\x45\x54\x0A\x34\x30\x33\x39\x30\x20\x4E\x45"
            b"\x57\x53\x48\x20\x4C\x44\x20\x48\x4C\x2C\x41\x44\x52\x53\x48\x0A"
            b"\x34\x30\x34\x30\x30\x20\x20\x20\x20\x20\x20\x20\x44\x45\x43\x20"
            b"\x48\x0A\x34\x30\x34\x31\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44"
            b"\x20\x28\x32\x33\x36\x30\x36\x29\x2C\x48\x4C\x0A\x34\x30\x34\x32"
            b"\x30\x20\x20\x20\x20\x20\x20\x20\x52\x45\x54\x0A\x34\x30\x34\x33"
            b"\x30\x20\x46\x46\x49\x4C\x45\x20\x4C\x44\x20\x41\x2C\x28\x32\x30"
            b"\x37\x30\x38\x29\x0A\x34\x30\x34\x34\x30\x20\x20\x20\x20\x20\x20"
            b"\x20\x43\x50\x20\x30\x0A\x34\x30\x34\x35\x30\x20\x20\x20\x20\x20"
            b"\x20\x20\x4A\x52\x20\x5A\x2C\x4E\x46\x49\x4C\x45\x0A\x34\x30\x34"
            b"\x36\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x42\x2C\x41\x0A"
            b"\x34\x30\x34\x37\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x44"
            b"\x45\x2C\x31\x38\x34\x33\x32\x0A\x34\x30\x34\x38\x30\x20\x46\x46"
            b"\x32\x20\x20\x20\x4C\x44\x20\x48\x4C\x2C\x46\x4E\x41\x4D\x45\x0A"
            b"\x34\x30\x34\x39\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x28"
            b"\x50\x44\x45\x29\x2C\x44\x45\x0A\x34\x30\x35\x30\x30\x20\x20\x20"
            b"\x20\x20\x20\x20\x4C\x44\x20\x28\x50\x42\x43\x29\x2C\x42\x43\x0A"
            b"\x34\x30\x35\x31\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x42"
            b"\x2C\x38\x0A\x34\x30\x35\x32\x30\x20\x46\x46\x33\x20\x20\x20\x4C"
            b"\x44\x20\x41\x2C\x28\x44\x45\x29\x0A\x34\x30\x35\x33\x30\x20\x20"
            b"\x20\x20\x20\x20\x20\x43\x50\x20\x28\x48\x4C\x29\x0A\x34\x30\x35"
            b"\x34\x30\x20\x20\x20\x20\x20\x20\x20\x4A\x52\x20\x4E\x5A\x2C\x4E"
            b"\x45\x58\x54\x46\x0A\x34\x30\x35\x35\x30\x20\x20\x20\x20\x20\x20"
            b"\x20\x49\x4E\x43\x20\x44\x45\x0A\x34\x30\x35\x36\x30\x20\x20\x20"
            b"\x20\x20\x20\x20\x49\x4E\x43\x20\x48\x4C\x0A\x34\x30\x35\x37\x30"
            b"\x20\x20\x20\x20\x20\x20\x20\x44\x4A\x4E\x5A\x20\x46\x46\x33\x0A"
            b"\x34\x30\x35\x38\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x41"
            b"\x2C\x28\x44\x45\x29\x0A\x34\x30\x35\x39\x30\x20\x20\x20\x20\x20"
            b"\x20\x20\x43\x50\x20\x36\x39\x0A\x34\x30\x36\x30\x30\x20\x20\x20"
            b"\x20\x20\x20\x20\x4A\x52\x20\x4E\x5A\x2C\x4E\x45\x58\x54\x46\x0A"
            b"\x34\x30\x36\x31\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x48"
            b"\x4C\x2C\x36\x0A\x34\x30\x36\x32\x30\x20\x20\x20\x20\x20\x20\x20"
            b"\x41\x44\x44\x20\x48\x4C\x2C\x44\x45\x0A\x34\x30\x36\x33\x30\x20"
            b"\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x41\x2C\x28\x48\x4C\x29\x0A"
            b"\x34\x30\x36\x34\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x28"
            b"\x53\x45\x43\x29\x2C\x41\x0A\x34\x30\x36\x35\x30\x20\x20\x20\x20"
            b"\x20\x20\x20\x49\x4E\x43\x20\x48\x4C\x0A\x34\x30\x36\x36\x30\x20"
            b"\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x41\x2C\x28\x48\x4C\x29\x0A"
            b"\x34\x30\x36\x37\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x28"
            b"\x54\x52\x43\x29\x2C\x41\x0A\x34\x30\x36\x38\x30\x20\x20\x20\x20"
            b"\x20\x20\x20\x4A\x50\x20\x4C\x4F\x41\x32\x0A\x34\x30\x36\x39\x30"
            b"\x20\x4E\x45\x58\x54\x46\x20\x4C\x44\x20\x44\x45\x2C\x28\x50\x44"
            b"\x45\x29\x0A\x34\x30\x37\x30\x30\x20\x20\x20\x20\x20\x20\x20\x4C"
            b"\x44\x20\x48\x4C\x2C\x31\x36\x0A\x34\x30\x37\x31\x30\x20\x20\x20"
            b"\x20\x20\x20\x20\x41\x44\x44\x20\x48\x4C\x2C\x44\x45\x0A\x34\x30"
            b"\x37\x32\x30\x20\x20\x20\x20\x20\x20\x20\x45\x58\x20\x44\x45\x2C"
            b"\x48\x4C\x0A\x34\x30\x37\x33\x30\x20\x20\x20\x20\x20\x20\x20\x4C"
            b"\x44\x20\x42\x43\x2C\x28\x50\x42\x43\x29\x0A\x34\x30\x37\x34\x30"
            b"\x20\x20\x20\x20\x20\x20\x20\x44\x4A\x4E\x5A\x20\x46\x46\x32\x0A"
            b"\x34\x30\x37\x35\x30\x20\x4E\x46\x49\x4C\x45\x20\x43\x41\x4C\x4C"
            b"\x20\x4E\x45\x57\x53\x48\x0A\x34\x30\x37\x36\x30\x20\x20\x20\x20"
            b"\x20\x20\x20\x4C\x44\x20\x44\x45\x2C\x4D\x53\x47\x32\x0A\x34\x30"
            b"\x37\x37\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x42\x43\x2C"
            b"\x4D\x53\x47\x33\x2D\x4D\x53\x47\x32\x0A\x34\x30\x37\x38\x30\x20"
            b"\x20\x20\x20\x20\x20\x20\x43\x41\x4C\x4C\x20\x23\x32\x30\x33\x43"
            b"\x0A\x34\x30\x37\x38\x31\x20\x20\x20\x20\x20\x20\x20\x43\x41\x4C"
            b"\x4C\x20\x42\x45\x45\x50\x0A\x34\x30\x37\x38\x32\x20\x20\x20\x20"
            b"\x20\x20\x20\x4C\x44\x20\x44\x45\x2C\x4D\x53\x47\x33\x0A\x34\x30"
            b"\x37\x38\x33\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x42\x43\x2C"
            b"\x54\x52\x43\x2D\x4D\x53\x47\x33\x0A\x34\x30\x37\x38\x34\x20\x20"
            b"\x20\x20\x20\x20\x20\x43\x41\x4C\x4C\x20\x23\x32\x30\x33\x43\x0A"
            b"\x34\x30\x38\x30\x30\x20\x43\x41\x4C\x4C\x20\x50\x41\x55\x53\x3A"
            b"\x43\x41\x4C\x4C\x20\x53\x54\x41\x4E\x44\x0A\x34\x30\x38\x31\x30"
            b"\x20\x20\x20\x20\x20\x20\x20\x4A\x50\x20\x4C\x4F\x41\x44\x0A\x34"
            b"\x30\x38\x32\x30\x20\x50\x41\x55\x53\x20\x20\x58\x4F\x52\x20\x41"
            b"\x0A\x34\x30\x38\x33\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x20"
            b"\x28\x32\x33\x35\x36\x30\x29\x2C\x41\x0A\x34\x30\x38\x34\x30\x20"
            b"\x50\x41\x32\x20\x20\x20\x4C\x44\x20\x41\x2C\x28\x32\x33\x35\x36"
            b"\x30\x29\x0A\x34\x30\x38\x35\x30\x20\x20\x20\x20\x20\x20\x20\x43"
            b"\x50\x20\x30\x0A\x34\x30\x38\x36\x30\x20\x20\x20\x20\x20\x20\x20"
            b"\x52\x45\x54\x20\x4E\x5A\x0A\x34\x30\x38\x37\x30\x20\x20\x20\x20"
            b"\x20\x20\x20\x4A\x52\x20\x50\x41\x32\x0A\x34\x30\x38\x38\x30\x20"
            b"\x42\x45\x45\x50\x20\x20\x4C\x44\x20\x44\x45\x2C\x23\x30\x31\x30"
            b"\x35\x0A\x34\x30\x38\x39\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44"
            b"\x20\x48\x4C\x2C\x23\x30\x36\x36\x36\x0A\x34\x30\x39\x30\x30\x20"
            b"\x20\x20\x20\x20\x20\x20\x43\x41\x4C\x4C\x20\x23\x30\x33\x42\x35"
            b"\x0A\x34\x30\x39\x31\x30\x20\x20\x20\x20\x20\x20\x20\x52\x45\x54"
            b"\x0A\x34\x30\x39\x32\x30\x20\x4C\x4F\x41\x44\x20\x20\x4C\x44\x20"
            b"\x48\x4C\x2C\x32\x32\x35\x36\x30\x0A\x34\x30\x39\x33\x30\x20\x20"
            b"\x20\x20\x20\x20\x20\x4C\x44\x20\x44\x45\x2C\x32\x32\x35\x36\x31"
            b"\x0A\x34\x30\x39\x34\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x20"
            b"\x42\x43\x2C\x37\x33\x36\x0A\x34\x30\x39\x35\x30\x20\x20\x20\x20"
            b"\x20\x20\x20\x4C\x44\x20\x28\x48\x4C\x29\x2C\x30\x0A\x34\x30\x39"
            b"\x36\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x49\x52\x0A\x34\x30"
            b"\x39\x37\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x42\x43\x2C"
            b"\x23\x30\x39\x30\x35\x0A\x34\x30\x39\x38\x30\x20\x20\x20\x20\x20"
            b"\x20\x20\x4C\x44\x20\x44\x45\x2C\x30\x0A\x34\x30\x39\x39\x30\x20"
            b"\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x48\x4C\x2C\x31\x38\x34\x33"
            b"\x32\x0A\x34\x31\x30\x30\x30\x20\x20\x20\x20\x20\x20\x20\x43\x41"
            b"\x4C\x4C\x20\x31\x35\x36\x33\x35\x0A\x34\x31\x30\x31\x30\x20\x20"
            b"\x20\x20\x20\x20\x20\x4A\x50\x20\x46\x46\x49\x4C\x45\x0A\x34\x31"
            b"\x30\x32\x30\x20\x4C\x4F\x41\x32\x20\x20\x4C\x44\x20\x41\x2C\x28"
            b"\x53\x45\x43\x29\x0A\x34\x31\x30\x33\x30\x20\x20\x20\x20\x20\x20"
            b"\x20\x4C\x44\x20\x45\x2C\x41\x0A\x34\x31\x30\x34\x30\x20\x20\x20"
            b"\x20\x20\x20\x20\x4C\x44\x20\x41\x2C\x28\x54\x52\x43\x29\x0A\x34"
            b"\x31\x30\x35\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x44\x2C"
            b"\x41\x0A\x34\x31\x30\x36\x30\x20\x20\x20\x20\x20\x20\x20\x4C\x44"
            b"\x20\x42\x43\x2C\x23\x32\x36\x30\x35\x0A\x34\x31\x30\x37\x30\x20"
            b"\x20\x20\x20\x20\x20\x20\x4C\x44\x20\x48\x4C\x2C\x33\x30\x30\x30"
            b"\x30\x0A\x34\x31\x30\x38\x30\x20\x20\x20\x20\x20\x20\x20\x43\x41"
            b"\x4C\x4C\x20\x31\x35\x36\x33\x35\x0A\x34\x31\x30\x39\x30\x20\x20"
            b"\x20\x20\x20\x20\x20\x4A\x50\x20\x33\x31\x36\x39\x33\x0A\x36\x30"
            b"\x30\x30\x30\x20\x41\x44\x52\x53\x48\x20\x45\x51\x55\x20\x33\x30"
            b"\x30\x30\x30\x0A\x36\x30\x30\x31\x30\x20\x4D\x53\x47\x31\x20\x20"
            b"\x44\x45\x46\x42\x20\x32\x32\x2C\x30\x2C\x30\x2C\x31\x37\x2C\x30"
            b"\x0A\x36\x30\x30\x32\x30\x20\x20\x20\x20\x20\x20\x20\x44\x45\x46"
            b"\x42\x20\x31\x36\x2C\x37\x0A\x36\x30\x30\x33\x30\x20\x44\x45\x46"
            b"\x4D\x20\x22\x46\x4F\x4E\x54\x20\x45\x44\x49\x54\x4F\x52\x20\x62"
            b"\x79\x20\x4C\x79\x61\x22\x0A\x36\x30\x30\x34\x30\x20\x44\x45\x46"
            b"\x4D\x20\x22\x64\x76\x69\x6E\x73\x6B\x79\x20\x4B\x69\x72\x69\x6C"
            b"\x6C\x22\x0A\x36\x30\x30\x35\x30\x20\x46\x4E\x41\x4D\x45\x20\x44"
            b"\x45\x46\x4D\x20\x22\x65\x64\x69\x74\x6F\x72\x20\x20\x22\x0A\x36"
            b"\x30\x30\x36\x30\x20\x50\x44\x45\x20\x20\x20\x44\x45\x46\x57\x20"
            b"\x30\x0A\x36\x30\x30\x37\x30\x20\x50\x42\x43\x20\x20\x20\x44\x45"
            b"\x46\x57\x20\x30\x0A\x36\x30\x30\x38\x30\x20\x4D\x53\x47\x32\x20"
            b"\x20\x44\x45\x46\x42\x20\x32\x32\x2C\x35\x2C\x30\x2C\x31\x37\x2C"
            b"\x30\x0A\x36\x30\x30\x39\x30\x20\x44\x45\x46\x42\x20\x31\x36\x2C"
            b"\x37\x2C\x31\x39\x2C\x31\x0A\x36\x30\x31\x30\x30\x20\x44\x45\x46"
            b"\x4D\x20\x22\x46\x69\x6C\x65\x20\x27\x65\x64\x69\x74\x6F\x72\x20"
            b"\x20\x3C\x45\x3E\x27\x22\x0A\x36\x30\x31\x31\x30\x20\x44\x45\x46"
            b"\x4D\x20\x22\x20\x6E\x6F\x74\x20\x66\x6F\x75\x6E\x64\x22\x0A\x36"
            b"\x30\x31\x32\x30\x20\x4D\x53\x47\x33\x20\x20\x44\x45\x46\x42\x20"
            b"\x32\x32\x2C\x36\x2C\x30\x2C\x31\x37\x2C\x30\x0A\x36\x30\x31\x32"
            b"\x35\x20\x20\x20\x20\x20\x20\x20\x44\x45\x46\x42\x20\x31\x36\x2C"
            b"\x37\x2C\x31\x39\x2C\x30\x0A\x36\x30\x31\x33\x30\x20\x44\x45\x46"
            b"\x4D\x20\x22\x50\x52\x45\x53\x53\x20\x41\x4E\x59\x20\x4B\x45\x59"
            b"\x20\x46\x4F\x52\x20\x22\x0A\x36\x30\x31\x34\x30\x20\x44\x45\x46"
            b"\x4D\x20\x22\x52\x45\x4C\x4F\x41\x44\x20\x46\x49\x4C\x45\x22\x0A"
            b"\x36\x30\x31\x36\x30\x20\x54\x52\x43\x20\x20\x20\x44\x45\x46\x42"
            b"\x20\x30\x0A\x36\x30\x31\x37\x30\x20\x53\x45\x43\x20\x20\x20\x44"
            b"\x45\x46\x42\x20\x30\x0A\x36\x30\x31\x38\x30\x20\x45\x4E\x44\x32"
            b"\x20\x20\x4E\x4F\x50\x0A"
        )


if __name__ == '__main__':
    unittest.main()
