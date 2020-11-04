from enum import Enum, auto
from collections import deque

class Error(Enum):
    NONE = auto()
    DEAD = auto()
    ALPHABET = auto()

def verify_input(state_count,alphabet,inp):
    ret = True
    inp = inp.split(",")
    if len(inp) != 3:
        ret = False
    elif not inp[0].isdecimal():
        ret = False
    else:
        inp[0] = int(inp[0])
        if inp[0] >= state_count:
            ret = False
        elif len(inp[1]) != 1:
            ret = False
        elif alphabet.count(inp[1]) == 0 and inp[1] != "":
            ret = False
        else:
            inp[2] = inp[2].split("-")
            for s in inp[2]:
                if s.isdecimal():
                    s = int(s)
                    if s >= state_count:
                        ret = False
                        break
                else:
                    ret = False
                    break
     
    return ret

def format_transitions(transitions):
    trans = {}
    for t in transitions:
        t = t.split(",")
        t[2] = t[2].split("-")
        if len(t[2]) > 1:
            for s in t[2]:
                new_s = t[0]+","+t[1]+","+s
                transitions.append(new_s)
            continue
        t[0] = int(t[0])
        t[2] = int(t[2][0])
        if t[0] not in trans:
            trans[t[0]] = {}
        if t[2] not in trans[t[0]]:
            trans[t[0]][t[2]] = []
        trans[t[0]][t[2]].append(t[1])
    return trans

def recognize_sentence(sentence,automata):
    belongs = Error.DEAD

    current_state = deque([automata["initial"]])
    current_char = deque([0])
    transitions = automata["transitions"]
    while len(current_char) > 0:
        for i in range(current_char[0],len(sentence)):
            char = sentence[i]
            if char not in automata["alphabet"]:
                belongs = Error.ALPHABET
                break
            elif str(current_state[0]) not in transitions:
                print(transitions)
                break
            else:
                if "&" in automata["alphabet"]: # Aumenta árvore do não-determinismo no epsilon
                    epsilon = _get_keys("&",transitions[str(current_state[0])])
                    for e in range(0,len(epsilon)):
                        current_state.append(epsilon[e])
                        current_char.append(current_char[0])
                
                next_states = _get_keys(char,transitions[str(current_state[0])])
                if len(next_states) < 1: # Verifica se tem transições pelo char no estado atual
                    break
                else:
                    current_state[0] = next_states[0]
                    current_char[0] = i+1
                    for j in range(1,len(next_states)): # Aumenta árvore do não-determinístico
                        current_state.append(next_states[j])
                        current_char.append(i+1)
        
        if "&" in automata["alphabet"] and str(current_state[0]) in transitions: # Verifica transições por epsilon no último estado
            epsilon = _get_keys("&",transitions[str(current_state[0])])
            for e in range(0,len(epsilon)):
                current_state.append(epsilon[e])
                current_char.append(current_char[0])
        
        print(current_state,"\n",current_char)

        if current_char[0] == len(sentence): # Verifica se consome toda a entrada
            if current_state[0] in automata["final"]: # Verifica se termina num estado final
                belongs = Error.NONE
                break

        current_state.popleft() # Para para próximo ramo da árvore
        current_char.popleft()
    
    return belongs

def determine_automata(automata,_count_start=0):
    epsilon = _get_epsilon_transitions(automata["transitions"])
    corresp = {}

    alphabet = set()
    transitions = {}
    count = _count_start
    final = set()

    this_state = {automata["initial"]}
    if automata["initial"] in epsilon:
        this_state = epsilon[automata["initial"]]
    next_states = []
    while True:
        sstr = str(this_state)
        if sstr in corresp:
            if str(corresp[sstr]) in transitions:
                if not next_states:
                    break
                this_state = next_states[0]
                del next_states[0]
                continue
            else:
                transitions[str(corresp[sstr])] = {}
        else:
            corresp[sstr] = count
            transitions[str(corresp[sstr])] = {}
            count += 1
        
        for s in this_state:
            if s in automata["final"]:
                final.add(corresp[sstr])
                break

        for a in automata["alphabet"]:
            if a == "&":
                continue
            aux = []
            for state in this_state:
                if str(state) in automata["transitions"]:
                    aux += _get_keys(a,automata["transitions"][str(state)])
                for s in aux:
                    if s in epsilon:
                        for e in epsilon[s]:
                            if e not in aux:
                                aux.append(e)
            aux = set(aux)

            if not aux:
                continue
            else:
                if a not in alphabet:
                    alphabet.add(a)

            if str(aux) not in corresp:
                corresp[str(aux)] = count
                count += 1
            
            transitions[str(corresp[sstr])][str(corresp[str(aux)])] = a
            if aux not in next_states:
                next_states.append(aux)

    new_aut = {}
    new_aut["count"] = count
    new_aut["initial"] = _count_start
    new_aut["final"] = []
    new_aut["final"] += final
    new_aut["alphabet"] = []
    new_aut["alphabet"] += alphabet
    new_aut["transitions"] = transitions

    return new_aut

def unite_automata(aut1,aut2):
    aut1 = determine_automata(aut1)
    aut2 = determine_automata(aut2,aut1["count"])
    alphabet = ["&"]
    alphabet += set(aut1["alphabet"]) | set(aut2["alphabet"])
    initial = aut2["count"]
    transitions = aut1["transitions"]
    transitions.update(aut2["transitions"])
    transitions[initial] = {str(aut1["initial"]):"&",str(aut2["initial"]):"&"}

    aut = {}
    aut["count"] = aut2["count"]+1
    aut["initial"] = initial
    aut["final"] = aut1["final"]+aut2["final"]
    aut["alphabet"] = alphabet
    aut["transitions"] = transitions
    aut = determine_automata(aut)

    return aut

def complement(automata):
    # O complemento precisa ser em cima de um autômato determinístico
    automata = determine_automata(automata)

    # Cria estado morto, para completar o autômato
    automata["transitions"][str(automata["count"])] = {}
    for a in automata["alphabet"]:
        if a == "&":
            continue
        automata["transitions"][str(automata["count"])][str(automata["count"])] = a
    automata["count"] += 1

    for state in range(0,automata["count"]):
        if state in automata["final"]: # Faz estados finais serem não-finais
            automata["final"].remove(state)
        else: # Faz estados não-finais serem finais
            automata["final"].append(state)
        
        for a in automata["alphabet"]: # Faz os estados transitarem pro morto
            if a == "&": # Ignora epsilon
                continue
            if not _get_keys(a,automata["transitions"][str(state)]):
                automata["transitions"][str(state)][str(automata["count"]-1)] = a
    
    return automata

def intersect_automata(aut1,aut2):
    # A interseção pode ser vista como o complemento da união dos complementos
    aut1 = complement(aut1)
    aut2 = complement(aut2)

    automata = unite_automata(aut1,aut2)
    automata = complement(automata)

    # TODO: Minimizar autômato.

    return automata

def _get_keys(value,dic):
    key = []
    for k,v in dic.items():
        if value in v:
            key.append(int(k))
    return key

def _get_epsilon_transitions(transitions):
    epsilon = {}
    for s,t in transitions.items():
        trans = _get_keys("&",t)
        if not trans:
            continue
        
        s = int(s)
        epsilon[s] = {s}
        
        while trans:
            e = trans[0]
            if e not in epsilon[s]:
                if e in transitions:
                    trans += _get_keys("&",transitions[e])
                epsilon[s].add(e)
            while e in trans:
                trans.remove(e)
        
        if epsilon[s] == {s}:
            del epsilon[s]
    
    return epsilon
