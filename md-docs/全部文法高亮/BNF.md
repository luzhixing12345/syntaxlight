
# bnf
## [1.bnf](https://github.com/luzhixing12345/syntaxlight/tree/main/test/bnf/1.bnf)

```bnf
<syntax>     ::= <rule>+
<rule>       ::= <rule-name> "::="  <expression>

# ID 可以带 -

<rule-name> ::= "<" <ID> ">" <punctuator>?
<expression> ::= <term> ("|" <term>)*

<term>  ::= (<item> | <rule-name> | <group-term>)* <CRLF>?
<item> ::= (<STR> | <ID>) <punctuator>?

<group-term> ::= "(" <expression> ")" <punctuator>?
               | "{" <expression> "}" <punctuator>?

<punctuator> ::= '+' | '*' | '?'


```
## [2.bnf](https://github.com/luzhixing12345/syntaxlight/tree/main/test/bnf/2.bnf)

```bnf
<syntax>         ::= <rule> | <rule> <syntax>
<rule>           ::= <opt-whitespace> "<" <rule-name> ">" <opt-whitespace> "::=" <opt-whitespace> <expression> <line-end>
<opt-whitespace> ::= " " <opt-whitespace> | ""
<expression>     ::= <list> | <list> <opt-whitespace> "|" <opt-whitespace> <expression>
<line-end>       ::= <opt-whitespace> <EOL> | <line-end> <line-end>
<list>           ::= <term> | <term> <opt-whitespace> <list>
<term>           ::= <literal> | "<" <rule-name> ">"
<literal>        ::= '"' <text1> '"' | "'" <text2> "'"
<text1>          ::= "" | <character1> <text1>
<text2>          ::= "" | <character2> <text2>
<character>      ::= <letter> | <digit> | <symbol>
<letter>         ::= "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J" | "K" | "L" | "M" | "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X" | "Y" | "Z" | "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z"
<digit>          ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
<symbol>         ::= "|" | " " | "!" | "#" | "$" | "%" | "&" | "(" | ")" | "*" | "+" | "," | "-" | "." | "/" | ":" | ";" | ">" | "=" | "<" | "?" | "@" | "[" | "\\" | "]" | "^" | "_" | "`" | "{" | "}" | "~"
<character1>     ::= <character> | "'"
<character2>     ::= <character> | '"'
<rule-name>      ::= <letter> | <rule-name> <rule-char>
<rule-char>      ::= <letter> | <digit> | "-"
```
## [3.bnf](https://github.com/luzhixing12345/syntaxlight/tree/main/test/bnf/3.bnf)

```bnf
# C BNF for ISO/IEC C17
<translation-unit> ::= {<external-declaration>}*

<external-declaration> ::= <function-definition>
                         | <declaration>

<function-definition> ::= {<declaration-specifier>}* <declarator> {<declaration>}* <compound-statement>


<declaration-specifier> ::= <storage-class-specifier>
                          | <type-specifier>
                          | <type-qualifier>
                          | <function-specifier>
                          | <alignment-specifier>

<storage-class-specifier> ::= auto
                            | register
                            | static
                            | extern
                            | typedef
                            | _Thread_local

<type-specifier> ::= void
                   | char
                   | short
                   | int
                   | long
                   | float
                   | double
                   | signed
                   | unsigned
                   | _Bool
                   | _Complex
                   | <atomic-type-specifier>
                   | <struct-or-union-specifier>
                   | <enum-specifier>
                   | <typedef-name>

<function-specifier> ::= inline
                       | _Noreturn

<alignment-specifier> ::= _Alignas "(" <type-name> ")"
                        | _Alignas "(" <constant-expression> ")"

<atomic-type-specifier> ::= _Atomic "(" <type-name> ")"

<struct-or-union-specifier> ::= <struct-or-union> <identifier> ("{" {<struct-declaration>}* "}")?
                              | <struct-or-union> "{" {<struct-declaration>}* "}"

<struct-or-union> ::= struct
                    | union

