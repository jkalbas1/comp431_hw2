#Joseph Kalbas 730414620
#All code in this file has been written solely by myself, Joseph Kalbas

from sys import stdin
import os
 
receivers = []
seen = ""
special = ["<", ">", "(", ")", "[", "]", "\\", ".", ",", ";", ":", "\"", "@"]
space = [" ", "\t"]
rc_loc = ""
rc_dom = ""
sender = ""

def mail_token(line):
    if(line[0:4] == "MAIL"):
        global seen
        seen += line[0:4]
        return True
    return False

def whitespace(line):
    global seen
    line = line.split(seen)[1]
    if(line[0] != " " and line[0] != "\t"):
        return False
    for sp in line:
        if sp == " " or sp == "\t":
            seen += sp
        else:
            return True

def from_token(line):
    global seen
    line = line.split(seen)[1]
    if line[0:5] != "FROM:":
        return False
    seen += line[0:5]
    return True

def nullspace(line):
    global seen
    whitespace(line)
    return True

def local_part(line):
    global seen
    global rc_loc
    rc_loc = ""
    line = line.split(seen)[1]
    count = 0
    for sp in line:
        if sp in special or sp in space:
            if count == 0:
                print("501 syntax error in parameters or arguments")
                return False
            return True
        else:
            count+=1
            seen += sp
            rc_loc += sp
    return True

def domain(line):
    global seen
    global rc_dom
    rc_dom = ""
    line = line.split(seen)[1]
    count = 0
    run_count = 0
    for sp in line:
        if count == 0 and not sp.isalpha():
            print("501 syntax error in parameters or arguments")
            return False
        if sp == ".":
            seen += sp
            rc_dom += sp
            count = 0
            run_count += 1
            continue
        if sp.isalpha() or sp.isdigit():
            count += 1
            run_count += 1
            rc_dom += sp
            seen += sp
        else:
            break
    if line[run_count-1] == ".":
        print("501 syntax error in parameters or arguments")
        return False
    return True

def path(line):
    global seen
    copy_line = line.split(seen)[1]
    if(copy_line[0] != "<"):
        print("501 syntax error in parameters or arguments")
        return False
    seen += "<"
    if not local_part(line):
        return False
    copy_line = line.split(seen)[1]
    if(copy_line[0] != "@"):
        print("501 syntax error in parameters or arguments")
        return False
    
    seen += "@"

    if not domain(line):
        return False

    copy_line = line.split(seen)[1]
    if copy_line[0] != ">":
        print("501 syntax error in parameters or arguments")
        return False
    seen += ">"
    return True

def crlf(line):
    global seen
    copy_line = line.split(seen)[1]
    if copy_line[0] != "\n":
        print("501 syntax error in parameters or arguments")
        return False
    return True

def mail_from(line):
    global seen
    global sender
    seen = ""

    if not mail_token(line):
        print("500 Syntax error: command unrecognized")
        return False

    if not whitespace(line):
        print("500 Syntax error: command unrecognized")
        return False

    if not from_token(line):
        print("500 Syntax error: command unrecognized")
        return False

    nullspace(line)

    if not path(line):
        return False
    
    nullspace(line)

    if not crlf(line):
        return False
    
    sender = "<" + rc_loc + "@" + rc_dom + ">"
    return True

def to_token(line):
    global seen
    line = line.split(seen)[1]
    if line[0:3] == "TO:":
        seen += "TO:"
        return True
    return False

def rcpt(line):
    global seen
    global receivers
    seen = "RCPT"

    if not whitespace(line):
        print("500 Syntax error: command unrecognized")
        return False
    
    if not to_token(line):
        print("500 Syntax error: command unrecognized")
        return False
    
    nullspace(line)

    if not path(line):
        return False
    
    nullspace(line)

    if not crlf(line):
        return False

    receivers.append(rc_loc + "@" + rc_dom)
    return True
    
def data(line):
    global seen
    seen = "DATA"
    nullspace(line)
    if not crlf(line):
        print("500 Syntax error: command unrecognized")
        return False

    return True


#Hold a string representation of previous previous message
state = ""
data_seen = ""

#implement these below
sender = ""

for line in stdin:
    print(line, end="")

    if(line[0:4] == "MAIL"):
        if mail_from(line) and state == "":
            print("250 OK")
            state = "mail"
        elif state != "":
            print("503 Bad sequence of commands")
            state = ""
            receivers = []
            data_seen = ""
        else:
            state = ""
            receivers = []
            data_seen = ""
    elif(line[0:4] == "RCPT"):
        if rcpt(line):
            if state == "mail" or state == "rcpt":
                print("250 OK")
                ## add recipient to receivers list
                state = "rcpt"
            else:
                print("503 Bad sequence of commands")
                state = ""
                receivers = []
                data_seen = ""
        else:
            state = ""
            receivers = []
            data_seen = ""
    elif(line [0:4] == "DATA"):
        if data(line):
            if state == "rcpt":
                print("354 Start mail input; end with <CRLF>.<CRLF>")
                state = "DATA"
            else:
                print("503 Bad sequence of commands")
                state = ""
                receivers = []
                data_seen = ""
        else:
            state = ""
            receivers = []
            data_seen = ""
    else:
        if state == "DATA":
            if line == ".\n":
                print("250 OK")
                for add in receivers:
                    file = open("forward/" + add, "a+")
                    file.write("From: " + sender + "\n")
                    for rep in receivers:
                        file.write("To: <" + rep + ">\n")
                    file.write(data_seen)
                    file.close()

                state = ""
                data_seen = ""
                receivers = []
            else:
                data_seen += line
        else:
            print("500 Syntax error: command unrecognized")
            state = ""
            data_seen = ""
            receivers = []

