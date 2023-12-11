// //PARSER
// option : OPTION_CHAR; quoted : DOUBLEQUOTE | BACKQUOTE | SINGLEQUOTE; argument : (quoted
// | UNQUOTED)+; redirection : '<' WHITESPACE argument | '>' WHITESPACE argument; fullCall :
// WHITESPACE* UNQUOTEDRESERVEDCHAR (WHITESPACE option)* (WHITESPACE argument)* (WHITESPACE option)*
// (WHITESPACE argument)* (WHITESPACE redirection)* WHITESPACE*; seq : fullCall ';' fullCall | seq
// ';' fullCall; pipe : fullCall '|' fullCall | pipe '|' fullCall; command : pipe | seq | fullCall;
// reserved : UNQUOTEDRESERVEDCHAR;

// //LEXER
// OPTION_CHAR :'-' [A-Za-z]+; WHITESPACE : (' ' | '\t')+; DOUBLEQUOTE : '"' ( ('`' ~('\n'
// | '`')* '`') | ~('"' | '`' | '\n' ) )* '"'; SINGLEQUOTE : '\'' (~('\n' | '\''))* '\''; BACKQUOTE
// : '`' (~('\n' | '`'))* '`'; UNQUOTEDRESERVEDCHAR : (~( ' ' | '\t' | '"' | '\'' | '\n' | '`' | ';'
// | '|' | '<' | '>' | '#'))+; UNQUOTED : (~( ' ' | '\t' | '\n' | ';' | '|' | '<' | '>' | '#'))+;

grammar ShellGrammar;

//parser rules
command: (pipe | seq | call)? EOF;
pipe: call PIPE call | call PIPE pipe;
seq: (pipe | call) SEMICOLON (pipe | seq | call);
call: WHITESPACE* (redirection WHITESPACE*)* argument (WHITESPACE* atom)* WHITESPACE*;
argument:(quoted|UNQUOTED)+;
atom: redirection |argument;
quoted: single_quoted | double_quoted | back_quoted;
single_quoted: SINGLE_QUOTE (~(NEWLINE | SINGLE_QUOTE))* SINGLE_QUOTE;
back_quoted: BACK_QUOTE (~(NEWLINE | BACK_QUOTE))* BACK_QUOTE;
double_quoted: DOUBLE_QUOTE (back_quoted|~(NEWLINE|DOUBLE_QUOTE|BACK_QUOTE))* DOUBLE_QUOTE;
redirection: LESS_THAN WHITESPACE* argument | GREATER_THAN WHITESPACE* argument;


//lexer rules
LESS_THAN: '<';
GREATER_THAN: '>';
WHITESPACE: [ \t\r]+;
SEMICOLON: ';';
PIPE: '|';
NEWLINE: '\n';
SINGLE_QUOTE: '\'';
DOUBLE_QUOTE:'"';
BACK_QUOTE: '`';
UNQUOTED: ~[ "'`\n;|<>\t]+;