<struct-declaration> ::= <specifier-qualifier-list>* <struct-declarator-list>? ";"
                       | <static_assert-declaration>

<specifier-qualifier> ::= <type-specifier> <specifier-qualifier>?
                        | <type-qualifier> <specifier-qualifier>?

<struct-declarator-list> ::= <struct-declarator> ("," <struct-declarator>)*

<struct-declarator> ::= <declarator> (":" <constant-expression>)?
                      | ":" <constant-expression>

<declarator> ::= {<pointer>}? <direct-declarator>

<pointer> ::= ("*" <type-qualifier>*)*

<type-qualifier> ::= const
                   | volatile
                   | restrict
                   | _Atomic

<direct-declarator> ::= <identifier>
                      | "(" <declarator> ")"
                      | <direct-declarator> "[" <type-qualifier-list>? <assignment-expression>? "]"
                      | <direct-declarator> "[" static <type-qualifier-list>? <assignment-expression> "]"
                      | <direct-declarator> "[" <type-qualifier-list> static <assignment-expression> "]"
                      | <direct-declarator> "[" <type-qualifier-list>? "*" "]"
                      | <direct-declarator> "(" <parameter-list> ")"
                      | <direct-declarator> "(" (<identifier-list>)? ")"

<type-qualifier-list> ::= <type-qualifier>+

<parameter-list> ::= <parameter-declaration> ("," <parameter-declaration>)* ("," "...")?

<identifier-list> ::= <identifier> ("," <identifier>)*

<constant-expression> ::= <conditional-expression>

<conditional-expression> ::= <logical-or-expression> ("?" <expression> ":" <conditional-expression>)?

<logical-or-expression> ::= <logical-and-expression> ("||" <logical-and-expression>)*

<logical-and-expression> ::= <inclusive-or-expression> ("&&" <inclusive-or-expression>)*

<inclusive-or-expression> ::= <exclusive-or-expression> ("|" <exclusive-or-expression>)*

<exclusive-or-expression> ::= <and-expression> ("^" <and-expression>)*

<and-expression> ::= <equality-expression> ("&" <equality-expression>)*

<equality-expression> ::= <relational-expression> (("=="|"!=") <relational-expression>)*

<relational-expression> ::= <shift-expression> (("<"|">"|"<="|">=") <shift-expression>)*

<shift-expression> ::= <additive-expression> (("<<" | ">>") <additive-expression>)*

<additive-expression> ::= <multiplicative-expression> (("+"|"-") <multiplicative-expression>)*

<multiplicative-expression> ::= <cast-expression> (("*"|"/"|"%") <cast-expression>)*

<cast-expression> ::= <unary-expression>
                    | "(" <type-name> ")" <cast-expression>


<unary-expression> ::= <postfix-expression>
                     | "++" <unary-expression>
                     | "--" <unary-expression>
                     | <unary-operator> <cast-expression>
                     | sizeof <unary-expression>
                     | sizeof   "(" <type-name> ")"
                     | _Alignof "(" <type-name> ")"

<postfix-expression> ::= <primary-expression>
                       | <postfix-expression> "[" <expression> "]"
                       | <postfix-expression> "(" <argument-expression-list>? ")"
                       | <postfix-expression> "." <identifier>
                       | <postfix-expression> "->" <identifier>
                       | <postfix-expression> "++"
                       | <postfix-expression> "--"
                       | "(" <type-name> ")" "{" <initializer-list> (",")? "}"

<static_assert-declaration> ::= _Static_assert "(" <constant-expression> "," <string> ")"

<primary-expression> ::= <identifier>
                       | <constant>
                       | <string>
                       | "(" <expression> ")"
                       | <generic-selection>

<generic-selection> ::= _Generic "(" <assignment-expression> "," <generic-assoc-list> ")"

<generic-assoc-list> ::= <generic-association> ("," <generic-association>)*

<generic-association> ::= <type-name> ":" <assignment-expression>
                        | default ":" <assignment-expression>

