#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from builtins import zip
from builtins import str
import os
import string
import re
try :
    from collections import OrderedDict
except ImportError :
    from ordereddict import OrderedDict
import warnings

import pycrfsuite
import probableparsing

# The address components are based upon the `United States Thoroughfare, Landmark, and Postal Address Data Standard
# http://www.urisa.org/advocacy/united-states-thoroughfare-landmark-and-postal-address-data-standard


LABELS = [
'number_first',
'number_last',
'street_name',
'locality_name',
'state',
'postcode',
'sub_unit_type',
'sub_unit_number',
'sub_unit_seperator',
'level_type',
'level_number',
'subdivision_type',
'subdivision_number',
'institution_type',
'institution_number',
# 'address_number_prefix',
# 'address_number_suffix',
# 'street_name_direction_pre',
'street_suffix',
# 'street_name_modifier_pre',
'street_type'
# 'street_type_pre',
'po_box_type',
'po_box_number'
# 'USPSBoxType',
# 'USPSBoxID',
# 'USPSBoxGroupType',
# 'USPSBoxGroupID',
# 'LandmarkName',
# 'CornerOf',
# 'IntersectionSeparator',
# 'OccupancyType',
# 'OccupancyIdentifier',
# 'Recipient',
# 'BuildingName',
# 'NotAddress'
]

PARENT_LABEL = 'AddressString'
GROUP_LABEL = 'AddressCollection'

MODEL_FILE = 'au_addr.crfsuite'
MODEL_PATH = os.path.split(os.path.abspath(__file__))[0] + '/' + MODEL_FILE

DIRECTIONS = set(['n', 's', 'e', 'w',
                  'ne', 'nw', 'se', 'sw',
                  'north', 'south', 'east', 'west',
                  'northeast', 'northwest', 'southeast', 'southwest'])

SUBDIVISIONS = ('lot', 'block')

