"""
Callback utilities for 9ID
==========================

If the (un)subscribe functions aren't working, it may be because
apsbits.core has been updated/reverted to main branch. 9ID's installation
of apsbits (in BITS_env) has changes in apsbits.core.run_engine_init
so that a re_subscriptions dictionary is created/returned

.. autosummary::
    ~unsubscribe_bec
    ~subscribe_bec
""" 

def unsubscribe_bec(RE, subscriptions):
    """
    Unsubscribing BEC and updating subscriptions dictionary

    Parameters:

    RE: run engine instance in use
    re_subscriptions: dictionary of RE subscriptions


    Returns: 
    updated subscription dictionary

    Usage:      
    re_subscriptions = unsubscribe_bec(RE, re_subscriptions)        
    """

    if 'bec' in subscriptions:
        RE.unsubscribe(subscriptions['bec'])
        del subscriptions['bec']
    else: 
        print('bec not in re_subscriptions')
    return subscriptions

    


def subscribe_bec(RE, subscriptions):
    """
    (Re)subscribing BEC and updating subscriptions dictionary

    Parameters:

    RE: run engine instance in use
    re_subscriptions: dictionary of RE subscriptions


    Returns: 
    updated subscription dictionary

    Usage:
    re_subscriptions = subscribe_bec(RE, re_subscriptions)      
    """
    if 'bec' not in subscriptions:
        subscriptions['bec'] = RE.subscribe(bec)
    else:
        print(f'Error: bec already in re_subscriptions as token {subscriptions["bec"]}')
    return subscriptions
    