<constant> ::= <integer-constant>
             | <character-constant>
             | <floating-constant>
             | <enumeration-constant>
             | <predefined-constant>

<expression> ::= <assignment-expression> ("," <assignment-expression>)*

<argument-expression-list> ::= <assignment-expression> ("," <assignment-expression>)*

<assignment-expression> ::= <conditional-expression>
                          | <unary-expression> <assignment-operator> <assignment-expression>

<assignment-operator> ::= "="
                        | "*="
                        | "/="
                        | "%="
                        | "+="
                        | "-="
                        | "<<="
                        | ">>="
                        | "&="
                        | "^="
                        | "|="

<unary-operator> ::= "&"
                   | "*"
                   | "+"
                   | "-"
                   | "~"
                   | "!"

<type-name> ::= {<specifier-qualifier>}+ {<abstract-declarator>}?

<parameter-declaration> ::= {<declaration-specifier>}+ <declarator>
                          | {<declaration-specifier>}+ (<abstract-declarator>)?

<abstract-declarator> ::= <pointer>
                        | <pointer> <direct-abstract-declarator>
                        | <direct-abstract-declarator>

<direct-abstract-declarator> ::=  
        | "(" <abstract-declarator> ")"
        | <direct-abstract-declarator>? "(" <parameter-type-list>? ")"
        | <direct-abstract-declarator>? "[" <type-qualifier-list>? <assignment-expression>? "]"
        | <direct-abstract-declarator>? "[" static <type-qualifier-list>? <assignment-expression> "]"
        | <direct-abstract-declarator>? "[" <type-qualifier-list> static <assignment-expression> "]"
        | <direct-abstract-declarator>? "[" "*" "]"

<enum-specifier> ::= enum (<identifier>)? "{" <enumerator> ("," <enumerator>)* ","? "}"
                   | enum <identifier>

<enumerator> ::= <enumeration-constant> ("=" <constant-expression>)?

<typedef-name> ::= <identifier>

<declaration> ::= <declaration-specifier>+ (<init-declarator-list>)? ";"
                | <static-assert-declaration>

<init-declarator-list> ::= <init-declarator> ("," <init-declarator>)*

<init-declarator> ::= <declarator> ("=" <initializer>)?

<initializer> ::= <assignment-expression>
                | "{" <initializer-list> "}"
                | "{" <initializer-list> "," "}"

<initializer-list> ::= <designation>? <initializer> ("," <designation>? <initializer>)*

<designation> ::= <designator>+ "="

<designator> ::= "[" <constant-expression> "]"
               | "." <identifier>

<compound-statement> ::= "{" (<block-item>)* "}"

<block-item> ::= <declaration>
               | <statement>

<statement> ::= <labeled-statement>
              | <expression-statement>
              | <compound-statement>
              | <selection-statement>
              | <iteration-statement>
              | <jump-statement>

<labeled-statement> ::= <identifier> ":" <statement>
                      | case <constant-expression> ":" <statement>
                      | default ":" <statement>

<expression-statement> ::= {<expression>}? ";"

<selection-statement> ::= if "(" <expression> ")" <statement>
                        | if "(" <expression> ")" <statement> else <statement>
                        | switch "(" <expression> ")" <statement>

<iteration-statement> ::= while "(" <expression> ")" <statement>
                        | do <statement> while "(" <expression> ")" ";"
                        | for "(" {<expression>}? ";" {<expression>}? ";" {<expression>}? ")" <statement>
                        | for "(" <declaration> <expression>? ";" <expression>? ")" <statement>

<jump-statement> ::= goto <identifier> ";"
                   | continue ";"
                   | break ";"
                   | return {<expression>}? ";"
```
## [4.bnf](https://github.com/luzhixing12345/syntaxlight/tree/main/test/bnf/4.bnf)

```bnf
<Json> ::= <Object>
         | <Array>

<Object> ::= '{' <Pair>? ( ',' <Pair> )* '}'

<Pair> ::= <STRING> ':' <Value>

<Array> ::= '[' <Value>? ( ',' <Value> )* ']'

