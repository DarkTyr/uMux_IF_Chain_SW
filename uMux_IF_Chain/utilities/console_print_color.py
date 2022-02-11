# -*- coding: utf-8 -*-
class Console_Print_Color():
    def __init__(self):
        # All are bright colors at the moment
        self.HEADER = '\033[95m'        # Magenta
        self.HEADER_DARK = '\033[35m'   # Dark Magenta
        self.OKBLUE = '\033[94m'        # Blue
        self.OKBLUE_DARK = '\033[34m'   # Dark Blue
        self.OKGREEN = '\033[92m'       # Green
        self.OKGREEN_DARK = '\033[32m'  # Dark Green
        self.WARNING = '\033[93m'       # Yellow
        self.WARNING_DARK = '\033[33m'  # Dark Yellow
        self.CRIT = '\033[91m'          # Red
        self.CRIT_DARK = '\033[31m'     # Dark Red
        self.ENDC = '\033[0m'           # End Character
        self.BOLD = '\033[1m'           # Bold, which doesn't really work
        self.UNDERLINE = '\033[4m'      # Underlines the text, which works in linux only

    def test(self):
        self.print_header('This is a print_header()')
        self.print_result('This is print_result()')
        self.print_info('This is print_info()')
        self.print_crit('This is print_ctri()')
        self.print_warning('This is print_warning()')
        self.print_norm('This is print_norm() which is a regular print')
        print(self.HEADER_DARK + 'This is a Header_DARK' + self.ENDC)
        print(self.OKBLUE_DARK + 'This is a OKBLUE_DARK' + self.ENDC)
        print(self.OKGREEN_DARK + 'This is a OKGREEN_DARK' + self.ENDC)
        print(self.WARNING_DARK + 'This is a WARNING_DARK' + self.ENDC)
        print(self.CRIT_DARK + 'This is a CRIT_DARK' + self.ENDC)
        print(self.BOLD + 'This is a BOLD' + self.ENDC)
        print(self.UNDERLINE + 'This is a UNDERLINE normal print' + self.ENDC)
        print(self.UNDERLINE + self.WARNING + 'This is a UNDERLINE warning print' + self.ENDC)

    def print_uheader(self, text):
        print(self.UNDERLINE + self.HEADER + text + self.ENDC + self.ENDC)

    def print_header(self, text):
        print(self.HEADER + text + self.ENDC)

    def print_result(self, text):
        print(self.OKGREEN + text + self.ENDC)

    def print_info(self, text):
        print(self.OKBLUE + text + self.ENDC)
    
    def print_norm(self, text):
        print(text)

    def print_warning(self, text):
        print(self.WARNING + text + self.ENDC)

    def print_crit(self, text):
        print(self.CRIT + text + self.ENDC)

def print_header(text):
    '''Prints as Magenta
    '''
    print('\033[95m' + text + '\033[0m')

def print_result(text):
    '''Prints as Green
    '''
    print('\033[92m' + text + '\033[0m')

def print_info(text):
    '''Prints as Blue
    '''
    print('\033[94m' + text + '\033[0m')

def print_norm(text):
    '''Prints as White
    '''
    print(text)

def print_warning(text):
    '''Prints as Yellow
    '''
    print('\033[93m' + text + '\033[0m')
    
def print_crit(text):
    '''Prints as Red
    '''
    print('\033[91m' + text + '\033[0m')


#the     '\033[30m' series are the darker colors.