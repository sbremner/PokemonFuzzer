from burp import IBurpExtender
from burp import IIntruderPayloadGeneratorFactory
from burp import IIntruderPayloadGenerator

from java.util import List, ArrayList

from modules.utils import weighted_random, weighted_pairs

from modules.PokemonFuzzer.mutations import (
    sql_injection,
    xss_attempt,
    chunk_repeater,
    basic_replace,
    double_or_nothing
)

import re
import sys
import random
import inspect


# BHP: Page 78-87
class BurpExtender(IBurpExtender, IIntruderPayloadGeneratorFactory):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        
        callbacks.registerIntruderPayloadGeneratorFactory(self)
        
        return
        
    def getGeneratorName(self):
        return "Pokemon Fuzzer"
        
    def createNewInstance(self, attack):
        return PokemonFuzzer(self, attack)
        
        
class PokemonFuzzer(IIntruderPayloadGenerator):
    # A list of the mutators that the fuzzer will utilize
    # Note: A weight can be supplied to the mutators to 
    # influence the rate at which each mutation is used
    # ----------
    # pattern :: the regex pattern used to match the payload
    #   in order to include the mutators in the available selection
    # mutators :: the mutators that will be included if the pattern
    #   matches (see format below)
    #   
    #       (<weight>, <mutator function>, [optional: kwags for mutator])
    # shortcircuit :: tells the matcher to short-circuit after matching
    #   this mutant group (no other patterns will be tested/included
    mutants = [
        {
            # Numeric input
            'pattern': re.compile(r'^([\d]+?)$'),
            'mutators': weighted_pairs([
                (1, sql_injection),
                (2, double_or_nothing, {'negative_chance': 25}),
            ]),
            'shortcircuit': False
        },
        {
            # Catch all pattern to be used with all payloads
            'pattern': re.compile(r'(.*?)'),
            'mutators': weighted_pairs([
                (1, xss_attempt),
                (1, chunk_repeater),
                basic_replace,
            ]),
            'shortcircuit': False
        }
    ]
    
    # Default mutant if none of our mutants above match
    # Note: override this to impact the default mutant when
    # no patterns above match
    default_mutant = lambda x : x
    
    def __init__(self, extender, attack):
        self._extender = extender
        self._helpers = extender._helpers
        self._attack = attack
        self.max_payloads = 10
        self.num_iterations = 0
        
        self.payload_history = []
        
        return
        
    def preprocessor(self, payload):
        return payload
        
    def postprocessor(self, payload):
        return payload
        
    # This function let's burp know when the extension has completed
    # Since we are controlling it with max_payloads/num_iterations,
    # we would have to adjust these numbers to increase the run duration
    def hasMorePayloads(self):
        if self.num_iterations == self.max_payloads:
            return False
        else:
            return True
            
    def getNextPayload(self, current_payload):
        # convert into a string
        original_payload = "".join(chr(x) for x in current_payload)
        
        # call our simple mutator to fuzz the POST
        payload = self.mutate_payload(original_payload)
        
        # increase the number of fuzzing attempts
        self.num_iterations += 1
        
        return payload
        
    def reset(self):
        self.num_iterations = 0
        self.payload_history = []
        return
        
    def available_mutants(self, original_payload):
        available = []
        
        for m in self.mutants:
            if m.get('pattern', None) and m['pattern'].search(original_payload):
                # Add to our available mutants since our pattern matched
                available += m['mutators']
                
                # Check if we need to short-circuit here and return the mutants
                if m.get('shortcircuit', False) == True:
                    break
                    
        return available
        
    def select_mutator(self, original_payload):
        available = self.available_mutants(original_payload)

        # Return a default mutant if we have no other options
        if len(available) == 0:
            return self.default_mutant
                    
        # Select a weighted random mutant from our available mutants
        return weighted_random(available)
        
    def mutate_payload(self, original_payload):
        # Select a random mutator to use on our payload
        mutant = self.select_mutator(original_payload)

        # Optional: Could add any pre-payload processing here
        if getattr(self, 'preprocessor', None) is not None:
            original_payload = self.preprocessor(original_payload)
        
        # Invoke the selected mutant
        payload = self.invoke_mutant(original_payload, mutant)
        
        # Optional: Could add any post-payload processing here
        if getattr(self, 'postprocessor', None) is not None:
            payload = self.postprocessor(payload)
        
        return payload

    def invoke_mutant(self, original_payload, mutant):        
        # Check if our mutant has kwargs
        if inspect.isfunction(mutant):
            # Mutator does not include kwargs, just call directly
            payload = mutant(original_payload)
        else:
            try:
                # Unpack the kwargs for our function call
                mutant, kwargs = mutant
                
                # Call our mutator with the desired kwargs
                payload = mutant(original_payload, **kwargs)
            except ValueError:
                # Error unpacking mutator - probably too many values to unpack
                # print error and return default mutation
                sys.stderr.write('Mutant arguments raised ValueError: {0}'.format(mutant))
                return self.default_mutator(original_payload)
            
        return payload