<Value> ::= <STRING>
          | '-'? <NUMBER>
          | <Object>
          | <Array>
          | true
          | false
          | null
```
## [5.bnf](https://github.com/luzhixing12345/syntaxlight/tree/main/test/bnf/5.bnf)

```bnf
<toml> ::= <expression> ( <CRLF> <expression> )*

<expression> ::= (<pair> | <table>)?

<pair> ::= <path> '=' <value>

<path> ::= (<ID> | <STRING>) ( '.' (<ID> | <STRING>)) *

<table> ::= <table_header>       <CRLF> <table_entry>
          | <table_array_header> <CRLF> <table_entry>

<table_header>       ::=  '['     <path>     ']'
<table_array_header> ::=  '[' '[' <path> ']' ']'

<table_entry> ::= (<pair>)? ( <CRLF> <pair> )*

<value> ::= <STRING> | <NUMBER> | <DATE> | true | false | <array> | <inline_table> 

<array> ::= '[' ( <value> (',' <value> )* ','?)? ']'

<inline_table> ::= '{' ( <pair> (',' <pair>)* ','?)? '}'
```
## [6.bnf](https://github.com/luzhixing12345/syntaxlight/tree/main/test/bnf/6.bnf)

```bnf
<chunk> ::= <block>

<block> ::= (<stat>)* <retstat>?

<stat> ::= ';'
         | <varlist> '=' <explist> 
         | <functioncall> 
         | <label>
         | break
         | goto <Name>
         | do <block> end 
         | while <exp> do <block> end 
         | repeat <block> until <exp> 
         | if <exp> then <block> (elseif <exp> then <block>)* (else <block>)? end 
         | for <Name> '=' <exp> ',' <exp> (',' <exp>)? do <block> end 
         | for <namelist> in <explist> do <block> end 
         | function <funcname> <funcbody> 
         | local function <Name> <funcbody> 
         | local <attnamelist> ('=' <explist>)?

<attnamelist> ::= <Name> <attrib> ("," <Name> <attrib>)*

<attrib> ::= ("<" <Name> ">")?

<retstat> ::= return (<explist>)? ';'?

<label> ::= '::' <Name> "::"

<funcname> ::= <Name> ('.' <Name>)* (':' <Name>)?

<varlist> ::= <var> (',' <var>)*

<var> ::= <Name> 
        | <prefixexp> '[' <exp> ']' 
        | <prefixexp> '.' <Name> 

<namelist> ::= <Name> (',' <Name>)*

<explist> ::= <exp> (',' <exp>)*

<exp> ::= nil 
        | false 
        | true 
        | <NUMBER> 
        | <STRING>
        | '...' 
        | <functiondef>
        | <prefixexp> 
        | <tableconstructor> 
        | <exp> <binop> <exp> 
        | <unop> <exp> 

<prefixexp> ::= <var>
              | <functioncall> 
              | '(' <exp> ')'

<functioncall> ::= <prefixexp> <args> 
                 | <prefixexp> ':' <Name> <args> 

<args> ::= '(' <explist>? ')' 
         | <tableconstructor> 
         | <STRING> 

<functiondef>::= function <funcbody>

<funcbody> ::= '(' <parlist>? ')' <block> end

<parlist> ::= <namelist> (',' '...')?
            | '...'

<tableconstructor> ::= '{' <fieldlist>? '}'

<fieldlist> ::= <field> (<fieldsep> <field>)* <fieldsep>?

<field> ::= '[' <exp> ']' '=' <exp> 
          | <Name> '=' <exp> 
          | <exp>

<fieldsep> ::= ',' 
             | ';'

<binop> ::= '+' 
          | '-' 
          | '*' 
          | '/' 
          | '//'
          | '^' 
          | '%' 
          | '&'
          | '~'
          | '|'
          | '>>'
          | '<<'
          | '..' 
          | '<' 
          | '<=' 
          | '>' 
          | '>=' 
          | '==' 
          | '~=' 
          | and 
          | or