STREET_TYPES = {'bluf', 'paths', 'tunnl', 'valley', 'harbr', 'lodge',
                'plz', 'bch', 'msn', 'squ', 'frgs', 'haven', 'drs',
                'islands', 'frk', 'extensions', 'annx', 'bayoo',
                'knol', 'hollow', 'cpe', 'psge', 'dvd', 'loops',
                'lock', 'crossroad', 'aly', 'fld', 'gdn', 'estates',
                'grns', 'alley', 'gatway', 'mtn', 'trail', 'shrs',
                'cape', 'pkwys', 'plns', 'ht', 'arcade', 'fls',
                'knls', 'streets', 'crse', 'frg', 'boul', 'brg',
                'vis', 'wall', 'boulv', 'center', 'lake', 'extnsn',
                'hbr', 'hvn', 'centers', 'mntain', 'shores',
                'mission', 'fry', 'un', 'hllw', 'via', 'forks',
                'anex', 'gatewy', 'bridge', 'pr', 'creek', 'mdw',
                'cliffs', 'grov', 'flt', 'manor', 'trace', 'crossing',
                'grn', 'trks', 'fall', 'mountin', 'valleys', 'avenu',
                'route', 'trak', 'parkway', 'crsnt', 'spg', 'locks',
                'spurs', 'tunnel', 'loop', 'vlys', 'orchard',
                'gardens', 'byp', 'greens', 'turnpike', 'curve',
                'vist', 'avnue', 'clfs', 'fwy', 'strvn', 'rdge',
                'walk', 'trafficway', 'walks', 'circl', 'ctrs',
                'ports', 'station', 'ml', 'pnes', 'row', 'island',
                'cen', 'ridge', 'garden', 'frway', 'junctn', 'drive',
                'street', 'crcle', 'crest', 'mountains', 'beach',
                'bluff', 'juncton', 'viadct', 'rvr', 'smt', 'knolls',
                'plza', 'blf', 'traces', 'trails', 'pl', 'square',
                'villag', 'commons', 'mtwy', 'ter', 'cp', 'cliff',
                'xrd', 'exp', 'ville', 'path', 'track', 'est',
                'glens', 'spng', 'branch', 'br', 'frd', 'tunl', 'mnt',
                'bgs', 'forests', 'opas', 'point', 'skwy', 'rad',
                'manors', 'plaza', 'gdns', 'port', 'trlr', 'bnd',
                'frwy', 'knoll', 'place', 'throughway', 'avenue',
                'crsent', 'rnch', 'trnpk', 'mt', 'lndg', 'freewy',
                'trl', 'road', 'stravenue', 'ferry', 'hls', 'ave',
                'prts', 'gtwy', 'cv', 'strvnue', 'forges', 'hill',
                'mountain', 'allee', 'cyn', 'pln', 'hiwy', 'overpass',
                'spngs', 'vly', 'shoals', 'shl', 'isle', 'ests',
                'rdg', 'vlg', 'clb', 'club', 'well', 'lodg', 'expy',
                'vill', 'crcl', 'iss', 'mtns', 'bend', 'expw',
                'bluffs', 'prk', 'ft', 'brnch', 'bypas', 'bot',
                'fields', 'hbrs', 'cent', 'lks', 'prt', 'key', 'cor',
                'motorway', 'radial', 'jct', 'courts', 'hwy', 'hgwy', 'ally',
                'highwy', 'rapid', 'riv', 'pines', 'rdgs', 'cmp',
                'is', 'xrds', 'brk', 'mills', 'circle', 'strt',
                'shls', 'ramp', 'viaduct', 'aven', 'harb', 'sq',
                'sta', 'streme', 'hway', 'rte', 'dl', 'dm', 'ext',
                'rnchs', 'glns', 'roads', 'flds', 'frds', 'holws',
                'vista', 'uns', 'statn', 'straven', 'villages', 'mnr',
                'sumit', 'burg', 'flts', 'wls', 'crossroads', 'view',
                'trwy', 'cmn', 'str', 'pts', 'hl', 'cntr', 'prairie',
                'upas', 'shoal', 'mall', 'pne', 'vsta', 'sumitt',
                'heights', 'express', 'pikes', 'blvd', 'hts', 'pkwy',
                'trlrs', 'shore', 'brooks', 'trailer', 'ln', 'jctn',
                'mount', 'pkway', 'trfy', 'squares', 'green', 'mtin',
                'driv', 'lcks', 'brdge', 'neck', 'pine', 'islnd',
                'common', 'mnrs', 'cnter', 'junction', 'frst', 'vlly',
                'spring', 'xing', 'rds', 'lgts', 'tunnels', 'lk',
                'cove', 'loaf', 'burgs', 'groves', 'court', 'vally',
                'ct', 'terrace', 'centr', 'vst', 'shr', 'prr', 'oval',
                'stra', 'lck', 'nck', 'rapids', 'cnyn', 'village',
                'drv', 'sts', 'tunel', 'meadows', 'grv', 'gateway',
                'falls', 'passage', 'inlt', 'pass', 'vw', 'harbor',
                'bypass', 'lgt', 'extension', 'canyon', 'mews',
                'causwa', 'river', 'knl', 'trls', 'crescent', 'anx',
                'strm', 'tpke', 'jction', 'annex', 'crst', 'curv',
                'jctns', 'bottom', 'corner', 'lights', 'inlet', 'lf',
                'shoars', 'avn', 'boulevard', 'cors', 'brks', 'av',
                'mill', 'glen', 'lndng', 'bg', 'grove', 'keys',
                'rivr', 'dv', 'orch', 'springs', 'ranch', 'light',
                'shoar', 'landing', 'freeway', 'mssn', 'way', 'arc',
                'byu', 'cmns', 'forg', 'coves', 'parkwy', 'vws',
                'parkways', 'vlgs', 'sqre', 'cir', 'wy', 'fords',
                'sqrs', 'radiel', 'spur', 'lane', 'flat', 'trce',
                'skyway', 'bypa', 'park', 'hills', 'mls', 'plain',
                'unions', 'frry', 'islnds', 'causeway', 'orchrd',
                'radl', 'mntn', 'mdws', 'medows', 'wells', 'grvs',
                'expressway', 'vl', 'sqs', 'sprngs', 'field',
                'tracks', 'grdns', 'rst', 'missn', 'underpass', 'ldg',
                'circ', 'pky', 'stravn', 'clf', 'ranches', 'crssng',
                'kys', 'rpds', 'cswy', 'rest', 'camp', 'hollows',
                'mntns', 'stn', 'drives', 'points', 'estate', 'strav',
                'st', 'frks', 'forest', 'div', 'centre', 'hrbor',
                'union', 'canyn', 'cres', 'corners', 'cirs', 'spgs',
                'views', 'meadow', 'turnpk', 'summit', 'ford',
                'divide', 'pt', 'trk', 'ways', 'lakes', 'jcts', 'cts',
                'dale', 'villiage', 'gardn', 'dr', 'fork', 'wl',
                'rue', 'ovl', 'sprng', 'rd', 'sqr', 'stream',
                'plains', 'highway', 'ldge', 'gtway', 'extn', 'frt',
                'pike', 'expr', 'tunls', 'hiway', 'holw', 'dam',
                'rpd', 'bayou', 'circles', 'isles', 'ctr', 'grdn',
                'terr', 'blfs', 'btm', 'gln', 'flats', 'crk', 'forge',
                'ridges', 'parks', 'bottm', 'land', 'grden',
                'junctions', 'fort', 'byps', 'harbors', 'villg',
                'brook', 'ky', 'course', 'cvs', 'run', 'vdct', 'exts'}


