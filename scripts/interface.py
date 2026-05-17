import os

from main import (
    CONFIGURE_VLAN,
    SHOW_VLAN,
    SET_INTERFACE_STATE,
    SHOW_RUNNING_CONFIG,
    CONFIGURE_TRUNK
)


def LIMPAR_TELA():
    os.system("cls" if os.name == "nt" else "clear")

def MENU():
    print("\n=== MENU DE CONFIGURAÇÃO DE SWITCH ===")
    print("\n1 - Configuração completa de VLAN")
    print("\n2 - Mostrar VLANs")
    print("\n3 - Ativar/Desativar Interface")
    print("\n4 - Mostrar Interface")
    print("\n5 - Configurar Trunk")
    print("\n0 - Sair")


def OBTER_IP():
    return input("\nDigite o IP do Switch: ")


# 🔹 1
def OPCAO_CONFIGURAR_VLAN():

    LIMPAR_TELA()

    print("=== CONFIGURAR VLAN ===")

    HOST = OBTER_IP()
    VLAN = input("ID da VLAN: ")
    VLAN_NAME = input("Nome da VLAN: ")
    INTERFACE_SWITCH = input("Porta do Switch (ex: Ethernet1/0 - 2/3): ")
    VLAN_IP = input("IP da VLAN: ")
    VLAN_MASK = input("Máscara da VLAN: ")

    print("\nAplicando configuração...\n")
    print(CONFIGURE_VLAN(HOST, VLAN, VLAN_NAME, INTERFACE_SWITCH, VLAN_IP, VLAN_MASK))


# 🔹 2
def OPCAO_MOSTRAR_VLAN():

    LIMPAR_TELA()

    print("=== MOSTRAR VLAN ===")

    HOST = OBTER_IP()

    print("\nBuscando VLANs...\n")
    print(SHOW_VLAN(HOST))


# 🔹 3
def OPCAO_INTERFACE_ESTADO():

    LIMPAR_TELA()

    print("=== ALTERAR PORTA ===")

    HOST = OBTER_IP()
    INTERFACE = input("Interface (ex: Ethernet1/0 - 2/3): ")
    STATE = input("Estado (UP/DOWN): ").upper()

    print("\nAplicando configuração...\n")
    print(SET_INTERFACE_STATE(HOST, INTERFACE, STATE))


# 🔹 4
def OPCAO_MOSTRAR_INTERFACE():

    LIMPAR_TELA()

    print("=== MOSTRAR INTERFACE ===")

    HOST = OBTER_IP()

    print("\nBuscando configuração do switch...\n")
    print(SHOW_RUNNING_CONFIG(HOST))


# 🔹 5
def OPCAO_TRUNK():

    LIMPAR_TELA()

    print("=== CONFIGURAR TRUNK ===")

    HOST = OBTER_IP()
    INTERFACE = input("Interface (ex: Ethernet1/0 - 2/3: ")
    VLANS = input("VLANs permitidas (ex: 10,20,30): ")

    print("\nAplicando configuração...\n")
    print(CONFIGURE_TRUNK(HOST, INTERFACE, VLANS))


# 🔁 LOOP PRINCIPAL
while True:
    LIMPAR_TELA()
    MENU()
    OPCAO = input("\nEscolha uma opção: ")

    if OPCAO == "1":
        OPCAO_CONFIGURAR_VLAN()

    elif OPCAO == "2":
        OPCAO_MOSTRAR_VLAN()

    elif OPCAO == "3":
        OPCAO_INTERFACE_ESTADO()

    elif OPCAO == "4":
        OPCAO_MOSTRAR_INTERFACE()

    elif OPCAO == "5":
        OPCAO_TRUNK()

    elif OPCAO == "0":
        print("Saindo...")
        break

    else:
        print("❌ Opção inválida")

    CONTINUAR = input("\nDeseja continuar? (S/N): ").upper()
    if CONTINUAR != "S":
        break

    LIMPAR_TELA()
