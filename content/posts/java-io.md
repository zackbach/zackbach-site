+++
title = 'Overview of Java I/O'
date = 2023-05-09T21:35:09-04:00
tags = ['Java']
+++

The `java.io` package is based on *streams*, a flow of data with a reader on one end and a writer at the other: either bytes or characters
- The newer `java.nio` package is based on *channels* which use "buffers" containing primitive data


## Streams
`InputStream` and `OutputStream` define functionality for reading/writing bytes
- `System.in` is an input stream, while `System.out` and `System.err` are output streams (technically `PrintStreams`, a subclass of `OutputStream`)
- `.read()` can be used to read a byte, `.write()` can be used to write a byte, etc
- `.close()` is used to close the stream after use, which should be done
    - You can also use the `try`-with-resources feature

`Reader` and `Writer` define functionality for reading/writing characters

`InputStreamReader` and `OutputStreamReader` take in an `InputStream` or `OutputStream` respectively and are themselves `Reader` or `Writer` respectively
- These use character-encoding schemes (uses system default by default)
- They "wrap around" byte streams to make a character stream

Each of these 4 streams have `Buffered` versions that are much faster
- `BufferedReader` wraps a `Reader` and adds a `readLine()` method
- A data buffer is added to the stream path, which is filled initially then read from quickly. For writing, a buffer is written to which is written to the actual stream only once the buffer is full
    - You can `.flush()` the buffer to write it to the underlying stream
These are examples of `FilterInputStream`, `FilterReader`, etc

Another example of filtered stream comes with `DataInputStream` and `DataOutputStream`, which allow for reading/writing more complex primitive data (like doubles, etc) from an input/output stream
- Ex: `.readDouble()`, `.writeInt()`, etc

`PrintWriter` allows for using `print` or `println` which turn their arguments into strings and push them out the stream
- `PrintWriter` can wrap either `OutputStream` *or* `Writer`
    - You can add a boolean to specify whether it should auto-flush whenever a newline is sent: data is sent line-by-line to a terminal/etc
- The `PrintStream` byte stream is a legacy class that just wraps `OutputStream`, seen in `System.out` and `System.err`
    - Use a `PrintWriter` in all cases
These classes never throw `IOException`s, rather they have a `.checkError()` method


## Files
`java.io.File` has information about a file/directory
- You can create a `new File(String)`, where the given string is a (relative or absolute) path
- This does not create a file or directory, just handle such a directory (you can use `.exists()`)
- Paths are annoying to deal with because they are OS-dependent, but you can access this character with `File.separatorChar`

There are a variety of operations we can perform / observations we can make
- `isFile(), isDirectory(), exists(), isAbsolute(), getName(), lastModified()`, etc
If the file refers to a directory, you can use `mkdir()` to try to make a single directory or `mkdirs()` to create all levels
- `.createNewFile()` attempts to create a new (zero-length) file at the location
- Commonly, we use file streams to create files/etc: see below

### File Streams
`FileInputStream` and `FileOutputStream` are byte-based streams for reading from and writing to files
- These can take pathnames (String) or `File` objects
- Like before, these can be combined with filter streams like buffered or data or print
    - You can wrap these in an `InputStreamReader` or `OutputStreamReader` to get character-based streams, or use `FileReader` and `FileWriter` which do this wrapping for you with some nice defaults

Get in the habit of handling `FileNotFoundException`s and `IOException`s
- You can use try-with-resources, which automatically closes too

While `FileReader` will throw a `FileNotFoundException` if the file is not found, `FileWriter` will either create a new file or overwrite the current contents of the file
- A common pattern will be to wrap a `FileWriter` in a `PrintWriter`
- Remember to `.close()`!

## NIO and Paths
The `java.nio.file` package is a more modern API for file interaction

You can use `FileSystem` alongside channels which are more modern, but probably outside of the scope of this OOD class

A `Path` is very similar to a `File` and can be created from a string (using a file system?)
- `Path`s are used by NIO's `Files` object which contains a lot of useful static methods for path operations
- You can use `myPath.toFile()` or `myFile.toPath()` to convert between the two
- `Path` has no constructor: you must use some sort of factory or `Path.of(String)`

The `Files` class has many powerful static methods:
- `createFile(), exists(), getAttribute(), getLastModifiedTime(), newBufferedReader(), newInputStream(), readAllLines(), walkFileTree(), write()`, etc: check documentation!

While `java.io` deals with streams, `java.nio` deals with channels
- Instead of reading bytes or characters, we deal with `ByteBuffer`s and `CharBuffer`s


## Scanners
When reading strings, we can parse the input into primitive types using `Integer.parseInt`, `Boolean.parseBoolean`, etc
- `Scanner`s allow us to parse individual primitive types from not only strings, but streams of tokens
- By default, spaces are used as delimiters, but `new Scanner(...).useDelimiter()` can be used to change that
    - You could also use `StringTokenizer(String, delimiter)` instead to delimit, checking `.hasMoreTokens()` and `.nextToken()`
    - This allows to use `BufferedReader`s instead of `Scanner`s
        - You could also use `StreamTokenizer` which is similar

See https://usaco.guide/general/fast-io?lang=java for some examples