try :
    TAGGER = pycrfsuite.Tagger()
    TAGGER.open(MODEL_PATH)
except IOError :
    warnings.warn('You must train the model (parserator train --trainfile FILES) to create the %s file before you can use the parse and tag methods' %MODEL_FILE)

def parse(address_string) :
    print("Calling Tokenize")
    tokens = tokenize(address_string)
    print("DEBUG: Tokens: {}".format(tokens))

    if not tokens :
        return []

    features = tokens2features(tokens)

    tags = TAGGER.tag(features)
    return list(zip(tokens, tags))

def tag(address_string) :
    tagged_address = OrderedDict()

    last_label = None
    intersection = False

    for token, label in parse(address_string) :
        if label == 'IntersectionSeparator' :
            intersection = True
        if 'street_name' in label and intersection :
            label = 'Second' + label
        if label == last_label :
            tagged_address[label].append(token)
        elif label not in tagged_address :
            tagged_address[label] = [token]
        else :
            raise Error("TOKEN: {}".format(token))
            # raise RepeatedLabelError(address_string, parse(address_string), label, token)

        last_label = label

    for token in tagged_address :
        component = ' '.join(tagged_address[token])
        component = component.strip(" ,;")
        tagged_address[token] = component


    if 'number_first' in tagged_address and not intersection :
        address_type = 'Street Address'
    elif intersection and 'number_first' not in tagged_address :
        address_type = 'Intersection'
    elif 'po_box_number' in tagged_address :
        address_type = 'PO Box'
    else :
        address_type = 'Ambiguous'

    return (tagged_address, address_type)

def tokenize(address_string) :
    if isinstance(address_string, bytes):
        address_string = str(address_string, encoding='utf-8')
    address_string = re.sub('(&#38;)|(&amp;)', '&', address_string)
    re_tokens = re.compile(r"""
    \(*\b[^\s\\,;#&()]+[.,;)\\\n]*   # ['ab. cd,ef '] -> ['ab.', 'cd,', 'ef']
    |
    [#&]                       # [^'#abc'] -> ['#']
    """,
                           re.VERBOSE | re.UNICODE)

    tokens = re_tokens.findall(address_string)

    if not tokens :
        return []

    return tokens

def tokenFeatures(token) :

    if token in (u'&', u'#', u'½', '/', '\\') :
        token_clean = token
    else :
        token_clean = re.sub(r'(^[\W]*)|([^.\w]*$)', u'', token, flags=re.UNICODE)

    print("token: {} token_clean: {}".format(token, token_clean))

    token_abbrev = re.sub(r'[.]', u'', token_clean.lower())
    features = {'abbrev' : token_clean[-1] == u'.',
                'digits' : digits(token_clean),
                'word' : (token_abbrev
                          if not token_abbrev.isdigit()
                          else False),
                'trailing.zeros' : (trailingZeros(token_abbrev)
                                    if token_abbrev.isdigit()
                                    else False),
                'length' : (u'd:' + str(len(token_abbrev))
                            if token_abbrev.isdigit()
                            else u'w:' + str(len(token_abbrev))),
                'endsinpunc' : (token[-1]
                                if bool(re.match('.+[^.\w]', token, flags=re.UNICODE))
                                else False),
                'directional' : token_abbrev in DIRECTIONS,
                'street_type' : token_abbrev in STREET_TYPES,
                'has.vowels'  : bool(set(token_abbrev[1:]) & set('aeiou')),
                'subdivision' : token_abbrev in SUBDIVISIONS
                }


    return features

def tokens2features(address):

    feature_sequence = [tokenFeatures(address[0])]
    previous_features = feature_sequence[-1].copy()

    for token in address[1:] :
        token_features = tokenFeatures(token)
        current_features = token_features.copy()

        feature_sequence[-1]['next'] = current_features
        token_features['previous'] = previous_features

        feature_sequence.append(token_features)

        previous_features = current_features

    feature_sequence[0]['address.start'] = True
    feature_sequence[-1]['address.end'] = True

    if len(feature_sequence) > 1 :
        feature_sequence[1]['previous']['address.start'] = True
        feature_sequence[-2]['next']['address.end'] = True

    return feature_sequence

def digits(token) :
    if token.isdigit() :
        return 'all_digits'
    elif set(token) & set(string.digits) :
        return 'some_digits'
    else :
        return 'no_digits'

def trailingZeros(token) :
    results = re.findall(r'(0+)$', token)
    if results :
        return results[0]
    else :
        return ''



class RepeatedLabelError(probableparsing.RepeatedLabelError) :
    REPO_URL = 'https://github.com/datamade/usaddress/issues/new'
    DOCS_URL = 'http://usaddress.readthedocs.org/'
