#!/bin/sh/env python

type_map = {
    'tinyint':          int,
    'smallint':         int,
    'int':              int,
    'integer':          int,
    'bigint':           int,
    'decimal':          float,              # 0.13.0
    'numeric':          float,              # 3.0.0
    'float':            float,
    'double':           float,
    'double precision': float,              # 2.2.0
    'boolean':          bool,
    'char':             str,                # 0.13.0
    'varchar':          str,                # 0.12.0
    'binary':           str,                # 0.8.0
    'date':             str,                # 0.12.0
    'interval':         str,                # 0.12.0
    'timestamp':        str,                # 0.8.0
    'arrays':           None,               # 0.14
    'maps':             None,               # 0.14
    'structs':          None,
    'union':            None,               # 0.7.0
}