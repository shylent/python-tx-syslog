# encoding: utf-8
'''
@author: shylent
'''
from pymeta import grammar
from twisted.python.util import OrderedDict
import datetime


rfc_5424_to_python = ur"""
SYSLOG_MSG      ::= <HEADER>:h <SP> <STRUCTURED_DATA>:sd (<SP> <MSG>)?:msg
    => (h, sd, (msg or None))

HEADER          ::= <PRI>:pri <VERSION>:ver <SP> <TIMESTAMP>:t <SP>
                   <HOSTNAME>:hn <SP> <APP_NAME>:an  <SP> <PROCID>:pid <SP> <MSGID>:mid
    => OD((('pri', pri), ('version', ver), ('timestamp', t), ('hostname', hn), ('app_name', an), ('procid', pid), ('msgid', mid)))

PRI             ::= '<' <PRIVAL>:pri '>' => int(pri)
PRIVAL          ::= <sequence 'digit' 0 191>:ds => ''.join(ds)
VERSION         ::= <NONZERO_DIGIT>:nzd <digit>*:ds !(ds.insert(0, nzd)) ?(int(''.join(ds)) <= 999) => ''.join(ds)  
HOSTNAME        ::= <NILVALUE> | <sequence 'PRINTUSASCII' 1 255>:cs => ''.join(cs)
APP_NAME        ::= <NILVALUE> | <sequence 'PRINTUSASCII' 1 48>:cs => ''.join(cs)
PROCID          ::= <NILVALUE> | <sequence 'PRINTUSASCII' 1 128>:cs => ''.join(cs)
MSGID           ::= <NILVALUE> | <sequence 'PRINTUSASCII' 1 32>:cs => ''.join(cs)

TIMESTAMP       ::= (<NILVALUE> | <FULL_DATE>:d "T" <FULL_TIME>:t
                    !(datetime.datetime(d.year, d.month, d.day,t[0].hour, t[0].minute, t[0].second, t[0].microsecond), t[1]))

FULL_DATE       ::= <DATE_FULLYEAR>:y '-' <DATE_MONTH>:m '-' <DATE_MDAY>:d
                     => datetime.date(int(y), int(m), int(d)) 
DATE_FULLYEAR   ::= <digit>+:ds => ''.join(ds)
DATE_MONTH      ::= <digit>:d1 <digit>:d2 => d1+d2
DATE_MDAY       ::= <digit>:d1 <digit>:d2 => d1+d2

FULL_TIME       ::= <PARTIAL_TIME>:t <TIME_OFFSET>:o => (t, o)
PARTIAL_TIME    ::= <TIME_HOUR>:h ":" <TIME_MINUTE>:m ":" <TIME_SECOND>:s (<TIME_SECFRAC>?:psf !(psf or 0)):sf
    => datetime.time(h, m, s, sf)

TIME_HOUR       ::= <digit>+:ds !(int(''.join(ds))):h ?(0 <= h <= 23)  => h  
TIME_MINUTE     ::= <digit>+:ds !(int(''.join(ds))):m ?(0 <= m <= 59)  => m
TIME_SECOND     ::= <digit>+:ds !(int(''.join(ds))):s ?(0 <= s <= 59)  => s
TIME_SECFRAC    ::= "." <sequence 'digit' 0 6>:ds => int(''.join(ds).ljust(6, '0'))
TIME_OFFSET     ::= ("Z" !(datetime.timedelta()) | <TIME_NUMOFFSET>)
TIME_NUMOFFSET  ::= (("+" | "-"):s !((s == '+')*2 - 1)):sign <TIME_HOUR>:h ":" <TIME_MINUTE>:m
    => sign*datetime.timedelta(hours=h, minutes=m)

STRUCTURED_DATA ::= <NILVALUE> | <SD_ELEMENT>+:els => OD(els)
SD_ELEMENT      ::= "[" <SD_ID>:id (<SP> <SD_PARAM>)*:params "]" => (id, tuple(params)) 
SD_PARAM        ::= <PARAM_NAME>:n '=' '"' <PARAM_VALUE>:v '"' => (n, v)
SD_ID           ::= <SD_NAME>
PARAM_NAME      ::= <SD_NAME>
PARAM_VALUE     ::= (<escaped> | ~('"' | ']' | '\\') <OCTET>)+:s => ''.join(s).decode('utf-8')

SD_NAME         ::= (~('=' | ']' | '"' | ' ') <PRINTUSASCII>)+:s ?(len(s) <= 32) => ''.join(s)

MSG             ::= <MSG_UTF_8> | <MSG_ANY>
MSG_ANY         ::= <OCTET>*:c => ''.join(c)
MSG_UTF_8       ::= <BOM> <UTF_8_STRING>:u8s => u8s
BOM             ::= <char '\xef'> <char '\xbb'> <char '\xbf'>

escaped ::= '\\' (
      '"' => '"'
    | '\\'=> '\\'
    | ']' => ']'
    | <OCTET>:s => '\\'+s 
)

UTF_8_STRING ::= <OCTET>*:s => ''.join(s).decode('utf-8')
OCTET ::= <charRange '\x00' '\xff'>
PRINTUSASCII ::= <charRange '!' '~'>
NONZERO_DIGIT ::= <charRange '1' '9'>
SP ::= ' '
NILVALUE ::= '-' => None


charRange :c1 :c2 ::=  <anything>:c ?(c1 <= c <= c2) => c
sequence :r :l :h ::= <apply r>*:ss ?(l <= len(ss) <= h) => [s[0] for s in ss]
char :c ::=  <anything>:ic ?(ic == c) => ic
apply :rule ::= => self.apply(rule)

"""


RFC5424ToPythonGrammar = grammar.OMeta.makeGrammar(rfc_5424_to_python,
                                                   {'datetime':datetime, 'OD':OrderedDict},
                                                   'RFC5424ToPythonGrammar')
