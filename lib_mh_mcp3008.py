"""
MicroPython Library for MCP3008 8-channel ADC with SPI

Datasheet for the MCP3008: https://www.microchip.com/datasheet/MCP3008

This code makes much use of Adafruit's CircuitPython code at
https://github.com/adafruit/Adafruit_CircuitPython_MCP3xxx
adapted for MicroPython.

Tested on the Raspberry Pi Pico.

Thanks, @Raspberry_Pi and @Adafruit, for all you've given us!
"""

import machine


class MCP3008:

    def __init__(self, spi, cs, ref_voltage=3.3):
        """
        Initialise une instance pour dialoguer avec un ADC MCP3008.

        Args:
            spi: instance SPI déjà configurée
            cs:  pin utilisée pour le Chip Select (active en niveau bas)
            ref_voltage: tension de référence utilisée par l'ADC (souvent 3.3 V)
        """
        self.cs = cs
        self.cs.value(1)  # Désactive le MCP3008 (CS = 1) avant toute communication        
        self._spi = spi
        
        # Buffer contenant les 3 octets envoyés au MCP3008 :
        # octet 0 = bit "start" (valeur fixe 0x01)
        # octet 1 = configuration (mode + canal)
        # octet 2 = "dummy byte" (sert à recevoir les bits faibles)
        self._out_buf = bytearray(3)
        self._out_buf[0] = 0x01 # bit de start obligatoire pour MCP3008
        
        self._in_buf = bytearray(3)
        self._ref_voltage = ref_voltage

    def reference_voltage(self) -> float:
        """Renvoie la tension de référence (VREF) utilisée par le MCP3008."""
        return self._ref_voltage

    def read(self, channel, is_differential=False):
        """
        Lit une tension sur un canal du MCP3008.

        Args:
            channel: numéro du canal (0 à 7)
            is_differential: si True, lit la différence de potentiel entre deux canaux 
                             pair/impair (CH0-CH1, CH2-CH3, etc.). 

        Returns:
            Une valeur brute entre 0 et 1023 correspondant à la tension mesurée
            (10 bits). 1023 correspond à VREF.
        """
        # Vérifie que le canal demandé existe
        if not 0 <= channel <= 7:
            raise ValueError("Canal invalide")
        
        # Active la broche CS (chip select) pour commencer la communication SPI
        self.cs.value(0)
        
        # Préparation du second octet à envoyer :
        # - bit 7 : mode single-ended (1) ou différentiel (0)
        # - bits 6-4 : numéro du canal
        self._out_buf[1] = ((not is_differential) << 7) | (channel << 4)
        
        # Envoie les 3 octets (start + config) et récupère la réponse (3 octets aussi)       
        self._spi.write_readinto(self._out_buf, self._in_buf)
        
        # Désactive CS : fin de transaction
        self.cs.value(1)
        
        # Reconstruction des 10 bits utiles :
        # - les 2 bits de poids fort sont dans in_buf[1] & 0x03
        # - les 8 bits de poids faible sont dans in_buf[2]        
        return ((self._in_buf[1] & 0x03) << 8) | self._in_buf[2]

    def read_all(self):
        """
        Lit successivement les 8 canaux du MCP3008.

        Returns:
            Une liste contenant les 8 valeurs lues (0–1023), dans l'ordre CH0 → CH7.

        Notes:
            - Chaque appel déclenche une lecture SPI complète.
            - Pratique si l’on veut lire tous les capteurs rapidement.
        """
        # On appelle read() pour chaque canal de 0 à 7 et 
        # on renvoie la liste des valeurs
        return [self.read(ch) for ch in range(8)]

    def read_voltage(self, channel):
        """
        Renvoie la tension en volts du canal.
        """
        raw = self.read(channel)
        return raw * (self._ref_voltage / 1023.0)

    def read_all_voltage(self):
        """
        Lit les 8 canaux du MCP3008 et renvoie leurs tensions en volts.

        Returns:
            Une liste de 8 valeurs en volts, correspondant aux canaux CH0 à CH7.
        """
        return [(self.read(ch) * self._ref_voltage / 1023.0) for ch in range(8)]

if __name__ == "__main__":
    
    import time
    from machine import Pin, SPI
    
    # ----------------------------------------------------
    #  Configuration du bus SPI du Raspberry Pi Pico
    # ----------------------------------------------------
    spi = machine.SPI(0, sck=Pin(6),mosi=Pin(3),miso=Pin(0), baudrate=100000)

    # ----------------------------------------------------
    #  Pin Chip Select du MCP3008 (active en niveau bas)
    # ----------------------------------------------------
    cs = machine.Pin(1, machine.Pin.OUT)

    # ----------------------------------------------------
    #  Création de l'instance MCP3008 pour effectuer les tests
    # ----------------------------------------------------
    adc = MCP3008(spi, cs)

    # ----------------------------------------------------
    #  Boucle de test : lecture des 8 canaux toutes les secondes
    # ----------------------------------------------------
    while True:
        print(adc.read_all())
        print(adc.read_all_voltage())
        time.sleep(1)
