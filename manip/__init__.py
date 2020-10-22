# Importa arquivos
import io_terminal
import expression
import grammar
import automata

import json
import os
from enum import IntEnum, auto, unique

@unique
class StructType(IntEnum):
    AUTOMATA = auto()
    EXPRESSION = auto()
    RGRAMMAR = auto()
    CFGRAMMAR = auto()

struct = {}
struct_type = 0

def menu():
    # Chama interface do menu
    inp = io_terminal.initial_menu()

    # Lógica da opção escolhida
    if inp == 0:
        input_menu()
    elif inp == 1:
        file_menu(True)

def input_menu():
    inp = io_terminal.input_menu()
    if inp == 0:
        finite_automata()
    elif inp == 1:
        regular_grammar()
    elif inp == 2:
        regular_expression()
    elif inp == 3:
        context_free_grammar()
    elif inp == 4:
        menu()

def file_menu(opening):
    global struct_type
    global struct

    file_path = ".save/"
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    if opening:
        file_name = io_terminal.open_file_menu()
        if os.path.isfile(file_path+file_name):
            save = []
            with open(file_path+file_name,"r") as f:
                save = json.loads(f.read())

            if save == "" or len(save) != 2:
                io_terminal.file_error()
            elif not save[0] in list(map(int,StructType)):
                io_terminal.file_error()
            else:
                struct_type = save[0]
                struct = save[1]
                print(struct)
        else:
            io_terminal.file_error()
        
    else:
        file_name = io_terminal.save_file_menu()
        with open(file_path+file_name,"w") as f:
            print(json.dumps([struct_type.value,struct]),file=f)
    
    if struct_type == StructType.AUTOMATA:
        finite_automata_menu()
    elif struct_type == StructType.EXPRESSION:
        regular_expression_menu()
    elif struct_type == StructType.RGRAMMAR:
        regular_grammar_menu()
    elif struct_type == StructType.CFGRAMMAR:
        io_terminal._nope()

def finite_automata():
    global struct_type
    global struct
    struct_type = StructType.AUTOMATA
    struct = io_terminal.automata_input()
    finite_automata_menu()

def finite_automata_menu():
    ret = False
    while True:
        inp = io_terminal.finite_automata_menu()
        if inp == 0: # Conversão para AFD
            io_terminal._nope()
        elif inp == 1: # Conversão para GR
            io_terminal._nope()
        elif inp == 2: # Reconhecimento de sentença
            sentence = io_terminal.sentence_input()
            belongs = automata.recognize_sentence(sentence,struct)
            io_terminal.recognize_sentence(belongs)
        elif inp == 3: # Minimização
            io_terminal._nope()
        elif inp == 4: # União
            io_terminal._nope()
        elif inp == 5: # Interseção
            io_terminal._nope()
        elif inp == 6: # Editar
            io_terminal._nope()
        elif inp == 7: # Salvar
            file_menu(False)
        elif inp == 8: # Menu
            ret = True
            break
        else: # Sair
            break
    if ret:
        menu()

def regular_grammar():
    global struct_type
    global struct
    struct_type = StructType.RGRAMMAR
    struct = io_terminal.grammar_input(0)
    regular_grammar_menu()

def regular_grammar_menu():
    ret = False
    while True:
        inp = io_terminal.regular_grammar_menu()
        if inp == 0: # Conversão para AFND
            io_terminal._nope()
        elif inp == 1: # Editar
            io_terminal._nope()
        elif inp == 2: # Salvar
            file_menu(False)
        elif inp == 3: # Menu
            ret = True
            break
        else: # Sair
            break
    if ret:
        menu()

def regular_expression():
    global struct_type
    global struct
    struct_type = StructType.EXPRESSION
    struct = io_terminal.expression_input()
    regular_expression_menu()

def regular_expression_menu():
    ret = False
    while True:
        inp = io_terminal.regular_expression_menu()
        if inp == 0: # Conversão para AFD
            io_terminal._nope()
        elif inp == 1: # Editar
            io_terminal._nope()
        elif inp == 2: # Salvar
            file_menu(False)
        elif inp == 3: # Menu
            ret = True
            break
        else: # Sair
            break
    if ret:
        menu()

def context_free_grammar():
    io_terminal._nope()
    menu()

if __name__ == "__main__":
    menu()
