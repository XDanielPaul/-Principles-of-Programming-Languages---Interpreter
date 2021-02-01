import xml.etree.ElementTree as ET
import re
import sys


class Interpret():

    fp = None
    jump = None
    calladdup = 0

    # Processes arguements and loads XML
    def processArgs_and_loadXML(self):
        #Processing ARGS
        if (len(sys.argv) == 3):
            if ("--source=" in sys.argv[1] and "--input=" in sys.argv[2]):
                xmlfile = sys.argv[1].split("=",1)[1]
                inputfile = sys.argv[2].split("=",1)[1]
            elif ("--input=" in sys.argv[1] and "--source=" in sys.argv[2]):
                inputfile = sys.argv[1].split("=",1)[1]
                xmlfile = sys.argv[2].split("=",1)[1]
            else:
                sys.stderr.write("Wrong parameter.")
                sys.exit(10)
        elif (len(sys.argv) == 2):
            if ("--source=" in sys.argv[1]):
                xmlfile = sys.argv[1].split("=",1)[1]
            elif ("--input=" in sys.argv[1]):
                inputfile = sys.argv[1].split("=",1)[1]
                try:
                    self.fp = open(inputfile, 'r')
                except:
                    sys.exit(11)
                xmlfile = input()
            elif ("--help" in sys.argv[1]):
                print("Interpreter is used either by python3.8 interpreter.py and entering either argument --source=FILE or --input=FILE (unspecifyied argument expects stdin as input) or entering both")
                sys.exit(0)
            else:
                sys.stderr.write("ERROR")
                sys.exit(10)
        else:
            sys.stderr.write("ERROR")
            sys.exit(10)

        #Loading XML
        try:
            tree = ET.parse(xmlfile)
            return tree.getroot()
        except:
            sys.stderr.write("Not a valid file")
            sys.exit(31)

    # Loads XML
    def interpret(self):
        self.root = self.processArgs_and_loadXML()
        if (self.root.tag != "program" or self.root.attrib['language'] != "IPPcode20"):
            sys.exit(32)
        self.count = 0
        self.processInstructions()
        
    # Checks Syntax of instructions and arguments and returns orders of instructions
    def checkSyntax(self):
        order = []
        
        instr_codes = ["MOVE","CREATEFRAME","PUSHFRAME","POPFRAME","DEFVAR","CALL","RETURN","PUSHS","POPS","ADD","SUB","MUL","IDIV","LT","GT","EQ","AND","NOT","OR","INT2CHAR","STR2INT","READ","WRITE","CONCAT","STRLEN","GETCHAR","SETCHAR","TYPE","LABEL","JUMP","JUMPIFEQ","JUMPIFNEQ","EXIT","DPRINT","BREAK"]
        for arg in self.root:
            try:
                if (arg.tag != "instruction" or arg.attrib['opcode'].upper() not in instr_codes):
                    sys.exit(32)
                try:
                    if(int(arg.attrib['order']) in order or int(arg.attrib['order']) <= 0):
                        sys.exit(32)
                    order.append(int(arg.attrib['order']))
                except:
                    sys.exit(32)
                cnt = 1
                for ar in arg:
                    if(ar.tag != "arg"+str(cnt)):
                        sys.exit(32)
                    cnt += 1
            except:
                sys.exit(32)
        return order

    # Processes instructions
    def processInstructions(self):
        
        # Sorted order of instructions 
        order = sorted(self.checkSyntax())

        #Preloads labels
        for arg in self.root:
            if (arg.attrib['opcode'].upper() == "LABEL" and arg[0].attrib['type'] == "label"):
                Label.append(arg[0].text ,arg.attrib['order'])

        # Loop processing instructions
        while (self.count != len(self.root)):
            for arg in self.root:
                if (int(arg.attrib['order']) == order[self.count]):
                    # Loads Instruction object
                    instruction = Instruction(arg, arg.attrib['opcode'])
                    # Interprets instruction
                    instruction.resolveInstruction()
            self.count += 1
            # Resolves jump or return
            if (Interpret.jump != None):
                self.count = order.index(Interpret.jump)
                self.count += Interpret.calladdup
                Interpret.calladdup = 0
                Interpret.jump = None

