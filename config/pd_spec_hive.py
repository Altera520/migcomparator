#!/bin/sh/env python

import pandera as pa

type_map = {
    'tinyint':          pa.Int8,
    'smallint':         pa.Int16,
    'int':              pa.Int32,
    'integer':          pa.Int32,
    'bigint':           pa.Int64,
    'decimal':          pa.Float64,              # 0.13.0
    'numeric':          pa.Float64,              # 3.0.0
    'float':            pa.Float32,
    'double':           pa.Float64,
    'double precision': pa.Float64,              # 2.2.0
    'boolean':          pa.Bool,
    'char':             pa.String,                # 0.13.0
    'varchar':          pa.String,                # 0.12.0
    'binary':           pa.String,                # 0.8.0
    'date':             pa.String,                # 0.12.0
    'interval':         pa.String,                # 0.12.0
    'timestamp':        pa.String,                # 0.8.0
    'arrays':           None,               # 0.14
    'maps':             None,               # 0.14
    'structs':          None,
    'union':            None,               # 0.7.0
}