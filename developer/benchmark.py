#!/usr/bin/env python
# coding:utf-8

import redis
import time

def bench(descr, func, cnt):
  start = time.time()
  func(cnt)
  print descr, time.time() - start

def without_pipelining(cnt):
  r = redis.Redis()
  [r.ping() for x in range(cnt)]

def with_pipelining(cnt):
  r = redis.Redis().pipeline()
  [r.ping() for x in range(cnt)]

if __name__ == '__main__':
  bench('without pipeline', without_pipelining, 10000)
  bench('   with pipeline', with_pipelining, 10000)

  


