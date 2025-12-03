## 查看内存使用

```bash
# 查看类的实例个数和内存占用情况
jmap -histo {pid}
```

## 导出内存镜像

*方法1*
```bash
jmap -dump:live,format=b,file=heap-live.hprof <pid>
```

区别：
* live → 执行 Full GC，只导出“存活”的对象
* 非 live → 可能包含已死但未 GC 的对象

*方法2* 从 JDK 8u40+ 开始, 官方推荐使用
```bash
jcmd 12345 GC.heap_dump /tmp/heap.hprof
```

*jcmd 在执行 `GC.heap_dump` 时会触发一次 **安全点（SafePoint）GC 标记**，确保 dump 中只有存活对象*
所以结论就是jcmd默认就是导出live对象

查看某个进程使用的内存
```bash
top -p {pid}

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND
  376 root      20   0   12.1g   1.7g  16028 S  62.3  1.4  76:49.55 java
```