<unop> ::= '-' 
         | not 
         | '#'
         | '~'
```
## [7.bnf](https://github.com/luzhixing12345/syntaxlight/tree/main/test/bnf/7.bnf)

```bnf
<regex> ::= <term>
          | <term> '|' <regex>
<term>  ::= <factor>*
          | <factor>+
<factor>::= <base> <quantifier>?

<base>  ::= <char>
          | '\' <char>
          | '(' <regex> ')'
<quantifier> ::= '*'
               | '+'
               | '?'
```
## [8.bnf](https://github.com/luzhixing12345/syntaxlight/tree/main/test/bnf/8.bnf)

```bnf
<regex> ::= <union>

<union> ::= <concatenation>
          | <union> '|' <concatenation>

<concatenation> ::= <quantification>
                  | <concatenation> <quantification>

<quantification> ::= <elementary>
                    | <elementary> '*'
                    | <elementary> '+'
                    | <elementary> '?'
                    | <elementary> '{' <integer> '}'
                    | <elementary> '{' <integer> ',' '}'
                    | <elementary> '{' ',' <integer> '}'
                    | <elementary> '{' <integer> ',' <integer> '}'

<elementary> ::= <grouping>
                | <character>
                | <dot>
                | <escape>
                | <backreference>
                | <lookaround>

<grouping> ::= '(' <regex> ')'
             | '(?:' <regex> ')'
             | '(?<' <name> '>' <regex> ')'
             | '(?' <modifier> ':' <regex> ')'
             | '(?' <modifier> '<' <name> '>' <regex> ')'

<character> ::= <nondot>
               | <posix>
               | <unicode>
               | <hex>
               | <oct>

# <nondot> ::= any character except '.', '|', '*', '+', '?', '[', ']', '{', '}', '(', ')', '\', '^', '$', '#'

<posix> ::= '\d'
          | '\D'
          | '\s'
          | '\S'
          | '\w'
          | '\W'
          | '\p{...}'
          | '\P{...}'

<unicode> ::= '\p{...}'
             | '\P{...}'

<hex> ::= '\xHH'

<oct> ::= '\0OOO'

<dot> ::= '.'

<escape> ::= '\'
            | '\n'
            | '\r'
            | '\t'
            | '\f'
            | '\b'
            | '\v'
            | '\cX'

<backreference> ::= '\n'

<lookaround> ::= ("?=" <regex> )
                 | ("?!" <regex> )
                 | ("?<=" <regex> )
                 | ("?<!" <regex> )

<modifier> ::= 'i'
             | 'm'
             | 's'
             | 'x'
             | 'a'
             | 'u'
             | 'U'

# <integer> ::= any non-negative integer

# <name> ::= any valid name
```
## [9.bnf](https://github.com/luzhixing12345/syntaxlight/tree/main/test/bnf/9.bnf)

```bnf

# https://graphviz.org/doc/info/lang.html

<graph> ::= strict? (graph | digraph) <ID>? '{' <stmt_list>? '}'
<stmt_list> ::= <stmt> (';' <stmt>)* ';'?
<stmt> ::= <node_stmt>
         | <edge_stmt>
         | <attr_stmt>
         | <ID> '=' <ID>
         | <subgraph>
<attr_stmt> ::= ( graph | node | edge) <attr_list>
<attr_list> ::= '[' <a_list>? ']' <attr_list>?
<a_list> ::= <ID> '=' <ID> (';' | ',')? <a_list>?
<edge_stmt> ::= (<node_id> | <subgraph>) <edgeRHS> <attr_list>?
<edgeRHS> ::= <edgeop> (<node_id> | <subgraph>) <edgeRHS>?
<node_stmt> ::= <node_id> <attr_list>?
<node_id> ::= <ID> <port>?
<port> ::= ':' <ID> (':' <compass_pt>)?
         | ':' <compass_pt>
<subgraph> ::= (subgraph <ID>? )? '{' <stmt_list> '}'
<compass_pt> ::= (n | ne | e | se | s | sw | w | nw | c | _)
```