class Instruction():

    call_stack = []
    stack = []

    def __init__(self, instruction, opcode):
        #### self.instruction[0].text = >GF@counter<
        #### self.instruction[0].tag = arg1
        #### self.instruction[0].attrib = {'type': 'string'}
        self.opcode = opcode.upper()
        self.instruction = instruction
        self.args = self.loadArgs()
        
    # Checks number and type of args and interprets instructions
    def resolveInstruction(self):
        if (self.opcode == "DEFVAR"):
           self.checkArgs(Variable)
           Frames.append(self.args.get('arg1').name)
        elif (self.opcode == "MOVE"):
            self.checkArgs(Variable, [Variable,Constant])
            Frames.initialize(self.args.get('arg1').name, self.args.get('arg2'))
        elif (self.opcode == "READ"):
            self.checkArgs(Variable, ['int', 'string', 'bool'])
            self.IREAD(self.args.get('arg1'), self.args.get('arg2'))
        elif (self.opcode == "WRITE"):
            self.checkArgs([Variable,Constant])
            self.IWRITE(self.getSymbValue(self.args.get('arg1')))
        elif (self.opcode == "CREATEFRAME"):
            Frames.tempFrame = {}
        elif (self.opcode == "PUSHFRAME"):
            if (Frames.tempFrame == None):
                sys.exit(55)
            Frames.frame_stack.append(Frames.tempFrame)
            Frames.localFrame = Frames.frame_stack[-1]
        elif (self.opcode == "POPFRAME"):
            if (Frames.localFrame == None):
                sys.exit(55)
            Frames.frame_stack.pop()
            Frames.localFrame = None
        elif (self.opcode == "CONCAT"):
            self.checkArgs(Variable, [Variable,Constant], [Variable,Constant])
            self.ICONCAT(self.getSymbValue(self.args.get('arg2')),self.getSymbValue(self.args.get('arg3')))
        elif (self.opcode == "STRLEN"):
            self.checkArgs(Variable, [Variable,Constant])
            self.ISTRLEN(self.args.get('arg1'), self.getSymbValue(self.args.get('arg2')))
        elif (self.opcode == "GETCHAR"):
            self.checkArgs(Variable, [Variable,Constant], [Variable,Constant])
            self.IGETCHAR(self.args.get('arg1'),self.getSymbValue(self.args.get('arg2')), self.getSymbValue(self.args.get('arg3')))
        elif (self.opcode == "SETCHAR"):
            self.checkArgs(Variable, [Variable,Constant], [Variable,Constant])
            self.ISETCHAR(self.args.get('arg1'),self.getSymbValue(self.args.get('arg2')), self.getSymbValue(self.args.get('arg3')))
        elif (self.opcode == "STRI2INT"):
            self.checkArgs(Variable, [Variable,Constant], [Variable,Constant])
            self.ISTRI2INT(self.args.get('arg1'),self.getSymbValue(self.args.get('arg2')), self.getSymbValue(self.args.get('arg3')))
        elif (self.opcode == "INT2CHAR"):
            self.checkArgs(Variable, [Variable,Constant])
            self.IINT2CHAR(self.args.get('arg1'),self.getSymbValue(self.args.get('arg2')))
        elif (self.opcode == "AND"):
            self.checkArgs(Variable, [Variable,Constant], [Variable,Constant])
            self.IAND(self.args.get('arg1'), self.getSymbValue(self.args.get('arg2')),  self.getSymbValue(self.args.get('arg3')))
        elif (self.opcode == "OR"):
            self.checkArgs(Variable, [Variable,Constant], [Variable,Constant])
            self.IOR(self.args.get('arg1'), self.getSymbValue(self.args.get('arg2')),  self.getSymbValue(self.args.get('arg3'))) 
        elif (self.opcode == "NOT"):
            self.checkArgs(Variable, [Variable,Constant])
            self.INOT(self.args.get('arg1'), self.getSymbValue(self.args.get('arg2')))
        elif (self.opcode == "LT"):
            self.checkArgs(Variable, [Variable,Constant], [Variable,Constant])
            self.ILT(self.args.get('arg1'), self.getSymbValue(self.args.get('arg2')), self.getSymbValue(self.args.get('arg3')))
        elif (self.opcode == "GT"):
            self.checkArgs(Variable, [Variable,Constant], [Variable,Constant])
            self.IGT(self.args.get('arg1'), self.getSymbValue(self.args.get('arg2')), self.getSymbValue(self.args.get('arg3')))
        elif (self.opcode == "EQ"):
            self.checkArgs(Variable, [Variable,Constant], [Variable,Constant])
            self.IEQ(self.args.get('arg1'), self.getSymbValue(self.args.get('arg2')), self.getSymbValue(self.args.get('arg3')))
        elif (self.opcode == "JUMP"):
            self.checkArgs(Label)
            if (self.args.get('arg1').name in Label.labels):
                Interpret.jump = ((int(Label.labels.get(self.args.get('arg1').name))))
        elif (self.opcode == "JUMPIFEQ"):
            self.checkArgs(Label, [Variable,Constant], [Variable,Constant])
            self.IEQUAL(self.args.get('arg1'),self.getSymbValue(self.args.get('arg2')), self.getSymbValue(self.args.get('arg3')))
        elif (self.opcode == "JUMPIFNEQ"):
            self.checkArgs(Label, [Variable,Constant], [Variable,Constant])
            self.INEQUAL(self.args.get('arg1'),self.getSymbValue(self.args.get('arg2')), self.getSymbValue(self.args.get('arg3')))
        elif (self.opcode == "ADD"):
            self.checkArgs(Variable, [Variable, Constant], [Variable, Constant])
            self.IADD(self.args.get('arg1'),self.getSymbValue(self.args.get('arg2')), self.getSymbValue(self.args.get('arg3')))
        elif (self.opcode == "SUB"):
            self.checkArgs(Variable, [Variable, Constant], [Variable, Constant])
            self.ISUB(self.args.get('arg1'),self.getSymbValue(self.args.get('arg2')), self.getSymbValue(self.args.get('arg3')))
        elif (self.opcode == "MUL"):
            self.checkArgs(Variable, [Variable, Constant], [Variable, Constant])
            self.IMUL(self.args.get('arg1'),self.getSymbValue(self.args.get('arg2')), self.getSymbValue(self.args.get('arg3')))
        elif (self.opcode == "IDIV"):
            self.checkArgs(Variable, [Variable, Constant], [Variable, Constant])
            self.IDIV(self.args.get('arg1'),self.getSymbValue(self.args.get('arg2')), self.getSymbValue(self.args.get('arg3')))
        elif (self.opcode == "TYPE"):
            self.checkArgs(Variable , [Variable, Constant])
            self.ITYPE(self.args.get('arg1'),self.getSymbValue(self.args.get('arg2')))
        elif (self.opcode == "PUSHS"):
            self.checkArgs([Variable, Constant])
            Instruction.stack.append(self.getSymbValue(self.args.get('arg1')))
        elif (self.opcode == "POPS"):
            self.checkArgs(Variable)
            Frames.setValue(self.args.get('arg1').name, Instruction.stack[-1])
            Instruction.stack.pop()
        elif (self.opcode == "CALL"):
            self.checkArgs(Label)
            Instruction.call_stack.append(self.instruction.attrib['order'])
            if (self.args.get('arg1').name in Label.labels):
                Interpret.jump = (int(Label.labels.get(self.args.get('arg1').name)))
        elif (self.opcode == "RETURN"):
            if (not Instruction.call_stack):
                sys.exit(56)
            else:
                Interpret.jump = (int(Instruction.call_stack[-1]))
                Interpret.calladdup = 1
                Instruction.call_stack.pop()
        elif (self.opcode == "DPRINT"):
            self.checkArgs([Variable, Constant])
            sys.stderr.write(self.getSymbValue(self.args.get('arg1')))
        elif (self.opcode == "BREAK"):
            sys.stderr.write("\n" + "Instruction order: " + self.instruction.attrib['order'] + "\n")
            sys.stderr.write("Current instruction: " + self.instruction.attrib['opcode']+ "\n")
            sys.stderr.write("Global frame: " + str(Frames.globalFrame)+ "\n")
            sys.stderr.write("Local frame " + str(Frames.localFrame)+ "\n")
            sys.stderr.write("Temporary frame: " + str(Frames.tempFrame)+ "\n")
        elif (self.opcode == "EXIT"):
            self.checkArgs([Variable,Constant])
            val = self.getSymbValue(self.args.get('arg1'))
            if (type(val) == int and val >= 0 and val <= 49):
                sys.exit(val)
            else:
                sys.exit(57)
        else:
            #Label
            pass

    # Checks number and type of arguments
    def checkArgs(self, *arguments):
        i = 0
        # Checking number of arguments
        if (len(arguments) != len(self.args)):
            sys.exit(32)

        # Checking type of arguments
        for arg in self.args.values():
            # If its [Variable, Constant]
            if (isinstance(arguments[i],list)):
                if (arg in arguments[i] or isinstance(arg,arguments[i][0]) or isinstance(arg,arguments[i][1])):
                    i = i+1
                else:
                    sys.exit(53)
            # If its explicitly one type of object
            elif (isinstance(arg, arguments[i])):
                i = i+1
            else:
                sys.exit(53)

    # Loads arguments into dictionary
    def loadArgs(self):
        args = {}
        for arg in self.instruction:
            args.update({arg.tag : self.resolveType(arg)})
        return args

    # Resolves type of argument
    def resolveType(self, arg):
        if (arg.attrib['type'] == 'var'):
            return Variable(arg.text)        
        elif (arg.attrib['type'] in ['string','int','nil','bool']):
            return Constant(arg)
        elif (arg.attrib['type'] == 'label'):
            return Label(arg.text)
        elif (arg.attrib['type'] == 'type'):
            if (arg.text in ['int', 'string', 'bool']):
                return arg.text
            else:
                sys.exit(53)
        else:
            sys.exit(53)

    def IREAD(self, var, _type):
        if (Interpret.fp != None):
            line = Interpret.fp.readline()
        else:
            line = input()
        
        if (_type == 'string'):
            line = str(line)
        elif (_type == 'bool' and line == 'true' or line == 'false'):
            line = bool(line.capitalize())
        elif (_type == 'int'):
            line = int(line)
        else:
            line = ""

        Frames.setValue(var.name, line)

    def IWRITE(self, content):
        if (type(content) == bool):
            content = str(content).lower()
        print(content, end='')

    def ICONCAT(self, symb1, symb2):
        Frames.setValue(self.args.get('arg1').name,(str(symb1) + str(symb2)))

    def IEQUAL(self,label, symb1, symb2):
        if (type(symb1) == type(symb2)):
            if(symb1 == symb2): 
                if (label.name in Label.labels):
                    Interpret.jump = int(Label.labels.get(label.name))

    def INEQUAL(self,label, symb1, symb2):
        if (type(symb1) == type(symb2)):
            if(symb1 != symb2): 
                if (label.name in Label.labels):
                    Interpret.jump = int(Label.labels.get(label.name))

    def ILT(self, var, symb1, symb2):
        if (type(symb1) == type(symb2)):
            try:
                Frames.setValue(var.name, symb1 < symb2)
            except:
                sys.exit(53)
        else:
            sys.exit(53)

    def IGT(self, var, symb1, symb2):
        if (type(symb1) == type(symb2)):
            try:
                Frames.setValue(var.name, symb1 > symb2)
            except:
                sys.exit(53)
        else:
            sys.exit(53)

    def IEQ(self, var, symb1, symb2):
        if (type(symb1) == type(symb2)):
            try:
                Frames.setValue(var.name, symb1 == symb2)
            except:
                sys.exit(53)
        else:
            sys.exit(53)

    def IADD(self, var, symb1, symb2):
        if (type(symb1) == int and type(symb2) == int):
            Frames.setValue(var.name, int(symb1+symb2))
        else:
            sys.exit(53)

    def ISUB(self,var,symb1,symb2):
        if (type(symb1) == int and type(symb2) == int):
            Frames.setValue(var.name, int(symb1-symb2))
        else:
            sys.exit(53)

    def IMUL(self,var,symb1,symb2):
        if (type(symb1) == int and type(symb2) == int):
            Frames.setValue(var.name, int(symb1*symb2))
        else:
            sys.exit(53)

    def IDIV(self,var,symb1,symb2):
        if (type(symb1) == int and type(symb2) == int):
            if (symb2 == 0):
                sys.exit(57)
            Frames.setValue(var.name, int(symb1//symb2))
        else:
            sys.exit(53)

    def ISTRLEN(self,var,symb):
        if (type(symb) == str):
            Frames.setValue(var.name, len(symb))
        else:
            sys.exit(53)

    def IGETCHAR(self,var, symb1, symb2):
        if (type(symb1) == str and type(symb2) == int):
            try:
                Frames.setValue(var.name, symb1[symb2])
            except:
                sys.exit(58)
        else:
            sys.exit(53)

    def ISETCHAR(self, var, symb1, symb2):
        var_val = Frames.getValue(var.name)
        if (type(var) == str and type(symb1) == int and type(symb2) == str):
            try:
                var_val[symb1] = symb2[0]
                Frames.setValue(var.name, var_val)
            except:
                sys.exit(58)
        else:
            sys.exit(53)

    def ITYPE(self, var, symb):
        if (type(symb) == str):
            Frames.setValue(var.name, "string")
        elif (type(symb) == int):
            Frames.setValue(var.name, "int")
        elif (type(symb) == bool):
            Frames.setValue(var.name, "bool")
        elif (symb == None):
            Frames.setValue(var.name, "")
        else:
            sys.exit(53)

    def IINT2CHAR(self, var, symb):
        if(type(symb) == int):
            try:
                Frames.setValue(var.name, chr(symb))
            except:
                sys.exit(58)
        else:
            sys.exit(53)

    def ISTRI2INT(self, var, symb1, symb2):
        if (type(symb1) == str and type(symb2) == int):
            try:
                Frames.setValue(var.name, ord(symb1[symb2]))
            except:
                sys.exit(58)
        else:
            sys.exit(53)

    def IAND(self, var, symb1, symb2):
        if (type(symb1) == bool and type(symb2) == bool):
            Frames.setValue(var.name, (symb1 and symb2))
        else:
            sys.exit(53)

    def IOR(self, var, symb1, symb2):
        if (type(symb1) == bool and type(symb2) == bool):
            Frames.setValue(var.name, (symb1 or symb2))
        else:
            sys.exit(53)

    def INOT(self, var, symb1):
        if (type(symb1) == bool):
            Frames.setValue(var.name, not(symb1))
        else:
            sys.exit(53)

    def getSymbValue(self,symb):
        if (isinstance(symb, Variable)):
            return Frames.getValue(symb.name)
        else:
            return symb.value

class Frames():

    globalFrame = {}
    localFrame = None
    tempFrame = None
    frame_stack = []

    # Defines variable in it's frame
    @classmethod
    def append(cls, name):
        frame = cls.resolveFrame(name)
        
        if (frame == None):
            sys.exit(55)

        if (name[3:] in frame):
            sys.exit(52)

        frame[name[3:]] = None

    # Gets a frame of variable
    @classmethod
    def resolveFrame(cls,name):
        if (name[:3] == "GF@"):
            return cls.globalFrame
        elif (name[:3] == "LF@"):
            return cls.localFrame
        elif (name[:3] == "TF@"):
            return cls.tempFrame
        else:
            sys.exit(57)

    # Checks if variable exists in the frame
    @classmethod
    def isinFrame(cls, name):
        frame = cls.resolveFrame(name)

        if (frame == None):
            sys.exit(55)

        if (name[3:] in frame):
            return True 
        else:
            return False

    # Gets value of a variable
    @classmethod
    def getValue(cls,name):
        if (Frames.isinFrame(name) == False):
            sys.exit(54)
        frame = cls.resolveFrame(name)
        return frame[name[3:]]

    # Sets value of a variable
    @classmethod
    def setValue(cls,name, value):
        if (Frames.isinFrame(name) == False):
            sys.exit(54)
        frame = cls.resolveFrame(name)
        frame[name[3:]] = value

    # Initializates variable
    @classmethod
    def initialize(cls, target, content):
        # Check if var is initialized
        if (Frames.isinFrame(target) == False):
            sys.exit(54)

        frame_target = cls.resolveFrame(target)

        # If content is variable
        if (isinstance(content, Variable)):
            content = content.name
            # Check if content var is initialized
            if (Frames.isinFrame(content) == False):
                sys.exit(54)

            frame_content = cls.resolveFrame(content)
            frame_target[target[3:]] = frame_content[content[3:]]

        # If content is constant
        elif (isinstance(content, Constant)):
            frame_target[target[3:]] = content.value

# Variable object
class Variable():

    def __init__(self, name):
        self.name = name

# Label object
class Label():
    
    labels = {}

    def __init__(self,name):
        self.name = name
    
    # Appends label to dictionary of labels
    @classmethod
    def append(cls,name, number):
        if (name in cls.labels):
            sys.exit(52)
        
        cls.labels.update({name : number})

# Constant object
class Constant():

    def __init__(self, argument):
        self.argument = argument
        self.value = self.resolvesymb()

    # Resolves type of constant
    def resolvesymb(self):
        # String constant
        if (self.argument.attrib['type'] == 'string'):
            if (self.argument.text == None):
                self.value = ''
            else:
                try:
                    self.value = str(self.argument.text)
                    # Converts escape sequences
                    escape_seq_list = list(set(re.findall(r"\\[0][0-9][0-9]", self.value)))
                    for esc_seq in escape_seq_list:
                        self.value = self.value.replace(esc_seq, chr(int(esc_seq[2:])))
                except:
                    sys.stderr.write("Invalid string value")
                    sys.exit(58)
        # Int constant
        elif (self.argument.attrib['type'] == 'int'):
            try:
                self.value = int(self.argument.text)
            except:
                sys.stderr.write("Invalid int value")
                sys.exit(32)
        # Bool constant
        elif (self.argument.attrib['type'] == 'bool'):
            if (self.argument.text.lower() == 'true'):
                self.value = True
            elif ( self.argument.text.lower() == 'false'):
                self.value = False
            else:
                sys.stderr.write("Invalid bool value")
                sys.exit(32)
        # Nil constant
        elif (self.argument.attrib['type'] == 'nil'):
            try:
                self.value = ''
            except:
                sys.stderr.write("Invalid nil")
                sys.exit(32)
        else:   
            sys.stderr.write("Wrong constant type")
            sys.exit(32)

        #Just in case I need type...
        self.type = self.argument.attrib['type']
        return self.value
    

    

def main():
    # Calls interpret class which runs interpret
    Interpret().interpret()
    # Closes input file if exists
    if (Interpret.fp != None):
        Interpret.fp.close()
    sys.exit(0)

main()


